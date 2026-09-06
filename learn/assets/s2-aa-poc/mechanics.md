# ESP32-S2 Mini + switched AA prototype mechanics

This revision separates a **single-gang wall actuator** from an **independently mounted electronics carrier**. It uses the new DAIERTEK four-AA holder and a LOLIN S2 Mini reference outline. The battery weight is carried by its own mounting surface rather than added to the servo's wallplate attachment. Keep the breadboard on the bench for the first circuit test; its model, outline and rail arrangement have not been identified. The carrier is the next step after breadboard testing, with female jumpers connecting the S2 Mini off the breadboard.

**Prototype status: print small fit coupons first. These STLs are not a claim of exact fit to the user's unmeasured hardware.** There is no verified size drawing for the purchased converter, no measured wallplate, and no confirmation that the user's S2 Mini and MG90S match the reference manufacturers. An adjustable bay is deliberate; an invented exact converter would hide the missing information.

## Files and operation

- [Blender assembly](https://github.com/eoinest/auto-switch/blob/main/hardware/cad/s2-aa-poc/generated/s2-aa-prototype.blend)
- [Rendered assembly](https://github.com/eoinest/auto-switch/blob/main/hardware/cad/s2-aa-poc/generated/assembly-preview.png)
- [Parameters](https://github.com/eoinest/auto-switch/blob/main/hardware/cad/s2-aa-poc/config.json)
- [Reproducible generator](https://github.com/eoinest/auto-switch/blob/main/hardware/cad/s2-aa-poc/generate.py)
- [Mesh and sweep report](https://github.com/eoinest/auto-switch/blob/main/hardware/cad/s2-aa-poc/generated/validation.json)
- [Independent STL report](https://github.com/eoinest/auto-switch/blob/main/hardware/cad/s2-aa-poc/generated/stl-verification.json)

Open the `.blend` and press Space over the 3D view to preview neutral, +10°, neutral, −10°, neutral over frames 1–85. This animation illustrates movement; it is not a validated firmware calibration. One Blender unit represents one millimetre. STL exports are individually centered in XY and placed on Z=0 in millimetres.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/s2-aa-poc/generate.py
python3 hardware/cad/s2-aa-poc/verify.py
```

## Component dimensions and evidence

| Item | Used geometry | Confidence and remaining measurements |
|---|---|---|
| DAIERTEK switched 4-AA case, Amazon B09N1GDWQ9 | 68.7 × 64.2 × 22.5 mm outer case | Seller nominal dimensions from the project holder research. Physical case, switch projection, lid release and lead exit remain unmeasured. The model's small switch position is illustrative. |
| LOLIN S2 Mini V1.0.0 | 25.4 × 34.3 mm PCB outline | Official WEMOS drawing and product specification. Board thickness is provisionally 1.6 mm; underside soldered headers and components are cosmetic fit references. Actual clone, header rows and connectors require inspection. |
| MG90S | 22.8 mm case length, 12.4 mm width, 28.4 mm housing height, 32.5 mm base-to-shaft tip, 32.1 mm ear span, 18.5 mm base-to-ear underside | TowerPro dimension table. This is not proof of the user's servo dimensions. Ear thickness 2 mm, hole pitch 27.5 mm, shaft offset 5.2 mm and supplied horn geometry are assumptions requiring measurement. |
| Teyleten Robot Amazon B0GCW44FDL | **No exact component geometry**. Pink wireframe reserves 40 × 36 × 18 mm | Product picture shows XL63070 silk, while seller title specifies TPS63070. Mechanical drawing was unavailable. Reserved volume is a design allowance, not measured size. Revise it if the delivered PCB/inductor/wires exceed it. |
| Existing wallplate | Provisional single-gang 69.85 × 114.3 × 6 mm | Default inherited from earlier project, not measured from the photograph. This does not fit arbitrary jumbo plates or the office double-gang plate. |
| Existing rocker | 31.5 × 65 mm, front plane Z=10 mm | Visual proxy only. Measure travel, active surface height and contact force. |
| Soft contact pads | 3M SJ5302 nominal 7.9 mm diameter × 2.2 mm height | Existing project pad choice; requires two physical pads or a re-dimensioned suitable substitute. Not included in printable STL. |

Sources: [DAIERTEK Amazon listing](https://www.amazon.com/dp/B09N1GDWQ9), [previous holder research](https://github.com/eoinest/auto-switch/blob/main/docs/aa-holder-research.md), [WEMOS S2 Mini](https://www.wemos.cc/en/latest/s2/s2_mini.html), [official dimension PDF](https://www.wemos.cc/en/latest/_static/files/dim_s2_mini_v1.0.0.pdf), [TowerPro MG90S](https://towerpro.com.tw/product/mg90s-3/), [existing servo evidence](https://github.com/eoinest/auto-switch/blob/main/docs/component-sources.md), [converter listing](https://www.amazon.com/dp/B0GCW44FDL).

## How the mechanism works

The servo sits beside the rocker with its output shaft **parallel to the wall**. A dual-ended orange paddle rocks toward the upper or lower end of the switch, then returns to neutral. Contact pads are 26 mm from the axis. At 10° rotation, the end travel due to radius alone is about 4.5 mm; the rearward pad offset also affects its path. Neutral pad-to-proxy-rocker gap is approximately 3.7 mm. Actual rocker travel determines calibration.

The longer paddle reaches the ends of the rocker; it does **not** increase available pressing force for the same servo torque. Force is approximately torque divided by contact radius. Starting gently near neutral, limiting dwell and returning to neutral reduce the chance of peeling off the fixture. Adhesive load capacity, wall paint, servo stall behavior and frame strength have not been experimentally validated.

The supplied plastic horn remains on the servo spline with its original center screw. Two small fasteners attach the printed flange to that horn through adjustable slots at approximately ±7 mm radius. The center access hole allows the original center screw to be removed. Do not substitute an unverified screw thread into the servo. Verify horn thickness, fastener diameter and available arm holes before printing the paddle. It intentionally has no printed spline.

**The photographed wall is textured. The previously selected Command 17201 strips explicitly exclude textured walls: do not use them on this wall, and an adhesion trial does not override that restriction.** The printed wings are only generic mounting surfaces, not approval for adhesive installation. Use a separately supported bench fixture for this prototype until an external mechanical support or mounting product approved for the actual surface has been designed. Do not remove the wallplate or add screws into the electrical box to improvise support.

The two servo ear towers have clearance slots around 28.5 mm pitch, allowing the reference 27.5 mm hole pattern. Their screws need M2-size through hardware and nuts selected after the actual ears are checked. The wing backs provide broad surfaces for a future compatible mounting method. If removable adhesive is used on a manufacturer-approved smooth surface, arrange its pull tabs so they remain reachable. The assembly lifts away as a whole to restore full manual access; the narrow neutral paddle also leaves the rocker sides exposed.

## Electronics carrier

The black AA case rests on raised saddles with 0.7 mm nominal clearance per side. Two reusable straps feed through the adjacent slots to retain it; remove the straps for battery replacement. Keep straps clear of the lid catch, switch and wire exit after inspecting the delivered holder.

The S2 Mini rests at four PCB corners, with 20 mm between the carrier floor and the board underside for headers and female jumper plugs. The center is open and the antenna end is kept away from the battery. Corner geometry and strap position must be dry-fitted to the actual board; avoid pressing straps onto components or the antenna. The open top provides USB, boot and reset access. The detailed USB plug body and cable bend are not exact models.

The converter bay has adjustable tie slots and raised edge supports, **not source-matched mounting holes**. Fit a separate insulating support to the actual board, then retain it with ties/straps without loading components or solder joints. Verify clearance under the PCB and airflow around the inductor before powering it. Until dimensions are known, use the converter on the bench and do not treat the bay as ready to fasten the actual board.

Both carriers need independent support; attachment to the photographed textured wall remains unresolved. No fastener enters the electrical wall box and no mains wiring is modified. Carrier-to-carrier wiring is a route illustration, not an electrical schematic; use the S2-specific wiring diagram as the electrical authority.

## Prints and additional mechanical items

| STL | Purpose |
|---|---|
| `01_plate_fit_ring.stl` | Cheap outer plate fit check before the large chassis |
| `02_wall_chassis.stl` | Frame, adhesive wings and servo ear towers |
| `03_factory_horn_paddle.stl` | Moving paddle; uses stock horn and separate soft pads |
| `04_electronics_carrier.stl` | Open battery/S2/adjustable-converter tray |
| `05_battery_fit_ring.stl` | Check seller case outline plus 0.7 mm per-side allowance |
| `06_s2_outline_coupon.stl` | Check reference PCB outline plus 0.7 mm allowance |

Additional mechanical items: an external support appropriate to the mounting surface (Command 17201 strips are excluded on the photographed textured wall); two soft contact pads; reusable battery straps; board/converter retention ties with insulation where needed; two servo ear fasteners/nuts; two horn fasteners; original servo horn and original center screw. Exact lengths and threads are not established from the available photos. Existing electrical BOM components alone do not complete the mechanical assembly.

All parts fit within the Bambu A1's 256 mm build envelope. PETG is a reasonable prototype material; begin with the 2 mm coupons. Use adequate perimeters around the ear towers and inspect layer adhesion. Paddle export is rotated to place its broad side near the bed; slicer support review is still necessary for the flange and contact feet. Mesh validity is not proof of structural strength or support-free printing.

## Verification performed and required

The generator rejects non-manifold print meshes, disconnected printable pieces and nonpositive volume. It samples the paddle at every integer degree from −10° through +10° and checks the actual meshes for intersections with the printed chassis. It also checks the servo-body reference against the chassis. An independent Python reader checks every exported STL for exactly two incident triangles per edge, positive volume, bed placement and A1 size. These checks do not validate wall adhesion, servo force, real component tolerances or all possible wire collisions.

Before printing the full assembly, measure the plate width/height/projection, rocker face/travel, actual MG90S body/ears/shaft/horn, actual S2 outline and loaded header height, delivered battery case including its lid and switch, and converter PCB width/length/tallest component plus wire exits. Update `config.json` and regenerate. The office's two-gang design will need a separate measured frame; this revision intentionally prototypes one switch.
