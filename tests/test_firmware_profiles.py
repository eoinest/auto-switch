"""Exercise actual hardware and startup modules against observable fake GPIO."""
import asyncio
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import mock_open, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "firmware"))
from control import Controller


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "firmware" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProfileTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "firmware/config.aa-demo.example.json").read_text())
        self.events = []
        events = self.events

        class Pin:
            OUT = 1
            def __init__(self, number, *_args, **kwargs):
                self.number = number
                self.level = kwargs.get("value")
                events.append(("pin", number, self.level))
            def value(self, level):
                self.level = level
                events.append(("level", self.number, level))

        class PWM:
            def __init__(self, pin, **_kwargs):
                self.pin = pin.number
            def duty_ns(self, value):
                events.append(("pulse", self.pin, value))
            def duty_u16(self, value):
                events.append(("duty", self.pin, value))
            def deinit(self):
                events.append(("deinit", self.pin))

        def adc(_):
            raise AssertionError("AA demo must not instantiate the unwired ADC")

        self.machine = types.SimpleNamespace(Pin=Pin, PWM=PWM, ADC=adc)
        with patch.dict(sys.modules, {"machine": self.machine}):
            self.hardware_module = load("profile_hardware", "hardware.py")

    def assert_no_gate(self):
        self.assertFalse(any(event[1] == 15 for event in self.events))

    async def test_ungated_cycle_preserves_motion_bounds_and_never_touches_gate(self):
        hardware = self.hardware_module.Hardware(self.config)
        async def immediate(_):
            await asyncio.sleep(0)
        controller = Controller(self.config, hardware, immediate)
        with self.assertRaisesRegex(ValueError, "uncalibrated"):
            await controller.move(0, "on")
        self.config["channels"][0].update(enabled=True, calibrated=True)
        await controller.move(0, "on")
        self.assertEqual([e for e in self.events if e[0] == "pulse"],
                         [("pulse", 16, 1500000), ("pulse", 16, 1400000), ("pulse", 16, 1500000)])
        self.assertIn(("deinit", 16), self.events)
        self.assertEqual(self.events[-1], ("pin", 16, 0))
        self.assertIsNone(hardware.enable)
        self.assertIsNone(hardware.battery())
        self.assert_no_gate()

    async def test_ungated_cancellation_stops_pwm_without_claiming_power_cut(self):
        self.config["channels"][0].update(enabled=True, calibrated=True)
        hardware = self.hardware_module.Hardware(self.config)
        started = asyncio.Event()
        async def pause(_):
            if hardware.pwms:
                started.set()
                await asyncio.sleep(10)
        controller = Controller(self.config, hardware, pause)
        task = asyncio.create_task(controller.move(0, "on"))
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertIn(("deinit", 16), self.events)
        self.assertEqual(controller.states[0], "unknown")
        self.assertFalse(controller.busy)
        self.assert_no_gate()

    def test_legacy_default_retains_gate(self):
        config = json.loads((ROOT / "firmware/config.example.json").read_text())
        hardware = self.hardware_module.Hardware(config)
        self.assertEqual(self.events[0], ("pin", 15, 0))
        hardware.power_on()
        self.assertEqual(hardware.enable.level, 1)
        hardware.off()
        self.assertEqual(hardware.enable.level, 0)

    def test_invalid_profiles_reject_before_any_gpio(self):
        changes = [{"hardware_profile": "typo"}, {"power_enable_pin": 15},
                   {"battery": {"enabled": True}}, {"transport": "gateway"},
                   {"hardware_profile": "gated", "power_enable_pin": None},
                   {"hardware_profile": "gated", "power_enable_pin": True}]
        for change in changes:
            config = copy.deepcopy(self.config)
            config.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.hardware_module.Hardware(config)
        for pin in (15, 18):
            config = copy.deepcopy(self.config)
            config["channels"][0]["pin"] = pin
            with self.assertRaises(ValueError):
                self.hardware_module.Hardware(config)
        config = copy.deepcopy(self.config)
        config["channels"][0]["on_us"] = 500
        with self.assertRaises(ValueError):
            self.hardware_module.Hardware(config)
        self.assertEqual(self.events, [])

    def test_bench_import_and_off_respect_profile(self):
        with patch.dict(sys.modules, {"machine": self.machine, "uasyncio": asyncio,
                                    "hardware": self.hardware_module}):
            bench = load("profile_bench", "bench.py")
        self.assertEqual(self.events, [])
        with patch("builtins.open", mock_open(read_data=json.dumps(self.config))), patch("builtins.print") as output:
            bench.off()
        self.assertIn("still powered", output.call_args.args[0])
        self.assert_no_gate()

    def test_startup_failure_and_import_do_not_touch_gate(self):
        with patch.dict(sys.modules, {"machine": self.machine, "uasyncio": asyncio,
                                    "hardware": self.hardware_module}):
            main = load("profile_main", "main.py")
        config = copy.deepcopy(self.config)
        config["hardware_profile"] = "unknown"
        with patch("builtins.open", mock_open(read_data=json.dumps(config))), patch("builtins.print") as output:
            main.start()
        self.assertNotIn("servo power off", output.call_args.args[0])
        self.assertEqual(self.events, [])


if __name__ == "__main__":
    unittest.main()
