#!/usr/bin/env python3
"""Deterministic component illustrations and exact-hole AA demo wiring.

Cosmetic internals are illustrative; terminal orientation follows manufacturer
photos linked in the build guide. Electrical geometry is emitted for auditing.
"""
import csv
import io
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/wiring/aa-demo'
PLAN = json.loads((OUT / 'layout.json').read_text())
HARNESS = json.loads((OUT / 'harness.json').read_text())
W, H = 2480, 1900
BG = '#f6f5ee'
COL = {'5V':'#d4472f', 'GND':'#344754', 'VSYS':'#8853aa',
       'PWM0':'#167fac', 'PWM0_RAW':'#167fac', 'PWM1':'#b14c8a',
       'PWM1_RAW':'#b14c8a', 'BAT_POS':'#b6791b',
       'FUSED_BAT':'#b6791b', 'PACK_SW':'#b6791b'}
XS = dict(zip('abcdefghij', (1030,1050,1070,1090,1110,1170,1190,1210,1230,1250)))
def xy(h): return (XS[h[0]], 310 + (int(h[1:])-1)*18)

def render(gangs):
    from verify_aa_demo import validate_layout
    from verify_breadboard import profile
    validate_layout(PLAN, HARNESS, gangs)
    plan, harness = profile(PLAN, HARNESS, gangs)
    a=[]; routes=[]; terminals={}
    def add(s): a.append(s)
    def text(x,y,s,size=20,fill='#243e45',weight=400,anchor='start'):
        add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>')
    def rect(x,y,w,h,fill='#fff',stroke='#c1c9c7',r=8):
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
    def circle(x,y,r,fill,stroke='none'):
        add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>')
    def tag(x,y,s,c='#344754'):
        rect(x-5,y-19,len(s)*10+12,27,'#fff',c,4); text(x,y,s,17,c,600)
    def line(points,c,width=4):
        d='M'+' L'.join(f'{x},{y}' for x,y in points)
        add(f'<path d="{d}" stroke="{c}" stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    def terminal(name,x,y,label=None,dx=0,dy=-13):
        terminals[name]=(x,y)
        add(f'<circle data-terminal="{name}" cx="{x}" cy="{y}" r="6" fill="#ebd294" stroke="#665e41" stroke-width="2"/>')
        if label: text(x+dx,y+dy,label,15,'#243e45',600)
    def wire(ref,start,end,via,c,step=1):
        pts=[terminals[start], *via, terminals[end]]
        d='M'+' L'.join(f'{x},{y}' for x,y in pts)
        add(f'<g data-step="{step}" data-wire="{ref}"><title>{escape(ref+": "+start+" → "+end)}</title>')
        line(pts,BG,10)
        add(f'<path data-from="{start}" data-to="{end}" d="{d}" stroke="{c}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        for n in (start,end): circle(*terminals[n],4,c,'#fff')
        add('</g>')
        routes.append({'id':ref,'from':start,'to':end,'points':pts})
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">AA demo: {gangs}-servo illustrated breadboard</title><desc id="desc">A four-AA NiMH holder, inline fuse, RCY connector, physical master switch, regulator, three WAGO power junctions, capacitor, headered Pico and MG90S servos with exact breadboard holes. No servo gate or battery sensing. Illustrations are not to scale.</desc><style>text{{font-family:Arial,Helvetica,sans-serif}} .ghost{{opacity:.12}} [data-wire]{{cursor:pointer}}</style><defs><linearGradient id="cell" x1="0" x2="1"><stop stop-color="#b8c2c5"/><stop offset=".35" stop-color="#f8faf6"/><stop offset=".75" stop-color="#e4e9e3"/><stop offset="1" stop-color="#a3b0b4"/></linearGradient><linearGradient id="metal"><stop stop-color="#666d70"/><stop offset=".45" stop-color="#edf1ef"/><stop offset="1" stop-color="#747c7c"/></linearGradient><linearGradient id="can"><stop stop-color="#212a30"/><stop offset=".45" stop-color="#44575c"/><stop offset="1" stop-color="#172327"/></linearGradient></defs>')
    rect(0,0,W,H,BG,BG,0)
    text(60,65,'AUTO SWITCH',18,'#56746d',700)
    text(60,115,'The AA demo · every part, every connection',43,'#183a39',700)
    text(60,155,f'{gangs} servo'+('s' if gangs==2 else '')+' · 4 rechargeable AA NiMH cells · continuously powered servo · no GP15 gate / no GP26 battery sensor',22)
    text(60,188,'Assembly illustration, not to scale. Follow labels and hole addresses; check actual module silkscreen before soldering.',18)
    for x,t in [(70,'01  BATTERY & POWER'),(955,'02  BREADBOARD'),(1760,'03  ACTUATOR'+('S' if gangs==2 else ''))]:
        text(x,253,t,20,'#56746d',700)
    # Breadboard: exact five-hole strips and unused rail holes.
    rect(940,280,400,1220,'#dfdfd5','#bdc6bd',18)
    rect(1013,292,115,1160,'#fffef8',r=3);rect(1153,292,115,1160,'#fffef8',r=3)
    rect(1130,300,20,1145,'#b8c0b8',r=2)
    for xx in (967,985,1293,1311):
        for row in [3+6*g+k for g in range(10) for k in range(5)]: circle(xx,310+(row-1)*18,3,'#a9b0a7')
    for row in range(1,64):
        yy=310+(row-1)*18
        for columns in ('abcde','fghij'): line([xy(columns[0]+str(row)),xy(columns[-1]+str(row))],'#e9e9df',9)
        for column in XS:
            xx,yy=xy(column+str(row))
            add(f'<circle data-hole="{column}{row}" cx="{xx}" cy="{yy}" r="3.6" fill="#8f9b91"/>')
        text(998,yy+4,row,11,anchor='middle');text(1280,yy+4,row,11,anchor='middle')
    for col,xx in XS.items(): text(xx,301,col,13,anchor='middle');text(xx,1470,col,13,anchor='middle')
    text(962,1485,'Rails UNUSED',12);text(1245,1485,'Rails UNUSED',12)
    # Headered Pico W; pin pitch and orientation match physical layout.
    add('<g data-component="PICO" data-step="1">')
    rect(1059,333,162,349,'#216b4b','#134b34',4)
    rect(1109,315,61,38,'url(#metal)','#6a7372',3)
    rect(1117,315,45,13,'#263533',r=1)
    rect(1111,417,58,58,'#263330','#0a1815',2)
    for yy in range(423,475,8):
        rect(1106,yy,5,3,'#bec7b8',r=0);rect(1169,yy,5,3,'#bec7b8',r=0)
    text(1121,446,'RP2040',9,'#b6b9b5');text(1086,526,'PICO W',20,'#fff',700)
    rect(1085,372,23,16,'#bfc9c0',r=3);text(1085,404,'BOOTSEL',9,'#fff')
    rect(1097,548,76,64,'#b7c2b8','#f4ead1',2);text(1104,583,'RADIO',12,'#344e43')
    line([(1102,637),(1179,637),(1179,650),(1116,650),(1116,662),(1179,662)],'#d3c77a',3)
    for i in range(15): rect(1088+(i%3)*11,395+(i//3)*20,6,4,'#c7b998',r=0)
    used={'39':'VSYS','38':'GND','40':'VBUS ×','21':'GP16'}
    if gangs==2: used['22']='GP17'
    for num,hole in plan['pico_pins'].items():
        xx,yy=xy(hole);rect(xx-5,yy-5,10,10,'#d3bc6d','#88723a',0)
        text(xx+(10 if hole[0]=='c' else -10),yy+3,num,8,'#fff',anchor='start' if hole[0]=='c' else 'end')
        if num in used: text(xx-25,yy+4,used[num],10,'#fff',600,'end')
    text(1060,709,'c3–c22 / h3–h22',18)
    text(1058,734,'USB socket points UP',17)
    add('</g>')
    # Assign all breadboard electrical terminals (including accessible jumper holes).
    for name,hole in plan['terminal_bindings'].items(): terminals[name]=xy(hole)
    for j in plan['jumpers']:
        for end in ('a','b'): terminals['hole:'+j[end]]=xy(j[end])
    for lead in plan['leads']: terminals['hole:'+lead['hole']]=xy(lead['hole'])
    # Battery holder: four cylindrical cells, alternating polarities, springs.
    add('<g data-component="BAT" data-step="1">')
    rect(90,300,325,290,'#252c30','#111b1c',14)
    for i in range(4):
        xx=104+i*76;up=i%2==0
        rect(xx,323,66,241,'url(#cell)','#abb6b5',18)
        for k in range(4): line([(xx+22,317+k*2),(xx+42,319+k*2)],'#adb9bd',2)
        rect(xx+23,317 if up else 561,19,7,'#c7cfd0',r=2)
        text(xx+33,349,'+' if up else '−',20,'#334b52',600,'middle')
        text(xx+33,550,'−' if up else '+',20,'#334b52',600,'middle')
        add(f'<text x="{xx+33}" y="472" font-size="20" fill="#416b65" text-anchor="middle" transform="rotate(-90 {xx+33} 472)">AA NiMH · 1.2 V</text>')
    terminal('BAT.red',415,535,'+',-20,5);terminal('BAT.black',415,567,'−',-20,5)
    text(95,625,'BAT · Pololu 1153 holder + 4 AA cells',20,weight=600)
    text(95,651,'Follow the + / − moulded inside your holder.',17)
    add('</g>')
    # Fuse and keyed two-wire disconnect, drawn as real housings.
    add('<g data-component="F1" data-step="1">')
    rect(515,320,210,65,'#303b40','#0f1b1f',30)
    for xx in range(535,592,8): line([(xx,327),(xx,378)],'#536065',3)
    line([(650,323),(650,382)],'#839194',3)
    terminal('F1.in',515,352);terminal('F1.out',725,352)
    text(502,290,'F1 · inline fuse holder',20,weight=600)
    text(518,414,'2 A time-lag ceramic fuse inside',17)
    # Small cutaway reference below, not a second installed fuse.
    rect(550,430,100,22,'#eceee8','#9baaa6',3)
    rect(550,430,16,22,'url(#metal)',r=2);rect(634,430,16,22,'url(#metal)',r=2)
    text(666,447,'5 × 20 mm',15)
    add('</g><g data-component="RCY" data-step="1">')
    rect(520,495,90,75,'#b52e28','#84231f',4);rect(610,490,91,85,'#d94131','#84231f',4)
    rect(595,481,32,14,'#ee6550','#84231f',2)
    terminal('RCY.battery_positive',520,515,'+',14,5)
    terminal('RCY.battery_negative',520,551,'−',14,5)
    terminal('RCY.load_positive',701,515,'+',-25,5)
    terminal('RCY.load_negative',701,551,'−',-25,5)
    text(517,608,'RCY · unplug here before wiring',19,weight=600)
    add('</g>')
    # Pololu 2810 top view: VIN left upper pair, GND middle, ON lower;
    # VOUT right upper pair; slide at bottom. Other duplicate pads unused.
    add('<g data-component="MASTER" data-step="1">')
    rect(520,680,170,170,'#2a7958','#164a39',4)
    for xx in (532,678):
        for yy in (694,716,746,768,797,831): circle(xx,yy,5,'#d9d4a5','#b6c2ac')
    rect(552,698,39,32,'#263234',r=2);rect(611,698,39,32,'#263234',r=2)
    for yy in (741,761,782):
        rect(560,yy,16,6,'#d2c39e',r=0);rect(612,yy,20,7,'#313b3a',r=0)
    rect(567,815,76,31,'url(#metal)',r=3);rect(578,831,21,28,'#1c262b',r=2)
    terminal('MASTER.VIN',532,716,'VIN',10,-9)
    terminal('MASTER.GND',532,746,'GND',10,21)
    terminal('MASTER.VOUT',678,716,'VOUT',-50,-9)
    text(548,801,'ON ×',13,'#fff');text(539,881,'OFF ← slider → ON',17)
    text(230,815,'MASTER · Pololu 2810',20,weight=600)
    text(230,843,'Slider only; ON pad unused.',17)
    add('</g>')
    # Regulator: top view, input at left, output right; GND above VIN/VOUT.
    add('<g data-component="REG" data-step="1">')
    rect(340,1000,263,129,'#287454','#134536',4)
    for xx in (350,593):
        for yy in (1010,1119): circle(xx,yy,6,'#c9d6ce','#d7dbb7')
    rect(427,1018,81,80,'#252f32','#0d1b1f',18);text(450,1065,'100',21,'#586469')
    for xx in (398,548):
        circle(xx,1098,17,'#9daeb0','#405558');line([(xx-10,1098),(xx+10,1098)],'#4e6365',2)
    for xx in (389,516,543): rect(xx,1033,15,10,'#cec3a7',r=1)
    for yy in (1059,1074): rect(514,yy,21,8,'#222f30',r=0)
    terminal('REG.GND',352,1030,'GND',12,-7)
    terminal('REG.VIN',352,1060,'VIN',12,6)
    terminal('REG.VOUT',591,1060,'VOUT',-57,6)
    circle(591,1030,5,'#d9d4a5');text(543,1024,'GND ×',12,'#fff')
    circle(352,1090,5,'#d9d4a5');text(363,1094,'EN ×',12,'#fff')
    text(350,1171,'REG · S18V20F5 · fixed 5 V',20,weight=600)
    text(350,1198,'Solder to labelled pads; EN unused.',17)
    add('</g>')
    def wago(ref,x,y,label,color):
        add(f'<g data-component="{ref}" data-step="1">')
        rect(x,y,192,111,'#c3cfcc','#819b94',7)
        for i in range(5):
            xx=x+16+34*i
            rect(xx-10,y+8,27,64,'#ee841d','#b96013',4)
            for yy in range(int(y+20),int(y+56),8): line([(xx-6,yy),(xx+13,yy)],'#ffb053',2)
            rect(xx-10,y+76,26,27,'#6f837b','#a7b9b1',3)
            terminal(f'{ref}.{i+1}',xx+3,y+103)
            text(xx+3,y+91,i+1,13,'#fff',600,'middle')
        text(x,y-42,label,20,color,700);text(x,y-16,ref+' · WAGO 221-415',16)
        add('</g>')
    wago('P5V',689,970,'+5 V distribution',COL['5V'])
    wago('PGND_A',230,1340,'GROUND A',COL['GND'])
    wago('PGND_B',1600,1340,'GROUND B',COL['GND'])
    text(1840,1380,'WAGO PORT KEY',19,weight=700)
    text(1840,1410,'Number ports left to right as shown.',17)
    text(1840,1440,'All 5 ports inside ONE block are connected.',17)
    text(1840,1470,'GROUND B port 5 stays empty.',17)
    # Electrolytic capacitor: its negative stripe follows the negative lead.
    add('<g data-component="C1" data-step="1">')
    rect(618,1330,97,115,'url(#can)','#132328',9)
    add('<ellipse cx="666.5" cy="1330" rx="48.5" ry="15" fill="#b4c0bd" stroke="#546865"/>')
    line([(645,1323),(684,1336)],'#6d7e79',2);line([(647,1339),(684,1322)],'#6d7e79',2)
    rect(686,1344,18,90,'#a8b9b0',r=0)
    for yy in (1360,1385,1410):text(695,yy,'−',19,'#344e48',600,'middle')
    text(630,1379,'470',20,'#e2eee5',600);text(630,1406,'µF',20,'#e2eee5')
    line([(640,1445),(640,1465)],'#a8b1ab',3);line([(692,1445),(692,1465)],'#a8b1ab',3)
    terminal('C1.positive',640,1465,'+',0,25);terminal('C1.negative',692,1465,'−',0,25)
    text(611,1265,'C1 · 470 µF / 10 V',20,weight=600)
    text(611,1292,'Stripe / short lead → GND',17)
    add('</g>')
    # MG90S case, mounting ears, original horn and three-wire connector.
    for i in range(gangs):
        x,y=2020,395+i*535
        add(f'<g data-component="SERVO{i}" data-step="{3+i}">')
        rect(x-24,y+60,191,28,'#42484b','#222e30',3)
        for xx in (x-13,x+157):circle(xx,y+74,5,'#cdd4d0','#151e20')
        rect(x,y+21,145,165,'#3f484c','#1b292d',8)
        rect(x+5,y+22,135,43,'#566267','#27373b',6)
        circle(x+45,y+38,29,'#a1aeb1','#3a4b50');circle(x+45,y+38,16,'#bdab75','#5f604d')
        rect(x+32,y-13,26,111,'#e1e5dd','#aeb9b2',11)
        for yy in (y+2,y+76,y+87):circle(x+45,yy,3,'#677a75')
        circle(x+45,y+38,6,'url(#metal)','#4b5959')
        rect(x+14,y+88,117,60,'#a7b947','#74842b',3)
        text(x+27,y+112,'MG90S',21,'#26351d',700);text(x+26,y+135,'180° SERVO',12,'#334425')
        for yy in (y+72,y+161):line([(x+6,yy),(x+139,yy)],'#28383b',2)
        # Matching extension keeps the servo's own connector intact.
        cy=y+255
        for dx,c in ((0,COL['GND']),(30,COL['5V']),(60,COL[f'PWM{i}'])):
            line([(x+65+dx/3,y+186),(x+65+dx/3,y+210),(1850+dx,y+210),(1850+dx,cy-12)],c,6)
        rect(1835,cy-15,92,51,'#222e33','#101d23',4)
        line([(1838,cy+9),(1924,cy+9)],'#83989c',2)
        for dx,n in ((0,'ground'),(30,'power'),(60,'signal')):
            terminal(f'SERVO{i}.{n}',1850+dx,cy+30)
        text(1780,y-47,f'SERVO {i+1} · MG90S',25,weight=600)
        text(1780,y-17,'Original horn + matching 3-wire extension',17)
        text(1944,cy+14,'Extension / breakout',17)
        text(1847,cy+63,'G',15,COL['GND']);text(1874,cy+63,'+',15,COL['5V']);text(1904,cy+63,'S',15,COL[f'PWM{i}'])
        add('</g>')
    if gangs==1:
        rect(1790,960,540,216,'#ecf1e7','#ccd6c8',15)
        text(1818,1003,'Start with one unloaded servo',25,weight=600)
        for yy,s in [(1043,'This build uses one servo on Pico GP16.'),(1078,'P5V port 5 and GROUND B port 4 stay empty.'),(1113,'GP17 is unused. No extra resistor or wires.'),(1148,'Calibrate unloaded before pressing the switch.')]:text(1818,yy,s,18)
    # Resistors / diode occupy the exact hole endpoints; body centered on lead.
    for p in plan['placements']:
        add(f'<g data-component="{p["ref"]}" data-step="{p["step"]}">')
        ends=list(p['terminals'].items());(n1,h1),(n2,h2)=ends
        x,y=xy(h1);_,yy=xy(h2)
        line([(x,y),(x,yy)],'#9fa49b',3)
        if p['type']=='diode':
            rect(x-8,y+25,16,41,'#2d3439','#131d20',3)
            rect(x-8,y+58,16,6,'#d2d9d6',r=0)
            text(704,y-45,'D1 · 1N5819',17,weight=700)
            text(704,y-20,'stripe at a35',15,COL['VSYS'])
        else:
            rect(x-8,y+24,16,43,'#d8c79d','#a9976c',5)
            for offset,c in zip((29,37,45,53,62),('#764527','#191919','#191919','#764527','#764527')):rect(x-8,y+offset,16,3,c,r=0)
            text(x+16,y+45,p['ref'],14,weight=700);text(x+16,y+66,'1 kΩ',15)
        for name,h in ends:
            xx,yy=xy(h)
            add(f'<circle data-terminal="{p["ref"]}.{name}" cx="{xx}" cy="{yy}" r="4" fill="#6b695a"/>')
        add('</g>')
    # Electrical wires are emitted from the authoritative layout, never guessed.
    vias={
      ('BAT.red','F1.in'):[(463,535),(463,352)],
      ('F1.out','RCY.battery_positive'):[(766,352),(766,469),(490,469),(490,515)],
      ('RCY.battery_positive','RCY.load_positive'):[],
      ('RCY.load_positive','MASTER.VIN'):[(742,515),(742,649),(484,649),(484,716)],
      ('MASTER.VOUT','REG.VIN'):[(774,716),(774,895),(304,895),(304,1060)],
      ('REG.VOUT','P5V.1'):[(630,1060),(630,1148),(708,1148)],
      ('P5V.2','C1.positive'):[(742,1227),(567,1227),(567,1558),(640,1558)],
      ('P5V.4','SERVO0.power'):[(810,1110),(895,1110),(895,220),(1700,220),(1700,703),(1880,703)],
      ('P5V.5','SERVO1.power'):[(844,1090),(910,1090),(910,207),(1750,207),(1750,1263),(1880,1263)],
      ('BAT.black','RCY.battery_negative'):[(449,567),(449,589),(480,589),(480,551)],
      ('RCY.battery_negative','RCY.load_negative'):[],
      ('RCY.load_negative','PGND_A.1'):[(825,551),(825,900),(930,900),(930,1219),(177,1219),(177,1540),(249,1540)],
      ('PGND_A.2','MASTER.GND'):[(283,1579),(154,1579),(154,745),(485,745),(485,746)],
      ('PGND_A.3','REG.GND'):[(317,1539),(209,1539),(209,974),(317,974),(317,1030)],
      ('PGND_A.4','PGND_B.1'):[(351,1595),(1619,1595)],
      ('PGND_A.5','C1.negative'):[(385,1510),(692,1510)],
      ('PGND_B.3','SERVO0.ground'):[(1687,1557),(1772,1557),(1772,724),(1850,724)],
      ('PGND_B.4','SERVO1.ground'):[(1721,1576),(1794,1576),(1794,1292),(1850,1292)],
    }
    term_net={t:n for n,ts in harness['nets'].items() for t in ts}
    for i,(s,e) in enumerate(plan['external_wires']):
        wire('E'+str(i+1),s,e,vias[(s,e)],COL.get(term_net[s],'#b6791b'),1 if not s.startswith('P5V.4') else 3)
    jvias={'J1':[(1050,939),(1370,939),(1370,364)],'J2':[(1400,1192),(1400,382)],
           'J3':[(1309,688),(1309,832)],'J4':[(1333,670),(1333,1012)]}
    for j in plan['jumpers']:
        wire(j['id'],'hole:'+j['a'],'hole:'+j['b'],jvias[j['id']],COL[j['net']],j['step'])
    lvias={'L1':[(919,832),(919,1168),(776,1168)],
           'L2':[(920,1192),(920,1571),(1653,1571)],
           'L3':[(1480,922),(1480,750),(1910,750)],
           'L4':[(1510,1102),(1510,1240),(1910,1240)]}
    for l in plan['leads']:
        wire(l['id'],'hole:'+l['hole'],l['node'],lvias[l['id']],COL[l['net']],l['step'])
    # A visible termination at every jumper lead. Crossings have white clearance,
    # not dots; electrical joins occur inside terminal strips or WAGO blocks.
    for j in plan['jumpers']:
        pos={'J1':(1378,790),'J2':(1408,1080),'J3':(1280,776),'J4':(1343,991)}[j['id']]
        tag(*pos,j['id'],COL[j['net']])
    for l in plan['leads']:
        pos={'L1':(813,1162),'L2':(1000,1565),'L3':(1490,882),'L4':(1520,1190)}[l['id']]
        tag(*pos,l['id'],COL[l['net']])
    # Bottom legend, build addresses, and charger reference.
    rect(60,1640,430,210,'#e9eee5','#ced8cb',12)
    text(83,1674,'CHARGING IS SEPARATE',19,weight=700)
    rect(87,1694,145,126,'#f8faf4','#b7c3b9',14)
    for i in range(4):rect(98+i*30,1708,23,90,'url(#cell)','#a0afa7',8)
    text(254,1717,'Remove cells.',19)
    text(254,1745,'Use a NiMH charger.',18)
    text(254,1774,'Never charge the',18)
    text(254,1800,'AA pack via Pico USB.',18)
    text(92,1840,'External charger · no connection to this circuit',15)
    rect(520,1640,911,210,'#fffef8','#cbd5ce',12)
    text(546,1676,'BREADBOARD BUILD KEY',19,weight=700)
    rows=[('D1','a30 → a35; stripe at a35'),('J1 / J2','b35 → j4   /   b50 → j5'),('R_PWM0 / J3','f30 → f35   /   j22 → j30'),('L1 / L2 / L3','b30 → P5V.3   /   a50 → PGND_B.2   /   j35 → servo 1 S')]
    if gangs==2: rows.append(('Second servo','R f40 → f45; J4 j21 → j40; L4 j45 → servo 2 S'))
    for i,(l,r) in enumerate(rows):text(546,1708+i*28,l,16,weight=700);text(740,1708+i*28,r,16)
    rect(1460,1640,960,210,'#e9eee5','#ced8cb',12)
    text(1487,1676,'BEFORE POWER',19,weight=700)
    for i,t in enumerate(['Remove Pico and unplug servos for first voltage checks.',
       'Black probe c50; red c30 ≈ 5 V; red c35 below 5.5 V.',
       'Disconnect battery before reinserting the Pico. USB initially unplugged.',
       'Only use the aa-demo firmware profile. No automatic low-battery cutoff.',
       'Thick power wiring stays OFF the breadboard; crossing lines do not join.']):text(1487,1708+i*28,t,17)
    text(60,1880,'AUTO-SWITCH / AA DEMO  •  Manufacturer-based illustrations; cosmetic details simplified. Connectivity checked, physical build not yet tested.',16)
    add('</svg>')
    path=OUT/f'breadboard-{gangs}-servo.svg'
    path.write_text('\n'.join(a)+'\n')
    (OUT/f'render-map-{gangs}.json').write_text(json.dumps({'width':W,'height':H,'terminals':terminals,'routes':routes},indent=2)+'\n')
    buf=io.StringIO();writer=csv.writer(buf);writer.writerow(['item','from','to','note'])
    for p in plan['placements']:
        hs=list(p['terminals'].values());writer.writerow([p['ref'],*hs,p.get('note',p['value'])])
    for j in plan['jumpers']:writer.writerow([j['id'],j['a'],j['b'],j['net']])
    for l in plan['leads']:writer.writerow([l['id'],l['hole'],l['node'],l['note']])
    for i,(s,e) in enumerate(plan['external_wires']):writer.writerow(['E'+str(i+1),s,e,'external harness'])
    (OUT/f'placements-{gangs}-servo.csv').write_text(buf.getvalue())
    print(path.relative_to(ROOT))

if __name__=='__main__':
    for gangs in (1,2): render(gangs)
