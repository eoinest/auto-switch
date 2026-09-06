# S2 electronics carrier component audit

Checked 2026-09-05 against the selected component identities and the existing `hardware/cad/s2-aa-poc` parameters. This is a source and interface audit, not physical-fit approval. No measurements of the user's delivered components were supplied in this audit.

## Current BOM and dimensional evidence

| Component | Evidence | CAD consequence |
| --- | --- | --- |
| Headerless ESP32-S2 Mini | User confirmed no headers. [WEMOS](https://www.wemos.cc/en/latest/s2/s2_mini.html) publishes 34.3 × 25.4 mm for LOLIN S2 Mini V1.0.0 and links its [dimension drawing](https://www.wemos.cc/en/latest/_static/files/dim_s2_mini_v1.0.0.pdf). | The nominal outline is sourced. Clone identity, PCB thickness, component underside, actual USB cable and soldered-wire geometry are not established by those two outline dimensions. Do not reserve sockets or header stacks. |
| DAIERTEK switched four-AA holder, B09N1GDWQ9 | The exact [seller listing](https://www.amazon.com/dp/B09N1GDWQ9), selected 4AA variant, states 68.7 × 64.2 × 22.5 mm and approximately 150 mm leads. It describes the switch on the back and a screw-secured cover. These dimensions appear both in the feature bullets and brand product description. | Seller nominal body size supports the existing cradle outline, with fit allowance. It does not establish tolerances, which face must remain accessible, switch projection, lead exit, cover screw access or removal travel. A cosmetic top-mounted switch is not evidence of real accessibility. |
| Four AA cells | Existing selected four-AA case contains the cells. | Carrier should fit the loaded, closed case; individual AA diameter does not establish the loaded case envelope or lid clearance. |
| Teyleten Robot buck-boost, B0GCW44FDL | The exact [seller listing](https://www.amazon.com/dp/B0GCW44FDL) identifies TPS63070; earlier project inspection records XL63070 on its PCB image. Current listing description and specification table provide no usable mechanical dimension drawing. | The 40 × 36 × 18 mm bay is a design allowance, not this module's dimensions. No exact board model, hole positions or support locations can be justified from the listing. A chip datasheet cannot establish the seller's complete PCB geometry. |
| Wiring and retention | Direct solder wires, ties/straps and converter insulation are required by the mechanical design. Exact products and as-built dimensions are not supplied. | Include routing, service loops, underside joints and a means of retaining the boards without pressing on components. These items need a real fit check; empty volume alone is insufficient. |
| Breadboard | User-owned board remains unidentified. Existing design explicitly keeps it on the bench. | Do not describe this carrier as holding the breadboard. |

No replacement battery holder or converter was selected during this audit.

## Findings in the pre-audit carrier

1. The converter supports are 3 mm wide at ±20 mm from its bay center, leaving a **37 mm inner gap**. A smaller board can fit within the reserved volume yet fall between these supports. The support/retention interface needs redesign or a separately sized insulating insert. A larger empty bay alone does not prove fit.
2. The current model places a cosmetic switch on the battery case top. The seller describes a back switch. Model orientation and access must follow the delivered holder rather than that cosmetic reference. Make battery replacement and switch operation possible without straining soldered wires.
3. S2 supports sit under PCB corners, but nominal board outline alone does not prove those corners are free of underside pads or solder. The actual headerless board and soldered harness must be checked against the supports and retention path.
4. Mechanical consumables are part of the assembly: battery retention straps, board/converter ties and insulation/strain relief. They need dimensions in the assembly record before a retention claim is made.
5. The `s2-aa-poc.md` bench BOM still describes header jumpers. The enclosure BOM must state direct solder connections for this user's headerless S2. The bench diagram's wiring remains an electrical reference, not an as-built enclosure harness.

These findings describe the generator before this review's changes. A subsequent model revision can resolve them, but that resolution must be checked against the actual generated geometry.

## Minimum physical evidence for final fit

- **Converter:** PCB length × width, total height including underside joints, component-side and underside views, solder-pad positions and intended wire exits. If no mounting holes exist, verify the actual edges/underside that may touch its insulating support and tie path.
- **AA holder:** loaded and closed length × width × height, switch face and projection, cover fastener and opening direction, lead exit with bend space. A fit coupon verifies outline only.
- **Headerless S2:** compare PCB outline with the official reference; confirm USB plug body/insertion path, underside joints and three-wire service loop clear the supports. Keep the antenna end exposed and avoid trapping the wires under retention.
- **Consumables:** actual tie/strap width and thickness, insulating support thickness, wire outside diameter and solder-joint height.
- **Print:** print the small fit checks in the intended material, nozzle/profile and orientation. Check insertion, retention, cable routing, battery replacement and USB access before printing the complete carrier.

Final fit is demonstrated by a dry assembly of the delivered parts; manifold STL validation and nominal manufacturer outlines establish different properties.
