# All revised pieces: V8 fit-test print

[Download the combined STL](generated/auto-switch-ALL-NEW-PIECES-v8-FIT-TEST.stl).

This combines the V7 battery carrier and its centered flat bar with the selected option C booster adapter, two retaining fingers and two seat shims. These are separate pieces arranged together on one Bambu A1 bed, not an assembled solid. Reuse the existing separate Command-strip wall bracket. Electronic reference objects and metal fasteners are excluded.

**The booster is a fit test.** Its PCB is assumed to be 16 × 30 × 1.2 mm; the thickness and underside have not been measured. Its end-center support/contact areas must be clear of components, pads and solder. The battery bar has zero designed vertical gap against a seller-nominal 19 mm case; the cradle retains its previous lateral clearance. These exports do not establish physical snugness.

Import in millimeters at 100% scale. All parts are oriented flat on the bed. Use by-layer printing; the layout is not checked for sequential/by-object printing. Keep the two small shims: they set the booster finger height. Printed fit and material tolerance still need checking against the unpowered board. If a finger presses on a component, solder or bends the board, do not tighten it to force a fit.

Fasteners: two M3×30 screws and two M3 nuts for the battery bar. See the [booster fit-test instructions](../booster-retention-v1/README.md) for its verified modeled screw stack and assembly. Existing ESP32 attachment remains two M1.6×16 screws and nuts.

The manifest records source hashes and each packed part. `independent-stl-audit.json` checks closed solids, contents, spacing, bed contact and A1 bounds. These are digital geometry checks, not a physical fit approval.

```sh
python3 hardware/cad/revision-print-v8/combine.py
python3 hardware/cad/electronics-retention-v4/verify_stl_independent.py hardware/cad/revision-print-v8/generated/parts hardware/cad/revision-print-v8/generated/auto-switch-ALL-NEW-PIECES-v8-FIT-TEST.stl
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/revision-print-v8/render_layout.py
```
