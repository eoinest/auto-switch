# Connection and GPIO review — 2026-09-08

Scope: received XL63070 module, switched four-AA holder, ESP32-S2 Mini, one MG90S, and the current solder-prep/breadboard artifacts. This checks intended connectivity and documented interfaces; it is not an electrical test of the user's hardware.

## Result

**The proposed nets are correct. No misplaced power or signal connection was found.** The direct-output-hole version is a sensible simplification: the two devices receive power in parallel, with separate leads meeting at the converter. A three-way splice or power breadboard is unnecessary. The conditional proceed decision and USB procedures in [the combined review](wiring-decision-2026-09-08.md) agree with this review.

Two older instructions need narrower wording: “use one convenient hole” unnecessarily excludes using both duplicate holes in a labeled output group; “disconnect all three S2 harness leads for USB” is a safe isolated-programming procedure, but is not required for a correctly isolated live servo test.

## Verified pin and net mapping

With the S2 component side facing the viewer and USB pointing down, the bottom three pads in the **outermost right row** are VBUS, GND and GPIO16, bottom upward. The neighboring inner row is different: GPIO15, GND and GPIO17. The official diagram was visually checked; do not select a pin solely by approximate position. [WEMOS pinout](https://www.wemos.cc/en/latest/_static/boards/s2_mini_v1.0.0_4_16x9.jpg)

The official schematic connects USB VBUS directly to the VBUS header net and onboard 3.3 V regulator input. Therefore regulated 5 V belongs on VBUS. USB power and an externally driven VBUS are not automatically isolated. Neither 3V3 nor GPIO16 is a 5 V power input. [WEMOS schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf)

| Net | Connections |
|---|---|
| Battery positive | Switched holder red → converter VIN |
| Shared ground | Holder black → converter input GND; converter output GND → S2 GND and servo ground |
| Regulated positive | Converter VOUT → S2 VBUS and servo positive |
| Control | S2 GPIO16 → servo signal |

In the received module photo, with the inductor on the left and text upright, VOUT is upper left, output GND upper right, VIN lower left and input GND lower right. Duplicate holes within each labeled group provide alternative physical solder positions on the same intended net. Using one VOUT hole for each load and one output-GND hole for each return is appropriate **after confirming continuity on the unpowered actual board**. VIN and VOUT remain different nets. The two ground groups are intended to be common.

The servo's signal is referenced to shared ground. A connection to GPIO16 does not supply motor power. Keeping common ground during split-supply testing does not join the positive power rails. [Pololu explains the three servo connections](https://www.pololu.com/blog/16/electrical-characteristics-of-servos-and-introduction-to-the-servo-control-interface).

## Breadboard and flying-lead checks

Both repository checks pass:

- `python3 tools/verify_s2_demo.py`: 12 wires, two midpoint rail bridges, shared i38/j38 signal strip and four isolated required nets.
- `python3 tools/verify_solder_prep.py`: seven solder groups, 12 wires, required net separation, rail bridges, photo orientation and GPIO16 profile.

These checks validate the encoded board topology, not a physical breadboard. Check the actual rail breaks unpowered. Within an ordinary five-hole terminal strip, all holes are common; positive and ground must not share one strip. The current headerless S2 flying-lead arrangement is appropriate. Fully populating both adjacent S2 header columns and inserting them into common breadboard strips can short neighboring pins; that is not the arrangement reviewed here.

The direct converter branches make power rails optional. They do not change the required four electrical nets.

## Logic voltage and powered-off behavior

GPIO16 is a 3.3 V-domain signal. Espressif specifies input levels relative to its supply domain, not 5 V tolerance. Do not add a 5 V pull-up or connect servo positive to it. [ESP32-S2 datasheet, DC characteristics](https://documentation.espressif.com/esp32-s2_datasheet_en.html)

A 3.3 V PWM signal is a reasonable initial test: Pololu documents modern receivers using about 3 V pulses and many servos working with 3.3 V microcontrollers. This does **not** establish the input threshold of the user's particular MG90S or clone. Its threshold remains unverified. A level shifter is conditional on a demonstrated interface problem, not a default requirement. [Pololu servo interface details](https://www.pololu.com/blog/17/servo-control-interface-in-detail)

Removing the booster-to-VBUS connection prevents a direct positive-supply connection during USB testing, but does not make GPIO16 electrically isolated. A powered controller sending pulses to an unpowered servo may inject current through input protection. The servo's internal circuit was not identified, so this is a general interface risk rather than a demonstrated fault in this unit. Likewise, a powered servo must not be assumed to back-power the ESP32: its signal is normally an input, but its precise pull-up and powered-off behavior are unknown. [TI describes the general signal-line back-power mechanism](https://www.ti.com/document-viewer/lit/html/SCDA015).

For live USB debugging without added parts:

1. Reconfigure with USB unplugged and cells removed. Physically disconnect and insulate booster VOUT → S2 VBUS; eliminate any equivalent connection through breadboard rails.
2. Establish shared ground. Initially leave the PWM lead disconnected.
3. Power the S2 by USB and the servo by the battery/converter, then connect PWM while both are powered.
4. Disconnect PWM before switching either supply off. Do not command the servo with its supply off.

For isolated programming, disconnecting all three harness leads remains the simplest option. For normal battery use, leave USB unplugged and reconnect the VBUS branch. The battery switch alone does not isolate USB from a still-connected VBUS branch.

`firmware/hardware.py` initializes the signal low and returns it low after stopping/deinitializing PWM. This helps normal operation but does not guarantee all boot, crash or independent-power sequences. Stopping PWM also does not disconnect servo power. A series signal resistor can limit some injection current; it is not a voltage regulator or guaranteed powered-off isolation.

## Findings by category

**Actual connection errors to avoid:** 5 V/raw battery voltage on GPIO or 3V3, VIN-to-VOUT bridges, missing shared ground, joined USB/external positive supplies, and breadboard strips accidentally joining different nets. None was found in the encoded current wiring.

**Conditional bench evidence still needed:** actual terminal continuity and polarity, measured converter output, stable supply at the loads, the servo's 3.3 V signal response, and real breadboard contact topology. No source or drawing substitutes for these checks.

**Optional for this minimal demo:** power breadboard, three-way splices, WAGO connectors, servo power gating, and a signal resistor or level shifter without a demonstrated need. This pin review adds no mandatory shopping list. See the separate power review for converter/load limits and fault protection.
