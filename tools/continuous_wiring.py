"""One continuous circuit; explicit terminal geometry is checked against the harness."""
from html import escape
import json


def draw(SVG, harness):
    s = SVG(2200,1400,'Auto Switch — one complete circuit',
        'A continuous schematic of every external harness connection. All grounds join the bottom return bus. Wire crossings with a white gap are not connected; filled dots are junctions. The Pico internal USB and 3.3 volt power path is shown inside its board outline.')
    s.items.append('<style>.wire{stroke-width:3}.net{font-size:16px}.name{font-size:22px}.small{font-size:16px}.terminal{fill:#fff;stroke:#344858;stroke-width:2}</style>')
    s.text(45,55,'Auto Switch · the whole circuit','title')
    s.text(45,90,'Every wire drawn. Follow battery power across the top, signals through the middle, and the common return along the bottom.','subtitle')
    s.text(45,125,'● Joined wires       White gap at a crossing = not connected       Pad numbers are physical Pico pads, not GPIO numbers','body')
    s.text(45,157,'Orange: raw battery · Red: regulated / motor power · Purple: Pico supply · Blue: control · Teal: sensing · Gray: ground','small')
    nets = harness['nets']
    term_net = {t:n for n,ts in nets.items() for t in ts}
    terminals = {}; wires = {n:[] for n in nets}; junctions=[]
    def pin(t,x,y):
        assert t not in terminals,t
        terminals[t]=(x,y)
    def wire(n,*points): wires[n].append(points)
    def dot(n,x,y):junctions.append((n,x,y))
    def box(x,y,w,h,title,lines,part,fill='#fff'):
        s.box(x,y,w,h,title,lines,part,fill)
    def r(ref,x,y,value,vertical=True):
        s.resistor(x,y,ref,value,vertical,'adc' if ref in ('R_TOP','R_BOTTOM') else 'signal')
        pin(ref+'.1',x,y);pin(ref+'.2',x if vertical else x+82,y+72 if vertical else y)
    def cap(ref,x,y,value):
        s.path(f'M{x} {y}v26m0 14v32','ground',arrow=False)
        s.path(f'M{x-21} {y+26}h42m-42 14h42','ground',arrow=False)
        s.text(x+29,y+25,ref,'net');s.text(x+29,y+53,value,'small')
        pin(ref+('.positive' if ref=='C1' else '.1'),x,y)
        pin(ref+('.negative' if ref=='C1' else '.2'),x,y+72)
        if ref=='C1':s.text(x-37,y+24,'+','name');s.text(x+29,y+77,'− stripe','small')
    def diode(ref,x,y,down=True):
        # Diode direction symbol with the Schottky hooked cathode bar.
        # Vertical symbol: anode at top for D1, cathode at top for D2.
        transform=f'translate({x} {y})'+('' if down else ' translate(0 72) rotate(180)')
        s.items.append(f'<g transform="{transform}" stroke="#ba421f" stroke-width="3" fill="none"><path d="M0 0V24M0 48V72M-17 24H17L0 44ZM-22 40V48H22V56"/></g>')
        s.text(x+28,y+22,ref+' · 1N5819','net');s.text(x+28,y+49,'stripe '+('↓ to VSYS' if down else '↑ to servo +'),'small')
        pin(ref+('.anode' if down else '.cathode'),x,y)
        pin(ref+('.cathode' if down else '.anode'),x,y+72)

    # Source chain, physical components and connection points.
    box(45,205,200,160,'4 × AA NiMH',['4.8 V nominal','Pololu 1153 holder','Recharge externally'],'BAT','#fff4df')
    pin('BAT.red',245,280);pin('BAT.black',135,365)
    s.text(308,228,'F1 · 2 A time-delay','net');s.text(309,325,'Fuse close to battery +','small')
    s.rect(325,266,70,28,'#fff4df',radius=3);s.path('M300 280H325M395 280H420','battery',arrow=False)
    pin('F1.in',300,280);pin('F1.out',420,280)
    box(520,205,250,160,'Master switch',['Pololu 2810 LV','Physical slide switch','ON: leave unconnected'],'MASTER','#fff4df')
    pin('MASTER.VIN',520,280);pin('MASTER.VOUT',770,280);pin('MASTER.GND',590,365)
    s.text(484,261,'VIN','small');s.text(777,261,'VOUT','small')
    box(875,205,265,160,'5 V regulator',['Pololu S18V20F5','Buck-boost converter','ENABLE: unconnected'],'REG','#ffece4')
    pin('REG.VIN',875,280);pin('REG.VOUT',1140,280);pin('REG.GND',990,365)
    s.text(838,261,'VIN','small');s.text(1148,261,'VOUT','small')
    box(1340,205,255,160,'Servo power gate',['Pololu 2810 LV','Physical slider OFF','GP15 controls ON'],'GATE','#ffece4')
    pin('GATE.VIN',1340,280);pin('GATE.VOUT',1595,280);pin('GATE.ON',1435,365);pin('GATE.GND',1555,365)
    s.text(1303,261,'VIN','small');s.text(1603,261,'VOUT','small');s.text(1392,351,'ON','net');s.text(1520,351,'GND','small')

    # Controller low on the page, allowing all supply branches above it.
    s.rect(650,665,485,450,'#edf5ef','#68a184',18)
    s.text(675,701,'HEADERLESS PICO W','name');s.text(675,729,'Power components already on board','small')
    pin('PICO.pin39_VSYS',1030,665);pin('PICO.pin38_GND',725,1115)
    pin('PICO.pin31_GP26',650,930);pin('PICO.pin20_GP15',1135,780)
    pin('PICO.pin21_GP16',1135,900);pin('PICO.pin22_GP17',1135,1020)
    s.text(1050,653,'39 · VSYS','net');s.text(738,1100,'38 · GND','net')
    s.text(670,924,'31 · GP26','net')
    for y,txt in [(780,'20 · GP15'),(900,'21 · GP16'),(1020,'22 · GP17')]:s.text(990,y+29 if y==780 else y-12,txt,'net')
    s.text(680,1069,'40 · VBUS and 36 · 3V3 OUT: no harness wire','small')
    # Internal supply explanation, not additional harness components.
    box(695,815,225,64,'3.3 V regulator',[],None,'#fff')
    s.path('M1030 665V756H808V815','vsys');s.dot(1030,756,'vsys')
    s.path('M808 879V969','chip')
    box(690,969,245,62,'Chip + Wi-Fi',[],None,'#dbedde');s.text(818,952,'3.3 V','net')
    s.text(680,759,'VBUS','small')
    s.path('M650 780H748V756H770','usb',arrow=False)
    s.items.append('<path d="M770 743V769L788 756ZM791 741V771M791 756H1030" fill="white" stroke="#7354b3" stroke-width="3"/>')
    s.text(677,806,'USB diode','small')
    box(355,685,210,125,'Optional USB',['USB cable → socket','Nominal 5 V','Socket is on Pico'],'USB','#f0eafa')
    s.path('M565 750H605V780H650','usb',arrow=False)
    wire('GND',(395,810),(395,850),(610,850),(610,1115),(725,1115))
    dot('GND',725,1115)
    s.text(400,839,'USB GND','small')

    # Real external passives.
    diode('D1',850,495,True)
    cap('C1',1230,465,'470 µF / 10 V')
    diode('D2',1660,430,False)
    r('R_BLEED',2110,430,'1 kΩ · ¼ W')
    # Keep this edge component’s labels inside the canvas.
    s.items[-2]=s.items[-2].replace('x="2129"','x="1955"')
    s.items[-1]=s.items[-1].replace('x="2129"','x="1955"')
    r('R_EN',1340,810,'100 kΩ')
    r('R_PWM0',1490,900,'1 kΩ',False)
    r('R_PWM1',1490,1020,'1 kΩ',False)
    r('R_TOP',260,830,'100 kΩ · 1%')
    r('R_BOTTOM',260,980,'47 kΩ · 1%')
    cap('C_ADC',465,980,'100 nF')
    s.text(310,480,'BATTERY SENSING','section')
    s.text(310,510,'Raw pack after master,','small')
    s.text(310,537,'before the 5 V regulator.','small')
    s.text(280,1143,'ADC = pack × 47 / 147','small')
    s.text(280,1170,'≈ 1.53 V at 4.8 V','small')

    # Two actuators, independent timing, common supply/return.
    for i,y in [(0,545),(1,875)]:
        box(1790,y,245,200,f'Servo {i} · MG90S',
            ['Power (red*)','Signal (orange*)','Ground (brown*)', 'Second switch only' if i else 'First switch'],f'SERVO{i}','#fff')
        pin(f'SERVO{i}.power',1900,y);pin(f'SERVO{i}.signal',1790,y+95);pin(f'SERVO{i}.ground',2035,y+160)
    s.text(1790,1130,'* Verify colors on your actual servo.','small')
    s.text(1790,1156,'Servo 1 + R_PWM1 omitted for one switch.','small')

    # One continuous set of polylines per named net, no remote connection labels.
    wire('BAT_POS',(245,280),(300,280))
    wire('FUSED_BAT',(420,280),(520,280))
    wire('PACK_SW',(770,280),(875,280));wire('PACK_SW',(815,280),(815,415),(260,415),(260,830));dot('PACK_SW',815,280)
    wire('5V',(1140,280),(1340,280));wire('5V',(1230,280),(1230,425),(850,425),(850,495));wire('5V',(1230,425),(1230,465));dot('5V',1230,280);dot('5V',1230,425)
    wire('VSYS',(850,567),(850,605),(1030,605),(1030,665))
    wire('SERVO_5V',(1595,280),(2160,280),(2160,845),(1900,845),(1900,875))
    wire('SERVO_5V',(1900,280),(1900,545));wire('SERVO_5V',(1660,280),(1660,430));wire('SERVO_5V',(2110,280),(2110,430))
    for x in (1660,1900,2110):dot('SERVO_5V',x,280)
    wire('ADC',(260,902),(260,930),(650,930));wire('ADC',(260,930),(260,980));wire('ADC',(465,930),(465,980));dot('ADC',260,930);dot('ADC',465,930)
    wire('SERVO_ENABLE',(1135,780),(1435,780),(1435,365));wire('SERVO_ENABLE',(1340,780),(1340,810));dot('SERVO_ENABLE',1340,780)
    wire('PWM0_RAW',(1135,900),(1490,900));wire('PWM0',(1572,900),(1720,900),(1720,640),(1790,640))
    wire('PWM1_RAW',(1135,1020),(1490,1020));wire('PWM1',(1572,1020),(1735,1020),(1735,970),(1790,970))
    wire('GND',(135,1240),(2160,1240))
    dot('GND',135,630)
    grounds={'BAT.black':[(135,365),(135,1240)],'MASTER.GND':[(590,365),(590,630),(60,630),(60,1240),(135,1240)],
        'REG.GND':[(990,365),(990,395),(1165,395),(1165,1240)],'GATE.GND':[(1555,365),(1605,365),(1605,1240)],
        'PICO.pin38_GND':[(725,1115),(725,1240)],'SERVO0.ground':[(2035,705),(2070,705),(2070,1240)],
        'SERVO1.ground':[(2035,1035),(2070,1035)],'D2.anode':[(1660,502),(1660,1240)],
        'C1.negative':[(1230,537),(1230,1240)],'R_BOTTOM.2':[(260,1052),(260,1240)],
        'C_ADC.2':[(465,1052),(465,1240)],'R_EN.2':[(1340,882),(1340,1240)],'R_BLEED.2':[(2110,502),(2110,1240)]}
    for t,points in grounds.items():wire('GND',*points);dot('GND',*points[-1])
    # Insert electrical wires behind symbols/text, so component labels stay readable.
    # Each wire has a paper-colored halo: unrelated crossings have an explicit gap.
    geometry=[]
    colors={'GND':'#344858','BAT_POS':'#ad5c12','FUSED_BAT':'#ad5c12','PACK_SW':'#ad5c12','5V':'#ba421f','VSYS':'#7354b3','SERVO_5V':'#ba421f','ADC':'#137b7d'}
    for n in ['GND']+[n for n in nets if n!='GND']:
        geometry.append(f'<g data-net="{n}"><title>{n}: {escape(", ".join(nets[n]))}</title>')
        for pts in wires[n]:
            d='M'+'L'.join(f'{x} {y}' for x,y in pts)
            geometry.append(f'<path d="{d}" fill="none" stroke="#f7f6f0" stroke-width="9" stroke-linejoin="round"/>')
            geometry.append(f'<path data-wire="{n}" data-points="{escape(json.dumps(pts))}" d="{d}" fill="none" stroke="{colors.get(n,"#176e99")}" stroke-width="3" stroke-linejoin="round"/>')
        geometry.append('</g>')
    for n,x,y in junctions:geometry.append(f'<circle data-junction="{n}" cx="{x}" cy="{y}" r="5" fill="{colors.get(n,"#176e99")}"/>')
    # First five items comprise SVG metadata/style/background; append wires after background.
    background = next(i for i,v in enumerate(s.items) if v.startswith('<rect width="2200"'))
    s.items[background+1:background+1]=geometry
    assert set(terminals)==set(term_net),set(term_net)^set(terminals)
    for t,(x,y) in terminals.items():
        s.items.append(f'<circle class="terminal" data-terminal="{escape(t)}" data-net="{term_net[t]}" cx="{x}" cy="{y}" r="4"><title>{escape(t)}</title></circle>')
    for t in harness['leave_unconnected']:
        s.items.append(f'<metadata data-nc="{escape(t)}">{escape(t)}: no external harness connection</metadata>')
    # Connector poles, inline on the already drawn positive and negative conductors.
    # Dashed bracket identifies the two halves as the same detachable connector.
    s.items.append('<path d="M475 270V385H115" fill="none" stroke="#8b9697" stroke-width="1.5" stroke-dasharray="4 5"/>')
    for x,y in [(475,280),(135,385)]:
        s.rect(x-9,y-8,18,16,'#fff4df',radius=1)
        s.path(f'M{x-9} {y}h18','battery' if y==280 else 'ground',arrow=False)
    s.text(308,355,'RCY disconnect · both poles','small')
    s.text(790,188,'PACK_SW','net');s.text(1180,188,'REGULATED 5 V','net');s.text(1760,188,'SWITCHED SERVO_5V','net')
    s.text(500,916,'ADC','net')
    s.text(47,1282,'COMMON GND — one continuous return. Motor current returns here directly; it does not pass through the Pico.','name')
    s.text(47,1318,'External D1 feeds VSYS. USB feeds VSYS through the Pico’s own diode. USB alone cannot power this servo branch.','body')
    s.text(47,1348,'C1 is BEFORE the gate. D2 and R_BLEED are AFTER it. All values match harness revision '+str(harness['revision'])+'.','body')
    s.text(47,1378,'Electrical topology, not physical board placement. Check silkscreen, diode/capacitor polarity and continuity before powering the assembly.','small')
    s.save('connection-map.svg')
