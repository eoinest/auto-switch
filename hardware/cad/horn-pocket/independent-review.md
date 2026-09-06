# Independent horn-pocket interface review

Status: PASS for the final nominal interface and saved-mesh checks. This is a **provisional fit-coupon design**, not approval of the supplied horn's actual shape and not a replacement for production paddles.

The assumed horn is a 22 × 5 × 2 mm double arm with a 7 mm hub. Its actual taper, boss, holes and face geometry have not been established by the existing project measurements or manufacturer outline. The supplied horn must remain the spline interface.

## Seat and screw access

The design adds a raised locating rim rather than moving the horn inward. The seating face stays at X13, preserving the baseline horn/shaft engagement and paddle position. The flange spans X9–13: **4 mm of floor remains**. The rim rises another **1.2 mm**, to X14.2. A nominal 2 mm arm therefore projects 0.8 mm beyond the rim; the pocket locates it without covering it or creating a snap fit.

The default 0.3 mm per-side allowance gives a 22.6 × 5.6 mm arm pocket plus a 7.6 mm hub pocket. The outer contour adds 1.2 mm walls; the 26 × 14 mm flange supports the full rim. Coupons compare 0.2, 0.3 and 0.4 mm allowances, not three supposedly verified horn sizes.

The 4.8 mm center access hole is preserved through the flange. It provides the existing axial screwdriver path, but actual center-screw head dimensions still govern fit. The outer slots retain a 4 mm straight section plus a 2.2 mm diameter end profile, giving a 6.2 mm overall slot length. At centers Y±7, their extreme ends are Y±10.1, still inside the default pocket ends Y±11.3. Actual horn attachment fasteners remain dependent on the supplied holes; the locating rim does not replace screws.

A symmetric double-arm pocket aligns the paddle and horn during assembly but does not establish the servo's electrical neutral angle. Neutral calibration and stock-horn spline installation remain separate steps.

## Printing and identification

Only the small coupon STLs are exported. Full-paddle models remain labeled previews; existing production STLs are unchanged. Coupons print with the flange floor directly on the bed and the cavity facing upward.

In a top-down view of the master coupon layout, increasing world X runs **0.2, 0.3, 0.4 mm from left to right**. Text labels are preview-only. Mark each coupon before lifting it off the bed so the different allowances cannot be mixed up.

Use a coupon to establish easy seating without force. It cannot verify a differently shaped horn, a hidden center boss, hole diameters, axial engagement on a real servo, fastener lengths, or loaded torque behavior. No physical-fit claim is made by the nominal contour checks.

## Final saved-mesh audit

`review_interface_independent.py` loads the final close-up Blender file and measures the actual meshes independently of the generator's report:

- Horn/seat intersection: approximately 0.00000067 mm³, below the 0.0001 mm³ numerical-contact tolerance.
- Center access cylinder: no intersection for a 4.78 mm diameter probe.
- Both outer slot paths: no intersection for 2 mm diameter probes at Y±7. This checks the printed slot paths, not the stock horn's unknown hole sizes.
- Measured flange floor: exactly 4 mm.
- Measured rim depth above preserved X13 seating plane: approximately 1.2 mm.

The final close-up render was inspected. Results are saved in `generated/independent-interface-review.json`. The earlier preview flange-ramp ledge was corrected to a 7 mm run from X2 to X9 for the 7 mm increase in half-width. Full-paddle production geometry and motion remain outside this coupon-only approval.
