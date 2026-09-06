#!/usr/bin/env python3
"""Reproducible S2 Mini / four-AA breadboard illustration and wiring manifest.

Terminal placement follows WEMOS pinout and the selected converter's product
photo. Cosmetic geometry is illustrative, not a CAD dimension source.
"""
import csv
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/wiring/s2-aa-poc'
WEB = ROOT / 'learn/assets/s2-aa-poc'
W, H = 2100, 1460
C = {'BAT+':'#b47716', '5V':'#d44432', 'GND':'#344957', 'PWM':'#1485aa'}
BG = '#f6f5ef'

def render():
    a=[]; terminals={}; routes=[]
    def add(s): a.append(s)
    def txt(x,y,s,size=19,fill='#213e43',weight=400,anchor='start'):
        add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>')
    def rect(x,y,w,h,fill,stroke='none',r=5):
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
    def circle(x,y,r,fill,stroke='none'):
        add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>')
    def line(pts,color,width=4):
        d='M'+' L'.join(f'{x},{y}' for x,y in pts)
        add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    def terminal(name,x,y,net):
        terminals[name]={'xy':[x,y], 'net':net}
        circle(x,y,6,'#dfc780','#6b633e')
    def wire(name,src,dst,via,note):
        assert terminals[src]['net']==terminals[dst]['net'], (src,dst)
        net=terminals[src]['net']; pts=[terminals[src]['xy'],*via,terminals[dst]['xy']]
        add(f'<g data-wire="{name}" tabindex="0" role="button" aria-label="{escape(name+": "+note)}"><title>{escape(name+": "+note)}</title>')
        line(pts,BG,12);line(pts,C[net],5)
        for p in [pts[0],pts[-1]]:circle(*p,5,C[net],'white')
        add('</g>'); routes.append({'id':name,'from':src,'to':dst,'net':net,'note':note,'points':pts})
    def flag(x,y,s,color):
        rect(x-5,y-19,len(s)*10+12,27,'#fff',color,4);txt(x,y,s,16,color,700)
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc"><title id="title">ESP32-S2 Mini · one-servo AA prototype</title><desc id="desc">One continuous illustrated assembly map: switched four-AA alkaline holder, 5 V buck-boost module, breadboard power rails, S2 Mini beside breadboard, and MG90S servo. Raw battery connects only to converter input. USB remains unplugged. All connections have numbered wire labels.</desc><style>text{{font-family:Arial,Helvetica,sans-serif}} [data-wire]{{cursor:pointer}} [data-wire]:focus{{outline:none}} .selected path:last-of-type{{stroke-width:10}} </style><defs><linearGradient id="cell"><stop stop-color="#111c22"/><stop offset=".45" stop-color="#37474f"/><stop offset="1" stop-color="#121c22"/></linearGradient><linearGradient id="metal"><stop stop-color="#6c777b"/><stop offset=".5" stop-color="#e0e8e7"/><stop offset="1" stop-color="#7b878a"/></linearGradient></defs>')
    rect(0,0,W,H,BG)
    txt(55,52,'AUTO SWITCH / S2 AA POC',17,'#54776e',700)
    txt(55,103,'One battery pack. One servo. Every wire.',40,weight=700)
    txt(55,141,'ESP32-S2 Mini · DAIERTEK switched 4-AA holder · Teyleten 5 V buck-boost · breadboard rails',21)
    txt(55,174,'Top views, enlarged for clarity. Follow terminal labels; drawing is not to scale. Confirm your board matches the reference.',17)
    for x,s in [(60,'01  BATTERY & CONVERTER'),(715,'02  BREADBOARD'),(1275,'03  CONTROLLER & SERVO')]:txt(x,226,s,18,'#54776e',700)
    # Switched battery holder. Cells shown as a cutaway; actual molded polarity wins.
    rect(70,275,410,360,'#202a2e','#0e181b',15)
    rect(82,292,386,307,'#111b20','#4c595d',9)
    for i in range(4):
        xx=96+i*91; up=i%2==0
        rect(xx,312,75,267,'url(#cell)','#697678',18)
        rect(xx+2,up and 315 or 514,71,62,'url(#metal)',r=13)
        rect(xx+27,306 if up else 578,21,8,'#bdc8c9',r=2)
        txt(xx+37,343,'+' if up else '−',23,'white',700,'middle')
        txt(xx+37,560,'−' if up else '+',23,'white',700,'middle')
        add(f'<text x="{xx+40}" y="445" transform="rotate(-90 {xx+40} 445)" font-size="16" text-anchor="middle" fill="#e8ece7">AA ALKALINE · 1.5 V</text>')
    rect(359,606,91,20,'#adb6b5',r=3);rect(366,603,29,26,'#0e181b',r=3)
    txt(91,623,'DAIERTEK',16,'#d8e0dc',700)
    terminal('BAT.red',480,568,'BAT+'); terminal('BAT.black',480,605,'GND')
    txt(70,673,'Built-in switch → both electronics and servo',19,weight=700)
    txt(70,704,'4 alkaline AAs ≈ 6 V nominal. Cover shown removed.',17)
    txt(70,734,'Follow the + / − moulded inside the actual holder.',17)
    # Converter: exact observed top-view terminal order, duplicate holes.
    rect(160,845,380,190,'#17487b','#0e355c',3)
    for xx in (177,523):
        for yy in (869,893,984,1008):circle(xx,yy,8,'#c7cecf','#eee')
    for x,y,w,h in [(188,849,37,55),(188,978,37,53),(472,849,35,56),(473,978,34,53)]:rect(x,y,w,h,'#e9edeb',r=0)
    txt(192,875,'VIN',12,weight=700);txt(192,1000,'GND',10,weight=700)
    txt(474,875,'OUT',10,weight=700);txt(476,1000,'GND',10,weight=700)
    rect(290,830,104,86,'#828888','#434e50',7);txt(310,882,'1R5',29,'#4a5252',700)
    rect(237,924,44,47,'#ca873f','#ecc175',2);txt(241,946,'106',12,'#684123')
    rect(321,930,42,34,'#1f2529',r=1)
    for xx in (388,414,440,466):rect(xx,931,14,28,'#cdbba0','#78868b',1)
    for xx in (249,279,309):rect(xx,1004,14,10,'url(#metal)',r=0)
    txt(234,996,'EN  PS  ADJ',11,'white')
    for xx,label in [(398,'9V'),(441,'5V'),(483,'3V3')]:
        txt(xx,981,label,11,'white',600,'middle');rect(xx-7,992,14,11,'url(#metal)',r=0)
    rect(435,989,12,18,'#e2e7e4',r=2)
    txt(228,1025,'XL63070 / TPS63070 listing',12,'white')
    terminal('REG.VIN',177,869,'BAT+');terminal('REG.GND_IN',177,1008,'GND')
    terminal('REG.VOUT',523,869,'5V');terminal('REG.GND_OUT',523,1008,'GND')
    txt(110,1076,'5 V version · verify output with your meter',20,weight=700)
    txt(110,1107,'EN / PS / ADJ unused. No adjustment screw.',17)
    txt(110,1136,'Power pads are soldered; do not bridge selectors.',17)
    # Generic 830-point board: 63 five-hole rows, four 50-hole rails.
    rect(715,259,440,872,'#dddcd4','#bec5bc',16)
    rect(815,276,118,817,'#fffef8',r=2);rect(963,276,118,817,'#fffef8',r=2)
    rect(939,278,18,815,'#aeb8af',r=2)
    xs=dict(zip('abcdefghij',[831,852,873,894,915,978,999,1020,1041,1062]))
    yrow=lambda r:295+(r-1)*12
    railrows=[3+6*g+k for g in range(10) for k in range(5)]
    for r in range(1,64):
        yy=yrow(r)
        for cols in ('abcde','fghij'):line([(xs[cols[0]],yy),(xs[cols[-1]],yy)],'#e5e7dd',8)
        for c,x in xs.items():circle(x,yy,3.6,'#849287')
        if r==1 or r%5==0:txt(800,yy+4,r,11,anchor='middle');txt(1089,yy+4,r,11,anchor='middle')
    for c,x in xs.items():txt(x,286,c,12,anchor='middle')
    for x,col in [(746,'#d44432'),(772,'#344957'),(1104,'#d44432'),(1130,'#344957')]:
        line([(x-8,300),(x-8,657)],col,2);line([(x-8,683),(x-8,1042)],col,2)
        for n,r in enumerate(railrows,1):
            circle(x,yrow(r),3.7,'#879489')
            if x in (746,772):terminals[('P' if x==746 else 'G')+str(n)]={'xy':[x,yrow(r)],'net':'5V' if x==746 else 'GND'}
        txt(x,278,'+' if col=='#d44432' else '−',18,col,700,'middle')
    txt(724,1114,'LEFT rails used',16,weight=700);txt(980,1114,'RIGHT rails unused',15)
    # Visible rail addressing is ordinal; separate from main terminal row labels.
    for n in [1,8,10,25,26,35,38,48,50]:
        txt(706,yrow(railrows[n-1])+4,f'{n:02}',10,'#54776e',anchor='end')
    txt(820,1140,'Rows a–e join; rows f–j join.',16)
    terminal('j38',xs['j'],yrow(38),'PWM');terminal('i38',xs['i'],yrow(38),'PWM')
    # S2 Mini: USB DOWN, outer and inner headers reconstructed from WEMOS pinout.
    bx,by=1380,285
    rect(bx,by,270,365,'#973976','#642152',24)
    for xx in (bx+28,bx+242):circle(xx,by+26,11,BG,'#d9a0c1')
    line([(bx+62,by+53),(bx+62,by+16),(bx+100,by+16),(bx+100,by+47),(bx+139,by+47),(bx+139,by+16),(bx+181,by+16),(bx+181,by+47)],'#b55399',7)
    rect(bx+97,by+143,77,85,'#34313b','#b1a3af',2)
    for i in range(12):
        yy=by+148+i*6;rect(bx+90,yy,7,3,'#d6c3cf',r=0);rect(bx+174,yy,7,3,'#d6c3cf',r=0)
    txt(bx+111,by+183,'ESP32',12,'#ddd');txt(bx+112,by+201,'S2',12,'#ddd')
    rect(bx+144,by+93,37,22,'url(#metal)',r=4)
    for i in range(22):rect(bx+64+(i%3)*20,by+92+(i//3)*19,11,5,'#c7b7a6',r=1)
    rect(bx+94,by+297,91,76,'url(#metal)','#505660',5);rect(bx+103,by+356,72,14,'#222b35',r=4)
    for xx in (bx+22,bx+222):rect(xx,by+322,29,24,'#d1d1ce',r=3)
    txt(bx+111,by+271,'S2 mini',19,'white',700)
    rows=[['EN','1','40','39'],['3','2','38','37'],['5','4','36','35'],['7','6','34','33'],['9','8','21','18'],['11','10','17','16'],['12','13','GND','GND'],['3V3','14','15','VBUS']]
    pinxs=[bx+15,bx+43,bx+227,bx+255]
    for ri,pins in enumerate(rows):
        yy=by+80+ri*29
        for ci,label in enumerate(pins):
            circle(pinxs[ci],yy,7,'#ddc58a','#e4d7ad');circle(pinxs[ci],yy,3,'#33404b')
            txt(pinxs[ci]+(10 if ci<2 else -10),yy+3,label,8,'white',600,'start' if ci<2 else 'end')
    terminal('S2.GPIO16',pinxs[3],by+80+5*29,'PWM')
    terminal('S2.GND',pinxs[3],by+80+6*29,'GND')
    terminal('S2.VBUS',pinxs[3],by+80+7*29,'5V')
    for name,yy,color in [('GPIO16',510,C['PWM']),('GND',539,C['GND']),('5V / VBUS',568,C['5V'])]:txt(1667,yy-11,name,16,color,700)
    txt(1320,694,'USB points DOWN · stays unplugged',20,weight=700)
    txt(1320,723,'Board beside breadboard; female jumpers on headers.',17)
    txt(1320,752,'Both header rows must not share breadboard strips.',17)
    # Servo and recognizable three-position socket.
    sx,sy=1450,883
    rect(sx-22,sy+21,286,27,'#27353c','#0f1e25',4)
    for xx in (sx-10,sx+251):circle(xx,sy+34,6,BG)
    rect(sx,sy+37,241,150,'#2f414b','#10232c',8)
    rect(sx,sy,241,68,'#536875','#263f4b',10)
    circle(sx+99,sy+12,48,'#667b88','#283f4a');circle(sx+99,sy+12,19,'#c7c5ba','#c0b087')
    rect(sx+21,sy-1,155,20,'#ebeee7','#798981',8);circle(sx+99,sy+9,6,'#59696c')
    for xx in (sx+39,sx+57,sx+140,sx+158):circle(xx,sy+9,3,'#909b95')
    rect(sx+23,sy+98,195,49,'#c8d8d9',r=3);txt(sx+39,sy+130,'MG90S  SERVO',20,'#294750',700)
    # Cable socket at left. Pin function explicitly labeled; cable color must be verified.
    rect(1260,929,44,96,'#212e36','#131e24',4)
    for ci,(yy,col) in enumerate([(944,C['GND']),(977,C['5V']),(1010,C['PWM'])]):
        rect(1267,yy-6,16,12,'#9fa494',r=1);line([(1304,yy),(1380,yy),(1415,sy+165+ci*9),(sx,sy+165+ci*9)],col,4)
    terminal('SERVO.GND',1267,944,'GND');terminal('SERVO.V+',1267,977,'5V');terminal('SERVO.S',1267,1010,'PWM')
    txt(1730,930,'Brown / black = GND',17,C['GND'],600)
    txt(1730,962,'Red = +5 V',17,C['5V'],600)
    txt(1730,994,'Orange / yellow = signal',17,C['PWM'],600)
    txt(1320,1110,'Male jumper pins enter the servo’s female plug.',17)
    txt(1320,1140,'Check polarity. Start with the horn unloaded.',17)
    # Routes. Junctions only at terminals/internal strips, white halos show crossings.
    wire('W1','BAT.red','REG.VIN',[(577,568),(577,787),(118,787),(118,869)],'Holder red → converter VIN; solder connection')
    wire('W2','BAT.black','REG.GND_IN',[(600,605),(600,813),(87,813),(87,1008)],'Holder black → converter input GND; solder connection')
    wire('W3','REG.VOUT','P48',[(646,869),(646,yrow(railrows[47]))],'Converter VOUT → left + rail hole 48')
    wire('W4','REG.GND_OUT','G50',[(622,1008),(622,1067),(772,1067)],'Converter output GND → left − rail hole 50')
    wire('B+','P25','P26',[(727,yrow(railrows[24])),(727,yrow(railrows[25]))],'Bridge positive rail midpoint: P25 → P26')
    wire('B−','G25','G26',[(792,yrow(railrows[24])),(792,yrow(railrows[25]))],'Bridge ground rail midpoint: G25 → G26')
    wire('W5','P8','S2.VBUS',[(689,yrow(railrows[7])),(689,244),(1850,244),(1850,568)],'Left + rail hole 8 → S2 outer-right bottom pin 5V/VBUS')
    wire('W6','G10','S2.GND',[(670,yrow(railrows[9])),(670,257),(1820,257),(1820,539)],'Left − rail hole 10 → S2 outer-right second pin from bottom GND')
    wire('W7','S2.GPIO16','j38',[(1785,510),(1785,789),(1185,789),(1185,yrow(38))],'S2 GPIO16 → breadboard j38')
    wire('W8','i38','SERVO.S',[(1041,816),(1215,816),(1215,1010)],'Breadboard i38 → servo signal; i38 and j38 share the same strip')
    wire('W9','P35','SERVO.V+',[(686,yrow(railrows[34])),(686,1168),(1237,1168),(1237,977)],'Left + rail hole 35 → servo red power pin')
    wire('W10','G38','SERVO.GND',[(663,yrow(railrows[37])),(663,1190),(1194,1190),(1194,944)],'Left − rail hole 38 → servo brown/black ground pin')
    for x,y,s,n in [(508,778,'W1','BAT+'),(510,810,'W2','GND'),(566,864,'W3','5V'),(549,1059,'W4','GND'),(1770,239,'W5','5V'),(1740,285,'W6','GND'),(1730,782,'W7','PWM'),(1070,811,'W8','PWM'),(882,1163,'W9','5V'),(882,1213,'W10','GND'),(682,677,'B+','5V'),(788,701,'B−','GND')]:flag(x,y,s,C[n])
    txt(977,724,'i38 / j38',14,C['PWM'],700)
    # Footer instructions are part of downloadable image.
    rect(55,1245,980,159,'#e5eee8','#c8d4cb',12)
    txt(78,1278,'BEFORE POWER',18,weight=700)
    for i,s in enumerate(['1  Remove cells while soldering and inserting jumpers.', '2  Disconnect S2 and servo. Measure + rail to − rail: about 5.0 V.', '3  Power OFF, connect S2 and servo, then switch ON for an unloaded test.', 'Rail numbers P/G count holes from the top. Main rows use a–j / 1–63.']):txt(78,1308+i*26,s,17)
    rect(1060,1245,985,159,'#f0e6d4','#dacaac',12)
    txt(1083,1278,'USB PROGRAMMING: DISCONNECT THE S2’S THREE JUMPERS FIRST',17,weight=700)
    for i,s in enumerate(['The S2’s 5V/VBUS pin is directly connected to USB power.', 'Turning the holder OFF alone does not isolate the servo rail from USB.', 'Never connect raw battery voltage to 5V/VBUS, 3V3, or GPIO.', 'Cosmetic internals simplified. Hardware load test and actual-board match pending.']):txt(1083,1308+i*26,s,17)
    txt(55,1440,'Sources: WEMOS S2 Mini V1.0.0 pinout/schematic · Amazon B09N1GDWQ9 / B0GCW44FDL · TowerPro MG90S. Reference build, not a certified assembly.',15)
    add('</svg>')
    OUT.mkdir(parents=True,exist_ok=True);WEB.mkdir(parents=True,exist_ok=True)
    svg='\n'.join(a)+'\n'
    manifest={'schema_version':1,'width':W,'height':H,'board_reference':'LOLIN S2 Mini V1.0.0, top view, USB down','terminals':terminals,'routes':routes,'rail_note':'P and G ordinal hole numbers, each split at 25/26; both midpoint bridges installed','usb_rule':'Disconnect all three S2 jumpers before connecting USB.'}
    for p in (OUT,WEB):
        (p/'breadboard.svg').write_text(svg)
        (p/'wiring.json').write_text(json.dumps(manifest,indent=2)+'\n')
        with (p/'connections.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=['id','from','to','net','note']);w.writeheader()
            w.writerows({k:r[k] for k in w.fieldnames} for r in routes)
    print(OUT/'breadboard.svg')

if __name__=='__main__':render()
