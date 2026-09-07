# V5 replacement battery retention

This replaces the two broad V4 battery bars while **reusing the printed carrier, wall bracket and four M3×35 mounting screws/nuts**. Two narrow fixed edge rails leave the switch face open. Each rail has a screw-adjusted, guided pressure shoe; removable shims take up sideways play against all four cradle walls.

The seller's dimension photo distinguishes the **19 mm case body** from the **22.5 mm height including the switch**. The old bars stopped at Z26 above a case face at Z22, explaining approximately **4 mm vertical slack**, rather than the previously assumed 0.5 mm. The nominal cradle also leaves **1.4 mm total play in each horizontal axis**. See `photo-measurements.json` for the photo reconstruction and its limits.

## Print these replacements

- [All replacement pieces in one STL](generated/battery-retention-v5-REPLACEMENT-ALL-PIECES.stl): **16 pieces** — two rails, two pressure shoes and four each of the 0.4, 0.6 and 0.8 mm tabbed shims.
- Numbered individual STLs are also in `generated/`; print four copies of each shim file if using individual exports.
- [Assembly preview](generated/battery-retention-v5-assembly.png)
- [Print layout](generated/battery-retention-v5-print-layout.png)
- The two `.blend` files preserve both views. The existing carrier in the assembly is reference-only and is excluded from all replacement STLs.

Rails are oriented with their broad front faces flat on the bed. Their bottom-loaded nut recesses print without a suspended roof because the model is inverted. The mounting-screw counterbores still narrow from 6.4 to 3.4 mm, leaving a short, approximately 1.5 mm radial shoulder bridge. Pressure shoes lie on their open C-shaped ends; the small blind screw-tip recess may also require a short bridge in the slicer. Shims print blade-flat, minimum thickness 0.4 mm, with a raised grip at one end. Use a layer height that preserves these thin shims and inspect the sliced first layers.

Import the master in **millimetres at 100% scale**, keeping its existing part orientations. Use **0.2 mm layers** so the three shim thicknesses are whole layer counts, and print **by layer**, not sequentially by object. Preview the small bridges and confirm that the 0.4 mm shim blades contain two layers before starting.

### Identify the shim sizes

The master STL has no embossed size labels. **Keep its original arrangement and mark the shim grip tabs before lifting them off the bed.** Viewed straight down, with the long rails running vertically and the two shoes below their central arms, the rows read left to right:

```text
Back row:     .8   .8   .8
Middle row:   .4   .4   .6   .6   .6   .6   .8
Front row:    rail  shoe  rail  shoe        .4   .4
```

The front row starts at print Y8, middle at Y67, and back at Y83.6 mm. Numbers are shim thicknesses in millimetres. If the slicer rearranges the pieces, use the individually named shim STLs instead and print each size as its own labeled batch; the arrangement above will no longer identify them.

## Fasteners

| Item | Quantity | Status |
|---|---:|---|
| M3×35 mounting screws | 4 | Reuse |
| Ordinary M3 mounting nuts | 4 | Reuse |
| **M3×10 adjustment screws** | **2** | Additional, from the existing M3 kit |
| **Ordinary M3 adjustment nuts** | **2** | Additional, from the existing M3 kit |

No washers are modeled. The reused mounting screws still bear at **Z29**, inside shallow counterbores. The new nuts load from **underneath** each central arm and bear upward against a **2 mm fixed roof**. The printed shoe has a **blind screw-tip seat** leaving 1.2 mm of plastic between the metal tip and the battery case. Its guide walls and retaining lips prevent ordinary sideways wandering and downward loss while installed; keep the screw tip engaged in its seat during use.

## Assemble and adjust

1. Disconnect battery power. Remove the old bars and lift out the holder.
2. Put the holder back **switch facing outward**, oriented as shown: switch near the lower-right corner and the wire exit near the upper-right edge. The old center-bottom wire notch does not line up with this orientation. Route insulated leads above the low right cradle wall, away from the post and shoe; the actual cable exit height still needs checking.
3. Try thin shims at the four cradle edges. A 0.6 + 0.6 mm pair leaves about 0.2 mm nominal clearance per axis; a 0.6 + 0.8 pair fills the nominal 1.4 mm gap. Choose the combination that stops rocking **without forcing the case into the cradle**. Grip tabs project outward above the walls and remain accessible.
4. Insert one M3 nut into the underside recess of each rail's central arm. Thread its M3×10 screw from above to retain the nut. Keep the tip retracted above the pressure shoe until the shoe is aligned.
5. Install the rails using the four original M3×35 screws and underside nuts. The rails seat on the existing posts.
6. Slide each pressure shoe onto the free inner end of its rail arm, resting its broad pad on the case. Center the blind recess under the adjustment screw.
7. Turn each adjustment screw only until play stops. **Do not crush the case.** The screw tip must enter the shoe's blind seat and must never bear directly on the battery holder. The two adjustment screws can accommodate nominal case-body heights from 18.5 to 20.5 mm.

For battery service, remove both rails to lift the holder out. Simply loosening the adjustment screws does not make the overhanging arms disappear. The shoes are intentionally removable through the open ends for assembly and retrieval; hold them when removing a rail or completely withdrawing an adjustment screw.

## Verification and remaining checks

The generator validates each printable as one connected, watertight, positive-volume solid. It checks the pressure shoes against the fixed rails at nine body heights across **18.5–20.5 mm**, and checks new rails/shoes against the photo-based **18 × 22 mm switch access window**. No new rail occupies the modeled upper-right wire corridor. The existing posts remain close to the outside edge of the switch access window; physical finger access still needs a dry fit.

Seller dimensions and photo-derived switch coordinates are not a precision measurement of the delivered holder. Cover seam and wire stubs are illustrative; wire exit height, molded corner shape and printed clearances remain physical checks. The original V4 carrier files are unchanged.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/battery-retention-v5/generate.py
```
