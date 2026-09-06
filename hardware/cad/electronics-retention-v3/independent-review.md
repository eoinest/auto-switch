# Independent retention review

Status: **review concept only; actual component fit is not approved. A user-requested concept STL export is available in `generated/stl-concept/`; it does not change this physical-fit assessment.**

This review independently checked the generator coordinates and the revised saved Blender assembly. It covers the nominal reference envelopes, not the purchased hardware. `generated/independent-travel-review.json` records 28 actual Boolean intersection-volume checks: both converter jaws at every 1 mm position from −3 to +3 mm against both the base and recessed floor. All had zero intersection volume at the report precision. Each of the six printable meshes also independently passed a connected-vertex traversal: one connected solid, zero non-manifold edges, and positive signed volume.

## Problems found and corrected

- The original converter jaw feet collided with the insulating floor during inward adjustment. The floor is now narrower and recessed: at maximum inward travel the lower jaw ledge has 1 mm horizontal clearance from the floor and the jaw foot has 4 mm. Mesh checks independently confirmed the full travel.
- The original capture lip reached 3 mm onto the PCB, but the stated bare-edge requirement was 2 mm. The lower supporting ledge still reaches 3 mm and the stated land now matches it. The upper lip was shortened to 2.5 mm so outward jaw travel releases it with 0.5 mm nominal clearance.
- The original converter slot left only 1.3 mm of base material to the outer edge. Moving the converter left gives 5.3 mm at the outermost slot edge.
- The original board reference sat directly on the converter floor. Two lower edge ledges now support it 3 mm above the central floor; this provides room for underside parts only where those parts are actually shorter than the gap.
- The S2 USB connector now faces outward, away from the AA holder. Two plastic rests support its USB end.

## Nominal capture and assembly

| Part | How it is held | Checked clearances and access |
|---|---|---|
| AA holder | Four low cradle walls constrain horizontal motion; two removable bars prevent lift-out; floor supports the case. | A 68.7 × 64.2 × 22.5 mm box has 0.7 mm side allowance and 0.5 mm space below the bars. Walls rise 8 mm above the base, so this nominal box cannot slide underneath a bar and escape. Bar screws bottom the bars on separate rigid posts, rather than tightening the bars into the case. Remove both bars and lift the holder for switch/lid access. |
| S2 Mini | Two factory-hole bolts secure the antenna end; plastic edge rests carry downward load near the USB end. | PCB underside is 7 mm above the base except at its supports. Bolts constrain lift and lateral movement; rests reduce USB-end cantilever flex. Actual hole positions, underside parts, pad rows and solder joints require inspection. |
| Converter | Two opposing movable jaws support the bare PCB edges below and capture them above; two end stops prevent longitudinal escape. | The nominal 40 × 36 × 1.6 mm PCB has 0.4 mm vertical jaw clearance and 0.5 mm clearance to each end stop. Each jaw needs a clear 3 × 10 mm lower contact area and 2.5 × 10 mm upper capture area; the configuration conservatively requires 3 × 10 mm clear on both faces. The reference component envelope has 0.5 mm lateral clearance to the upper lip, which must be checked against real components. |

The converter width adjustment is **34–46 mm**, based on two jaws each moving 3 mm from a nominal 40 mm opening. It is not a general fit range for arbitrary boards: board length remains based on the 36 mm reference, thickness on 1.6 mm, and contact locations are fixed along the edges. No claim is made that the selected B0GCW44FDL lies in this range.

For removal, loosen both jaw screws and slide both jaws fully outward. The 2.5 mm upper lip and 3 mm available travel leave 0.5 mm nominal lateral clearance per side for lifting the PCB. If the print or actual board binds, remove a jaw screw and withdraw that jaw completely; do not flex the PCB through a closed groove.

## Fastener stack review

The model uses screw length measured below its head, straight through-holes, and ordinary nuts accessible from the open underside. No hidden captive-nut pocket or printed thread is assumed.

| Location | Modeled screw | Stack below head through nut | Screw tip relative to base underside | Clearance above foot-bottom plane |
|---|---|---|---|---|
| Battery bars, four | M3 × 35 | 29 mm to base underside + 2.4 mm nut | −6 mm | 1 mm |
| Converter floor and jaws, four | M3 × 10 | 5 mm to base underside + 2.4 mm nut | −5 mm | 2 mm |
| S2, two | M1.6 × 16 | 11.6 mm to base underside + 1.3 mm nut | −4.4 mm | 2.6 mm |

All modeled nuts engage the screw shafts and can be installed before placing the tray on its feet. Screw heads are accessible from above. The feet provide 7 mm below-base space; tightening nuts is done by lifting or turning the tray, not by attempting to fit a tool into that 7 mm gap while it rests on a table. Washer thickness is not included in these stacks; adding washers requires recalculating engagement and checking the selected real head/washer size. No metal fastener crosses the converter PCB footprint.

## Still required before a print release

- Confirm the purchased S2 variant's two holes and their locations, PCB thickness, and clear support areas on the underside, especially the USB-end rests. The 3.3 mm antenna-end hole offset is inferred, not independently dimensioned in the cited drawing.
- Measure the converter PCB length/width/thickness; inspect both faces for 3 × 10 mm clear edge lands, underside parts, solder pads and wire exits. The 40 × 36 × 18 mm reference remains a placeholder. Boards with obstructed edges need a different mount.
- Measure the AA holder's widest seam, full depth including projections, switch, cover and wire exit. The floor and wire notch are not yet verified against those features. The nominal 0.5 mm bar gap must remain positive on the actual case.
- Dry-fit printed coupons and actual screws/nuts, then check USB insertion, wire bends, bar removal and battery replacement. Nominal dimensions and closed meshes do not establish FDM tolerance, beam stiffness, creep, load capacity or electrical clearances.
- This is a bench electronics carrier; no wall attachment or ability to carry the battery load on the servo's adhesive mounting is asserted.
