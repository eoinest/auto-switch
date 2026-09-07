# Independent booster fit-test review

**PASS for the assumed 16 × 30 × 1.2 mm reference board only.** This verifies the new printed mechanism against its saved nominal model. It does not establish the delivered board's thickness, underside clearance, soldered-wire clearance or actual contact patches.

[review_mechanics_independent.py](review_mechanics_independent.py) loads the saved assembly and reads the five binary STL files. Results are recorded in [generated/independent-mechanical-review.json](generated/independent-mechanical-review.json); the audit saves no CAD changes.

## Contact and screw stack

Both end-center support shelves measure **Z6.5** at the contact patches. Both finger undersides measure **Z7.7**, giving the modeled PCB exactly **1.2 mm** between support and finger. The shelves are 2.8 mm wide and 1.6 mm deep, supporting the nominal 0.6 mm finger overlap and its inward adjustment range. The two upper contacts sit between the modeled corner pads, rather than on components or terminal pads.

Both screw hard seats measure **Z7.3**. Each included shim is **0.4 mm thick**, bringing the finger seat to Z7.7. Those shims are required for the default 1.2 mm PCB model. Without them the fingers sit lower; do not simply omit them with this board assumption.

Low end stops finish at **Z7.22**, below even the unshimmed seat. This corrects the study's taller stops, which would have prevented lower finger adjustment. The audit confirms that the fingers can reach their hard seats without colliding with those stops. Low side-guide inner faces measure **X±8.2**, giving 0.2 mm per-side allowance around the nominal 16 mm PCB. Anti-rotation key inner faces measure **X±4.3**, giving 0.2 mm per side around each 8.2 mm finger foot.

Two **M3×16 screws** pass through the fingers, shims, adapter and carrier, into ordinary M3 nuts. The under-head plane is Z9.7, so the screw tips end at Z−6.3. With the nuts ending at Z−2.4, each screw projects 3.9 mm beyond the nut. The existing wall-bracket pad-front plane is Z−10, leaving 3.7 mm of nominal clearance. Hole probes verify the local Y±23 positions: **46 mm pitch**, mapping to carrier X22/Y22 and X22/Y68.

## Retention and clearance

The mechanism restrains width with low side guides, length with two short-end stops, and lift with the two removable fingers. Direct supports beneath the finger patches prevent the design from relying on PCB bending. The keyed feet resist finger rotation, while the screws clamp them onto printed seats rather than providing unlimited downward adjustment.

**100 exact Boolean intersection checks returned zero volume.** These cover printed parts against the approximate solder-pad/component references, intended PCB clearances, finger-to-adapter clearance, and the mounting-shaft paths. Intended planar contact is offset by 0.001 mm during the checks to avoid coplanar numerical artifacts. The component references are approximate, so these results are not proof of clearance around the real module or its solder fillets.

Outward sliding can remove the finger overlap; the nominal position must be checked during assembly. The fixed tray also has finite width/length clearance, so the slotted fingers do not make this a universal adjustable holder. Wires need separate strain relief; the current adapter does not include a dedicated wire clamp.

## Print geometry

All five exported parts have their flat faces at **Z0** and **zero suspended downward-facing area**. The adapter's mounting ears were widened to 12 mm so the anti-rotation guides have support beneath them; the narrower study ears would have left 0.7 mm ledges. Approximate exported sizes are:

| Part | Quantity | Dimensions |
|---|---:|---|
| Adapter | 1 | 20 × 58 × 6.2 mm |
| End finger | 2 | 8.2 × 13.6 × 2 mm |
| Height shim | 2 | 7.8 × 11 × 0.4 mm |

The generator checks each part is connected and manifold; the parent agent independently audits the final combined STL. Use 0.2 mm layers to preserve the two-layer shims. No physical fit, clamp strength, creep, vibration or thermal test has been performed. Dry-fit without power and revise the contact stack if it forces or bends the board.
