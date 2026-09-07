# Parts for the current POC

One bedroom paddle switch, one servo, and an **ESP32-S2 Mini hosting the On/Off website**. The board is currently tested on USB; the portable battery circuit is planned.

| Part | Quantity | Selection / status |
|---|---:|---|
| Headerless ESP32-S2 Mini | 1 | User-owned, running MicroPython; direct-solder connections |
| MG90S 180° micro servo | 1 | User-owned; reuse its stock horn and centre screw |
| [DAIERTEK switched four-AA holder](https://www.amazon.com/dp/B09N1GDWQ9) | 1 | Received; seller drawing shows 64.2 × 68.7 × 19 mm case, 22.5 mm including switch; approximately 150 mm leads |
| Amazon Basics 1.5 V AA alkaline batteries | 4 | Ordered; go inside the holder |
| [Teyleten Robot 5 V buck-boost module](https://www.amazon.com/dp/B0GCW44FDL) | 1 | Selected; exact physical dimensions still needed |
| Breadboard and jumper wires | 1 set | User-owned; bench assembly only |
| USB-C data cable | 1 | User-owned; programming and USB-only tests |
| Solder, heat shrink and wiring tools | As needed | User-owned |

The selected converter listing calls it TPS63070 while its pictured PCB says XL63070. Match the received module to the [wiring guide](docs/s2-aa-poc.md) and verify its output with the multimeter. The older LM2596 buck-only board is not the selected AA converter.

## Printed mechanism and retention

- **Servo mount and paddle:** [approved STL exports and fit instructions](docs/servo-command-mount.md).
- **Narrow Command strips:** [17207 listing](https://www.amazon.com/dp/B09XJDK6RS), four mating pairs (eight individual strips) total: two pairs for the actuator and two for the separate electronics wall bracket. Check the actual smooth mounting surface and strip thickness.
- **Horn/servo fasteners and two soft contact pads:** select to fit the actual servo and printed mechanism; reuse the original spline screw.
- **Electronics holder:** [mounting guide](docs/electronics-retention.md). Keep the v4 carrier and wall bracket; use the [v5 battery-retainer replacement](hardware/cad/battery-retention-v5/README.md) after the reported loose fit and blocked switch. Two M1.6 screws/nuts attach the S2 through its factory holes; M3 hardware secures the battery retainers and converter jaws. See the dimensioned fastener list in the mounting guide.

The electronics tray is separate from the actuator. Its wall bracket is modeled, but adhesive retention and component fits remain physically unverified. The converter still uses a placeholder envelope and must be measured before its fit can be approved.

[Detailed quantities, wire checklist and fit status (CSV)](hardware/s2-current-bom.csv) · [Current wiring](docs/s2-aa-poc.md)

The [earlier Pico/gated BOM](docs/history/pico-bom.md) is retained only as a historical reference.
