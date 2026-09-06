# Independent wall-bracket review

Status: **mounting geometry checked; purchased-component fit and wall load capacity remain unverified.** The two main structural prints are the flat-bottom carrier and one connected H-shaped rear bracket. Five separate battery/converter retainers remain in the seven-piece master STL.

## Checks performed

Reviewed `generate.py`, the final saved `generated/electronics-retention-v4.blend`, and the rear-pad render independently of the design author. Exact Boolean intersections of the rear bracket against all 42 other assembled mesh objects—including screw/nut references, electronic envelopes, and printed retainers—are zero at the report precision. Results are in `generated/independent-bracket-intersections.json`.

The same report checks each wall-facing pad by clipping its coplanar mesh triangles to its full 20 × 144 mm rectangle. Both rectangles contain **2,880 mm² of continuous flat surface** at Z = −13 mm. The screw bores and nut-entry slots do not break through these adhesive surfaces.

An initial check found that the four nut references had their pointed corners facing the 6 mm slot walls. Each overlapped the bracket by approximately 0.256 mm³. The references were rotated 30° so their flats face those walls, matching the required insertion orientation; all four now clear. No change to the printed pocket dimensions was needed.

## Screw stack and access

Four **M3 × 12 mm screws and four ordinary M3 nuts** attach the carrier to the bracket at X = ±53 mm, Y = ±65 mm. No washers are included in this stack.

- The carrier is 3 mm thick. The bracket post contacts its underside at Z = 0, and the nut pocket roof is at Z = −4.6 mm. The screw therefore clamps the carrier and 4.6 mm of post roof before engaging the nut.
- The modeled nut is 5.5 mm across flats and 2.4 mm thick. The slot is 6 mm wide and 2.8 mm high: nominal allowances of 0.5 mm across flats and 0.4 mm vertically. Its inward opening admits the nut with its flats aligned to the slot walls; the width prevents a full rotation once inserted.
- Under-head screw length is measured from Z = 3 mm. A 12 mm screw ends at Z = −9 mm, approximately 2 mm beyond the seated nut and 0.5 mm above the blind-bore bottom. It remains 4 mm in front of the rear adhesive plane. Longer screws can bottom out; M3 × 10 is not the selected stack.
- Screw heads and straight screwdriver approaches from the front clear the existing battery posts, converter fixtures and S2 reference envelope.

Insert the four nuts from the inward-facing side openings before joining the carrier to the bracket. Install the electronics and their underside nuts while the carrier is still separate. Then bring the carrier onto the bracket and tighten the four front screws gently. Removing those four screws releases the carrier for later underside access while leaving the adhesive bracket in place.

## Clearance behind the carrier

The bracket pad front is at Z = −10 mm and its wall-facing surface is at Z = −13 mm. Existing battery screws extend lowest, to Z = −6 mm: they retain **4 mm clearance to the pad front** and **7 mm to the rear mounting plane**. Converter screw tips at Z = −5 mm and S2 screw tips at Z = −4.4 mm have more clearance. The bracket does not occupy their nut locations. The physical Command-strip pair adds a wall gap, but that extra thickness is not needed for these clearances.

## Command strips and removal

There is one uninterrupted 20 × 144 mm rear pad on each side. These exceed the project's recorded narrow Command 17207 envelope of approximately 12.65 × 92.74 mm. Use one interlocking pair per pad, one half on the bracket and the matching half on the wall, following the strip manufacturer's preparation and loading instructions.

Orient the release tabs downward and leave them exposed below the pad edges. The carrier overhangs the bracket by 8 mm at top and bottom; removing the carrier first provides unobstructed access to separate the interlocking strips and stretch the wall-side release tabs downward along the wall. Do not hide tabs behind the adhesive contact area.

## Printing

The carrier has no integrated underside legs: its full 120 × 160 mm underside, apart from screw holes, lies on the bed. The rear bracket prints with both adhesive-pad backs and its connecting web on the bed; its four posts grow upward. The pads extend to Y = ±72 mm, beyond the posts at ±71 mm, avoiding an unsupported post lip.

The enclosed nut slots have approximately **6 mm roof bridges**. Inspect those bridge layers in the slicer; print quality must allow real nuts to slide in. The two small converter jaws retain their previous side-down orientation and 1 mm recess; they may still benefit from local support or a brim. This revision removes the large suspended carrier floor, not every possible support on every small retainer.

The master contains seven separate, bed-oriented solids with preserved relative packing. Its source layout occupies X = 5–250 mm and Y = 5–233 mm on a 256 × 256 mm A1 bed, so it has only 5–6 mm horizontal edge margin before adding any brim. Keep the arrangement at 100% scale and inspect slicer bed/brim limits. Numerical STL topology and packing are checked separately by the parent reviewer.

## Remaining physical checks

The converter is still the unmeasured 40 × 36 × 18 mm reference from v3; its real dimensions and unobstructed edge lands must be checked. S2 support clearances and battery-holder projections retain the prior physical-fit qualifications. Printed nut-slot tolerance, bridge sag, screw lengths, wall finish, adhesive adhesion to the selected print material, and the loaded assembly's strength require an actual dry fit and mounting test. Closed meshes and nominal clearance do not establish those properties.
