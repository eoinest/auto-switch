# ESP32-S2 Mini / four-AA / one-servo POC

This is the current **bench wiring reference**. It supersedes the Pico-specific POC wiring for this build; the old diagrams remain historical references. It does not claim that the existing Pico firmware has been ported or tested on ESP32-S2.

Open [the interactive illustrated map](../learn/s2-aa-poc.html), [PNG](../hardware/wiring/s2-aa-poc/breadboard.png), [SVG](../hardware/wiring/s2-aa-poc/breadboard.svg), or [wire checklist](../hardware/wiring/s2-aa-poc/connections.csv). Every wire is shown in one view. Illustrations reconstruct the component appearance but are not dimension drawings.

## Selected components

| Part | Quantity | Reference / status |
|---|---:|---|
| ESP32-S2 Mini | 1 | User-owned. Drawing uses [LOLIN S2 Mini V1.0.0](https://www.wemos.cc/en/latest/s2/s2_mini.html), 34.3 × 25.4 mm; exact clone/header configuration not yet photographed. |
| DAIERTEK switched four-AA holder | 1 | User ordered [Amazon B09N1GDWQ9](https://www.amazon.com/dp/B09N1GDWQ9), nominal 68.7 × 64.2 × 22.5 mm. Integrated switch replaces the separate rocker. |
| Amazon Basics AA alkaline cells, 1.5 V | 4 | User ordered. In series: 6 V nominal; raw battery never feeds the ESP32 directly. Do not recharge these cells. |
| Teyleten Robot 5 V buck-boost module | 1 | Selected [Amazon B0GCW44FDL](https://www.amazon.com/dp/B0GCW44FDL). Title says TPS63070; product PCB photo says XL63070. Published board dimensions and authentic chip identity not established. Selection pads, not an adjustment screw. |
| MG90S 180° servo | 1 | User-owned. Verify plug wire colors and orientation on actual servo. |
| Solderless breadboard | 1 | User-owned; exact model unknown. Illustration uses generic 830-point topology with 63 five-hole rows and split 50-hole rails. Adapt to actual board, verified unpowered with continuity mode. |
| Female-to-male jumper leads | 3 | S2 header to breadboard: 5 V, GND, GPIO16. If headers are unsoldered, solder correct headers or leads first. |
| Male-to-male jumpers | 5 | Three into the servo female plug and two rail midpoint bridges. Use shortest practical power leads. |
| Two converter-output leads with male breadboard tips | 2 | Solder stripped ends to converter output; use clean factory pins or 22 AWG solid ends at breadboard. |
| Solder, suitable insulation and strain relief | As needed | User-owned tools/materials. No soldering directly to the breadboard. |

No external servo gate, signal resistor, extra capacitor, battery ADC, WAGO, separate rocker, or isolation diode is installed in this minimal bench map. The converter includes its own capacitors. Short-circuit protection and load capacity of the complete battery/holder/breadboard assembly are not certified by this drawing. Keep this as a supervised bench test; disconnect cells before modifying wiring. A permanent unattended build needs a separate protection and power-distribution review.

## Wiring and board orientation

Use the [WEMOS official pinout](https://www.wemos.cc/en/latest/_static/boards/s2_mini_v1.0.0_4_16x9.jpg): top/component side facing you, USB connector pointing **down**. On the **outermost right header**, the bottom three pins are, from bottom upward: **VBUS (often labelled 5V), GND, GPIO16**. Inner pins are different. The S2 Mini has no Pico-style VSYS pin.

Keep the S2 beside the breadboard with three female-to-male jumpers. Do not insert both adjacent header rows into a standard breadboard's connected five-hole strips: that would short different pins together.

On the selected converter's top-view photo with lettering upright: **VIN upper left, GND lower left, VOUT upper right, GND lower right**. Each power terminal has duplicate holes. Left/right ground pads share a ground net. Compare the actual received module before soldering. Leave EN, PS and ADJ unconnected; seller says EN is enabled and PS is PWM by default. Only the 5 V voltage-selection link should be selected; do not short other selections.

| Wire | From | To |
|---|---|---|
| W1 | Holder red, after its built-in switch | Converter VIN |
| W2 | Holder black | Converter input GND |
| W3 | Converter VOUT, verified 5 V | Left positive rail P48 |
| W4 | Converter output GND | Left ground rail G50 |
| B+ | Positive rail P25 | P26, bridging midpoint break |
| B− | Ground rail G25 | G26, bridging midpoint break |
| W5 | Positive rail P8 | S2 5V/VBUS |
| W6 | Ground rail G10 | S2 GND |
| W7 | S2 GPIO16 | Breadboard j38 |
| W8 | Breadboard i38 | Servo signal, usually orange/yellow |
| W9 | Positive rail P35 | Servo red + |
| W10 | Ground rail G38 | Servo brown/black GND |

P/G numbers count the 50 left rail holes from the top; these are drawing labels, not necessarily printed on your breadboard. Main strips use a–j and rows 1–63. i38 and j38 are joined inside the same five-hole strip. Right-side power rails are unused. All grounds are common. The signal is **3.3 V PWM**, not a 5 V power connection. Never connect a GPIO or 3V3 pin to the 5 V rail.

## Build and verify

1. Remove batteries. Solder holder leads to converter input and two output leads to its output pads. Inspect for solder bridges and add insulation/strain relief without covering hot components. Keep wire strands out of neighboring pads.
2. With power disconnected, check the breadboard rail continuity and its midpoint split. Add the two rail bridges as shown. Verify + and ground are not shorted. Do not use resistance/continuity mode on a powered circuit.
3. Leave S2 and servo disconnected. Install cells with correct polarity, switch on, and measure output with black meter lead in COM and red in V/Ω, DC volts mode. Black probe on ground rail and red on positive rail should read about 5.0 V. If it reads raw battery voltage or another selection such as 9 V, switch off and investigate before connecting anything.
4. Switch off and remove cells before connecting S2/servo. Install only the three identified S2 jumpers and servo connections. Keep USB unplugged. Initial motion must use conservative PWM limits with the horn unloaded; full 180° commands are not the initial test.
5. Watch for resets, jitter, voltage sag and warm contacts/regulator during short tests. A multimeter can miss fast supply dips; passing this check is not proof of transient performance. Do not deliberately stall the servo. Thin jumper leads and breadboard contacts can become the limit before the converter does.

## USB programming — important S2 difference

The [official S2 Mini schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf) ties the 5V/VBUS header directly to USB VBUS. **Disconnect the S2's three jumper leads before plugging in USB.** Turning the battery switch off, or unplugging only the battery, is insufficient: USB would otherwise power the servo rail and feed voltage into the converter output.

After programming, unplug USB first, reconnect the three jumpers with battery power off, then switch the battery holder on. The existing Pico configuration must not be treated as tested S2 firmware. GPIO16 is an ordinary output-capable pin on ESP32-S2; PWM support is described in [Espressif's LEDC documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s2/api-reference/peripherals/ledc.html).

## Mechanical prototype

See [S2/AA mechanical notes](s2-aa-mechanical.md). Source-based S2 outline, holder nominal case and MG90S reference dimensions are separate from unmeasured clone tolerances and assumed wallplate dimensions. Converter bay is adjustable and clearly labelled **fit pending**; no exact purchased converter model has been fabricated from guessed dimensions. Print the small fit coupons before full parts.

## Reproduce

`python3 tools/render_s2_demo.py` produces both SVG copies, wiring JSON and CSV. `python3 tools/verify_s2_demo.py` independently checks breadboard topology against the required nets. PNG is rasterized from that SVG using the open-source `sharp` package. The static learning page has no hardware API calls.

Physical assembly, firmware on the actual S2, converter current capacity and mechanical fit remain untested.
