# Browser updates and Wi-Fi recovery

Auto Switch normally joins saved home Wi-Fi and serves the switch controls at
**http://auto-switch.local/**. It does not expose an updater during ordinary use.

**Implementation status:** code and host tests complete; one-time installation,
BOOT-button timing, AP behavior and an actual wireless upload on the S2 Mini are
still pending. The board was not detected over USB during this change.

## Enter update mode

1. Power on normally. Do not hold BOOT/0 during reset or plugging in power: that
   selects the ESP32 ROM bootloader. Let the button be released after startup.
2. Hold **BOOT/0 for three seconds**, then release it. Servo control is stopped
   and locked out until reboot. This works even while home Wi-Fi is unavailable.
3. If home Wi-Fi is connected (or connects within about 15 seconds), open
   **http://auto-switch.local/update**. Your computer keeps its normal Internet.
4. Otherwise join the protected **AutoSwitch-Update** network, using your private
   update password, and open **http://192.168.4.1/update**. This network provides
   local access only; your computer will normally lose Internet while joined.

The same private password authorizes uploads on the page. It is stored locally
in `.local/s2/update-password.txt` and on the board in `maintenance_cfg.py`.
The update page has no external assets and works without Internet. If home Wi-Fi
vanishes after entering update mode, the device attempts recovery after ten
seconds, followed by a bounded reconnect attempt, before starting its own AP.
It waits until any active upload finishes before switching networks.

## Upload an application update

Build the current application bundle on the Mac:

```sh
python3 tools/build_update_bundle.py
```

Select `output/auto-switch.asupdate` on the update page, enter the private update
password, then choose **Upload and restart**. Keep battery power stable throughout.
The device verifies file names, lengths, SHA-256 hashes and Python syntax before
installing any files, then reboots. It waits for BOOT/0 to be released before
resetting so it does not accidentally enter the USB bootloader.

If you joined AutoSwitch-Update, reconnect to home Wi-Fi afterward and reopen
http://auto-switch.local/. No USB connection is needed for this routine workflow.

This updates the MicroPython application and website, not the underlying
MicroPython interpreter. Interpreter replacement still uses USB flashing.
The browser updater replaces the earlier WebREPL proposal; no always-on REPL or
second update service is started by the current application.

## Change home networks

In update mode, expand **Change Wi-Fi**, enter the new network name and personal
Wi-Fi password, then choose **Save Wi-Fi and restart**. The device saves those
settings separately and reboots. Join the same new network on your phone.
This supports a 1–32 byte SSID and an 8–63 character ASCII personal Wi-Fi password;
enterprise and open networks are outside this POC.

If the credentials are wrong, hold BOOT/0 again after startup and recover through
AutoSwitch-Update. You do not need to put Wi-Fi passwords into source code or
application bundles. Uploads preserve `config.json`, `calibration.json`,
`maintenance_cfg.py` and `boot.py`. Changing Wi-Fi preserves other configuration.

## One-time USB installation

On the already configured S2 Mini, disconnect the battery/servo harness before
plugging in USB. From the repository root run:

```sh
python3 tools/wireless_update.py provision --port /dev/cu.YOUR_DEVICE
```

This copies the complete application plus a separate randomly generated update
password. It preserves existing Wi-Fi settings and calibration. It needs
`mpremote` in `.venv/bin/mpremote` or on PATH. A fresh board first needs the
[normal MicroPython setup](s2-firmware.md), including its private `config.json`
and `www/` directory. Provisioning is not a flash erase.

The generated password is not printed or passed as a process argument. The
local password and configuration have owner-only permissions, are Git-ignored,
and the precommit check rejects known update passwords copied into tracked files.
Open the local password file privately when you need to enter it in the browser.

## Limits and recovery

Update mode stops PWM and prevents even previously accepted control requests from
restarting it. It does not disconnect servo power or guarantee a servo releases
holding torque. Enter after a normal press has returned to neutral. Stop and
reposition the mechanism safely if a fault interrupted its motion.

A bad or interrupted upload before activation leaves active files unchanged and
the servo disabled. Retry the upload in update mode. Each file replacement uses
LittleFS rename, but the complete bundle is **not atomic and has no automatic
rollback**. Power loss during activation may leave mixed versions requiring USB
recovery. A program that fails before the maintenance supervisor loads may also
require USB; AP recovery is not a replacement for the ROM bootloader.

Retain the removable power connection and access to USB. Disconnect the
battery/servo harness before recovery over USB; OTA does not electrically isolate
VBUS. No additional circuit components are needed for the update feature.

The AP uses WPA2. The upload page uses password authentication over HTTP, without
TLS, so use this only on your trusted home network or protected recovery AP,
without port forwarding. Credentials are never returned by the server.

Sources: [MicroPython v1.29 WLAN](https://docs.micropython.org/en/v1.29.0/library/network.WLAN.html),
[WEMOS S2 Mini](https://www.wemos.cc/en/latest/s2/s2_mini.html),
[MicroPython ESP32 Wi-Fi implementation](https://github.com/micropython/micropython/blob/v1.29.0/ports/esp32/network_wlan.c).
