# Minimum-demo electrical sanity check

Reviewed 2026-09-07 for the headerless ESP32-S2 Mini, received XL63070 module, switched four-AA holder, and one MG90S. No firmware, private configuration, or connected hardware was accessed or changed.

**Verdict: the current power topology is suitable for a short, supervised first bench trial, conditional on voltage and load testing. Its current capacity has not been demonstrated.** Extra power gating, a signal resistor, battery monitoring, WAGO connectors, or a separate rocker are not needed to establish basic operation. This is not approval for an unattended or stall-tolerant installation.

## Correct minimum connections

```text
4 × AA alkaline cells
       holder switch
          │ +                        XL63070 VOUT — measured 5 V
          └── VIN [XL63070] VOUT ───────────┬── S2 5V/VBUS
holder − ──── GND         GND ────────┐    └── servo red/+ supply
                                     ├─────── S2 GND
                                     └─────── servo brown/black GND
                                              
                              S2 GPIO16 ────── servo signal
```

The two converter GND terminal groups are the same common ground. The signal is 3.3 V PWM; it is not the servo's power supply. Never connect the 5 V power rail to GPIO16 or 3V3.

The [WEMOS S2 Mini schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf) connects VBUS to the USB supply and the onboard 3.3 V regulator input. Its 3V3 net powers the ESP32; it is a different net. The [official pin diagram](https://www.wemos.cc/en/latest/_static/boards/s2_mini_v1.0.0_4_16x9.jpg), viewed component-side with USB down, puts VBUS, GND, GPIO16 in the bottom three positions of the outermost right pad row, read upward. Compare the actual board labels before soldering. [Espressif's LEDC documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s2/api-reference/peripherals/ledc.html) supports routing PWM to an output GPIO.

In the received `IMG_3222.JPG` orientation, **VOUT is upper left, GND upper right, VIN lower left, and GND lower right**. Duplicate holes within each labeled terminal group are alternate solder positions, not additional independent signals. The older map rotates the converter; follow labels rather than page-left/page-right.

## Voltage selection and batteries

The current BOM specifies **four Amazon Basics 1.5 V alkaline cells**, not NiMH and not the earlier LiPo. Their series voltage is approximately 6 V nominal and varies with charge/load. Raw pack voltage goes only to converter VIN. Keep using the buck-boost for this alkaline configuration; a resistor is not a substitute for voltage regulation.

The [selected module's seller information](https://www.amazon.com/dp/B0GCW44FDL) offers 3.3/5/9 V selection links, says to use only one selection, and describes EN as enabled and PWM as the default. Leave EN, PS, and ADJ alone for this trial. **A “5 V” purchase option, board name, or apparent solder bridge is not a voltage measurement.** Before connecting the S2 or servo, check actual VOUT-to-GND with the multimeter. Investigate any output materially different from approximately 5.0 V.

## Current capability: possible, not yet proven

The seller advertises **2 A maximum**, with operating-condition and heating caveats. It does not establish that this particular assembled module can supply 2 A continuously at every input voltage. The chip name alone cannot certify the module's inductor, cooling, soldering, or protection behavior. Do not treat a chip switch-current rating as available 5 V output current.

[TowerPro's MG90S specification](https://towerpro.com.tw/product/mg90s-3/) gives 4.8 V operating information, but does not supply a verified peak/stall-current figure or a 3.3 V signal-high threshold for this user's servo. A regulated 5 V rail and 3.3 V GPIO signal are reasonable first-trial choices, but actual response must be checked. If motion fails while power remains stable, check pulse settings, plug orientation, and signal compatibility; never apply 5 V to an ESP32 GPIO to “fix” it.

Both Wi-Fi transmission and servo starting/changing load can produce short current demands. [Espressif recommends a supply capable of at least 500 mA for the chip's 3.3 V power design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s2/schematic-checklist.html#power-supply); that is a supply-design recommendation, not a claim that this assembled board always consumes 500 mA. Its existing onboard regulator and capacitors remain in use.

For illustration only, assuming 85% converter efficiency:

```text
input current ≈ (5 V × output current) / (battery voltage × 0.85)

1 A at the 5 V output → about 0.98 A from a 6 V pack
1 A at the 5 V output → about 1.47 A from a 4 V pack
2 A at the 5 V output → about 2.94 A from a 4 V pack
```

Those are calculation examples, not measured servo demand or a promise of converter performance. Lower battery voltage demands more input current for the same output power. Cell resistance, holder contacts, switch, thin jumpers, and breadboard contacts can cause sag before a headline converter limit is reached. [Energizer's alkaline application manual](https://data.energizer.com/pdfs/alkaline_appman.pdf) documents load-dependent voltage and internal-resistance effects; it is general alkaline behavior, not a test of these Amazon cells.

## Minimum bring-up sequence

1. **No batteries and no USB:** verify polarity, insulation, solder joints, and the actual breadboard's continuity/splits. Use factory male jumper pins or suitable solid wire ends; do not force loose stranded wire into breadboard contacts.
2. **Converter only:** leave S2 and servo disconnected. Measure the switched pack input and converter output. Meter black lead goes in COM, red in V/Ω, meter set to DC voltage—not current. Do not use continuity mode while powered.
3. **S2 alone:** switch off before connecting it, then run from the verified converter supply with USB absent. Confirm Wi-Fi/web serving stays stable.
4. **Add the unloaded servo:** switch off first. Test conservative movements with the horn free from the switch mechanism. Keep the supply wiring short and secure. Stop for jitter, ESP32 resets, visible voltage sag, or heating at cells/contacts/leads/converter. Do not deliberately stall the servo.
5. Only after that succeeds, test gentle mechanical loading. A multimeter can miss rapid dips; “about 5 V” on its display does not rule out brief brownouts. Repeated trouble calls for better power-path measurements/distribution, not longer forced runs.

An added bulk capacitor near the servo can help short transients if testing shows a need; it cannot repair inadequate continuous current or bad contacts. A fuse is useful fault protection, not a requirement for the logic to operate and not a voltage regulator. The minimal unfused trial relies on disconnected-power assembly and supervision; it is not short-circuit protected as a complete system. Fuse selection and permanent wiring protection belong to the later hardware review. No new protective-part shopping list is necessary to start these staged checks.

## USB programming isolation

**Remove all three S2 harness leads before connecting USB.** Turning the holder switch off is insufficient: the S2 VBUS pad is directly connected to USB, so USB could energize the servo rail and the converter's output. Unplug USB before reconnecting the harness, with battery power off. This simple disconnect procedure avoids adding a power-selection circuit for the demo.

## Repository checks and stale text

`python3 tools/verify_s2_demo.py` passed: 12 mapped wires, both rail bridges, one shared signal strip, four required separate nets, and reference pin order. This checks the drawing's intended connectivity, not real board ratings or physical wiring.

`docs/s2-aa-poc.md` correctly specifies three direct-solder S2 leads with male breadboard ends. At review time `learn/s2-aa-poc.html` still incorrectly specified female-to-male S2 leads and said firmware had not been ported/tested. Those page references were corrected in this update: it now uses direct-solder leads and reports completed USB-only network testing. Servo/battery operation remains marked untested.
