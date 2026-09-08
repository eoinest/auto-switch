# Power-path review — 2026-09-08

Scope: received XL63070 module (Teyleten Robot Amazon B0GCW44FDL), switched four-AA alkaline holder, LOLIN-reference ESP32-S2 Mini, one MG90S-type servo. Header pins versus soldered wires do not change the electrical nets. No hardware, firmware, or private configuration was accessed.

**Verdict:** the direct output forks are electrically sensible for a supervised trial. The split-supply USB-debug variant is also valid **when the converter-to-S2 VBUS path is physically disconnected**, with common ground retained. Current capacity and servo transients remain untested. Treat signal connections across independently switched supplies as a separate sequencing issue.

## Must be correct before power is applied

1. **Use the right supply pads.** Battery red goes to converter VIN; battery black to input GND. Measured 5 V VOUT goes to S2 **5V/VBUS**, never 3V3 or GPIO16. Servo power gets a separate VOUT branch and separate output-GND return. The S2's VBUS supplies its onboard 3.3 V regulator; it is not the chip's 3.3 V rail. [Official WEMOS schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf)

2. **Identify the received converter by its labels.** In `IMG_3222.JPG`, VOUT is upper left, GND upper right, VIN lower left, GND lower right. The two holes in each large terminal pad are duplicate connection points. Using both VOUT holes to feed two branches, and both output-GND holes for returns, does not create two independently regulated outputs or double the available current. Verify duplicate-pad continuity with all power removed if the actual soldering/labels are unclear.

3. **Verify output selection with a meter.** The [exact seller listing](https://www.amazon.com/dp/B0GCW44FDL) describes 3.3/5/9 V links and allows one selection at a time. Leave configuration pads unchanged during wire preparation; measure VOUT-to-GND with both S2 and servo disconnected. Target approximately 5.0 V. A listing option, “5V” silk label, or apparent bridge is not proof. Do not use a resistor to drop raw four-AA voltage to 5 V.

4. **Never join USB 5 V to converter VOUT through the S2.** VBUS on the [LOLIN reference schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf) is directly tied to USB VBUS. Turning the holder switch off does not disconnect the converter's output from the S2. There is no established reverse-blocking guarantee for this received converter. Do not rely on a presumed diode, USB-port protection, or unverified chip identity to make parallel supplies acceptable.

5. **Insulate the disconnected positive lead in USB-debug mode.** Remove the booster-to-S2 VBUS wire physically, not merely its battery supply. Verify that no breadboard positive rail or second lead reconnects those nets. Keep GND common; removing ground while leaving a control signal is not a power-isolation method. The servo must draw its motor current through its own return to the converter, not through the S2's small ground lead.

6. **Avoid driving an unpowered device through GPIO16.** The servo input circuit is unknown. Independently switched supplies can leave a powered signal connected to an unpowered receiver. General CMOS I/O can conduct into an unpowered supply unless specifically designed for power-off isolation; this is a possible path, not a claim that this servo contains a particular protection diode. [TI discussion of partial-power-down I/O](https://www.ti.com/lit/an/scea026/scea026.pdf) ESP32-S2 GPIO levels also must remain within its supply-related limits; 5 V is not an acceptable signal. [ESP32-S2 datasheet, DC characteristics](https://www.espressif.com/sites/default/files/documentation/esp32-s2_datasheet_en.pdf)

For a simple USB-debug procedure, leave the signal disconnected until both devices are powered and the ESP32 output is in a known inactive state; connect it only for the test. Disconnect the signal before shutting down either supply. Ground can remain connected. An explicitly verified inactive-low sequence may replace physical signal disconnection for controlled shutdown, but unexpected brownouts remain outside that guarantee. The earlier instruction to remove **all three** S2 leads remains a valid fully disconnected programming procedure; it is not the only possible arrangement.

## The two valid power arrangements

```text
BATTERY DEMO — USB absent

4AA + switch → converter VIN
converter VOUT ──┬── S2 VBUS
                 └── servo +
converter GND ───┬── S2 GND
                 └── servo GND
S2 GPIO16 ────────── servo signal

USB DEBUG — converter-to-S2 VBUS lead removed and insulated

USB ──────────────── S2 USB connector / VBUS
4AA + switch → converter VIN
converter VOUT ───── servo +        [NO connection to S2 VBUS]
converter GND ───┬── servo GND
                 └── S2 GND         [common reference retained]
S2 GPIO16 ────────── servo signal    [connect only while both powered]
```

## Bench-test unknowns — do not turn these into guarantees

- **Total output capacity:** the module listing advertises 2 A maximum, not proven continuous 5 V output under every input/thermal condition. Both branch currents count against the same total. No TI chip performance or reverse-current specification is assumed to apply to this assembled XL63070-labeled unit.
- **Low-input demand:** for illustration at 85% efficiency, 5 V × 1 A requires about 0.98 A from a 6 V pack, but about 1.47 A from a 4 V pack. These are calculated examples, not measured servo current. Cells, holder switch, contacts, solder joints, and wires may be the limit. Alkaline voltage and usable capacity vary with loading; use fresh matched cells for the first demo. [Energizer alkaline application manual](https://data.energizer.com/pdfs/alkaline_appman.pdf)
- **Actual servo peak current and supply transients:** this clone's stall/starting current is unmeasured. Servo current can pulse strongly when starting, correcting position, or changing load; a vendor's measurements of other servos demonstrate the mechanism, not this unit's numeric demand. [Pololu servo measurements](https://www.pololu.com/blog/17/servo-control-interface-in-detail)
- **No-load 5 V is insufficient validation:** check S2-only operation, then short unloaded servo motion, then modest mechanical load. Observe both converter output and voltage at the load connectors. Stop on resets, jitter, sag, or heating. A multimeter may miss short droops or overshoot. Do not deliberately stall the servo. USB-debug isolates the ESP32's positive supply but does not prove battery-demo stability.
- **Signal tolerance:** the received servo's documented 3.3 V threshold and power-off behavior are unavailable. Stable power plus absent/unreliable motion requires signal investigation; it does not justify putting 5 V on an ESP32 GPIO.

## Optional improvements, not prerequisites for initial function

Extra bulk capacitance, a signal series resistor, a fault fuse, or a power-selection/isolating buffer circuit may improve a later design. They are not substitutes for correct pad selection, physical supply separation, and voltage verification. A capacitor cannot compensate for insufficient steady current. A series resistor is not a level shifter or assured isolation. Power gating, battery ADC, WAGO connectors, and another switch are unnecessary for this minimal supervised test.

The unfused assembly is not certified short-circuit protected. Remove cells and USB before soldering or changing power connections, retain insulation/strain relief, and do not infer unattended-operation approval from a successful short test.
