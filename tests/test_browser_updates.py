import asyncio
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'firmware'))
import maintenance as m
sys.path.insert(0, str(ROOT / 'tools'))
import build_update_bundle as builder
import wireless_update as provisioner


def bundle(files=None):
    result = bytearray(m.MAGIC)
    for name, data in files if files is not None else [(name, b'x=1\n') for name in m.FILES]:
        result.extend(json.dumps({'path': name, 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}).encode() + b'\n')
        result.extend(data + b'\n')
    return bytes(result + b'{"end":true}\n')


def reader(data):
    value = asyncio.StreamReader()
    value.feed_data(data)
    value.feed_eof()
    return value


class TemporaryDirectoryTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.previous = os.getcwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        Path('www').mkdir()

    def tearDown(self):
        os.chdir(self.previous)
        self.temp.cleanup()

    async def test_bundle_verifies_all_files_before_replacing(self):
        for name in m.FILES:
            Path(name).write_text('old\n')
        Path('config.json').write_text('private settings')
        Path('calibration.json').write_text('calibration')
        data = bundle()
        await m.stage_bundle(reader(data), len(data))
        self.assertTrue(all(Path(name).read_text() == 'old\n' for name in m.FILES))
        m.activate()
        self.assertTrue(all(Path(name).read_text() == 'x=1\n' for name in m.FILES))
        self.assertEqual(Path('config.json').read_text(), 'private settings')
        self.assertEqual(Path('calibration.json').read_text(), 'calibration')

    async def test_actual_builder_bundle_matches_device_contract(self):
        self.assertEqual(tuple(builder.ALLOWED_PATHS), m.FILES)
        data = builder.bundle_bytes(ROOT / 'firmware')
        await m.stage_bundle(reader(data), len(data))
        self.assertEqual(Path(m.stage_path(m.FILES.index('main.py'))).read_bytes(), (ROOT / 'firmware/main.py').read_bytes())

    async def test_invalid_and_truncated_bundles_never_touch_active_files(self):
        Path('main.py').write_text('active')
        cases = [bundle()[:-3], bundle() + b'extra', bundle([('config.json', b'bad')]),
                 bundle([('../main.py', b'bad')]), bundle([('main.py', b'x=1\n'), ('main.py', b'x=1\n')]),
                 bundle([('control.py', b'syntax error here')]), bundle().replace(b'x=1', b'x=2', 1)]
        for data in cases:
            with self.subTest(size=len(data)):
                with self.assertRaises((ValueError, SyntaxError)):
                    await m.stage_bundle(reader(data), len(data))
                self.assertEqual(Path('main.py').read_text(), 'active')

    async def test_bad_auth_and_parallel_upload_rejected_before_body(self):
        api = m.UpdateAPI('a' * 24, Mock())
        for token, busy, expected in [('bad', False, 401), ('a' * 24, True, 409)]:
            api.busy = busy
            data = ('POST /update HTTP/1.1\r\nAuthorization: Bearer %s\r\nContent-Length: 100\r\n\r\n' % token).encode()
            response = await api.dispatch(reader(data))
            self.assertEqual(response[0], expected)
        self.assertFalse(list(Path('.').glob('.update-*')))

    async def test_bad_hash_no_activation_or_reset(self):
        api = m.UpdateAPI('a' * 24, Mock())
        data = bundle().replace(b'x=1', b'x=2', 1)
        header = ('POST /update HTTP/1.1\r\nAuthorization: Bearer %s\r\nContent-Type: application/octet-stream\r\nContent-Length: %d\r\n\r\n' % ('a' * 24, len(data))).encode()
        with patch.object(m, 'activate') as activate:
            with self.assertRaises(ValueError):
                await api.dispatch(reader(header + data))
            activate.assert_not_called()
        self.assertFalse(api.rebooting)
        self.assertFalse(api.busy)
        api.reset.assert_not_called()

    async def test_wifi_credentials_cannot_be_changed_over_device_http(self):
        api = m.UpdateAPI('a' * 24, Mock())
        response = await api.dispatch(reader(('POST /update/wifi HTTP/1.1\r\nAuthorization: Bearer %s\r\nContent-Length: 0\r\n\r\n' % ('a' * 24)).encode()))
        self.assertEqual(response[0], 404)

    async def test_real_http_upload_and_page(self):
        api = m.UpdateAPI('a' * 24, Mock(), static_path=str(ROOT / 'firmware/www/update.html'))
        rebooted = asyncio.Event()
        async def fake_reboot():
            rebooted.set()
        api.reboot = fake_reboot
        server = await asyncio.start_server(api.handle, '127.0.0.1', 0)
        port = server.sockets[0].getsockname()[1]
        try:
            r, w = await asyncio.open_connection('127.0.0.1', port)
            w.write(b'GET /update HTTP/1.1\r\nHost: localhost\r\n\r\n')
            await w.drain()
            response = await r.read()
            self.assertTrue(response.startswith(b'HTTP/1.1 200'))
            self.assertIn(b'<html', response)
            w.close()
            await w.wait_closed()
            data = bundle()
            r, w = await asyncio.open_connection('127.0.0.1', port)
            w.write(('POST /update HTTP/1.1\r\nAuthorization: Bearer %s\r\nContent-Type: application/octet-stream\r\nContent-Length: %d\r\n\r\n' % ('a' * 24, len(data))).encode() + data)
            await w.drain()
            response = await r.read()
            self.assertTrue(response.startswith(b'HTTP/1.1 200'))
            await asyncio.wait_for(rebooted.wait(), 1)
            self.assertEqual(Path('main.py').read_text(), 'x=1\n')
            w.close()
            await w.wait_closed()
        finally:
            server.close()
            await server.wait_closed()


class ProvisionTests(unittest.TestCase):
    def test_private_credentials_reused_without_printing_or_command_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            private = Path(directory)
            with patch.object(provisioner, 'PRIVATE', private), patch.object(provisioner.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()) as out:
                provisioner.provision('test-port')
                secret = (private / 'update-password.txt').read_text().strip()
                provisioner.create_credentials()
            self.assertEqual(len(secret), 24)
            self.assertEqual((private / 'update-password.txt').read_text().strip(), secret)
            self.assertEqual((private / 'maintenance_cfg.py').stat().st_mode & 0o777, 0o600)
            self.assertNotIn(secret, out.getvalue())
            self.assertNotIn(secret, repr(run.call_args_list))
            commands = [item.args[0] for item in run.call_args_list]
            self.assertFalse(any('config.json' in arg or 'calibration.json' in arg for command in commands for arg in command))


if __name__ == '__main__':
    unittest.main()
