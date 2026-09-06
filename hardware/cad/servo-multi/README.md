# Double and triple switch actuators

These mechanical concepts extend the user-confirmed single-switch fit to nominal **46 mm gang centers**. They leave the original single model unchanged. Actual double/triple plate fit, travel and adhesive capacity have not been tested.

Each rocker has its own MG90S. The double mount points both servos outward. The triple points the outer servos outward and raises the center servo axis by 30 mm, avoiding the adjacent paddle. Its longer center contact legs have closer-spaced tips so they stay over the intended rocker during the modeled motion.

## Files

Each `generated/double/` and `generated/triple/` directory contains:

- `double-ALL-PIECES-CONCEPT.stl` or `triple-ALL-PIECES-CONCEPT.stl`: all separate printable parts on one A1 bed, in millimetres.
- Numbered individual STLs, retaining the same print-layout XY positions.
- `*-assembled-CONCEPT.blend`: installed arrangement, with reference-only plate, servos, stock horns and soft pads.
- `*-print-layout-CONCEPT.blend` and `print-layout.png`: print orientations.
- `assembly.png`, `validation.json`, and `independent-stl-audit.json`.

See the [independent review](independent-review.md) and [dimension sources](sources.md) for the checks and their limits.

The double set has **five printed pieces**: frame, two screw-on saddles and two paddles. Triple has **seven**: frame, three saddles and three paddles. These are separate objects in the master STL, not print-in-place assemblies.

## Attachment and printing

The frame has two uninterrupted **14.5 × 116 mm rear landing pads**, one at each outside edge. Each accepts one mating pair of Command 17207 narrow strips. There are no inter-gang adhesive pads: the approximately 11 mm gap between assumed bezels is too narrow for the full strip outline. The centered strips sit behind the frame. To remove wall-side strips, first separate the interlocking pairs and lift away the frame, then stretch-release each wall-side tab according to the manufacturer instructions; do not glue the two halves together. Plastic projects 0.85 mm past each top/bottom edge of the nominal plate, while the centered 92.74 mm strip outline stays on the plate. Mated strip thickness remains an assumed 4 mm.

The frame prints with its entire rear face on the bed. Servo saddles print separately, foot down, and bolt to the frame after printing. The paddles print broad side down and include a 45-degree transition beneath the horn flange. Saddle ear holes are horizontal 2.2 mm bores with short bridges; inspect the slicer preview before printing. No tall chassis overhang is needed. The original single-switch paddle file has not been modified.

Saddle screws sit at **Y = ±54 mm**, beyond the entire strip outline. Their heads are on the front of the saddle, and ordinary nuts go behind the frame. Assemble and tighten these before attaching strips. The nominal stack is 4 mm saddle + 3 mm frame + 2.4 mm nut. An M3×10 screw extends approximately 0.6 mm beyond the nut and stops 1 mm above the nominal plate face. Omit washers for this length; verify actual screw/nut and strip thickness before sticking the frame down.

| Item | Double | Triple |
|---|---:|---:|
| MG90S, with original horn and center screw | 2 | 3 |
| M3×10 saddle screws | 4 | 6 |
| Ordinary M3 nuts | 4 | 6 |
| M2×10 servo-ear screws | 4 | 6 |
| Ordinary M2 nuts | 4 | 6 |
| Command 17207 mating pairs | 2 | 2 |
| Soft contact pads, 7.9 mm diameter × 2.2 mm | 4 | 6 |

Horn-to-paddle fasteners still depend on the supplied horn's actual holes; the model retains the single design's adjustable two-hole arrangement. Do not substitute a printed spline for the stock horn.

## Verification limits

The generator checks each paddle against the frame, all saddles and servo envelopes at every integer angle from −10° through +10°. It also checks all independent combinations of paddle angles, rather than rotating every channel together. All printable parts must be watertight, one connected component each, positive volume and packed within the A1 bed. These checks do not prove adhesive peel strength, actual switch travel, servo force or printed stiffness.

The original outer contact geometry is retained: axis Z31, contacts Y±26, soft-pad bottom Z13.7. Its nominal circular-pad edge only barely fits the assumed 65 mm rocker at the worst sampled angle. This needs a real multi-plate travel check despite the single fit confirmation. The triple center changes to axis Z61, contacts Y±19, soft-pad bottom Z12; this keeps its complete soft-pad contact footprint inside the modeled rocker while reaching approximately the same press depth as the outer mechanism. Long center legs and posts need physical stiffness testing.

These models do not change the one-servo firmware or certify the existing battery/converter for two or three simultaneous servo loads. Multi-channel controls and power sizing are separate work.

## Regenerate

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/servo-multi/generate.py -- double
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/servo-multi/generate.py -- triple
```

Run `python3 hardware/cad/servo-multi/verify_stl_independent.py` to independently check the exported files against the master layouts.

The generator only replaces its own variant exports. `config.json` records nominal plate dimensions and the source single-config path. `validation.json` records the source hash.

Plate references: [Leviton wallplate size guide](https://leviton.com/content/dam/leviton/commercial-industrial/product_documents/solution_sheets/Wallplate%20Size%20Guide%20Q-1289.pdf), [Leviton dimensional drawing](https://leviton.com/content/dam/leviton/residential/product_documents/product_specification/Q-874A%20Special%20Purpose%20Wallplates%20PB.pdf). Strip reference and original MG90S envelopes remain in `../servo-command/config.json`.
