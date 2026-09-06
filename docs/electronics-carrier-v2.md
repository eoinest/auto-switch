# Electronics carrier v2 — fit-test revision

**Retention is being redesigned:** use the [v3 mounting review](electronics-retention.md) for S2 screw mounts, converter edge capture and battery retaining bars. This v2 tray is an earlier fit-test layout, not the final component mount.

This revision is for the current **headerless ESP32-S2 Mini + DAIERTEK switched four-AA holder + Teyleten Robot B0GCW44FDL buck-boost module**. It is a separate carrier beside the approved one-servo actuator. The breadboard stays on the bench.

**Full-carrier physical fit is not approved.** The selected converter has no verified mechanical drawing, and the actual holder, solder joints and USB plug have not been measured. An exported STL can be a valid printable solid without fitting those components. Start with the supplied fit-test pieces and keep the full carrier as a draft until the checks below pass.

- [Current BOM CSV](../hardware/s2-current-bom.csv)
- [Independent component/source audit](s2-electronics-component-audit.md)
- [Current electrical wiring](s2-aa-poc.md)
- [Approved separate servo mechanism](servo-command-mount.md)

## Review files and STL exports

- [Full assembly in Blender](../hardware/cad/electronics-carrier-v2/generated/full-assembly-review.blend) — approved actuator geometry plus revised electronics carrier.
- [Full assembly image](../hardware/cad/electronics-carrier-v2/generated/full-assembly-review.png)
- [Electronics-only Blender model](../hardware/cad/electronics-carrier-v2/generated/electronics-carrier-v2.blend)
- [Draft full carrier STL](../hardware/cad/electronics-carrier-v2/generated/electronics_carrier_v2_DRAFT_FIT_TEST.stl) — **120 × 160 × 10 mm; physical fit pending**.
- [Battery outline fit ring](../hardware/cad/electronics-carrier-v2/generated/holder_fit_ring.stl) — **76.1 × 71.6 × 2 mm**; tests the case perimeter only.
- [S2 corner-support fit coupon](../hardware/cad/electronics-carrier-v2/generated/s2_corner_support_coupon.stl) — **35.4 × 44.3 × 10 mm**; tests the nominal corner supports and underside clearance, not full retention.
- [Independent exported-STL verification](../hardware/cad/electronics-carrier-v2/generated/independent-verification.json)
- [Generator verification](../hardware/cad/electronics-carrier-v2/generated/validation.json)

The revised tray has a 3 mm floor and a 7 mm nominal clearance beneath the S2. The USB connector faces outboard; the 12 × 20 × 10 mm plug volume is an allowance, not a measured cable. Minimum tie-slot width is 3.5 mm for nominal 2.5 mm ties. Battery slots are 4.5 mm wide and require narrow reusable ties, not wide hook-and-loop straps. The holder lifts out for its back switch and screw cover. The converter rests over a continuous floor and requires a removable insulating spacer selected after inspecting its underside; this is not a completed converter retention design.

## Problems found in the previous carrier

Independent reviewers found blocked converter strap slots, 2 mm slots narrower than the referenced 2.5 mm ties, converter rails that a smaller PCB could not span, a USB socket facing the battery with no verified plug clearance, and a battery-strap opening leaving only 0.4 mm to the tray edge. The old assembly also shows the superseded broad wall chassis instead of the approved narrow Command-strip actuator.

The previous mesh was closed and connected and fit the A1 bed. Those checks did not detect the assembly problems above. The new revision and its independent mesh review must address both geometry and assembly access.

## What must be checked on the actual parts

With batteries removed and USB disconnected:

1. **Converter:** measure PCB length and width, overall height including underside solder joints, and any projecting components. Record input/output wire exits. The exact selected ASIN matters; dimensions of a similar-looking module are not a substitute.
2. **Holder:** measure the loaded, closed case, then locate its back switch, cover screw, lid opening direction and lead exit. Its seller nominal outline is 68.7 × 64.2 × 22.5 mm. Retention must allow removal to operate/access the back and replace cells.
3. **S2:** check the actual board outline against the nominal 25.4 × 34.3 mm. Look under the board for components and solder joints that would touch a support. Plug the actual USB cable in and check room for the plug and cable bend. Do not compress components, solder pads or antenna with a strap.
4. **Harness:** inspect the soldered wire diameter and bend space, heat shrink and strain relief. Mechanical wire references are not pin assignments; follow the wiring document.
5. **Retention:** insert the actual straps/ties into the printed slots. Confirm a small converter rests securely on its insulating support and cannot slide into solder joints or wires. A large empty bay alone does not establish retention.

## Print and use scope

The fit-test pieces check only the interfaces they reproduce. An outline ring alone cannot validate a populated PCB's underside, its retention, or USB access. Inspect the supplied verification report for the exact scope of each coupon.

Use the Bambu A1 in millimetres and inspect the slicer preview before printing. Do not print the component reference blocks, USB cable envelope, labels or presentation surface. Keep the already-approved servo STL files separate from the draft electronics carrier.

The battery carrier needs its own support; its weight must not be hung from the servo attachment. No carrier wall-attachment method has been physically validated. Bench assembly and dry fit come before powered operation.

## Independent review results

Three agents reviewed component sources, mechanical design and exported mesh geometry. The final independent verifier reads the STL triangles directly: all three parts are single closed, consistently wound solids at Z=0 within the A1 envelope. All ten slots are open; measured slot apertures are 3.5 or 4.5 mm, with a minimum 3.25 mm outer-edge ligament. Samples confirm the continuous 3 mm converter floor, nominal battery clearance and 7 mm S2 underside clearance. No downward-facing surface exceeding 45 degrees occurs above the bed; a slicer inspection is still required.

The combined preview uses `servo-command.blend` at frame 1. A separate Blender comparison found its mount and paddle equivalent to the approved STL shapes, with at most 0.000004 mm numerical deviation after rigid placement normalization. The previously edited Blender files and approved servo STLs were not overwritten.

Regenerate with Blender's background mode and `hardware/cad/electronics-carrier-v2/generate.py`, then run `python3 hardware/cad/electronics-carrier-v2/verify_independent.py`. Generate the combined preview using `assemble_review.py`. Mesh checks do not remove the physical-fit blockers listed above.
