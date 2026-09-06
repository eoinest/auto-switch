# Recessed stock-horn locating seat — provisional

This revision adds a shallow shaped seat so the supplied servo horn can locate against the paddle before its screws are installed. The printed rim guides alignment; **the screws still retain the horn**. Nothing replaces the supplied spline or center screw.

The exact horn is not yet identified. The current **22 × 5 × 2 mm double-arm and 7 mm hub** are inherited project assumptions, not a dimensioned TowerPro horn drawing. Taper, spoke count, underside bosses and screw-hole sizes must be matched to the actual supplied horn before producing a working paddle. See [source notes](sources.md).

## What is ready

- [Blender close-up](generated/horn-seat-closeup-PROVISIONAL.blend) and [render](generated/horn-seat-closeup.png): empty seat, seated horn, and lifted horn.
- [Paddle-family Blender preview](generated/paddle-family-pocket-PREVIEW.blend) and [render](generated/paddle-family-pocket.png): the interface in the normal, mirrored and raised-center paddles. **Preview only; no production paddle STLs exported.**
- [All three fit coupons STL](generated/horn-fit-coupons-ALL-THREE-PROVISIONAL.stl): three small flange-only samples, with **0.2, 0.3 and 0.4 mm clearance per side**, laid out separately.
- Three corresponding individual coupon STLs and `horn-fit-coupons-print-layout.png` identify their order. Labels are display-only, not embossed on the prints. Keep the coupons in their layout order or label them after printing.

Print the coupon cavity facing up, flat floor on the bed. These coupons only test the assumed horn interface; they do not attach to the wall or actuate a switch. Identify the actual horn before deciding whether this provisional profile is worth printing.

## Geometry

The existing horn/paddle contact plane remains **X = 13 mm**. Adding a **1.2 mm-high rim** toward the servo creates the recess without moving the horn along its shaft. The original **4 mm flange floor** remains intact. At the default 0.3 mm clearance, the pocket is the union of a **22.6 × 5.6 mm arm outline and 7.6 mm hub circle**, surrounded by **1.2 mm walls**. The flange is widened to 26 mm to support the locating rim.

The 2 mm-thick nominal arm remains 0.8 mm proud of the rim. A **4.8 mm center opening** preserves tool access, and the two original adjustable attachment slots remain centered at Y = ±7 mm. Their overall length is 6.2 mm: 4 mm straight section plus 2.2 mm diameter round ends. Actual horn fastener diameter remains unconfirmed.

The full-paddle preview includes a 45-degree transition supporting the widened flange. Before a production export, we still need to verify the actual horn outline, seating face, screw fit, tool clearance and complete mechanism travel with the new rim.

## Checks

The generator requires all coupon and preview paddle meshes to be watertight, one connected component and positive volume. Coupon orientation is floor-down, cavity-up. Geometry checks do not establish a physical fit. `validation.json` records dimensions, source hash and remaining assumptions.

The [independent interface review](independent-review.md) verifies the nominal seated horn, floor depth and screw paths. `python3 hardware/cad/horn-pocket/verify_stl_independent.py` independently checks the exported coupon meshes, master equivalence, spacing and bed placement.

Existing single-switch and double/triple production files were not changed.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/horn-pocket/generate.py
```
