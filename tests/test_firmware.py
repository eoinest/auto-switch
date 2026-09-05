import asyncio
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import importlib.util
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "firmware"))
from control import Controller, Scheduler, battery_reading
from http_api import API, read_request
from gateway_client import process_commands, validate_poll


def configuration():
    return json.loads((ROOT / "firmware/config.example.json").read_text())


class FakeHardware:
    def __init__(self):
        self.events = []
        self.powered = False

    def off(self):
        self.events.append(("off",))
        self.powered = False

    def power_on(self):
        self.events.append(("power",))
        self.powered = True

    def pulse(self, channel, pulse):
        self.events.append(("pulse", channel, pulse))


async def instant_sleep(_):
    await asyncio.sleep(0)


class FirmwareTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = configuration()
        self.hardware = FakeHardware()
        self.controller = Controller(self.config, self.hardware, instant_sleep)
        self.token = "a" * 64
        self.api = API(self.controller, lambda: {"channels": self.controller.status_channels()}, self.token)
        self.headers = {"authorization": "Bearer " + self.token, "content-type": "application/json"}

    def enable(self, channel=0):
        self.config["channels"][channel].update(enabled=True, calibrated=True)

    async def test_default_cannot_move_and_starts_unknown(self):
        with self.assertRaisesRegex(ValueError, "uncalibrated"):
            await self.controller.move(0, "on")
        self.assertEqual(self.hardware.events, [])
        self.assertEqual(self.controller.status_channels()[0]["state"], "unknown")

    async def test_normal_cycle_neutral_press_neutral_then_rail_off(self):
        self.enable()
        await self.controller.move(0, "on")
        self.assertEqual([e for e in self.hardware.events if e[0] == "pulse"],
                         [("pulse", 0, 1500), ("pulse", 0, 1400), ("pulse", 0, 1500)])
        self.assertFalse(self.hardware.powered)
        self.assertEqual(self.controller.states[0], "on")

    async def test_motor_failure_cuts_power_and_marks_unknown(self):
        self.enable()
        def fail(*_):
            raise OSError("hardware failure")
        self.hardware.pulse = fail
        with self.assertRaises(OSError):
            await self.controller.move(0, "off")
        self.assertFalse(self.hardware.powered)
        self.assertFalse(self.controller.busy)
        self.assertEqual(self.controller.states[0], "unknown")

    async def test_cancellation_cuts_power(self):
        self.enable()
        started = asyncio.Event()
        async def pause(_):
            started.set()
            await asyncio.sleep(10)
        self.controller.sleep = pause
        task = asyncio.create_task(self.controller.move(0, "on"))
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertFalse(self.hardware.powered)
        self.assertEqual(self.controller.states[0], "unknown")

    async def test_two_second_cycle_timeout_cuts_power(self):
        self.enable()
        async def pause(_):
            await asyncio.sleep(10)
        self.controller.sleep = pause
        with self.assertRaises(asyncio.TimeoutError):
            await self.controller.move(0, "on")
        self.assertFalse(self.hardware.powered)

    async def test_concurrent_motion_rejected(self):
        self.enable(0)
        self.enable(1)
        async with self.controller.lock:
            with self.assertRaisesRegex(RuntimeError, "busy"):
                await self.controller.move(1, "off")
        self.assertEqual(self.hardware.events, [])

    async def test_status_and_actuation_require_authentication(self):
        for method, path, body in [("GET", "/api/status", b""),
                                  ("POST", "/api/switch", b'{"channel":0,"state":"on"}')]:
            code, _ = await self.api.route(method, path, {}, body)
            self.assertEqual(code, 401)
        code, result = await self.api.route("GET", "/api/status", self.headers, b"")
        self.assertEqual(code, 200)
        self.assertEqual(result["channels"][0]["state"], "unknown")

    async def test_remote_payload_rejects_angles_extra_keys_bool_channel(self):
        self.enable()
        for value in [{"channel": 0, "state": "on", "angle": 180},
                      {"channel": True, "state": "on"},
                      {"channel": 2, "state": "off"},
                      {"channel": 0, "state": "toggle"}, []]:
            code, _ = await self.api.route("POST", "/api/switch", self.headers, json.dumps(value).encode())
            self.assertEqual(code, 400, value)
        self.assertFalse(self.hardware.powered)

    async def test_authenticated_route_returns_updated_command_state(self):
        self.enable()
        code, value = await self.api.route("POST", "/api/switch", self.headers,
                                          b'{"channel":0,"state":"off"}')
        self.assertEqual(code, 200)
        self.assertEqual(value["channels"][0]["last_command"], "off")

    async def test_bounded_http_parser(self):
        for request in [b"GET / HTTP/1.1\r\nX: " + b"a" * 2048,
                        b"POST /api/switch HTTP/1.1\r\nContent-Length: 9999\r\n\r\n",
                        b"POST / HTTP/1.1\r\nContent-Length: 2\r\nContent-Length: 2\r\n\r\n{}",
                        b"POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n"]:
            reader = asyncio.StreamReader()
            reader.feed_data(request)
            reader.feed_eof()
            with self.assertRaises(ValueError):
                await read_request(reader)

    async def test_gateway_ack_failure_does_not_replay(self):
        self.enable()
        class Client:
            calls = 0
            async def post(self, path, data):
                self.calls += 1
                raise OSError("lost acknowledgement")
        client = Client()
        payload = {"mode": "demo", "poll_interval_s": 1,
                   "commands": [{"id": "one", "channel": 0, "state": "on"}]}
        await process_commands(payload, self.controller, client, lambda: {})
        self.assertEqual(client.calls, 1)
        self.assertEqual(sum(e == ("power",) for e in self.hardware.events), 1)

    async def test_gateway_ack_network_holds_motor_guard(self):
        self.enable()
        controller = self.controller
        class Client:
            async def post(self, path, data):
                self.assert_guard = controller.lock.locked() and not controller.busy
        client = Client()
        payload = {"mode": "daily", "poll_interval_s": 60,
                   "commands": [{"id": "one", "channel": 0, "state": "on"}]}
        await process_commands(payload, self.controller, client, lambda: {})
        self.assertTrue(client.assert_guard)

    async def test_gateway_housekeeping_cannot_interrupt_local_schedule(self):
        self.enable()
        self.config.update(transport="gateway", wifi={"ssid": "test", "password": ""})
        hardware = self.hardware
        hardware.battery = lambda: None
        class StopRun(BaseException):
            pass
        class Pin:
            OUT = 1
            def __init__(self, *_args, **_kwargs):
                pass
        class WLAN:
            def __init__(self, *_):
                pass
            def isconnected(self):
                return True
        class Clock:
            elapsed_ms = 0
            def tick(self):
                self.elapsed_ms += 1
            def sync(self):
                pass
            def synced(self):
                return True
        class OnceScheduler:
            def __init__(self, *_):
                self.sent = False
            def due(self, *_):
                if self.sent:
                    return []
                self.sent = True
                return [{"channel": 0, "state": "on"}]
        test = self
        class Client:
            polls = 0
            def __init__(self, *_):
                pass
            async def post(self, path, data):
                test.assertFalse(hardware.powered)
                await asyncio.sleep(0.03)
                test.assertFalse(hardware.powered)
                self.polls += 1
                if self.polls == 2:
                    raise StopRun()
                return {"mode": "demo", "poll_interval_s": 1, "commands": []}
        spec = importlib.util.spec_from_file_location("test_device_main", ROOT / "firmware/main.py")
        module = importlib.util.module_from_spec(spec)
        replacements = {"machine": types.SimpleNamespace(Pin=Pin), "uasyncio": asyncio,
                        "hardware": types.SimpleNamespace(Hardware=lambda _: hardware),
                        "network": types.SimpleNamespace(WLAN=WLAN, STA_IF=0)}
        async def short_loop_sleep(seconds):
            await asyncio.sleep(0.1 if seconds >= 1 else seconds)
        with patch.dict(sys.modules, replacements):
            spec.loader.exec_module(module)
            module.Clock, module.Scheduler, module.GatewayClient = Clock, OnceScheduler, Client
            module.asyncio = types.SimpleNamespace(create_task=asyncio.create_task, sleep=short_loop_sleep)
            with self.assertRaises(StopRun):
                await asyncio.wait_for(module.run(self.config), 3)
        self.assertEqual([e for e in hardware.events if e[0] == "pulse"],
                         [("pulse", 0, 1500), ("pulse", 0, 1400), ("pulse", 0, 1500)])
        self.assertFalse(self.hardware.powered)

    async def test_invalid_later_gateway_command_prevents_entire_batch(self):
        self.enable()
        payload = {"mode": "daily", "poll_interval_s": 60,
                   "commands": [{"id": "one", "channel": 0, "state": "on"},
                                {"id": "two", "channel": 99, "state": "off"}]}
        with self.assertRaises(ValueError):
            await process_commands(payload, self.controller, None, lambda: {})
        self.assertEqual(self.hardware.events, [])

    def test_limits_fail_closed(self):
        for key, value in [("on_us", 500), ("off_us", 2500), ("dwell_ms", 100000),
                           ("return_ms", -1), ("neutral_us", 1400)]:
            config = copy.deepcopy(self.config)
            config["channels"][0][key] = value
            with self.assertRaises(ValueError, msg=key):
                Controller(config, self.hardware)

    def test_utc_schedules_require_sync_fire_once_and_no_catchup(self):
        entry = {"enabled": True, "channel": 0, "state": "off", "hour": 23,
                 "minute": 0, "days": [0]}
        scheduler = Scheduler([entry], 2)
        monday = (2026, 9, 7, 23, 0, 0, 0, 250)
        self.assertEqual(scheduler.due(monday, False), [])
        self.assertEqual(scheduler.due(monday, True), [entry])
        self.assertEqual(scheduler.due(monday, True), [])
        self.assertEqual(scheduler.due((2026, 9, 14, 23, 1, 0, 0, 257), True), [])
        self.assertEqual(scheduler.due((2026, 9, 15, 23, 0, 0, 1, 258), True), [])

    def test_battery_requires_profile_for_percent(self):
        cfg = self.config["battery"]
        reading = battery_reading(32768, cfg)
        self.assertAlmostEqual(reading["voltage"], 5.16, places=2)
        self.assertIsNone(reading["percent"])
        self.assertTrue(reading["estimated"])
        self.assertFalse(reading["low"])
        self.assertTrue(battery_reading(25000, cfg)["low"])
        cfg.update(empty_v=4.4, full_v=5.6)
        self.assertIsInstance(battery_reading(32768, cfg)["percent"], int)

    def test_hardware_inhibits_low_pack_before_enabling_servo(self):
        class Pin:
            OUT = 1
            def __init__(self, number, *_args, value=0):
                self.level = value
            def value(self, value=None):
                if value is not None:
                    self.level = value
                return self.level
        class ADC:
            raw = 25000
            def __init__(self, *_):
                pass
            def read_u16(self):
                return self.raw
        machine = types.SimpleNamespace(Pin=Pin, ADC=ADC, PWM=object)
        spec = importlib.util.spec_from_file_location("test_device_hardware", ROOT / "firmware/hardware.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"machine": machine}):
            spec.loader.exec_module(module)
        self.config["battery"]["enabled"] = True
        hardware = module.Hardware(self.config)
        with self.assertRaisesRegex(ValueError, "battery below"):
            hardware.power_on()
        self.assertEqual(hardware.enable.level, 0)
        ADC.raw = 32768
        hardware.power_on()
        self.assertEqual(hardware.enable.level, 1)
        hardware.off()
        self.assertEqual(hardware.enable.level, 0)


if __name__ == "__main__":
    unittest.main()
