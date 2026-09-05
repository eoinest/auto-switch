# AA-demo source inspection record

Inspection date: **2026-09-05**. These checks support [shopping choices](aa-demo-shopping.md), not a claim that delivered parts or the assembled circuit have been tested. Direct links were opened using web retrieval. Manufacturer specifications take precedence over Amazon's sometimes inconsistent attribute tables. No accounts, carts, or purchases were changed. No prices are used in the shopping guide.

## Amazon listing identities

The following direct pages returned matching product-title text and ASIN evidence. Descriptions below are brief identification summaries, not copied listing descriptions. Stock, seller, selected variation and price must be checked again at checkout.

| Direct URL / ASIN | Identity observed | Limits of check |
| --- | --- | --- |
| [B00JHKSMJU](https://www.amazon.com/dp/B00JHKSMJU) | Panasonic K-KJ17MCA4BA charger kit including four AA eneloop rechargeable cells | Confirm AA kit variant. Not a separate four-kit purchase. [Panasonic corroboration](https://www.panasonic.com/ca/consumer/batteries/rechargeable/eneloop/kkj17mca4ba.html). |
| [B01EV6LJ7G](https://www.amazon.com/dp/B01EV6LJ7G) | ELEGOO three-pack, 830-point breadboards | This ASIN was reached from the manufacturer's Amazon button. [Manufacturer page](https://us.elegoo.com/products/elegoo-3pcs-breadboard-830-point-solderless-prototype-pcb-board-kit). Check physical row numbering before wiring. |
| [B06XH47DC2](https://www.amazon.com/dp/B06XH47DC2) | WAGO 221-415 five-conductor connectors, ten-pack | Listing identity is not authentication of an individual seller's stock. Amazon ancillary attributes were not used for dimensional design. |
| [B07TX6BX47](https://www.amazon.com/dp/B07TX6BX47) | TUOFENG 22 AWG solid tinned-copper wire, six colors, 30 ft each | Copper construction is a listing claim; no physical sample measured. |
| [B01M0O1NXM](https://www.amazon.com/dp/B01M0O1NXM) | BNTECHGO 22 AWG stranded tinned-copper silicone wire, ten colors, 10 ft each | Corroborated by the [manufacturer's matching kit](https://bntechgo.com/bntechgo-22-gauge-silicone-wire-kit-ultra-flexible-10-colors-each-10-ft-high-temp-200-c-600v-22-awg-silicone-wire-60-strands-of-tinned-copper-wire-stranded-wire-for-model-battery/). |
| [B079KG1TN2](https://www.amazon.com/dp/B079KG1TN2) | CHANZON 100-piece 1N5819, advertised DO-41, 1 A, 40 V | Conditional bench alternative. No independent CHANZON manufacturing/lead-diameter verification. A Vishay datasheet does not certify this brand. |

Rejected link example: opening `https://www.amazon.com/dp/B084GDLSCK` returned a different selected variant, B08W7RB32Z, a ¼-inch 50-foot roll. It was not retained as the proposed small-wire heat-shrink assortment. This is why an ASIN must be checked against the actual selected product.

## Rechecked specialty purchase links

Both requested DigiKey links were reopened after the shopping guide was drafted. The returned page's manufacturer part number and specification matched; neither returned a different component.

| URL | Matching data observed | Primary corroboration |
| --- | --- | --- |
| [DigiKey 9921021](https://www.digikey.com/en/products/detail/panasonic-electronic-components/EEU-FR1A471/9921021) | Panasonic **EEU-FR1A471**, distributor number P124219-ND; 470 µF, 10 V, polarized radial; Ø8 mm and 3.5 mm lead pitch | [Panasonic EEUFR1A471](https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1A471). Panasonic omits the hyphen in its URL/part rendering. |
| [DigiKey 13011](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-1K/13011) | Yageo **MFR-25FBF52-1K**, distributor number 1.00KXBK-ND; 1 kΩ, ±1%, ¼ W, axial metal film | [Yageo MFR family datasheet](https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf). |
| [DigiKey 29453](https://www.digikey.com/en/products/detail/littelfuse-inc/01500274Z/29453) | Littelfuse **01500274Z**, inline wire-lead holder; accepts 5 × 20 mm fuse | Manufacturer linked by distributor. The older standalone Littelfuse asset URL used in the legacy BOM now redirects to a missing page. |
| [DigiKey 639706](https://www.digikey.com/en/products/detail/schurter-inc/0001-2507/639706) | SCHURTER **0001.2507** | [Manufacturer SPT 5×20 table](https://www.schurter.com/en/datasheet/SPT_5x20), including DC ratings. |

## Manufacturer terminal and geometry references

These are the manufacturer's photo/diagram source pages, not screenshots or rehosted copies. The browsing text exposed their captions. Consult the labelled views to distinguish electrical pads from mounting holes and top from bottom. Physical board silkscreen must agree before soldering.

- [Pololu 2810 picture gallery](https://www.pololu.com/product/2810/pictures): includes a pinout diagram, bottom view with dimensions, supplied hardware, and schematic. The [product usage instructions](https://www.pololu.com/product/2810) establish slider-only operation from VIN/GND to VOUT; our ON/control pads are unused.
- [Pololu 2574 picture gallery](https://www.pololu.com/product/2574/pictures): includes the labelled top view, bottom dimensions, optional terminal blocks, and a direct-solder wiring/strain-relief example. The [product instructions](https://www.pololu.com/product/2574) identify VIN, GND, VOUT and ENABLE; ENABLE is left disconnected in this design.
- [Pololu 1153](https://www.pololu.com/product/1153): bare-holder envelope and supplied 24 AWG lead description. Loaded-cell height is not established by that bare-holder envelope.
- [Pololu 2169](https://www.pololu.com/product/2169), [2180](https://www.pololu.com/product/2180), and [2181](https://www.pololu.com/product/2181): specified servo extension and mating RCY pigtails. Actual connector wire color/polarity still gets a continuity check.
- [WAGO 221-415](https://www.wago.com/us/wire-splicing-connectors/compact-splicing-connector/p/221-415) and [manufacturer-hosted CAD/specification record](https://wago-embedded.customer-domain.wago.com/3d-cad-models/221-485-splicing-connector-with-levers-for-all-conductor-types-max-4-mm-5-conductor-transparent-housing-surrounding-air-temperature-max-85-c-t85-wago?info=wago%2Fpg07%2Fserie221%2F0221-0415_0999-0962.prj): exact 221-415 record, five connection points, 24–12 AWG, 11 mm stripping, 29.8 × 18.3 × 8.15 mm. The latter URL slug says 221-485 but its selected record explicitly identifies 221-415; use the selected item data, not the slug.
- [Vishay diode datasheet](https://www.vishay.com/docs/88525/1n5817.pdf): cathode band and actual DO-41 lead dimensions. Oversize leads must not be forced into a breadboard.

## Wire allowance audit

The two-servo placement list has four breadboard jumpers and four board/external logic leads. External power paths also include supplied holder, fuse-holder, RCY and servo-extension wires. The earlier 0.5 m solid / 1 m stranded allocations could be tight for a spread-out demonstration, so the guide and CSV now allow **1 m solid plus 2 m stranded**, including 1 m each red and black stranded, for either profile. This is a purchasing/cutting allowance, not a measured cable schedule. The selected multicolor sets exceed it comfortably. Place modules close together, leave service slack, then trim; drawing pixel distances are not physical lengths.
