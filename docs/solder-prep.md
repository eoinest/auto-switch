# Solder preparation — headerless S2 Mini and received XL63070

**Latest revision:** the [USB setup wiring map](usb-wifi-setup.md) adds a dedicated switch in the booster → ESP32 VBUS branch. Earlier images below do not yet depict that switch.

[One-page diagram](../hardware/wiring/solder-prep/solder-prep.png) · [Scalable SVG](../hardware/wiring/solder-prep/solder-prep.svg) · [Latest three-critic wiring review](reviews/wiring-decision-2026-09-08.md)

## Seven terminal groups to prepare

Disconnect USB and remove batteries before soldering. Apply a small amount of solder to the chosen pads and stripped wire ends; avoid large blobs, loose strands and bridges to neighboring pads. For the illustrated breadboard arrangement, use one convenient hole from each converter terminal group. For direct wiring, use both VOUT holes for separate S2/servo power leads and both output GND holes for their separate returns; verify same-group continuity unpowered. These are duplicate connections to one supply, not extra current capacity. Keep the two bare center strips at the converter’s short ends free for the mounting fingers.

### ESP32-S2 Mini: three pads

View the component side with USB pointing down. On the **outermost right-hand pad row**, the bottom three pads are:

| Position | Pad | Wire goes to |
|---|---|---|
| Bottom | VBUS / 5V | Verified 5 V positive rail |
| One above bottom | GND | Ground rail |
| Two above bottom | 16 / GPIO16 | Servo signal, usually orange/yellow |

Use the actual printed labels as the final check. The inner row has different signals, and a view from the underside is mirrored. **Do not use 3V3, GPIO15 or GPIO17 in place of these pads.** The official [WEMOS pinout](https://www.wemos.cc/en/latest/_static/boards/s2_mini_v1.0.0_4_16x9.jpg) establishes these locations for LOLIN S2 Mini V1.0.0; compare clone labels before soldering. The firmware’s S2 profile uses GPIO16 at 50 Hz.

### Received XL63070: four terminal groups

View the component side like your photo: inductor on the left and the XL63070 label at the bottom.

| Position | Pad group | Wire goes to |
|---|---|---|
| Bottom left | VIN | Switched holder red (+), about 6 V nominal from four alkaline AAs |
| Bottom right | GND | Holder black (−) |
| Top left | VOUT | Shared positive rail, **after measuring about 5.0 V** |
| Top right | GND | Shared ground rail |

The two GND groups are the same electrical ground. Duplicate holes within a terminal group share a net and can accept separate wires to the two loads. **Do not pre-tin EN, PS, ADJ or the voltage-selection links.** Leave the factory configuration unchanged during this preparation; verify its output separately.

## Whole circuit

```text
4 × AA alkaline cells in switched holder
  red (+) ── built-in switch ── VIN  ┌──────────┐ VOUT ── verified 5 V ──┬── S2 VBUS/5V
 black (−) ─────────────────── GND  │ XL63070  │                       └── Servo red (+)
                                    └──────────┘ GND ── ground rail ──┬── S2 GND
                                                                      └── Servo brown/black
                                                           S2 GPIO16 ──── Servo signal
```

The holder red lead is already switched; no second switch is required. The S2 and servo draw power in parallel. Servo power does not flow through an ESP32 GPIO or its 3.3 V regulator. On a breadboard, check the actual power-rail splits with power disconnected and bridge any split used by these connections. Keep the power leads short; the [breadboard checklist](../hardware/wiring/s2-aa-poc/connections.csv) gives the existing illustrated hole positions.

## Before power-up

1. With batteries removed, inspect solder joints and check for a hard short between power and ground. Capacitors may cause a brief continuity response; investigate a sustained near-zero resistance. Continuity mode is for unpowered wiring.
2. Leave the S2 and servo disconnected. Install cells and measure VOUT against GND using DC volts mode, black lead in COM and red lead in V/Ω. It must be about 5.0 V, not raw battery voltage or another jumper setting.
3. Switch off before connecting the S2, then test its Wi-Fi. Next test the servo unloaded with small movements before adding switch load. Stop if the board resets, the servo jitters or contacts become hot; those symptoms mean the power path needs attention.
4. For USB programming, disconnect all three S2 harness leads from the breadboard first, and keep their exposed ends isolated. The [S2 schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf) directly ties VBUS to USB power: switching the battery holder off alone does not isolate USB from the servo/converter rail.

No firmware was enabled or flashed as part of this diagram update. The actual battery-and-servo circuit still needs these bench tests.

## USB live testing is a separate wiring mode

The all-three-leads disconnect above is the simple isolated programming procedure. For live servo testing over USB, physically remove and insulate **only the booster-to-S2 VBUS power lead**, ensure no breadboard positive rail bypasses it, and retain the common ground. USB then powers the S2; the battery/booster powers the servo. Keep GPIO16 disconnected until both devices are powered; disconnect it before either supply is switched off, unless a verified inactive-signal procedure is in use. Do not send commands to an unpowered servo. See the [mode table and complete direct-wiring map](reviews/wiring-decision-2026-09-08.md).
