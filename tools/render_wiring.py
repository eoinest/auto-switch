"""Generate editable SVG learning and wiring diagrams from the project's netlist.

Run from any directory. No runtime dependencies. The power map is an explanatory
availability diagram; the wiring sheet's terminal schedule is sourced verbatim
from harness.json and is the authoritative external connectivity on the sheet.
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

# Full wiring sheet: named nets avoid hidden junctions and crossed-wire ambiguity.
s=SVG(1800,2100,'Auto Switch — complete external wiring sheet','Functional circuit panels with named electrical nets, Pico physical pad assignments, all passive components, and an automatically generated exhaustive terminal schedule from harness.json. Matching net names mean connected wires. Pico internal USB power path is shown separately in power-map.svg.')
s.text(40,55,'Auto Switch · complete connection sheet','title')
s.text(40,87,f'Revision {HARNESS["revision"]} electrical nets · direct-solder Pico preferred · exact per-hole prototype-board routing is not supplied','subtitle')
s.rect(40,110,1720,67,'#eaf1f1')
s.text(60,138,'HOW TO READ THIS SHEET   Same net name = the same connected wire, wherever it appears.','body')
s.text(60,163,'Solid lines carry supply/return; blue dashes carry signals. A filled dot is a junction. No crossing wires imply a connection.','small')
s.text(40,216,'A   SOURCE AND PICO SUPPLY','section')
s.box(40,237,260,145,'BAT · 4 × AA NiMH',['Pololu 1153 holder','Red → F1 input','Black → GND'],'BAT','#fff4df')
s.box(360,237,285,145,'F1 + disconnect',['01500274Z fuse holder','0001.2507 · 2 A time-delay','JST RCY 2180 + 2181'],'F1','#fff4df')
s.box(705,237,295,145,'MASTER · Pololu 2810',['VIN ← FUSED_BAT','VOUT → PACK_SW','GND → GND · ON unused'],'MASTER','#fff4df')
s.box(1060,237,310,145,'REG · Pololu 2574',['VIN ← PACK_SW','VOUT → 5V · GND → GND','ENABLE left unconnected'],'REG','#ffece4')
s.path('M300 308H360','battery');s.path('M645 308H705','battery');s.path('M1000 308H1060','battery');s.path('M1370 308H1410')
s.box(1410,237,350,145,'D1 · 1N5819',['Anode ← 5V','Striped cathode → VSYS','VSYS → Pico pad 39'],'D1','#ffece4')
s.text(40,412,'BAT_POS: holder + to fuse. FUSED_BAT passes through RCY to master VIN. RCY also disconnects the GND lead.','small')
s.text(40,437,'Pico USB/VBUS and its onboard diode are separate from D1. See power-map.svg for the complete internal power path.','small')
s.text(40,485,'B   CONTROLLER PADS','section')
s.box(40,506,505,339,'PICO W / PICO 2 W',['39 · VSYS ← D1 cathode','38 · GND → common GND','20 · GP15 → SERVO_ENABLE (gate ON)','21 · GP16 → PWM0_RAW → R_PWM0','22 · GP17 → PWM1_RAW → R_PWM1','31 · GP26 / ADC0 ← ADC','40 · VBUS: no external wire','36 · 3V3 OUT: no external wire'],'PICO','#edf5ef')
s.text(59,826,'Numbers identify pads even without soldered headers.','small')
s.text(590,485,'C   MOTOR POWER AND LOGIC','section')
s.box(590,506,410,158,'GATE · Pololu 2810 LV',['VIN ← 5V · VOUT → SERVO_5V','ON ← SERVO_ENABLE · GND → GND','Keep physical slider OFF.','GP15 is 3.3 V logic, not motor power.'],'GATE','#ffece4')
s.box(1055,506,335,158,'SERVO0 · MG90S',['Power ← SERVO_5V','Ground → GND','Signal ← PWM0','Use original servo mating plug.'],'SERVO0','#fff')
s.box(1430,506,330,158,'SERVO1 · MG90S',['Power ← SERVO_5V','Ground → GND','Signal ← PWM1','Omit for one-gang version.'],'SERVO1','#fff')
s.path('M1000 577H1055');s.text(1008,486,'SERVO_5V','net',COLORS['motor'])
s.text(590,704,'PWM0_RAW','net',COLORS['signal']);s.path('M725 698H760','signal',True,False)
s.resistor(760,698,'R_PWM0','1 kΩ');s.path('M842 698H973','signal',True);s.text(899,681,'PWM0','net',COLORS['signal'])
s.text(1080,704,'PWM1_RAW','net',COLORS['signal']);s.path('M1215 698H1250','signal',True,False)
s.resistor(1250,698,'R_PWM1','1 kΩ');s.path('M1332 698H1463','signal',True);s.text(1390,681,'PWM1','net',COLORS['signal'])
s.text(590,791,'Each servo has its own signal; both share power and ground.','body')
s.text(590,819,'Run motor + and return on direct power wiring. A Pico GPIO carries only the control signal.','small')
s.text(40,890,'D   PASSIVES · ADD ALL OF THESE TO THE NAMED NETS','section')
# Input capacitor.
s.rect(40,912,325,351,'#fff')
s.text(60,945,'C1 · supply buffer','name');s.text(60,973,'470 µF / 10 V','body')
s.text(95,1014,'5V','net',COLORS['regulated']);s.path('M125 1030V1080',arrow=False)
s.path('M99 1080H151M99 1094H151',arrow=False);s.text(159,1076,'+','name');s.text(159,1111,'− stripe','small')
s.path('M125 1094V1175','ground',arrow=False);s.ground(125,1175)
s.text(60,1231,'Close to gate VIN and GND.','small')
# Gate enable pulldown.
s.rect(385,912,335,351,'#fff');s.text(405,945,'R_EN · default off','name');s.text(405,981,'SERVO_ENABLE','net',COLORS['signal'])
s.resistor(440,1000,'R_EN','100 kΩ',True);s.path('M440 1072V1175','ground',arrow=False);s.ground(440,1175)
s.text(405,1209,'Pull gate ON toward GND','small');s.text(405,1231,'while GPIO is not driving it.','small')
# Switched rail diode + bleeder.
s.rect(740,912,510,351,'#fff');s.text(760,945,'D2 + R_BLEED · shutoff','name');s.text(760,982,'SERVO_5V','net',COLORS['motor'])
s.path('M790 1002H1070',arrow=False);s.dot(850,1002);s.dot(1070,1002)
s.path('M850 1002V1040',arrow=False);s.diode(850,1112,'',True,'regulated');s.text(874,1047,'D2','net');s.text(874,1074,'1N5819','small');s.text(874,1101,'stripe ↑','small')
s.resistor(1070,1002,'R_BLEED','1 kΩ, ¼ W',True,'regulated')
s.path('M850 1112V1175H1070V1074','ground',arrow=False);s.ground(965,1175)
s.text(760,1210,'D2: anode at GND, cathode at servo +.','small');s.text(760,1233,'Bleeder discharges the switched rail.','small')
# Divider.
s.rect(1270,912,490,351,'#fff');s.text(1290,945,'Battery divider + filter','name');s.text(1290,978,'PACK_SW','net',COLORS['battery'])
s.resistor(1320,989,'R_TOP','100 kΩ, 1%',True,'adc');s.dot(1320,1061,'adc');s.path('M1320 1061H1675','adc',False,False);s.text(1550,1044,'ADC → GP26','net',COLORS['adc'])
s.resistor(1320,1061,'R_BOTTOM','47 kΩ, 1%',True,'adc');s.path('M1320 1133V1175H1620V1127','ground',arrow=False);s.ground(1470,1175)
s.dot(1620,1061,'adc');s.path('M1620 1061V1114','adc',False,False);s.path('M1600 1114H1640M1600 1127H1640','adc',False,False);s.text(1469,1107,'C_ADC','net');s.text(1469,1136,'100 nF','small')
s.text(1290,1210,'V_ADC = V_PACK_SW × 47 / 147','small');s.text(1290,1233,'At 4.8 V nominal: about 1.53 V.','small')
s.text(40,1308,'E   COMPLETE TERMINAL SCHEDULE · GENERATED FROM hardware/wiring/harness.json','section')
s.text(40,1340,'Use board silkscreen for the real pad layout. These are electrical connections, not cable colors or physical positions.','small')
y=1363
for i,(net,terminals) in enumerate(HARNESS['nets'].items()):
    # Up to two wrapped lines; deliberately readable instead of shrinking type.
    chunks=[]; current=''
    for terminal in terminals:
        proposed=current+('  ·  ' if current else '')+terminal
        if len(proposed)>135:
            chunks.append(current);current=terminal
        else:current=proposed
    chunks.append(current)
    height=28*len(chunks)+14
    s.rect(40,y,1720,height,'#edf1ee' if i%2==0 else '#fff','#dce3df',0)
    s.text(55,y+27,net,'net')
    for row,line in enumerate(chunks):s.text(280,y+27+28*row,line,'mono')
    y+=height
s.text(40,y+33,'LEFT UNCONNECTED: '+', '.join(HARNESS['leave_unconnected']),'small')
s.text(40,y+61,'ONE-GANG BUILD: omit SERVO1 and R_PWM1. Only one motor moves at a time in firmware.','small')
s.text(40,y+89,'Bench verification required: net continuity, polarity, regulated voltage, startup droop and actual servo current.','small')
s.text(40,y+117,'Sources: Raspberry Pi Pico W datasheet §§3.4–3.5; Pololu 2810 and 2574 documentation; docs/wiring.md.','small')
# Accommodate any future growth in the terminal schedule without cutting content.
needed=y+146
s.items[0]=s.items[0].replace('height="2100"','height="'+str(needed)+'"').replace('0 0 1800 2100','0 0 1800 '+str(needed))
# Background dimensions update independent from construction ordering.
s.items=[v.replace('<rect width="1800" height="2100"','<rect width="1800" height="'+str(needed)+'"') for v in s.items]
s.save('connection-map.svg')
