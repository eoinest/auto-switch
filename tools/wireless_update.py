#!/usr/bin/env python3
"""Password-protected MicroPython application updates; never writes device config."""
import argparse
import base64
import contextlib
import hashlib
import io
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/vendor/webrepl"))
import client

PRIVATE = ROOT / ".local/s2"
PASSWORD = PRIVATE / "webrepl-password.txt"
MODULES = ("control.py", "calibration.py", "hardware.py", "http_api.py",
           "gateway_client.py", "bench.py", "wireless_updates.py", "main.py")
ASSETS = ("www/index.html", "www/app.js", "www/style.css")


def manifest():
    # Explicit allowlist: no Wi-Fi settings, calibration or update credentials.
    return [(ROOT / "firmware" / name, name) for name in MODULES + ASSETS]


def password():
    value = PASSWORD.read_text().strip()
    if len(value) != 9 or not value.isascii() or not value.isalnum():
        raise ValueError("Invalid local WebREPL password; provision over USB again")
    return value


def create_credentials():
    PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not PASSWORD.exists():
        value = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(9))
        with os.fdopen(os.open(PASSWORD, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as stream:
            stream.write(value + '\n')
    os.chmod(PASSWORD, 0o600)
    value = password()
    cfg = PRIVATE / "webrepl_cfg.py"
    with os.fdopen(os.open(cfg, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as stream:
        stream.write('PASS = ' + repr(value) + '\n')
    os.chmod(cfg, 0o600)
    return cfg


def provision(port):
    """One-time setup on an already configured board; no flash erase or config copy."""
    cfg = create_credentials()
    executable = ROOT / '.venv/bin/mpremote'
    base = [str(executable) if executable.exists() else 'mpremote', 'connect', port]
    # mpremote receives only file paths, never the password as an argument.
    subprocess.run(base + ['exec', 'import webrepl; print("WebREPL available")'], check=True)
    subprocess.run(base + ['fs', 'cp', str(ROOT / 'firmware/wireless_updates.py'),
                          str(ROOT / 'firmware/main.py'), str(cfg), ':'], check=True)
    subprocess.run(base + ['reset'], check=True)
    print('Installed wireless update support. Local credentials saved privately.')


def connect(host):
    sock = socket.create_connection((host, 8266), timeout=15)
    try:
        nonce = base64.b64encode(secrets.token_bytes(16))
        sock.sendall(b'GET / HTTP/1.1\r\nHost: webrepl\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Key: ' + nonce + b'\r\nSec-WebSocket-Version: 13\r\n\r\n')
        header = bytearray()
        while not header.endswith(b'\r\n\r\n'):
            data = sock.recv(1)
            if not data or len(header) > 8192:
                raise OSError('Invalid WebREPL handshake')
            header.extend(data)
        if not header.startswith(b'HTTP/1.1 101 '):
            raise OSError('WebREPL upgrade refused')
        ws = client.websocket(sock)
        client.login(ws, password())
        client.get_ver(ws)  # Authenticate before sending Ctrl-C or touching files.
        return sock, ws
    except BaseException:
        sock.close()
        raise


def read_until(ws, suffix, limit=65536):
    result = bytearray()
    while not result.endswith(suffix):
        result.extend(ws.read(1, text_ok=True))
        if len(result) > limit:
            raise OSError('Unexpected WebREPL response')
    return bytes(result)


def execute(ws, source):
    marker = 'UPDATE_' + secrets.token_hex(8)
    # One friendly-REPL line; token printed on its own line proves completion.
    ws.write(('exec(' + repr(source + '\nprint(' + repr(marker) + ')') + ')\r').encode(), client.WEBREPL_FRAME_TXT)
    # Ignore any stale login/interrupt prompts. Only our random marker on its
    # own output line proves execution; its escaped appearance in echo cannot.
    read_until(ws, ('\r\n' + marker + '\r\n').encode())
    read_until(ws, b'>>> ')


def stop_application(ws):
    ws.write(b'\x03', client.WEBREPL_FRAME_TXT)
    # A WebREPL login emits a synthetic >>> even when main.py is still running.
    # Confirm a real command executes rather than trusting that stale prompt.
    time.sleep(0.3)
    # main.start's synchronous finally stops PWM before reaching the REPL.
    # Reinforce the current POC pin low.
    execute(ws, 'import machine\nmachine.Pin(16, machine.Pin.OUT, value=0)')


def stage(ws, files):
    with tempfile.TemporaryDirectory(prefix='auto-switch-verify-') as folder:
        for index, (local, remote) in enumerate(files):
            destination = '.ota-' + str(index)
            check = Path(folder) / str(index)
            with contextlib.redirect_stdout(io.StringIO()):
                client.put_file(ws, str(local), destination)
                client.get_file(ws, str(check), destination)
            if hashlib.sha256(local.read_bytes()).digest() != hashlib.sha256(check.read_bytes()).digest():
                raise OSError('Read-back verification failed: ' + remote)
            print('Verified ' + remote)


def activate_source(files):
    # Commit main.py last. LittleFS rename replaces a destination atomically,
    # but the entire bundle is NOT atomic and has no automatic rollback.
    order = [i for i, (_, name) in enumerate(files) if name != 'main.py']
    order += [i for i, (_, name) in enumerate(files) if name == 'main.py']
    return 'import os\n' + '\n'.join('os.rename(%r, %r)' % ('.ota-' + str(i), files[i][1]) for i in order)


def wait_http(host):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen('http://' + host + '/', timeout=3) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(2)
    raise OSError('Update sent but website did not return; do not assume successful startup')


def update(host):
    files = manifest()
    for local, _ in files:
        if not local.is_file():
            raise ValueError('Missing application file: ' + str(local))
        if local.suffix == '.py':
            compile(local.read_bytes(), str(local), 'exec')
    sock, ws = connect(host)
    try:
        stop_application(ws)
        print('Application stopped; servo PWM off. Keep power on until finished.')
        # Fail before transfers on unsupported filesystems rather than delete
        # existing files to emulate rename-overwrite (which risks losing them).
        execute(ws, "import os\nopen('.ota-probe-a','w').close()\nopen('.ota-probe-b','w').close()\nos.rename('.ota-probe-a','.ota-probe-b')\nos.remove('.ota-probe-b')")
        stage(ws, files)
        for index, (_, name) in enumerate(files):
            if name.endswith('.py'):
                execute(ws, "import gc\ngc.collect()\nwith open(%r) as f:\n compile(f.read(), %r, 'exec')\ngc.collect()" % ('.ota-' + str(index), name))
        execute(ws, activate_source(files))
        ws.write(b'import machine; machine.reset()\r', client.WEBREPL_FRAME_TXT)
    finally:
        sock.close()
    wait_http(host)
    print('Update complete: http://' + host + '/')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='auto-switch.local')
    sub = parser.add_subparsers(dest='command', required=True)
    usb = sub.add_parser('provision', help='One-time USB setup; disconnect battery/servo harness first')
    usb.add_argument('--port', required=True)
    sub.add_parser('check', help='Authenticate over Wi-Fi without moving or stopping the servo')
    sub.add_parser('push', help='Stop application, upload/verify code and website, restart')
    args = parser.parse_args()
    try:
        if args.command == 'provision':
            provision(args.port)
        elif args.command == 'check':
            sock, _ = connect(args.host)
            sock.close()
            print('Wireless authentication succeeded.')
        else:
            update(args.host)
    except (OSError, ValueError, AssertionError, subprocess.CalledProcessError):
        # Never echo password-bearing protocol data or configuration exceptions.
        print('Update/setup failed. Check connection and private credentials. If push started, the app may remain stopped; see docs/wireless-updates.md.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
