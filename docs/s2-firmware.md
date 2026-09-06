# S2 Mini firmware and USB-only bring-up

Use `firmware/config.s2-demo.example.json` for the headerless ESP32-S2 Mini.
The `s2-demo` profile requires exactly one channel on GPIO16, no servo power
gate and no battery ADC. Both direct HTTP and Mac gateway transports are
supported. The example defaults to gateway transport and leaves movement
disabled and uncalibrated. Sample pulse widths are not calibrated endpoints.

## Installed board

On 2026-09-05, esptool identified the connected board as ESP32-S2FNR2,
4 MB flash and 2 MB embedded PSRAM. A complete 4,194,304-byte original flash
backup was saved locally before erasing. Official
[LOLIN S2 Mini MicroPython v1.29.0](https://micropython.org/download/LOLIN_S2_MINI/)
was installed at offset `0x1000`; esptool verified the written data hash.
The board subsequently reported the LOLIN_S2_MINI build through its USB REPL.

Private Wi-Fi credentials, client/device tokens, flash backup and test logs
are in the Git-ignored `.local/s2/` directory. Never publish that directory.
`config.json` on the board contains its Wi-Fi password and device token.

## Transfer or update

Keep the board disconnected from the battery/servo harness during USB setup.
The S2 Mini's VBUS pad connects directly to USB power; switching off the battery
alone does not isolate the servo rail. See [wiring precautions](s2-aa-poc.md).

1. Fill a private copy of the S2 example. For gateway transport, set `host`
   to the Mac's LAN IP, `port` to the gateway port and `token` to its device key.
   The website uses the separate client key. Reserve the Mac's IP in the router
   or update the board configuration if that address changes.
2. Copy the six Python modules and the private configuration with `mpremote`:

```sh
mpremote fs cp firmware/control.py firmware/hardware.py firmware/http_api.py firmware/gateway_client.py firmware/bench.py firmware/main.py :
mpremote fs cp .local/s2/config.json :config.json
mpremote reset
```

For direct transport also copy `firmware/www/` to `/www/` on the board and set
a non-placeholder `api_token`. Gateway mode serves the website from the Mac;
it does not expose a second web server on the board.

The local bring-up gateway uses port 8768. Its private restart helper is
`python3 .local/s2/run-gateway.py`; stop the existing gateway before restarting.
The website asks for the client token saved in `.local/s2/client-token.txt`.
The Mac must remain running and reachable for gateway control.

## Validation scope

The real board joined Wi-Fi, synchronized its clock and sent authenticated
status with `hardware_profile: s2-demo`, `platform: esp32`, `battery: null`
and `servo_power_gated: false`. The gateway rejects unauthenticated status
requests and movement requests for the disabled channel. Status also includes
MicroPython's numeric `reset_cause` to diagnose restarts.

Demo mode requests a one-second delay between completed polls; network overhead
adds to the interval. Daily mode disables Wi-Fi between polls, but does not put
the CPU into deep sleep or disconnect servo power. No battery-life claim follows
from these software modes.

During USB-only testing, demo check-ins arrived about every 1.8–1.9 seconds
and uptime increased continuously during a one-minute observation. Switching
to daily mode with a 10-second interval reproduced a restart, including with
no serial connection open. The next boot reported reset cause `1` (power-on);
the cause of the reset is not yet established. Daily mode is **not validated
on this board**. The gateway was returned to demo mode. Check USB power/cable
and the board's power behavior before using radio-off operation.

The 26 firmware tests and 14 gateway tests pass on the host. The broader suite
also reports a pre-existing stale BOM audit for the separately modified
`hardware/cad/generated/auto-switch.blend`; that model was not changed by
firmware provisioning.

Servo movement, PWM waveform, electrical assembly, battery operation and
mechanical fit have not been tested on this board. Leave `enabled` and
`calibrated` false until the assembled actuator has been calibrated.
