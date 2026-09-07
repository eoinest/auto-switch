# V6: one simple battery crossbar

This preview uses **one horizontal bar and the two equal-height upper towers already printed in the V4 carrier**. The unused lower pair remains in place. No adjuster screws or pressure shoes are needed.

The ends sit on the existing Z26 tower tops. The bar's front is flat at Z29. An integral center land reaches down to Z22.2: the 3 mm carrier base plus the seller's **nominal 19 mm case body**, plus **0.2 mm clearance**. That is a preview dimension, not a promise of exact tightness; the delivered case and print tolerances still determine fit.

- [Single crossbar preview STL](generated/battery-retention-v6-SINGLE-CROSSBAR-PREVIEW.stl)
- [Assembly preview](generated/battery-retention-v6-assembly.png)
- [Print orientation](generated/battery-retention-v6-print.png)
- Corresponding Blender files and `validation.json` are in `generated/`.

Print the bar with its full flat front face on the bed, as exported. Its overall dimensions are **96 × 10 × 6.8 mm**. Reuse **two M3×35 screws and two ordinary M3 nuts** on the upper tower pair at Y−12. The new bar leaves the lower-right power switch exposed and stops short of the illustrated upper-right wire corridor. The original carrier is excluded from the STL and is unchanged.

The one bar does not eliminate horizontal play in the cradle; the existing V5 shims remain optional. Remove the bar to lift out the holder. Check switch access, insulated-wire routing and whether the small nominal vertical clearance feels acceptable before treating this as a final fit.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/battery-retention-v6/generate.py
```
