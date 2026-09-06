# Bill of materials — auto-switch

**Current POC:** [One servo, switched AA holder and breadboard rails](docs/poc-wiring.md) · [ASCII circuit](docs/poc-wiring.txt). Use that parts checklist; the earlier WAGO and gated BOMs below are references.

**Current build: simplified AA demo with one servo, using your headered Pico.**

- [Amazon-first shopping list with exact parts and quantities](docs/aa-demo-shopping.md)
- [AA demo BOM CSV](hardware/aa-demo-bom.csv)
- [Illustrated breadboard viewer](learn/aa-demo.html) · [One-servo SVG](hardware/wiring/aa-demo/breadboard-1-servo.svg)
- [Assembly guide and AA firmware profile](docs/aa-demo-plan.md)

Use the AA-demo list for new bench purchases. The older BOM below describes the gated enclosure and its historical fit audit; it does not certify the new WAGO/breadboard assembly or add those parts to your current shopping list.

---

## Earlier gated prototype — reference BOM

**Earlier gated assembly: headerless Raspberry Pi Pico W, direct-soldered wires, four rechargeable AA cells.** One-gang controls one paddle; two-gang controls two. Each room needs its own complete unit. The current design does **not** use a PiCowBell, male Pico headers or a separate header adapter. Your headered Pico remains useful for bench tests.

[Download the BOM CSV](hardware/bom.csv) · [Detailed purchasing notes](docs/shopping-list.md) · [Actual STL fit report](docs/bom-fit-report.md) · [Wiring guide](docs/wiring.md)

Quantities below are **installed quantities per device**, except rows marked shared or allowance. Buy the smallest pack covering the count; the fuse purchase is three (one installed, two spares), and the 100 nF capacitor purchase is three (one installed, two spares). The Panasonic kit includes one external charger and the first four cells. Nothing has been purchased. Purchase links are selections, not live stock or price guarantees.

**Fit status: nominal digital checks pass; physical fit is not certified.** The purchased-part meshes were checked against the actual STL triangles, not only compared with a dimensions list. The exact MG90S/horn, loaded holder, soldered harness, connectors and installed wallplate still require measurements and coupon tests. Horn-to-yoke fasteners and the mounting method for the textured wall remain unresolved. Do not order a full kit on the assumption that these two interfaces are finalized.

## Electronics / harness

| Part / purchase link | One-gang | Two-gang | Quantity unit | Fit status |
|---|---:|---:|---|---|
| [Raspberry Pi Pico W (headerless)](https://www.raspberrypi.com/products/raspberry-pi-pico/) | 1 | 1 | piece | nominal geometry; physical fit pending |
| [Pololu 1153](https://www.pololu.com/product/1153) | 1 | 1 | piece | nominal geometry; physical fit pending |
| [Pololu 2574 S18V20F5](https://www.pololu.com/product/2574) | 1 | 1 | piece | nominal geometry; physical fit pending |
| [Pololu 2810 Mini MOSFET Slide Switch LV](https://www.pololu.com/product/2810) | 2 | 2 | piece | nominal geometry; physical fit pending |
| [Adafruit 1608 quarter Perma-Proto](https://www.mouser.com/en/ProductDetail/Adafruit/1608?qs=GURawfaeGuCPUqYJerHUuQ%3D%3D) | 1 | 1 | piece | nominal geometry; physical fit pending |
| [Littelfuse 01500274Z](https://www.digikey.com/en/products/detail/littelfuse-inc/01500274Z/29453) | 1 | 1 | piece | nominal geometry; physical fit pending |
| [SCHURTER 0001.2507 SPT 5x20 2A time-lag](https://www.digikey.com/en/products/detail/schurter-inc/0001-2507/639706) | 1 | 1 | piece | standard 5×20 holder interface; verify actual assembly |
| [Pololu 2180 JST RCY female pigtail](https://www.pololu.com/product/2180) | 1 | 1 | piece | allowance only; measure and route actual item |
| [Pololu 2181 JST RCY male pigtail](https://www.pololu.com/product/2181) | 1 | 1 | piece | allowance only; measure and route actual item |
| [Pololu 2169 12-inch twisted servo extension](https://www.pololu.com/product/2169) | 1 | 2 | piece | allowance only; measure and route actual item |
| [Panasonic EEUFR1A471](https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ast-ind-152838.pdf) | 1 | 1 | piece | component body space only; board wiring not pad-routed |
| [KEMET C315C104K5R5TA](https://search.kemet.com/component-documentation/download/specsheet/C315C104K5R5TA) | 1 | 1 | piece | component body space only; board wiring not pad-routed |
| [Vishay 1N5819-E3/73](https://www.vishay.com/docs/88525/1n5817.pdf) | 2 | 2 | piece | component body space only; board wiring not pad-routed |
| [Yageo MFR-25FBF52-100K](https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf) | 2 | 2 | piece | component body space only; board wiring not pad-routed |
| [Yageo MFR-25FBF52-47K](https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf) | 1 | 1 | piece | component body space only; board wiring not pad-routed |
| [Yageo MFR-25FBF52-1K](https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf) | 2 | 3 | piece | component body space only; board wiring not pad-routed |
| [Adafruit 3111 22AWG stranded six-color spool set](https://www.adafruit.com/product/3111) | 1 | 1 | metre (cut allowance) | allowance only; measure and route actual item |
| [Adafruit 344 heat-shrink assortment](https://www.adafruit.com/product/344) | 1 | 1 | shared pack | allowance only; measure and route actual item |
| [Adafruit 3879 USB-C to Micro-B 0.3m](https://www.adafruit.com/product/3879) | 1 | 1 | shared cable | allowance only; measure and route actual item |
| [Panduit PLT1M-C](https://www.digikey.com/en/products/detail/panduit-corp/PLT1M-C/280033) | 6 | 6 | piece | allowance only; measure and route actual item |

## Actuator

| Part / purchase link | One-gang | Two-gang | Quantity unit | Fit status |
|---|---:|---:|---|---|
| [Existing MG90S 180-degree servo; TowerPro drawing reference](https://towerpro.com.tw/product/mg90s-3/) | 1 | 2 | piece | provisional; user brand and mounting dimensions unknown |
| [Original matching double-arm servo horn](https://towerpro.com.tw/product/mg90s-3/) | 1 | 2 | piece (included with servo) | provisional; actual horn required |
| [Original servo horn centre screw](https://towerpro.com.tw/product/mg90s-3/) | 1 | 2 | piece (included with servo) | unverified thread; reuse original only |
| Horn-to-yoke screws: specification pending horn measurement | 2 | 4 | planned fastening point | BLOCKED: exact fastener not selected |

## Battery

| Part / purchase link | One-gang | Two-gang | Quantity unit | Fit status |
|---|---:|---:|---|---|
| [Panasonic eneloop AA NiMH (four matched cells)](https://www.panasonicbatteryproducts.com/product/eneloop-combo-packs/) | 4 | 4 | cell | nominal AA envelope; loaded holder height pending |

## Shared tools

| Part / purchase link | One-gang | Two-gang | Quantity unit | Fit status |
|---|---:|---:|---|---|
| [Panasonic BQ-CC17 external charger (K-KJ17MCA4BA kit)](https://www.panasonicbatteryproducts.com/product/eneloop-combo-packs/) | 1 | 1 | shared charger | outside enclosure |
| [M2x0.4 hand tap and holder](https://www.mcmaster.com/products/taps/thread-size~m2/) | 1 | 1 | shared tool | outside enclosure |
| Digital calipers and multimeter | 1 | 1 | shared tool set | outside enclosure |

## Mechanical hardware

| Part / purchase link | One-gang | Two-gang | Quantity unit | Fit status |
|---|---:|---:|---|---|
| [Westfield WF52650 M2×6 nylon cheese-head screws](https://www.westfieldfasteners.co.uk/Bolts-Screws-Metric/Plastic-Machine-Screw-Slotted-Cheese-M2x6-Nylon.html) | 4 | 4 | piece | nominal interface check; physical assembly pending |
| [Bambu AA030 M2.5x8 SHCS](https://us.store.bambulab.com/en/products/m2-5-socket-head-cap-machine-screws-shcs-1) | 16 | 16 | piece | nominal interface check; physical assembly pending |
| [Bambu AA037 M3x8 SHCS](https://us.store.bambulab.com/products/m3-socket-head-cap-machine-screws-shcs-1) | 4 | 4 | piece | nominal interface check; physical assembly pending |
| [Bambu AA036 M3x6 SHCS](https://us.store.bambulab.com/products/m3-socket-head-cap-machine-screws-shcs-1) | 4 | 4 | piece | nominal interface check; physical assembly pending |
| [M3x0.5 standard hex nuts: 5.5 mm AF, max 2.4 mm thick](https://www.mcmaster.com/products/metric-hex-nuts/) | 4 | 4 | piece | nominal interface check; physical assembly pending |
| [M2x0.4 x10mm A2 socket-head screws](https://www.kljack.com/products/-2c10kcss/) | 2 | 4 | piece | nominal interface check; physical assembly pending |
| [M2x0.4 standard hex nuts: 4 mm AF, max 1.6 mm thick](https://www.mcmaster.com/products/metric-hex-nuts/) | 2 | 4 | piece | nominal interface check; physical assembly pending |
| [M2 flat washers: 2.2 mm ID, 5 mm OD, 0.3 mm thick](https://www.mcmaster.com/products/metric-washers/) | 2 | 4 | piece | nominal interface check; physical assembly pending |
| [Panduit PLT2M-C 2.5mm x~200mm cable ties](https://www.digikey.com/en/products/detail/panduit-corp/PLT2M-C/280041) | 2 | 2 | piece | nominal interface check; physical assembly pending |
| [3M SJ5302 urethane bumper: Ø7.9×2.2 mm](https://www.3m.co.uk/3M/en_GB/p/dc/v000180779/) | 2 | 4 | piece | nominal interface check; physical assembly pending |

## Installation

| Part / purchase link | One-gang | Two-gang | Quantity unit | Fit status |
|---|---:|---:|---|---|
| [External support for textured wall: selection unresolved](https://www.command.com.sg/3M/en_SG/command-sg/how-to-use/picture-hanging-strips/) | 1 | 1 | mounting arrangement | BLOCKED: photographed wall excludes selected Command strips |

## Print material

| Part / purchase link | One-gang | Two-gang | Quantity unit | Fit status |
|---|---:|---:|---|---|
| PETG filament | 1 | 1 | shared spool | slicer and print calibration required |

## What to print

These are installed print quantities, **not** one copy of every STL. Each unit uses its own pod and lid. Two copies of the docking strap are needed for either unit. The shared pod has 170 × 158 × 40 mm internal space; the assembled layout is about 174 × 300.7 × 47 mm. We retained wiring/service space instead of assuming a bare Pico automatically makes the whole pod smaller.

| STL | One-gang | Two-gang |
|---|---:|---:|
| [1g_chassis.stl](hardware/cad/generated/1g_chassis.stl) | 1 | 0 |
| [1g_servo1_yoke.stl](hardware/cad/generated/1g_servo1_yoke.stl) | 1 | 0 |
| [2g_chassis.stl](hardware/cad/generated/2g_chassis.stl) | 0 | 1 |
| [2g_servo1_yoke.stl](hardware/cad/generated/2g_servo1_yoke.stl) | 0 | 1 |
| [2g_servo2_yoke.stl](hardware/cad/generated/2g_servo2_yoke.stl) | 0 | 1 |
| [docking_strap.stl](hardware/cad/generated/docking_strap.stl) | 2 | 2 |
| [electronics_lid.stl](hardware/cad/generated/electronics_lid.stl) | 1 | 1 |
| [electronics_pod.stl](hardware/cad/generated/electronics_pod.stl) | 1 | 1 |
| [retainer_master.stl](hardware/cad/generated/retainer_master.stl) | 1 | 1 |
| [retainer_proto.stl](hardware/cad/generated/retainer_proto.stl) | 1 | 1 |
| [retainer_regulator.stl](hardware/cad/generated/retainer_regulator.stl) | 1 | 1 |
| [retainer_servo_gate.stl](hardware/cad/generated/retainer_servo_gate.stl) | 1 | 1 |

Print the relevant wallplate fit ring, `coupon_pico_mount.stl`, `coupon_servo_ear_mount.stl`, `coupon_battery_holder.stl` and four board cradles **first**. Cradle coupons use their matching retainer. Coupon screws can be reused in the device after testing. Coupon material and brim/support consumption depend on slicer settings.

## Headerless Pico connection and mounting

Four M2×6 **nylon** screws hold the actual Pico board through its Ø2.1 mm mounting holes. Pre-tap the printed pilots M2×0.4; nylon screws are not self-tapping. The official Pico W model includes the board, USB socket and major components. Wires solder directly to the pads labelled VSYS, GND, GP15, GP16, GP26, and GP17 for the second servo. The board remains tethered to its harness when unscrewed; leave a service loop and strain relief.

The old socketed arrangement is available in Git history. Its carrier and four M2.5×6 mounting screws do not fit the new default mounting scheme. Do not push the already-headered board into this lower mounting position.

The [CSV](hardware/bom.csv) has the per-part STL mapping, source URLs and detailed assembly notes. The [fit report](docs/bom-fit-report.md) separates source dimensions, design allowances and unresolved physical measurements.
