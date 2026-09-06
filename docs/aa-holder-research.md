# AA holder candidates for a future auto-switch revision

Researched 2026-09-05. Scope: one Pico W and one MG90S. These are candidates, not a replacement wiring plan or an assertion that existing STLs fit. No purchases were made. Prices exclude cells, charger, shipping and tax.

## Recommendation

For Amazon purchasing, shortlist the **DAIERTEK B09N1GDWQ9 4-AA switched holder** below. For easiest breadboard connection, **Adafruit #830** is better documented and already has male header tips. For a thinner printed enclosure, **Pololu #1153** saves thickness by leaving battery retention to our chassis.

Use four rechargeable NiMH AA cells with a suitably rated **5 V buck-boost regulator** if we want a stable shared supply. A battery holder alone does not regulate its output. The existing LM2596 is a buck converter and cannot raise a four-cell NiMH pack's nominal 4.8 V to 5 V. Six AAs offer an alternative if reusing that converter matters more than enclosure size.

## Four concrete options

| Candidate and purchase/source link | Published body size | Connections and switch | Observed price | Mounting implications |
| --- | --- | --- | --- | --- |
| [DAIERTEK B09N1GDWQ9, 4 AA, three-pack — Amazon US](https://www.amazon.com/dp/B09N1GDWQ9) | 68.7 × 64.2 × 22.5 mm | Built-in on/off switch, cover, approximately 150 mm tinned wire leads; conductor gauge not established | $8.39 one-time price / three holders (~$2.80 each); page also showed $7.97 with a 5% discount, not used as the baseline | Plan a removable printed cradle. No verified mounting-hole coordinates or tolerance drawing found. Keep the lid and switch accessible. |
| [Adafruit #830, 4 AA with switch](https://www.adafruit.com/product/830) | Product page gives 2.5 × 2.75 × 0.75 inches, ±0.1 inch; converted approximately 63.5 × 69.9 × 19.1 mm, ±2.5 mm | Cover, switch, 152 mm leads with individual 0.1-inch male header tips | $2.95 each, listed in stock | Good breadboard candidate. Use a cradle until the delivered unit is measured; linked drawing and coarse product dimensions differ. |
| [Pololu #1153, open 4 AA holder](https://www.pololu.com/product/1153) | 58 × 63 × 16 mm | Two 152 mm, 24 AWG stripped leads; no built-in switch or cover | $2.99 each | Smallest flat candidate here. Our enclosure must retain cells. Hole pattern not dimensioned in the product specifications; use a cradle or measure before placing screw bosses. Existing rocker can serve as the master switch. |
| [Pololu #1771, enclosed 6 AA with switch](https://www.pololu.com/product/1771) | 72 × 96 × 19 mm | Sliding cover, switch; two 152 mm, 24 AWG stripped leads | $5.69 each; confirm stock at checkout | Larger footprint and two more cells, but better voltage headroom for the existing buck converter. Needs its own cradle and battery-access clearance. |

The Amazon US page was checked for the exact ASIN, title, selected **4AA** variant, dimensions, and pricing. Its variation family also contains 18650 holders and mixed AA packs; those are different products. Amazon availability and offers can change. Brand-provided marketplace dimensions are weaker evidence than a tolerance drawing.

Adafruit's linked [EPD-200659 drawing](https://cdn-shop.adafruit.com/datasheets/EPD-200659.pdf) is for a lead-wire holder; the current #830 page describes a later header-tip revision. Do not freeze CAD from that drawing alone.

## What changes electrically

| Cells | Nominal pack voltage | Consequence for our 5 V circuit |
| --- | --- | --- |
| 4 × NiMH AA, 1.2 V each | 4.8 V | Voltage varies with charge and load. Use buck-boost to maintain 5 V; the LM2596 cannot boost. |
| 4 × alkaline AA, 1.5 V each | 6 V | Fresh cells can exceed nominal voltage; never treat this as a direct Pico VSYS supply. A buck can lose regulation as cells discharge; buck-boost covers both sides of 5 V. |
| 6 × NiMH AA | 7.2 V | A candidate for LM2596 reuse. Test the actual board at low battery voltage and servo load; its dropout means it may stop holding 5 V before the cells are exhausted. |
| 6 × alkaline AA | 9 V | More buck input headroom, but still requires regulation and load testing. |

These consequences follow from the [LM2596 step-down design and dropout characteristics](https://www.ti.com/lit/ds/symlink/lm2596.pdf), [Pico W power-input requirements](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf), and the holder suppliers' stated series arrangement and nominal chemistry voltages. Do not interpret a nominal NiMH voltage as its maximum immediately after charging. This recommendation does not depend on wiring a raw pack directly into VSYS.

The previously considered [Pololu S18V20F5](https://www.pololu.com/product/2574) is an example of a 5 V buck-boost, listed at $29.95. Its current capability depends on input voltage and cooling; the product's approximately 2 A figure is not a universal guarantee. It is a reference option, not an additional purchase selected by this holder research.

## Wire connection and servo current

- Adafruit #830's header tips can insert into a breadboard, but fit does not establish current capacity. Raw battery leads belong at the regulator input, not the regulated 5 V rail.
- For the other holders, solder each flexible lead to a short **22 AWG solid-core pigtail**, separately heat-shrink each splice, and provide strain relief. Only the clean solid end enters the breadboard. Alternatively use a terminal-to-header breakout with published wire and current ratings. [Adafruit's breadboard guidance](https://learn.adafruit.com/breadboards-for-beginners?view=all) recommends 22 AWG solid wire.
- A detachable RCY/JST or similar connector is optional. Choose an actual rated matching pair, verify polarity, and do not infer compatibility from red plastic or the word “JST.” No exact connector pair has been selected here.
- None of the four checked holder listings provides a verified continuous/pulse current rating for the entire spring-contact, wire, and switch assembly. Do not assume a built-in miniature slide switch has the rating of the user's separate DaierTek rocker switch.
- Before approving one for the actuator, measure supply sag and heating during actual servo starts and switch presses, including at lower cell charge. The exact MG90S unit's current and the breadboard's contact limits remain unverified. For the mounted version, use secure wired/soldered power distribution instead of relying on breadboard contacts.

## Before making the final enclosure

Measure the delivered holder with the selected cells installed: overall size, lid removal direction and travel, switch location/travel, wire exit and bend space, and any real mounting holes. Print a small fit coupon/cradle first. No holder in this note has been checked against an STL, and no hole coordinates or final fit clearance have been invented.
