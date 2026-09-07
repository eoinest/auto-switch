# Independent battery-retention review

Status: **PASS for the nominal mechanical geometry and stated screw range.** Independent checks use the final saved assembly, after correcting the right-shoe transform. Physical dry fit remains required.

## Why the old bars could not clamp

The v4 cradle measures 70.1 × 65.6 mm internally, against a nominal 68.7 × 64.2 mm holder: **1.4 mm of total clearance in both X and Y**. The four posts stop at Z26, and the old bars rest directly on them. The seller's dimension image distinguishes **19 mm case thickness** from **22.5 mm including the projecting switch**. With the case resting on the 3 mm carrier, its flat face is at Z22. The old bars therefore leave approximately **4 mm above that face**, regardless of further screw tightening.

A replacement must control X/Y independently of vertical clamping. The side shims address X/Y clearance; central pressure shoes address Z. No snug-fit guarantee follows from the nominal dimensions or seller images.

## Holder orientation and access

The seller's broad-face dimensions are 64.2 mm wide × 68.7 mm high. It must rotate 90° into the existing 68.7 mm X × 64.2 mm Y cradle. For the selected orientation, the slider center is estimated near X+28.8, Y−53.4 mm, and its opening is approximately 4.1 mm along X × 9 mm along Y. Short central contacts at Y−32 avoid the original crossbar's switch obstruction. A 5 mm allowance around the opening defines a reasonable nominal front-access envelope, not a guarantee for every finger size.

The seller photographs show the cable leaving the opposite upper corner. In the chosen orientation this is near X+34.35, Y−5…0 mm. The old centered negative-Y notch is on the wrong edge for that orientation. Keep the corner clear and route the insulated leads over the low cradle wall without pinching. The exact cable-exit height and bend radius are not dimensioned; a drawn wire route is illustrative. The cradle wall rises 8 mm above the carrier surface.

## Existing mount compatibility

The four existing post centers are X±43, Y−52/−12 mm, with 10 × 12 mm footprints. Their tops are Z26. A 3 mm rail mounting seat preserves the existing M3 × 35 screw stack: under-head Z29, nominal tip Z−6, with existing nuts below the carrier. Two bolts per rail restrain rotation; a single slotted clip would rely much more heavily on friction.

For battery service, remove both rails to lift the holder out. Loosening the adjustment screws alone leaves the arms overhanging the case. Opening a cover in place is not established by the seller photographs. The existing carrier and wall bracket are reused unchanged.

## Adjustment screw and shoe interface

The ordinary M3 nut is 5.5 mm across flats and 2.4 mm thick. Its bottom-loaded pocket is 5.95 mm across flats, with 2.6 mm recess depth. Under adjustment load the nut bears upward at Z29 against a **2 mm fixed roof**. A top-open nut pocket would not provide this reaction surface; the draft was corrected before release. Insert the nut from below and engage the screw before installing the rail.

Each M3×10 screw pushes into a blind 3.6 mm diameter cup in its shoe. The cup is 0.8 mm deep and leaves **1.2 mm of plastic between the screw tip and the case**. For case thicknesses 18.5–20.5 mm, screw tips lie at Z22.7–24.7 and under-head faces at Z32.7–34.7. This leaves 1.9–3.9 mm of tip projection below the nut, full engagement through the 2.4 mm nut, and at least 1.7 mm clearance above the fixed rail. No washers are included in this stack.

The guide opening is 8.8 mm around an 8 mm arm: **0.4 mm nominal clearance on each side**. Retaining lips overlap the arm by 0.7 mm each. The 6.6 mm central opening leaves 0.55 mm per side around the modeled 5.5 mm screw head. These are print allowances, not tested tolerances. The shoe slides axially onto the arm for assembly; its screw must stay seated in the blind cup during use to prevent axial escape. Hold the shoe when withdrawing the screw or removing a rail.

## Access and printing limits

The modeled 18 × 22 mm finger-access envelope clears the new rails and shoes, but its outer edge is only approximately 0.2 mm from the existing post/rail boundary. The switch itself is unobstructed; physical finger access still needs a dry fit. The new right rail stops at Y−6, leaving 1.5 mm to the modeled cable corridor. The cable route is an estimate, not a verified molded exit or bend radius.

The corrected shim grips begin at assembled Z11.2, clearing the cradle wall top at Z11 by 0.2 mm. Choose shims according to the delivered holder and actual print; do not force a nominal 0.6 + 0.8 mm combination into a tighter gap.

Rails print front-face down, so the bottom-loaded nut pockets open upward. Mounting-head counterbores narrow from Ø6.4 to Ø3.4 after 2 mm height, producing short approximately 1.5 mm radial shoulder bridges. Shoes print on their C-shaped ends; inspect those shoulders and the small blind-cup bridge in the slicer. Shims print flat at 0.4/0.6/0.8 mm thickness. Use 0.2 mm layers and identify the unlabeled shim sizes from the preserved layout before lifting them. Parent-agent binary STL checks separately verify closed solids, bed placement, spacing and master/individual consistency.

## Review findings corrected

- Changed the draft top-open adjustment-nut recess to a bottom-loaded pocket with a fixed reaction roof.
- Enlarged the shoe head opening from 5.6 to 6.6 mm for useful clearance around an ordinary M3 socket head.
- Raised shim grips clear of the existing cradle wall; the earlier position intersected it by 0.2 mm.
- Identified a right-shoe transform reset during height checks. Both shoes now have their transforms baked before travel checks, assembly saving and exports. The final saved assembly places each shoe under its adjustment screw; the earlier reset moved the right shoe to the origin and invalidated its placement checks.

No physical fit, clamp-force, fatigue or creep test has been performed. Tighten only until play stops; these printed shoes are not torque-rated clamps.

## Final saved-mesh audit

[review_mechanics_independent.py](review_mechanics_independent.py) loads the final saved assembly and writes [independent-mechanical-review.json](generated/independent-mechanical-review.json). It does not save changes to the CAD file.

- **46 exact Boolean intersection checks returned zero volume**, covering rails against the original carrier and access envelopes, adjustment nuts, mounting-shaft clearance through the reused posts and rails, and both shoes/adjustment screws at 18.5, 19 and 20.5 mm case heights.
- Four illustrative 0.6 mm shims clear the original carrier within numerical tolerance; maximum computed intersection was **0.0000058 mm³**. Their grip bottoms are 0.2 mm above the cradle walls.
- Ray sections through the saved meshes confirm **2 mm adjustment-nut roofs, 3 mm mounting-bearing stacks and 1.2 mm shoe cup floors** on both sides.
- Both adjustment screws retain full nut engagement and the stated head clearance throughout the reviewed range. The generator separately checks nine shoe positions at 0.25 mm case-height increments.

Deliberately coincident bearing surfaces are separated by 0.001 mm during the Boolean checks to avoid coplanar numerical artifacts. The geometric audit is not a structural load or print-fit test.
