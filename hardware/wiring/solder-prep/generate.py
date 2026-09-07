#!/usr/bin/env python3
"""Deterministic vector illustration: received XL63070 + headerless S2 Mini solder prep.
No photos, credentials or machine-specific state are embedded.
"""
from html import escape
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
W,H=1900,1520
BG='#f7f5ef';INK='#203d42';RED='#d64b39';GND='#344b59';PWM='#1686a6';BAT='#bd7b21';GOLD='#dec382'
a=[];nets={};wires=[]
def add(s):a.append(s)
def text(x,y,s,size=20,color=INK,weight=400,anchor='start'):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>')
def rect(x,y,w,h,fill,stroke='none',r=5):add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
def circle(x,y,r,fill,stroke='none',sw=1):add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def line(points,color,width=4):add(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
def terminal(n,x,y,net):nets[n]={'xy':[x,y],'net':net}
def wire(src,dst,via=()):
    assert nets[src]['net']==nets[dst]['net'],(src,dst)
    net=nets[src]['net'];color={'BAT+':BAT,'5V':RED,'GND':GND,'PWM':PWM}[net];points=[nets[src]['xy'],*via,nets[dst]['xy']]
    line(points,BG,12);line(points,color,5)
    for x,y in [points[0],points[-1]]:circle(x,y,5,color,'white',1.5)
    wires.append({'from':src,'to':dst,'net':net,'points':points})
def badge(x,y,n):circle(x,y,17,'white',INK,2);text(x,y+6,n,18,INK,700,'middle')
def pad_group(x,y,label,num,net,name):
    rect(x-34,y-19,68,38,'#b9c4c7','#f5ead0',2)
    for xx in [x-12,x+12]:circle(xx,y,8,'#e1ce97');circle(xx,y,3.8,'#263744')
    terminal(name,x-12,y,net)
    text(x,y+(49 if y<1000 else -33),label,17,'white',700,'middle')
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">Auto Switch: seven solder groups, one complete wiring map</title><desc id="desc">Headerless S2 Mini component side up, USB down. Outer right bottom pads are VBUS, GND and GPIO16. Received converter portrait orientation has VOUT top left, GND top right, VIN bottom left and GND bottom right. Four AA cells feed converter input. Meter-verified five volt output supplies controller VBUS and one servo. Grounds are shared; GPIO16 carries PWM signal. Breadboard rail midpoint bridges are shown.</desc><style>text{{font-family:Arial,Helvetica,sans-serif}}</style>')
rect(0,0,W,H,BG)
text(60,55,'AUTO SWITCH / SOLDER PREP',18,'#5e7b73',700)
text(60,110,'Seven pad groups. One complete connection map.',39,weight=700)
text(60,153,'Headerless ESP32-S2 Mini + received XL63070 + switched 4-AA holder + one MG90S',22)
text(60,185,'Illustrations enlarged for clarity, not dimensional drawings. Match the labels on your actual boards.',18)
# S2 Mini, component-side-up USB-down; official outer row numbering.
bx,by=455,260
text(bx,235,'ESP32-S2 MINI · NO HEADERS',21,weight=700)
rect(bx,by,280,400,'#923b79','#6e285a',22)
for xx in [bx+28,bx+252]:circle(xx,by+24,10,BG,GOLD,3)
line([(bx+60,by+50),(bx+60,by+18),(bx+95,by+18),(bx+95,by+46),(bx+130,by+46),(bx+130,by+18),(bx+177,by+18),(bx+177,by+48)],'#ca73b2',6)
rect(bx+101,by+141,79,85,'#252a31','#aab0b4',2)
for i in range(10):
    rect(bx+94,by+146+i*7,7,3,'#d5c7d0',r=0);rect(bx+180,by+146+i*7,7,3,'#d5c7d0',r=0)
text(bx+140,by+177,'ESP32',13,'#eee',600,'middle');text(bx+140,by+198,'S2',14,'#eee',600,'middle')
for i in range(14):rect(bx+67+(i%2)*17,by+85+(i//2)*23,11,7,'#ccbaa1',r=1)
rect(bx+160,by+89,36,22,'#bdc6c9','#eef1ee',3)
text(bx+144,by+275,'S2 mini',21,'white',700,'middle')
rows=[['EN','1','40','39'],['3','2','38','37'],['5','4','36','35'],['7','6','34','33'],['9','8','21','18'],['11','10','17','16'],['12','13','GND','GND'],['3V3','14','15','VBUS']]
xs=[bx+17,bx+45,bx+235,bx+263]
for ri,labels in enumerate(rows):
    yy=by+65+ri*34
    for ci,lab in enumerate(labels):
        circle(xs[ci],yy,8,GOLD);circle(xs[ci],yy,3.5,'#233541')
        text(xs[ci]+(10 if ci<2 else -10),yy+3,lab,8,'white',600,'start' if ci<2 else 'end')
for n,ri,net,label,num in [('S2.GPIO16',5,'PWM','GPIO16 · signal',3),('S2.GND',6,'GND','GND',2),('S2.VBUS',7,'5V','VBUS / 5V',1)]:
    yy=by+65+ri*34;terminal(n,xs[3],yy,net)
    text(785,yy-10,label.replace(' · signal',''),15,{'PWM':PWM,'GND':GND,'5V':RED}[net],700)
rect(bx+92,by+325,97,82,'#aab7bd','#5b6a70',5);rect(bx+100,by+389,81,14,'#23333a',4)
text(bx+140,by+445,'USB DOWN · UNPLUGGED',18,weight=700,anchor='middle')
text(bx-35,by+477,'Use only the OUTERMOST right row.',17)

# Actual received converter portrait orientation.
cx,cy=460,800
text(cx-40,765,'RECEIVED XL63070 · COMPONENT SIDE UP',20,weight=700)
rect(cx,cy,220,405,'#0c3b6a','#092d50',3)
pad_group(499,829,'VOUT',6,'5V','REG.VOUT');pad_group(641,829,'GND',7,'GND','REG.GND_OUT')
pad_group(499,1175,'VIN',4,'BAT+','REG.VIN');pad_group(641,1175,'GND',5,'GND','REG.GND_IN')
rect(cx+18,cy+156,78,92,'#657279','#364750',6);text(cx+57,cy+210,'1R5',31,'#29383e',700,'middle')
rect(cx+112,cy+205,40,45,'#171f2a',r=1)
for yy in [87,112,137,261]:rect(cx+105,cy+yy,41,13,'#c4b49b','#7e8b90',1)
for yy in [94,127,160,193,226,259,292]:rect(cx+183,cy+yy,15,12,'#c4b49b','#728594',1)
rect(cx+85,cy+301,55,31,'#bb8d53','#e8c68f',2)
for yy,lab in [(90,'3V3'),(123,'5V'),(156,'9V'),(237,'ADJ'),(270,'PS'),(303,'EN')]:
    rect(cx+158,cy+yy,14,9,'#b2bdc3',r=1);text(cx+167,cy+yy-4,lab,9,'white',600,'middle')
text(cx+110,cy+367,'XL63070',16,'white',700,'middle')

# Battery holder, closed case: actual switch and leads, cells described rather than guessed polarity.
text(65,820,'SWITCHED 4-AA HOLDER',21,weight=700)
rect(70,865,260,320,'#263138','#0d1b22',15);rect(85,882,230,286,'#354249','#647077',9)
for i in range(4):rect(105+i*47,915,35,173,'#536169','#7c878a',12);text(122+i*47,1008,'AA',14,'#e0e5e4',700,'middle')
text(200,1118,'4 × 1.5 V alkaline',19,'#edf0ec',700,'middle')
rect(239,889,58,24,'#9babae',r=3);rect(243,886,22,30,'#172229',r=2)
text(70,849,'≈ 6 V nominal · converter input only',16,BAT,700)
terminal('BAT.red',330,1120,'BAT+');terminal('BAT.black',330,1155,'GND')
# Generic breadboard rail strip, with explicit breaks and PWM joined row.
text(890,235,'BREADBOARD JOINS',21,weight=700)
rect(890,270,275,940,'#e2e2d9','#c2cbc2',14)
for x,col in [(920,RED),(960,GND)]:
    line([(x,310),(x,691)],col,3);line([(x,745),(x,1173)],col,3)
    for start,end in [(330,685),(750,1160)]:
        for yy in range(start,end,19):circle(x,yy,4,'#87958c')
    text(x,295,'+' if col==RED else '−',25,col,700,'middle')
text(991,695,'Rail break',14,weight=700);text(991,716,'bridge both',14,weight=700)
# Main row for signal is separate from both supply rails.
line([(1010,779),(1122,779)],'#a8b8ac',11)
for xx in [1010,1038,1066,1094,1122]:circle(xx,779,5,'#5a7567')
text(1007,805,'Same 5-hole strip',14,PWM,700)
for name,x,y,net in [('P.S2',920,563,'5V'),('G.S2',960,529,'GND'),('P.SERVO',920,930,'5V'),('G.SERVO',960,895,'GND'),('P.IN',920,1100,'5V'),('G.IN',960,1135,'GND'),('P.A',920,691,'5V'),('P.B',920,745,'5V'),('G.A',960,691,'GND'),('G.B',960,745,'GND'),('SIG.A',1010,779,'PWM'),('SIG.B',1122,779,'PWM')]:terminal(name,x,y,net)
# Servo, female plug shown with exposed pins only at jumper interface.
text(1295,755,'ONE MG90S SERVO',22,weight=700)
sx,sy=1390,830
rect(sx-18,sy+32,278,27,'#25353d','#101e25',3)
for xx in [sx-7,sx+249]:circle(xx,sy+45,6,BG)
rect(sx,sy+40,245,155,'#2d414b','#122732',8);rect(sx,sy,245,68,'#60757e','#304b57',10)
circle(sx+94,sy+5,48,'#75878d','#3c5661',2)
rect(sx+13,sy-6,163,21,'#e3e7e3','#7e9298',8);circle(sx+94,sy+4,7,'#a7b0ad','#6d7c7b',2)
for xx in [sx+31,sx+49,sx+137,sx+156]:circle(xx,sy+4,3,'#6b7c83')
rect(sx+30,sy+105,180,46,'#b7c9cb',r=3);text(sx+120,sy+136,'MG90S',24,'#29434c',700,'middle')
rect(1240,876,50,105,'#1b2c36','#101a20',4)
for n,yy,net,col in [('SERVO.GND',895,'GND',GND),('SERVO.V+',930,'5V',RED),('SERVO.S',965,'PWM',PWM)]:
    rect(1246,yy-7,18,14,'#a9b1ad',r=1);terminal(n,1254,yy,net)
    line([(1290,yy),(1335,yy),(1360,1010+(yy-895)*.25),(1390,1010+(yy-895)*.25)],col,5)
text(1300,1110,'Red = +5 V · brown/black = ground',18)
text(1300,1140,'Orange/yellow = PWM signal',18,PWM)
text(1300,1170,'Check actual servo plug colors before connecting.',16)
# One network, all wires. Halos indicate crossings without electrical junctions.
wire('S2.VBUS','P.S2');wire('S2.GND','G.S2')
wire('S2.GPIO16','SIG.A',[(875,495),(875,779)])
wire('SIG.B','SERVO.S',[(1206,779),(1206,965)])
wire('P.SERVO','SERVO.V+');wire('G.SERVO','SERVO.GND')
wire('REG.VOUT','P.IN',[(487,795),(847,795),(847,1100)])
wire('REG.GND_OUT','G.IN',[(830,829),(830,1135)])
wire('BAT.red','REG.VIN',[(375,1120),(375,1217),(487,1217)])
wire('BAT.black','REG.GND_IN',[(352,1155),(352,1281),(629,1281)])
wire('P.A','P.B',[(904,691),(904,745)]);wire('G.A','G.B',[(980,691),(980,745)])
# Numbered callouts are on the actual selected side and drawn above wires.
for num,yy in [(3,495),(2,529),(1,563)]:badge(751,yy,num)
for num,xx,yy in [(6,441,829),(4,441,1175),(5,699,1175)]:badge(xx,yy,num)
line([(688,844),(677,829)],INK,1.5);badge(704,856,7)
# Explicit junction markers where rail branches attach.
for n in ['P.S2','G.S2','P.SERVO','G.SERVO','P.IN','G.IN']:circle(*nets[n]['xy'],6,RED if nets[n]['net']=='5V' else GND,'white',1)
text(996,1040,'+ rail: converter → S2 + servo',14,RED,700)
text(996,1066,'− rail: common ground',14,GND,700)
# Seven-pad checklist, part of this same map rather than another circuit fragment.
rect(1225,240,615,460,'#edf1e9','#cbd6c8',12)
text(1250,278,'SOLDER PREP: 7 PAD GROUPS',23,weight=700)
for i,(s,col) in enumerate([('1  S2 VBUS / 5V',RED),('2  S2 GND',GND),('3  S2 GPIO16 · 3.3 V PWM',PWM),('4  Converter VIN · battery red',BAT),('5  Converter input GND · battery black',GND),('6  Converter VOUT · target 5.0 V',RED),('7  Converter output GND',GND)]):text(1250,318+i*36,s,20,col,700)
text(1250,590,'Each converter group has two joined holes.',18)
text(1250,618,'Choose one hole per group; do not join neighboring groups.',17)
text(1250,653,'Leave EN / PS / ADJ and voltage-selection pads',18,weight=700)
text(1250,680,'untouched during solder prep.',18,weight=700)
# Prominent meter/USB instructions, all retained in downloadable image.
rect(60,1320,1780,155,'#e9eee6','#c7d3c4',12)
text(83,1354,'BEFORE CONNECTING THE S2 OR SERVO',19,weight=700)
text(83,1386,'Remove cells while soldering. Then power only holder + converter and measure VOUT to GND: target about 5.0 V.',19)
text(83,1417,'Output selection is NOT verified by this drawing. Switch off and disconnect cells again before completing the wiring.',18)
text(83,1448,'For USB programming: unplug all three S2 leads from the circuit first. Battery OFF alone does not isolate USB power.',18,weight=700)
text(60,1503,'Junctions are dots. Wire crossings with a white gap are not connected. Breadboard rails may differ: check continuity with all power removed.',16)
add('</svg>')
(OUT/'solder-prep.svg').write_text('\n'.join(a)+'\n')
manifest={'status':'Bench wiring plan; physical assembly and converter output untested','orientation':{'S2':'component side up, USB down; outermost right row bottom-up VBUS,GND,GPIO16','converter':'received photo portrait, inductor left: VOUTtop-left,GNDtop-right,VINbottom-left,GND bottom-right'},'solder_groups':7,'solder_group_terminals':{'1':'S2.VBUS','2':'S2.GND','3':'S2.GPIO16','4':'REG.VIN','5':'REG.GND_IN','6':'REG.VOUT','7':'REG.GND_OUT'},'internal_connections':[['REG.GND_IN','REG.GND_OUT'],['SIG.A','SIG.B'],['P.S2','P.A'],['P.B','P.SERVO'],['P.SERVO','P.IN'],['G.S2','G.A'],['G.B','G.SERVO'],['G.SERVO','G.IN']],'converter_groups':4,'duplicate_holes_per_converter_group':2,'terminals':nets,'wires':wires,'sources':['https://www.wemos.cc/en/latest/_static/boards/s2_mini_v1.0.0_4_16x9.jpg','https://www.wemos.cc/en/latest/_static/files/sch_s2_mini_v1.0.0.pdf'],'photo_reference':'User-supplied IMG_3222.JPG, not embedded'}
(OUT/'connections.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(OUT/'solder-prep.svg')
