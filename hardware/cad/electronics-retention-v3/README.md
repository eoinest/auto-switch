# Electronics retention v3 — review concept

This replaces the idea that a component merely occupying a bay is securely mounted. It is an **assembly concept, not a fit-approved print**. The existing approved servo mechanism and v2 geometry files are unchanged. A user-requested [concept STL export](generated/stl-concept/) is now available; it is not a final fit-approved release.

Open `generated/electronics-retention-v3.blend`. The left collection is assembled; the right is exploded. Blue and orange are proposed printed parts. Green, black and metallic objects are references and purchased hardware, never printable components. `generated/electronics-retention-v3.png` shows both views. `generated/electronics-retention-v3-underside.png` exposes the accessible nuts and bolt tips from below.

## Actual retention and service access

| Component | Retention | Removal / access |
|---|---|---|
| Headerless S2 Mini | Two M1.6 screws through its factory holes and insulating standoffs; plastic supports under the USB-end board edges resist flex | Lift the carrier to access ordinary nuts from underneath; undo two screws. USB faces outward (+Y). No enclosure over antenna. Verify underside solder/component clearance at supports. |
| AA holder | Four low cradle walls locate the body; two removable crossbars prevent lift-out | Crossbars bottom on rigid towers, leaving a nominal 0.5 mm gap above the holder. Undo four M3 screws and lift holder out for rear switch/cover access. A front-wall notch allows lead exit, but actual lead position still needs verification. |
| Buck-boost PCB without holes | Recessed insulating floor, two removable/sliding lip jaws with lower edge ledges and two end stops capture X, Z and Y respectively | Loosen jaw screws and slide them outward; lift the PCB. Both jaws can be fully removed. No screw passes through the PCB. Metal hardware stays outside its assumed outline. |

All nuts are loose ordinary nuts accessible from the open underside. They are not trapped inside printed cavities. The 7 mm feet make room for nut bodies and screw ends, but assembly still requires lifting the carrier and holding a nut while turning its screw. The concept does not provide a quick wall-docking attachment; it is a bench retention review.

## Dimensioned example and uncertainty

- Carrier: 120 × 160 × 3 mm; underside feet extend 7 mm.
- S2 PCB: 25.4 × 34.3 mm; two 2 mm factory holes on a 20.4 mm pitch. Hole row is **3.3 mm from the antenna end provisionally**: inferred from official drawing vectors, not an explicitly labeled dimension. The modeled 1.6 mm PCB thickness also needs confirmation. Hole axes in the assembled scene are X = −40.2, −19.8 mm; Y = 33.15 mm. PCB bottom Z = 10 mm, hence 7 mm clearance above the carrier. Printed clearance holes are 1.8 mm for M1.6 screws; test before assembly.
- Battery body reference: 68.7 × 64.2 × 22.5 mm; cradle interior 70.1 × 65.6 mm. Body bottom Z = 3 mm and top Z = 25.5 mm. Crossbar bottom Z = 26 mm, leaving 0.5 mm clearance. Wall height 8 mm is much greater than that gap, so the body cannot climb over a wall while bars are fitted. Bar width 10 mm, thickness 3 mm, screw pitch 86 mm, screw rows Y = −52 and −12 mm. Dimensions are nominal, not a dry-fit result.
- Converter example: **40 × 36 mm board, 1.6 mm PCB thickness, 18 mm total height is a placeholder, not a measured B0GCW44FDL model.** Jaw travel is ±3 mm on each side (nominal width adjustment 34–46 mm); longitudinal clearance is fixed for a 36 mm board plus 0.5 mm per end. This is a module-specific concept with small fit adjustment, not a universal holder. A 30 × 16 mm board would need a regenerated floor and jaw placement.
- Converter floor top Z = 5 mm, PCB bottom Z = 8 mm and top Z = 9.6 mm, lip underside Z = 10 mm, giving 0.4 mm vertical free play rather than crushing the board. Lower support ledges overlap each opposing PCB edge by 3 mm, while the upper lips overlap by 2.5 mm. The 3 mm outward jaw travel leaves 0.5 mm clearance for vertical removal of the nominal board; **at least 3 × 10 mm component-free edge land is required on each side**, plus clearance at end stops. The board is supported only on assumed bare edge lands, with a nominal 3 mm gap above the recessed floor for underside solder/components. The floor is narrowed to 26 mm so jaws can move through their full inward travel without colliding with it; minimum geometric gap is 1 mm. Verify actual underside protrusions fit this clearance. Floor, jaw lips, end-stop positions and thickness slot must be redesigned if terminals/components occupy these regions.

The converter's actual board dimensions, component positions, underside protrusions, terminal access, adjustment screw access and usable bare edges remain unknown. Do not print a carrier for it from this example. `config.json` records assumptions; dimensions in `generate.py` must be revised together when measurements arrive.

## Fastener BOM for this example

| Hardware | Quantity | Grip calculation / reason |
|---|---:|---|
| M1.6 × 16 mm machine screw | 2 | 1.6 mm PCB + 7 mm standoff + 3 mm carrier + ~1.3 mm nut = 12.9 mm; nominal 3.1 mm thread remains. Head bears around factory hole; do not tighten against components. |
| M1.6 nut | 2 | Approximate 3.2 mm across flats, 1.3 mm thick. Fully accessible below base. |
| M3 × 35 mm machine screw | 4 | 3 mm crossbar + 23 mm hard-stop tower + 3 mm carrier + ~2.4 mm nut = 31.4 mm; nominal 3.6 mm thread remains. Tip ends at Z = −6 mm, within the 7 mm feet. |
| M3 × 10 mm machine screw | 4 | Two for floor ears, two for jaws. 2 mm part + 3 mm carrier + ~2.4 mm nut = 7.4 mm; nominal 2.6 mm thread remains. |
| M3 nut | 8 | Approximate 5.5 mm across flats, 2.4 mm thick. |

Lengths above assume no washers. If adding washers, include their thickness in the stack and verify useful thread engagement. Keep bolt ends within the underside clearance. Ordinary machine screws are shown; thumbscrews may be substituted only after checking head size and clearance.

## Verification boundaries

`generated/geometry-checks.json` checks that every proposed printed mesh has manifold edges and positive volume. It is **not** a component-fit, interference, material-strength or physical-assembly test. Retainer geometry is undergoing independent review; actual components must still be measured and dry-fitted. S2 factory-hole information: [WEMOS S2 Mini dimensions](https://www.wemos.cc/en/latest/_static/files/dim_s2_mini_v1.0.0.pdf).

Regenerate the Blender scene using:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python hardware/cad/electronics-retention-v3/generate.py
```

## Concept STL export

Run Blender in background with `export_concept.py` to export only the six assembled printed meshes. Component/hardware references and exploded duplicates are excluded. The [export manifest](generated/stl-concept/export-manifest.json) records source hashes and orientations. All parts are individually placed at Z=0 in millimetres. Read [print notes](generated/stl-concept/READ-ME-FIRST.txt): the feet-down base needs support beneath its raised floor, and the side-oriented jaws may need support beneath their recessed faces. Import as separate objects and arrange, rather than combining at their shared origin.
