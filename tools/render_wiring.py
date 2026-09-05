"""Render an explanatory wiring map for the selected V2 parts (not a PCB layout)."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/wiring/connection-map.svg'
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000" viewBox="0 0 1400 1000">',
'''<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#486351"/></marker></defs>
<rect width="1400" height="1000" fill="#f7f8f3"/>
<style>text{font-family:Arial,sans-serif;fill:#20342a}.title{font-size:29px;font-weight:700}.sub{font-size:15px;fill:#54675b}.name{font-size:19px;font-weight:700}.detail{font-size:14px}.wire{fill:none;stroke:#486351;stroke-width:3;marker-end:url(#arrow)}.signal{fill:none;stroke:#b87922;stroke-width:3;stroke-dasharray:7 4;marker-end:url(#arrow)}.tag{font-size:13px;fill:#396143;font-weight:700}</style>''']

def text(x,y,content,cls='detail'):
    parts.append(f'<text x="{x}" y="{y}" class="{cls}">{escape(content)}</text>')

def box(x,y,w,h,name,lines,color='#e7edde'):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#9bab9b"/>')
    text(x+17,y+29,name,'name')
    for i,line in enumerate(lines):text(x+17,y+55+i*21,line)

def path(d,signal=False):
    parts.append(f'<path d="{d}" class="{"signal" if signal else "wire"}"/>')

text(40,50,'Auto Switch · selected parts and connections','title')
text(40,79,'4 × AA NiMH  →  regulated 5 V  →  Pico W + separately switched servos','sub')
box(40,120,230,118,'Battery holder',['Pololu 1153 · 4 AA cells','Red = positive','Black = common ground'])
box(325,120,180,118,'Fuse + plug',['Fuse near holder positive','Keyed battery disconnect','See shopping list'])
box(560,120,270,118,'Master switch',['Pololu 2810 LV','Use physical slide switch','ON input stays disconnected'])
box(920,120,370,118,'5 V regulator',['Pololu 2574 · S18V20F5','PACK_SW → VIN · VOUT → 5 V','Leave ENABLE disconnected'])
path('M 270 174 H 325');path('M 505 174 H 560');path('M 830 174 H 920')
text(843,160,'PACK_SW','tag')
box(920,307,370,95,'Bulk capacitor',['470 µF / ≥10 V across 5 V and GND','Negative stripe → GND'])
path('M 1110 238 V 307');text(1125,277,'5 V','tag')
box(920,465,370,121,'Servo power gate',['Pololu 2810 LV · physical slide OFF','VIN = 5 V · ON = GP15 (3.3 V logic)','VOUT feeds only the servos'])
path('M 1280 270 H 1330 V 518 H 1290');path('M 1110 270 H 1280')
box(920,658,370,116,'Servo plugs',['Ground / switched 5 V / signal','One plug per MG90S','Route motor returns straight to GND'])
path('M 1105 586 V 658');text(1120,626,'SERVO_5V','tag')
box(510,307,322,113,'Pico supply diode D1',['1N5819 · anode from regulated 5 V','Striped cathode → Pico VSYS pin 39','USB may power Pico independently'])
path('M 1010 270 H 668 V 307')
box(510,477,322,199,'Pico W / Pico 2 W',['Pin 39 VSYS ← diode D1','Pin 38 GND → common ground','Pin 20 GP15 → gate ON','Pin 21 GP16 → 1 kΩ → servo 0 signal','Pin 22 GP17 → 1 kΩ → servo 1 signal','Pin 31 GP26 ← battery ADC node'])
path('M 667 420 V 477')
path('M 832 548 H 920',True)
path('M 832 604 H 871 V 730 H 920',True)
box(40,307,375,146,'Battery voltage divider',['PACK_SW → 100 kΩ → ADC node','ADC node → 47 kΩ → GND','ADC node → 100 nF → GND','ADC node → GP26 (never raw pack)'])
path('M 870 174 V 271 H 231 V 307')
path('M 415 389 H 455 V 628 H 510',True)
box(40,506,375,172,'Small protection parts',['100 kΩ: gate ON input → GND','1 kΩ / ¼ W: SERVO_5V → GND','D2 1N5819 negative-spike clamp:','striped cathode → SERVO_5V','anode → GND'], '#f0e9d9')
box(40,736,792,86,'Every GND is common',['Battery black, both switches, regulator, Pico, capacitors and servo ground wires.'])
text(40,873,'Pin numbers refer to the Pico’s physical 40-pin edge headers, not GPIO numbers.','sub')
text(40,901,'The servo gate slider must remain OFF; ON bypasses the Pico’s power control.','sub')
text(40,929,'This battery build leaves VBUS unused. VBUS exposes USB 5 V, but has no software power switch.','sub')
text(40,957,'Functional connection map; follow docs/wiring.md for pinouts, harness assembly and meter checks.','sub')
parts.append('</svg>')
OUT.write_text('\n'.join(parts)+'\n')
print(OUT)
