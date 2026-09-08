# Parts for the current POC

One bedroom paddle switch, one servo, and an **ESP32-S2 Mini hosting the On/Off website**. The board is currently tested on USB; the portable battery circuit is planned.

| Part | Quantity | Selection / status |
|---|---:|---|
| Headerless ESP32-S2 Mini | 1 | User-owned, running MicroPython; direct-solder connections |
| MG90S 180° micro servo | 1 | User-owned; reuse its stock horn and centre screw |
| [DAIERTEK switched four-AA holder](https://www.amazon.com/dp/B09N1GDWQ9) | 1 | Received; seller drawing shows 64.2 × 68.7 × 19 mm case, 22.5 mm including switch; approximately 150 mm leads |
| Amazon Basics 1.5 V AA alkaline batteries | 4 | Ordered; go inside the holder |
| [Teyleten Robot 5 V buck-boost module](https://www.amazon.com/dp/B0GCW44FDL) | 1 | Received: PCB labeled XL63070; exact dimensions still needed |
| Breadboard and jumper wires | 1 set | User-owned; bench assembly only |
| Dedicated SPST ESP32 power-isolation switch | 1 | User-owned rocker switch candidate; placed only in booster 5 V → ESP32 VBUS branch. Verify its DC rating and actual terminal labels; see [USB wiring](docs/usb-wifi-setup.md) |
| USB-C data cable | 1 | User-owned; programming and USB-only tests |
| Solder, heat shrink and wiring tools | As needed | User-owned |

The received converter PCB is labeled XL63070 (confirmed in the user’s photos); the selected listing calls it TPS63070. Match the received module to the [wiring guide](docs/s2-aa-poc.md) and verify its output with the multimeter. The older LM2596 buck-only board is not the selected AA converter.

## Printed mechanism and retention

- **Servo mount and paddle:** [approved STL exports and fit instructions](docs/servo-command-mount.md).
- **Narrow Command strips:** [17207 listing](https://www.amazon.com/dp/B09XJDK6RS), four mating pairs (eight individual strips) total: two pairs for the actuator and two for the separate electronics wall bracket. Check the actual smooth mounting surface and strip thickness.
- **Horn/servo fasteners and two soft contact pads:** select to fit the actual servo and printed mechanism; reuse the original spline screw.
- **Electronics holder:** [mounting guide](docs/electronics-retention.md). Print the [v7 carrier and centered flat battery bar](hardware/cad/battery-retention-v7/README.md), and reuse the separate wall bracket. The battery bar uses two M3 × 30 screws/nuts. Optional v5 shims address sideways play. The old booster clips failed physical fit; the [option C replacement fit-test](hardware/cad/booster-retention-v1/README.md) uses two M3 × 16 screws and two M3 nuts. [All revised pieces share one STL](hardware/cad/revision-print-v8/README.md), with booster dimensions still provisional. Two M1.6 screws/nuts attach the S2 through its factory holes; its existing attachment geometry is retained.

The electronics tray is separate from the actuator. Its wall bracket is modeled, but adhesive retention and component fits remain physically unverified. The converter still uses a placeholder envelope and must be measured before its fit can be approved.

[Detailed quantities, wire checklist and fit status (CSV)](hardware/s2-current-bom.csv) · [Current wiring](docs/s2-aa-poc.md)

The [earlier Pico/gated BOM](docs/history/pico-bom.md) is retained only as a historical reference.
