# Recessed stock-horn locating seat — provisional

This revision adds a shallow shaped seat so the supplied servo horn can locate against the paddle before its screws are installed. The printed rim guides alignment; **the screws still retain the horn**. Nothing replaces the supplied spline or center screw.

The supplied photo identifies a **straight, tapered double-ended horn with rounded tips**. Its outline is now photo-estimated as **31.5 mm overall span, 5.3 mm arm root width, 4.0 mm tip width and 7.4 mm hub diameter**. The printed frame underneath provides the approximate scale. Perspective and horn height make this an estimate, not a precision measurement: independent estimates span approximately 31–32 mm, with about ±1 mm overall uncertainty. Arm thickness **2 mm** and hub depth **4 mm** remain unmeasured assumptions. See [source notes](sources.md).

## What is ready

- [Blender close-up](generated/horn-seat-closeup-PROVISIONAL.blend) and [render](generated/horn-seat-closeup.png): empty seat, seated horn, and lifted horn.
- [Paddle-family Blender preview](generated/paddle-family-pocket-PREVIEW.blend) and [render](generated/paddle-family-pocket.png): the interface in the normal, mirrored and raised-center paddles. **Preview only; no production paddle STLs exported.**
- [All three fit coupons STL](generated/horn-fit-coupons-ALL-THREE-PHOTO-ESTIMATE.stl): three small flange-only samples using **97%, 100% and 103% profile sizes**, each with **0.3 mm clearance per side**. Their underlying horn spans are 30.555, 31.5 and 32.445 mm.
- Three corresponding individual coupon STLs and `horn-fit-coupons-print-layout.png` identify their order. Labels are display-only, not embossed on the prints. The supplied layout runs 97%, 100%, 103% along increasing X. Mark them before removing them from the bed. Import the complete file at 100% scale; the three profile sizes are already built into it.

Print the coupon cavity facing up, flat floor on the bed. These coupons only test the assumed horn interface; they do not attach to the wall or actuate a switch. Try the actual horn in each coupon without forcing it. Choose a pocket that seats flat with minimal play, then report its label and whether the screw holes line up. None may fit if the photo or unmeasured underside geometry differs substantially; adjust the model from that result before printing a full paddle.

## Geometry

The existing horn/paddle contact plane remains **X = 13 mm**. Adding a **1.2 mm-high rim** toward the servo creates the recess without moving the horn along its shaft. The original **4 mm flange floor** remains intact. At the nominal 100% profile and default 0.3 mm clearance, the pocket is a **32.1 mm overall tapered/rounded arm outline and 8.0 mm hub circle**, surrounded by **1.2 mm walls**. The flange is widened to **36 mm**, supporting even the largest coupon's 35.445 mm outer rim span. A single closed polygon merges the tapered arms, round tips and hub; no rectangular substitute is used.

The assumed 2 mm-thick arm would remain 0.8 mm proud of the rim; actual arm thickness still needs checking. A **4.8 mm center opening** preserves tool access, and the two original adjustable attachment slots remain centered at Y = ±7 mm. Their overall length is 6.2 mm: 4 mm straight section plus 2.2 mm diameter round ends. Actual horn fastener diameter remains unconfirmed.

The full-paddle preview includes a 45-degree transition from X−3/Y±6 to X9/Y±18, supporting the widened flange from the existing paddle beam. Before a production export, we still need to verify the actual horn outline, seating face, screw fit, tool clearance and complete mechanism travel with the new rim.

## Checks

The generator requires all coupon and preview paddle meshes to be watertight, one connected component and positive volume. Coupon orientation is floor-down, cavity-up. Geometry checks do not establish a physical fit. `validation.json` records dimensions, source hash and remaining assumptions.

The [independent interface review](independent-review.md) verifies the nominal seated horn, floor depth and screw paths. `python3 hardware/cad/horn-pocket/verify_stl_independent.py` independently checks the exported coupon meshes, master equivalence, spacing and bed placement.

Existing single-switch and double/triple production files were not changed.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/horn-pocket/generate.py
```
