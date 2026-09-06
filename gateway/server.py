"""Auto Switch LAN relay. Python 3.10+, standard library only.

Commands are delivered at most once: ambiguous movement is never retried.
Run `python3 gateway/server.py --help`; this server does not touch GPIO.
"""
import argparse
import hmac
import json
import os
from pathlib import Path
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "firmware" / "www"
MAX_BODY = 16384


class Store:
    def __init__(self, path, demo=False):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.demo = demo
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS commands (id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel INTEGER NOT NULL, state TEXT NOT NULL, created REAL NOT NULL,
            expires REAL NOT NULL, status TEXT NOT NULL, error TEXT);
        """)
        for key, value in [("mode", "daily"), ("poll_interval_s", 60), ("last_seen", None), ("status", None)]:
            self.db.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", (key, json.dumps(value)))
        self.db.commit()
        if demo:
            self.update_status({"device": "Office · preview", "channels": [
                {"id": i, "name": name, "state": "unknown", "enabled": True, "calibrated": True}
                for i, name in enumerate(["Desk lights", "Room lights"])],
                "battery": {"voltage": 4.96, "percent": 76, "estimated": True}, "clock_synced": True})

    def get(self, key):
        return json.loads(self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()[0])

    def put(self, key, value):
        self.db.execute("UPDATE settings SET value=? WHERE key=?", (json.dumps(value), key))

    @staticmethod
    def validate_status(status):
        # Python accepts NaN/Infinity by default, but browsers reject them as JSON.
        # Validate before storing so one malformed check-in cannot break the UI.
        json.dumps(status, allow_nan=False)
        if not isinstance(status, dict) or not isinstance(status.get("channels"), list):
            raise ValueError("Device status must contain channels")
        channels = status["channels"]
        if len(channels) not in (1, 2):
            raise ValueError("Expected one or two channels")
        ids = []
        for channel in channels:
            if not isinstance(channel, dict) or type(channel.get("id")) is not int or channel["id"] not in (0, 1):
                raise ValueError("Invalid channel")
            if channel.get("state") not in ("unknown", "on", "off"):
                raise ValueError("Invalid command history")
            ids.append(channel["id"])
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate channel IDs")

    def update_status(self, status):
        self.validate_status(status)
        with self.lock, self.db:
            self.put("status", status)
            self.put("last_seen", time.time())

    def expire(self):
        now = time.time()
        self.db.execute("UPDATE commands SET status='expired', error='Expired before delivery' WHERE status='queued' AND expires < ?", (now,))
        self.db.execute("UPDATE commands SET status='uncertain', error='No acknowledgement; physical position unknown' WHERE status='dispatched' AND expires < ?", (now,))

    def status(self):
        with self.lock, self.db:
            self.expire()
            data = self.get("status") or {"device": "Auto Switch", "channels": [], "battery": None, "clock_synced": False}
            seen = self.get("last_seen")
            recent = self.db.execute("SELECT id,channel,state,status,error FROM commands ORDER BY id DESC LIMIT 8").fetchall()
            data.update({"gateway": True, "preview": self.demo, "mode": self.get("mode"),
                "poll_interval_s": self.get("poll_interval_s"), "last_seen": seen,
                "last_seen_age_s": None if seen is None else max(0, round(time.time() - seen)),
                "pending": self.db.execute("SELECT COUNT(*) FROM commands WHERE status IN ('queued','dispatched')").fetchone()[0],
                "commands": [dict(r) for r in recent]})
            return data

    def queue(self, body):
        channel, state = body.get("channel"), body.get("state")
        if type(channel) is not int or channel not in (0, 1) or state not in ("on", "off"):
            raise ValueError("Expected channel 0/1 and state on/off")
        with self.lock, self.db:
            status = self.get("status")
            match = next((c for c in status["channels"] if c["id"] == channel), None) if status else None
            if not match or match.get("enabled") is not True or match.get("calibrated") is not True:
                raise ValueError("Device must check in with this channel calibrated and enabled")
            self.expire()
            self.db.execute("UPDATE commands SET status='superseded' WHERE channel=? AND status='queued'", (channel,))
            now = time.time()
            ttl = max(600, self.get("poll_interval_s") * 3)
            cursor = self.db.execute("INSERT INTO commands(channel,state,created,expires,status) VALUES (?,?,?,?,?)",
                (channel, state, now, now + ttl, "applied" if self.demo else "queued"))
            if self.demo:
                match["state"] = state
                self.put("status", status)
                self.put("last_seen", now)
            return {"id": str(cursor.lastrowid), "status": "applied" if self.demo else "queued"}

    def mode(self, body):
        mode, interval = body.get("mode"), body.get("poll_interval_s", 60)
        if mode not in ("daily", "demo") or type(interval) is not int or not 10 <= interval <= 3600:
            raise ValueError("Mode must be daily/demo, interval 10–3600 seconds")
        with self.lock, self.db:
            self.put("mode", mode)
            self.put("poll_interval_s", interval)
        return {"mode": mode, "poll_interval_s": interval, "applies": "next device check-in"}

    def poll(self, body):
        self.validate_status(body.get("status"))
        with self.lock, self.db:
            self.put("status", body["status"])
            self.put("last_seen", time.time())
            self.expire()
            # At most one delivery per poll, and never replay a delivered movement.
            row = self.db.execute("SELECT id,channel,state FROM commands WHERE status='queued' ORDER BY id LIMIT 1").fetchone()
            commands = []
            if row:
                self.db.execute("UPDATE commands SET status='dispatched' WHERE id=?", (row["id"],))
                commands = [{"id": str(row["id"]), "channel": row["channel"], "state": row["state"]}]
            return {"commands": commands, "mode": self.get("mode"), "poll_interval_s": self.get("poll_interval_s")}

    def ack(self, body):
        ident = body.get("id")
        if not isinstance(ident, str) or not ident.isdigit() or type(body.get("success")) is not bool:
            raise ValueError("Expected command id and success boolean")
        if "status" in body:
            self.validate_status(body["status"])
        with self.lock, self.db:
            row = self.db.execute("SELECT status FROM commands WHERE id=?", (ident,)).fetchone()
            if not row or row["status"] not in ("dispatched", "uncertain", "applied", "failed"):
                raise ValueError("Command was not dispatched")
            if row["status"] in ("dispatched", "uncertain"):
                self.db.execute("UPDATE commands SET status=?, error=? WHERE id=?",
                    ("applied" if body["success"] else "failed", str(body.get("error", ""))[:200], ident))
                if "status" in body:
                    self.put("status", body["status"])
                self.put("last_seen", time.time())
        return {"ok": True}


def handler_for(store, client_token, device_token, open_client=False):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, fmt, *args):
            # Request paths/headers can contain accidental credentials; omit them.
            pass

        def reply(self, code, data, mime="application/json"):
            raw = json.dumps(data, allow_nan=False).encode() if mime == "application/json" else data
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def authorized(self, device=False):
            if open_client and not device:
                return True
            expected = device_token if device else client_token
            actual = self.headers.get("Authorization", "")
            return hmac.compare_digest(actual.encode(), ("Bearer " + expected).encode())

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/api/access":
                return self.reply(200, {"open_client": open_client})
            if path == "/api/status":
                if not self.authorized():
                    return self.reply(401, {"error": "Unauthorized"})
                return self.reply(200, {**store.status(), "open_client": open_client})
            static = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path not in static:
                return self.reply(404, {"error": "Not found"})
            name, mime = static[path]
            return self.reply(200, (WWW / name).read_bytes(), mime)

        def do_POST(self):
            path = self.path
            device = path in ("/api/device/poll", "/api/device/ack")
            if not self.authorized(device):
                return self.reply(401, {"error": "Unauthorized"})
            try:
                if self.headers.get("Transfer-Encoding"):
                    return self.reply(400, {"error": "Transfer encoding unsupported"})
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= MAX_BODY:
                    return self.reply(413, {"error": "Body must be 1–16384 bytes"})
                if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
                    return self.reply(415, {"error": "Use application/json"})
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError("Expected an object")
                # Also catches exponent overflow (e.g. 1e400), which parse_constant
                # alone would miss. Reject malformed input before any mutation.
                json.dumps(body, allow_nan=False)
                routes = {"/api/switch": store.queue, "/api/mode": store.mode, "/api/device/poll": store.poll, "/api/device/ack": store.ack}
                if path not in routes:
                    return self.reply(404, {"error": "Not found"})
                return self.reply(202 if path == "/api/switch" else 200, routes[path](body))
            except (ValueError, TypeError, UnicodeError, RecursionError) as error:
                return self.reply(400, {"error": str(error)})
            except (TimeoutError, ConnectionError):
                self.close_connection = True

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Use 0.0.0.0 to serve your LAN")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", type=Path, default=ROOT / "gateway" / "state.sqlite3")
    parser.add_argument("--demo", action="store_true", help="Simulate a device; loopback only; no GPIO")
    parser.add_argument("--open-client", action="store_true", help="Allow browser control without a client key for a trusted LAN prototype; device authentication stays required")
    args = parser.parse_args()
    if args.demo and args.host not in ("127.0.0.1", "localhost", "::1"):
        parser.error("Preview mode is restricted to loopback")
    client_token = "preview-device-key-only" if args.demo else os.environ.get("AUTO_SWITCH_CLIENT_TOKEN", "")
    device_token = "preview-hardware-key-only" if args.demo else os.environ.get("AUTO_SWITCH_DEVICE_TOKEN", "")
    required_keys = (device_token,) if args.open_client else (client_token, device_token)
    valid_keys = all(32 <= len(key) <= 128 and not key.startswith("REPLACE")
                     and all(33 <= ord(char) <= 126 for char in key)
                     for key in required_keys)
    if not args.demo and (not valid_keys or (not args.open_client and client_token == device_token)):
        parser.error("Set AUTO_SWITCH_DEVICE_TOKEN and, unless --open-client is set, a distinct AUTO_SWITCH_CLIENT_TOKEN (32–128 printable characters; replace example placeholders)")
    store = Store(":memory:" if args.demo else args.db, args.demo)
    server = ThreadingHTTPServer((args.host, args.port), handler_for(store, client_token, device_token, args.open_client))
    print(f"Auto Switch {'PREVIEW' if args.demo else 'gateway'}: http://{args.host}:{args.port}/{'?demo' if args.demo else ''}", flush=True)
    if args.open_client:
        print("Open LAN prototype: browser control needs no key; device check-ins remain authenticated.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.db.close()


if __name__ == "__main__":
    main()
