"""Small bounded HTTP/1.1 surface; API tokens never enter URLs or static files."""
import json
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

MAX_HEADER = 2048
MAX_BODY = 256
STATIC = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
          "/style.css": ("style.css", "text/css")}


async def read_headers(reader):
    data = bytearray()
    while not data.endswith(b"\r\n\r\n"):
        part = await reader.read(1)
        if not part:
            raise ValueError("incomplete headers")
        data.extend(part)
        if len(data) > MAX_HEADER:
            raise ValueError("headers too large")
    lines = bytes(data).decode("ascii").split("\r\n")
    headers = {}
    for line in lines[1:-2]:
        if ":" not in line:
            raise ValueError("invalid header")
        key, value = line.split(":", 1)
        key = key.strip().lower()
        if key in headers:
            raise ValueError("duplicate header")
        headers[key] = value.strip()
    if "transfer-encoding" in headers:
        raise ValueError("chunked bodies unsupported")
    return lines[0], headers


async def read_body(reader, headers, limit):
    value = headers.get("content-length", "0")
    if not value.isdigit() or len(value) > 6:
        raise ValueError("invalid content length")
    length = int(value)
    if length > limit:
        raise ValueError("body too large")
    data = bytearray()
    while len(data) < length:
        part = await reader.read(length - len(data))
        if not part:
            raise ValueError("incomplete body")
        data.extend(part)
    return bytes(data)


async def read_request(reader):
    first, headers = await read_headers(reader)
    parts = first.split(" ")
    if len(parts) != 3 or parts[2] not in ("HTTP/1.0", "HTTP/1.1"):
        raise ValueError("invalid request")
    method, path = parts[:2]
    if method not in ("GET", "POST") or not path.startswith("/"):
        raise ValueError("unsupported request")
    return method, path, headers, await read_body(reader, headers, MAX_BODY)


def token_matches(value, expected):
    # Full comparison avoids an early exit on a matching prefix.
    actual = "Bearer " + expected
    if len(value) != len(actual):
        return False
    different = 0
    for a, b in zip(value, actual):
        different |= ord(a) ^ ord(b)
    return different == 0


def validate_token(token):
    if (not isinstance(token, str) or not 24 <= len(token) <= 128
            or token.startswith("REPLACE")
            or any(not 33 <= ord(c) <= 126 for c in token)):
        raise ValueError("set a random 24-128 character API token")


def client_access(config):
    """Unauthenticated browser access is an explicit S2 direct-demo choice."""
    enabled = config.get("open_client", False)
    if type(enabled) is not bool:
        raise ValueError("open_client must be true or false")
    if enabled and (config.get("hardware_profile") != "s2-demo"
                    or config.get("transport", "direct") != "direct"):
        raise ValueError("open_client requires s2-demo with direct transport")
    return enabled


class API:
    def __init__(self, controller, status, token, static_root="www", open_client=False):
        if type(open_client) is not bool:
            raise ValueError("open_client must be true or false")
        if not open_client:
            validate_token(token)
        self.open_client = open_client
        self.controller, self.status, self.token = controller, status, token
        self.static_root = static_root
        self.connections = 0

    async def route(self, method, path, headers, body):
        if method == "GET" and path == "/api/access":
            return 200, {"open_client": self.open_client}
        if path.startswith("/api/"):
            if not self.open_client and not token_matches(headers.get("authorization", ""), self.token):
                return 401, {"error": "unauthorized"}
            if method == "GET" and path == "/api/status":
                return 200, self.status()
            if method == "POST" and path == "/api/switch":
                if headers.get("content-type", "").split(";")[0] != "application/json":
                    return 415, {"error": "application/json required"}
                try:
                    payload = json.loads(body)
                    if not isinstance(payload, dict) or set(payload) != {"channel", "state"}:
                        raise ValueError("expected channel and state only")
                    await self.controller.move(payload["channel"], payload["state"])
                    return 200, self.status()
                except ValueError as error:
                    return 400, {"error": str(error)}
                except RuntimeError:
                    return 409, {"error": "actuator busy"}
                except Exception:
                    return 503, {"error": "actuation failed; state unknown"}
            return 404, {"error": "not found"}
        if method == "GET" and path in STATIC:
            name, mime = STATIC[path]
            try:
                with open(self.static_root + "/" + name, "rb") as stream:
                    data = stream.read(65537)
                if len(data) > 65536:
                    raise OSError("static asset too large")
                return 200, (mime, data)
            except OSError:
                return 404, {"error": "UI asset missing"}
        return 404, {"error": "not found"}

    async def handle(self, reader, writer):
        self.connections += 1
        try:
            if self.connections > 4:
                return
            try:
                request = await asyncio.wait_for(read_request(reader), 4)
                code, data = await self.route(*request)
            except (ValueError, UnicodeError):
                code, data = 400, {"error": "malformed or oversized request"}
            except Exception:
                code, data = 408, {"error": "request timed out"}
            if isinstance(data, tuple):
                mime, body = data
            else:
                mime, body = "application/json", json.dumps(data).encode()
            header = ("HTTP/1.1 %d Response\r\nContent-Type: %s\r\nContent-Length: %d\r\n"
                      "Connection: close\r\nCache-Control: no-store\r\n"
                      "X-Content-Type-Options: nosniff\r\n"
                      "Content-Security-Policy: default-src 'self'; frame-ancestors 'none'\r\n\r\n"
                      % (code, mime, len(body)))
            writer.write(header.encode())
            writer.write(body)
            await asyncio.wait_for(writer.drain(), 4)
        except Exception:
            pass
        finally:
            self.connections -= 1
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), 1)
            except Exception:
                pass
