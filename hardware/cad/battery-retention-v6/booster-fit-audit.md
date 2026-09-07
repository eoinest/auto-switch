# Buck-boost PCB retaining-clip audit

Reviewed 2026-09-07. **The current L-shaped clips are not verified to fit the purchased converter. No converter CAD was changed by this audit.**

## Actual part evidence

The selected item is [Teyleten Robot, Amazon B0GCW44FDL](https://www.amazon.com/dp/B0GCW44FDL), the 5 V buck-boost module listing titled TPS63070. The listing text and four seller detail photographs were inspected. None supplied a mechanical outline, PCB thickness, dimensional tolerances, or populated height. Its photographed PCB is labeled XL63070. Photos show solder pads and components near board edges; the pictured unsoldered underside has pads/traces, without large mounted components. User-added solder and wires will change those clearances. These images do **not** establish physical measurements or a usable clamping zone.

Seller images inspected: [angled top](https://m.media-amazon.com/images/I/71qDJNk9I+L._AC_SL1500_.jpg), [opposite angle](https://m.media-amazon.com/images/I/61B96kvdgDL._AC_SL1500_.jpg), [top detail](https://m.media-amazon.com/images/I/71s7e56PAbL._AC_SL1500_.jpg), [underside](https://m.media-amazon.com/images/I/61OZry9F3fL._AC_SL1500_.jpg).

The [TI TPS63070 product documentation](https://www.ti.com/product/TPS63070) describes an integrated circuit. Its package drawing is **not** a drawing of this seller's assembled board. An IC package height, the large inductor height, PCB substrate thickness, and total assembled module height are different dimensions. None can be substituted for another in the clip design.

**Exact PCB length, width, thickness, populated height, and clamp-safe edge areas remain unknown.** Similar-looking modules and generic 1.6 mm PCB conventions are not adequate evidence for this purchased unit.

## What the current CAD actually captures

Authority: `hardware/cad/electronics-retention-v4/generate.py`, converter cassette section, especially lines 84–95; associated `config.json`. Coordinates below are assembly Z, in millimetres.

| Feature | Current geometry | Implication |
|---|---:|---|
| Lower supporting shelf | Z 6–8 | PCB underside is supported at Z 8 |
| Upper retaining lip | Z 10–12 | Lip underside is at Z 10 |
| Clear throat between shelf and lip | **2.0 mm** | This is the thickness the PCB must fit into |
| Assumed PCB | Z 8–9.6 = **1.6 mm** | Leaves **0.4 mm** nominal vertical play, before print error |
| Whole placeholder assembly | Z 8–26 = **18 mm** | This is populated height, not clip throat height |
| Modeled components above PCB | Z 9.6–26 = 16.4 mm | A cosmetic envelope; no real component locations verified |
| Shelf overlap under each edge | 3 mm inward × 10 mm along edge | Requires clear underside contact areas |
| Lip overlap over each edge | 2.5 mm inward × 10 mm along edge | Must avoid components, solder, and wires |
| PCB underside to recessed-floor top | Z 8 minus Z 5 = **3 mm** | Underside solder/wire clearance allowance only |
| Opposing upright faces | 40 mm apart nominally | Sized around an unverified 40 mm dimension |
| Jaw screw-slot center travel | ±3 mm per jaw | Roughly 34–46 mm nominal board-width span, not unlimited adjustment |
| Longitudinal end-stop inner gap | 37 mm | The 36 mm placeholder has 0.5 mm gap at each end |

The model's component envelope starts 3 mm inside the PCB edges. The retaining lip then has 0.5 mm clearance to that invented envelope. This says nothing about the real inductor, capacitors, pads, or solder joints.

**Config-only changes will not fix this:** the current generator uses literal `(40,36,1.6)` PCB dimensions and literal shelf/lip coordinates. `converter_pcb_thickness_assumption_mm` and the placeholder dimensions in the config are descriptive; they do not drive these clip solids. The generator must be updated along with the measured values.

## Measurements needed before resizing

With power disconnected, record:

1. Bare PCB length and width; use the board outline, excluding wire tails.
2. **PCB thickness at an exposed unsoldered edge**, preferably using calipers. Measure the laminate/board, not over the inductor or a solder joint.
3. Height above the PCB and protrusion below it after soldering; include the planned wire exits.
4. Top and underside photos with a ruler, identifying two opposing clear edge patches suitable for retention. A photo helps identify component interference, but is not a reliable substitute for a thickness measurement.

Then derive the throat from the measured maximum thickness plus a deliberate print clearance, set shelf/lip contact locations on verified empty PCB areas, and validate the complete populated model. A small clip-gap fit coupon should precede full printing. If no suitable edge patches exist, use a different retaining geometry instead of squeezing components under the existing lip.

**Disposition:** current clips remain concept parts. The 2 mm throat may accommodate a 1.6 mm bare board, but neither that thickness nor the assumed board outline is confirmed for this module.
