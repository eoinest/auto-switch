"""Test the ZIP-extracted app without Python/mpremote on PATH or a USB board."""
import json
import os
from pathlib import Path
import re
import select
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]


def request(url, token=None, post=False):
    headers = {'Origin': url.rsplit('/', 1)[0]} if post else {}
    if token:
        headers['X-AutoSwitch-CSRF'] = token
    return urllib.request.urlopen(urllib.request.Request(url, data=b'' if post else None, headers=headers), timeout=5)


def main():
    archive = ROOT / 'dist/companion/AutoSwitch-Setup-0.1.0-macOS-arm64.zip'
    with tempfile.TemporaryDirectory(prefix='Auto Switch Share Test ') as folder:
        subprocess.run(['ditto', '-x', '-k', str(archive), folder], check=True)
        app = Path(folder) / 'Auto Switch Setup.app'
        executable = app / 'Contents/MacOS/Auto Switch Setup'
        subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True)
        subprocess.run(['lipo', str(executable), '-verify_arch', 'arm64'], check=True)
        forbidden = {'config.json', 'maintenance_cfg.py', 'webrepl_cfg.py',
                     'wifi-password.txt', 'update-password.txt', '.local', '.env'}
        for path in app.rglob('*'):
            if path.name in forbidden:
                raise AssertionError('Private filename in bundle: ' + path.name)
        # No repository Python environment or user PYTHONPATH can rescue this test.
        env = {'PATH': '/usr/bin:/bin', 'HOME': os.environ['HOME'],
               'LANG': 'en_US.UTF-8', 'PYTHONUNBUFFERED': '1'}
        for args in (['--help'], ['connect', 'list']):
            result = subprocess.run([str(executable), '--device-command'] + args,
                                    cwd=folder, env=env, capture_output=True, timeout=20)
            if result.returncode:
                raise AssertionError('Bundled USB helper failed')
            if args == ['--help'] and b'mpremote' not in result.stdout:
                raise AssertionError('USB helper did not dispatch')
        process = subprocess.Popen([str(executable), '--no-browser'], cwd=folder,
                                   env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        try:
            if not select.select([process.stdout], [], [], 15)[0]:
                raise AssertionError('App did not start')
            line = process.stdout.readline()
            match = re.search(r'http://127\.0\.0\.1:\d+/', line)
            if not match:
                raise AssertionError('App did not report a loopback address')
            base = match.group(0)
            with request(base) as response:
                html = response.read().decode()
            token = re.search(r'name="csrf" content="([^"]+)"', html).group(1)
            for name in ('app.js', 'style.css'):
                with request(base + name) as response:
                    assert response.status == 200 and len(response.read()) > 50
            with request(base + 'ports', token) as response:
                assert isinstance(json.load(response)['ports'], list)
            try:
                request(base + 'quit', post=True)
            except urllib.error.HTTPError as error:
                assert error.code == 403
            else:
                raise AssertionError('Unauthenticated shutdown was accepted')
            with request(base + 'quit', token, post=True) as response:
                assert json.load(response)['ok'] is True
            assert process.wait(timeout=10) == 0
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
    print('PASS: extracted arm64 app, signature, file inventory, bundled USB helper, HTTP assets, port listing and authenticated quit.')


if __name__ == '__main__':
    main()
