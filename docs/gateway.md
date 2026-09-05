# Mac mini relay and phone control

Use a Pico **W** or **2 W**. The Mac mini serves the phone page and holds a persistent command queue; the Pico makes outbound requests to it. One relay instance serves one controller with one or two servos. For bedroom and office, run two instances on different ports with separate database files and keys.

## Run the relay

Python 3.10 or newer is the only server dependency. Keep the Mac awake on your LAN; reserve its IP address in your router. From the repository:

```sh
python3 -c 'import secrets; print(secrets.token_hex(32)); print(secrets.token_hex(32))'
# Use the two different generated values below; don't commit them.
export AUTO_SWITCH_CLIENT_TOKEN='paste-first-generated-value'
export AUTO_SWITCH_DEVICE_TOKEN='paste-second-generated-value'
python3 gateway/server.py --host 0.0.0.0 --port 8765
```

Open `http://MAC_MINI_LAN_IP:8765/` on your phone on the same Wi-Fi. Enter the **client** key. The device key goes only into the Pico's `gateway.token` configuration. Allow incoming Python connections on the Mac's local network if its firewall prompts. No router port-forwarding is needed.

In `firmware/config.json`, select:

```json
{
  "transport": "gateway",
  "gateway": {
    "host": "192.168.1.10",
    "port": 8765,
    "token": "YOUR_SEPARATE_DEVICE_KEY"
  }
}
```

Merge those fields into the complete example; keep Wi-Fi settings, channels and calibration. Use your Mac's actual IP, without `http://` or a path. Reserve the IP to avoid DNS lookup and address changes. Full flashing and calibration: [firmware.md](firmware.md).

The server prints a listening address, not a phone-resolvable hostname. Replace `0.0.0.0` or `127.0.0.1` with the Mac's LAN IP when using a phone. The default bind address is loopback; `--host 0.0.0.0` deliberately enables LAN access.

## Two power modes

| Mode | Pico behavior | Delay |
| --- | --- | --- |
| Daily | Disable Wi-Fi between polls; retain local processor/RTC operation | Configured interval plus Wi-Fi association and request time |
| Demo | Stay connected and poll every second | Usually around a second plus movement/network time; measure on your LAN |

The UI changes the **requested** mode. A sleeping/disconnected Pico cannot hear a mode change immediately: it picks it up at the next poll. Default Daily interval is 60 seconds; the server accepts 10–3600 seconds. A network failure falls back to Daily with a 30-second retry interval. Mode and interval persist in SQLite across server restarts.

Daily mode currently uses ordinary radio-off waiting, not a proven ultra-low-current sleep mode. It implements the connectivity tradeoff but does **not** establish months of battery life. See the assumptions and measurement procedure in [power.md](power.md). MCU sleep or a timer that cuts board power is a later hardware/firmware iteration.

## Commands and uncertainty

1. The phone queues `on` or `off`; the UI shows it as pending.
2. The next device poll receives at most one command. Delivery is recorded in SQLite **before** sending the response.
3. The Pico briefly presses and returns the yoke to neutral, then disables servo power.
4. The Pico acknowledges the attempt. `applied` means the calibrated servo sequence finished, **not** that a sensor verified the light.

The relay never automatically redelivers a movement after an ambiguous failure. If a response is lost, a command can be missed; this is intentional to avoid unexpected repeated movements. A dispatched command without an acknowledgement eventually becomes `uncertain`. Queued commands expire after the longer of ten minutes or three Daily intervals. New queued intent supersedes older undelivered intent for the same channel. Already delivered commands may still finish.

States are command history. They begin `unknown` after a Pico restart; manual switching and three-way circuits are not sensed. With a three-way circuit, top/bottom paddle presses cannot reliably mean actual light on/off without feedback. Name/use them as paddle positions or add a light/state sensor before relying on them as true on/off.

## API

All API requests require `Authorization: Bearer TOKEN`; POST bodies use `Content-Type: application/json`. Keys never go in URLs.

| Endpoint | Key | Body / result |
| --- | --- | --- |
| `GET /api/status` | Client | Last device report, battery estimate, requested mode, queue status, time since last check-in |
| `POST /api/switch` | Client | `{"channel":0,"state":"on"}` → HTTP 202 with command ID |
| `POST /api/mode` | Client | `{"mode":"daily","poll_interval_s":60}` |
| `POST /api/device/poll` | Device | `{"status":...}` → commands, mode, interval |
| `POST /api/device/ack` | Device | `{"id":"1","success":true,"status":...}` |

This is HTTP on a **trusted private LAN**: bearer keys protect control access, but are not encrypted over the LAN. Do not expose it to the internet. The page has no third-party scripts/fonts, stores its key only in memory, and has a Disconnect action. A hardened TLS reverse proxy or VPN can be added outside the Pico for remote access; it is not configured here.

## Keep running on a Mac

For the first bench session keep the terminal running. Once verified, use macOS `launchd` to run the same command on login: an example template is in `gateway/launchd.example.plist`. Replace every placeholder with your absolute repository/Python paths and distinct keys. Store a filled copy outside Git with user-only file permissions. Enable it only when ready; the repository does not install a login service or change Mac sleep settings automatically.

## Preview without hardware

```sh
python3 gateway/server.py --demo
```

Open `http://127.0.0.1:8765/?demo` and click Connect. Preview uses an in-memory database and a clearly labeled simulated device; it cannot move a servo and is restricted to loopback. The preview key is intentionally public and prefilled. The `?demo` URL alone does not switch a real server into simulation.

## Checks

`python3 -m unittest discover -s tests -v` covers role separation, malformed requests, calibration gating, persistent at-most-once dispatch, expiry, supersession, mode updates and a phone→relay→device acknowledgement round trip. The real board, Wi-Fi, servo and battery must still be bench-tested.
