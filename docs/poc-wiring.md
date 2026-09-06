# Earlier Pico POC: one servo, switched AA holder, breadboard rails

**Historical reference — earlier Pico design; not the current build instructions.** For the current ESP32-S2 Mini POC, start with [S2 wiring](s2-aa-poc.md), [S2 firmware](s2-firmware.md) and the [current BOM](../BOM.md).

Decision recorded 2026-09-05. This was the earlier Pico proof-of-concept wiring plan: use existing materials where suitable, one Pico W / Pico 2 W and one MG90S. The earlier illustrated WAGO assembly and its shopping budget are reference designs, not the shopping requirements for this POC.

[Download the plain ASCII map](poc-wiring.txt).

```text
ONE-SERVO AA BREADBOARD POC -- conceptual wiring, not exact hole placement

  4 x AA NiMH in a holder with a built-in ON/OFF switch
  (battery voltage varies; this is NOT a fixed 5 V source)

  Holder RED (+, switched) ---- F1 fuse ----> REG VIN
  Holder BLACK (-) ------------------------> GND rail

                 +---------------------------+
                 | REG: fixed 5 V buck-boost  |
                 | (e.g. existing S18V20F5)   |
                 |                           |
                 | VIN   GND           VOUT  |
                 +--------|--------------|---+
                          |              |
                          v              v
                       GND rail       +5 V rail

  BREADBOARD +5 V RAIL ================================================
                              |                         |
                              |                         +----> MG90S RED (+)
                              |
                              +---- D1 Schottky ----> Pico VSYS (pin 39)
                                    anode -> cathode       |
                                             stripe       v
                                                  onboard regulator
                                                          |
                                                    Pico's 3.3 V

                                      Pico GP16 (pin 21) ----> MG90S SIGNAL
                                                               orange/yellow
                                                               (verify yours)

  BREADBOARD GND RAIL =================================================
                   |                 |                    |
                   |                 |                    +----> MG90S GND
                   |                 |                           brown/black
                   |                 +----> Pico GND (pin 38)
                   +----> REG GND and holder BLACK (-), as shown above

  Optional USB data cable -----------------------> Pico micro-USB socket
  VBUS (pin 40) and 3V3(OUT) (pin 36): no external wires in this POC.

  Every connection marked '+5 V rail' joins the SAME regulated supply.
  Every connection marked 'GND rail' joins the SAME ground return.
  D1's stripe faces the Pico. F1 is in the positive battery lead.
```

## Parts to check at home

| Part | Quantity | Role / selection |
| --- | ---: | --- |
| Headered Pico W / Pico 2 W | 1 | Existing board; GP16 controls one servo |
| MG90S and original lead/horn | 1 | Existing servo; confirm connector polarity |
| Matched rechargeable AA NiMH cells | 4 | Charge externally; do not substitute four alkalines on an unregulated Pico supply |
| Four-AA holder with ON/OFF switch | 1 | Replaces separate holder/master-switch/RCY assembly; integrated switch is in the positive lead. Confirm its wiring and current suitability. [Adafruit 830](https://www.adafruit.com/product/830) is a candidate with male jumper ends, not a load-verified selection. |
| Fixed 5 V buck-boost regulator | 1 | Still required by this plan. Previous selection: [Pololu S18V20F5 / 2574](https://www.pololu.com/product/2574). A breadboard adapter marked 5 V is not necessarily a buck-boost converter or capable of the servo load. |
| D1 Schottky diode | 1 | Previous choice 1N5819; stripe toward VSYS; retained to permit USB programming with the battery supply attached |
| F1 fuse and insulated inline holder | 1 each | Retained for battery wiring protection. Prior choice: 2 A time-delay, 5 x 20 mm. Rating remains provisional pending current/holder/wire checks; mount close to the holder's positive output. |
| Breadboard, 22 AWG solid-wire links, suitable male-ended leads | As needed | Power/ground rails distribute connections. Servo socket needs mating male pins; loose stranded wire does not plug directly into a breadboard. |
| Solder/heat-shrink and multimeter | Shared | Adapt switch/module leads if needed; check continuity and voltage |
| NiMH charger and USB data cable | Shared | Charge removed cells; program the Pico |

No WAGO blocks, separate RCY pair, GPIO-controlled power gate, or battery-sensing divider is required for this POC. A connector or extension may still be useful if needed to mate with the actual servo plug; reuse one if available.

The control signal is drawn **directly from GP16 to the servo**. The earlier 1 kOhm series resistor is optional protection, not fitted in this minimal map. The earlier 470 uF / 10 V capacitor is also omitted from the baseline; it can be added across the regulated rails (positive to +5 V, striped negative to GND) if transient behavior warrants it. Neither omission constitutes a verified hardware result.

## How to read and build this map

1. Keep the batteries and USB disconnected during wiring. Use one red rail for regulated +5 V and one blue rail for GND. The rail colours are labels, not power sources. Check rail continuity with the meter: some boards split rails halfway, and opposite-side rails are usually separate. Bridge any sections you actually use.
2. Put the switched holder output through the fuse into regulator VIN. Holder negative and regulator GND join the ground rail. Only regulator VOUT feeds the +5 V rail. Follow the actual board labels; the regulator box above is a logical symbol, not a terminal-location drawing. On S18V20F5, ENABLE stays unconnected.
3. With Pico and servo disconnected, power the supply and measure regulated +5 V against GND and the diode output against GND. The diode output must be within the board's VSYS limits (never above 5.5 V). Then switch off and disconnect the pack again before inserting the Pico or servo.
4. Connect VSYS through D1, Pico GND to ground, servo power/ground to their rails, and GP16 to servo signal. Place the regulator feed and servo power connections near each other; keep leads short and secure the holder/switch so movement does not pull on breadboard contacts.
5. Use [config.aa-demo.example.json](../firmware/config.aa-demo.example.json) with the [firmware guide](firmware.md): `hardware_profile: "aa-demo"`, `power_enable_pin: null`, battery sensing off, one GP16 channel. The channel starts disabled and uncalibrated. Calibrate with the servo unloaded, before attaching a switch-pressing mechanism.

## Scope and limits

This is an **initial supervised, unloaded-servo breadboard experiment**. The selected holder's switch current rating, actual breadboard/contact rating, and servo startup/loaded current are not established. Passing an unloaded test does not validate the wall-switch load. If contacts become warm, voltage collapses, the Pico resets, or the servo jitters, switch off and investigate the supply/connections; direct soldered power distribution is a fallback, not automatically a larger fuse.

The diagram retains the regulator, diode and fuse deliberately. Four AA cells do not produce fixed 5 V. Supplying battery power to VSYS through a Schottky diode follows [Raspberry Pi's power guidance, pages 16-17](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf). With the holder switched off, attached USB can still power the Pico; it does not power the servo rail through D1. Disconnect both sources before rewiring.

No automatic low-battery cutoff is provided. Remove cells for external charging and switch off before depletion. No revised enclosure/STL fit or powered performance is claimed. The old $160 estimate included the WAGO build's retail packs and is not a price quote for this reduced POC; first inventory the parts above, especially the regulator, diode and fuse.
