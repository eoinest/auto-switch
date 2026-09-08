"""Copy with companion modules to Pico W or S2 Mini running MicroPython."""
import json
import time
import sys
import uasyncio as asyncio
from control import Controller, Scheduler
from calibration import load_calibration, save_calibration
from hardware import Hardware
from http_api import API, client_access
from gateway_client import GatewayClient, validate_poll, process_commands


def configure_hostname(network, config):
    """Set the optional local network name before Wi-Fi starts."""
    hostname = config.get("hostname")
    if hostname is None:
        return
    if (not isinstance(hostname, str) or not 1 <= len(hostname) <= 63
            or hostname[0] == "-" or hostname[-1] == "-"
            or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in hostname)):
        raise ValueError("hostname must be 1-63 lowercase ASCII letters, digits or internal hyphens")
    network.hostname(hostname)


class Clock:
    def __init__(self):
        self.previous = time.ticks_ms()
        self.elapsed_ms = 0
        self.last_sync_ms = None
        self.next_sync_ms = 0

    def tick(self):
        current = time.ticks_ms()
        self.elapsed_ms += time.ticks_diff(current, self.previous)
        self.previous = current

    def synced(self):
        return self.last_sync_ms is not None and self.elapsed_ms - self.last_sync_ms < 86400000

    def sync(self):
        if self.elapsed_ms < self.next_sync_ms:
            return
        self.next_sync_ms = self.elapsed_ms + 60000
        try:
            import ntptime
            ntptime.timeout = 2
            ntptime.settime()
            if 2024 <= time.localtime()[0] <= 2099:
                self.last_sync_ms = self.elapsed_ms
                self.next_sync_ms = self.elapsed_ms + 21600000
        except Exception:
            print("NTP unavailable; schedules need a recent successful UTC sync")


def wifi_txpower(wifi):
    """Optional ESP32 radio diagnostic setting; retain platform defaults otherwise."""
    if "txpower_dbm" not in wifi:
        return None
    value = wifi["txpower_dbm"]
    if sys.platform != "esp32":
        raise ValueError("wifi.txpower_dbm is only supported on ESP32")
    if type(value) not in (int, float) or not 2 <= value <= 20:
        raise ValueError("wifi.txpower_dbm must be a finite number from 2 to 20")
    return value


async def connect(wlan, wifi):
    txpower = wifi_txpower(wifi)
    if wlan.isconnected():
        return
    wlan.active(True)
    if txpower is not None:
        wlan.config(txpower=txpower)
    wlan.connect(wifi["ssid"], wifi["password"])
    for _ in range(60):
        if wlan.isconnected():
            return
        await asyncio.sleep(0.2)
    wlan.active(False)
    raise OSError("WiFi connection timed out")


async def maintain_clock_and_schedules(clock, scheduler, controller):
    while True:
        clock.tick()
        for entry in scheduler.due(time.localtime(), clock.synced()):
            try:
                # Network housekeeping uses the same guard because DNS/NTP
                # may block the interpreter. A due local event waits for it.
                while controller.lock.locked():
                    await asyncio.sleep(0.05)
                await controller.move(entry["channel"], entry["state"])
            except Exception as error:
                print("Schedule skipped:", str(error))
        await asyncio.sleep(1)


async def run(config, hardware=None):
    hardware = hardware if hardware is not None else Hardware(config)
    import machine
    reset_cause = machine.reset_cause()
    scheduler_task = None
    try:
        controller = Controller(config, hardware, persist=save_calibration)
        scheduler = Scheduler(config.get("schedules_utc", []), len(controller.channels))
        clock = Clock()
        transport = config.get("transport", "direct")
        if transport not in ("direct", "gateway"):
            raise ValueError("transport must be direct or gateway")
        try:
            import network
            configure_hostname(network, config)
            wlan = network.WLAN(network.STA_IF)
        except (ImportError, AttributeError):
            print("No WiFi hardware: use USB REPL import bench; bench.move(0, 'on')")
            return

        def status():
            clock.tick()
            return {"device": config.get("device", "auto-switch"),
                    "channels": controller.status_channels(), "battery": hardware.battery(),
                    "uptime": clock.elapsed_ms // 1000, "clock_synced": clock.synced(),
                    "busy": controller.busy, "transport": transport,
                    "calibration": controller.calibration_status(),
                    "calibration_available": config.get("hardware_profile") == "s2-demo" and transport == "direct",
                    "hardware_profile": config.get("hardware_profile", "gated"),
                    "platform": sys.platform, "reset_cause": reset_cause,
                    "servo_power_gated": controller.power_enable_pin is not None}

        # Validate credentials before starting schedules or network operations.
        open_client = client_access(config)
        client = GatewayClient(config["gateway"]) if transport == "gateway" else None
        api = API(controller, status, config.get("api_token", ""),
                  open_client=open_client) if client is None else None
        wifi = config["wifi"]
        if not wifi.get("ssid"):
            raise ValueError("set wifi.ssid in config.json")
        scheduler_task = asyncio.create_task(maintain_clock_and_schedules(clock, scheduler, controller))
        if transport == "direct":
            while True:
                try:
                    async with controller.lock:
                        await connect(wlan, wifi)
                        clock.sync()
                    break
                except OSError as error:
                    print(str(error))
                    await asyncio.sleep(15)
            server = await asyncio.start_server(api.handle, "0.0.0.0", 80, backlog=2)
            print("auto-switch UI: http://" + wlan.ifconfig()[0])
            try:
                while True:
                    try:
                        async with controller.lock:
                            await connect(wlan, wifi)
                            clock.sync()
                    except OSError:
                        pass
                    await asyncio.sleep(30)
            finally:
                server.close()
                await server.wait_closed()
        else:
            mode, interval = "daily", 60
            while True:
                try:
                    async with controller.lock:
                        await connect(wlan, wifi)
                        clock.sync()
                        payload = await client.post("/api/device/poll", {"status": status()})
                    validate_poll(payload, len(controller.channels))
                    mode = payload["mode"]
                    interval = 1 if mode == "demo" else payload["poll_interval_s"]
                    await process_commands(payload, controller, client, status)
                except Exception as error:
                    print("Gateway poll failed:", str(error))
                    mode, interval = "daily", 30
                # Only Controller owns servo power during runtime; a local
                # schedule may be running while this transport becomes idle.
                if mode == "daily":
                    async with controller.lock:
                        wlan.disconnect()
                        wlan.active(False)
                await asyncio.sleep(interval)
    finally:
        if scheduler_task is not None:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except BaseException:
                pass
        hardware.off()


async def supervise(config, hardware):
    if config.get("hardware_profile") != "s2-demo" or config.get("transport", "direct") != "direct":
        return await run(config, hardware)
    import machine
    import maintenance
    button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    hold = maintenance.BootHold()
    task = asyncio.create_task(run(config, hardware))
    try:
        while True:
            if hold.update(button.value(), time.ticks_ms()):
                hardware.inhibit()
                if task is not None:
                    task.cancel()
                    try:
                        await task
                    except BaseException:
                        pass
                    task = None
                hardware.off()
                # Remove a legacy WebREPL listener if an older boot.py started it.
                if "webrepl" in sys.modules:
                    sys.modules["webrepl"].stop()
                await maintenance.run(config, connect)
                return
            if task is not None and task.done():
                try:
                    await task
                except Exception:
                    print("Application stopped; hold BOOT/0 for update recovery")
                task = None
                hardware.off()
            await asyncio.sleep(0.05)
    finally:
        hardware.inhibit()
        if task is not None:
            task.cancel()
            try:
                await task
            except BaseException:
                pass
        hardware.off()


def start():
    hardware = None
    try:
        with open("config.json") as stream:
            config = json.load(stream)
        load_calibration(config)
        hardware = Hardware(config)
        asyncio.run(supervise(config, hardware))
    except OSError as error:
        print("Startup stopped. Copy/edit config.example.json as config.json:", str(error))
    except Exception as error:
        print("Startup stopped; disconnect servo supply before troubleshooting:", str(error))
    finally:
        # KeyboardInterrupt can escape the event-loop poll without unwinding a
        # suspended coroutine on MicroPython. Clean up synchronously before REPL.
        if hardware is not None:
            hardware.off()


if __name__ == "__main__":
    start()
