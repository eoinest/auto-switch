# Selected direction: simplified AA demo

**Current POC:** [Switched AA holder + breadboard rails, one servo](poc-wiring.md). The WAGO assembly below is an earlier reference; use the POC parts checklist for this build.

Decision recorded 2026-09-05: use **four rechargeable AA NiMH cells**, a ready-made regulated 5 V supply, continuous Wi-Fi, and no GPIO-controlled servo power gate. The current build uses **one servo only**, controlling one paddle. The Mac mini relay is optional for direct phone control on the same local network.

The [Amazon-first shopping list](aa-demo-shopping.md) and [BOM CSV](../hardware/aa-demo-bom.csv) are now populated. Use the [illustrated breadboard viewer](../learn/aa-demo.html) or [one-servo image](../hardware/wiring/aa-demo/breadboard-1-servo.svg). Its wires, hole assignments, and connector ports pass an independent connectivity check. Physical operation remains untested.

Use [config.aa-demo.example.json](../firmware/config.aa-demo.example.json), following [firmware setup](firmware.md), for this ungated circuit. The old Demo networking setting alone is not the AA hardware profile. Existing STL exports and their fit report still describe the previous gated enclosure; no exact-fit claim is made for this bench assembly.

## Power plan

```text
4× AA NiMH holder + --> fuse --> physical master --> 5 V regulator VIN
holder - --------------------------------------------------- GND

regulator +5 V --------+---------------------------> servo power
                      |
                      +--> D1 anode --> cathode ---> Pico VSYS (pin 39)
                      |                stripe
                      +--> C1 positive

common GND -----------+---------------------------> servo GND
                      +---------------------------> Pico GND (pin 38)
                      +---------------------------> regulator/master GND
                      +---------------------------> C1 negative

Pico GP16 (pin 21) --> 1k series resistor ----------> servo signal
```

D1 isolates the external supply when USB powers the Pico for programming. Do not connect this battery/regulator to VBUS. With the battery master off, USB may still power the Pico; it does not power the servo branch through D1. Never connect four AA cells directly to Pico VSYS without ensuring the voltage stays within its input limits. Final diagrams must show actual connector orientation and all ground connections.

## Electrical parts overview

The authoritative installed quantities, Amazon listings, pack quantities, and specialty-part fallbacks are in the [shopping list](aa-demo-shopping.md). The overview below explains their roles. Reuse existing parts where suitable; new connector blocks and bench materials are included in the full BOM.

| Part | Installed quantity | Purpose / status |
| --- | --- | --- |
| Pico W; existing headered board for bench | 1 | Headerless option for the final assembly |
| Existing MG90S with original horn/screw | 1 | Actual geometry and loaded current still to verify |
| Four matched AA NiMH cells | 4 | Rechargeable AA; not an interchangeable alkaline or lithium profile |
| External NiMH charger | 1 shared | Cells removed for charging |
| [Pololu 1153 holder](https://www.pololu.com/product/1153) | 1 | Existing selected four-AA holder |
| [Pololu S18V20F5 / 2574](https://www.pololu.com/product/2574) | 1 | Existing 5 V step-up/step-down regulator; available output depends on battery voltage and cooling |
| [Pololu 2810 physical master](https://www.pololu.com/product/2810) | 1 | Retain one existing assembled switch, operated by its slider only; ON input unused |
| SCHURTER 0001.2507 2 A time-lag fuse + Littelfuse 01500274Z holder | 1 each | Existing selections; validate against measured pack current and wiring |
| 1N5819 diode | 1 | D1 in Pico supply branch; striped end toward VSYS |
| Panasonic EEUFR1A471 470 µF, 10 V capacitor | 1 | Starting bulk capacitor across regulated supply; polarity matters |
| 1 kΩ, 1/4 W series resistor | 1 | One per servo signal |
| RCY disconnect pair, servo extension, 22 AWG power wire, heat-shrink | 1 pair, 1 extension | Retain keyed connections and strain relief; verify actual polarity |
| Breadboard and logic jumpers; soldered harness for motor power | 1 shared | Use the checked one-servo layout below |
| Multimeter | 1 shared | Polarity, voltage, and battery checks |

The retained master contains MOSFETs internally, but it is a purchased physical on/off switch, with no Pico enable wire or control logic. We remove the **second** switch previously used as the servo gate. A suitably rated purely mechanical master can replace it later, with its connector and mount checked separately.

Remove the servo gate's GP15 connection, 100 kΩ enable pulldown, 1 kΩ output bleeder, and switched-output clamp diode. Remove the battery ADC divider (100 kΩ/47 kΩ) and its 100 nF filter for this supervised demo. No new connection to GP15 or GP26 is needed. The exact construction board, fasteners, and enclosure layout remain to be reconciled with the reduced circuit.

## Exact breadboard assembly

Use a 63-row, 830-point breadboard. With all power removed, fit the headered Pico with USB upward: its left header occupies **c3–c22**, right header **h3–h22**. Side power rails remain unused. Every a–e group in one row is connected; f–j is a separate group.

| Component / wire | From | To |
| --- | --- | --- |
| D1 1N5819 | a30, anode | a35, striped cathode |
| J1 | b35 | j4, Pico VSYS strip |
| J2 | b50 | j5, Pico GND strip |
| R_PWM0 1 kΩ | f30 | f35 |
| J3 | j22, GP16 strip | j30 |
| L1 | b30 | P5V connector port 3 |
| L2 | a50 | PGND_B connector port 2 |
| L3 | j35 | First servo signal via extension |

The selected diode leads may be thicker than a breadboard comfortably accepts. Do not force them: if needed, solder and individually insulate short 22 AWG solid-wire adapters while retaining the same endpoints and stripe orientation. No exposed conductor should touch another strip.

Use **three WAGO 221-415 blocks** with one wire per port. The numbered ports and all external wires are in the [shopping guide](aa-demo-shopping.md#how-the-three-junction-blocks-are-used) and [one-servo checklist CSV](../hardware/wiring/aa-demo/placements-1-servo.csv). Solder insulated pigtails onto the capacitor. Cut a matching servo extension to make the power/ground/signal breakout, preserving the original servo cable. Motor current stays on the external power harness, never through the breadboard.

Before applying power, check the list wire by wire, including the RCY connector's contact polarity and each module's silkscreen. **Lift out the Pico, disconnect USB and unplug the servo for initial voltage checks.** Connect the battery and turn on the master. With the black probe at free hole c50, measure c30 (nominal regulated 5 V), then c35 (diode output, lower than c30 and below 5.5 V). A nearly unloaded meter reading is not a test of regulator current capability or diode drop under load. Switch off and unplug the battery before reinserting the Pico. Then test one unloaded servo with the AA firmware's bounded neutral/calibration workflow before any switch pressing.

## Operating limits and remaining physical work

- This profile has no automatic depleted-pack cutoff or battery percentage. Use it for supervised demonstrations, check the cells with a meter, and switch off/recharge before depletion. Do not run it until it fails. The regulator's internal undervoltage limit is not a suitable four-cell NiMH cutoff. A later unattended profile needs an appropriate depletion strategy.
- Connect only one servo. GP17 remains unused. Battery input current can exceed output current when boosting voltage; the regulator's headline current rating does not establish margin for the fused holder and harness.
- The explicit ungated firmware profile leaves GP15 unused, disables absent ADC hardware, and retains motion calibration. Stopping PWM does not electrically disconnect the servo or guarantee torque release. Confirm the expected behavior on the actual board and servo.
- The AA maps and BOM are available for bench construction; the older lesson maps remain clearly labeled as the gated prototype.
- Update the Blender assembly and regenerate/verify STL exports after the electrical layout is settled. Existing battery/servo/Pico interfaces remain useful references, but removing components is not proof that a smaller enclosure will fit.
- Measure loaded servo behavior and actual average power. Previous runtime estimates assumed gated servos and must not be reused unchanged.

See [portable power comparison](portable-demo-research.md) for alternatives, sources, and the distinction between nominal design calculations and hardware measurements.

## Regeneration and verification

Run `python3 tools/render_aa_demo.py`, then `python3 tools/verify_aa_demo.py`. Run `python3 tools/build_aa_demo.py` after changing the BOM or guide to update the local viewer assets. `python3 -m unittest discover -s tests -p 'test_aa_demo.py'` checks the physical hole graph and deliberately broken SVG routes. The drawn component internals are simplified illustrations; module terminal orientation was inspected using [Pololu 2574 photos](https://www.pololu.com/product/2574/pictures) and [Pololu 2810 photos](https://www.pololu.com/product/2810/pictures). [Shopping source checks](aa-demo-source-checks.md).
