"""USB REPL bench control, including original Pico without WiFi."""
import json
import uasyncio as asyncio
from machine import Pin
from control import Controller
from hardware import Hardware

Pin(15, Pin.OUT, value=0)


def move(channel, state):
    """Same calibrated bounded cycle as LAN control; never raw arbitrary angles."""
    with open("config.json") as stream:
        config = json.load(stream)
    hardware = Hardware(config)
    try:
        controller = Controller(config, hardware)
        asyncio.run(controller.move(channel, state))
        print(controller.status_channels())
    finally:
        hardware.off()


def off():
    """Emergency rail disable on the documented default pin."""
    Pin(15, Pin.OUT, value=0)


def neutral(channel=0):
    """Detached-horn alignment only: neutral pulse for 300ms, then power off."""
    with open("config.json") as stream:
        config = json.load(stream)
    hardware = Hardware(config)
    try:
        controller = Controller(config, hardware)  # validate pulse/pin bounds
        if type(channel) is not int or not 0 <= channel < len(controller.channels):
            raise ValueError("invalid channel")
        async def align():
            hardware.power_on()
            await asyncio.sleep(0.05)
            hardware.pulse(channel, controller.channels[channel]["neutral_us"])
            await asyncio.sleep(0.3)
        asyncio.run(align())
    finally:
        hardware.off()
