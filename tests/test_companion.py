"""USB companion config preservation, cleanup and local request boundaries."""
import http.client
import threading
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('companion_server', ROOT / 'companion/server.py')
companion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(companion)


class CompanionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.private = Path(self.temp.name) / 'private'
        self.payload = {'port': '/dev/cu.usbmodemTEST', 'ssid': 'New Wi-Fi', 'password': 'new-test-password'}
        self.old = {'wifi': {'ssid': 'old', 'password': 'old-test-password', 'hostname': 'auto-switch'},
                    'servo': {'gpio': 16, 'neutral': 83}, 'calibration': {'off': 71}, 'custom': [1, 2]}
        self.calls = []
        self.upload = None
        self.seen_files = []
        self.ports = patch.object(companion, 'serial_ports', return_value=[self.payload['port']])
        self.ports.start()
        self.addCleanup(self.ports.stop)

    def device(self, port, *args):
        self.calls.append((port, args))
        if args[:3] == ('fs', 'cp', ':config.json'):
            target = Path(args[3])
            self.seen_files.append(target)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(target.parent.stat().st_mode), 0o700)
            target.write_text(json.dumps(self.old))
        elif args[:2] == ('fs', 'cp'):
            target = Path(args[2])
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            self.upload = json.loads(target.read_text())

    def assert_clean(self):
        self.assertTrue(all(not path.exists() for path in self.seen_files))
        if self.private.exists():
            self.assertEqual(list(self.private.iterdir()), [])
            self.assertEqual(stat.S_IMODE(self.private.stat().st_mode), 0o700)

    def test_only_wifi_changes_and_atomic_remote_rename(self):
        with patch.object(companion, 'run_device', side_effect=self.device):
            result = companion.save_wifi(self.payload, self.private)
        expected = json.loads(json.dumps(self.old))
        expected['wifi'].update(ssid='New Wi-Fi', password='new-test-password')
        self.assertEqual(self.upload, expected)
        self.assertTrue(result['rebooting'])
        self.assertEqual(self.calls[1][1][-1], ':config.json.usb-setup.tmp')
        self.assertIn("os.rename('config.json.usb-setup.tmp', 'config.json')", self.calls[2][1][1])
        self.assertEqual(self.calls[3][1], ('reset',))
        self.assertNotIn(self.payload['password'], repr(self.calls))
        self.assert_clean()

    def test_failed_read_never_writes_or_resets(self):
        with patch.object(companion, 'run_device', side_effect=companion.SetupError('USB communication failed.')) as run:
            with self.assertRaises(companion.SetupError):
                companion.save_wifi(self.payload, self.private)
        self.assertEqual(run.call_count, 1)
        self.assert_clean()

    def test_malformed_config_never_writes(self):
        def malformed(port, *args):
            self.calls.append(args)
            target = Path(args[3])
            self.seen_files.append(target)
            target.write_text('{broken')
        with patch.object(companion, 'run_device', side_effect=malformed):
            with self.assertRaisesRegex(companion.SetupError, 'No settings were written'):
                companion.save_wifi(self.payload, self.private)
        self.assertEqual(len(self.calls), 1)
        self.assert_clean()

    def test_invalid_wifi_object_never_writes(self):
        self.old['wifi'] = ['wrong type']
        with patch.object(companion, 'run_device', side_effect=self.device):
            with self.assertRaises(companion.SetupError):
                companion.save_wifi(self.payload, self.private)
        self.assertIsNone(self.upload)
        self.assert_clean()

    def test_failed_upload_attempts_remote_cleanup_and_cleans_local(self):
        def fail_upload(port, *args):
            self.device(port, *args)
            if args[:2] == ('fs', 'cp') and args[2] != ':config.json':
                raise companion.SetupError('USB communication failed.')
        with patch.object(companion, 'run_device', side_effect=fail_upload):
            with self.assertRaises(companion.SetupError):
                companion.save_wifi(self.payload, self.private)
        self.assertIn('os.remove', self.calls[-1][1][1])
        self.assertFalse(any(args == ('reset',) for _, args in self.calls))
        self.assert_clean()

    def test_failed_rename_no_reset(self):
        def fail_rename(port, *args):
            self.device(port, *args)
            if args[0] == 'exec' and 'os.rename' in args[1]:
                raise companion.SetupError('USB communication failed.')
        with patch.object(companion, 'run_device', side_effect=fail_rename):
            with self.assertRaises(companion.SetupError):
                companion.save_wifi(self.payload, self.private)
        self.assertFalse(any(args == ('reset',) for _, args in self.calls))
        self.assert_clean()

    def test_reset_failure_reports_saved_without_false_restart(self):
        def fail_reset(port, *args):
            self.device(port, *args)
            if args == ('reset',):
                raise companion.SetupError('USB communication failed.')
        with patch.object(companion, 'run_device', side_effect=fail_reset):
            result = companion.save_wifi(self.payload, self.private)
        self.assertEqual(result, {'ok': True, 'saved': True, 'rebooting': False})
        self.assert_clean()

    def test_port_allowlist_and_wifi_validation(self):
        invalid = [dict(self.payload, port='/tmp/not-a-device'), dict(self.payload, password='short'),
                   dict(self.payload, ssid='x\0y'), dict(self.payload, ssid='é' * 17),
                   dict(self.payload, password='nonasciié'), dict(self.payload, extra='field')]
        with patch.object(companion, 'run_device') as run:
            for payload in invalid:
                with self.subTest(payload={k: v for k, v in payload.items() if k != 'password'}):
                    with self.assertRaises(companion.SetupError):
                        companion.save_wifi(payload, self.private)
            run.assert_not_called()

    def test_subprocess_captured_no_sensitive_error_output(self):
        result = subprocess.CompletedProcess([], 1, stdout=b'private config', stderr=b'private password')
        with patch.object(companion.subprocess, 'run', return_value=result) as run:
            with self.assertRaises(companion.SetupError) as caught:
                companion.run_device(self.payload['port'], 'fs', 'cp', ':config.json', '/tmp/config')
        self.assertNotIn('private', str(caught.exception))
        self.assertEqual(run.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(run.call_args.kwargs['stderr'], subprocess.PIPE)
        self.assertEqual(run.call_args.kwargs['timeout'], 25)

    def test_host_origin_and_csrf_boundaries(self):
        hosts = {'127.0.0.1:8790', 'localhost:8790'}
        origins = {'http://' + host for host in hosts}
        good = {'Host': '127.0.0.1:8790', 'Origin': 'http://127.0.0.1:8790', 'X-AutoSwitch-CSRF': 'random-token'}
        def allowed(headers, **kwargs):
            return companion.allowed_request(headers, hosts, origins, 'random-token', **kwargs)
        self.assertTrue(allowed(good, mutation=True))
        self.assertTrue(allowed({'Host': 'localhost:8790'}))
        self.assertFalse(allowed(dict(good, Host='evil.example:8790'), mutation=True))
        self.assertFalse(allowed(dict(good, Origin='https://evil.example'), mutation=True))
        self.assertFalse(allowed({'Host': '127.0.0.1:8790', 'X-AutoSwitch-CSRF': 'random-token'}, mutation=True))
        self.assertFalse(allowed({'Host': '127.0.0.1:8790'}, csrf=True))
        self.assertFalse(allowed(dict(good, **{'X-AutoSwitch-CSRF': 'wrong'}), mutation=True))
        self.assertFalse(allowed(dict(good, **{'X-AutoSwitch-CSRF': 'é'}), mutation=True))


    def test_http_page_ports_and_write_protection(self):
        server = companion.SetupServer(('127.0.0.1', 0))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        host = '127.0.0.1:' + str(server.server_address[1])
        def request(method, path, body=None, headers=None):
            connection = http.client.HTTPConnection('127.0.0.1', server.server_address[1], timeout=3)
            try:
                connection.request(method, path, body=body, headers=headers or {})
                response = connection.getresponse()
                return response.status, dict(response.getheaders()), response.read()
            finally:
                connection.close()
        status, headers, body = request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn(server.token.encode(), body)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
        self.assertEqual(request('GET', '/', headers={'Host': 'evil.example'})[0], 403)
        self.assertEqual(request('GET', '/ports')[0], 403)
        self.assertEqual(request('GET', '/ports', headers={'X-AutoSwitch-CSRF': server.token})[0], 200)
        payload = json.dumps(self.payload)
        valid = {'Origin': 'http://' + host, 'X-AutoSwitch-CSRF': server.token, 'Content-Type': 'application/json'}
        with patch.object(companion, 'save_wifi', return_value={'ok': True, 'saved': True, 'rebooting': True}) as save:
            self.assertEqual(request('POST', '/wifi', payload, {'Content-Type': 'application/json'})[0], 403)
            self.assertEqual(request('POST', '/wifi', payload, dict(valid, Origin='http://evil.example'))[0], 403)
            save.assert_not_called()
            self.assertEqual(request('POST', '/wifi', payload, valid)[0], 200)
            save.assert_called_once_with(self.payload)
            self.assertEqual(request('POST', '/wifi', 'x' * 1025, valid)[0], 400)
            self.assertEqual(request('POST', '/wifi', payload, dict(valid, **{'Transfer-Encoding': 'chunked'}))[0], 400)
            self.assertEqual(save.call_count, 1)


if __name__ == '__main__':
    unittest.main()
