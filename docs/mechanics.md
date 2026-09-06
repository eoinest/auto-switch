# Mechanical prototype: headerless Pico W revision

**Historical reference — earlier Pico design; not the current build instructions.** For the current ESP32-S2 Mini POC, start with [S2 wiring](s2-aa-poc.md), [S2 firmware](s2-firmware.md) and the [current BOM](../BOM.md).

The photo shows **Decora-style / decorator paddle rocker switches in a two-gang wallplate**. “Decora” is Leviton's trademark; “decorator rocker” is the generic search term. One gang is the matching single-switch arrangement. Gang count does not establish single-pole versus three-way wiring.

This revision uses manufacturer dimensions and the official Pico W reference geometry, with explicit assembly clearances. **It is not yet a verified fit to your particular servo, soldered harness, battery holder or installed wallplate.** Print the small fit coupons and record the remaining measurements before printing the complete assembly. All parts stay outside the existing plate; this design does not require opening the switch or attaching anything behind it.

## What the Blender scene contains

`hardware/cad/config.json` is the editable dimensional configuration. `generate.py` creates both assemblies, exports millimetre STLs, and saves `generated/auto-switch.blend` and `assembly.png`. Objects marked `PRINT` are printed parts. `VENDOR Pico W` objects are the eleven components tessellated from Raspberry Pi's original STEP model. `COMPONENT` objects show purchased parts; `KEEPOUT` wireframes show service allowances. Component objects include their dimensional basis as Blender custom properties. Coupons and lids are hidden in the assembly preview, but available in the Outliner.

The Pico W mesh includes its actual board outline, mounting holes, connector and major components. The current default has no headers or carrier. Four nylon M2×6 screws mount the headerless board directly. Pico 2 W shares the published board footprint, but **the Pico W mesh is not an exact model of Pico 2 W's components**. The selected headerless board and actual solder/wire protrusion still require confirmation. See [component provenance](component-sources.md) and the [vendor notice](../hardware/components/vendor/NOTICE.md); third-party geometry retains its original license.

The holder, four AA cells, regulator, master switch, servo power gate, fuse holder, battery connector, prototyping board and illustrative wiring appear as separate objects. Manufacturer envelopes are distinguished from illustrative internal details. The perfboard placement is a component-space example, not a completed pad-by-pad board layout. The full circuit and connection order are in [wiring.md](wiring.md).

## Construction and mounting

- Each plate surround has 0.7 mm clearance per side, a 9 mm skirt and two 20 × 78 mm external adhesive lands. These are locating features; no unmeasured snap hooks are hidden behind the plate.
- A **separate universal electronics pod** bolts to either surround using two docking straps. The pod has 170 × 158 × 40 mm nominal internal space, a 4 mm floor and a removable lid. Individual print parts fit the A1 bed; the assembled device is substantially larger than a single wallplate. The enclosure is intentionally spacious for soldered wiring and removable batteries.
- The sideways MG90S is retained through its mounting ears using two M2 × 10 mm screws, nuts and washers. The provisional slots accommodate a 26–29 mm ear-hole pitch; this is not proof that the user's servo matches. The ear thickness, hole dimensions, shaft position, cable exit and horn remain unverified. The mounting coupon checks these before a large print.
- A two-ended yoke screws to the supplied **double-arm servo horn**. The original centre screw secures that horn to the spline. A 4.4 mm access hole provides screwdriver access. The provisional horn holes are 2.2 mm diameter, 14 mm apart. Measure the horn and use short compatible screws; do not force a printed spline onto the servo. A single-arm horn needs a revised flange or a matching replacement horn.
- The contact posts receive two bought **3M SJ5302 round bumpers, nominal Ø7.9 × 2.2 mm**, per servo. These compliant contacts are not calibrated force limiters.
- The headerless Pico uses its four published mounting holes and Ø3.9 mm printed posts; M2×6 nylon screws enter pre-tapped M2×0.4 pilots. The PCB underside sits at Z=8 mm above a Z=4 mm floor, leaving 4 mm below the board. A 3 mm subset is reserved for solder and wires. The other boards use shelves and removable edge retainers because exact mounting-hole coordinates are not consistently available. The battery holder sits on raised feet, has corner locators and uses straps through channels entirely above the enclosure floor. Two short ties retain the fuse holder through paired eyes; four more ties secure the wire harness through raised eyes. No tie or fastener protrudes between the enclosure back and wall.

The pictured wall is textured. **The selected Command 17201 strips explicitly exclude textured walls; do not use them there, and do not treat a trial adhesion test as overriding that restriction.** The adhesive lands are usable only with a mounting product approved for the actual surface. A suitable external mechanical mount or separately supported prototype is still needed for this wall. The present CAD does not solve that installation constraint. Do not remove the electrical wallplate or add screws into the switch box to improvise an attachment.

## Dimensional evidence and remaining fit checks

| Component or feature | Basis in this revision | Still to confirm |
|---|---|---|
| Pico W PCB | Official STEP; nominal 51 × 21 × 1 mm; hole pitch 47 × 11.4 mm, Ø2.1 mm | Headerless W selection and actual solder protrusion |
| TowerPro MG90S reference | Drawing: case length 22.8, width 12.4, case height 28.4, shaft-tip height 32.5, ear span 32.1 mm | User's manufacturer; ear-hole pitch, thickness, shaft offset, spline and horn |
| Pololu 1153 holder | Bare envelope 63 × 58 × 16 mm in this orientation | Loaded height; 22 mm is a reserved allowance, not a sourced loaded measurement |
| Pololu 2574 regulator | Published 43 × 21 × 10 mm envelope; drawing approximately 43.2 × 21 mm | Soldered wire bends and underside protrusions |
| Two Pololu 2810 switches | 15.24 × 15.24 mm PCB; 2.54 mm published height | Slider travel, wire bends and tool access |
| Adafruit 1608 PermaProto | Published 43 × 50.8 mm | Assembled circuit routing and exact actual board |
| Littelfuse fuse holder | 47.5 ±1 mm long, Ø11 mm | Cap removal, trimmed lead routing and retention |
| RCY and USB plugs | Explicit service envelopes, not exact manufacturer shell meshes | Actual molded plugs and unplugging clearance |
| One-/two-gang wallplate | Reference 69.85/115.9 × 114.3 mm; 46 mm gang pitch | Actual outside width, height, taper, depth and rocker travel |

Published dimensions and links are cataloged in [component-sources.md](component-sources.md) and [shopping-list.md](shopping-list.md). TowerPro's abbreviated product dimensions conflict slightly with its drawing; this model follows the drawing and does not assume all “MG90S” products are interchangeable. “All metal” commonly describes gears rather than the outer case.

Measure the plate while installed. Print `1g_fit_ring.stl` or `2g_fit_ring.stl` first. The thin ring checks the outline, not skirt depth or rocker travel. Print `coupon_servo_ear_mount`, `coupon_battery_holder`, `coupon_pico_mount` and each relevant board cradle with its corresponding retainer. The battery coupon is a 22 mm open collar; separately measure loaded height and wire exit. The Pico coupon checks the actual four post positions, tapped screw fit and underside solder clearance; the USB opening is in the full pod. Update the configuration and regenerate if anything fails. **Do not scale the whole STL**, because that changes screw and component interfaces together.

## Travel, force and manual operation

For torque τ and pad radius r, tangential force is approximately **F = τ/r**. A longer servo arm increases travel and reduces available force; reaching the switch's ends independently reduces the force required compared with pressing near its pivot. TowerPro's 1.8 kgf·cm stall rating at 4.8 V corresponds to roughly 6.8 N at a 26 mm radius, before losses. Stall is a limit, not an operating target.

Blender's frames 1–100 illustrate a ±10° upper/lower press, returning to neutral. The pivot is 31 mm above the wall reference and pad radius 26 mm. The rigid posts must clear the rocker; only the compliant bumper should make contact. The configuration check evaluates the descending rigid corner at the configured sweep. This does not establish real switch travel, calibrated servo pulse angles or full collision-free motion. Adhesive thickness, switch tilt, horn indexing and servo variations all change the contact position. Start at neutral and advance in tiny increments off the wall; stop immediately after a switch clicks.

The short press and neutral return reduce sustained force, but the mounting still carries the reaction force and battery weight. No force sensor, spring-return clutch or physical torque limiter is included. Check manual access at neutral. If power fails during a press, disconnect the low-voltage supply and remove the externally attached assembly or horn rather than forcing the paddle against servo gears.

## Printing and assembly

The A1's 256 × 256 × 256 mm build volume accommodates each exported part. The separate pod and lid are nominally 174 × 162 mm in XY. With the pod mounted above the surround and the lid closed, **both complete layouts occupy approximately 174 × 300.7 × 47 mm** (width × height × depth), excluding adhesive thickness and plug insertion space. Refer to `generated/validation.json` for all current dimensions. Leave room for slicer supports or brim; bed-fit checks do not include those additions.

1. Print and test the fit coupons first. Record every required measurement in the configuration before committing to full parts.
2. Print the surround and pod flat back down. PETG with a 0.2 mm layer, four perimeters and 25–35% infill is a starting point. Inspect bridge and overhang supports in the slicer. No universal G-code is provided.
3. Print each yoke in its exported side orientation; inspect support placement around the offset flange. Print the lid, four retainers and **two copies of `docking_strap.stl`**. Pilot holes are intended for careful screw threading in plastic; test first and avoid overtightening.
4. Pre-tap the Pico mounting coupon and posts M2×0.4, then fit the headerless Pico with four M2 × 6 nylon screws; use sixteen M2.5 × 8 screws across four retainers. Four M3 × 8 screws attach the lid. Four M3 × 6 screws and four M3 nuts attach the two docking straps. Each servo requires two M2 × 10 screws with matching nuts/washers, plus the original horn centre screw and measured compatible horn screws.
5. Fit and insulate the circuit following the wiring guide. Cut the selected servo extension to retain its male mating plug with roughly 100 mm of lead after a dry fit; solder those leads directly to the power board. Do not coil a full 12-inch extension inside this layout. The original servo stays unplug-removable. Keep the USB and antenna service areas free of added metal and wiring.
6. Test with a supported assembly and suitable spare switch before any wall installation. Check horn clearance, neutral return, fuse access, battery removal, connector polarity and cable strain relief. Resolve the textured-wall mounting method before attaching the loaded device.

## Regeneration and limits of validation

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python hardware/cad/generate.py
python3 hardware/cad/verify_stl.py
/Applications/Blender.app/Contents/MacOS/Blender --background hardware/cad/generated/auto-switch.blend --python-exit-code 1 --python hardware/cad/audit_fit.py
python3 tools/verify_bom.py
python3 tools/render_bom.py
open -a /Applications/Blender.app hardware/cad/generated/auto-switch.blend
```

Blender is sufficient to reproduce the model with its bundled Python; FreeCAD is a free alternative for later constraint-driven CAD work. The vendor STEP conversion is already included and need not run to regenerate this scene.

The generator requires one connected manifold volume per printable. Independent STL checks verify manifold edges, positive volume, bed origin and A1 bounds against the generated manifest. The fit report checks nominal component-body containment and separation, the four retainer envelopes against adjacent component bodies and each other, and retainer clearance from the lid-pillar envelopes. It also records installed assembly bounds and measurements still required. These checks do not certify manufacturing tolerance, complete wiring routes, all component/shelf contacts, dynamic collisions, print strength, servo torque, adhesive durability, RF performance or electrical temperature. The render is a design preview, not a built and tested device.


## BOM linked to exported meshes

The [root BOM](../BOM.md) lists installed single/two-gang quantities, exact selections, print quantities and unresolved interfaces. [BOM fit report](bom-fit-report.md) is the readable check summary; the underlying `generated/bom-fit-report.json` records the hashes of each STL actually audited. `audit_fit.py` independently reads STL triangles, transforms them back into the saved assembly, computes nominal component/STL intersection volumes, and probes the Pico mounting holes, solder space and USB port. Thus its evidence concerns the actual exported files, not just a matching list of nominal dimensions.

The remaining measurement gates and unresolved textured-wall mount are intentional limitations. A green geometry check does not make this a print-and-install kit. The board circuit is not pad-by-pad routed, all wire bends and complete fasteners are not simulated, and the servo/horn geometry still needs identification.
