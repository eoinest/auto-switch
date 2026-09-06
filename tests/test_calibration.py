"""Host checks for the physical calibration transaction and reboot storage."""
import asyncio
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "firmware"))
from control import Controller
from calibration import save_calibration, load_calibration
from http_api import API


class Hardware:
    def __init__(self):
        self.events = []
    def off(self):
        self.events.append("off")
    def power_on(self):
        self.events.append("power")
    def pulse(self, channel, pulse):
        self.events.append((channel, pulse))


async def instant(_):
    await asyncio.sleep(0)


class CalibrationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "firmware/config.s2-demo.example.json").read_text())
        self.original = copy.deepcopy(self.config)
        self.hardware = Hardware()
        self.saved = []
        self.now = 0
        self.controller = Controller(self.config, self.hardware, instant,
                                     lambda value: self.saved.append(copy.deepcopy(value)), lambda: self.now)

    async def start(self):
        await self.controller.calibrate({"action": "start", "channel": 0})

    async def action(self, action, **extra):
        await self.controller.calibrate({"action": action,
                                         "revision": self.controller.calibration_revision, **extra})

    async def test_enter_and_unmoved_done_never_move_or_enable(self):
        await self.start()
        self.assertEqual(self.hardware.events, [])
        with self.assertRaisesRegex(ValueError, "test its center"):
            await self.action("done")
        self.assertEqual(self.saved, [])
        self.assertEqual(self.config, self.original)

    async def test_nudge_moves_center_only_and_preserves_offsets_through_save(self):
        await self.start()
        await self.action("nudge", delta=10)
        self.assertEqual(self.hardware.events, ["off", "power", (0, 1510), "off"])
        self.assertEqual(self.config, self.original)
        await self.action("done")
        cfg = self.controller.channels[0]
        self.assertEqual((cfg["on_us"], cfg["neutral_us"], cfg["off_us"]), (1410, 1510, 1610))
        self.assertTrue(cfg["enabled"] and cfg["calibrated"])
        self.assertEqual(len(self.saved), 1)
        self.assertIsNone(self.controller.calibration_status())

    async def test_test_does_not_change_values_and_cancel_discards_changes(self):
        await self.start()
        await self.action("test")
        self.assertIn((0, 1500), self.hardware.events)
        await self.action("nudge", delta=-10)
        await self.action("cancel")
        self.assertEqual(self.config, self.original)
        self.assertEqual(self.saved, [])
        self.assertEqual(self.hardware.events[-1], "off")

    async def test_bounds_apply_to_endpoints_not_just_center(self):
        self.config["channels"][0].update(on_us=1700, neutral_us=1800, off_us=1900)
        await self.start()
        with self.assertRaisesRegex(ValueError, "off_us"):
            await self.action("nudge", delta=10)
        self.assertEqual(self.hardware.events, [])
        self.assertFalse(self.controller.calibration_status()["tested"])

    async def test_invalid_delta_and_boolean_rejected(self):
        await self.start()
        for delta in (-20, 0, 100, True, 10.0, "10"):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                await self.action("nudge", delta=delta)
        self.assertEqual(self.hardware.events, [])

    async def test_duplicate_revision_cannot_repeat_motion(self):
        await self.start()
        payload = {"action": "nudge", "delta": 10, "revision": self.controller.calibration_revision}
        await self.controller.calibrate(payload)
        events = list(self.hardware.events)
        with self.assertRaisesRegex(RuntimeError, "changed"):
            await self.controller.calibrate(payload)
        self.assertEqual(self.hardware.events, events)

    async def test_move_rejected_during_calibration_and_concurrent_calibration_rejected(self):
        await self.start()
        with self.assertRaisesRegex(RuntimeError, "finish or cancel"):
            await self.controller.move(0, "off")
        async with self.controller.lock:
            with self.assertRaisesRegex(RuntimeError, "busy"):
                await self.action("test")
        self.assertEqual(self.hardware.events, [])

    async def test_timeout_discards_draft_without_moving(self):
        await self.start()
        await self.action("nudge", delta=10)
        events = list(self.hardware.events)
        self.now = 120001
        self.assertIsNone(self.controller.calibration_status())
        self.assertEqual(self.config, self.original)
        self.assertEqual(self.hardware.events, events)
        with self.assertRaisesRegex(ValueError, "expired"):
            await self.action("done")

    async def test_storage_failure_keeps_old_configuration(self):
        await self.start()
        await self.action("test")
        def fail(_):
            raise OSError("disk full")
        self.controller.persist = fail
        with self.assertRaises(OSError):
            await self.action("done")
        self.assertEqual(self.config, self.original)
        self.assertIsNotNone(self.controller.calibration_status())

    async def test_pulse_failure_and_cancellation_stop_pwm(self):
        await self.start()
        def fail(*_):
            raise OSError("servo failure")
        self.hardware.pulse = fail
        with self.assertRaises(OSError):
            await self.action("test")
        self.assertEqual(self.hardware.events[-1], "off")
        self.assertFalse(self.controller.busy)
        self.assertFalse(self.controller.calibration_status()["tested"])
        self.hardware.pulse = lambda *_: None
        started = asyncio.Event()
        async def pause(_):
            started.set()
            await asyncio.sleep(30)
        self.controller.sleep = pause
        task = asyncio.create_task(self.action("test"))
        await started.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(self.hardware.events[-1], "off")
        self.assertFalse(self.controller.busy)

    async def test_api_requires_json_and_auth_and_reports_conflicts(self):
        token = "a" * 32
        api = API(self.controller, lambda: {"calibration": self.controller.calibration_status()}, token)
        body = b'{"action":"start","channel":0}'
        code, _ = await api.route("POST", "/api/calibration", {}, body)
        self.assertEqual(code, 401)
        auth = {"authorization": "Bearer " + token}
        code, _ = await api.route("POST", "/api/calibration", auth, body)
        self.assertEqual(code, 415)
        auth["content-type"] = "application/json"
        code, data = await api.route("POST", "/api/calibration", auth, body)
        self.assertEqual(code, 200)
        self.assertFalse(data["calibration"]["tested"])
        code, _ = await api.route("POST", "/api/calibration", auth, body)
        self.assertEqual(code, 409)


class StorageTests(unittest.TestCase):
    def test_roundtrip_keeps_secrets_out_and_restores_only_matching_pins(self):
        config = json.loads((ROOT / "firmware/config.s2-demo.example.json").read_text())
        config["wifi"]["password"] = "fixture-secret-not-a-real-password"
        config["channels"][0].update(neutral_us=1520, on_us=1420, off_us=1620, enabled=True, calibrated=True)
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/calibration.json"
            save_calibration(config["channels"], path)
            text = Path(path).read_text()
            self.assertNotIn("password", text)
            self.assertNotIn("fixture-secret", text)
            reboot = json.loads((ROOT / "firmware/config.s2-demo.example.json").read_text())
            load_calibration(reboot, path)
            self.assertEqual(reboot["channels"][0]["neutral_us"], 1520)
            self.assertTrue(reboot["channels"][0]["enabled"])
            reboot["channels"][0]["pin"] = 17
            with self.assertRaises(ValueError):
                load_calibration(reboot, path)
            before = Path(path).read_bytes()
            with patch("calibration.os.rename", side_effect=OSError("rename failure")):
                with self.assertRaises(OSError):
                    save_calibration(config["channels"], path)
            self.assertEqual(Path(path).read_bytes(), before)

    def test_invalid_saved_data_rejects_without_partial_override(self):
        config = json.loads((ROOT / "firmware/config.s2-demo.example.json").read_text())
        original = copy.deepcopy(config)
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/calibration.json"
            load_calibration(config, path)  # First boot is allowed.
            save_calibration(config["channels"], path)
            saved = json.loads(Path(path).read_text())
            saved["channels"][0]["off_us"] = 2000
            Path(path).write_text(json.dumps(saved))
            with self.assertRaises(ValueError):
                load_calibration(config, path)
            self.assertEqual(config, original)
