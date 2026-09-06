# Read the Auto Switch diagrams

**Historical reference — earlier Pico design; not the current build instructions.** For the current ESP32-S2 Mini POC, start with [S2 wiring](s2-aa-poc.md), [S2 firmware](s2-firmware.md) and the [current BOM](../BOM.md).

Start with the [complete connection map](../hardware/wiring/connection-map.svg): one continuous drawing with every component, all supply and signal wires, and a shared ground return. The learning site opens this map first and provides fit, zoom and full-screen controls.

The [power explorer](../hardware/wiring/power-map.svg) remains an optional teaching view. Follow the red supply branch **into VSYS pad 39**, across the boundary of the Pico board, through its onboard regulator, and into the chip at 3.3 V. This is the missing link between the battery assembly and the running Pico.

The connection map draws all 46 external terminals from [harness.json](../hardware/wiring/harness.json). Automated geometry checks verify that each terminal touches its assigned wire and that every named net is connected within the drawing. Labels identify wires; you do not need to jump between repeated labels or separate panels. Use the [assembly instructions](wiring.md) and [shopping list](shopping-list.md) alongside it. These diagrams are functional electrical drawings, not an exact per-hole soldering layout or a substitute for continuity checks.

## Two supplies meet inside the Pico

The external branch is holder positive → fuse → RCY disconnect → master switch → external 5 V regulator → **external D1** → VSYS. The Pico's own regulator then generates 3.3 V. The external diode's striped cathode faces VSYS.

The USB branch is USB connector → **VBUS** → **onboard diode** → the same VSYS junction. The onboard diode is already installed on the Pico; do not buy or solder another part for that symbol. The diagram calls our added diode “external D1” to distinguish it from the Pico schematic's own reference designators. VBUS is the USB supply connection, not a Pico-generated 5 V regulator output. This topology and the external-diode arrangement follow the [official Pico W power documentation, sections 3.4–3.5](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf).

With USB alone, the Pico works and the motor rail stays off. With the battery master on, the external branch can power the Pico and the servo gate's input. With both supplies, the branch with the higher voltage after its diode normally supplies VSYS; closely matched sources can share current. Neither diode is an ideal zero-drop valve, and the voltage drop depends on current and temperature. A teaching simulator can show *available paths* without predicting exact current sharing.

Direct soldering to a headerless Pico keeps the same physical **pad numbers**. “GP15” means a GPIO function; “20” identifies its physical edge pad. Pad 39 is VSYS; pad 38 is ground. Pad 40 VBUS and pad 36 3V3 OUT receive no external harness wire in this build. USB is still plugged into the board's USB connector for programming. [Official pinouts](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html).

## The servo uses a different branch

Regulated 5 V also feeds the **VIN** of the servo's Pololu 2810 LV gate. Its VOUT feeds the servo supply wire. The Pico drives the gate's **ON** input with GP15, using 3.3 V logic. This signal controls a MOSFET; motor current flows through the MOSFET's power terminals, not through GP15. The gate's physical slider must remain OFF so that it does not override software control. The manufacturer specifies that ON above approximately 1 V enables the gate. [Pololu 2810 operation](https://www.pololu.com/product/2810).

The 5 V regulator is a different device with a different job. It converts the battery's varying voltage into a nominal 5 V supply; it cannot provide unlimited motor current. Leave its ENABLE input unconnected in this design. [Pololu S18V20F5](https://www.pololu.com/product/2574).

GP16 and GP17 carry servo position commands through their separate 1 kΩ resistors. Turning off this PWM signal does not physically disconnect the servo's power. Turning off the gate does. Keep the signals inactive when motor power is off; a powered signal can otherwise feed a small unintended path through a servo's input electronics.

## Grounds, junctions and symbols

- **GND is one connected net:** battery negative, USB ground, Pico, regulator, both switch modules, servos and passive returns share it. Every external ground wire is drawn back to one continuous bus along the bottom. Ground is the circuit's reference voltage and return path; it need not be connected to the earth or the wall.
- **Motor return:** connect it at the power assembly, not by routing it through the Pico. The heavy supply line and its return together form the current loop.
- **Named nets:** every appearance of `5V`, for example, refers to the same connected conductor. `5V` and `SERVO_5V` are different nets separated by the gate. `PACK_SW` is varying raw battery voltage after the master, not regulated 5 V.
- **Filled dot:** wires join at that point. A white gap at an unrelated crossing shows that the wires do not join. All same-net branches are continuous and marked with junction dots.
- **Resistor rectangle:** limits current or helps set a voltage. Value is in ohms (Ω); kΩ means thousands of ohms.
- **Capacitor plates:** store a little electrical energy. C1 is polarized: its positive terminal faces 5 V and its negative stripe faces ground. C_ADC is a non-polar ceramic capacitor.
- **Diode bar:** marks the cathode. On our two external 1N5819 parts, the physical stripe identifies that end. D2's cathode faces the switched servo supply; its anode faces ground.

D2 addresses negative output transients; C1 buffers the input supply; R_BLEED discharges the servo rail after switching off. These do not guarantee a noise-free system or make an undersized supply adequate. Their roles follow the switch manufacturer's [transient-protection guidance](https://www.pololu.com/product/2810). The actual servo, wire length and power supply still need bench measurements.

## Battery sensing

The upper 100 kΩ resistor starts at **PACK_SW**, before the 5 V regulator. Its lower end joins GP26/ADC0, the 47 kΩ lower resistor, and the 100 nF filter capacitor. The resistor and capacitor's other terminals connect to ground. The nominal relationship is:

`V_ADC = V_PACK_SW × 47 / (100 + 47)`

At a 4.8 V pack, that gives about 1.53 V. Sensing the regulated 5 V line would mostly tell you that the regulator still works, rather than reveal the battery's changing voltage. A voltage reading is not a precise NiMH charge percentage.

## Interactive integration

`tools/render_wiring.py` regenerates both SVGs without external libraries. `tools/continuous_wiring.py` lays out the complete circuit. Visible terminal circles carry `data-terminal` identifiers, while polylines carry `data-wire` net names and machine-checkable points; tests compare these with the harness. This checks drawn connectivity rather than relying only on text labels. The power map has stable group IDs:

| ID | Meaning |
| --- | --- |
| `path-battery` | Holder, fuse, connector and incoming master supply; available while battery is connected |
| `path-pack-sw` | Master output wire and PACK_SW label; available only when battery is connected and master is on |
| `path-regulated` | External regulator and regulated 5 V branch |
| `path-pico-external` | Added diode and incoming VSYS supply |
| `path-usb` | USB, VBUS and onboard USB diode |
| `path-vsys` | Shared VSYS and onboard regulator |
| `path-3v3` | Pico chip's regulated supply |
| `path-motor-input` | Gate input and gate module |
| `path-motor-output` | Switched rail and servo(s) |
| `path-ground` | Common ground reference and return paths |
| `path-control` | GP15 control signal |
| `path-pwm` | GP16 / GP17 position command signals |
| `path-adc` | Battery measurement network |

The CSS class `is-off` dims a group. Major components have `data-part` attributes for click-to-explain integration. These IDs distinguish supply availability from commanded motion: a USB-powered Pico can drive GP15 even when no battery supply exists for the motor. A working motor path requires both battery/regulator power and an enabled gate. Ground remains the shared reference, rather than becoming “off” when its voltage is zero.
