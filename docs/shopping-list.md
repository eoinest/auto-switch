# Selected prototype shopping list

This is a concrete set of parts for **one two-gang actuator**. Use the Pico W / Pico 2 W, two MG90S servos, soldering tools, and printer you already have. One-gang uses the same electronics but one servo, one extension, and one fewer 1k signal resistor. A second independent room unit needs another complete electronics set and four cells; charger, wire spools, USB cable, and tools can be shared. Nothing has been purchased.

The selected modules preserve firmware GP15 servo power control. The physical fit is based on vendor drawings where available, with explicit allowances for unreported connectors, soldered headers, and wires. See [machine-readable dimensions](../hardware/components/power-parts.json), [wiring](wiring.md), and [power calculations](power.md). Measure the actual holder with cells, your servo horns, and your soldered Pico before printing the final shell.

## Battery, power and sockets

| Buy quantity | Exact selection and purchase link | What it does |
| --- | --- | --- |
| 1 | [Pololu 1153 four-AA holder](https://www.pololu.com/product/1153) | Removable cells; wire leads, not a 9V snap connector. Published holder 63 × 58 × 16 mm; loaded-cell clearance is still a measurement. |
| 1 kit | Panasonic **K-KJ17MCA4BA**, BQ-CC17 charger with four eneloop AA cells; [manufacturer catalog](https://www.panasonicbatteryproducts.com/wp-content/uploads/2024/01/2023-PANASONIC-CATALOG_DIGITAL.pdf), [manufacturer combo-pack/store links](https://www.panasonicbatteryproducts.com/product/eneloop-combo-packs/) | Charge cells outside the device. Use four matched AA NiMH cells; this is not a Li-ion battery design. Check the exact kit code and included cell capacity when ordering. |
| 1 | [Pololu 2574 S18V20F5 5V regulator](https://www.pololu.com/product/2574) | Buck-boost supply. Direct-solder wires; included optional terminal blocks are not in the enclosure envelope. |
| 2 | [Pololu 2810 Mini MOSFET Slide Switch LV](https://www.pololu.com/product/2810) | One accessible physical master, one servo gate controlled through its ON pad. Servo gate slider stays OFF under a cover. Master ON pad unused. |
| 1 | [Adafruit 5905 Proto Under Plate PiCowBell](https://www.adafruit.com/product/5905) | Detachable Pico carrier with pre-soldered female sockets. **No additional pair of 20-pin female headers needed.** |
| 1 | [Adafruit 1608 quarter Perma-Proto](https://www.adafruit.com/product/1608); [DigiKey exact part](https://www.digikey.com/en/products/detail/adafruit-industries-llc/1608/5154676); [Mouser exact part](https://www.mouser.com/en/ProductDetail/Adafruit/1608?qs=GURawfaeGuCPUqYJerHUuQ%3D%3D) | Discrete components and harness junctions. Manufacturer and DigiKey were out of stock when researched; Mouser lists the exact part but live availability was not verified. Do not substitute a different board size without updating CAD. |
| 1 | [Littelfuse 01500274Z inline 5×20 fuse holder](https://www.digikey.com/en/products/detail/littelfuse-inc/01500274Z/29453) | Near the battery positive lead. Prewired 16AWG loop is cut and trimmed; body about 47.5 × Ø11 mm. |
| 3 | [SCHURTER 0001.2507 2A time-lag ceramic fuse](https://www.digikey.com/en/products/detail/schurter-inc/0001-2507/639706) | One fitted, two spares. Explicit DC rating in [manufacturer specification](https://www.schurter.com/en/datasheet/SPT_5x20). Verify pulse/fault coordination during bench testing. |

The 2810 switch boards are assembled, but harness soldering is still required. The master protects the regulator and ADC divider against reversed input. Its LED costs about 1 mA continuously, now included in the estimator. The gate is not a hardware current limiter or timeout. The firmware operates the servos sequentially: the regulator's “2A” label is not a guarantee of continuous capability at a discharged pack voltage inside the printed pod.

## Connectors and wires

| Buy quantity | Exact selection | Connection |
| --- | --- | --- |
| 1 each | [Pololu 2180 female RCY pigtail](https://www.pololu.com/product/2180) and [2181 male RCY pigtail](https://www.pololu.com/product/2181) | Matched, precrimped 20AWG battery connector pair. Place the recessed-contact half on the fused battery side. Check physical contacts and polarity, since RC male/female naming can be confusing. |
| 2 | [Pololu 2169 12-inch twisted servo extension](https://www.pololu.com/product/2169) | 22AWG, male-to-female. For the fitted build, cut it to retain the male end with about 100mm of wire, then solder to the component board. One extension for one-gang. |
| 1 optional bench strip | [Pololu 965 40-pin straight male header](https://www.pololu.com/product/965) | Optional for a bench setup retaining the complete extensions: break into two three-pin lengths, 2.54mm pitch. Mark GND / +5V / signal. Final fitted harness below solders directly. |
| 1 shared set | [Adafruit 3111 six-color 22AWG stranded wire set](https://www.adafruit.com/product/3111) | Direct solder power and ground harness; budget roughly 1m total hookup per unit, trim after dry-fit. Existing equivalent stranded wire can replace this purchase. |
| 1 pack; allow 12 ties per unit | [Panduit PLT1M-C](https://www.digikey.com/en/products/detail/panduit-corp/PLT1M-C/280033), 99 × 2.5mm | Strain relief through printed tie slots; trim tails. Count is a routing allowance, not a validated assembly count. |
| 1 shared pack | [Adafruit 344 heat-shrink assortment](https://www.adafruit.com/product/344) | Insulate soldered splices and exposed component leads. |
| 1 shared cable | [Adafruit 3879 USB-C to Micro-B data cable, 0.3m](https://www.adafruit.com/product/3879) | Mac commissioning and firmware uploads through the accessible Pico socket. Existing working data cable is fine. No panel adapter is necessary. |

For the **fitted harness**, the servo female connector plugs into the retained extension male connector. Its three shortened wires solder directly to the component-board ground, switched 5V, and per-channel signal-resistor output. Choose final wire length after dry-fit, insulate it, and secure a small service loop; do not pack the unused 300mm extension plus original servo lead into a coil near the antenna. The unused female half is a bench spare. This leaves each servo detachable without needing the optional male-header strip.

No crimp tool is needed for these prewired connectors. Solder the carrier's duplicated GPIO/VSYS/GND pads to the component board so the Pico itself stays removable. Use direct 22AWG power connections rather than assuming the protoboard's thin buses are rated for motor pulses. Keep every ground common, and route the motor return directly to the power branch. Solder alone is not strain relief: secure the insulated wires through the pod's tie features. Keep a service loop so opening the lid cannot pull on solder joints.

RCY is specified for 3A with 22AWG in [JST's specification](https://www.jst.com/products/wire-to-wire-connectors/rcy-connector/); thicker pigtails do not increase that contact rating. Do not use a servo Y cable joining two signal wires. Do not use thin breadboard jumper leads as the battery/servo power harness. Actual MG90S connector shape and wire colors must be checked before connection.

## Small components

| Installed quantity (two-gang) | Exact selected part and purchase link | Use |
| --- | --- | --- |
| 1 | [Panasonic EEU-FR1A471](https://www.mouser.com/en/ProductDetail/Panasonic-Industry/EEU-FR1A471?qs=tfZGHB2PWd0zwvBgXk6r8A%3D%3D), 470µF 10V radial | C1 across unswitched regulated 5V and ground; observe polarity. Nominal can Ø8 × 11.5mm, 3.5mm lead pitch; allow 13mm seated height. |
| 1; buy 3 | [KEMET C315C104K5R5TA](https://www.digikey.com/en/products/detail/kemet/C315C104K5R5TA/12701330), 100nF 50V radial | One ADC filter capacitor; two spares for local supply bypass if bench layout needs them. |
| 2 | [Vishay 1N5819-E3/73](https://www.digikey.com/en/products/detail/vishay-general-semiconductor-diodes-division/1N5819-E3-73/2139980), 1A 40V Schottky | D1 supply ORing to Pico VSYS; D2 negative servo-rail clamp. Stripe is cathode. Follow the wiring diagram: their orientations differ. |
| 2 | [Yageo MFR-25FBF52-100K](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-100K/13473), 100k 1% ¼W | Battery divider top and GP15 gate pulldown. |
| 1 | [Yageo MFR-25FBF52-47K](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-47K/9138173), 47k 1% ¼W | Battery divider bottom. |
| 3 | [Yageo MFR-25FBF52-1K](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-1K/13011), 1k 1% ¼W | One per PWM signal plus one switched-rail bleeder. One-gang installs two. |

Primary dimensions: [Panasonic FR drawing/table](https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ast-ind-152838.pdf), [KEMET part sheet](https://search.kemet.com/component-documentation/download/specsheet/C315C104K5R5TA), [Vishay 1N5819](https://www.vishay.com/docs/88525/1n5817.pdf), [Yageo MFR](https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf). Prices, packaging minimums, and stock can change; choose single pieces/cut tape rather than factory reels.

## What is exact, and what still needs fitting

The carrier outline and mounting-hole coordinates come from [Adafruit's 5905 Eagle source](https://github.com/adafruit/Adafruit-Proto-Under-Plate-PiCowBell-PCB): 52.07 × 38.10mm PCB, four 2.5mm drilled holes centered at X=±23.495, Y=±16.510mm. Its product envelope excludes the plugged-in Pico and your existing headers. The vendor's guide links a model for another PiCowBell SKU; that is not evidence of a 5905 model.

The [regulator drawing](https://www.pololu.com/file/0J1417/s18v20x-step-up-step-down-voltage-regulator-dimensions.pdf) and [switch drawing](https://www.pololu.com/file/0J1103/mini-mosfet-slide-switch-with-reverse-voltage-protection-dimension-diagram.pdf) establish PCB outlines. Wire exits, solder blobs, connector insertion space, and print tolerances remain assembly allowances. The 2810 electrical holes are not mounting screw holes. The holder's stated 16mm height is not proof that a loaded holder occupies only 16mm.

Reserve a region free of extra metal, wire bundles, battery cells, and power modules around the Pico antenna; 10mm is this project's preliminary clearance, not a certified radio keepout. The PiCowBell manufacturer supports Pico W use, but that does not establish the assembled enclosure's radio performance. Test Wi-Fi with the populated pod closed, in the final orientation, before trusting the battery estimate: retries increase energy use.

## Mechanical hardware and contact pads

These quantities match the current CAD assembly. Buy the next pack size above the installed quantity. Standard metric equivalents are fine when head and nut dimensions match; countersunk screws are not substitutes for the selected flat-bearing socket caps.

| Installed quantity | Selection | Position |
| --- | --- | --- |
| 4 | [Bambu AA029, M2.5×6 SHCS](https://us.store.bambulab.com/en/products/m2-5-socket-head-cap-machine-screws-shcs-1), one 20-pack | PiCowBell mounting. Head Ø4.3 × 2.35mm. |
| 16 | [Bambu AA030, M2.5×8 SHCS](https://us.store.bambulab.com/en/products/m2-5-socket-head-cap-machine-screws-shcs-1), one 20-pack | Four removable perimeter retainers: regulator, protoboard, two switches. |
| 4 | [Bambu AA037, M3×8 SHCS](https://us.store.bambulab.com/products/m3-socket-head-cap-machine-screws-shcs-1), one 20-pack | Electronics lid. Head Ø5.4 × 2.8mm. |
| 4 | [Bambu AA036, M3×6 SHCS](https://us.store.bambulab.com/products/m3-socket-head-cap-machine-screws-shcs-1), one 20-pack | Pod-to-frame docking. |
| 4 | M3×0.5 standard hex nuts, 5.5mm across flats, 2.4mm maximum thickness; [McMaster metric nut selector](https://www.mcmaster.com/products/metric-hex-nuts/) | Docking nut pockets. Confirm the selected nut dimensions rather than substituting tall locking nuts. |
| 4; one-gang 2 | M2×0.4 × 10mm socket-head screws, plus matching M2 hex nuts and M2 flat washers; [K.L. Jack M2×10 A2 socket screw](https://www.kljack.com/products/-2c10kcss/), [metric nut selector](https://www.mcmaster.com/products/metric-hex-nuts/), [washer selector](https://www.mcmaster.com/products/metric-washers/) | Two screws/nuts/washers per servo mounting ear pair. Verify ear thickness and nut engagement on your MG90S. |
| 2 | [Panduit PLT2M-C](https://www.digikey.com/en/products/detail/panduit-corp/PLT2M-C/280041), 2.5mm-wide × approximately 200mm ties | Battery holder straps. Separate from the shorter wire ties above. |
| 4; one-gang 2 | **3M SJ5302** clear hemispherical Bumpon pads, Ø7.9 × 2.2mm; [manufacturer specification and buying options](https://www.3m.co.uk/3M/en_GB/p/dc/v000180779/) | One contact pad at each end of each yoke. Urethane, not silicone; prevents hard plastic contact but does not replace force/angle calibration. |
| 4 pairs initially | **3M Command 17201-4PK-ES** medium picture-hanging strips; [manufacturer 17201 family](https://www.commandbrand.com.au/3M/en_AU/p/d/v000081764/), [US exact four-pair pack](https://www.fleetfarm.com/detail/command-medium-picture-hanging-strips/0000000361272) | Two frame lands plus pod support. Medium strip footprint approximately 19×70mm; measure mated thickness before setting fit depth. Keep removal tabs accessible. |

The frame has two 20×78mm adhesive lands. Do not trim Command strips to force a fit, cover their pull tabs, or interpret a picture-hanging weight rating as an allowable repeated servo peeling force. The photographed wall appears textured; [3M explicitly excludes textured walls and rough surfaces](https://www.command.com.sg/3M/en_SG/command-sg/how-to-use/picture-hanging-strips/). These strips are a conditional pick for a suitable smooth mounting surface, not approval to stick this prototype to the photographed paint. The mounting design needs a different support arrangement if the intended surface is excluded. A snug ring does not itself prove retention under actuation. Follow the strip package's cleaning, pressing, cure, and removal directions.

Reuse the **original servo spline horn and shaft screw**. The horn-to-printed-yoke screw diameter and spacing must come from your actual supplied horn: no generic M2 spline/shaft screw purchase is specified, since forcing the wrong thread can damage the servo. The bench-fit process determines whether the supplied horn screws can retain the yoke or whether matching small screws/nuts are needed. That is the one deliberately unresolved fastener interface.

Use PETG for the functional chassis/yokes and PLA for quick fit coupons if already on hand. A meter, calipers, wire stripper/cutter, and small hex keys (1.5, 2, 2.5mm) are needed for assembly and checks. No battery charger, exposed mains wiring, or wall-plate replacement circuit is built into this enclosure.
