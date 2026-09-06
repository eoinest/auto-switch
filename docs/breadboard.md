# Breadboard bench build

**Historical reference — earlier Pico design; not the current build instructions.** For the current ESP32-S2 Mini POC, start with [S2 wiring](s2-aa-poc.md), [S2 firmware](s2-firmware.md) and the [current BOM](../BOM.md).

Use the [interactive Breadboard tab](../learn/index.html#breadboard), [full layout](../hardware/wiring/breadboard/layout.svg) and [hole checklist CSV](../hardware/wiring/breadboard/placements.csv). This is a temporary bench version of the same circuit. The final enclosure still uses the headerless Pico and soldered wiring; this layout does not claim that the breadboard fits the STLs.

## What to add

| Item | Quantity | Purpose |
| --- | ---: | --- |
| [Adafruit 239 full-size 830-point breadboard](https://www.adafruit.com/product/239), or a matching 63-row board | 1 | Two five-hole strips per numbered row, columns a–j |
| [Adafruit 1957, 20 male/male 150 mm jumpers](https://www.adafruit.com/product/1957) | 1 pack | Eight complete jumpers plus six cut-to-one-male-end leads for two servos; seven plus five for one servo |
| Existing Pico W with two straight 20-pin male headers | 1 | Headerless board is for the final assembly; no extra Pico required for the bench if yours matches |
| Components, 22 AWG power wire, heat-shrink and servo extension(s) from the [BOM](../BOM.md) | As listed | Same electrical circuit; Perma-Proto is not needed for the breadboard stage |

The 150 mm jumpers are 28 AWG. Use them for Pico supply and logic branches, not the motor-current path. For L1–L6, retain one male end for the breadboard and solder/insulate the other end into its named external connection. Do not push frayed stranded wire directly into the holes. Keep the existing thicker power harness between battery, regulator, gate and servo(s).

The regulator and Pololu 2810 modules support 0.1-inch headers, but this layout deliberately keeps their motor power connections beside the breadboard on direct wiring. This is a reliability choice for this prototype, not a claim that those modules cannot fit a breadboard. [Regulator](https://www.pololu.com/product/2574), [switch module](https://www.pololu.com/product/2810).

## Board orientation and connected holes

Place the breadboard with its numbered rows increasing downward, a–e on the left and f–j on the right. Put the Pico USB socket at the **top**. Its first left pin goes into **c3**, first right pin into **h3**; the bottom header pins are **c22** and **h22**. Do not shift it down one row and keep using this table.

The Pico header rows are 17.78 mm apart. Across a standard board, c→d→e (5.08 mm), the e/f trench (7.62 mm), and f→g→h (5.08 mm) total 17.78 mm. Columns a/b and i/j remain exposed. [Pico W physical drawing](https://datasheets.raspberrypi.com/picow/pico-w-product-brief.pdf), [official pinout](https://datasheets.raspberrypi.com/picow/PicoW-A4-Pinout.pdf).

Each numbered row has two separate metal strips: a–e and f–j. Thus b35 connects to the diode lead in a35; j4 connects to Pico VSYS in h4. Adjacent rows are separate. **All side power rails are unused**, avoiding assumptions about split rails. Confirm strip continuity with your own board before placing parts. [Adafruit breadboard guide](https://learn.adafruit.com/breadboards-for-beginners/breadboard-tips-and-tricks).

| Pico function | Physical pin | Header hole | Accessible jumper hole |
| --- | ---: | --- | --- |
| VSYS | 39 | h4 | j4 |
| GND | 38 | h5 | j5 |
| GP15 / gate enable | 20 | c22 | b22 |
| GP16 / first signal | 21 | h22 | j22 |
| GP17 / second signal | 22 | h21 | j21 |
| GP26 / ADC | 31 | h12 | j12 |

VBUS pin 40 at h3 and 3V3 OUT pin 36 at h7 have no external wires. The board's USB socket remains available for programming.

## Place parts with all power disconnected

Resistors have no polarity. For axial parts spanning five rows, form the leads gently to the hole spacing while supporting the lead near the body. Do not force the body down or strain the ceramic capacitor. The resistor bands show nominal five-band 1% parts; confirm the resistance/value of the purchased part with a meter.

| Part | First hole | Second hole | Important detail |
| --- | --- | --- | --- |
| D1, 1N5819 | a30 anode | a35 cathode | Silver stripe toward row 35 |
| R_TOP, 100 kΩ 1% | a40 | a45 | Battery divider upper resistor |
| R_BOTTOM, 47 kΩ 1% | b45 | b50 | Battery divider lower resistor |
| C_ADC, 100 nF ceramic | e45 | e46 | Non-polar; adjacent rows, **not two holes in one row** |
| R_EN, 100 kΩ | a55 | a60 | Gate-enable pulldown |
| R_PWM0, 1 kΩ | f30 | f35 | First servo signal series resistor |
| R_PWM1, 1 kΩ | f40 | f45 | Second servo only |

| Jumper | From | To | Function |
| --- | --- | --- | --- |
| J1 | b35 | j4 | D1 cathode to VSYS |
| J2 | c50 | j5 | Ground to Pico |
| J3 | b22 | b55 | GP15 to gate-enable strip |
| J4 | j22 | j30 | GP16 to R_PWM0 input |
| J5 | j21 | j40 | GP17 to R_PWM1 input; second servo only |
| J6 | d45 | j12 | ADC divider junction to GP26 |
| J7 | d46 | d50 | Capacitor return to ground strip |
| J8 | b60 | e50 | Enable-pulldown return to ground strip |

The five sockets a50–e50 are all used, once each. A wire laid over other holes does not connect to them; only the two inserted ends count. Use the hole table rather than interpreting a cable crossing as a junction.

## Connect the power harness beside the board

The right-hand diagram cards label **electrical destinations**, not the positions of the module pads. Use the actual modules' printed VIN/VOUT/GND/ON labels and the [continuous circuit map](../hardware/wiring/connection-map.svg).

Build and insulate the battery → fuse → RCY → master → regulator → gate → servo power path according to the [wiring guide](wiring.md). The RCY disconnect breaks both battery leads. Connect all grounds on this power assembly. Add **C1** positive to regulator 5 V, negative stripe to ground near gate VIN; **D2** stripe to switched servo 5 V, anode to ground; and **R_BLEED** between switched servo 5 V and ground. Neither D2 nor the bulk capacitor belongs on the ADC strip. Keep master ON and regulator ENABLE unused; the servo gate's physical slider stays OFF.

| Lead | Breadboard end | External destination |
| --- | --- | --- |
| L1 | b30 | Regulated 5 V junction P5V (REG VOUT, gate VIN, C1 positive) |
| L2 | a50 | Common ground junction PGND |
| L3 | b40 | PACK_SW junction: master VOUT / regulator VIN, before regulation |
| L4 | c55 | Servo gate ON input |
| L5 | j35 | Servo 0 signal conductor only |
| L6 | j45 | Servo 1 signal conductor only; second servo only |

P5V, PACK and PGND are names for insulated wire junctions, not additional boards to purchase. Retain the servo's original mating plug using the selected extension: its power and ground wires go to the external harness, and its signal wire joins L5 or L6. Confirm the actual wire order; do not rely on colors alone. The motor current must have its direct positive and return path, independent of the breadboard.

## First-power checks

1. With USB and batteries disconnected, check every part and jumper against the tables. Check no positive net is shorted to GND; check D1, D2 and C1 polarity. Confirm your breadboard copper strips match the diagram.
2. **Lift the Pico out of the breadboard**, leaving jumpers in place. Disconnect both servos. Connect the external harness including L1, L2 and L3; this lets you test without applying unknown voltages to Pico pins.
3. Insert the four matched NiMH cells, turn the master on, and use the meter in **DC voltage mode**, black probe in the free hole c60 (GND). Measure free hole c30: nominal regulated **5 V**. Measure free hole c35: the diode-fed Pico supply, below or very close to 5 V with no load; it must never exceed the Pico's 5.5 V VSYS maximum. A diode drop is load-dependent, so do not require a fixed 4.7 V reading.
4. Measure free hole c45: approximately pack voltage × 47/147; e.g. **1.53 V at 4.8 V pack**, or **2.05 V at 6.4 V pack**. It must be below 3.3 V with margin. Compare L3's measured pack voltage and the actual resistor values. Do not insert the Pico if readings disagree.
5. Turn the master off, unplug the battery connector, verify the rails have fallen, then reinstall the Pico at c3/h3. Connect USB for firmware/configuration as needed. Verify the servo gate slider is OFF and its output is off at startup.
6. With power removed again, attach **one unloaded servo**. Power up and use the project's calibrated, bounded motion procedure. The second servo stays unplugged until the first works. Check supply droop and connections before trying the mechanism. Firmware is fail-closed until calibrated; this diagram does not authorize an automatic full-angle sweep.

Do not put a meter in current mode across the battery terminals. No electrical or physical assembly has been tested by generating this diagram; these are instructions and checked design geometry.

## Rebuild and electrical validation

`hardware/wiring/breadboard/layout.json` is the canonical hole plan. The generator creates the SVG and CSV. The independent validator joins actual five-hole strips and declared wires, then checks them against all harness terminals. It does not electrically join the two ends of resistors or diodes when comparing nets. It also checks all 40 Pico header positions, unused-pin isolation and hole occupancy.

```sh
python3 tools/render_breadboard.py
python3 tools/verify_breadboard.py
python3 tools/build_learning.py
python3 -m unittest discover -s tests -p 'test_breadboard.py' -v
```

Both one- and two-servo profiles pass the design checks. This does not measure breadboard contact quality, wire resistance, lead clearances, radio performance or real startup current.
