# Hardware and fit

## What the switches are called

The photo shows **decorator rocker switches**, also called **paddle switches** or **Decora-style switches**, in a **two-gang wallplate**. Decora is Leviton's brand name; the shape alone does not identify the manufacturer. The bedroom version is a one-gang decorator wallplate. “Gang” counts adjacent device positions; it does not identify whether the switch circuit is single-pole or three-way. [Leviton product terminology](https://leviton.com/content/dam/leviton/distribution-marketing/program-support/ED-G-00213%20MPG%20Growth%20Brochure.pdf).

Reference dimensions below are starting presets, not measurements of the photographed plate. Plate perimeter dimensions differ even where the device opening is compatible. [Leviton's wallplate size guide](https://leviton.com/content/dam/leviton/commercial-industrial/product_documents/solution_sheets/Wallplate%20Size%20Guide%20Q-1289.pdf).

| Plate | One gang, width × height | Two gang, width × height |
| --- | --- | --- |
| Standard | 69.85 × 114.3 mm | about 115.9 × 114.3 mm |
| Midway | about 79.4 × 123.8 mm | about 125.4 × 123.8 mm |
| Oversize | 88.9 × 133.4 mm | about 134.9 × 133.4 mm |

The guide adds about 46 mm width per additional gang. Curvature, thickness, screw heads, and manufacturers' tolerances still matter. The photo has perspective distortion and no scale; it cannot establish a snug fit.

Measure with the existing plate installed:

1. Overall width and height; maximum projection from the wall; corner radius and edge bevel.
2. Each moving paddle's width, height, center location, and top/bottom projection in both positions.
3. Gap between two paddle centers; the mounting cannot assume the paddle is centered perfectly in its opening.
4. Travel at the contact points and approximate force at those points (a small push-force gauge is useful).
5. Your actual MG90S body, ear spacing, shaft height, stock horn holes, and retaining screw.
6. The purchased battery holder and regulator board, including plugs and cable bend space.

Print the fit frame before the complete chassis. The generated models are an adjustable prototype. Do not infer a fit approval from an STL file existing.

## Mechanism

Use one servo for each paddle to control both office lights independently. Use the supplied servo horn and its original shaft screw; fasten the printed arm to the horn's holes. Do not print a guessed spline or substitute a screw that bottoms in the output shaft. A horn needs a positive torque connection; its center screw alone should not transmit all the torque through smooth plastic.

A servo shaft parallel to the wall lets a double-ended arm rock toward the upper or lower end of the switch. Soft contact pads take up small alignment differences. The arm briefly presses, returns to a position with both tips clear, then loses electrical power. Manual operation must remain possible at rest. Start with the servo unmounted and the arm removed, center it, then assemble and calibrate in small increments. Never run an assumed full 180° sweep against the switch.

For fixed shaft torque, a longer servo arm gives **less contact force**: `F = torque / radius`. It increases reach and displacement per degree. Pressing farther from the light switch's own pivot can reduce the force needed to click that switch. These are two different levers. As an ideal illustration, 1.8 kgf·cm is about 0.176 N·m; a 30 mm horn radius would produce about 5.9 N at stall. Real useful force must be lower, with margin; stall torque is not a continuous operating point.

The equal-and-opposite pressing force pulls the housing outward. At offset `d` from its support, adhesive also experiences a peeling moment `F × d`. A longer horn does not cancel that load. Use a broad stiff frame, supports close to both contact points, shallow projection from the wall, compliant tips, and the minimum travel that clicks the switch. Adhesive pull ratings cannot be treated as cyclic peel ratings. Repeated pressing, wall texture, paint adhesion, temperature, and battery weight all need a real test. Keep adhesive removal tabs accessible and never glue the moving paddle. A sleeve around a plate locates the device but does not, by itself, resist pulling off the wall.

All installation and testing in this project remains outside the intact wallplate: no wiring, mains access, longer wallplate screws, or modifications to the electrical switch. Stop testing if the frame lifts, the switch does not click freely, or the servo buzzes after pressing. A software duration limit is useful but is not independent current sensing or a mechanical overload clutch.

## Board and servo identification

Pico/Pico H lack wireless hardware. Pico W/Pico WH include Wi-Fi; headers do not change this. The existing non-wireless Pico can run the servo bench code over USB. For this project's Mac mini gateway and phone UI, the node needs a **Pico W/WH or Pico 2 W** with its matching MicroPython firmware and a 2.4 GHz Wi-Fi network. The user has a wireless board; verify the exact model before flashing. A Pico is a microcontroller, not a Linux Raspberry Pi. [Raspberry Pi board variants](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html).

TowerPro lists an MG90S body of 22.8 × 12.2 × 28.5 mm, 1.8 kgf·cm stall torque at 4.8 V, and 4.8 V operating voltage. Its own page contains mixed voltage references and warns about lookalike products. It does **not** provide a stall-current specification there. The “MG90S” name on an Amazon listing does not establish exact dimensions, shaft/horn geometry, safe pulse endpoints, or current consumption. Confirm the supplied servo's rated supply range before using the proposed regulated 5 V rail; do not interpret the page's 6.6 V torque entry as blanket permission to use that voltage. [Original TowerPro MG90S page](https://towerpro.com.tw/product/mg90s-3/).

Start with a supply path designed for roughly **2 A available to one moving servo plus logic**, and measure the actual loaded peaks. This is a design allowance, not a sourced MG90S current rating. Serialize commands on the double unit; two simultaneous stall/start currents require a larger verified power path. Larger servos and lookalikes may require more. [Power wiring and test sequence](power.md).

## Selected parts for revision 2

The first version used placeholder component envelopes and an unspecified servo load-switch carrier. The current headerless revision selects actual purchasable parts so the enclosure can be designed around their mounting and connection requirements:

| Function | Selected component |
| --- | --- |
| Removable batteries and contacts | Pololu 1153 four-AA holder with its supplied red/black leads |
| Cells | Four matched Panasonic eneloop AA NiMH cells; external NiMH charger |
| Regulated 5 V | Pololu 2574 / S18V20F5 |
| Master and servo switches | Two Pololu 2810 **LV slide-switch** modules; different control wiring for each |
| Direct Pico mounting | Headerless Pico W, four M2 × 6 nylon screws and soldered edge-pad wires; no PiCowBell |
| Passive components and soldered junctions | Adafruit 1608 quarter-size Perma-Proto |
| Battery disconnect | Mating Pololu 2180 + 2181 JST RCY prewired pigtails |
| Protection and wiring | Selected fuse/holder, diodes, capacitor, resistors, servo mating leads and power wire in the shopping list |

The root [BOM](../BOM.md), [BOM CSV](../hardware/bom.csv) and [shopping list](shopping-list.md) give manufacturer/order identifiers, source links and quantities. The [wiring guide](wiring.md) maps those parts to the existing GP15/16/17/26 firmware pins, including connector polarity and actual physical Pico pin numbers. The 2810 is an assembled high-side module; it replaces the earlier generic TPS22918 suggestion.

The [component-source register](component-sources.md) separates manufacturer dimensions, conservative fit allowances and unresolved measurements. A part number freezes the intended purchased part; it does not eliminate manufacturer tolerances, solder protrusion or variation in third-party MG90S servos. The revised CAD checks nominal component placement and clearance. The small fit coupons and a bench assembly still verify the actual printed and purchased parts.
