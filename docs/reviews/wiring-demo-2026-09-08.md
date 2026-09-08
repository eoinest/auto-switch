# Critical review: minimum supervised wiring demo

Reviewed 2026-09-08. Scope: four AA alkaline cells in the switched holder → received XL63070 module → measured approximately 5 V → ESP32-S2 Mini VBUS and one MG90S in parallel; common ground; GPIO16 signal. No physical measurements were made in this review. No CAD, firmware, private files or hardware were changed.

**Conditional go for staged, attended bench testing. No unconditional electrical-capacity approval.** The simple topology is reasonable. Secure connections, output-voltage verification, USB isolation and conservative servo motion are the minimum. A gate, signal resistor, extra capacitor or battery monitor is not automatically necessary for the first demonstration. Unknown converter/holder/contact/servo ratings prevent approving continuous load, a jammed mechanism or unattended use.

## Main findings

| Failure mode | Consequence | Minimum action for this demo |
|---|---|---|
| Wrong converter selection, reversed connector or mistaken S2 pad | Supply applied to the wrong node can damage parts immediately. | Verify actual labels and polarity with power removed; measure converter output before connecting either load. VBUS is the supply input here; 3V3 and GPIO16 are not 5 V supply pins. |
| USB and converter both connected to S2 VBUS | USB and converter outputs become tied together. Battery OFF does not isolate the USB supply from the converter output or servo rail. | Physically disconnect and insulate the converter-to-S2-VBUS lead before USB use. Keep this disconnect accessible. |
| Loose strands, oversized/tinned blobs in breadboard contacts, twisted bare splices | Intermittent supply, adjacent-pad shorts, local heating or a pulled-off PCB pad. | Use secure insulated solder/crimp joints and correct breadboard pins or solid wire ends. Provide strain relief. Do not use loose twists as finished joints. |
| Servo start/reversal/load spike through a resistive contact chain | Servo jitter, controller resets or misleading command failures. | Prefer short separate supply/return branches from converter output to each load. Watch voltage at the load connectors, not just at the converter. Stop on resets or repeatable jitter. |
| Servo reaches a mechanical stop or pushes continuously after the switch flips | High current and heating; mount damage or repeated brownout/reboot motion. | First test with no switch load. Start near neutral with small moves. Do not deliberately stall it or leave it buzzing against the switch. |
| USB powers the ESP while the servo is switched off, but PWM remains active | Possible current injection through the servo input; exact behavior of this servo is undocumented. | Stop PWM and hold the signal low/high-impedance before servo power-off, or disconnect the signal lead. If software behavior is unknown, use the physical signal disconnect. |
| Meter lead left in a current socket during voltage measurement | Meter can short the supply. | Black lead in COM, red in V/Ω, DC voltage mode. Current measurement is not required for the first spin. |

The [WEMOS S2 Mini schematic](https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf) directly connects the USB VBUS net to the board's VBUS header and regulator input. That supports the power-source isolation finding; it does not establish the rating of the user's clone, connector or soldered harness.

[BusBoard's breadboard guidance](https://www.busboard.com/faq) specifies suitable solid-core wire for its products, and its [BB830 specifications](https://busboard.com/BB830T) describe a particular contact system. Those ratings must not be transferred to an unidentified breadboard. Factory male jumper ends or correctly sized solid-wire ends are preferable to forcing a bundle of solder-tinned strands into an unknown spring contact. Poor contact can fail before the converter reaches its advertised limit.

[Pololu's servo electrical overview](https://www.pololu.com/blog/16/electrical-characteristics-of-servos-and-introduction-to-the-servo-control-interface) distinguishes idle and stall demand, while its [motor/power-supply guidance](https://www.pololu.com/docs/0J73/4.1) explains why starting and stalled motors demand more current than a freely running motor. This is general guidance, not an MG90S current measurement. Do not assign the user's servo a guessed stall-current rating or run it into a stop to discover one.

The powered-off signal warning is a **precaution based on a known IC failure mechanism, not proof of this servo's internal circuit**. [TI documents back-powering through input protection structures](https://www.ti.com/lit/ab/scda015c/scda015c.pdf?ts=1781771181252). The MG90S signal-input circuit and powered-off tolerance are not established here. Removing only the converter-to-VBUS wire solves the USB supply tie, but does not by itself solve a powered signal into an unpowered servo.

## Simplest practical distribution

The two duplicate VOUT holes may carry separate leads to S2 VBUS and servo positive; the two duplicate output-GND holes may carry separate returns from S2 GND and servo ground, **after confirming those duplicate holes share their labeled net with power removed**. This preserves the same parallel topology and can eliminate the breadboard power rails entirely. It does not double the module's current rating or provide independent regulated outputs.

Use one secure termination per chosen hole, with insulation and strain relief that do not load the PCB pad. Keep the signal lead distinct from power. If using the existing breadboard instead, verify every used rail segment and bridge any required split with power removed. Avoid routing servo supply current through the controller board or through a long chain of jumper contacts. These are practical reductions in connection resistance and failure points, not a certification of the remaining wiring.

## Power modes and sequencing

| Mode | Converter → S2 VBUS lead | USB | Ground/signal |
|---|---|---|---|
| Battery-only demo | Connected | Unplugged | Common ground and GPIO16 connected. |
| USB programming, servo power off | Disconnected and insulated | Connected | Ground may remain; disconnect the servo signal unless its inactive state is verified. |
| Live USB debugging while battery powers the servo | Disconnected and insulated | Connected | Common ground **must remain**; signal may remain while the servo is powered. Disable/disconnect signal before switching servo power off. |

Set up or change the power wiring with both sources disconnected. A live-debug session can retain ground and signal; removing all three harness leads is the simpler isolation procedure for programming without servo operation, not an electrical requirement for every debug session. Do not replace the missing positive lead with a jumper elsewhere on the breadboard. If there is any uncertainty about isolation, use the battery-only demo or disconnect the whole harness before USB programming.

## Minimum go/no-go bring-up

1. **Unpowered inspection.** Remove cells and unplug USB. Inspect the seven terminal groups, plug polarity, free strands and solder bridges. Confirm intended ground/duplicate-pad continuity and any breadboard joins. A transient continuity beep can result from capacitors charging; a sustained near-short between positive and ground needs investigation. Continuity/resistance tests are unpowered only. Place the assembly on a stable insulating surface with the switch accessible.
2. **Converter only.** Leave S2 and servo supply leads detached. With meter leads in COM and V/Ω and DC-voltage mode selected, connect probes so they cannot slip across neighboring pads. Install correctly oriented cells, switch on, record VIN-to-input-GND and VOUT-to-output-GND. **Go only if output is approximately 5.0 V and polarity is correct.** A raw-pack-like value or another selection is a no-go. The purchase option and apparent link position are not measurements. Switch off before connecting a load.
3. **S2 alone, battery only.** Connect its VBUS and ground with USB absent. Confirm the page remains reachable during Wi-Fi activity. Record voltage at the S2's VBUS/GND pads. Reboots, unstable connection accompanied by resets, or a large drop from converter VOUT are a no-go pending diagnosis.
4. **Add the servo, unloaded.** Switch off first and connect the servo, with its output free of the switch mechanism. Start with a few small movements near the intended neutral position. Record voltage at the servo supply connector and watch the S2 for resets. Stop for repeated jitter, uncommanded motion, sustained straining noise, warm leads/contacts/cells, rapidly increasing converter temperature or odor. Do not touch exposed energized pads to assess temperature; switch off before handling.
5. **Gentle switch trial only after the unloaded test passes.** Use a few short actuations with conservative endpoints. The mechanism must finish without the servo remaining forced against a hard stop. Keep hands clear of moving parts and power off promptly if motion binds. This establishes only that the tested motion worked under the tested battery/load conditions.

Do not treat a successful web response as evidence that the servo moved, or one successful flip as evidence of reliable current capacity. After any short, reset or overheating event, disconnect power and find the cause before repeating the test.

[Fluke's multimeter guidance](https://media.fluke.com/ade6b718-4577-4b57-903b-b10600664c67_original%20file.pdf) explains why a voltage test with the lead in the current jack can create a short. Use voltage measurements first; any later current measurement requires the correct fused range and a series connection, with power off while rearranging leads. Never put an ammeter directly across the battery or output.

## Measurements to record, and what they establish

| Measurement | First trial? | Purpose / limit |
|---|---|---|
| Converter VIN and unloaded VOUT, including polarity | Required | Finds reversed input/output or wrong output setting. Does not prove load capacity. |
| S2 VBUS-to-GND during Wi-Fi operation | Required | Checks the controller's actual supply connection. Slow display may miss transients. |
| Servo connector supply during small motion, then gentle switch load | Required | Checks voltage delivered through the complete power path. Record reset/jitter/strain observations as well. |
| Converter VOUT versus load-end voltage during comparable motion | If the first motion fails or sags | A substantial difference points to lead/contact loss; sag at both ends points upstream. Sequential meter readings are only approximate for changing loads. |
| Minimum/maximum voltage, with meter model and capture speed | If available | Useful screening, but not a blanket transient pass. |
| Oscilloscope capture at servo supply and S2 VBUS/3V3 | Needed to resolve unexplained resets/jitter before claiming reliability | Separates brief dips/noise from slow average voltage. Not a required purchase before the first supervised motion. |
| Actual working-current peaks, temperature rise over intended duty cycle, lower-battery behavior | Before continuous/unattended approval | Establishes evidence for supply, protection and runtime choices. Do not obtain these by deliberately jamming the servo. |

A basic DMM showing 5.0 V can miss short disturbances. [Fluke's fast/peak min-max explanation](https://www.fluke.com/en-au/learn/blog/digital-multimeters/under-utilized-functions-how-to-use-fast-peak-min-max-on-your-dmm) makes clear that fast capture is a particular instrument feature, not something every meter's normal display or MIN/MAX mode guarantees. Stable readings and successful small movements are screening evidence, not proof of transient headroom.

## Essential now versus optional changes

- **Essential now:** correct measured voltage and polarity; secure insulated connections; clear USB power-source separation; common ground; inactive/disconnected signal when the servo is off; staged unloaded testing; immediate stop on electrical or mechanical trouble.
- **Not inherently needed for this first functional trial:** servo power gate, battery ADC, extra switch, WAGO connectors or a breadboard. Direct branch wiring can be simpler than rail distribution.
- **Signal resistor:** not a voltage regulator or automatic logic-level converter. It may limit fault/injection current or help signal integrity, but a random value does not establish powered-off safety or compatibility. Keep the signal at the ESP32's logic level; resolve actual input compatibility if it fails despite a sound supply.
- **Extra capacitor:** a possible response to measured transient trouble. It cannot repair poor joints, undersized sustained supply capacity or a jammed mechanism. A capacitor value and location should follow the observed problem and regulator requirements rather than being treated as a universal cure.
- **Fuse/current limiting:** valuable fault-energy protection, not required to make the logical circuit function. An unfused AA prototype is not protected merely because the voltage is low or someone is watching. The limited demo relies on careful disconnected-power assembly and immediate intervention; unknown wire/holder/servo current limits prevent selecting a defensible fuse rating here. Protection must be resolved before an unattended installation or a claim of fault tolerance.

No added component is a substitute for correcting a wiring fault or a stalled mechanism. The minimum circuit remains conditional on the physical checks above.
