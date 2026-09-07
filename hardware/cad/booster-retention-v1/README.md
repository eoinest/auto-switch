# XL63070 end-finger mount — FIT-TEST v1

This is a **printable fit test**, based on an unmeasured **16 × 30 × 1.2 mm PCB assumption**. It replaces the oversized converter floor and side jaws, using the same carrier holes at X22/Y22 and X22/Y68 (46 mm pitch). The carrier does not need to be reprinted for this adapter alone.

- [All five booster pieces in one STL](generated/booster-retention-v1-ALL-FIVE-FIT-TEST.stl)
- [Assembly](generated/booster-retention-v1-assembly-FIT-TEST.png)
- [Print layout](generated/booster-retention-v1-print-layout-FIT-TEST.png)
- [Dimensions and validation manifest](generated/manifest.json)
- Individual pieces are in `generated/stl-fit-test/`; corresponding Blender scenes are in `generated/`.

## Parts and hardware

| Piece | Quantity | Size, mm |
|---|---:|---|
| Open adapter with low guides and end supports | 1 | 20 × 58 × 6.2 |
| Removable end finger | 2 | 8.2 × 13.6 × 2 |
| Seat-height shim | 2 | 7.8 × 11 × 0.4 |

Use **two M3×16 screws and two ordinary M3 nuts** from the existing assortment. Each screw passes through a finger, its shim, the adapter and the carrier. The two **0.4 mm shims are essential for the default modeled stack**; they place the finger undersides at the assumed PCB top, Z7.7. The hard seats beneath them prevent indefinite downward travel. The screw under-head plane is Z9.7 and its tip is Z−6.3, with full engagement through the nut at Z0…−2.4. This leaves 3.7 mm to the existing wall-bracket pad-front plane at Z−10; check the actual screw stack when assembling.

## Print and dry fit

Print at **100% scale, millimeters**, with all pieces flat as exported. The nominal geometry needs no supports. A 0.2 mm layer height makes each shim two layers thick; verify those layers in the slicer before printing. The two fingers and two shims are identical pairs; their upper/lower names identify assembly positions.

1. With power disconnected, remove the old converter floor and jaws. Place the new adapter over the existing pair of mounting holes.
2. Set the board on the support shelves. Its solder joints, underside parts and four corner pads must clear the plastic. The two narrow end-center support shelves are assumed bare locations, not physically verified.
3. Put one 0.4 mm shim on each raised screw seat, then one finger above it with the narrow tongue facing the PCB. The side keys prevent the finger twisting.
4. Start with each screw centered in its slot. At the nominal position each 2.8 mm-wide tongue overlaps the center of the PCB end by 0.6 mm. The 1.6 mm-deep underside shelf supports the tongue footprint including inward adjustment. Outward movement can lose capture; check that both tongues actually overlap the board and remain between the terminal pads.
5. Install the nuts and tighten gently against the seats. Do not bend the PCB or force a finger over a component. If the board thickness or contact areas differ, stop and revise the fit instead of tightening harder. Route and secure wires separately so solder joints do not carry cable pull.

The underside support height is Z6.5, the assumed PCB top is Z7.7, and the low end stops finish at Z7.22 so they do not defeat subsequent shim-height changes. Low side guides touch the substrate edge rather than covering its populated top. The central underside and terminal corners remain open.

The board envelope, thickness, underside clearances and contact patches still need a physical check. This export is not a claim of production fit or thermal validation. Existing battery, controller and wall-bracket models are unchanged.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/booster-retention-v1/generate.py
```
