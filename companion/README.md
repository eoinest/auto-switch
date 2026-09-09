# USB Wi-Fi setup

## Downloadable Mac app

[Download Auto Switch Setup 0.1.0](https://github.com/eoinest/auto-switch/releases/tag/companion-v0.1.0).
Unzip and double-click **Auto Switch Setup.app** (optionally drag it to Applications).
It opens the setup page in your default browser. Python and USB tools are included;
no terminal commands or dependency installation are needed. Use **Quit setup app**
on the page when finished. The app picks a free local port automatically.

This preview supports **Apple Silicon Macs, macOS 15 or later**. It is ad-hoc signed,
not Apple-notarized; macOS may block the first launch on a recipient's computer.
See [Apple's guidance on opening downloaded apps](https://support.apple.com/en-us/102445).
Do not disable system-wide security protections. Intel Macs and Windows are not
included in this release. Saving to a physical ESP32 still needs hardware testing.

The packaged app keeps temporary device settings under
`~/Library/Application Support/Auto Switch Setup/private/`, outside the app bundle,
with owner-only permissions, and deletes them after each setup attempt. The ZIP
contains no Wi-Fi passwords or device configuration. Firmware installation still
uses the project tooling; this companion only saves Wi-Fi on an already-configured board.

## Run from source

From the repository root:

```sh
python3 companion/server.py
```

Open **http://127.0.0.1:8790/** on this Mac. The companion uses the repository’s `.venv/bin/mpremote` when present, otherwise `python3 -m mpremote` (install with `python3 -m pip install mpremote`). Use `--port 8791` if needed. Stop with Ctrl-C.

Before connecting USB, turn **battery power OFF** and the **dedicated booster → ESP32 VBUS isolation switch OFF**, or physically disconnect that VBUS wire. Also unplug the servo’s three-wire connector; its control signal otherwise remains connected to an unpowered servo. Battery OFF alone leaves a possible USB backfeed path. Connect the already-provisioned S2 Mini using a USB data cable, select its port, enter the Wi-Fi network and password, and save. This does not install firmware. The device must already have a valid `config.json`. When finished, unplug USB first, then reconnect the servo and restore the battery circuit.

The companion reads the device configuration first, changes only `wifi.ssid` and `wifi.password`, uploads a temporary configuration, then renames it over `config.json` and restarts the board. Existing calibration and other configuration are preserved. Failed reads never create replacement defaults. If restart cannot be confirmed after saving, the page tells you to press RST.

The web server binds only to `127.0.0.1`. Host, Origin and random CSRF checks protect writes; credentials travel in the POST body, never URLs or process arguments. There are no HTTP access logs. Device-command output is captured and never displayed. Temporary configuration files live under ignored `.local/s2/` with owner-only directory/file permissions and are deleted after each attempt. A forced process kill or computer crash can leave a private temporary directory there; it remains ignored by Git. Close the page and stop the companion when finished.

Select a 2.4 GHz personal Wi-Fi network supported by the S2 Mini. Passwords must contain 8–63 printable ASCII characters. After restart, join that Wi-Fi on your phone and open `http://auto-switch.local/` or the device’s address. There is no fallback access point or Wi-Fi editor on the device in this workflow.

## Build the Mac app

On an Apple Silicon Mac with Python 3.14 (this release was built on macOS 15.7.4):

```sh
python3 -m venv /tmp/auto-switch-build
/tmp/auto-switch-build/bin/python -m pip install -r companion/packaging/requirements.txt
/tmp/auto-switch-build/bin/python companion/packaging/build_macos.py
python3 companion/packaging/verify_macos.py
```

The shareable ZIP and `SHA256SUMS.txt` appear under `dist/companion/`. The verifier
extracts the ZIP to a path with spaces, checks its signature/architecture and
private-file inventory, runs the bundled USB helper on a minimal PATH, then tests
the HTTP assets, port enumeration and authenticated Quit action. It does not write
to USB hardware. Build inputs explicitly include UI assets and dependency metadata,
not the repository's private configuration directories. Dependency licenses are
included in the application resources.
