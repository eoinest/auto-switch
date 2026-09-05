# Learning module verification — 2026-09-05

The learning module uses the claim/source registry in [learn-sources.md](learn-sources.md). These checks validate software behavior and selected nominal geometry; they do not certify a physical circuit or assembly.

- 51 Python tests passed, including firmware, relay, wiring contracts, curriculum references, generated learning assets and BOM evidence.
- JavaScript model checks passed for all 16 supply/master/request combinations, resistance/current units, ADC limits, energy assumptions and capacitor depletion.
- Browser checks passed for USB-only motor isolation; both-source operation; master-off highlighting; wrong answers, retries and saved lesson progress; all five experiment controls; and correct/incorrect design challenge scoring.
- BOM search, one/two-servo quantities and installed print quantities worked in the browser. Local reference links resolved.
- Desktop, dark-mode and phone layouts were inspected. Power, lessons, workbench and parts pages had no document-width overflow at 320 px; detailed diagrams and tables intentionally scroll within their containers. The browser reported no console errors or warnings.
- Direct `file://` navigation was blocked by the browser automation tool, so that launch method was not browser-verified. The tested localhost version uses bundled local assets without fetching course data or calling hardware APIs. External reference and purchase links require internet access.
- All 21 STL files passed independent manifold, positive-volume, print-bed and A1 build-volume checks. The [BOM fit report](bom-fit-report.md) records 13 checks against current exported meshes and component models. Hash checks bind that evidence to the current BOM, models and STL files.

The remaining physical measurements, unselected horn fasteners and textured-wall attachment are explicit in the [BOM](../BOM.md). No hardware power, motion, battery-runtime or physical fit testing has been performed by these software checks.

## Continuous-map revision

The former panel-based connection sheet is replaced by one continuous circuit and a dedicated default Connection map tab. All 46 visible terminals have the correct net assignments and lie on actual SVG wire segments. Each of 13 nets is one connected segment graph; no unrelated nets have collinear overlaps or junction dots on each other. Seven learning/bundle/diagram tests pass. Browser checks cover zoom, fit-to-view, fullscreen entry/exit and fitting the entire map at both desktop and phone viewport sizes.

## Breadboard bench layout

The added 63-row breadboard plan places a headered Pico W at c3–c22/h3–h22. Ten independent tests check conductive strips, one/two-servo net equivalence, all 40 header positions, unused-pin isolation, duplicate hole occupancy, deliberate wiring errors, and actual rendered insertion markers/CSV addresses. Both profiles pass: 40 terminals across 11 nets for one servo; 46 across 13 nets for two. Browser checks cover step highlighting, 18/21 checklist rows, profile switching, fit/zoom/fullscreen and phone-width overflow. Source references and unpowered/voltage-check procedures are in the breadboard guide. This is an electrically checked design, not a bench-tested circuit or a fit check for the printed enclosure.
