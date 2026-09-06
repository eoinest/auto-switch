# Electronics mounting — v3 design review

The earlier tray reserved space but did not finish the component fastenings. This revision adds inspectable mechanical retention. It remains a **design concept**, pending actual component measurements and dry fits; it is not a replacement print-ready release.

## Inspect the design

- [Blender: assembled and exploded mounts](../hardware/cad/electronics-retention-v3/generated/electronics-retention-v3.blend)
- [Rendered assembly](../hardware/cad/electronics-retention-v3/generated/electronics-retention-v3.png)
- [Dimensioned mechanisms and example fastener BOM](../hardware/cad/electronics-retention-v3/README.md)
- [Independent retention review](../hardware/cad/electronics-retention-v3/independent-review.md)

The green/black component shapes and metal fasteners are reference objects. Blue/orange shapes are proposed printed parts. No new STL release is included: the example converter is 40 × 36 mm, not the measured selected module. Adjustments refine an already-sized mount; a smaller module requires regeneration rather than simply tightening the jaws further.

## S2 Mini: use its two mounting holes

The official LOLIN S2 Mini has **two 2.0 mm mounting holes, 20.4 mm centre to centre**, at the antenna end opposite USB. The horizontal edge inset is 2.5 mm. The approximately 3.3 mm inset from the antenna edge is derived from the drawing geometry, not an explicitly dimensioned measurement. Confirm it on the actual board before printing the final mount.

The design uses two small standoffs and M1.6 through screws/nuts, leaving 7 mm under the PCB for underside components and direct-solder joints. M1.6 gives nominal clearance through a 2.0 mm PCB hole; do not force an M2 screw through it. Keep screw heads/nuts and support footprints clear of antenna copper and populated areas. Any extra support near the USB end must land on a clear area of the actual board.

Sources: [official dimension drawing](https://www.wemos.cc/en/latest/_static/files/dim_s2_mini_v1.0.0.pdf), [official board photograph](https://www.wemos.cc/en/latest/_static/boards/s2_mini_v1.0.0_1_16x16.jpg).

## Buck-boost module: insulated edge capture

The selected B0GCW44FDL module has no mounting holes. The concept uses adjustable insulating jaws on a removable sled. Lower shelves support suitable bare PCB edges; upper lips capture those edges against lifting, and stops prevent sliding. The screws and nuts sit outside the PCB footprint.

Jaw positions, underside clearance and capture height depend on the **actual PCB thickness, component placement, solder joints and clear edge areas**. No clamp should press on the inductor, capacitors or soldered wires. If the delivered board has no suitable bare edges, this concept must change to a component-specific cage. The old 40 × 36 × 18 mm reserved space is not a board specification.

## Battery holder: removable retaining bars

A shallow cradle locates the closed case sideways. Two removable bars prevent it lifting out. The bars bolt to outboard posts with mechanical stops so tightening the bolts does not squeeze the battery case. The nominal design leaves a small gap over the seller-sized case; actual depth and seam projections need checking.

Remove the bars and lift the holder to access its back switch and screw-secured battery cover. Do not drill the battery housing. Leave the wire exit free and provide enough lead slack to lift the case without pulling its soldered connections.

## Before the final STL

Confirm the actual S2 hole position/diameter and underside clearance. Measure the converter's PCB length, width, thickness, height above/below the PCB, and identify bare clamp areas. Measure the closed battery holder including switch/seams and locate its lead exit. Then test the screw access, removal path and retention on small printed interfaces.

The current BOM is [here](../BOM.md). The previous [v2 fit-test tray](electronics-carrier-v2.md) remains available for reference; its mesh checks did not establish complete component retention.
