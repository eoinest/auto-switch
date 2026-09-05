# Mechanical prototype: externally mounted rocker actuator

The photo shows two **Decora-style / decorator paddle rocker switches in a two-gang wallplate**. “Decora” is Leviton's trademark; “decorator rocker” is the useful generic search term. A matching single switch is “one gang.” Gang count describes the number of devices; it does not identify single-pole versus three-way wiring. The photo cannot establish manufacturer, dimensions, or wiring type.

This is a first-fit prototype, **not a measured replica or a proven snug fit**. It preserves the existing wallplate and uses low-voltage parts entirely outside it. Do not remove the plate or insert fasteners behind it to attach this prototype.

## Delivered design

`hardware/cad/config.json` is the dimension source. `generate.py` builds the scene, exports binary millimetre STLs, checks mesh topology and connectedness, and renders the assembly. `generated/auto-switch.blend` contains both sizes side by side; objects prefixed `PRINT` are fabricated parts, and `REFERENCE` objects are envelopes for bought parts. Hidden fit rings and enclosure lids remain available in the Outliner. The preview leaves lids hidden to explain component placement. Play Blender’s timeline (frames 1–100) for an illustrative ±10° upper/lower yoke cycle; this is a motion demonstration, not calibrated firmware angles.

- A rectangular surround clears the existing plate by 0.7 mm per side. It has a 9 mm skirt, broad 20 × 78 mm external adhesive lands, and an integrated top enclosure. It locates around the plate; adhesive provides retention. There are deliberately no guessed snap hooks behind the plate.
- An MG90S lies sideways with its shaft horizontal, parallel to the wall. The one-gang unit uses a right-hand servo; the two-gang unit uses outward-facing left and right servos. The fixed servo body sits in a cradle, retained with two narrow cable ties through four holes, with thin foam as needed. This avoids assuming mounting-ear geometry shared by all MG90S clones.
- A two-ended yoke attaches to the **supplied servo horn**, using two small screws through the printed flange. The servo's original centre screw secures the horn to the spline; a 4.4 mm central access hole lets a screwdriver reach it. No printed spline is required. The provisional attachment holes are 2.2 mm diameter, 14 mm apart; measure your horn, adjust the JSON radius, and use compatible short screws. Fasteners must not contact the servo body. A single-arm supplied horn requires a matching flange redesign or a compatible double-arm horn.
- Two posts under the yoke carry 8 × 8 × 2 mm silicone/foam pads. A small rotation presses the upper or lower end, followed by a return to neutral and servo power-off. Soft pads take up small errors; they are not a certified force limiter.
- The enclosure holds a bought battery holder, a Pico W/2 W with headers, and power electronics. Raised rails give clearance below the Pico; cable ties retain it. The lid uses four M3 × 8 mm screws into 2.5 mm printed pilot holes; check the fit on a small offcut before threading PETG. No printed part is a battery contact. Keep wiring insulated and use suitable standoffs or insulation under converter/load-switch boards.

## Starting dimensions and what to measure

| Feature | Provisional CAD value | Required measurement |
|---|---:|---|
| One-gang outer plate | 69.85 × 114.3 mm | Actual widest width and height, including curved edges |
| Two-gang outer plate | 115.9 × 114.3 mm | Actual width/height; midway and oversize plates differ |
| Two-gang centre spacing | 46.0 mm | Centre-to-centre between rocker paddles |
| Plate surround clearance | 0.7 mm each side | Printer accuracy, plate taper and paint build-up |
| Existing plate reference thickness | 6 mm | Maximum height above wall under each servo bridge |
| Rocker face reference | 31.5 × 65 mm; surface 10 mm from wall | Width, height and both end heights in both positions |
| Servo envelope | 24 mm axial × 22.8 mm long × 12.2 mm wide | Actual body, output shaft, horn and cable exit |
| Servo pivot | 30 mm above wall; 26 mm pad radius | Gap after adhesive and silicone are fitted |
| Enclosure internal clearance | 96 × 116 × 34 mm | Chosen holder, converter, wiring and connectors |
| Battery holder reference | 64 × 60 × 22 mm | Exact purchased 4AA holder (Pololu 1153 is 63 × 58 × 16 mm in this orientation) |
| Pico/header envelope | 51 × 21 × 18 mm | Actual soldered headers and connector bend room |
| Converter reference | 43 × 21 × 10 mm | Chosen regulator; lateral room also reserved for load switch |

The plate dimensions are common reference sizes from [Leviton's wallplate dimensional drawings](https://leviton.com/content/dam/leviton/commercial-industrial/product_documents/product_specification/Q-874A%20Special%20Purpose%20Wallplates%20PB.pdf), not dimensions inferred from this photo. [TowerPro lists the MG90S as 22.8 × 12.2 × 28.5 mm overall](https://towerpro.com.tw/product/mg90s-3/); our separate body/shaft envelopes are approximate and must be checked on your servos. The term “all metal” often describes the gear train, not the external case or supplied horn.

Measure the wallplate while it remains installed. A ruler is sufficient to choose the initial preset; calipers help refine the fit. First print only the appropriate `1g_fit_ring.stl` or `2g_fit_ring.stl`. This 2 mm thin ring checks the maximum outer outline cheaply; it does not verify the 9 mm skirt depth, servo clearance, or rocker movement. If necessary, edit the dimensions and regenerate. Never scale the whole STL to adjust the plate: that would also scale the servo, screw and electronics features.

## Why the yoke works, and what a longer lever changes

For servo torque τ and pad radius r, tangential force is approximately **F = τ/r**. A longer servo arm gives more travel and reaches the paddle ends, but reduces available force. Pressing near the paddle ends independently reduces the force needed to operate the switch, compared with pressing near its pivot.

TowerPro's 1.8 kgf·cm stall figure at 4.8 V corresponds to about 0.176 N·m. At a 26 mm radius that is roughly 6.8 N (about 0.69 kgf) at stall, before geometry and losses. Stall is a limit, not a sensible operating target. Measure your switch's required force with a small force gauge or spring scale on a disconnected spare switch if possible, and keep comfortable margin. Clone performance may differ.

The model's neutral silicone tips are around 13 mm from the wall, versus a nominal 10 mm rocker surface. At 15° rotation the descending contact reaches roughly 6.6–7 mm from the wall and shifts along the paddle. This is a geometric starting point only: actual end height, adhesive thickness, pad compression and switch travel determine the pulse positions. **Do not copy 15° as a calibrated pressing angle.** Start at neutral, advance in tiny increments, and stop immediately after the switch clicks. The mirrored left and right units may require opposite software directions.

Adhesive still sees the reaction force from every press. A long arm does not remove it. The wide surround and wall pads distribute that force; a short press, neutral return, correct travel, and compliant contacts reduce unnecessary loading. The CAD does not promise adhesive retention on this textured painted wall. Use removable strips rated for your surface, follow their application/cure instructions, leave their removal tabs reachable, and test with the enclosure supported so a failed bond cannot fall. Strip thickness shifts the entire mechanism forward; recheck the gap after mounting. The enclosure's large flat back can provide additional adhesive area if needed. A redesigned external clamp is preferable if the surface will not retain adhesive reliably.

## Print and assemble

The largest exported part is under 256 mm in every axis, matching the [Bambu A1's 256 × 256 × 256 mm build volume](https://cdn1.bambulab.com/documentation/quick-start-a75adcb1d5d5e/Quick%20Start%20Guide%20for%20A1.pdf). The chassis is about 237 mm tall, so slice it individually and inspect bed margins/brim clearance. Dimensions in `generated/validation.json` are authoritative for the current configuration. The top enclosure is intentionally spacious for a first prototype; after selecting components and measuring, it can be made smaller.

1. Print the thin fit ring first in PLA. Confirm that it passes over the installed plate without force and that the switch centres match. Record the actual dimensions in the configuration.
2. Print the chassis flat back down. PETG is a reasonable final prototype material; a 0.2 mm layer, 4 perimeters and 25–35% infill are starting slicer settings. The raised servo bridges need local support from the bed. Inspect the slicer's layer preview and support placement before printing. No G-code is supplied because material and nozzle setup are user-specific.
3. Print the yoke in its supplied side orientation. Supports may be needed beneath the offset hub/bridge. Inspect hole orientation and layer adhesion around the hub; ream holes gently rather than forcing screws. Print the lid flat.
4. Test the servo, horn, cable ties and yoke off the wall first. Power the servo at neutral before fitting the horn. Attach the horn to the yoke and centre screw to the servo. Add compliant contact pads and ensure both ends clear at neutral.
5. Trial-position the assembled chassis over the installed plate before sticking it down. Check that the servo pedestals clear the plate and that the yoke cannot strike the frame through the small intended motion range. Route cables away from the horn and leave the original switch edges accessible.
6. Fit batteries, board and converter with insulated mounting. Establish neutral and very conservative press positions. Support the unit during initial mounted tests and verify that every command returns to neutral. Only then enable the software for normal use.

The narrow yoke leaves paddle edges accessible, but fingers and individual plates vary. Verify manual switching while the yoke is neutral. If power is lost with the yoke pressing, disconnect servo power and remove the horn or externally attached assembly; do not force the switch against stalled gears. This prototype has no spring-return clutch and no closed-loop force sensing.

## Regeneration and validation

From the repository root on this Mac:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python hardware/cad/generate.py
open -a /Applications/Blender.app hardware/cad/generated/auto-switch.blend
```

Blender is suitable for these deliverables because dimensions are generated from code and the editable `.blend` is included. FreeCAD is a free alternative worth considering for later constraint-driven mechanical revisions; it is not needed to reproduce this repository.

Run `python3 hardware/cad/verify_stl.py` for the independent exported-file checks; results are saved in `generated/stl-verification.json`. All nine supplied STLs passed manifold-edge, positive-volume, print-bed origin and A1 bounding-box checks.

The generator checks that each printable has zero non-manifold edges, one connected component and positive enclosed volume, and exports triangulated binary STLs. It reports bounding boxes in millimetres. This checks digital mesh integrity, not measured fit, print strength, full motion collision, servo torque, adhesive durability or electronics temperatures. The render is a design preview rather than a photograph of a built device. Those remaining checks require physical components and the fit/calibration steps above.
