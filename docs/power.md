# Power and battery life

## Recommended first build

Use four removable **AA NiMH** cells, a regulated **5 V buck-boost** supply, and a **high-side servo power switch**. AA is a more practical prototype starting point than AAA for servo pulses and energy capacity. The Mac mini runs the local gateway and phone website. **Demo mode** keeps Wi-Fi connected and polls every second; **Daily mode** disables the WLAN interface between configurable polls (60 seconds by default). Ordinary waiting in Daily mode is not deep sleep. Expect runtime to depend heavily on measured board waiting current; months are not established.

Panasonic's cited cell family lists minimum capacities of 1900 mAh for AA and 750 mAh for AAA at nominal 1.2 V. Four cells in series provide 4.8 V nominal; capacity remains 1900 or 750 mAh. That is about **9.12 Wh for four AA**, or **3.6 Wh for four AAA**. Other cell generations differ: use the wrapper rating and measured usable energy. [Panasonic eneloop specifications](https://www.panasonic.com/global/energy/products/eneloop/en/lineup/eneloop.html).

Fresh four-cell packs can exceed Pico's direct-input limit. Do not connect this pack straight to VSYS, 3V3, a GPIO, or the servo without confirming all ratings. Do not substitute four alkaline cells without re-evaluating the battery profile and cutoff. The regulator's minimum input limit is not an appropriate NiMH discharge cutoff. Stop use at the selected battery cutoff and recharge the cells externally; never use a Li-ion charging module for NiMH.

## Wiring contract

```text
4 × AA NiMH series pack
  positive -> fuse near pack -> master switch -> PACK+ (sense here)
  negative ---------------------------------------- COMMON GND

PACK+ -> 5 V buck-boost VIN
GND   -> regulator GND
regulator 5 V OUT -> +5V

+5V -> Schottky diode ANODE -> CATHODE (stripe) -> Pico VSYS (pin 39)
+5V -> bulk capacitor + ; capacitor - -> GND
+5V -> high-side load-switch VIN
load-switch VOUT -> servo red power wires
load-switch GND  -> COMMON GND
load-switch EN   <- GP15 (pin 20), with 100k pulldown to GND
servo brown/black ground -> COMMON GND (direct short power return)
GP16 -> 1k resistor -> first servo signal
GP17 -> 1k resistor -> second servo signal, if used
Pico GND -> COMMON GND

PACK+ -> 100k -> ADC node -> 47k -> GND
ADC node -> GP26 / ADC0 (pin 31)
ADC node -> 100nF -> GND
```

Verify actual connector polarity: wire colors are conventions. Regulator/load-switch local bypass capacitors, rise-time components, discharge network, and layout must follow the selected module's documentation. This functional wiring diagram is not a fabricated and tested PCB schematic.

The Pico's USB-to-VSYS diode and the external Schottky diode form supply ORing. USB can power the Pico while the external supply is connected, without feeding the servo rail or cells through VSYS. **Do not bridge VBUS and VSYS**, and do not connect the battery or regulator directly to VBUS. Place the external diode close to Pico. This follows Raspberry Pi's recommended external-power arrangement. [Raspberry Pi hardware design guide, power section](https://pip.raspberrypi.com/documents/RP-008279-DS).

The servo must get motor current from its own switched branch. Do not run it from Pico 3V3, a GPIO, or a computer USB port through the Pico traces. Use common ground and keep motor return current out of the ADC ground path. Tie the enable low in hardware so reset and unconfigured GPIO cannot intentionally enable the servo rail. Software drives signal low before/after power removal to reduce signal back-powering. A series resistor limits fault current; it is not a level shifter. If the servo cannot reliably accept 3.3 V PWM, add an appropriate unidirectional 3.3-to-5 V buffer with power-off isolation and verify its power sequencing.

The TPS22918 is an example **2 A, 1–5.5 V high-side load switch** with a GPIO-compatible enable, configurable rise time, and output discharge. It does not provide a current limiter. Use a documented assembled carrier/EVM or a correctly laid out circuit; the tiny bare IC is not a beginner wire-in component. Configure controlled startup and output discharge according to the carrier/datasheet so the disconnected servo rail falls promptly. Do not replace it with an unspecified low-side MOSFET module: switching ground can leave the servo powered through its signal. [TI TPS22918](https://www.ti.com/product/TPS22918).

A possible regulator is the **Pololu S18V20F5**. It handles voltages above and below 5 V, has reverse-input protection, and has about 1 mA typical no-load consumption under many conditions. Current capability depends on input voltage and thermal conditions; the 2 A headline is not a guarantee at every battery voltage. Leave its ENABLE unconnected in this first power design; the regulator remains on in both modes. Its enable is pulled toward VIN, so do not connect it directly to a Pico GPIO. [Pololu regulator documentation](https://www.pololu.com/product/2574).

Start with 470–1000 µF bulk capacitance rated at least 10 V on the unswitched regulated 5 V rail and local ceramics at the switch/module as specified. Check startup inrush and output droop with the actual load. A capacitor helps short transients; it cannot supply a sustained stall or make an undersized regulator adequate. Choose the fuse only after measuring input peaks: its current and time characteristic must protect the weakest wire/connector/holder without tripping on normal startup. Do not solder directly to cells.

## Measuring the battery

The external divider measures the **unregulated pack**, since regulated VSYS would remain nearly constant as the cells discharge. `Vpack = ADC_voltage × (100 + 47) / 47`, so the nominal scale is **3.12766**. At a deliberately conservative 6.4 V pack check, ADC voltage is about 2.05 V, below 3.3 V with 1% resistor tolerance. At 4.8 V the divider consumes about 33 µA. A 100 nF capacitor at the ADC provides filtering; allow at least 20 ms after power-up before sampling, average readings, and calibrate against a meter.

Master off must remove the divider supply as well as regulator input; otherwise an unpowered Pico can be back-powered through its ADC. The regulator's reverse-input protection does not protect the separate divider branch. Use a keyed holder/connector and check polarity before connection; add reverse-polarity protection ahead of both paths for a user-proof assembly. Do not sample a raw battery voltage directly on GP26.

Show measured pack volts and a low-battery warning first. NiMH's fairly flat discharge voltage, servo sag, temperature, and cell imbalance make a voltage-derived percentage only an estimate. A four-cell voltage does not reveal one weak or reversed cell. Test a cutoff around **4.4 V under a repeatable rested/light load** as a conservative initial calibration point, check individual cells, and adjust from the cell maker's limits and actual voltage sag. This number is a project starting assumption, not a certified battery protection threshold. A runtime estimate requires a measured current/energy model; accurate state of charge requires more instrumentation, such as a suitably chosen coulomb counter plus calibration. Do not substitute a single-cell Li-ion fuel-gauge module blindly.

## What runtime to expect

All currents below are **illustrative assumptions, not measured Pico W or MG90S specifications**. They show why keeping Wi-Fi reachable dominates small batteries. “50 mA” here means logic current seen at the regulated **5 V rail**, not 3.3 V chip current.

The bundled estimator separately models 80% accessible nominal battery energy, 85% conversion efficiency, 1.04 mA pack-side parasitics, 500 mA servo current at 5 V for 1 second total press-and-return time, and 20 actions per day across all servos. With those assumptions:

| Always-awake logic current at 5 V | Four AAA, 750 mAh | Four AA, 1900 mAh |
| --- | --- | --- |
| 20 mA | about 23 hours | about 59 hours |
| 50 mA | about 9.6 hours | about 24 hours |
| 100 mA | about 4.8 hours | about 12 hours |

At 50 mA, logic uses 6 Wh/day before conversion losses. The assumed 20 servo actions use only about 0.014 Wh/day. Frequent switching or a longer powered return changes the servo term, but servo idle holding is the avoidable cost: cut its power after each completed action. Use **total** press + return powered time, and count ON and OFF separately. Energy sufficiency does not establish that AAA can deliver required pulse current without brownout.

Run from the monorepo root:

```sh
python3 tools/battery_estimator.py
python3 tools/battery_estimator.py --capacity-mah 750 --active-ma 50 --json
python3 tools/battery_estimator.py --interval-seconds 60 --wake-seconds 3 --sleep-ma 10 --wake-ma 80
python3 -m unittest discover -s tests -p 'test_battery_estimator.py'
```

The estimator reports its assumptions and energy components. `usable_fraction` accounts for inaccessible capacity/cutoff, `efficiency` accounts for load conversion, and `parasitic_pack_ma` accounts for additional pack-side current. When entering measured whole-device battery current, avoid also counting component currents and conversion losses a second time. Self-discharge, cell aging, cold, capacity variation, and failed-network retries still require real validation.

## Daily and Demo network modes

The **Mac mini hosts the local gateway and phone UI**. It stores queued commands while the Pico is offline. The Pico W or Pico 2 W is an HTTP client of that gateway. Use the MicroPython UF2 specifically for the board in hand. A phone does not need to connect directly to a sleeping board. Other automations can use the documented HTTP API; an MCP protocol adapter is not included.

**Demo mode** keeps Wi-Fi associated and polls about every second. This gives roughly one-second command pickup, plus network and mechanical time, while drawing continuous connected-board power. The preceding always-awake table approximates this case using assumed measured-at-5-V board currents.

**Daily mode** turns the WLAN interface off between polls. The configurable interval is 10–3600 seconds, default 60; common UI choices are 30, 60, 300, and 900 seconds. This means daily use, not one wake every 24 hours. Commands wait up to roughly the interval plus reconnection time. A queued request to enter Demo also waits until the next poll; reboot/manual intervention may be faster when commissioning. The Mac mini must remain reachable and awake. Gateway electricity is outside the node battery estimate.

Daily mode uses ordinary asynchronous waiting with the radio interface disabled, not a claimed ultra-low-power suspend state. `WLAN.active(False)` describes interface state; it does not prove a measured whole-board current. The Pico, regulator, and other circuitry may still draw milliamps. MicroPython explicitly says sleep behavior depends on hardware. Current RP2 implementation also limits timed `lightsleep` calls to less than roughly 71 minutes and can return early for pending wireless work. Do not infer ESP32 sleep numbers for Pico W, or apply direct internal GPIO manipulation to the radio. [MicroPython machine documentation](https://docs.micropython.org/en/v1.28.0/library/machine.html), [RP2 sleep implementation](https://github.com/micropython/micropython/blob/master/ports/rp2/modmachine.c).

With the same batteries, efficiency, parasitics, and servo assumptions above, but **80 mA at 5 V during a 3-second association/poll** and the following assumed radio-off waiting current:

| Radio-off waiting current at 5 V | Four AA, 60-second polls | Four AA, 5-minute polls |
| --- | --- | --- |
| 5 mA (unmeasured scenario) | about 5.3 days | about 7.7 days |
| 10 mA (estimator default assumption) | about 3.6 days | about 4.4 days |
| 20 mA (unmeasured scenario) | about 2.2 days | about 2.4 days |
| 1 mA (experimental target, not established) | about 8.7 days | about 19 days |

These estimates show that longer intervals provide diminishing returns when the board's waiting current dominates. Four AAA would provide about 39% of these energy-based runtimes if they could supply the same peaks; that pulse-current condition needs testing. Replace the current assumptions with measurements on the actual Pico/UF2, disconnected from USB and debugger, with the finished regulator and servo switch.

Association cost matters. Let `Ic` be continuously connected current, `Is` radio-off waiting current, `Iw` average association/poll current, `tw` time spent reconnecting, and `T` poll interval; use the same measurement rail for all currents. Ignoring the common actuation cost, polling saves energy when:

```text
Is + (Iw - Is) × tw / T < Ic
T > tw × (Iw - Is) / (Ic - Is)    [requires Ic > Is]
```

For **assumed** `Ic=50 mA`, `Is=10 mA`, `Iw=80 mA`, `tw=3 s`, break-even is **5.25 seconds**. That is not a measured break-even. Measure current integrated over successful association, DHCP, transfer, and retries. For a measured excess reconnect energy `E` in joules and measured standby-power saving `deltaP` in watts, the measured break-even is `E / deltaP` seconds. Poor reception, a sleeping Mac mini, or unavailable Wi-Fi can erase the saving; connection timeouts and retry backoff must be bounded. The estimator includes `polling_break_even_seconds` in JSON and conservatively adds actuation-awake time to polling-awake time.

**Future improvement:** verify a specific low-power firmware/suspend path across repeated wake/reconnect cycles, or use an external timer/low-quiescent load switch to power the whole node only for polls. Full power-off must also isolate the battery ADC and unpowered signal paths, preserve command deduplication appropriately, and provide a way to enter Demo. A lower-quiescent regulator matters: even 1 mA pack-side overhead alone consumes about 0.115 Wh/day. Months of life require this hardware/firmware work and a complete measured discharge test; merely adding `sleep()` is insufficient.

## Bench validation before installing

1. Check board variant, servo voltage range, regulator output, all polarity, and ADC divided voltage with a meter before connecting the Pico.
2. Start with the servo disconnected; confirm the high-side enable is off during power-up, reset, USB connection, and firmware failure.
3. Attach one unloaded servo with its horn removed; center it, establish safe small pulse limits, and confirm power removal.
4. Measure input current and regulated-rail droop during motion, startup, and short controlled resistance on a fixture. Do not intentionally hold a servo stalled against the installed wall switch.
5. Fit the frame and arm, use the smallest press that clicks, return fully clear, then test repeated alternating presses. Verify the frame does not peel or creep and manual operation remains accessible.
6. Test low battery, reboot during motion, jammed mechanism, disconnected Wi-Fi, and interrupted requests. A software timeout is not proof against mechanical overload or a hardware fault.
7. Log pack energy and successful actions over a complete discharge cycle. Replace estimator assumptions with measurements before claiming a battery life or leaving the prototype unattended.
