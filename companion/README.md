# USB Wi-Fi setup

From the repository root:

```sh
python3 companion/server.py
```

Open **http://127.0.0.1:8790/** on this Mac. The companion uses the repository’s `.venv/bin/mpremote` when present, otherwise `python3 -m mpremote` (install with `python3 -m pip install mpremote`). Use `--port 8791` if needed. Stop with Ctrl-C.

Before connecting USB, turn **battery power OFF** and the **dedicated booster → ESP32 VBUS isolation switch OFF**, or physically disconnect that VBUS wire. Also unplug the servo’s three-wire connector; its control signal otherwise remains connected to an unpowered servo. Battery OFF alone leaves a possible USB backfeed path. Connect the already-provisioned S2 Mini using a USB data cable, select its port, enter the Wi-Fi network and password, and save. This does not install firmware. The device must already have a valid `config.json`. When finished, unplug USB first, then reconnect the servo and restore the battery circuit.

The companion reads the device configuration first, changes only `wifi.ssid` and `wifi.password`, uploads a temporary configuration, then renames it over `config.json` and restarts the board. Existing calibration and other configuration are preserved. Failed reads never create replacement defaults. If restart cannot be confirmed after saving, the page tells you to press RST.

The web server binds only to `127.0.0.1`. Host, Origin and random CSRF checks protect writes; credentials travel in the POST body, never URLs or process arguments. There are no HTTP access logs. Device-command output is captured and never displayed. Temporary configuration files live under ignored `.local/s2/` with owner-only directory/file permissions and are deleted after each attempt. A forced process kill or computer crash can leave a private temporary directory there; it remains ignored by Git. Close the page and stop the companion when finished.

Select a 2.4 GHz personal Wi-Fi network supported by the S2 Mini. Passwords must contain 8–63 printable ASCII characters. After restart, join that Wi-Fi on your phone and open `http://auto-switch.local/` or the device’s address. There is no fallback access point or Wi-Fi editor on the device in this workflow.
