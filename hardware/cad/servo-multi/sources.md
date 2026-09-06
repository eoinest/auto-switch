# Multi-switch design dimensions and scope

The user reports the existing single-switch measurements are confirmed. These variants use that design as their baseline; this work does not request another measurement of the single assembly or overwrite its files. No numeric double/triple plate measurements were supplied in this turn, so their spacing and outside envelopes use the nominal manufacturer references below.

| Input | Design basis |
|---|---|
| Switch center spacing | 46.0 mm nominal, manufacturer drawing |
| Standard single-plate envelope | Existing baseline 69.85 × 114.3 mm |
| Double-plate envelope | Baseline width + 46 = 115.85 × 114.3 mm |
| Triple-plate envelope | Baseline width + 92 = 161.85 × 114.3 mm |
| Servo/horn/rocker baseline | Existing `../servo-command/config.json`; user-reported confirmed single dimensions |
| Narrow Command 17207 outline | Existing 92.7354 × 12.6492 mm reservation; one mating pair on each outer pad |
| New middle mechanism | Raised pivot and revised contact positions require new mechanical testing; single-fit confirmation does not validate this new geometry |

Leviton's [wallplate size guide](https://leviton.com/content/dam/leviton/commercial-industrial/product_documents/solution_sheets/Wallplate%20Size%20Guide%20Q-1289.pdf) lists standard Decora plates approximately 69.8 × 114.3 mm and 46.0 mm additional width per gang. Its [80409 two-gang drawing](https://leviton.com/content/dam/leviton/residential/product_documents/product_specification/Q-874A%20Special%20Purpose%20Wallplates%20PB.pdf) explicitly shows 1.812 inch (46.0 mm) opening center spacing. These nominal outside dimensions describe a standard plate; larger midway/oversize plates exist.

The [Command 17207 product page](https://www.command.com/3M/en_US/p/d/b5005604166/) and [manufacturer catalog sheet](https://media.digikey.com/pdf/Data%20Sheets/3M%20PDFs/17207.pdf) identify the narrow picture-hanging strips. We retain the 14.5 × 116 mm outer adhesive pads; the additional length puts the saddle screws beyond the strip footprint. An 11 mm gap between nominal 35 mm bezels on 46 mm centers is too narrow for a 12.65 mm strip, so no strip is placed between rockers. Use the manufacturer's approved smooth surface. Separate the interlocking pairs and lift the frame away to expose the wall-side release tabs before stretch-removing those strips. No advertised picture weight rating establishes tested repeated-actuation capacity for this design.

## Electrical scope

This is a mechanical extension. Two- and three-switch models use two and three independent MG90S servos respectively. The running S2 POC remains configured for one servo: its wiring, software configuration and converter peak-current capacity have not been changed or validated for these variants. Do not infer that the existing one-servo power circuit is already qualified for simultaneous multi-servo operation.

Sources checked 2026-09-05. No mains wiring or replacement of the existing wallplate is part of the design.
