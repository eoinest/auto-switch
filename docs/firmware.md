# Firmware and local control

The firmware targets a **Pico W or Pico 2 W running the corresponding MicroPython UF2**. An ordinary Pico can run the USB bench helper, but it has no onboard Wi-Fi. No Raspberry Pi Linux image, cloud account, paid service, or third-party device library is required. The phone interface is a responsive website served by the Pico or the Mac mini gateway.

This is a prototype implementation with passing host tests. It has **not been flashed or tested against a physical board, servo, power circuit, or printed assembly**. The included angles are intentionally small starting points for calibration, not a known fit for your switch.

## Choose a transport

| Configuration | Phone opens | Radio behavior | Command behavior |
| --- | --- | --- | --- |
| `transport: "direct"` | `http://<pico-ip>/` | Wi-Fi stays connected | Immediate authenticated HTTP request; no daily/demo buttons |
| `transport: "gateway"`, daily mode | Mac mini gateway URL | Disconnects and turns WLAN off between polls | Mac mini queues the command until the next poll |
| `transport: "gateway"`, demo mode | Mac mini gateway URL | Wi-Fi stays connected | Pico polls every second |

The phone's daily/demo selection is stored by the gateway. A sleeping device learns a change at its next check-in, so switching to demo is also delayed by the current daily polling interval. Daily polling defaults to 60 seconds; reconnection and network overhead add to that interval. Daily mode uses `WLAN.active(False)` plus ordinary asynchronous sleep. The CPU is **not** placed in deep sleep, and months of battery life are not promised. Measure total battery input current using [the power guide](power.md) before estimating runtime.

Gateway delivery is at most once: the Mac mini marks a queued command dispatched before returning it. If delivery or acknowledgment is lost, the device never automatically repeats the physical motion. The UI can therefore show an uncertain result; inspect the switch before sending a replacement command. The device validates the entire poll response before acting on any command.

## Install

1. Select the MicroPython firmware for the exact board at [the official downloads page](https://micropython.org/download/). Existing MicroPython can be retained if its board-specific Wi-Fi, `uasyncio`, PWM and ADC interfaces work. Record the exact UF2 version in your build notes.
2. Follow the external low-voltage wiring in [power and electronics](power.md). Fit the GP15 enable pulldown before connecting servo power. Keep the horn detached for initial setup.
3. Copy `firmware/config.example.json` to `firmware/config.json`. This private file is ignored by Git. Set Wi-Fi credentials and generate a random token, for example `python3 -c 'import secrets; print(secrets.token_hex(32))'`.
4. For direct mode, set `api_token` and retain `transport: "direct"`. For gateway mode, set `transport: "gateway"`, `gateway.host` to the Mac mini's reserved LAN IPv4 address, `gateway.port`, and `gateway.token` to its **device token**. The phone uses the separate gateway **client token**. See [gateway setup](gateway.md).
5. Leave each channel's `enabled` and `calibrated` set to `false` until the physical fit and endpoints have been checked. Remove the second channel object for a single-switch build. Do not change `power_enable_pin`: this revision requires GP15.
6. Transfer the files with Thonny or [MicroPython's mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html). With mpremote installed and exactly one board connected, run from the repository root:

```sh
mpremote fs cp firmware/main.py firmware/control.py firmware/hardware.py firmware/http_api.py firmware/gateway_client.py firmware/bench.py :
mpremote fs cp firmware/config.json :config.json
mpremote fs mkdir :www
mpremote fs cp firmware/www/index.html firmware/www/app.js firmware/www/style.css :www/
mpremote reset
mpremote repl
```

Skip `mkdir` if `www` already exists. mpremote's filesystem commands stop the running program before transferring. Do transfers with the servo supply disconnected; then reconnect only after reviewing configuration. Ctrl-C in the REPL stops the running firmware and its cleanup disables the servo rail. A missing configuration or placeholder token stops startup without enabling motion.

In direct mode, the USB console prints the Pico URL. Reserve that address in your router. Your phone and device must be on a LAN that permits client-to-client traffic; guest-network isolation can prevent access. In gateway mode, the Pico does not also expose a direct HTTP server.

## Bench calibration

The servo uses the original MG90S horn, its center retaining screw, and the printed horn adapter. Do not rely on a printed imitation spline. Support the assembly on the bench while adjusting travel. The electrical installation remains closed; the mechanism only touches the plastic rocker.

1. With the printed lever detached, run `import bench; bench.neutral(0)` over the USB REPL. This emits the configured neutral pulse for 300 ms and turns the servo rail off. It is intentionally available before enabling a channel, so use it only with the horn detached.
2. Install the horn so neutral leaves clearance at both switch ends. Confirm that the unpowered mechanism is removable and that manual operation remains possible.
3. Change only the local `config.json` to enable and calibrate the channel. Begin with the small sample `on_us: 1400`, `neutral_us: 1500`, `off_us: 1600`. These are guesses, and you may need to swap on/off according to horn orientation. Test using `bench.move(0, 'on')` and `bench.move(0, 'off')`; use channel 1 for the right-hand servo.
4. Increase travel only in small increments, such as 25 µs, and stop as soon as the rocker latches. If the servo buzzes, the chassis lifts, or the lever flexes excessively, disconnect the servo supply and revise the fit or endpoint. Do not lengthen dwell to overpower a blocked switch.
5. Validate the on and off strokes repeatedly with the final mounting method before allowing unattended use. Set `calibrated: true` only for the finished geometry and servo. Recalibrate after moving the horn or changing a printed part.

Normal motion is: rail on → neutral → short on/off press → neutral → rail off, with only one servo moving at a time. Signal pins are driven low while the servo rail is off. Firmware constrains pulses to 1100–1900 µs, a total configured span of at most 400 µs, and a neutral position strictly between the two endpoints. Dwell and return times must each be 50–400 ms. The maximum configured cycle is 1.25 seconds and a 2-second **cooperative software timeout** cancels a stalled coroutine and disables power in `finally`.

That timeout is not an independent electrical fail-safe: a frozen interpreter cannot guarantee a GPIO transition. Network connection, DNS, NTP, poll and acknowledgment operations are guarded against starting while a servo is powered. Use a properly rated load switch and current-limited bench supply during development. A production design would need an independently enforced timeout or current limit if a software lockup must not leave the servo powered.

## Direct API

Both API endpoints require `Authorization: Bearer <api_token>`. The static website is public on the LAN; it does not contain credentials. Tokens are never accepted in a query string.

```http
GET /api/status HTTP/1.1
Authorization: Bearer <api_token>
```

```json
{
  "device": "auto-switch-office",
  "channels": [
    {"id": 0, "name": "Left switch", "state": "unknown", "last_command": null,
     "enabled": false, "calibrated": false}
  ],
  "battery": null,
  "uptime": 42,
  "clock_synced": false,
  "busy": false,
  "transport": "direct"
}
```

```http
POST /api/switch HTTP/1.1
Authorization: Bearer <api_token>
Content-Type: application/json

{"channel":0,"state":"on"}
```

A successful POST returns the updated status. Errors use `{"error":"..."}`: 400 for invalid or disabled/uncalibrated commands, 401 for absent/incorrect credentials, 409 when an actuator or its network guard is busy, 415 for an unsupported content type, and 503 for a failed motion. The endpoint accepts only `channel` and `state`; arbitrary angles, pulse widths, and configuration changes are unavailable remotely.

`state` is **last successfully commanded position**, not physical feedback. It starts `unknown` at boot and becomes `unknown` if a motion starts but fails. `last_command` records the most recent successful on/off command in RAM, or `null` at boot. Manual presses, linkage slip, three-way switching, and power loss can make command history differ from the actual light. Add a sensor for verified state.

Requests have a 2 KiB header limit, 256-byte body limit, a 4-second read deadline and at most four active connections. Duplicate headers and chunked request bodies are rejected. API responses disable caching. This is plain HTTP on a trusted private LAN, so other observers on that LAN may be able to see traffic and tokens. Do not port-forward this server; it does not implement TLS or internet-facing authentication protections.

## Gateway wire contract

The outbound client uses the configured gateway device bearer token:

```text
POST /api/device/poll   {"status": <device status>}
  -> {"mode":"daily"|"demo", "poll_interval_s":60,
      "commands":[{"id":"123","channel":0,"state":"on"}]}

POST /api/device/ack    {"id":"123","success":true,"status":<device status>}
  -> JSON object with HTTP 200
```

Failures acknowledge `success:false` with a short `error` string. The client accepts at most two commands per poll (the bundled gateway returns one), a maximum 4096-byte response, and polling intervals from 1 to 3600 seconds. Demo mode uses one second. Each transport request has an 8-second asynchronous deadline; MicroPython hostname resolution may block outside that cooperative deadline, so a reserved IPv4 address is preferable. A transport error returns the device to radio-off daily mode with a 30-second retry interval. Physical commands are never retried automatically after an acknowledgment failure.

## Battery readings

Enable `battery.enabled` only after installing and verifying the external divider on **GP26**. The default 100 kΩ top / 47 kΩ bottom divider multiplies measured ADC voltage by 147/47. Never connect a battery pack directly to a Pico ADC pin. Readings are averaged across eight ADC samples; divider tolerance, ADC reference error and load sag still affect accuracy.

An enabled battery report is `{voltage: 5.16, percent: null, estimated: true, low: false}`. `low_v` defaults to **4.4 V as an initial four-cell NiMH light-load threshold**, and must be calibrated for the actual pack and measurement circuit. The firmware checks this before enabling servo power, displays `low:true` below it, and inhibits new motions. This does **not** turn off the Pico or prevent further battery discharge. Fit a pack-appropriate hardware cutoff for unattended battery protection. Set `low_v: null` only when intentionally disabling this software threshold.

Percent stays `null` until `empty_v` and `full_v` are explicitly supplied from your own pack measurements. The optional percentage is a clamped linear voltage estimate, not coulomb counting; it is particularly approximate for flat-discharge NiMH cells. A voltage reading is often more honest than a guessed percent.

## Automatic schedules

`schedules_utc` supports up to 16 locally configured daily/weekly entries. Each has `enabled`, `channel`, `state`, `hour`, `minute`, and `days` (Monday = 0, Sunday = 6). Entries in the example are disabled. Times are explicitly **UTC**, with no automatic daylight-saving adjustment. Convert the intended local time before configuring them.

Schedules execute at most once per matching minute during one boot. They require a successful NTP synchronization within the preceding 24 hours and a plausible year; unsuccessful NTP attempts do not trust an arbitrary boot RTC. NTP is retried after one minute on failure and after six hours on success, whenever the network transport next connects. Once time is synchronized, configured events also run while daily mode has Wi-Fi turned off. A due event waits for any in-progress network guard, so network delays can make it late.

There is no catch-up for a minute missed while off, no persisted execution ledger across reboot, and no automatic motion retry after a failure. A restart within an event's minute can execute it again once NTP succeeds. Do not schedule the same action independently on both the Pico and an external automation. Firmware updates and schedule edits are made locally over USB; the phone UI controls on/off and gateway daily/demo mode.

## Verification and references

Run `python3 -m unittest discover -s tests -p 'test_firmware.py' -v` on a development computer. Tests cover authorization, oversized/malformed requests, uncalibrated refusal, pulse/time limits, interrupted motions, mutually exclusive actuation, low-battery inhibition, UTC scheduling, acknowledgment failure, and a simulated gateway loop with a concurrent local schedule. These checks use fake GPIO and networking; they cannot measure current, verify servo strength, prove an adhesive mounting load, or validate a UF2 on real hardware.

Primary interface references: [MicroPython RP2 quick reference](https://docs.micropython.org/en/latest/rp2/quickref.html), [PWM duty and deinitialization](https://docs.micropython.org/en/latest/library/machine.PWM.html), [asyncio streams and tasks](https://docs.micropython.org/en/latest/library/asyncio.html), [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html), and [port-dependent sleep behavior](https://docs.micropython.org/en/latest/library/machine.html).
