# Run the S2 Mini POC

The ESP32-S2 Mini hosts its own **On / Off** website over Wi-Fi. Your phone
connects directly to it; no Mac server is required. The current POC uses one
MG90S servo on **GPIO16**, with no check-in mode, servo power gate or battery
monitoring.

## What works today

The USB-powered board joined Wi-Fi and served the website, and the page was
opened on a phone. Direct HTTP, the `auto-switch.local` name and the deployed
website files were verified. **Servo movement, the battery circuit and physical
fit are not yet verified.** The servo remains disabled and uncalibrated.

## Install or update

Use official [LOLIN S2 Mini MicroPython](https://micropython.org/download/LOLIN_S2_MINI/)
(the current board runs v1.29.0) and `mpremote` on your computer. Run the commands
below from the repository root.

**Disconnect the battery and servo harness before plugging in USB.** VBUS is
connected directly to USB power; turning off the battery switch alone does not
isolate the servo rail. See the [POC wiring guide](s2-aa-poc.md).

1. For a first setup, copy [the S2 example](../firmware/config.s2-demo.example.json)
   to `.local/s2/config.json` and fill in `wifi.ssid` and `wifi.password` locally.
   On an existing setup, keep your private configuration. `.local/` is Git-ignored;
   never paste credentials into a tracked file or commit a device flash backup.
2. Keep `hardware_profile: "s2-demo"`, `transport: "direct"`,
   `open_client: true` and `hostname: "auto-switch"`. Leave the channel's
   `enabled` and `calibrated` fields `false`. Sample pulse widths are not
   calibrated endpoints.
3. Copy all modules, configuration and website assets **before resetting**:

```sh
mpremote fs cp firmware/control.py firmware/hardware.py firmware/http_api.py firmware/gateway_client.py firmware/bench.py firmware/main.py :
mpremote fs cp .local/s2/config.json :config.json
mpremote fs mkdir :www
mpremote fs cp firmware/www/index.html firmware/www/app.js firmware/www/style.css :www/
mpremote reset
```

Skip `mkdir` when `www` already exists. If multiple serial devices are attached,
add `connect /dev/cu.YOUR_DEVICE` immediately after `mpremote` in each command,
using your board's actual port. The imported `gateway_client.py` module must
still be copied even though this configuration does not use a gateway.

## Open it on your phone

Join the same Wi-Fi network and open **[http://auto-switch.local/](http://auto-switch.local/)**.
If local-name discovery is unavailable, use the numeric address printed in the
USB console as `auto-switch UI: http://...`. Neither address needs `:8768`.
Give each additional device a different `hostname`.

The two buttons stay disabled until the servo is calibrated. Open-client mode
has no login: anyone who can reach the board on the network can send requests,
but disabled or uncalibrated channels still cannot move. Keep this POC on your
local network without port forwarding.

For a normal restart, tap **RST** once. Holding **BOOT/0** while resetting is
for entering the firmware bootloader, not normal operation.

## Next bench step

Wire and test the servo away from the wall switch, calibrate its endpoints, and
only then enable movement. Follow the [wiring guide](s2-aa-poc.md) for the planned
battery supply. The working USB website does not establish battery life or prove
the assembled actuator fits.

Earlier gateway experiments, flash-backup details and the optional reduced
Wi-Fi transmit-power diagnostic are in [historical bring-up notes](history/s2-bringup.md).
