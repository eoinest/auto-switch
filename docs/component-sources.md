# Component geometry and source confidence

**Historical reference — earlier Pico design; not the current build instructions.** For the current ESP32-S2 Mini POC, start with [S2 wiring](s2-aa-poc.md), [S2 firmware](s2-firmware.md) and the [current BOM](../BOM.md).

The Pico W reference now uses **Raspberry Pi's own 3D assembly**, rather than an invented board-shaped box. The repository includes the original STEP archive plus a Blender-importable OBJ with 11 named parts. An MG90S label, however, does not identify one guaranteed mechanical drawing: the original manufacturer's page omits several dimensions needed for a tight mount, and other manufacturers sell different MG90S geometries.

Machine-readable values, source IDs, unresolved measurements, and checksums are in [board-servo.json](../hardware/components/board-servo.json). Final physical-fit approval still requires matching the actual purchased board, servo, solder joints and power components.

## Pico W and Pico 2 W mechanical interface

Both current manufacturer drawings were visually checked: **Pico W datasheet release 7** and **Pico 2 W datasheet release 2**, both built 03 July 2026, printed page 6, Figure 3. Their board outline, mounting pattern, and main header grid match. The components mounted on those boards differ. [Pico W datasheet](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf), [Pico 2 W datasheet](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf).

For this table, the origin is the center of the PCB's **top plane**, x crosses its short dimension, y points toward USB, and z points away from the PCB toward the components. Dimensions are in millimetres. The PCB occupies x = −10.5…10.5, y = −25.5…25.5, and nominally z = −1…0.

| Feature | Confirmed nominal geometry | Evidence and use |
| --- | --- | --- |
| PCB | 21 wide × 51 long × 1 thick | Mechanical specification text; allow manufacturing and print tolerance |
| Mounting holes | Four, diameter 2.1 ± 0.05 | Manufacturer text; use suitable M2 hardware rather than enlarging the PCB holes |
| Hole centers | (−5.7, −23.5), (+5.7, −23.5), (−5.7, +23.5), (+5.7, +23.5) | Derived from Figure 3's 11.4 transverse spacing and 2 mm offset at each short end |
| Main header rows | x = ±8.89 | Figure 3: 17.78 mm row spacing |
| Main header positions | y = 24.13 − 2.54i, i = 0…19 | Twenty per row; 2.54 pitch and 48.26 first-to-last span, centered on board |
| Header drill | Diameter 1 | Figure 3; not the protruding header-pin length |
| Micro-USB shell width | 8 | Figure 3; cable plug is a separate, larger envelope |
| Micro-USB overhang | 1.3 typical beyond USB board edge | Figure 3; original W source CAD measures about 1.35 |
| Antenna carrier cutout | 14 wide × 9 deep at the non-USB end | Section 2.2.1 and Figure 7; center it about x = 0 and reserve y = −25.5…−16.5 under the board |

The antenna guidance applies in three dimensions: keep nearby hardware and material away, particularly the battery, servo metal, wiring, carrier copper and fasteners. The 14 × 9 mm number is a **carrier cutout**, not a claim that objects placed 0.1 mm above that rectangle are harmless. Neither inspected datasheet gives one universal z clearance. Place the antenna at an exposed edge and verify Wi-Fi in the actual enclosure. [Pico W mechanical and keep-out sections](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf).

The current fitted revision uses a **headerless Pico W with direct soldered wires** and four nylon mounting screws. Its PCB hole pattern comes from the official drawing; the generated fit report probes the actual exported mounting posts and checks reserved underside solder and USB access. Solder height and wire bends still require a dry fit. The original headered Pico can be used on the bench.

The earlier socketed revision selected Adafruit 5905 PiCowBell (52.07 × 38.10 mm Eagle outline) and an assumed 18 mm loaded stack. That carrier and header stack are **not in the current default BOM or STL assembly**. The earlier source evidence remains attributable to [Adafruit's carrier](https://www.adafruit.com/product/5905) and [board source](https://github.com/adafruit/Adafruit-Proto-Under-Plate-PiCowBell-PCB).

## Original source CAD and Blender import

| Asset | What it actually contains |
| --- | --- |
| [PicoW-step.zip](../hardware/components/vendor/PicoW-step.zip) | Unmodified official archive; `PicoW.stp`, 2023-08-11 timestamp, assembly `rpi-picow-r3-2.brd` |
| [PicoW.obj](../hardware/components/vendor/PicoW.obj) + [PicoW.mtl](../hardware/components/vendor/PicoW.mtl) | Tessellation with 11 named objects, assembly placements, and available label colors |
| [PicoW-mesh-metadata.json](../hardware/components/vendor/PicoW-mesh-metadata.json) | Per-object exact-CAD bounding boxes, mesh counts, conversion settings and source hash |
| [Vendor notice](../hardware/components/vendor/NOTICE.md) | Raspberry Pi attribution and original design permission; these assets are not relicensed as this project's MIT work |

The official model contains three PCB layers and eight major components: USB, RF shield, RP2040, regulator, diode, LED, BOOTSEL switch and crystal. It does not contain a complete set of passives or headers. Thus it is a **manufacturer enclosure reference**, not a reconstruction of every manufactured detail. The original source is available from [Raspberry Pi's Pico W STEP download](https://pip.raspberrypi.com/documents/RP-008318-DS).

OBJ coordinates preserve the STEP's origin: x = 0…21, y = 0…51 with USB toward +y, PCB component-side reference z = 0. To use the centered convention above, subtract 10.5 from x and 25.5 from y. Import with x/y/z preserved and scale 1 when the Blender project treats one model unit as one millimetre; use scale 0.001 in a scene modeled in metres. OBJ has no inherent unit declaration.

The original W USB part is named **J1 / FCI_10103594-0001LF**. Its normalized CAD bounding box is approximately x = −3.995…3.995, y = 20.794…26.850, z = −0.800…2.695. The STEP's PCB bottom is −0.9607 rather than exactly −1; keep the datasheet's nominal 1 mm board thickness for clearance design. These numbers describe the receptacle, not a plugged-in USB cable. Measure the actual molded plug, reserve its insertion path, and preserve access to BOOTSEL.

The converter is optional and does not change firmware dependencies:

```sh
python3 -m venv /tmp/auto-switch-step-env
/tmp/auto-switch-step-env/bin/python -m pip install cadquery-ocp==8.0.1.0.0
/tmp/auto-switch-step-env/bin/python hardware/components/convert_step.py
```

The checked conversion used Python 3.12 and cadquery-ocp 8.0.1.0.0. Linear tessellation deflection is 0.03 mm and angular deflection is 0.2 radians. A color is preserved where the source supplies a part-label color; otherwise the exporter uses gray. It does not invent silkscreen, textures, missing components or header dimensions.

### Pico 2 W source-link mismatch

The current Pico 2 W datasheet's section 1.1 links to [RP-009061-CA](https://pip.raspberrypi.com/documents/RP-009061-CA). That downloaded archive contains `rpi_pico2.step` with root product `rpi_pico2`, including an RP2350A and the non-wireless layout. It is the **Pico 2 model**, not a verified Pico 2 W assembly. The official Pico 2 W product portal currently lists its datasheet, pinout and schematic, but no separately named 2 W STEP. This is why the repository does not silently substitute that file as an exact 2 W model. [Pico 2 W product portal](https://pip.raspberrypi.com/categories/1088-raspberry-pi-pico-2-w).

The common board footprint can support a fit-planning proxy for either W generation. A detailed Pico 2 W visual reference must remain labeled a proxy until a correct vendor model or measurements establish its component geometry.

## MG90S geometry

The original [TowerPro MG90S product page](https://towerpro.com.tw/product/mg90s-3/) publishes a six-letter dimension table with a [generic dimension key](https://towerpro.com.tw/wp-content/uploads/2014/07/%E5%B0%8F%E9%A6%AC%E9%81%94%E5%B0%BA%E5%AF%B8%E6%A8%99%E7%A4%BA%E5%9C%96B.jpg). The key was visually inspected to avoid mistaking overall shaft height for case height or mounting-hole pitch for ear span.

Use a servo-local axis convention: x follows the long case dimension, y crosses its width, and z points along the output shaft; z = 0 is the case base. The exact x position of the shaft relative to the case center is not established by the original table.

| Letter | Published value, mm | Meaning shown in manufacturer's key |
| --- | --- | --- |
| A | 32.5 | Base to output shaft tip |
| B | 22.8 | Main case length |
| C | 28.4 | Base to highest gearbox housing, excluding output shaft |
| D | 12.4 | Case width |
| E | 32.1 | Overall tip-to-tip mounting-ear span; **not hole pitch** |
| F | 18.5 | Base to underside of mounting ears |

The same page's short specification says 22.8 × 12.2 × 28.5 mm. The width differs by 0.2 mm from its table and the height convention differs. Keep that discrepancy visible. Use these values as a **TowerPro reference profile**, and measure the actual servos before a close-fitting print. The included arms and screws should be retained; the published page does not establish the shaft spline, center-screw thread, horn-hole pattern, ear-hole pitch, ear thickness, cable-exit envelope or their tolerances.

There is concrete evidence that other MG90S variants differ. A supplier-hosted **Shenzhen Sky Star Technology MG90S Analog Servo** datasheet gives a 22.4 × 12.1 × 22.8 mm case specification and a 20-tooth, 4.9 mm horn spline. Those are that manufacturer's values; they must not be assigned to the user's servo or to the original TowerPro part without identification. [Sky Star manufacturer sheet hosted by TinyTronics](https://www.tinytronics.nl/product_files/000263_Data_Sheet_of_MG90S_Analog_Servo_Motor.pdf).

No manufacturer-authorized MG90S STEP model was established in this research. Community CAD may be useful as an appearance reference, but it does not remove those missing measurements. The printed servo cradle should therefore use measured bodies and mounting holes, or adjustable slots and a removable retainer. The lever should attach to the **supplied horn**, avoiding an unverified printed spline.

## Measurements still needed for final fit

1. Use the selected headerless Pico W for the current source-matched assembly. A different board variant or existing soldered headers requires rechecking the component envelope.
2. Actual underside solder-joint height, direct-wire bend and strain relief, nylon screw engagement, and USB plug clearance.
3. Servo case length/width/height; mounting-ear span, underside height, thickness, hole diameter and center spacing; shaft center relative to case; highest horn/screw height and cable bend envelope.
4. The supplied horn's center and peripheral holes, retaining screw, and clearance through the printed adapter.
5. Actual USB plug envelope and insertion space, and the single/double wall-plate dimensions from the mechanical guide.

The unknown fields remain `null` in the component manifest rather than being presented as exact dimensions. Source drawings establish nominal geometry; they do not establish this printer's tolerance, the user's individual servo variant, or a tested assembled fit.
