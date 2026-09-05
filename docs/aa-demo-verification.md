# AA demo verification — 2026-09-05

Current scope: **one servo only**. The viewer, shopping quantities and firmware example use this build. Two-servo generator outputs remain as prior design references, outside the current shopping/build instructions.

One-servo update checks: 32 AA diagram/BOM tests passed; JavaScript syntax and learning-asset checks passed. Browser inspection confirmed one fixed build, four assembly steps, 24 BOM rows, and one-servo download targets. The PNG was regenerated from the updated SVG and visually inspected.

Previous delivery checks (before narrowing the viewer to one servo):

Delivered: Amazon-first bench BOM, one/two-servo component illustrations (SVG and PNG), exact-hole placement CSVs, a local viewer with shopping links, and an explicit ungated firmware profile. The prior gated circuit remains available and labeled as earlier work. No hardware was purchased or powered, and no STL enclosure changes were made.

## Checks completed

- Independent conductor/strip graph: one-servo 41 terminals, 8 nets, 53 occupied breadboard holes, 12/15 WAGO ports used; two-servo 47 terminals, 10 nets, 58 occupied holes, 14/15 ports used.
- Actual SVG verification: 22 wire paths for one servo, 26 for two; all 630 terminal holes, 40 Pico header squares, component endpoints, WAGO ports, conductor geometry, and exported placement tables agree. Mutations test shorts, opens, wrong pins, extra/missing paths, transformed geometry and misleading terminal crossings.
- Firmware fake-hardware checks: AA profile never touches GP15 or the absent battery ADC; legacy gated operation, calibration guards, and cleanup remain covered. PWM shutdown is not claimed to disconnect servo power.
- Purchasing counts checked against one/two-servo circuit quantities, and viewer asset copies checked against their source files.
- Browser: 24 BOM rows and six distinct Amazon purchase links; one/two-servo selection; fit/zoom; enter/exit fullscreen; SVG/PNG/checklist downloads returned successfully; 390 × 844 phone viewport had no page-level horizontal overflow. No page JavaScript errors occurred during the successful flow.
- Visually inspected full-resolution component diagrams and desktop/phone screenshots. Pololu top-view references were inspected for regulator and master terminal orientation. Photographic/cosmetic component details are simplified illustrations, not manufacturing drawings.

The initial complete test run was prevented from binding a local HTTP test socket by the sandbox. Re-running with local execution permission passed. A browser test-script URL-construction issue was corrected; it was not an application failure. Duplicate shopping links and two ambiguous drawn wire routes were corrected before the final checks.

## Reproduce

```sh
python3 tools/render_aa_demo.py
python3 tools/verify_aa_demo.py
python3 tools/build_aa_demo.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/build_learning.py --check
node --check learn/aa-demo.js
```

PNG files were exported from each final SVG using Chromium at its native 2480 × 1900 size. After changing vector geometry, re-export both PNGs before running `build_aa_demo.py`; that script copies PNGs rather than re-rendering them. Browser inspection screenshots are local ignored artifacts in `output/playwright/`.

## Limits

Connectivity checking does not simulate a circuit or certify solder joints, breadboard contact fit, battery depletion behavior, current capability, servo torque, or voltage transients. The complete assembly still needs the voltage and loaded-operation checks in [the guide](aa-demo-plan.md). Existing STL fit evidence does not apply to the new WAGO/breadboard assembly. Amazon checks establish listing identity, not delivered authenticity, checkout price, or inventory; see [the source record](aa-demo-source-checks.md).
