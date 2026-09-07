# V7: two centered towers and one flat bar

This revision **reprints the carrier**. All four old battery towers and their holes are removed. Only two towers remain, centered beside the holder at X ±43 mm, Y −32 mm. Existing S2, converter and wall-bracket attachment geometry stays in place.

The seller lists the battery case body as **19 mm thick**; its switch protrudes another 3.5 mm. The case sits on the 3 mm base. Both new tower tops and the flat bar underside are therefore **Z22 mm**, with **zero designed vertical clearance**. The bar rests directly on the nominal case and towers. Actual molded dimensions and printing tolerances still need a dry fit; do not force a thicker case under the bar.

- [Combined new carrier and bar STL](generated/battery-retention-v7-NEW-CARRIER-AND-BAR.stl)
- [Carrier alone](generated/01_NEW-CARRIER-v7.stl)
- [Flat bar alone](generated/02_FLAT-CROSSBAR-v7.stl)
- [Assembly](generated/battery-retention-v7-assembly.png)
- [Print layout](generated/battery-retention-v7-print-layout.png)

Both pieces are flat on the bed in the exports, in millimeters. The carrier is 120 × 160 × 22 mm; the bar is 96 × 10 × 3 mm. The combined layout fits a 256 × 256 mm A1 bed. It includes only these two revised pieces; reuse the separate wall bracket. The converter retainers still require verification against the actual board before reuse.

Use **two M3×30 screws and two ordinary M3 nuts** for the battery bar. Your WEIDEER kit B0DS8HYF64 includes M3×30 screws, so no additional fastener order is needed ([seller assortment chart](https://m.media-amazon.com/images/I/71Ddx5vNT7L._SL1500_.jpg)). The screw head bears at Z25 and its tip ends at Z−5, below the nut but ahead of the wall-bracket pad. The previous M3×35 screws are too long for this shorter stack. Remove the bar to lift out the battery holder. Switch and upper-right cable access remain open. The original cradle's horizontal clearance remains; existing V5 shims are optional for lateral play.

`config.json` drives case thickness, both tower heights and the bar position together. The generator checks closed connected printable meshes and absence of all four old posts. Independent review files record saved-mesh checks. This revision does not establish the fit of the previously modeled converter placeholder.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/battery-retention-v7/generate.py
```
