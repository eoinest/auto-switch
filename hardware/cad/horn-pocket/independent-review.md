# Independent photo-based horn-pocket review

Status: PASS for the final photo-estimated interface and preview print-orientation checks. This is a **photo-estimated fit-coupon design**, not approval of the supplied horn's exact dimensions and not a replacement for production paddles.

The actual photograph establishes a tapered double-arm horn. Scaling against the printed frame suggests an overall span of 31–32 mm, hub diameter around 7.3–7.5 mm, visible arm-root width around 5.3 mm, and rounded-end width around 4 mm. The design uses 31.5/7.4/5.3/4.0 mm respectively. Perspective and pixel-edge selection leave roughly±1 mm uncertainty in overall span. The photograph does not establish arm thickness, underside boss or axial seating depth; the 2 mm arm and 4 mm hub depth remain assumptions. Apparent arm asymmetry is not reliable enough to encode.

## Interface

The locating rim adds material around the horn while preserving the baseline seating plane at X13. The flange remains 4 mm thick, from X9 to X13. The rim rises 1.2 mm to X14.2. A nominal 2 mm arm projects 0.8 mm above the rim; screws provide retention, rather than a snap fit or printed spline.

The pocket has 0.3 mm per-side clearance. Three coupons scale the estimated outline to 97%,100% and 103%; all retain the same clearance. The largest rim spans 35.445 mm, so the revised 36 mm-wide flange supports it with 0.2775 mm remaining at each end. This fixes the earlier 35 mm flange overhang.

Center access remains 4.8 mm diameter. The outer slots retain a 4 mm straight segment plus 2.2 mm rounded ends, for 6.2 mm total length. Actual stock-horn holes, center-screw head and attachment fasteners still govern physical assembly. The pocket aligns the horn and paddle but does not establish the servo's neutral angle.

## Printing and identification

Only the three small coupon STLs are exported. Full paddles remain previews; existing production STLs are unchanged. Coupons print floor-down, cavity-up. In the master layout's top view, increasing world X gives **97%,100%,103% from left to right**. Labels are preview-only: mark each coupon before lifting it from the bed.

The widened full-paddle preview uses a ramp from X−3 to X9 while growing from half-width 6 to 18 mm, preserving a 45° slope. Independent transformed-mesh checks find no above-bed downward faces steeper than 45° on any of the normal, mirrored or raised previews. This checks orientation and overhang geometry; it does not approve full production motion or physical fit.

## Saved-mesh checks

`review_interface_independent.py` loads the final Blender files independently of the generator's checks:

- Nominal horn/seat intersection has a tiny coplanar-contact artifact, approximately 0.0013 mm³. Separating the horn by only 1 micrometre axially gives exactly 0 mm³, distinguishing numerical contact noise from rim interference.
- A4.78 mm diameter center-access probe and both 2 mm outer-slot probes have no intersection with the printed seat. These checks do not assert that unknown stock-horn holes accept those fasteners.
- Measured flange floor is 4.0 mm; rim depth is 1.2 mm.
- All three preview print orientations pass the 45° face check.

Results are recorded in `generated/independent-interface-review.json`. The root agent separately verifies closed coupon solids, Z=0, master/individual agreement and layout spacing. Physical horn fit, underside clearance, fasteners, loaded behavior and complete assembled motion with the widened flange remain unverified.
