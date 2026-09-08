"""BOOT-held browser updates on saved home Wi-Fi only."""
import binascii
import gc
import hashlib
import json
import os
import time
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from http_api import read_headers, token_matches

FILES = ('control.py', 'calibration.py', 'hardware.py', 'http_api.py',
         'gateway_client.py', 'bench.py', 'main.py', 'maintenance.py',
         'www/index.html', 'www/app.js', 'www/style.css', 'www/update.html')
MAGIC = b'AUTOSWITCH1\n'
MAX_BUNDLE = 512 * 1024
MAX_FILE = 64 * 1024


class BootHold:
    def __init__(self):
        self.armed = False
        self.since = None

    def update(self, value, now):
        if value:
            self.armed = True
            self.since = None
        elif self.armed:
            if self.since is None:
                self.since = now
            elif time.ticks_diff(now, self.since) >= 3000:
                self.armed = False
                return True
        return False


def credentials():
    import maintenance_cfg
    value = maintenance_cfg.PASSWORD
    if not isinstance(value, str) or not 24 <= len(value) <= 63 or not value.isalnum():
        raise ValueError('invalid private update password')
    if any(ord(c) > 127 for c in value):
        raise ValueError('invalid private update password')
    return value


async def choose_network(config, connect):
    import network
    # Explicitly disable AP mode even if an older firmware left it active.
    network.WLAN(network.WLAN.IF_AP).active(False)
    sta = network.WLAN(network.WLAN.IF_STA)
    try:
        await asyncio.wait_for(connect(sta, config['wifi']), 15)
        if sta.isconnected():
            return sta
    except (OSError, ValueError, asyncio.TimeoutError):
        pass
    return None


class BundleStream:
    def __init__(self, reader, length):
        self.reader, self.remaining = reader, length

    async def take(self, count):
        if count > self.remaining:
            raise ValueError('truncated bundle')
        result = bytearray()
        while len(result) < count:
            data = await self.reader.read(count - len(result))
            if not data:
                raise ValueError('truncated bundle')
            result.extend(data)
        self.remaining -= count
        return bytes(result)

    async def line(self):
        result = bytearray()
        while not result.endswith(b'\n'):
            if len(result) >= 256:
                raise ValueError('oversized record')
            result.extend(await self.take(1))
        return bytes(result)


def stage_path(index):
    return '.update-' + str(index)


def verify_staged(index, digest, name):
    sha = hashlib.sha256()
    path = stage_path(index)
    with open(path, 'rb') as stream:
        while True:
            data = stream.read(1024)
            if not data:
                break
            sha.update(data)
    if binascii.hexlify(sha.digest()).decode() != digest:
        raise ValueError('file verification failed')
    if name.endswith('.py'):
        gc.collect()
        with open(path) as stream:
            compile(stream.read(), name, 'exec')
        gc.collect()


async def stage_bundle(reader, length):
    if not 0 < length <= MAX_BUNDLE:
        raise ValueError('invalid bundle size')
    stream = BundleStream(reader, length)
    if await stream.take(len(MAGIC)) != MAGIC:
        raise ValueError('wrong bundle format')
    seen = set()
    while True:
        header = json.loads(await stream.line())
        if header == {'end': True}:
            if stream.remaining or seen != set(FILES):
                raise ValueError('incomplete or trailing bundle')
            return
        if not isinstance(header, dict) or set(header) != {'path', 'size', 'sha256'}:
            raise ValueError('invalid file record')
        name, size, digest = header['path'], header['size'], header['sha256']
        if not isinstance(name, str) or name not in FILES or name in seen:
            raise ValueError('unexpected or duplicate file')
        if type(size) is not int or not 0 < size <= MAX_FILE:
            raise ValueError('invalid file size')
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('invalid digest')
        index = FILES.index(name)
        with open(stage_path(index), 'wb') as output:
            remaining = size
            while remaining:
                chunk = await stream.take(min(1024, remaining))
                output.write(chunk)
                remaining -= len(chunk)
                await asyncio.sleep(0)
        if await stream.take(1) != b'\n':
            raise ValueError('missing file boundary')
        verify_staged(index, digest, name)
        seen.add(name)


def activate():
    # LittleFS rename-overwrite is atomic for each file, not for the full bundle.
    # Keep main last; USB is still the recovery path for failed activation.
    order = [name for name in FILES if name != 'main.py'] + ['main.py']
    for name in order:
        os.rename(stage_path(FILES.index(name)), name)


class UpdateAPI:
    def __init__(self, password, reset, static_path='www/update.html'):
        self.password, self.reset, self.static_path = password, reset, static_path
        self.busy = False
        self.rebooting = False
        self.connections = 0

    async def reboot(self):
        await asyncio.sleep(1)
        # BOOT low during reset selects ROM download instead of our application.
        import machine
        button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
        while not button.value():
            await asyncio.sleep(0.05)
        self.reset()

    async def dispatch(self, reader):
        first, headers = await asyncio.wait_for(read_headers(reader), 5)
        parts = first.split(' ')
        if len(parts) != 3 or parts[2] not in ('HTTP/1.0', 'HTTP/1.1'):
            raise ValueError('invalid request')
        method, path = parts[:2]
        if method == 'GET' and path in ('/', '/update'):
            with open(self.static_path, 'rb') as stream:
                body = stream.read(MAX_FILE + 1)
            if len(body) > MAX_FILE:
                raise ValueError('oversized page')
            return 200, ('text/html; charset=utf-8', body)
        if method != 'POST' or path != '/update':
            return 404, {'error': 'not found in update mode'}
        if not token_matches(headers.get('authorization', ''), self.password):
            return 401, {'error': 'incorrect update password'}
        if self.busy or self.rebooting:
            return 409, {'error': 'an update is already in progress'}
        self.busy = True
        try:
            media = headers.get('content-type', '').split(';')[0]
            value = headers.get('content-length', '')
            if media != 'application/octet-stream' or not value.isdigit() or len(value) > 6:
                raise ValueError('invalid upload headers')
            # Verify replacement behavior before any live file is touched.
            open('.update-probe-a', 'wb').close()
            open('.update-probe-b', 'wb').close()
            os.rename('.update-probe-a', '.update-probe-b')
            os.remove('.update-probe-b')
            await asyncio.wait_for(stage_bundle(reader, int(value)), 120)
            activate()
            self.rebooting = True
            return 200, {'ok': True, 'rebooting': True}
        finally:
            self.busy = False

    async def handle(self, reader, writer):
        self.connections += 1
        should_reboot = False
        try:
            if self.connections > 2:
                return
            try:
                code, data = await self.dispatch(reader)
                should_reboot = code == 200 and isinstance(data, dict) and data.get('rebooting') is True
            except Exception:
                # Neither uploaded source nor credentials enter logs/responses.
                code, data = 400, {'error': 'Update failed. Stay in update mode and retry; do not disconnect power during installation.'}
            mime, body = data if isinstance(data, tuple) else ('application/json', json.dumps(data).encode())
            writer.write(('HTTP/1.1 %d Response\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nContent-Security-Policy: default-src \'self\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; frame-ancestors \'none\'\r\n\r\n' % (code, mime, len(body))).encode())
            writer.write(body)
            await asyncio.wait_for(writer.drain(), 5)
        except Exception:
            pass
        finally:
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), 1)
            except Exception:
                pass
            self.connections -= 1
            if should_reboot:
                asyncio.create_task(self.reboot())


async def run(config, connect):
    import machine
    try:
        password = credentials()
    except Exception:
        print('Update mode needs private provisioning over USB. Servo remains disabled.')
        while True:
            await asyncio.sleep(1)
    sta = await choose_network(config, connect)
    if sta is None:
        print('Home Wi-Fi unavailable. Use USB companion to change credentials; no access point is created.')
    while sta is None:
        await asyncio.sleep(5)
        sta = await choose_network(config, connect)
    api = UpdateAPI(password, machine.reset)
    server = await asyncio.start_server(api.handle, '0.0.0.0', 80, backlog=2)
    print('Update mode: http://' + sta.ifconfig()[0] + '/update')
    try:
        while True:
            await asyncio.sleep(5)
            if not sta.isconnected() and not api.busy and not api.rebooting:
                await choose_network(config, connect)
    finally:
        server.close()
        await server.wait_closed()
