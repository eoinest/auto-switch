"""Generate editable SVG learning and wiring diagrams from the project's netlist.

Run from any directory. No runtime dependencies. The power map is an explanatory
availability diagram; the connection map draws every harness terminal in one
continuous circuit. Geometry tests bind the drawn wires to harness.json.
"""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/wiring'
HARNESS = json.loads((OUT / 'harness.json').read_text())
COLORS = {'battery':'#ad5c12', 'regulated':'#ba421f', 'pico':'#ba421f', 'usb':'#7354b3', 'vsys':'#7354b3', 'chip':'#187451', 'motor':'#ba421f', 'ground':'#344858', 'signal':'#176e99', 'adc':'#137b7d'}

class SVG:
    def __init__(self, width, height, title, desc):
        self.w, self.h = width, height
        self.items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="diagram-title diagram-desc">', f'<title id="diagram-title">{escape(title)}</title>', f'<desc id="diagram-desc">{escape(desc)}</desc>', '''<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>
<style>
text{font-family:Arial,Helvetica,sans-serif;fill:#233942}.title{font-size:34px;font-weight:700;letter-spacing:-.7px}.subtitle{font-size:19px;fill:#53636b}.name{font-size:22px;font-weight:700}.body{font-size:18px}.small{font-size:16px;fill:#53636b}.micro{font-size:14px;fill:#53636b}.net{font-size:17px;font-weight:700;letter-spacing:.3px}.mono{font-family:monospace;font-size:16px}.wire{fill:none;stroke-width:4;stroke-linejoin:round;stroke-linecap:round}.signal{stroke-dasharray:8 6;stroke-width:3}.is-off{opacity:.2} .component{cursor:pointer} .section{font-size:17px;font-weight:700;letter-spacing:1.4px;fill:#53636b}
</style>''', f'<rect width="{width}" height="{height}" fill="#f7f6f0"/>']
    def text(self,x,y,value,cls='body',fill=None):
        self.items.append(f'<text x="{x}" y="{y}" class="{cls}"'+(f' style="fill:{fill}"' if fill else '')+f'>{escape(str(value))}</text>')
    def rect(self,x,y,w,h,fill='#fff',stroke='#b5c5c9',radius=14):
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    def box(self,x,y,w,h,title,lines=(),part=None,fill='#fff'):
        if part:self.items.append(f'<g data-part="{part}" class="component">')
        self.rect(x,y,w,h,fill)
        self.text(x+18,y+32,title,'name')
        for n,line in enumerate(lines):self.text(x+18,y+61+n*25,line,'body')
        if part:self.items.append('</g>')
    def path(self,d,color='regulated',signal=False,arrow=True):
        c=COLORS.get(color,color)
        self.items.append(f'<path d="{d}" class="wire'+(' signal' if signal else '')+f'" stroke="{c}"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def dot(self,x,y,color='regulated'):
        self.items.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{COLORS.get(color,color)}"/>')
    def group(self,id):self.items.append(f'<g id="{id}">')
    def end(self):self.items.append('</g>')
    def ground(self,x,y):
        self.path(f'M{x} {y}v12m-15 0h30m-24 7h18m-12 7h6','ground',arrow=False)
    def resistor(self,x,y,label,value,vertical=False,color='signal'):
        if vertical:
            self.path(f'M{x} {y}v15m0 42v15',color,arrow=False)
            self.rect(x-8,y+15,16,42,'#fff',COLORS[color],0)
            self.text(x+19,y+32,label,'net');self.text(x+19,y+55,value,'small')
        else:
            self.path(f'M{x} {y}h15m52 0h15',color,arrow=False)
            self.rect(x+15,y-9,52,18,'#fff',COLORS[color],0)
            self.text(x+3,y-25,label,'net');self.text(x+7,y+38,value,'small')
    def diode(self,x,y,label,vertical=False,color='regulated'):
        # Diode symbol with marked cathode bar; outline triangle gives anode->cathode.
        transform=f'translate({x} {y})'+(' rotate(-90)' if vertical else '')
        self.items.append(f'<g transform="{transform}"><path d="M0 0H20M50 0H72M20 -14L46 0L20 14Z M48 -15V15" fill="white" stroke="{COLORS[color]}" stroke-width="3"/></g>')
        if label:self.text(x,y+37,label,'small')
    def save(self,name):
        target=OUT/name
        target.write_text('\n'.join(self.items+['</svg>'])+'\n')
        print(target)

s=SVG(1500,1320,'Auto Switch — follow the power into the Pico','Battery power passes through a fuse, disconnect, master switch and five volt regulator. One branch feeds external diode D1 and Pico VSYS pad 39, then its onboard regulator powers the chip at 3.3 volts. USB feeds VBUS and its separate onboard diode into VSYS. The other five volt branch powers the servo gate. Blue dashed lines are logic. All grounds are connected.')
s.text(40,55,'Where does the Pico get its power?','title')
s.text(40,87,'Two ways in. One 3.3 V supply inside. Motor power takes its own branch.','subtitle')
s.text(40,137,'1   BATTERY SUPPLY · PARTS YOU ADD','section')
s.group('path-battery')
s.box(40,165,210,140,'Four AA cells',['NiMH · 4.8 V nominal','Varies with charge','Pololu 1153 holder'],'BAT','#fff4df')
s.box(290,165,165,140,'Fuse F1',['2 A time-delay','Near battery +','5 × 20 mm'],'F1','#fff4df')
s.box(495,165,150,140,'RCY plug',['Detachable','2180 + 2181','Check polarity'],'RCY','#fff4df')
s.box(690,165,240,140,'Master switch',['Pololu 2810 LV','Use physical slider','ON pad left unused'],'MASTER','#fff4df')
s.path('M250 235H290','battery');s.path('M455 235H495','battery');s.path('M645 235H690','battery')
s.end()
s.group('path-pack-sw')
s.path('M930 235H1080','battery')
s.text(949,211,'PACK_SW','net',COLORS['battery'])
s.end()
s.group('path-regulated')
s.box(1080,165,380,140,'External 5 V regulator',['Pololu 2574 · S18V20F5','Makes steady 5 V from the pack','ENABLE pad left unused'],'REG','#ffece4')
s.path('M1268 305V357H800V415')
s.dot(1268,357);s.text(965,339,'REGULATED 5 V','net',COLORS['regulated'])
s.end()
s.text(40,392,'2   THE PICO BRANCH','section')
s.rect(390,575,630,480,'#edf5ef','#68a184',20)
s.group('path-pico-external')
s.box(605,415,385,110,'External diode D1',['1N5819 · stripe toward VSYS','Prevents USB feeding the servo rail'],'D1','#ffece4')
s.path('M800 525V593','pico')
s.text(605,556,'5 V minus a diode drop','small')
s.end()
s.text(414,620,'PICO W / PICO 2 W BOARD','name')
s.text(414,647,'Already built into the board below this line','small')
s.text(820,591,'39 · VSYS','net',COLORS['vsys'])
s.group('path-usb')
s.box(40,688,245,120,'Optional USB cable',['Nominal 5 V from a host','Programming / testing'],'USB','#f0eafa')
s.path('M285 748H421','usb')
s.text(414,714,'40 · VBUS','net',COLORS['usb'])
s.diode(563,748,'',False,'usb')
s.path('M421 748H563','usb');s.path('M635 748H800','usb')
s.text(541,690,'Onboard diode','net');s.text(529,716,'Already on the Pico','small')
s.end()
s.group('path-vsys')
s.path('M800 593V748','vsys',arrow=False);s.dot(800,748,'vsys');s.path('M800 748V802','vsys')
s.text(825,744,'VSYS junction','net',COLORS['vsys'])
s.box(680,802,300,91,'Onboard regulator',['VSYS → regulated 3.3 V'],None,'#fff')
s.end()
s.group('path-3v3')
s.path('M830 893V974H710','chip')
s.text(741,957,'3.3 V','net',COLORS['chip'])
s.box(425,933,285,83,'Chip + Wi-Fi',['This is what runs your code.'],'PICO','#dbedde')
s.end()
s.text(414,1040,'Pin numbers also identify solder pads on a headerless Pico.','small')
s.group('path-motor-input')
s.path('M1268 357V415','motor')
s.box(1080,415,380,166,'Servo power gate',['Pololu 2810 LV · slider stays OFF','VIN receives regulated 5 V','ON receives a 3.3 V control signal','GPIO decides; MOSFET carries power.'],'GATE','#ffece4')
s.end()
s.group('path-motor-output')
s.path('M1380 581V673','motor');s.text(1200,626,'SWITCHED SERVO_5V','net',COLORS['motor'])
s.box(1130,673,330,134,'MG90S servo(s)',['Separate power and signal wires','One or two independent motors','Power is disconnected when idle.'],'SERVO0','#ffece4')
s.end()
s.group('path-control')
s.path('M1020 876H1050V547H1080','signal',True)
s.text(1039,863,'20 · GP15 → ON','net',COLORS['signal'])
s.end()
s.group('path-pwm')
s.path('M1020 927H1097V765H1130','signal',True)
s.text(1071,934,'21 / 22 · GP16 / GP17','net',COLORS['signal'])
s.text(1103,960,'PWM → 1 kΩ → servo signal','small')
s.end()
s.group('path-adc')
s.box(40,423,310,199,'Battery measurement',['PACK_SW → 100 kΩ → ADC','ADC → 47 kΩ → GND','ADC → 100 nF → GND','ADC → pad 31 / GP26','Before the 5 V regulator.'],'ADC','#e4f2f2')
s.text(40,648,'Same PACK_SW net as the master output.','small')
s.end()
s.group('path-ground')
for gx,gy in [(135,305),(725,305),(1440,305),(160,808),(1100,581)]:
    s.path(f'M{gx} {gy}v12','ground',arrow=False);s.ground(gx,gy+12)
    s.text(gx+20,gy+23,'GND','small')
s.path('M55 1108H1450','ground',arrow=False)
s.ground(55,1108)
s.path('M567 1016V1108','ground',arrow=False);s.dot(567,1108,'ground')
s.text(590,1087,'38 · GND','net',COLORS['ground'])
s.path('M1440 807V1108','ground',arrow=False);s.dot(1440,1108,'ground')
s.text(40,1150,'COMMON GND: battery −, USB GND, Pico, regulator, both switches, servos and passive returns.','body')
s.text(40,1178,'This is the return path. Connect motor returns at the power assembly; do not route motor current through the Pico.','small')
s.end()
s.rect(40,1210,1420,77,'#fff')
s.text(60,1241,'Read the arrows as available power paths, not measured current. Blue dashes carry control / measurement signals.','body')
s.text(60,1268,'USB alone powers the Pico, not the motors. With both sources: the higher post-diode voltage usually wins; near-equal sources can share.','small')
s.save('power-map.svg')

# Complete circuit: every harness wire joins its actual endpoints on one map.
from continuous_wiring import draw
draw(SVG, HARNESS)
