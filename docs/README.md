# Documentation

Start with the [project overview](../README.md). The current POC is one headerless ESP32-S2 Mini, one MG90S servo, and a planned four-AA/5 V buck-boost supply. The ESP32 hosts the On/Off website directly.

## Current build

| Guide | Use it for |
|---|---|
| [Parts list](../BOM.md) | Current components and purchase links |
| [S2 wiring](s2-aa-poc.md) | Breadboard connections and power checks |
| [S2 firmware](s2-firmware.md) | Wi-Fi setup, board-hosted website and updating files |
| [Servo mechanism](servo-command-mount.md) | Mount, paddle and approved STL exports |
| [Electronics mounting](electronics-retention.md) | Screw mounts, converter jaws and removable battery retention; design review |
| [Previous carrier fit tests](electronics-carrier-v2.md) | Earlier v2 tray and small interface tests |
| [Private configuration](private-configuration.md) | Keep credentials out of Git |

## Supporting detail

- [Electronics component/source audit](s2-electronics-component-audit.md)
- [Independent carrier STL checks](../hardware/cad/electronics-carrier-v2/generated/independent-verification.json)
- [Detailed current BOM CSV](../hardware/s2-current-bom.csv)
- [Interactive S2 wiring viewer](../learn/s2-aa-poc.html)

The HTML viewer can be served locally with `python3 -m http.server 8767 --directory learn`, then opened at `http://localhost:8767/s2-aa-poc.html`. This is a documentation viewer, separate from the ESP32-hosted control website. Its illustration is a bench wiring reference; the v2 CAD guide is the current mechanical reference.

## Development checks

From the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_firmware*.py'
node --check firmware/www/app.js
python3 hardware/cad/electronics-carrier-v2/verify_independent.py
```

These check software logic and exported meshes. They cannot establish servo calibration, component fit or battery runtime.

## Historical designs

Earlier designs remain at their existing paths so old links still work. They are not required for the current POC:

- [Pico / gated-power BOM](history/pico-bom.md)
- [Pico power design](power.md) and [wiring](wiring.md)
- [Mac gateway](gateway.md) and [earlier firmware guide](firmware.md)
- [Previous S2 electronics tray](s2-aa-mechanical.md), superseded by v2
- [Earlier AA/Pico demo](aa-demo-plan.md)
- [Circuit learning material](../learn/README.md), which includes earlier designs
