"""Outbound polling for a Mac mini queue; no third-party device dependencies."""
import json
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from control import integer
from http_api import read_headers, read_body, validate_token


def validate_poll(payload, channel_count):
    if not isinstance(payload, dict) or payload.get("mode") not in ("daily", "demo"):
        raise ValueError("invalid gateway mode")
    integer(payload.get("poll_interval_s"), 1, 3600, "poll interval")
    commands = payload.get("commands")
    if not isinstance(commands, list) or len(commands) > 2:
        raise ValueError("gateway must return at most two commands")
    ids = set()
    for command in commands:
        if not isinstance(command, dict):
            raise ValueError("invalid command")
        ident = command.get("id")
        if not isinstance(ident, str) or not 1 <= len(ident) <= 128 or ident in ids:
            raise ValueError("invalid or duplicate command ID")
        ids.add(ident)
        integer(command.get("channel"), 0, channel_count - 1, "channel")
        if command.get("state") not in ("on", "off"):
            raise ValueError("invalid state")
    return payload


class GatewayClient:
    def __init__(self, cfg):
        self.host, self.port = cfg["host"], cfg.get("port", 8765)
        self.token = cfg["token"]
        validate_token(self.token)
        integer(self.port, 1, 65535, "gateway port")
        if not self.host or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-:" for c in self.host):
            raise ValueError("gateway host must be hostname or IP, without URL")

    async def post(self, path, payload):
        return await asyncio.wait_for(self._post(path, payload), 8)

    async def _post(self, path, payload):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        try:
            body = json.dumps(payload).encode()
            request = ("POST %s HTTP/1.1\r\nHost: %s:%d\r\nAuthorization: Bearer %s\r\n"
                       "Content-Type: application/json\r\nContent-Length: %d\r\n"
                       "Connection: close\r\n\r\n" % (path, self.host, self.port, self.token, len(body)))
            writer.write(request.encode())
            writer.write(body)
            await writer.drain()
            first, headers = await read_headers(reader)
            parts = first.split(" ")
            if len(parts) < 2 or parts[1] != "200":
                raise ValueError("gateway rejected request")
            body = await read_body(reader, headers, 4096)
            return json.loads(body)
        finally:
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), 1)
            except Exception:
                pass


async def process_commands(payload, controller, client, status):
    """An ack failure is recorded but must never replay the physical operation."""
    validate_poll(payload, len(controller.channels))
    for command in payload["commands"]:
        result = {"id": command["id"], "success": False}
        try:
            await controller.move(command["channel"], command["state"])
            result["success"] = True
        except Exception as error:
            result["error"] = str(error)[:120]
        result["status"] = status()
        try:
            # DNS resolution may block on MicroPython. Never start it while a
            # scheduled move has energized the servo rail.
            async with controller.lock:
                await client.post("/api/device/ack", result)
        except Exception:
            print("Gateway ack failed; motion will not be retried")
