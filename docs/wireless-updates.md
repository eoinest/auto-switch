# Wireless updates on home Wi-Fi

Auto Switch uses your saved home Wi-Fi for both the light controls and application
updates. **It does not create an access point.** Use the
[USB setup companion](usb-wifi-setup.md) when moving to another Wi-Fi network.

**Status:** implementation and host tests complete; installation and a real
wireless upload on the S2 Mini remain pending. The board was not detected over USB.

## Update the application

1. Power on normally and let the S2 join home Wi-Fi. Leave USB unplugged.
2. After startup, hold **BOOT/0 for three seconds**, then release it. Servo control
   stops and is locked out until reboot. Do not hold BOOT through reset, because
   that selects the ROM bootloader.
3. On the same Wi-Fi, open **http://auto-switch.local/update**.
4. Build the current application bundle from the repository root:

   ```sh
   python3 tools/build_update_bundle.py
   ```

5. Select `output/auto-switch.asupdate`, enter the private update password and
   choose **Upload and restart**. Keep battery power stable throughout.
6. After reboot, reopen **http://auto-switch.local/** for the light controls.

Your phone and computer stay on home Wi-Fi throughout. If the router drops, the
S2 retries that same network; it never creates another one. Changed credentials
must be saved through USB. If you entered update mode accidentally, release BOOT
and tap RST to return to normal operation (do not reset during an active upload).

## One-time installation

The current firmware must be installed over USB once before browser updates are
available. Follow [USB isolation and setup](usb-wifi-setup.md), then run:

```sh
python3 tools/wireless_update.py provision --port /dev/cu.YOUR_DEVICE
```

This copies the application and generates a separate update password, stored
privately in `.local/s2/update-password.txt` and the board's `maintenance_cfg.py`.
It preserves existing Wi-Fi credentials and calibration. It needs `mpremote`
in `.venv/bin/mpremote` or PATH and an existing application configuration and
`www/` directory. It does not erase flash or replace MicroPython.

Open the local password file privately when entering it in the update page.
It is never printed or passed as a process argument, and is Git-ignored with
owner-only file permissions. The precommit check also rejects this known secret
if accidentally copied into another tracked file.

## What is preserved and verified

Bundles contain only the explicit application-file allowlist. The device checks
file names, sizes, SHA-256 hashes and Python syntax before installing any files.
Uploads preserve `config.json`, `calibration.json`, `maintenance_cfg.py` and
`boot.py`. Wi-Fi credentials are not part of the application bundle.

The app stops PWM and prevents previously accepted commands from restarting it
in update mode. This does not cut servo power or guarantee loss of holding torque.
Enter update mode after the arm returns to neutral.

An interrupted or invalid upload before activation leaves active files unchanged
and servo control disabled. Retry in update mode. Individual file replacements
use LittleFS rename, but the complete bundle is **not atomic and has no automatic
rollback**. Power loss during activation can leave mixed versions requiring USB
recovery. Updating the MicroPython interpreter also still requires USB.

The authenticated update page uses HTTP without TLS; keep it on a trusted LAN
without port forwarding. The normal On/Off page remains deliberately open to
that LAN. Retain access to USB and the power-isolation switch for recovery.

Sources: [MicroPython v1.29 WLAN](https://docs.micropython.org/en/v1.29.0/library/network.WLAN.html),
[WEMOS S2 Mini](https://www.wemos.cc/en/latest/s2/s2_mini.html).
