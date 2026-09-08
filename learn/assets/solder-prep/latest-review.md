# Wiring decision: minimal one-servo demo

Scope: four AA alkaline cells in the switched holder, received XL63070 buck-boost module, ESP32-S2 Mini and one MG90S. This is a review of the proposed circuit and repository artifacts, not a measurement of the assembled hardware.

## Decision

Keep the basic circuit. It is a reasonable candidate for a short supervised bench demonstration once the output voltage and behavior under load are checked. It has not been proven to supply the actual servo's peak current, survive a short circuit, or tolerate a stalled mechanism.

No redesign or mandatory shopping list follows from the schematic alone. Correct polarity, insulation, a measured 5 V output, appropriate USB isolation, and a free-moving servo are prerequisites. Additional monitoring and switching circuitry are optional for this trial; unreliable power under load would require a concrete fix before continuing.

## Battery-only demo: recommended normal arrangement

```text
4 AA holder red (already switched) ─────────── XL63070 VIN
4 AA holder black ────────────────────────── XL63070 input GND

XL63070 VOUT hole A ──────────────────────── S2 VBUS / 5V
XL63070 VOUT hole B ──────────────────────── Servo red (+)
XL63070 output GND hole A ────────────────── S2 GND
XL63070 output GND hole B ────────────────── Servo brown/black (−)
S2 GPIO16 ───────────────────────────────── Servo signal

USB UNPLUGGED
```

Duplicate output holes within each labeled group let the PCB act as the junction: a three-way wire splice and power breadboard are not necessary. Confirm same-group continuity with power disconnected before using them. VIN and VOUT are different nodes; never bridge them. Both devices need ground, and the converter's input/output grounds are common. Keep the servo supply and return leads separate from the S2 leads until they meet at the converter.

The received-photo orientation is VOUT top left, GND top right, VIN bottom left, GND bottom right. S2 component side up with USB down: the bottom three pads of the outermost right row are VBUS, GND, GPIO16 from bottom upward. Match actual labels, especially if changing boards. Never put 5 V on 3V3 or GPIO16.

## USB modes: distinguish programming from live servo testing

The [official S2 Mini schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf) ties USB VBUS directly to the board's VBUS/5V pad. It does not isolate a connected external 5 V source from USB power.

| Mode | USB | Booster → S2 VBUS | Signal and ground |
|---|---|---|---|
| Battery demonstration | Unplugged | Connected | Connected |
| Programming with hardware isolated | Connected | Disconnected | All three S2 harness leads unplugged |
| Live USB debugging with battery-powered servo | Connected | **Physically disconnected and insulated** | Common ground stays; signal only while both devices are powered |

For live testing:

```text
Mac USB ────────────────────────── S2 power
Battery → booster VOUT ─────────── Servo power ONLY
Booster GND ──────────────────┬─── Servo GND
                              └─── S2 GND
S2 GPIO16 ───────────────────────── Servo signal (removable)

NO booster VOUT connection to S2 VBUS, directly or through a breadboard rail.
```

Change the power wiring with USB unplugged and cells removed. For the split-supply live-test mode, establish common ground, keep the signal disconnected until both devices are powered, then connect only that signal lead. Disconnect the signal before shutting down either supply. Do not issue commands while the servo supply is off. This avoids relying on undocumented powered-off behavior of the servo input. It is a precaution for this unknown module, not a claim that a specific internal protection circuit has been identified. [TI explains the general signal-line back-power mechanism](https://www.ti.com/document-viewer/lit/html/SCDA015).

Keeping common ground does not join the two positive supplies. Turning off the battery switch alone does not remove the direct USB/booster connection if the VBUS wire is still installed. Stopping PWM likewise does not disconnect servo power.

## Minimum bench evidence before calling it a working demo

1. **Unpowered wiring check:** cells removed and USB unplugged. Inspect for reversed leads, loose strands and solder bridges. Check duplicate-hole continuity and any breadboard rail splits. Do not use continuity mode on powered wiring; a brief capacitor-charging response is different from a sustained hard short.
2. **Converter alone:** S2 and servo disconnected. Black meter lead in COM, red in V/Ω, DC voltage mode. Measure approximately 5.0 V from VOUT to GND. The board's printed 5V label or purchased variant does not replace this measurement. Do not connect a meter set to current across a supply.
3. **S2 alone on battery:** verify it boots, joins Wi-Fi and serves the page with USB absent. Switch off before adding the servo.
4. **Unloaded servo:** horn clear of the switch mechanism, conservative movements. Check voltage at the loads, not just the converter. Stop for resets, repeated jitter, sag, a stalled motor or heating at cells, wires, contacts or converter. A multimeter can miss brief dips.
5. **Short gentle switch test:** only after the unloaded test succeeds. Avoid mechanical binding. The software returns to neutral and stops pulses, but it cannot sense a stall or certify that torque has been released.

Fresh AA cells are suitable for this trial, but not a guarantee of peak current. A seller's “2 A maximum” is not a measurement of continuous output at low battery voltage. Converter, holder, wiring and contacts must work together under the real load. The 3.3 V control signal is a reasonable initial choice, but the supplied servo's exact input threshold is unverified; no movement does not by itself prove a power fault. [Pololu's servo interface explanation](https://www.pololu.com/blog/16/electrical-characteristics-of-servos-and-introduction-to-the-servo-control-interface) distinguishes power, ground and control and explains load-dependent current.

## What we are not adding by default

- A servo power gate, battery ADC, WAGO blocks or a separate holder switch: unnecessary for this demo's requested behavior.
- A signal resistor: not a voltage regulator, power-source selector or substitute for correct power sequencing.
- A bulk capacitor: consider it for demonstrated transient trouble; it cannot repair inadequate sustained current or a bad connection.
- A level shifter: add only if the actual servo fails a correctly powered 3.3 V signal test and the required interface is established.

A fuse is useful fault protection, not a logic requirement. The minimal unfused prototype does **not** protect its complete wiring against shorts: supervision does not make it short-proof. Keep joints insulated, assemble unpowered, and remove cells when finished. An unattended installation or evidence of excessive fault/load current needs a protection review before use.

## Reviews and checks

- [Power critic](https://github.com/eoinest/auto-switch/blob/main/docs/reviews/wiring-power-2026-09-08.md)
- [Connection and GPIO critic](https://github.com/eoinest/auto-switch/blob/main/docs/reviews/wiring-connections-2026-09-08.md)
- [Practical demo critic](https://github.com/eoinest/auto-switch/blob/main/docs/reviews/wiring-demo-2026-09-08.md)

Both existing drawing net checkers pass. Source inspection of `firmware/hardware.py` confirms GPIO is set low at initialization and after PWM deinitialization. `firmware/control.py` bounds normal commands with a timeout and runs cleanup in `finally`. These are useful behaviors, not a current limiter or a guarantee about every boot, crash or separately switched power condition. No firmware was changed, enabled or flashed during this review.
