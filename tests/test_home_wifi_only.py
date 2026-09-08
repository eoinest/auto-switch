"""Home-network-only maintenance must never turn the S2 into an access point."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'firmware'))
spec = importlib.util.spec_from_file_location('home_only_maintenance', ROOT / 'firmware/maintenance.py')
maintenance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(maintenance)


class StopLoop(BaseException):
    pass


class Interface:
    def __init__(self, access_point=False):
        self.access_point = access_point
        self.enabled = access_point  # simulate a previously enabled legacy AP
        self.connected = False
        self.active_calls = []

    def active(self, value=None):
        if value is not None:
            self.active_calls.append(value)
            if self.access_point and value:
                raise AssertionError('Home-only firmware enabled an AP')
            self.enabled = value
        return self.enabled

    def config(self, **kwargs):
        if self.access_point:
            raise AssertionError('Home-only firmware configured an AP')

    def isconnected(self):
        return self.connected

    def ifconfig(self):
        return ('192.0.2.9', '255.255.255.0', '192.0.2.1', '192.0.2.1')


class Network:
    def __init__(self):
        self.ap, self.sta = Interface(True), Interface()
        network = self

        class WLAN:
            IF_STA, IF_AP = 0, 1

            def __new__(cls, identifier):
                return network.ap if identifier == cls.IF_AP else network.sta

        self.module = types.SimpleNamespace(WLAN=WLAN)


class HomeWifiOnlyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.network = Network()
        self.config = {'wifi': {'ssid': 'Example home network', 'password': 'test-only-password'}}
        self.modules = patch.dict(sys.modules, {'network': self.network.module,
                                               'machine': types.SimpleNamespace(reset=Mock())})
        self.modules.start()
        self.addCleanup(self.modules.stop)

    def assert_no_ap(self):
        self.assertTrue(self.network.ap.active_calls)
        self.assertTrue(all(value is False for value in self.network.ap.active_calls))
        self.assertFalse(self.network.ap.enabled)

    async def test_saved_network_success_disables_old_ap(self):
        async def connect(sta, wifi):
            self.assertIs(sta, self.network.sta)
            self.assertIs(wifi, self.config['wifi'])
            self.assertFalse(self.network.ap.active())
            sta.connected = True
        self.assertIs(await maintenance.choose_network(self.config, connect), self.network.sta)
        self.assert_no_ap()

    async def test_connection_errors_return_no_network_without_creating_ap(self):
        for error in (OSError('unavailable'), ValueError('invalid'), asyncio.TimeoutError()):
            async def connect(sta, wifi):
                raise error
            self.assertIsNone(await maintenance.choose_network(self.config, connect))
            self.assert_no_ap()

    async def test_connect_return_without_valid_ip_is_not_success(self):
        self.assertIsNone(await maintenance.choose_network(self.config, AsyncMock()))
        self.assert_no_ap()

    async def test_timeout_after_sta_deactivation_does_not_require_disconnect(self):
        async def connect(sta, wifi):
            sta.active(False)
            raise OSError('connection timed out after stopping station')
        self.assertIsNone(await maintenance.choose_network(self.config, connect))
        self.assert_no_ap()

    async def test_cancellation_propagates_without_starting_ap(self):
        async def connect(sta, wifi):
            raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await maintenance.choose_network(self.config, connect)
        self.assert_no_ap()

    async def test_missing_home_network_retries_without_starting_http_or_ap(self):
        calls, delays = [], []
        async def connect(sta, wifi):
            calls.append(wifi)
            raise OSError('router unavailable')
        async def sleep(seconds):
            delays.append(seconds)
            if len(delays) == 3:
                raise StopLoop()
        start_server = AsyncMock()
        fake_asyncio = types.SimpleNamespace(wait_for=asyncio.wait_for,
                                            TimeoutError=asyncio.TimeoutError,
                                            sleep=sleep, start_server=start_server)
        with patch.object(maintenance, 'credentials', return_value='x' * 24), \
                patch.object(maintenance, 'asyncio', fake_asyncio), patch('builtins.print'):
            with self.assertRaises(StopLoop):
                await maintenance.run(self.config, connect)
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [5, 5, 5])
        start_server.assert_not_awaited()
        self.assert_no_ap()

    async def test_network_loss_retries_same_station_without_ap(self):
        calls, delays = [], []
        server = types.SimpleNamespace(close=Mock(), wait_closed=AsyncMock())
        async def connect(sta, wifi):
            calls.append(wifi)
            sta.connected = len(calls) == 1
            if not sta.connected:
                raise OSError('router disappeared')
        async def sleep(seconds):
            delays.append(seconds)
            if len(delays) == 1:
                self.network.sta.connected = False
            else:
                raise StopLoop()
        start_server = AsyncMock(return_value=server)
        fake_asyncio = types.SimpleNamespace(wait_for=asyncio.wait_for,
                                            TimeoutError=asyncio.TimeoutError,
                                            sleep=sleep, start_server=start_server)
        with patch.object(maintenance, 'credentials', return_value='x' * 24), \
                patch.object(maintenance, 'asyncio', fake_asyncio), patch('builtins.print'):
            with self.assertRaises(StopLoop):
                await maintenance.run(self.config, connect)
        self.assertEqual(len(calls), 2)
        start_server.assert_awaited_once()
        server.close.assert_called_once()
        server.wait_closed.assert_awaited_once()
        self.assert_no_ap()


if __name__ == '__main__':
    unittest.main()
