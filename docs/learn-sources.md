# Learning module sources and review notes

Checked 2026-09-05. The module is original educational prose with worked project examples. Primary manufacturer/project documentation is linked below. Facts about the existing firmware are labeled project-specific, not independently validated performance.

The Pico W PDF exceeded the web parser’s size limit during this check. Its power topology was verified instead in Raspberry Pi’s **Hardware design with RP2040** §3.1.1, which explicitly covers Pico W, and cross-checked against the Pico 2 W datasheet release 2 (03 July 2026), §§2.1 and 3.4–3.5. The full Pico 2 W document was read successfully.

The numerical teaching examples are our calculations, not copied manufacturer examples. Nominal voltage, assumed currents and efficiencies are labeled; no demonstration substitutes for a load test. Browser interactions are an educational model rather than a SPICE simulation.

## ohm

[SparkFun: voltage, current, resistance and Ohm’s law](https://learn.sparkfun.com/tutorials/voltage-current-resistance-and-ohms-law/all)

- Voltage is a difference between two points; current is charge flow per unit time; V = I R for an ohmic resistor.

## circuits

[SparkFun: series and parallel circuits](https://learn.sparkfun.com/tutorials/series-and-parallel-circuits/all?print=1)

- Series elements share current; parallel branches share end nodes; a node represents an electrical junction.

## power

[SparkFun: electric power](https://learn.sparkfun.com/tutorials/electric-power/all?print=1)

- Electrical power P = V I; component power ratings limit heat dissipation.

## pico-power

[Raspberry Pi: Hardware design with RP2040, §3.1.1](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf)

- Explicitly covers Pico and Pico W: VBUS connects USB power to VSYS through a diode; VSYS feeds the onboard 3.3 V regulator.
- An external supply can feed VSYS through a separate Schottky diode for concurrent USB device use; do not bridge the supplies.
- Pico W physical pin mapping in the guide schematic: GP15=20, GP16=21, GP17=22, GP26=31, GND=38, VSYS=39, VBUS=40.

## pico2

[Raspberry Pi Pico 2 W datasheet, §§2.1, 3.3–3.5](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf)

- VBUS nominally 5 V when USB is powered; VSYS allowed range 1.8–5.5 V; 3V3 is regulator output; I/O voltage fixed at 3.3 V.
- Separate USB and external-source diodes provide power ORing into VSYS.
- ADC and pin numbering requirements; board antenna and mounting features require clearances.

## diodes

[SparkFun: diodes](https://learn.sparkfun.com/tutorials/diodes)

- Diodes conduct predominantly in one direction, with forward voltage drop and reverse limits; Schottky diodes generally reduce forward loss.

## polarity

[SparkFun: polarity](https://learn.sparkfun.com/tutorials/polarity/all.pdf)

- Diode body band marks cathode; polarity markings must be interpreted for the specific component.

## regulator

[Pololu S18V20F5 / item 2574](https://www.pololu.com/product/2574)

- Fixed 5 V step-up/step-down regulator; output current depends on input voltage and thermal conditions; typical efficiency 80–90%.
- About 1 mA typical no-load current under many conditions. ENABLE is pulled toward protected VIN; leave unused ENABLE disconnected.
- The disabled SEPIC regulator does not provide complete input/output isolation.

## gate

[Pololu Mini MOSFET Slide Switch LV / item 2810](https://www.pololu.com/product/2810)

- High-side MOSFET power path is controlled by the slider or ON input. With slider OFF, ON low/disconnected is off and above approximately 1 V is on.
- Switching wiring inductance can create positive input and negative output transients; keep wiring short and use appropriate capacitors/clamps.
- This switch is not an emergency disconnect; thermal current ratings depend on test conditions.

## servo

[Pololu: servo control interface in detail](https://www.pololu.com/blog/17/servo-control-interface-in-detail)

- Servo command is encoded by positive pulse duration; typical period is 20 ms; angle mapping and endpoints are not standardized.
- Servo electrical current varies with load and control behavior; signal timing does not replace the separate power connection.

## pwm

[MicroPython machine.PWM reference](https://docs.micropython.org/en/latest/library/machine.PWM.html)

- PWM exposes frequency and duty/pulse-duration controls; hardware resources and behavior are port-dependent.

## divider

[SparkFun: voltage dividers](https://learn.sparkfun.com/tutorials/voltage-dividers/all)

- For a lightly loaded divider, Vout = Vin Rbottom / (Rtop + Rbottom); a divider is unsuitable as a motor supply.

## adc

[MicroPython machine.ADC reference](https://docs.micropython.org/en/latest/library/machine.ADC.html)

- read_u16 returns a value scaled to 0–65535; scaling is not a promise of 16 bits of physical accuracy.

## capacitors

[SparkFun: capacitors](https://learn.sparkfun.com/tutorials/capacitors/all)

- Capacitors store electrical energy, resist abrupt voltage changes, have voltage limits and nonideal losses; some types require correct polarity.

## cells

[Panasonic eneloop lineup](https://www.panasonic.com/global/energy/products/eneloop/en/lineup/eneloop.html)

- AA eneloop capacity varies by product generation; project estimator uses the cited 1900 mAh minimum family and 1.2 V nominal cells.
- Discharge performance depends on conditions; nominal ratings are not measured project runtime.

## battery-use

[Panasonic eneloop FAQ](https://www.panasonic.com/global/energy/products/eneloop/en/faq.html)

- Use matched cells together, insert correctly, and do not mix chemistry, capacity, age or charge state.
- Primary dry cells must not be recharged; use the appropriate charger for the actual rechargeable chemistry.

## fuse

[SCHURTER SPT 5×20 datasheet](https://www.schurter.com/en/datasheet/typ_spt_5x20.pdf)

- 0001.2507 is a 2 A time-lag fuse with AC/DC ratings and specified pre-arcing time/current behavior, not an instantaneous 2 A limiter.

## meter-v

[Adafruit: measuring voltage](https://learn.adafruit.com/multimeters/voltage)

- Voltage is measured between two points with voltage-mode probes in parallel with the subject.

## meter-i

[Adafruit: measuring current](https://learn.adafruit.com/multimeters/current)

- Current measurement inserts the meter in the current path and requires the correct input jack and range; placing a current-mode meter across a supply creates a short.

## meter-r

[Adafruit: multimeters overview and continuity](https://learn.adafruit.com/multimeters?view=all)

- Resistance and continuity checks require an unpowered circuit; continuity indicates low resistance, not necessarily a fault.

## solder

[Adafruit: making a good solder joint](https://learn.adafruit.com/adafruit-guide-excellent-soldering/making-a-good-solder-joint)

- Heat both pad and conductor, feed solder to the joint, allow undisturbed cooling and trim wire leads.

## proto

[Adafruit quarter-size Perma-Proto / item 1608](https://www.adafruit.com/product/1608)

- The prototype board has connected rows and rails; its holes are not all electrically isolated.

## firmware-local

[auto-switch: power modes, assumptions and bench validation](https://github.com/eoinest/auto-switch/blob/main/docs/power.md)

- Project-specific source, not an independent authority: current Daily mode disables WLAN during ordinary waits; it does not establish deep sleep.
- The 4.4 V software guard inhibits actuation and does not disconnect the full pack; runtime numbers are assumptions until measured.

## Review boundaries

- VBUS availability was corrected from an overbroad earlier explanation: USB supplies VBUS; battery-only VSYS does not create 5 V there.
- Dual-diode ORing does not promise USB priority. The external diode prevents USB-fed VSYS from back-powering the external servo supply.
- Keep the servo gate slider OFF; its ON control and the regulator ENABLE are different electrical interfaces.
- Servo pulse width is taught separately from duty cycle and actual angle. No source establishes the user’s exact servo limits.
- The 100 kΩ / 47 kΩ divider is for measurement, not load power. Its low-voltage threshold is not a complete battery protection system.
- 470 µF transient examples explicitly assume an ideal isolated capacitor. They do not establish actual rail droop or clamp adequacy.
- Meter current mode is explicitly never placed across a supply. USB and battery are both removed before continuity work.
- Headerless Pico soldering retains all electrical pad assignments. CAD, wiring and physical tests are separate kinds of evidence.
- Course source links can change; checked date is retained in the JSON. Future changes to harness.json must be reflected in the capstone.

## pull-resistors

[SparkFun: pull-up and pull-down resistors](https://learn.sparkfun.com/tutorials/pull-up-resistors/what-is-a-pull-up-resistor) — checked 2026-09-05.

- Supports the general floating-node, pull-resistor and opposing-drive explanation in lesson 7. Its illustrative input-impedance numbers are not used as Pico specifications.
- The course deliberately does not assert an exact RP2040/RP2350 pin reset state. A high-impedance pin can still belong to a defined net if another component biases it.
- The 33 µA example is our Ohm’s-law calculation for 3.3 V across 100 kΩ, not a measurement of total ON-input, MOSFET-board or servo current.
- Pololu 2810 already specifies disconnected ON as OFF while its slider is OFF. The external pulldown is an explicit harness bias, not a claim that the bare module otherwise turns on unpredictably.
