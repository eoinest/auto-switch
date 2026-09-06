# First print: servo actuator with two Command-strip pads

This is the current mechanical POC for **the single switch in the bedroom**. Electronics remain on the bench. The Blender file contains only the mount, moving paddle, MG90S/horn references, switch reference and two Command strip pairs. Older electronics-carrier files remain separate.

## Buy this strip size

[Command Narrow Picture Hanging Strips, white, 12 pairs, 17207-12ES — Amazon B09XJDK6RS](https://www.amazon.com/dp/B09XJDK6RS). Amazon displayed **$7.49** on September 5, 2026; its displayed 94116 location offered September 6 delivery with Prime. Verify the selected **Narrow** variant and delivery at checkout. Nothing was purchased.

Use **two mating pairs total**, one on each side: **four individual strips**. These are the click-together picture-hanging fasteners, rather than replacement adhesive strips for hooks.

[3M's current 17207 specification](https://www.command.com/3M/en_US/p/d/b5005604166/?bvstate=pg%3A3%2Fct%3Ar) lists a 3.651 × 0.498 inch outline, approximately **92.74 × 12.65 mm**. Its published 0.1-inch thickness does not establish the installed, compressed thickness of a mating pair. That spacing is provisionally modeled as **4 mm** and must be measured. An [older 3M catalog sheet](https://media.digikey.com/pdf/Data%20Sheets/3M%20PDFs/17207.pdf) gives approximately 3⅝ × ½ inch, consistent with the reserved outline. Package generations can differ: check the delivered strips without trimming them.

Each printed rear pad is **14.5 × 96 mm**, leaving about **0.93 mm per side and 1.63 mm per end** around the published strip outline. The pad centers are 53.5 mm apart. Each pad is continuous and flat: no holes, raised lettering or recess edges under its adhesive.

## Where they stick

Both pairs sit on the **smooth front of the switch plate**, alongside the rocker. The earlier wings that reached onto the wall have been removed. The servo extends a little beyond the right edge, but its mounting load goes through the two plate-facing pads.

The full adhesive footprint must lie on a clean, flat, suitable surface, clear of the beveled edge and the rocker bezel. The room's actual plate has not been measured, so the model does **not** establish that this space is available. Its provisional plate outline is 69.85 × 114.3 mm; assumed bezel is 35 × 70 mm. The opening between pads is 39 mm wide and between crossbars is 72 mm high. If the fit test bridges a bevel, rocks, or touches the rocker bezel, revise the dimensions before using adhesive or printing the full mount.

The photographed office wall is textured. 3M excludes textured/rough surfaces for these strips. Smooth printed plastic also needs an adhesion trial; an FDM surface and an oscillating servo are not covered by a picture-weight claim. **Two pairs are the requested arrangement, not a verified servo-force rating.** Do not extrapolate the package's four-pair hanging rating into a peel-force limit.

Follow the [3M installation/removal instructions](https://www.command.com/3M/en_US/command/how-to-use/picture-hanging-strips/) and supplied package, including cleaning, pressing and the waiting period. Point both pull tabs down. Unclick and remove the entire actuator to expose them, then stretch the tabs down along the plate as instructed; there is no enclosing skirt below them. Check this removal route before sticking anything. Do not cut the strips or glue over their tabs.

## Files and print order

1. **[01_plate_and_strip_fit_test.stl](../hardware/cad/servo-command/generated/01_plate_and_strip_fit_test.stl)** — 68 × 96 × 1.2 mm thin template. Print this first, then hold it over the existing plate without adhesive. Check both pad regions against the flat surface and confirm the rocker moves freely through the opening. Test the actual strips against the printed pads with liners still on.
2. **[02_servo_mount.stl](../hardware/cad/servo-command/generated/02_servo_mount.stl)** — 73 × 96 × 29 mm mount and servo ear towers, after the template fits.
3. **[03_factory_horn_paddle.stl](../hardware/cad/servo-command/generated/03_factory_horn_paddle.stl)** — 22.1 × 60 × 17 mm in its exported print orientation. Attaches to the supplied servo horn; it has no printed spline.

[Blender assembly](../hardware/cad/servo-command/generated/servo-command.blend) · [front view](../hardware/cad/servo-command/generated/assembly.png) · [rear pads](../hardware/cad/servo-command/generated/rear-pads.png) · [parameters](../hardware/cad/servo-command/config.json).

Import STL in **millimetres, at 100% scale**. The template lies flat and needs no supports. A 0.4 mm nozzle and 0.2 mm layers are a reasonable starting point; six layers make the 1.2 mm template. PLA is sufficient for checking fit. For the full mount, use your calibrated material profile, four walls and approximately 30% infill as a starting point. Inspect the slicer's preview around the horizontal servo screw slots and paddle flange; the paddle may need supports. These are starting settings, not a tested print profile. All three files fit the Bambu A1 envelope. No print job has been sent.

## Servo assembly and remaining checks

The model retains the TowerPro MG90S reference case dimensions **22.8 × 12.4 × 28.4 mm**, with 32.5 mm base-to-shaft-tip and 32.1 mm mounting-ear span. See [TowerPro](https://towerpro.com.tw/product/mg90s-3/) and [the earlier dimensions table](s2-aa-mechanical.md). The user's exact servo, supplied horn, ear-hole pitch and ear thickness still require dry fitting. The assumed ear-hole pitch is 27.5 mm, ear thickness 2 mm, and horn hole positions are adjustable slots.

Additional physical items: stock horn and stock center screw; two servo ear screws/nuts of a size matching the actual ears; two horn-to-paddle fasteners; two soft contact pads (currently 7.9 mm diameter × 2.2 mm reference). Fastener lengths and horn threads have not been confirmed. Retain the supplied center screw rather than forcing a generic screw into the servo.

The axle stays at the previous 31 mm wall-relative height. The new adhesive/base spacing is accommodated by shorter towers, preserving the illustrated paddle path. Once the real mating-pair thickness and switch projection are measured, adjust spacing or contact depth as needed. Press Space over Blender's 3D view for the illustrative ±10° movement. Do not force an unpowered servo through its gears or use the animation as a calibrated endpoint.

## Verification

The Blender generator checks closed, single-piece printable meshes and samples paddle-to-mount collisions at each integer angle from −10° through +10°. It checks the reference servo body, plate and bezel against the mount and verifies strip outline margins. The independent STL reader checks closed edges, positive volume, bed placement and A1 size. All pass. This does not prove physical fit, continuous-motion clearance, adhesive durability, servo force, or successful switching.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/servo-command/generate.py
python3 hardware/cad/servo-command/verify.py
```
