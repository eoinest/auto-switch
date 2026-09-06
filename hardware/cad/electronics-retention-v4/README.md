# V4: flat carrier and separate Command-strip bracket

This revision separates the mounting structure into two printed pieces: the flat-bottom electronics carrier and one H-shaped wall bracket. The four integrated v3 feet are removed. Existing battery bars, converter floor, and converter jaws are preserved, so the complete print contains **seven pieces**.

Use [`generated/electronics-wall-mount-ALL-PIECES-v4-CONCEPT.stl`](generated/electronics-wall-mount-ALL-PIECES-v4-CONCEPT.stl) for printing. All seven pieces are oriented on Z=0 and spaced within a 245 × 228 mm footprint on the A1's 256 × 256 mm bed. This leaves 5 mm at the closest bed edges; adjacent part envelopes have a minimum 5 mm gap, so use no more than a 2 mm brim in this layout and inspect slicer placement. The assembled STL is for assembly visualization, not print-in-place.

## Wall attachment

- Two continuous rear pad faces, **20 × 144 mm each**, accept one mating pair of narrow Command 17207 strips per pad. The previously recorded strip outline is 12.65 × 92.74 mm. The long pads leave room to position the removal tabs at the lower edge.
- Carrier underside is Z=0; bracket rear adhesive face is Z=-13 mm. Pads are 3 mm thick, and four standoffs rise 10 mm from their front faces.
- Four attachment centers are X=±53, Y=±65 mm, clear of the existing component fasteners.
- Use **four M3 × 12 mm machine screws and four ordinary M3 nuts**, without washers. Screws enter from the carrier front through 3.4 mm clearance holes.
- Insert nuts into the inward-facing side slots before fitting the carrier. The 6 mm-wide slots constrain ordinary 5.5 mm-across-flats M3 nuts against rotation. Slot height is 2.8 mm; the nominal nut is 2.4 mm thick.
- The screw clamps the carrier and the 4.6 mm-thick roof above each nut. A 12 mm screw ends at Z=-9, inside the blind standoff bore, leaving 4 mm before the rear adhesive plane. The deepest existing component screw ends at Z=-6, leaving 4 mm to the bracket's pad fronts and 7 mm to its rear plane.
- Remove the carrier before removing Command strips so the stretch-release tabs are accessible. Pull according to the strip manufacturer's instructions along the wall, not outward. No adhesive thickness or published strip weight rating is treated as a guarantee against servo force or peeling.

## Electronics assembly fasteners

| Fastener | Quantity | Use |
|---|---:|---|
| M1.6 × 16 mm screws | 2 | S2 mounting holes and standoffs |
| M1.6 nuts | 2 | S2 mounting screws |
| M3 × 35 mm screws | 4 | Battery retaining bars |
| M3 × 10 mm screws | 4 | Converter floor and jaws |
| M3 × 12 mm screws | 4 | New carrier-to-wall-bracket attachment |
| M3 nuts | 12 | Eight component screws and four bracket screws |

No washers are included in these stacks. Servo mechanism fasteners are separate.

## Printing

The carrier's entire 120 × 160 mm underside lies on the bed; no supports are needed under a suspended base floor. The bracket prints with both adhesive pad faces directly on the bed. Its nut-pocket roofs require approximately **6 mm bridges**; inspect bridging in the slicer rather than enabling support inside nut cavities. Existing converter jaws lie on their sides and retain a 1 mm recess that may need local support; this revision does not claim every retained component is entirely free of support requirements.

Keep adhesion faces flat. Dry-fit screws, nuts, and purchased components before loading the wall mount. Component fit remains a concept: the converter's 40 × 36 mm envelope is still an unmeasured placeholder, and actual PCB edge clearances, holder protrusions, and S2 underside solder joints need physical checking.

## Files and regeneration

- `generated/electronics-print-layout-v4.blend`: seven printed pieces, laid out for the A1.
- `generated/electronics-retention-v4.blend`: assembly, including non-printable reference electronics and screws.
- `generated/stl-concept/`: individual printed pieces.
- `generated/export-manifest.json`: dimensions, placement transforms, STL hashes, and geometry checks.
- `generated/assembled-v4.png`, `rear-pads-v4.png`, `print-layout-v4.png`: visual reviews.

Run from the repo root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python hardware/cad/electronics-retention-v4/generate.py
```

This generator produces only printed geometry in both STL exports. Hardware references never enter the print files. The original v3 files are preserved.

Run the independent binary-mesh and layout audit after generation:

```sh
python3 hardware/cad/electronics-retention-v4/verify_stl_independent.py hardware/cad/electronics-retention-v4/generated/stl-concept hardware/cad/electronics-retention-v4/generated/electronics-wall-mount-ALL-PIECES-v4-CONCEPT.stl
```
