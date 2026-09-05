"""USB REPL bench control, including original Pico without WiFi."""
import json
import uasyncio as asyncio
from control import Controller
from hardware import Hardware


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
    """Stop signal output; only the gated profile can also disable the rail."""
    with open("config.json") as stream:
        config = json.load(stream)
    hardware = Hardware(config)
    hardware.off()
    if hardware.enable is None:
        print("PWM stopped; servo still powered. Disconnect supply to remove power.")


def neutral(channel=0):
    """Detached-horn alignment: neutral for 300ms, then profile-specific cleanup."""
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
