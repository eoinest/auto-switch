"""Independent host checks for physical maintenance entry and servo inhibition."""
import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'firmware'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


maintenance = load('supervisor_maintenance', 'firmware/maintenance.py')


class Pin:
    IN, OUT, PULL_UP = 0, 1, 2
    button = staticmethod(lambda: 1)
    values = {}

    def __init__(self, number, mode=None, pull=None, value=None):
        self.number = number
        if value is not None:
            self.values[number] = value

    def value(self, value=None):
        if value is not None:
            self.values[self.number] = value
        return self.button() if self.number == 0 else self.values.get(self.number, 0)


class PWM:
    created = []

    def __init__(self, pin, **kwargs):
        self.closed = False
        self.duty = kwargs.get('duty_u16')
        self.created.append(self)

    def duty_u16(self, value):
        self.duty = value

    def duty_ns(self, value):
        self.duty = value

    def deinit(self):
        self.closed = True


machine = types.SimpleNamespace(Pin=Pin, PWM=PWM, ADC=object)
with patch.dict(sys.modules, {'machine': machine, 'uasyncio': asyncio}):
    hardware_module = load('supervisor_hardware', 'firmware/hardware.py')
    with patch.dict(sys.modules, {'hardware': hardware_module}):
        main = load('supervisor_main', 'firmware/main.py')


def config():
    return json.loads((ROOT / 'firmware/config.s2-demo.example.json').read_text())


class ButtonTests(unittest.TestCase):
    def setUp(self):
        self.clock = patch.object(maintenance, 'time', types.SimpleNamespace(ticks_diff=lambda a, b: a - b))
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def test_held_during_startup_requires_release_then_new_hold(self):
        hold = maintenance.BootHold()
        for now in (0, 3000, 10000):
            self.assertFalse(hold.update(0, now))
        self.assertFalse(hold.update(1, 10001))
        self.assertFalse(hold.update(0, 10002))
        self.assertFalse(hold.update(0, 13001))
        self.assertTrue(hold.update(0, 13002))
        self.assertFalse(hold.update(0, 20000))  # one event per press

    def test_short_or_interrupted_press_does_not_accumulate_time(self):
        hold = maintenance.BootHold()
        for value, now in ((1, 0), (0, 10), (0, 2900), (1, 2910), (0, 2920), (0, 5900)):
            self.assertFalse(hold.update(value, now))
        self.assertTrue(hold.update(0, 5920))

    def test_hold_uses_wrap_safe_tick_difference(self):
        period = 8192
        diff = lambda a, b: ((a - b + period // 2) % period) - period // 2
        with patch.object(maintenance, 'time', types.SimpleNamespace(ticks_diff=diff)):
            hold = maintenance.BootHold()
            hold.update(1, 7999)
            hold.update(0, 8000)
            self.assertFalse(hold.update(0, (8000 + 2999) % period))
            self.assertTrue(hold.update(0, (8000 + 3000) % period))


class InhibitTests(unittest.TestCase):
    def test_inhibit_deinitializes_pwm_and_cannot_be_cleared_by_off(self):
        hardware = hardware_module.Hardware(config())
        hardware.power_on()
        hardware.pulse(0, 1500)
        pwm = hardware.pwms[0]
        hardware.inhibit()
        hardware.off()
        self.assertTrue(pwm.closed)
        self.assertEqual(pwm.duty, 0)
        self.assertEqual(Pin.values[16], 0)
        self.assertEqual(hardware.pwms, {})
        with self.assertRaisesRegex(RuntimeError, 'disabled'):
            hardware.power_on()
        with self.assertRaisesRegex(RuntimeError, 'disabled'):
            hardware.pulse(0, 1600)


class SupervisorTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, fail=False, late_handler=False):
        hardware = hardware_module.Hardware(config())
        events = []
        now = [0]
        late_task = []
        release_late = asyncio.Event()

        async def sleep(seconds):
            now[0] += round(seconds * 1000)
            await asyncio.sleep(0)

        async def accepted_request():
            await release_late.wait()
            try:
                hardware.pulse(0, 1700)
            except RuntimeError:
                events.append('late pulse rejected')

        async def application(configuration, actual_hardware):
            self.assertIs(actual_hardware, hardware)
            events.append('app started')
            if fail:
                raise OSError('simulated unavailable application')
            actual_hardware.pulse(0, 1500)
            if late_handler:
                late_task.append(asyncio.create_task(accepted_request()))
            try:
                await asyncio.Event().wait()
            finally:
                events.append(('app cancelled', actual_hardware.inhibited))
                release_late.set()

        async def enter_update(configuration, connect):
            events.append(('maintenance', hardware.inhibited, bool(hardware.pwms)))
            for task in late_task:
                await task

        fake_asyncio = types.SimpleNamespace(create_task=asyncio.create_task, sleep=sleep)
        fake_time = types.SimpleNamespace(ticks_ms=lambda: now[0], ticks_diff=lambda a, b: a - b)
        # One released sample arms detection; the next continuously-low samples
        # model a fresh press while the app is running or failed to start.
        with patch.dict(sys.modules, {'machine': machine, 'maintenance': maintenance}), \
                patch.object(Pin, 'button', staticmethod(lambda: int(now[0] == 0))), \
                patch.object(main, 'asyncio', fake_asyncio), patch.object(main, 'time', fake_time), \
                patch.object(maintenance, 'time', fake_time), patch.object(main, 'run', application), \
                patch.object(maintenance, 'run', enter_update), patch('builtins.print'):
            await main.supervise(config(), hardware)
        self.assertGreaterEqual(now[0], 3050)
        self.assertTrue(hardware.inhibited)
        self.assertEqual(hardware.pwms, {})
        self.assertIn(('maintenance', True, False), events)
        return events

    async def test_inhibits_before_cancelling_application_then_enters_update(self):
        events = await self.exercise()
        self.assertIn(('app cancelled', True), events)
        self.assertLess(events.index(('app cancelled', True)), events.index(('maintenance', True, False)))

    async def test_button_recovery_remains_available_after_application_failure(self):
        events = await self.exercise(fail=True)
        self.assertEqual(events[0], 'app started')
        self.assertIn(('maintenance', True, False), events)

    async def test_previously_accepted_request_cannot_restart_pwm(self):
        events = await self.exercise(late_handler=True)
        self.assertIn('late pulse rejected', events)

    async def test_other_profiles_do_not_claim_gpio_zero(self):
        calls = []
        async def run(configuration, hardware):
            calls.append((configuration, hardware))
            return 'normal'
        cfg, hw = {'hardware_profile': 'aa-demo'}, object()
        with patch.object(main, 'run', run), patch.dict(sys.modules, {'machine': None}):
            self.assertEqual(await main.supervise(cfg, hw), 'normal')
        self.assertEqual(calls, [(cfg, hw)])

    async def test_reset_waits_for_boot_button_release(self):
        samples = iter((0, 0, 1))
        sleeps, reset = [], []
        async def sleep(seconds):
            sleeps.append(seconds)
        api = maintenance.UpdateAPI('x' * 24, lambda: reset.append(True))
        with patch.dict(sys.modules, {'machine': machine}), \
                patch.object(Pin, 'button', staticmethod(lambda: next(samples))), \
                patch.object(maintenance, 'asyncio', types.SimpleNamespace(sleep=sleep)):
            await api.reboot()
        self.assertEqual(sleeps, [1, 0.05, 0.05])
        self.assertEqual(reset, [True])


if __name__ == '__main__':
    unittest.main()
