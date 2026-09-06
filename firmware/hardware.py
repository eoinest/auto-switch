"""Pico/S2 hardware boundary with explicit gated and powered demo profiles."""
from machine import ADC, Pin, PWM
from control import battery_reading, validate_hardware_config


class Hardware:
    def __init__(self, config):
        enable_pin = validate_hardware_config(config)
        self.enable = Pin(enable_pin, Pin.OUT, value=0) if enable_pin is not None else None
        self.pins = [c["pin"] for c in config["channels"]]
        self.pwms = {}
        for pin in self.pins:
            Pin(pin, Pin.OUT, value=0)
        self.battery_cfg = config.get("battery", {})
        self.adc = ADC(26) if self.battery_cfg.get("enabled") is True else None

    def power_on(self):
        # The AA demo rail is already powered; this cannot switch it.
        if self.enable is not None:
            self.enable.value(0)
        reading = self.battery()
        if reading is not None and reading["low"]:
            raise ValueError("battery below low_v; recharge before moving")
        if self.enable is not None:
            self.enable.value(1)

    def pulse(self, channel, microseconds):
        if channel not in self.pwms:
            self.pwms[channel] = PWM(Pin(self.pins[channel]), freq=50, duty_u16=0)
        self.pwms[channel].duty_ns(microseconds * 1000)

    def off(self):
        # Gated profile cuts the rail first. AA demo only stops control pulses;
        # it cannot guarantee loss of holding torque or remove servo power.
        if self.enable is not None:
            self.enable.value(0)
        for pwm in self.pwms.values():
            pwm.duty_u16(0)
            pwm.deinit()
        self.pwms = {}
        for pin in self.pins:
            Pin(pin, Pin.OUT, value=0)

    def battery(self):
        if self.adc is None:
            return None
        raw = sum(self.adc.read_u16() for _ in range(8)) // 8
        return battery_reading(raw, self.battery_cfg)
