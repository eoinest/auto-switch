# Independent V7 centered-tower review

Status: **PASS for the final nominal geometry.** Checks run against the saved assembly and binary STL exports; physical fit remains untested.

The intended revision reprints the carrier with only **two battery towers at X±43, Y−32 mm**. The old four tower positions, X±43 at Y−52/−12, must be empty above the 3 mm base, and their obsolete holes must be filled. Both new tower tops are Z22, matching a seller-nominal 19 mm case on the 3 mm carrier. The separate bar is a plain **96 × 10 × 3 mm slab**, underside Z22 and top Z25, without a central step or designed gap.

Two M3×30 screws preserve full engagement with ordinary M3 nuts under the carrier. Under-head Z25 minus 30 mm gives tip Z−5. With nuts extending to Z−2.4, the screw projects 2.6 mm beyond each nut. The existing wall-bracket pad front is Z−10, leaving 5 mm from screw tip to that plane. This is a geometric stack check, not a physical fastener measurement.

The bar is centered at Y−32, clear of the estimated lower-right switch and upper-right cable route. Wire exit height remains unmeasured. The original horizontal cradle clearance remains; a flat bar does not eliminate all lateral play. Optional existing shims can address that independently.

The first saved-carrier review exposed an import transform error: the original base shifted down 1.5 mm before modification, leaving old-post footprints and suspended faces. The final generator avoids that import-and-cut approach and rebuilds the carrier from the original V4 feature dimensions, replacing only the battery-post layout. The independent audit checks actual base bottom/top surfaces, not just configured coordinates, and compares geometry with the saved V4 carrier.

Seller dimensions are nominal. With zero designed vertical clearance, a taller physical case or printing error may prevent seating; do not force the holder or compensate by overtightening. The existing controller and converter mount fit is outside this review.

## Final saved-mesh results

[review_mechanics_independent.py](review_mechanics_independent.py) writes [generated/independent-mechanical-review.json](generated/independent-mechanical-review.json). It makes no saved CAD changes.

- Three sampled base sections measure **Z0 to Z3**. All four old post regions are empty above Z3, and all four old hole probes are completely filled. Removed-post probes exclude the 0.05 mm footprint overlap with the intentionally preserved cradle wall.
- Both centered post tops and both bar bearing faces measure **Z22**; both bar tops measure **Z25**. Seven underside samples across the bar are all Z22, confirming a flat slab without the former center step. The nominal case face also measures Z22: **zero designed gap**.
- Four M3 shaft checks clear both new mounting stacks. The bar clears the original carrier outside intended bearing contact, the nominal case, the switch-access envelope and cable corridor. Coincident bearing surfaces are offset by 0.001 mm during intersection checks to avoid numerical artifacts.
- Exact Boolean comparisons against the saved V4 carrier, excluding only the two battery-post strips, leave differences of **0.000037 mm³ added and 0.000171 mm³ removed**. These negligible numerical residues confirm preservation of the other modeled carrier features; they do not establish fit against physical controller or converter parts.
- Carrier STL dimensions are **120 × 160 × 22 mm**; bar dimensions are **96 × 10 × 3 mm**. Both rest at Z0 with broad flat contact and **zero suspended downward-facing area**. The combined layout occupies **120 × 180 mm**, with 10 mm between parts, inside the A1 bed. Near-vertical normals are excluded using a small angular tolerance.

The existing wall bracket and its attachments are reused. The new carrier and flat bar are the only two pieces in this revision's master STL.
