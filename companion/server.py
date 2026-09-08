#!/usr/bin/env python3
"""Loopback USB Wi-Fi setup for an already-provisioned Auto Switch S2 Mini."""
import argparse
import glob
import hmac
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
MAX_BODY = 1024
REMOTE_TEMP = 'config.json.usb-setup.tmp'


class SetupError(Exception):
    """Public, deliberately credential-free error."""


def serial_ports():
    patterns = ('/dev/cu.usb*', '/dev/ttyACM*', '/dev/ttyUSB*')
    return sorted({port for pattern in patterns for port in glob.glob(pattern)})


def validate_settings(payload):
    if not isinstance(payload, dict) or set(payload) != {'port', 'ssid', 'password'}:
        raise SetupError('Choose a port and enter the Wi-Fi settings.')
    port, ssid, password = payload['port'], payload['ssid'], payload['password']
    if not isinstance(port, str) or port not in serial_ports():
        raise SetupError('That USB port is no longer available. Refresh the list.')
    if not isinstance(ssid, str) or '\0' in ssid or not 1 <= len(ssid.encode('utf-8')) <= 32:
        raise SetupError('Network names must contain 1–32 bytes and no null characters.')
    if not isinstance(password, str) or not 8 <= len(password) <= 63 or any(not 32 <= ord(c) <= 126 for c in password):
        raise SetupError('Use a personal Wi-Fi password of 8–63 printable ASCII characters.')
    return port, ssid, password


def mpremote_command():
    executable = ROOT / '.venv' / 'bin' / 'mpremote'
    return [str(executable)] if executable.is_file() else [sys.executable, '-m', 'mpremote']


def run_device(port, *args):
    try:
        result = subprocess.run(mpremote_command() + ['connect', port, *args],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=25, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise SetupError('USB communication failed. Check the connection and try again.') from None
    if result.returncode:
        # mpremote may echo file contents or exception details; never expose them.
        raise SetupError('USB communication failed. Check the connection and try again.')


def save_wifi(payload, private_root=None):
    port, ssid, password = validate_settings(payload)
    private = Path(private_root) if private_root else ROOT / '.local' / 's2'
    private.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(private, 0o700)
    uploaded = False
    activated = False
    try:
        with tempfile.TemporaryDirectory(prefix='usb-wifi-', dir=private) as directory:
            os.chmod(directory, 0o700)
            config_path = Path(directory) / 'config.json'
            descriptor = os.open(config_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(descriptor)
            # A failed read is never replaced with defaults.
            run_device(port, 'fs', 'cp', ':config.json', str(config_path))
            os.chmod(config_path, 0o600)
            try:
                if config_path.stat().st_size > 65536:
                    raise ValueError('oversize')
                config = json.loads(config_path.read_text(encoding='utf-8'))
                if not isinstance(config, dict) or not isinstance(config.get('wifi', {}), dict):
                    raise ValueError('shape')
            except (ValueError, UnicodeError, OSError):
                raise SetupError('The device configuration could not be read safely. No settings were written.') from None
            config.setdefault('wifi', {}).update(ssid=ssid, password=password)
            config_path.write_text(json.dumps(config), encoding='utf-8')
            os.chmod(config_path, 0o600)
            # Record intent before the copy, so a partial remote file is removed.
            uploaded = True
            run_device(port, 'fs', 'cp', str(config_path), ':' + REMOTE_TEMP)
            run_device(port, 'exec', "import os; os.rename('" + REMOTE_TEMP + "', 'config.json')")
            activated = True
            try:
                run_device(port, 'reset')
            except SetupError:
                return {'ok': True, 'saved': True, 'rebooting': False}
            return {'ok': True, 'saved': True, 'rebooting': True}
    finally:
        if uploaded and not activated:
            try:
                run_device(port, 'exec', "import os; os.remove('" + REMOTE_TEMP + "')")
            except SetupError:
                pass


class SetupServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address=('127.0.0.1', 8790)):
        if address[0] != '127.0.0.1':
            raise ValueError('USB setup must bind to 127.0.0.1')
        super().__init__(address, Handler)
        self.token = secrets.token_urlsafe(32)
        port = self.server_address[1]
        self.hosts = {'127.0.0.1:' + str(port), 'localhost:' + str(port)}
        self.origins = {'http://' + host for host in self.hosts}
        self.operation = threading.Lock()


def allowed_request(headers, hosts, origins, token, mutation=False, csrf=False):
    """Pure policy helper used by the HTTP handler and unit tests."""
    if headers.get('Host') not in hosts:
        return False
    origin = headers.get('Origin')
    if (mutation and origin not in origins) or (origin is not None and origin not in origins):
        return False
    if csrf or mutation:
        presented = headers.get('X-AutoSwitch-CSRF', '')
        if not isinstance(presented, str) or not presented.isascii() or not hmac.compare_digest(presented, token):
            return False
    return True


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, payload, content_type='application/json; charset=utf-8'):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def authorized(self, mutation=False, csrf=False):
        if not allowed_request(self.headers, self.server.hosts, self.server.origins,
                               self.server.token, mutation, csrf):
            self.reply(403, {'error': 'Request refused. Open the local setup page again.'})
            return False
        return True

    def do_GET(self):
        if not self.authorized(csrf=self.path == '/ports'):
            return
        if self.path == '/ports':
            self.reply(200, {'ports': serial_ports()})
        elif self.path in ('/', '/app.js', '/style.css'):
            filename, media = {'/': ('index.html', 'text/html; charset=utf-8'),
                               '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                               '/style.css': ('style.css', 'text/css; charset=utf-8')}[self.path]
            body = (Path(__file__).parent / filename).read_bytes()
            if self.path == '/':
                body = body.replace(b'{{CSRF}}', self.server.token.encode('ascii'))
            self.reply(200, body, media)
        else:
            self.reply(404, {'error': 'Not found.'})

    def do_POST(self):
        if not self.authorized(mutation=True):
            return
        if self.path != '/wifi':
            self.reply(404, {'error': 'Not found.'})
            return
        lengths = self.headers.get_all('Content-Length', [])
        if (self.headers.get('Transfer-Encoding') is not None or len(lengths) != 1
                or not lengths[0].isdigit() or not 0 < int(lengths[0]) <= MAX_BODY
                or self.headers.get('Content-Type', '').split(';')[0] != 'application/json'):
            self.reply(400, {'error': 'Invalid request.'})
            return
        if not self.server.operation.acquire(blocking=False):
            self.reply(409, {'error': 'USB setup is already running. Wait for it to finish.'})
            return
        try:
            self.connection.settimeout(5)
            payload = json.loads(self.rfile.read(int(lengths[0])))
            result = save_wifi(payload)
            self.reply(200, result)
        except SetupError as error:
            self.reply(400, {'error': str(error)})
        except Exception:
            self.reply(400, {'error': 'Setup could not finish. Check the USB connection and try again.'})
        finally:
            self.server.operation.release()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8790)
    args = parser.parse_args()
    server = SetupServer(('127.0.0.1', args.port))
    print('Open http://127.0.0.1:' + str(server.server_address[1]) + '/')
    print('Local USB setup only. Press Ctrl-C to stop.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
