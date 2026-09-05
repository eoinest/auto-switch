# Portable demo power research

Researched 2026-09-05 with three independent subagents: USB power banks, Pico/servo power paths, and simpler battery alternatives. This is a design recommendation, not a replacement wiring guide or a tested BOM. Existing firmware, diagrams, and STLs still describe the earlier gated AA design.

**Decision update:** the user chose the simplified AA direction after reviewing this comparison. Follow the [AA demo plan](aa-demo-plan.md) for the selected next direction. The power-bank recommendation below is retained as research context, not the current selection.

## Recommendation

Use a finished, rechargeable USB power bank with documented always-on outputs. Keep Wi-Fi connected and omit software-controlled servo power gating. Prefer one bank with two USB-A outputs: one cable powers the Pico through its USB socket; the other supplies the servo directly. This avoids carrying motor current through the Pico while retaining one rechargeable battery and no external battery regulator or charger circuit.

The compact technical candidate is the Voltaic V25; the currently stocked fallback is the larger V50. Keep the bank separate from the wall actuator for the first prototype. Exact fit, mount strength, and loaded servo operation remain unverified.

## Shortlist

Prices are USD before shipping/tax; stock is a research-time snapshot.

| Candidate | Current manufacturer specification body | Availability observed | Decision |
| --- | --- | --- | --- |
| [Voltaic V25](https://voltaicsystems.com/v25/) | 24 Wh; 80 × 82 × 24 mm; 230 g; USB-A 5 V/2 A, 3 A maximum across two outputs | $45; out of stock | Smaller preferred candidate if available |
| [Voltaic V50](https://voltaicsystems.com/v50/) | 48 Wh; 118 × 82 × 24 mm; 368 g; same USB-A ratings | $74; in stock | Available bench-demo candidate; considerably heavier |

Both specify no low-current cutoff on USB-A. Use those ports; the top USB-C PD port is not compatible with always-on operation, including as a charging input while relying on that mode. The manufacturer's [version/always-on guide](https://voltaicsystems.com/always-on-batteries/) identifies the side charging input for that use. For the first demonstration, charging while operating need not be a requirement.

Product titles retain older capacity figures. Downloadable CAD exists, but its revision has not been matched to the current product. Before a snug cradle is designed, compare the purchased unit, current dimensions, cable exits, and the actual CAD geometry. Published body dimensions exclude the space our cable bends and strain relief will need.

An ordinary phone power bank may work, particularly if already owned, but needs an idle test. [Anker's general trickle-mode guidance](https://service.anker.com/article-description/What-is-Trickle-Charging-Mode) describes a two-hour automatic timeout and model-dependent support; this is not a blanket always-on guarantee. The [Adafruit 1566 Raspberry Pi battery](https://www.adafruit.com/product/1566) explicitly warns of sleep below about 100 mA and output interruption during charging transitions. A Raspberry Pi label alone does not establish compatibility with our idle load.

## Proposed power connections

```text
ONE always-on USB battery bank
  USB-A output 1 -- USB-A to Micro-B cable --> Pico USB socket
  USB-A output 2 -- USB power breakout -----> Servo +5 V
                            GND --------+---> Servo GND
                                        +---> Pico GND (pin 38)
  Pico GP16 (pin 21) ------------------------> Servo signal
  Pico GP17 (pin 22) ------------------------> Optional second servo signal
```

The second servo would share the external servo power/ground branch. Begin with one servo and operate two sequentially after validation. Do not join the two USB positive outputs or attach the external servo +5 V to Pico VBUS in this topology. Ground is joined for the control signal reference. The bank's shared current limit still applies; separate cables do not create separate batteries or guaranteed noise isolation.

A candidate bench adapter is [Adafruit 3628 USB-A male to screw terminals](https://www.adafruit.com/product/3628), listed at $4.95, accepting 26–16 AWG wire. It avoids cutting a USB cable. Its product page does not specify a full assembly current rating, so it is a candidate, not a validated high-current connector. Use labeled +5 V/GND terminals only, insulate them, and keep the motor power path off thin logic jumpers and solderless breadboard rails. Retain provision for a local supply capacitor and signal series resistors when the wiring is finalized; neither substitutes for adequate source current.

## What the Pico can and cannot supply

The official [Pico W](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf) and [Pico 2 W](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf) datasheets show USB power directly on VBUS, with a diode feeding VSYS and the onboard 3.3 V regulator. A servo on VBUS bypasses that diode and regulator. Thus the earlier VBUS-powered single-servo proposal is possible.

We did not find a specified whole-board VBUS-to-header peripheral current rating. A bank's 3 A rating does not certify that current through the Pico's connector, traces, headers, and attached wiring. Routing servo power externally avoids that uncertainty. An alternative single-output bank topology can feed the servo directly and Pico VSYS through a Schottky diode, following [Raspberry Pi's external-power guidance](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf). The two-port arrangement avoids adding that external diode by using the Pico USB socket normally.

[TowerPro's MG90S page](https://towerpro.com.tw/product/mg90s-3/) specifies nominal 4.8 V operation but no idle or stall current, and discusses counterfeit units. Its higher-voltage torque/speed entries do not constitute a clean operating-range specification for every MG90S-branded servo. Regulated 5 V is a proposed test supply, not proof of compatibility or current margin for the user's units. Do not treat reseller stall-current numbers as verified measurements.

## Why not AA cells or a Pico battery add-on?

Four AA NiMH cells plus a buck-boost regulator remain possible without a servo gate. The existing [Pololu S18V20F5](https://www.pololu.com/product/2574) explicitly supports four-cell battery applications, but retains the holder, regulator, switch/wiring, external charger, and depleted-pack handling. Its low input cutoff does not protect a four-cell NiMH pack appropriately by itself.

Small add-ons such as [Pimoroni's Pico LiPo SHIM](https://shop.pimoroni.com/products/pico-lipo-shim) and [Waveshare Pico-UPS-B](https://www.waveshare.com/product/raspberry-pi/pico-ups-b.htm) can power the Pico, but their product pages do not establish the regulated 5 V servo supply we need. They are not drop-in replacements for a power bank in this circuit.

## Runtime: conditional calculations

No current or runtime has been measured on the assembled project. Use the complete circuit's average power, including Wi-Fi, idle powered servos, and movement. The previous estimator's gated-servo assumptions do not apply unchanged.

For illustration only, assume 80% of nominal battery energy reaches the load after combined conversion and usable-capacity losses:

`hours = nominal Wh × 0.8 / average whole-device watts`

| Assumed whole-device average | 24 Wh bank | 48 Wh bank |
| --- | --- | --- |
| 0.5 W | about 38 h | about 77 h |
| 1 W | about 19 h | about 38 h |
| 2 W | about 10 h | about 19 h |

These are scenarios, not bounds or predictions. Powered servo idle/holding consumption can dominate; battery aging, network retries, and real conversion efficiency also matter. More battery energy extends runtime but does not establish peak-current capability. Use the bank's own indicator initially; its regulated USB voltage does not reveal charge percentage.

## Evidence needed before the hardware design is finalized

1. Verify actual Pico variant, servo connector polarity, and 5 V output before connection. Start unloaded with conservative travel.
2. With Wi-Fi running, test repeated movements and supported switch presses; check for reset, jitter, bank shutoff, and voltage sag. Avoid sustained stalls.
3. Leave the circuit idle overnight, then command a movement; repeat at low bank charge. For ordinary banks, this must exceed any documented timeout.
4. For two servos, test combined startup and idle behavior even when commanded moves are sequential.
5. Measure average USB energy over representative operation. A basic USB meter can miss short current/voltage transients; use faster instrumentation if needed to resolve unreliable motion.
6. Measure the selected bank and cables before modeling its holder. Test a supported actuator before adding battery weight to a wall mount.

The eventual firmware needs an explicit ungated hardware configuration; its existing Demo networking mode alone does not provide that. Preserve conservative calibration and return the arm clear of the rocker. Stopping PWM is not a guaranteed electrical cutoff or torque release, as discussed in [Pololu's servo interface guide](https://www.pololu.com/blog/16/electrical-characteristics-of-servos-and-introduction-to-the-servo-control-interface). No new hardware, firmware, BOM, or STL design has been implemented by this research.
