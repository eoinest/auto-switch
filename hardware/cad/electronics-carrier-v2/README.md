# Electronics carrier v2 — fit-test draft

This separate revision preserves the existing edited CAD. It addresses confirmed geometry problems in the previous electronics tray; it is **not final physical fit approval**. The converter for Amazon B0GCW44FDL is not measured, so the pink reference is explicitly a reserved space, not an exact board model.

The carrier is 120 × 160 × 10 mm and exports flat at Z=0. The 3 mm floor, vertical rests, and open through-slots are intended for a straightforward bench fit print on the A1. All dimensions are millimetres. No wall mounting or adhesive attachment is claimed for this electronics tray.

Changes:

- USB-C faces outboard, away from the AA case, with a 12 × 20 × 10 mm illustrative plug keepout. The actual USB cable envelope remains unmeasured.
- All retention slots pass through the full printed geometry. S2/converter slots are 3.5 mm wide for nominal 2.5 mm ties. Battery slots are 4.5 mm wide; wide Velcro straps will not fit them.
- Every slot has at least 3 mm of material to the outer tray edge; the tightest is 3.25 mm. The former battery-slot edge sliver was only about 0.4 mm.
- The battery pocket allows 0.7 mm per side around the seller-nominal 68.7 × 64.2 mm case. Remove both retaining ties and lift the case out to operate its back switch or screw cover. No unverified switch position is modeled.
- The headerless S2 rests on four small outer-corner supports. The underside is 7 mm above the floor, reserving 3 mm for solder joints. The supports avoid the nominal pad rows, but an inspection of the actual board underside is still required. The straps must avoid components, buttons, antenna, and solder joints.
- The converter area has a continuous insulating floor and external slots. A small board cannot fall through an unsupported 37 mm rail gap. An **insulating spacer and actual strap path remain to be selected after inspecting the module underside**. Do not treat the bare flat floor as a finished converter mounting solution.

## Print the small checks first

1. `generated/holder_fit_ring.stl` checks the nominal battery case outline with its 0.7 mm side allowance. Check the actual case's widest seam, screw, wire outlet, and switch projection too.
2. `generated/s2_corner_support_coupon.stl` reproduces the corner support footprints and 7 mm underside clearance. Confirm the board sits on bare PCB areas without contacting components or solder joints. Check the actual soldered wire exits.
3. `generated/electronics_carrier_v2_DRAFT_FIT_TEST.stl` is the larger layout draft. Print only as a fit-test prototype until the converter and retention details are resolved.

For temporary battery retention, use two removable/releasable ties that fit the 4.5 mm slots, approximately 250 mm long, without squeezing the battery case. Other lengths and strap styles need a fit check. The seller specifies the switch on the back; normal service requires lifting the holder out.

## Generate and review

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/electronics-carrier-v2/generate.py
```

The generator checks finite positive dimensions, manifold connected positive-volume prints, slot edge ligaments, rays through every slot center, nominal battery/PCB envelope separation, and nominal corner-pad clearance. These checks do not establish real component fit, strength, printing tolerances, or safe component retention.

`generated/electronics-carrier-v2.blend` contains `ELECTRONICS_V2_ASSEMBLY` with origin at the carrier center and floor Z=0. Fit coupons and presentation objects have separate collections. The existing approved isolated servo mechanism is unchanged and is not generated here.
