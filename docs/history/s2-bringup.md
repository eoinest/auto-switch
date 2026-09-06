# Historical S2 Mini bring-up notes

This records the earlier provisioning and gateway experiments. For the current
standalone, two-button POC, follow [the S2 firmware guide](../s2-firmware.md).
The gateway and daily/check-in modes below are not the current build.

Use `firmware/config.s2-demo.example.json` for the headerless ESP32-S2 Mini.
The `s2-demo` profile requires exactly one channel on GPIO16, no servo power
gate and no battery ADC. Both direct HTTP and Mac gateway transports are
supported. The example defaults to **direct transport**, with `open_client: true`:
the ESP32 serves the two-button **On / Off** website itself on port 80 and keeps
Wi-Fi active. No Mac gateway, mode selector or check-in interval is needed.
Movement remains disabled and uncalibrated. Sample pulse widths are not calibrated endpoints.

## Installed board

On 2026-09-05, esptool identified the connected board as ESP32-S2FNR2,
4 MB flash and 2 MB embedded PSRAM. A complete 4,194,304-byte original flash
backup was saved locally before erasing. Official
[LOLIN S2 Mini MicroPython v1.29.0](https://micropython.org/download/LOLIN_S2_MINI/)
was installed at offset `0x1000`; esptool verified the written data hash.
The board subsequently reported the LOLIN_S2_MINI build through its USB REPL.

Private Wi-Fi credentials, client/device tokens, flash backup and test logs
are in the Git-ignored `.local/s2/` directory. Never publish that directory.
`config.json` on the board contains its Wi-Fi password (and access tokens if
authenticated direct access or gateway transport is configured).

## Transfer or update

Keep the board disconnected from the battery/servo harness during USB setup.
The S2 Mini's VBUS pad connects directly to USB power; switching off the battery
alone does not isolate the servo rail. See [wiring precautions](../s2-aa-poc.md).

1. Fill a private copy of the S2 example with your Wi-Fi credentials. Keep
   `transport: "direct"` and `open_client: true` for the standalone demo.
   For authenticated browser access, use `open_client: false` and set a random
   24–128-character `api_token`. Credentials belong only in the ignored private copy.
2. Copy the six Python modules and the private configuration with `mpremote`:

```sh
mpremote fs cp firmware/control.py firmware/hardware.py firmware/http_api.py firmware/gateway_client.py firmware/bench.py firmware/main.py :
mpremote fs cp .local/s2/config.json :config.json
```

For direct transport also copy the three static assets to `/www/` before reset:

```sh
mpremote fs mkdir :www
mpremote fs cp firmware/www/index.html firmware/www/app.js firmware/www/style.css :www/
mpremote reset
```

Skip `mkdir` if the directory already exists. The USB console prints the board's
address as `auto-switch UI: http://...`. The S2 example also sets
`hostname: "auto-switch"` before Wi-Fi starts. Official ESP32 MicroPython's
[built-in mDNS responder](https://github.com/micropython/micropython/blob/v1.29.0/ports/esp32/network_wlan.c#L180-L195)
makes `http://auto-switch.local/` available on networks
and clients that support local multicast discovery. On the same Wi-Fi, use
that name or the printed numeric address on your phone; neither needs `:8768`.
Use a different hostname for each additional switch to avoid name collisions. `/api/access` lets the page discover
whether it should connect immediately or request a key. Open access applies only
to the explicitly selected S2 direct-demo profile. It does not bypass the enabled
and calibrated channel checks. A battery supply can replace USB after bring-up;
the Mac is not part of the direct control path.

### Optional ESP32 transmit-power diagnostic

The private `wifi` object may include `"txpower_dbm": 8.5` to reduce radio
transmit power during troubleshooting. Firmware applies it after activating
Wi-Fi and before connecting. This ESP32-only setting accepts finite numeric
values from 2 through 20 dBm; omit it to retain the platform default. It may
reduce Wi-Fi range. A successful connection at reduced transmit power does
**not** prove the USB cable or battery power supply is healthy, nor establish
battery life. The public example leaves this diagnostic setting unset.

## Optional legacy gateway transport

To use the Mac gateway again, set `transport: "gateway"`, `open_client: false`
and configure `gateway.host`, `gateway.port` and `gateway.token` in the private
configuration. Reserve the Mac's address in the router or update the host setting
when it changes. Gateway mode serves the website from the Mac; it does not expose
a second web server on the board.

The local bring-up gateway uses port 8768. Its private restart helper is
`python3 .local/s2/run-gateway.py`; stop the existing gateway before restarting.
The local prototype helper selects `--demo-only --open-client`. The website
shows only **On** and **Off**, and the gateway keeps the board in responsive
demo mode on every poll. `--demo-only` also replaces a saved daily-mode setting
and rejects API requests to enable check-in mode. It is distinct from `--demo`,
which simulates hardware. No channel is enabled or calibrated by this option.

With `--open-client`, the website opens
directly without asking for a key. Anyone who can reach this gateway can read
status and send control requests. This is a local-network convenience mode;
it does not create a public URL or change router settings. Device poll/ack
requests still require the private device token, and disabled or uncalibrated
channels still cannot move.

The gateway defaults to authenticated browser access. Remove `--open-client`
from the private helper and restart to restore the client-key prompt; the saved
client token remains in `.local/s2/client-token.txt`. For other launchers, opt in
explicitly with `python3 gateway/server.py --open-client --host 0.0.0.0` and supply
`AUTO_SWITCH_DEVICE_TOKEN` through the environment. A client token is optional
in this mode. Keep this prototype on the trusted LAN; do not forward its port.
The Mac must remain running and reachable for gateway control.

## Validation scope

The USB-connected S2 now serves the direct HTTP API on port 80. Both its
numeric LAN address and `auto-switch.local` returned HTTP 200 with
`transport: direct`, `platform: esp32`, and increasing uptime. The three served
UI assets matched the repository files byte for byte. This bring-up used the
optional 8.5 dBm transmit-power setting after intermittent USB connections;
the cause of those interruptions is not established. Servo channels remain
disabled and uncalibrated.

The following observations describe earlier gateway testing:

The real board joined Wi-Fi, synchronized its clock and sent authenticated
status with `hardware_profile: s2-demo`, `platform: esp32`, `battery: null`
and `servo_power_gated: false`. The default gateway rejects unauthenticated
status requests; the opt-in open-client mode accepts them. Both modes reject
movement requests for the disabled channel. Status also includes
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

The firmware and gateway tests cover both authenticated and open-client access,
including authenticated device check-ins and movement guards. The broader suite
also reports a pre-existing stale BOM audit for the separately modified
`hardware/cad/generated/auto-switch.blend`; that model was not changed by
firmware provisioning.

Servo movement, PWM waveform, electrical assembly, battery operation and
mechanical fit have not been tested on this board. Leave `enabled` and
`calibrated` false until the assembled actuator has been calibrated.
