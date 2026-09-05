"""Portable safety and scheduling logic; no hardware imports on a host."""
import time
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


def integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("invalid " + label)
    return value


def validate_channel(channel):
    for field in ("on_us", "off_us", "neutral_us"):
        integer(channel.get(field), 1100, 1900, field)
    if max(channel[k] for k in ("on_us", "off_us", "neutral_us")) - min(
        channel[k] for k in ("on_us", "off_us", "neutral_us")
    ) > 400:
        raise ValueError("pulse span exceeds 400 us; redesign travel")
    if not min(channel["on_us"], channel["off_us"]) < channel["neutral_us"] < max(channel["on_us"], channel["off_us"]):
        raise ValueError("neutral must lie between on and off")
    integer(channel.get("dwell_ms"), 50, 400, "dwell_ms")
    integer(channel.get("return_ms"), 50, 400, "return_ms")
    integer(channel.get("pin"), 0, 22, "servo pin")


class Controller:
    def __init__(self, config, hardware, sleep=None):
        self.config = config
        self.hardware = hardware
        if config.get("power_enable_pin", 15) != 15:
            raise ValueError("this wiring revision requires power_enable_pin 15")
        self.channels = config.get("channels", [])
        if not 1 <= len(self.channels) <= 2:
            raise ValueError("configure one or two channels")
        pins = []
        for channel in self.channels:
            validate_channel(channel)
            pins.append(channel["pin"])
        if len(set(pins)) != len(pins) or config.get("power_enable_pin", 15) in pins:
            raise ValueError("GPIO assignments overlap")
        self.lock = asyncio.Lock()
        self.sleep = sleep or asyncio.sleep
        self.states = ["unknown"] * len(self.channels)
        self.last_commands = [None] * len(self.channels)
        self.busy = False

    async def move(self, channel, state):
        integer(channel, 0, len(self.channels) - 1, "channel")
        if state not in ("on", "off"):
            raise ValueError("state must be on or off")
        cfg = self.channels[channel]
        validate_channel(cfg)
        if cfg.get("enabled") is not True or cfg.get("calibrated") is not True:
            raise ValueError("channel disabled or uncalibrated")
        # Reject excess work instead of queuing stale physical commands.
        if self.lock.locked():
            raise RuntimeError("actuator busy")
        async with self.lock:
            self.busy = True
            self.states[channel] = "unknown"
            try:
                await asyncio.wait_for(self._cycle(channel, cfg, state), 2)
                self.states[channel] = state
                self.last_commands[channel] = state
            finally:
                try:
                    self.hardware.off()
                finally:
                    self.busy = False

    async def _cycle(self, channel, cfg, state):
        self.hardware.off()
        self.hardware.power_on()
        await self.sleep(0.05)
        self.hardware.pulse(channel, cfg["neutral_us"])
        await self.sleep(cfg["return_ms"] / 1000)
        self.hardware.pulse(channel, cfg[state + "_us"])
        await self.sleep(cfg["dwell_ms"] / 1000)
        self.hardware.pulse(channel, cfg["neutral_us"])
        await self.sleep(cfg["return_ms"] / 1000)

    def status_channels(self):
        return [{"id": i, "name": c.get("name", "Switch " + str(i + 1)),
                 "state": self.states[i], "last_command": self.last_commands[i],
                 "enabled": c.get("enabled") is True,
                 "calibrated": c.get("calibrated") is True}
                for i, c in enumerate(self.channels)]


def battery_reading(raw, cfg):
    """Voltage is an ADC estimate; percent omitted without measured endpoints."""
    top = cfg.get("divider_top_ohms", 100000)
    bottom = cfg.get("divider_bottom_ohms", 47000)
    vref = cfg.get("adc_reference_v", 3.3)
    if not (1000 <= top <= 1000000 and 1000 <= bottom <= 1000000 and 3 <= vref <= 3.6):
        raise ValueError("invalid battery divider")
    voltage = raw / 65535 * vref * (top + bottom) / bottom
    percent = None
    empty, full = cfg.get("empty_v"), cfg.get("full_v")
    if empty is not None and full is not None and 0 < empty < full <= 20:
        percent = round(max(0, min(100, 100 * (voltage - empty) / (full - empty))))
    low_v = cfg.get("low_v", 4.4)
    if low_v is not None and not 0 < low_v < 20:
        raise ValueError("invalid battery low_v")
    return {"voltage": round(voltage, 2), "percent": percent, "estimated": True,
            "low": low_v is not None and voltage < low_v}


class Scheduler:
    """Once per matching UTC minute, no catch-up; valid synchronized time required."""
    def __init__(self, entries, channel_count):
        if len(entries) > 16:
            raise ValueError("at most 16 schedules")
        self.entries = entries
        self.seen = [None] * len(entries)
        for entry in entries:
            integer(entry.get("channel"), 0, channel_count - 1, "schedule channel")
            integer(entry.get("hour"), 0, 23, "UTC hour")
            integer(entry.get("minute"), 0, 59, "UTC minute")
            if entry.get("state") not in ("on", "off"):
                raise ValueError("invalid scheduled state")
            days = entry.get("days", list(range(7)))
            if not days or any(type(d) is not int or not 0 <= d <= 6 for d in days):
                raise ValueError("days use Monday=0 through Sunday=6")

    def due(self, now, synced):
        if not synced or not 2024 <= now[0] <= 2099:
            return []
        key = tuple(now[:5])
        result = []
        for i, entry in enumerate(self.entries):
            if (entry.get("enabled") is True and now[3] == entry["hour"]
                    and now[4] == entry["minute"]
                    and now[6] in entry.get("days", range(7)) and self.seen[i] != key):
                self.seen[i] = key
                result.append(entry)
        return result
