# Compact XL63070 mount study

This is a **visual comparison, not a printable design**. The received board is much smaller than the former 40 × 36 mm placeholder. These scenes use a provisional **16 × 30 mm PCB**, with **1.2 mm thickness assumed**. Component boxes are reconstructed approximately from the user's photos; underside parts, solder joints, bare contact areas and exact dimensions remain unverified.

- [Three options](generated/booster-retention-options-PROVISIONAL.png)
- [Recommended candidate closeup](generated/recommended-end-fingers-PROVISIONAL.png)
- [Editable Blender scene](generated/booster-retention-options-PROVISIONAL.blend)
- [Independent design review](design-review.md)

| Option | Retention | Tradeoff |
|---|---|---|
| A: slide-in rails | Continuous top lips and a removable end stop | Lips approach the inductor and right-edge components; removal requires sliding the wired board. |
| B: split side clamps | Short adjustable side jaws | Less coverage, but the proposed long-edge contact patches are crowded and unverified. Additional adapter hardware is needed. |
| **C: narrow end fingers** | Two keyed, removable fingers over the center of each short end; low side guides | Best candidate from the photos: the corner solder pads stay open. The narrow center contact patches and underside supports still need confirmation. |

**C is recommended for the next fit prototype.** Orange pieces are removable retaining fingers. Gold pieces represent thin seat-height shims. Teal shoulders beneath them provide a hard screw stop; tightening is not intended to force a poorly matched clamp onto the PCB. Measured board thickness sets the shoulder height, with small shim changes available for printed fit. Each finger is 2.8 mm wide and overlaps the board by only 0.6 mm in this concept. Low guides touch the substrate edge below its populated top face. Separate small end stops sit between the corner pads and leave 0.2 mm nominal end clearance. The central underside is open, and support ledges avoid the terminal-pad regions.

The adapter reuses the **46 mm spacing** between the existing converter-floor mounting holes. On the actual carrier these are X22/Y22 and X22/Y68. The study spreads the three candidates sideways for comparison; those scene positions are not assembly coordinates. Replace the old converter floor and jaws, while retaining the current carrier. Schematic screw heads in these images indicate attachment locations; no shafts or screw lengths are modeled. Final length and stack will follow actual measurements. Add wire strain relief away from solder joints.

No STL is generated. Before a fit coupon or final mount: confirm PCB width, length and thickness; show the underside; verify the two narrow bare center patches and support zones; account for the soldered wires. See the root-owned requirements and fit-evidence notes for measurement provenance.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/booster-retention-study/generate.py
```
