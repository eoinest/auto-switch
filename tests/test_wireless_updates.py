import asyncio
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch, mock_open

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


updater = load('wireless_tool', 'tools/wireless_update.py')
startup = load('wireless_start', 'firmware/wireless_updates.py')


class WirelessTests(unittest.TestCase):
    def test_opt_in_and_password_not_logged(self):
        server = Mock()
        cfg = types.SimpleNamespace(PASS='testONLY9')
        with patch.dict(sys.modules, {'webrepl': server, 'webrepl_cfg': cfg}), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertFalse(startup.start({}))
            self.assertTrue(startup.start({'hardware_profile': 's2-demo'}))
            server.start.assert_called_once_with(password=cfg.PASS)
        self.assertNotIn(cfg.PASS, out.getvalue())

    def test_bad_or_missing_password_does_not_start_server(self):
        for value in (None, '', 'x' * 10, 'bad\npass', 'é23456789'):
            server = Mock()
            with patch.dict(sys.modules, {'webrepl': server, 'webrepl_cfg': types.SimpleNamespace(PASS=value)}), patch('builtins.print'):
                self.assertFalse(startup.start({'hardware_profile': 's2-demo'}))
            server.start.assert_not_called()

    def test_allowlist_excludes_settings_and_calibration(self):
        paths = [name for _, name in updater.manifest()]
        self.assertIn('wireless_updates.py', paths)
        for name in ('config.json', 'calibration.json', 'webrepl_cfg.py', 'boot.py'):
            self.assertNotIn(name, paths)
        self.assertTrue(all(path.is_file() for path, _ in updater.manifest()))
        self.assertTrue(updater.activate_source(updater.manifest()).splitlines()[-1].endswith("'main.py')"))

    def test_private_password_generation_reuses_secret_and_restricts_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            private = Path(directory) / 'private'
            with patch.object(updater, 'PRIVATE', private), patch.object(updater, 'PASSWORD', private / 'webrepl-password.txt'):
                path = updater.create_credentials()
                value = updater.password()
                self.assertEqual(len(value), 9)
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                updater.create_credentials()
                self.assertEqual(updater.password(), value)

    def test_verification_failure_never_activates_or_resets(self):
        sock, ws = Mock(), Mock()
        with patch.object(updater, 'connect', return_value=(sock, ws)), patch.object(updater, 'stop_application'), patch.object(updater, 'execute') as execute, patch.object(updater, 'stage', side_effect=OSError('corruption')), patch.object(updater, 'wait_http') as wait:
            with self.assertRaises(OSError):
                updater.update('test.local')
            self.assertEqual(execute.call_count, 1)  # filesystem probe only
            ws.write.assert_not_called()
            wait.assert_not_called()
            sock.close.assert_called_once()

    def test_stage_detects_changed_readback(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'module.py'
            source.write_text('original')
            def corrupt(ws, local, remote):
                Path(local).write_text('corrupt')
            with patch.object(updater.client, 'put_file'), patch.object(updater.client, 'get_file', side_effect=corrupt):
                with self.assertRaisesRegex(OSError, 'Read-back'):
                    updater.stage(Mock(), [(source, 'module.py')])

    def test_closed_socket_during_ignored_frame_fails_instead_of_looping(self):
        sock = Mock()
        sock.recv.side_effect = [b'\x81\x03', b'']
        with self.assertRaises(OSError):
            updater.client.websocket(sock).read(1)

    def test_real_repl_sync_before_upload(self):
        ws = Mock()
        with patch.object(updater, 'read_until') as read, patch.object(updater.secrets, 'token_hex', return_value='randommarker'), patch.object(updater.time, 'sleep'):
            updater.stop_application(ws)
        self.assertEqual(read.call_args_list[0].args[1], b'\r\nUPDATE_randommarker\r\n')
        self.assertEqual(read.call_args_list[1].args[1], b'>>> ')
        self.assertEqual(ws.write.call_args_list[0].args[0], b'\x03')

    def test_keyboard_interrupt_deinitializes_actual_hardware_synchronously(self):
        sys.path.insert(0, str(ROOT / 'firmware'))
        hardware = Mock()
        with patch.dict(sys.modules, {'uasyncio': asyncio, 'hardware': types.SimpleNamespace(Hardware=Mock(return_value=hardware))}):
            main = load('wireless_main', 'firmware/main.py')
        def interrupted(coro):
            coro.close()
            raise KeyboardInterrupt()
        with patch('builtins.open', mock_open(read_data='{}')), patch.object(main, 'load_calibration'), patch.object(main.asyncio, 'run', side_effect=interrupted):
            with self.assertRaises(KeyboardInterrupt):
                main.start()
        hardware.off.assert_called_once()


if __name__ == '__main__':
    unittest.main()
