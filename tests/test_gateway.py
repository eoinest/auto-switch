import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

spec = importlib.util.spec_from_file_location("gateway_server", Path(__file__).resolve().parents[1] / "gateway/server.py")
gateway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gateway)


def status(state="unknown"):
    return {"device": "Test", "channels": [{"id": 0, "name": "Light", "state": state, "enabled": True, "calibrated": True}], "battery": None}


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.store = gateway.Store(":memory:")
        self.store.update_status(status())

    def tearDown(self):
        self.store.db.close()

    def test_delivery_is_never_replayed_after_lost_response(self):
        queued = self.store.queue({"channel": 0, "state": "on"})
        first = self.store.poll({"status": status()})
        self.assertEqual(first["commands"][0]["id"], queued["id"])
        self.assertEqual(self.store.poll({"status": status()})["commands"], [])
        self.assertEqual(self.store.status()["channels"][0]["state"], "unknown")

    def test_latest_queued_intent_supersedes_previous(self):
        self.store.queue({"channel": 0, "state": "on"})
        self.store.queue({"channel": 0, "state": "off"})
        self.assertEqual(self.store.poll({"status": status()})["commands"][0]["state"], "off")
        self.assertEqual(self.store.poll({"status": status()})["commands"], [])

    def test_acknowledgement_updates_history_and_is_idempotent(self):
        ident = self.store.queue({"channel": 0, "state": "on"})["id"]
        self.store.poll({"status": status()})
        body = {"id": ident, "success": True, "status": status("on")}
        self.store.ack(body)
        self.store.ack(body)
        self.assertEqual(self.store.status()["channels"][0]["state"], "on")
        self.assertEqual(self.store.status()["pending"], 0)

    def test_expired_movements_are_not_executed(self):
        self.store.queue({"channel": 0, "state": "on"})
        self.store.db.execute("UPDATE commands SET expires=?", (time.time() - 1,))
        self.assertEqual(self.store.poll({"status": status()})["commands"], [])
        self.assertEqual(self.store.status()["commands"][0]["status"], "expired")

    def test_mode_applies_on_next_poll(self):
        self.store.mode({"mode": "demo", "poll_interval_s": 300})
        response = self.store.poll({"status": status()})
        self.assertEqual((response["mode"], response["poll_interval_s"]), ("demo", 300))

    def test_reject_uncalibrated_invalid_channel_and_unsafe_interval(self):
        initial = status()
        initial["channels"][0]["calibrated"] = False
        self.store.update_status(initial)
        for body in [{"channel": 0, "state": "on"}, {"channel": True, "state": "on"}, {"channel": 0, "state": "toggle"}]:
            with self.assertRaises(ValueError):
                self.store.queue(body)
        with self.assertRaises(ValueError):
            self.store.mode({"mode": "daily", "poll_interval_s": 0})

    def test_restart_preserves_delivery_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.db"
            first = gateway.Store(path)
            first.update_status(status())
            first.queue({"channel": 0, "state": "on"})
            first.poll({"status": status()})
            first.db.close()
            second = gateway.Store(path)
            try:
                self.assertEqual(second.poll({"status": status()})["commands"], [])
            finally:
                second.db.close()

    def test_nonfinite_status_does_not_replace_last_valid_checkin(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            invalid = status("on")
            invalid["battery"] = {"voltage": value}
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.store.poll({"status": invalid})
            self.assertEqual(self.store.status()["channels"][0]["state"], "unknown")


class HTTPFixture:
    @classmethod
    def setUpClass(cls):
        cls.store = gateway.Store(":memory:")
        cls.store.update_status(status())
        cls.server = gateway.ThreadingHTTPServer(("127.0.0.1", 0), gateway.handler_for(
            cls.store, "c" * 32, "d" * 32, open_client=getattr(cls, "open_client", False)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = "http://127.0.0.1:%s" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.store.db.close()

    def request(self, path, token=None, body=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        request = Request(self.url + path, headers=headers, data=None if body is None else json.dumps(body).encode())
        try:
            with urlopen(request, timeout=2) as response:
                return response.status, response.read()
        except HTTPError as error:
            with error:
                return error.code, error.read()

class HTTPTests(HTTPFixture, unittest.TestCase):
    def test_access_metadata_is_public_but_contains_no_device_status(self):
        code, data = self.request("/api/access")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(data), {"open_client": False})

    def test_status_requires_client_key(self):
        self.assertEqual(self.request("/api/status")[0], 401)
        self.assertEqual(self.request("/api/status", "d" * 32)[0], 401)
        self.assertEqual(self.request("/api/status", "c" * 32)[0], 200)

    def test_device_key_cannot_issue_user_commands(self):
        self.assertEqual(self.request("/api/switch", "d" * 32, {"channel": 0, "state": "on"})[0], 401)
        self.assertEqual(self.request("/api/device/poll", "c" * 32, {"status": status()})[0], 401)

    def test_phone_to_device_round_trip(self):
        code, data = self.request("/api/switch", "c" * 32, {"channel": 0, "state": "off"})
        self.assertEqual(code, 202)
        ident = json.loads(data)["id"]
        code, poll = self.request("/api/device/poll", "d" * 32, {"status": status()})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(poll)["commands"][0]["id"], ident)
        code, _ = self.request("/api/device/ack", "d" * 32, {"id": ident, "success": True, "status": status("off")})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(self.request("/api/status", "c" * 32)[1])["channels"][0]["state"], "off")

    def test_static_allowlist_and_malformed_request(self):
        self.assertEqual(self.request("/")[0], 200)
        self.assertEqual(self.request("/../gateway/server.py")[0], 404)
        self.assertEqual(self.request("/api/switch", "c" * 32, ["not an object"])[0], 400)

    def test_nonfinite_json_cannot_poison_phone_status(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            invalid = status()
            invalid["battery"] = {"voltage": value}
            with self.subTest(value=value):
                self.assertEqual(self.request("/api/device/poll", "d" * 32, {"status": invalid})[0], 400)
        code, data = self.request("/api/status", "c" * 32)
        self.assertEqual(code, 200)
        self.assertIsNone(json.loads(data)["battery"])

    def test_overflowing_json_number_is_rejected_before_mutation(self):
        previous_mode = self.store.status()["mode"]
        request = Request(self.url + "/api/mode", headers={
            "Authorization": "Bearer " + "c" * 32, "Content-Type": "application/json"},
            data=b'{"mode":"demo","poll_interval_s":60,"extra":1e400}')
        with self.assertRaises(HTTPError) as raised:
            urlopen(request, timeout=2)
        with raised.exception as error:
            self.assertEqual(error.code, 400)
        self.assertEqual(self.store.status()["mode"], previous_mode)


class OpenClientHTTPTests(HTTPFixture, unittest.TestCase):
    open_client = True

    def test_access_metadata_enables_keyless_ui(self):
        code, data = self.request("/api/access")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(data), {"open_client": True})

    def test_status_and_mode_need_no_client_key(self):
        code, data = self.request("/api/status")
        self.assertEqual(code, 200)
        self.assertTrue(json.loads(data)["open_client"])
        self.assertEqual(self.request("/api/mode", body={"mode": "demo"})[0], 200)

    def test_device_endpoints_still_require_the_device_key(self):
        for path, body in (("/api/device/poll", {"status": status()}),
                           ("/api/device/ack", {"id": "1", "success": True})):
            for token in (None, "c" * 32, "incorrect"):
                with self.subTest(path=path, token=token):
                    self.assertEqual(self.request(path, token, body)[0], 401)

    def test_open_phone_to_authenticated_device_round_trip(self):
        code, data = self.request("/api/switch", body={"channel": 0, "state": "on"})
        self.assertEqual(code, 202)
        ident = json.loads(data)["id"]
        code, poll = self.request("/api/device/poll", "d" * 32, {"status": status()})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(poll)["commands"][0]["id"], ident)
        self.assertEqual(self.request("/api/device/ack", "d" * 32,
            {"id": ident, "success": True, "status": status("on")})[0], 200)

    def test_open_client_cannot_bypass_disabled_or_uncalibrated_channel(self):
        for field in ("enabled", "calibrated"):
            disabled = status()
            disabled["channels"][0][field] = False
            self.store.update_status(disabled)
            self.assertEqual(self.request("/api/switch", body={"channel": 0, "state": "on"})[0], 400)
        self.store.update_status(status())


if __name__ == "__main__":
    unittest.main()
