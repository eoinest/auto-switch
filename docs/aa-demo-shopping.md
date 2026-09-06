# AA demo: shopping list and bench hardware

**Current POC:** [Switched AA holder + breadboard rails, one servo](poc-wiring.md). The WAGO assembly below is an earlier reference; use the POC parts checklist for this build.

Checked **2026-09-05**. This list implements the [four-AA demo plan](aa-demo-plan.md): four matched NiMH cells, a fixed 5 V regulator, one physical master switch, a continuously powered servo, and no servo power gate or battery ADC circuit. The current build uses **one servo only**.

**Use the existing headered Pico and one MG90S servo.** This is a bench BOM. The old enclosure/STL fit report does not certify these new junction blocks, breadboard, connector routing, or assembly. Do not buy the old enclosure fasteners for this bench build.

**[Itemized price calculation](aa-demo-cost.md): about $160 before tax and shipping**, with a $147.79–181.79 planning range including new wire sets and retail packs. Missing Amazon prices are labeled allowances. Reuse and multimeter scenarios are included.

Source inspection records: [aa-demo-source-checks.md](aa-demo-source-checks.md).

Machine-readable quantities and purchasing notes: [aa-demo-bom.csv](../hardware/aa-demo-bom.csv). Quantities are installed parts, not packages: one battery kit already includes four cells and the charger. Nothing has been purchased.

## Amazon-first shopping

The direct Amazon pages below were opened and their product titles/variants checked. That establishes listing identity, not seller authenticity, live checkout stock, price, or a tested delivered sample. Amazon may change the selected variant. **No Amazon prices are quoted because a reliable current checkout price was not established.**

| Item | Installed: one servo | What to order | Why this selection |
| --- | --- | --- | --- |
| [Panasonic eneloop kit — B00JHKSMJU](https://www.amazon.com/dp/B00JHKSMJU) | 4 cells; 1 shared charger | **One** K-KJ17MCA4BA kit | Four AA NiMH cells and individual-cell charger. [Panasonic kit specification](https://www.panasonic.com/ca/consumer/batteries/rechargeable/eneloop/kkj17mca4ba.html). Remove cells from holder to charge. |
| [ELEGOO 830-point breadboards — B01EV6LJ7G](https://www.amazon.com/dp/B01EV6LJ7G) | 1 board | One three-pack; two spares | Manufacturer links to this ASIN. The terminal area has 630 holes, corresponding to 63 rows of ten, plus unused side rails. [Manufacturer](https://us.elegoo.com/products/elegoo-3pcs-breadboard-830-point-solderless-prototype-pcb-board-kit). |
| [WAGO 221-415 connectors — B06XH47DC2](https://www.amazon.com/dp/B06XH47DC2) | 3 blocks | One ten-pack; use three | One 5 V junction and two linked ground junctions. Buy genuine 221-415, not a visually similar unbranded block. [Manufacturer](https://www.wago.com/us/wire-splicing-connectors/compact-splicing-connector/p/221-415). |
| [TUOFENG 22 AWG solid copper wire — B07TX6BX47](https://www.amazon.com/dp/B07TX6BX47) | 1 m total allowance | One six-color set, or reuse equivalent | Solid wire makes breadboard jumpers and the leads connecting breadboard to WAGO blocks. Listing says solid tinned copper, six colors × 30 ft. |
| [BNTECHGO 22 AWG stranded copper wire — B01M0O1NXM](https://www.amazon.com/dp/B01M0O1NXM) | 2 m total allowance | One set, or reuse equivalent | Flexible power harness; ten colors × 10 ft. Use red for positive, black for ground. [Manufacturer](https://bntechgo.com/bntechgo-22-gauge-silicone-wire-kit-ultra-flexible-10-colors-each-10-ft-high-temp-200-c-600v-22-awg-silicone-wire-60-strands-of-tinned-copper-wire-stranded-wire-for-model-battery/). |
| [CHANZON 1N5819 diode — B079KG1TN2](https://www.amazon.com/dp/B079KG1TN2) | 1 diode | Listing is 100 pieces; a smaller traceable pack is sufficient | Amazon alternative advertised as DO-41, 1 A, 40 V Schottky. Its exact manufacturer/lead geometry has not been independently verified; see reference-grade fallback below. |

Have at least **1 m total solid wire and 2 m total stranded wire** available for this bench build, including at least 1 m red and 1 m black stranded wire. These generous cutting allowances replace the earlier 0.5 m/1 m estimates; supplied holder/RCY/servo-extension leads are additional. The selected sets exceed these quantities. Keep power leads short after a physical dry fit; the large drawing is not a cable-length template.

The solid-wire set can make all breadboard jumpers; a separate Dupont kit is not required. Optional [Adafruit 1957 male/male jumpers](https://www.adafruit.com/product/1957) are convenient for board-only logic connections. Keep the selected 22 AWG solid leads for WAGO connections. ELEGOO's separate 120-piece Dupont kit specifies copper-clad aluminum, so it is not the selected soldered harness material. [ELEGOO jumper material](https://us.elegoo.com/products/elegoo-multicolored-dupont-wire-kit).

## Specialty parts to order by exact model

I could not verify reliable exact Amazon listings for these selections. These manufacturer/distributor links avoid substituting an adjustable or step-up-only regulator, wrong connector family, or unknown fuse.

| Part | Installed quantity | Order | Connection or important detail |
| --- | --- | --- | --- |
| [Pololu 1153 four-AA holder](https://www.pololu.com/product/1153) | 1 | 1 | Includes 6-inch 24 AWG leads. Bare holder is 58 × 63 × 16 mm; loaded height and access still need measurement. |
| [Pololu 2574 S18V20F5](https://www.pololu.com/product/2574) | 1 | 1 | Fixed regulated 5 V, step-up and step-down. Direct-solder to VIN, GND, VOUT; ENABLE unused. Current capability varies with battery voltage and heat. |
| [Pololu 2810 LV master switch](https://www.pololu.com/product/2810) | 1 | **1, not 2** | Purchased slider-operated board. Use VIN, VOUT, GND; leave ON/control pads unused. No GPIO wire. |
| [Pololu 2180 female RCY pigtail](https://www.pololu.com/product/2180) + [2181 male RCY pigtail](https://www.pololu.com/product/2181) | 1 pair | One of each | Keyed battery disconnect, 100 mm leads. Recessed contacts on fused battery side. Verify actual continuity/polarity before connecting. |
| [Pololu 2169 servo extension](https://www.pololu.com/product/2169) | 1 | 1 | 300 mm, 22 AWG. Cut the extension, preserving the male-contact end that mates with the servo socket. Original servo cable stays intact. |
| [Littelfuse 01500274Z fuse holder](https://www.digikey.com/en/products/detail/littelfuse-inc/01500274Z/29453) | 1 | 1 | Enclosed inline holder with leads, fits 5 × 20 mm. Wire it close to battery positive. |
| [SCHURTER 0001.2507 fuse](https://www.digikey.com/en/products/detail/schurter-inc/0001-2507/639706) | 1 | 3: one fitted, two spares | 2 A time-lag, 5 × 20 mm, specified DC rating. [Manufacturer SPT table](https://www.schurter.com/en/datasheet/SPT_5x20). Still requires coordination against measured pack-current pulses and wiring. |
| [Panasonic EEU-FR1A471 capacitor](https://www.digikey.com/en/products/detail/panasonic-electronic-components/EEU-FR1A471/9921021) | 1 | 2: one fitted, one spare | C1, 470 µF, 10 V, polarized radial. Nominal Ø8 × 11.5 mm body, 3.5 mm lead pitch. [Manufacturer](https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1A471). |
| [Yageo MFR-25FBF52-1K resistor](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-1K/13011) | 1 | 10 shared spares | 1 kΩ, 1%, ¼ W axial, one per signal. [Manufacturer MFR series](https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf). |

For a diode with a traceable manufacturer specification, select **Vishay 1N5819-E3/73** from an authorized distributor; [DigiKey exact-part search](https://www.digikey.com/en/products?keywords=1N5819-E3%2F73) is a search link, not a verified stock listing. Its [Vishay datasheet](https://www.vishay.com/docs/88525/1n5817.pdf) specifies a 1 A, 40 V DO-41 part and identifies the band as cathode. This datasheet does **not** certify the CHANZON alternative. The Vishay lead diameter can be 0.71–0.86 mm: if it does not insert gently into the breadboard, solder short 22 AWG solid-wire adapters and insulate the joints rather than forcing it.

## How the three junction blocks are used

Label the blocks **P5V**, **GND_A**, and **GND_B**. Every hole in one 221-415 is electrically common; these are not five separate circuits. Number the holes left-to-right as drawn. One wire per hole, no doubled-up conductors.

| Port | P5V: regulated positive | GND_A | GND_B |
| --- | --- | --- | --- |
| 1 | Regulator VOUT | Battery negative via RCY | Link from GND_A.4 |
| 2 | C1 positive | Master GND | Pico GND feed |
| 3 | D1 anode feed | Regulator GND | Servo 0 ground |
| 4 | Servo 0 positive | Link to GND_B.1 | Empty |
| 5 | Empty | C1 negative | Empty |

The selected WAGO accepts 24–12 AWG copper conductors; the manufacturer specifies an 11 mm strip length and an approximately 29.8 × 18.3 × 8.15 mm body. Leave space above its levers. Do not add solder to the ends clamped in the connector; factory tinned copper strands are different from a solder-coated bundle. Confirm full insertion and tug gently. [WAGO product](https://www.wago.com/us/wire-splicing-connectors/compact-splicing-connector/p/221-415), [WAGO CAD/specification record](https://wago-embedded.customer-domain.wago.com/3d-cad-models/221-485-splicing-connector-with-levers-for-all-conductor-types-max-4-mm-5-conductor-transparent-housing-surrounding-air-temperature-max-85-c-t85-wago?info=wago%2Fpg07%2Fserie221%2F0221-0415_0999-0962.prj).

Solder an individually insulated 22 AWG pigtail to each capacitor lead, then connect to its assigned WAGO port. For the cut servo extension, power and ground go directly to the blocks; join its signal conductor to a short solid-wire end for the breadboard. Route the **motor current outside the breadboard**. The holder, fuse, master and regulator remain separate on a nonconductive base with strain relief.

## Tools and consumables

Reuse the soldering kit, suitable wire, and USB cable first. Fill these gaps if needed:

- A digital multimeter with DC volts, resistance, continuity and diode mode; [Adafruit 850](https://www.adafruit.com/product/850) is a concrete reference. Do not connect a meter in current mode directly across batteries.
- Thin-wall heat-shrink in small and medium sizes for individual solder joints; [Adafruit 344 assortment](https://www.adafruit.com/product/344) is a concrete reference. Slip it onto the wire before soldering.
- A **data-capable** USB-C to Micro-B cable for the Mac and Pico; [Adafruit 3879](https://www.adafruit.com/product/3879) is a reference. A charge-only cable cannot upload firmware.
- Wire stripper/cutter covering 24, 22, 20 and 16 AWG, electronics solder/flux, a suitable heat source for shrink, small cable ties, and a nonconductive bench base. The fuse holder and RCY leads differ from the new 22 AWG hookup wire.

For these generic consumables only: [Amazon heat-shrink search](https://www.amazon.com/s?k=heat+shrink+tubing+2%3A1+1mm+2mm+3mm+assortment), [USB data-cable search](https://www.amazon.com/s?k=USB+C+to+Micro+B+data+cable), and [multimeter search](https://www.amazon.com/s?k=digital+multimeter+DC+voltage+continuity+diode). **These are unverified search results, not selected or checked product listings.** An older Wirefy ASIN tested during research redirected to a different ¼-inch roll, so it was intentionally not recommended as a small-wire assortment.

## What is and is not verified

The BOM matches the selected electrical topology and accounts for connectors, power junctions, wires and tools. Exact mechanical fitting, soldering, breadboard contacts, loaded servo current, transient supply behavior and runtime have not been tested on the user's hardware. The new WAGO assembly has not been modeled into the old STLs. Battery operation is a supervised demo without automatic low-pack cutoff: charge cells externally and switch off before depletion. The ungated [AA-demo configuration](../firmware/config.aa-demo.example.json) now exists: it selects `hardware_profile: "aa-demo"`, `power_enable_pin: null`, and disables the absent battery ADC. Follow the [firmware guide](firmware.md) to install it and calibrate the initially disabled channel. This profile has not yet been verified on the physical device.
