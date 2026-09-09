# USB Wi-Fi setup companion

Normal use and wireless application updates both use your saved home Wi-Fi.
The ESP32 never creates a setup or recovery access point. To join a different
network, connect USB and save credentials through the local companion.

[Download the Mac app](https://github.com/eoinest/auto-switch/releases/tag/companion-v0.1.0)
for Apple Silicon/macOS 15+. It bundles Python and the USB tools; unzip and open
**Auto Switch Setup.app**. This preview is not Apple-notarized and may need manual
first-launch approval. The command below remains available for running from source.

**Status:** implementation and host tests complete; installation and saving to
the physical S2 Mini still need testing. The board was not detected during this change.

## The power switch

Put a dedicated SPST switch only in the **booster VOUT → ESP32 VBUS** wire.
The servo retains its own connection to booster VOUT. No positive breadboard
rail or other wire may bypass the switch. Keep ground common.

```text
 FOUR-AA HOLDER                    BUCK-BOOST, measured 5.0 V
 + --[holder ON/OFF]--------------> VIN
 - ------------------------------> GND
                                   VOUT hole A --[S2 ISOLATION]--> S2 VBUS/5V
                                   VOUT hole B ------------------> Servo +
                                   GND hole A -------------------> S2 GND
                                   GND hole B -------------------> Servo GND

                                                    S2 GPIO16 ---> Servo signal
 Mac USB ------------------------------------------> S2 USB-C
           Connect USB only with S2 ISOLATION open/OFF.
```

The VOUT holes are duplicate connections to the same regulated supply. The
[official S2 schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf)
connects the USB 5 V pin and VBUS pad directly. The new switch separates that
shared board supply from the booster. Switching off the holder alone does not.

Use an insulated switch and joints, with a DC rating suitable for the board's
supply current. The switch is not connected to a GPIO. With batteries removed
and USB unplugged, verify the new switch breaks continuity between booster
VOUT and S2 VBUS when OFF, and connects them when ON.

## Save Wi-Fi over USB

1. Turn the battery holder OFF and the S2 isolation switch OFF.
2. Unplug the servo's three-wire connector, then plug the S2 into the Mac by USB.
   The isolation switch separates positive power, but not GPIO16; unplugging the
   servo avoids sending a signal into an unpowered servo during setup.
3. From the repository root, launch the companion:

   ```sh
   python3 companion/server.py
   ```

4. Open the local address shown by the companion, select the connected board,
   enter the network name/password, and save. It reads the existing device
   configuration, changes only the Wi-Fi credentials, and restarts the S2.
5. Unplug USB. With both switches OFF, reconnect the servo. Turn the S2 isolation
   switch ON and then the holder ON for normal battery operation.
6. On a phone on that same Wi-Fi, open **http://auto-switch.local/**.

The companion configures an already-installed MicroPython application; it does
not flash firmware or erase the board. If the device configuration cannot be
read, it stops instead of replacing it with defaults. Saved calibration and
other configuration remain intact. An incorrect Wi-Fi password can be corrected
by repeating USB setup.

The companion listens only on the Mac's loopback address. Passwords are not put
in URLs, subprocess arguments, logs or Git. Private temporary configuration files
have owner-only permissions and are deleted after the operation. Do not copy
device config or flash dumps into tracked files.

## Updates after connection

Once connected to home Wi-Fi, application updates remain wireless: hold BOOT/0
for three seconds after startup, release it, and open
**http://auto-switch.local/update**. Battery wiring stays connected and USB stays
unplugged. See [wireless update instructions](wireless-updates.md).

No new enclosure switch cutout has been modeled in this change. Position the
isolation switch where it remains accessible; the old printed carriers are
unchanged.
