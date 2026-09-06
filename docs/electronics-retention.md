# Electronics mounting — v4 flat carrier and wall bracket

The main mount now prints as **two pieces**: a carrier with a flat underside and a separate H-shaped wall bracket. Four screws join them after printing. The bracket has two continuous **20 × 144 mm** rear pads for the narrow Command strips. The five removable component retainers remain separate, making seven printed pieces total.

The mounting geometry has been checked; purchased-component fit and adhesive retention remain unverified. In particular, the converter still uses the earlier placeholder dimensions.

## Inspect the design

- **[Master STL: all seven pieces laid out for printing](../hardware/cad/electronics-retention-v4/generated/electronics-wall-mount-ALL-PIECES-v4-CONCEPT.stl)**
- [Blender print layout](../hardware/cad/electronics-retention-v4/generated/electronics-print-layout-v4.blend) · [assembled Blender model](../hardware/cad/electronics-retention-v4/generated/electronics-retention-v4.blend)
- [Rear adhesive pads](../hardware/cad/electronics-retention-v4/generated/rear-pads-v4.png) · [print layout image](../hardware/cad/electronics-retention-v4/generated/print-layout-v4.png)
- [Dimensioned mechanisms and fastener BOM](../hardware/cad/electronics-retention-v4/README.md)
- [Independent mounting review](../hardware/cad/electronics-retention-v4/independent-review.md) · [STL audit](../hardware/cad/electronics-retention-v4/generated/independent-stl-audit.json)

The master STL contains only printed pieces; electronic references and fasteners are excluded. Its **245 × 228 mm** footprint fits the A1's 256 mm bed, with at least 5 mm between part bounding boxes. Each part starts at Z=0. Import in millimetres, preserve the layout, and use **by-layer** printing. Check any brim or skirt stays inside the bed. The carrier has no underside feet or suspended floor; the bracket prints adhesive-side down. Its nut pockets have short 6 mm bridges. The existing converter jaws have small recessed faces that may need local support; inspect the slicer preview.

The [assembled STL](../hardware/cad/electronics-retention-v4/generated/electronics-wall-mount-ASSEMBLED-v4-CONCEPT.stl) is an assembly preview, not a print-in-place file. Individual STLs are in [stl-concept](../hardware/cad/electronics-retention-v4/generated/stl-concept/).

## Attach the wall bracket

Use **four M3 × 12 mm screws and four ordinary M3 nuts**, in addition to the component hardware. Slide the nuts into the bracket's inward-facing pockets before attaching the carrier. Install the electronics fasteners while the underside is accessible, then screw the carrier onto the bracket from its front. No washers are included in the modeled stack. The wall-contact plane is 13 mm behind the carrier underside, leaving at least 4 mm between the existing battery screw tips and the pad fronts.

Put one mating pair of [Command narrow 17207 strips](https://www.command.com/3M/en_US/p/d/b5005604166/) on each rear pad, with removal tabs downward. Remove the carrier first for full tab access. These are two additional pairs beyond the servo mount's two pairs. The [manufacturer's catalog outline](https://media.digikey.com/pdf/Data%20Sheets/3M%20PDFs/17207.pdf) is approximately 92 × 13 mm, comfortably inside each pad; check your delivered strips without trimming. Use a suitable smooth surface: 3M excludes textured walls. The strip's picture-hanging rating does not establish this assembly's tested load capacity.

The example converter is still 40 × 36 mm, not the measured selected module. A smaller board requires regeneration rather than simply tightening the jaws further.

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

## Before approving physical fit

Confirm the actual S2 hole position/diameter and underside clearance. Measure the converter's PCB length, width, thickness, height above/below the PCB, and identify bare clamp areas. Measure the closed battery holder including switch/seams and locate its lead exit. Then test the screw access, removal path and retention on small printed interfaces.

The current BOM is [here](../BOM.md). The previous [v2 fit-test tray](electronics-carrier-v2.md) remains available for reference; its mesh checks did not establish complete component retention.
