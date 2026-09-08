# Wireless application updates

Keep the battery/booster wiring connected and leave USB unplugged for routine
updates. This updates our MicroPython application and website, not the underlying
MicroPython interpreter. No Arduino migration or extra circuit parts are needed.

**Status: implemented and host-tested; installation and a live wireless upload
on the S2 Mini are pending.**

## One-time USB setup

Disconnect the battery and servo harness before connecting USB. On the already
configured S2 Mini, from this repository run:

```sh
python3 tools/wireless_update.py provision --port /dev/cu.YOUR_DEVICE
```

The script checks for built-in WebREPL, copies the startup integration and creates
a separate random nine-character password. It saves credentials only in ignored
`.local/s2/webrepl-password.txt` and `.local/s2/webrepl_cfg.py`, with owner-only
file permissions. It does not overwrite Wi-Fi settings or calibration. Install
`mpremote` if not already in `.venv/bin/mpremote` or on your PATH.

For a fresh board, first follow [normal firmware setup](s2-firmware.md). Include
`wireless_updates.py` among the copied modules. The absence of private
`webrepl_cfg.py` leaves wireless updating disabled.

After setup, unplug USB and restore the battery wiring. Keep the board's USB
socket accessible for recovery.

## Routine update

Use the same trusted Wi-Fi network and close any other WebREPL connection. Keep
batteries adequately charged and wait for the servo to return to neutral before
starting. From this repository:

```sh
python3 tools/wireless_update.py check
python3 tools/wireless_update.py push
```

If `.local` discovery does not work, supply the board's current numeric address:

```sh
python3 tools/wireless_update.py --host 192.168.1.123 push
```

`check` only authenticates. `push` interrupts the application, confirms a real
REPL, and drives GPIO16 low. The existing application's cleanup stops PWM; this
does not remove servo power. The website is unavailable during the update.

It uploads an explicit list of code and website files to temporary names, reads
each back and compares SHA-256 hashes, then checks Python syntax on the board
before installing any of them. It preserves
`config.json`, `calibration.json`, `boot.py` and `webrepl_cfg.py`. It installs
`main.py` last, restarts the board, then checks that the website returns.
No servo movement is commanded by the updater. The existing calibration and
enabled state are preserved.

## Failures and recovery

An interrupted transfer leaves the application stopped and the active files
unchanged. Retry `push` while WebREPL is reachable. Do not remove power during
installation: file replacement is individually atomic on the S2's LittleFS,
but the entire bundle is **not atomic and has no automatic rollback**. A power
failure during activation can leave mixed versions. The updater tests rename
replacement support before uploading, and refuses unsupported filesystems.

If startup or Wi-Fi breaks, use USB to reinstall known-good application files.
Disconnect the battery/servo harness before plugging USB in; wireless updates do
not add isolation to the S2's VBUS circuit. Updating the MicroPython interpreter
itself still uses the separate USB flashing procedure.

## Access and credentials

WebREPL gives full Python and filesystem access, independently of the deliberately
open On/Off website. Its password and transfers are **not encrypted**. Use only
on a trusted LAN without port forwarding. The protocol restricts passwords to
4–9 characters; our setup generates nine. No password is printed or passed as
a shell argument. Local credentials must not be committed, shared or included
in logs. Deleting `webrepl_cfg.py` from the board and restarting disables it.

The pinned upstream protocol helper is under `tools/vendor/webrepl`, with its
MIT license. Its original CLI printed passwords; that entry point is removed.

Sources: [MicroPython ESP32 WebREPL](https://docs.micropython.org/en/latest/esp32/quickref.html#webrepl-web-browser-interactive-prompt),
[WebREPL setup](https://github.com/micropython/micropython-lib/blob/master/micropython/net/webrepl/webrepl_setup.py),
[file-transfer protocol](https://github.com/micropython/micropython/blob/master/extmod/modwebrepl.c).
