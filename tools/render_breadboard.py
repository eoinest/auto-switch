"""Render a hole-addressed bench diagram and placement table from layout.json."""
from pathlib import Path
from html import escape
import csv, io, json

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'hardware/wiring/breadboard/layout.json'
plan=json.loads(PLAN.read_text())
W,H=2150,1690
COL={'VSYS':'#8454b5','GND':'#344858','ADC':'#008582','5V':'#ca4225','PACK_SW':'#b37316','SERVO_ENABLE':'#b18b08','PWM0_RAW':'#257bbe','PWM0':'#257bbe','PWM1_RAW':'#b05199','PWM1':'#b05199'}
xs=dict(zip('abcdefghij',[710,730,750,770,790,850,870,890,910,930]))
def xy(h):return xs[h[0]],260+(int(h[1:])-1)*20
def netcolor(n):return COL.get(n,'#ba421f')
a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" data-breadboard="true" aria-labelledby="bb-title bb-desc"><title id="bb-title">Auto Switch — exact breadboard layout</title><desc id="bb-desc">Headered Pico W bridges c3 to c22 and h3 to h22, USB upward. Breadboard holes and jumper IDs match the placement table. Motor power harness remains beside the breadboard. Side power rails are unused.</desc><style>[data-breadboard] text{{font-family:Arial,sans-serif;fill:#203b42}}.bb-title{{font-size:33px;font-weight:bold}}.bb-body{{font-size:19px}}.bb-small{{font-size:15px}}.bb-tiny{{font-size:12px}}.bb-label{{font-size:17px;font-weight:bold}}.bb-pin{{font-size:11px}}.bb-dim{{opacity:.15}}.bb-focus{{filter:drop-shadow(0 0 3px #98b342)}}.bb-jumper{{fill:none;stroke-width:5;stroke-linejoin:round;stroke-linecap:round}}</style><rect width="{W}" height="{H}" fill="#f7f6f0"/>']
def text(x,y,t,c='body',fill=None):a.append(f'<text x="{x}" y="{y}" class="bb-{c}"'+(f' style="fill:{fill}"' if fill else '')+f'>{escape(str(t))}</text>')
def rect(x,y,w,h,fill='#fff',r=8,stroke='#b9c8ca'):a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
def path(points,color,width=5):
 d='M'+'L'.join(f'{x},{y}' for x,y in points)
 a.append(f'<path d="{d}" class="bb-jumper" stroke="#f7f6f0" style="stroke-width:{width+5}px"/>')
 a.append(f'<path d="{d}" class="bb-jumper" stroke="{color}" style="stroke-width:{width}px"/>')
def dot(x,y,c):a.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{c}" stroke="#fff"/>')
def group(step,id):a.append(f'<g data-bb-step="{step}" data-bb-item="{id}">')
def end():a.append('</g>')
def tag(x,y,t,color):
 rect(x-5,y-17,len(t)*9+10,23,'#fff',4,color);text(x,y,t,'small',color)
text(40,53,'Auto Switch · breadboard bench layout','title')
text(40,87,'Exact hole addresses for your headered Pico. USB socket points UP. Components shown from above.','body')
text(40,120,'Power OFF while wiring. Motor supply wiring stays beside the breadboard. Side + / − rails are NOT USED.','body')
text(40,150,'J = male/male jumper on the breadboard. L = lead to the separate power harness. Crossing cables do not connect.','small')
# Left assembly key and practical strip explanation.
rect(40,200,470,320,'#edf5ef')
text(63,237,'READ THE HOLE LABELS','label')
for y,line in [(270,'a45 means column a, row 45.'),(301,'a45–e45 are one connected strip.'),(332,'f45–j45 are another strip.'),(363,'The centre trench separates those strips.'),(394,'Row 45 is NOT connected to row 46.'),(438,'Pico headers: c3–c22 and h3–h22.'),(469,'Keep columns a/b and i/j accessible.'),(500,'Do not use any side power rail.')]:text(63,y,line,'body' if y<410 else 'small')
# Full-size board: every tie strip and hole, with power rails visually unused.
rect(590,210,480,1360,'#e5e5de',15)
rect(686,226,124,1314,'#fafaf6',5);rect(830,226,124,1314,'#fafaf6',5)
rect(813,238,14,1280,'#cacdc6',2)
for x in (624,644,1000,1020):
 for row in sorted(3+6*group+k for group in range(10) for k in range(5)):
  cy=260+(row-1)*20
  a.append(f'<circle cx="{x}" cy="{cy}" r="3.5" fill="#bbbdb5"/>')
text(612,243,'UNUSED','tiny');text(985,243,'UNUSED','tiny')
for letter,x in xs.items():text(x-4,241,letter,'small');text(x-4,1559,letter,'small')
for row in range(1,64):
 cy=260+(row-1)*20
 for cols in ('abcde','fghij'):
  a.append(f'<path d="M{xs[cols[0]]} {cy}H{xs[cols[-1]]}" stroke="#e4e7df" stroke-width="10"/>')
 for letter,x in xs.items():a.append(f'<circle data-hole="{letter}{row}" cx="{x}" cy="{cy}" r="4.3" fill="#949d98"/>')
 text(665,cy+4,row,'tiny');text(966,cy+4,row,'tiny')
# Put long insulated jumpers behind the mounted parts so holes remain explicit.
for j in plan['jumpers']:
 group(j['step'],j['id']);p,q=xy(j['a']),xy(j['b']);color=netcolor(j['net'])
 # Loop through different side channels, never imply rows along the route are plugged.
 lanes={'J1':1095,'J2':1125,'J3':555,'J4':1160,'J5':1190,'J6':1220,'J7':778,'J8':680}
 lane=lanes[j['id']]
 # J1/J2/J6 leave the left half through the central free space below the Pico.
 path([p,(lane,p[1]),(lane,q[1]),q],color)
 dot(*p,color);a[-1]=a[-1].replace('<circle ',f'<circle data-bb-endpoint="{j["a"]}" ');dot(*q,color);a[-1]=a[-1].replace('<circle ',f'<circle data-bb-endpoint="{j["b"]}" ')
 ty=(p[1]+q[1])/2
 tag(lane+8,ty,j['id'],color)
 end()
# Pico footprint and only the labels useful for this build. Actual 40 pin holes remain occupied.
group(1,'PICO')
rect(737,286,166,406,'#247756',5, '#175540')
rect(791,268,58,31,'#c9d0d0',3)
text(788,316,'USB ↑','small','#fff')
rect(797,405,47,59,'#313c3a',2);text(789,493,'PICO W','small','#fff')
text(780,522,'HEADERS','tiny','#fff');text(783,543,'INSTALLED','tiny','#fff')
used={'39':'VSYS','38':'GND','31':'GP26','22':'GP17','21':'GP16','20':'GP15','40':'VBUS'}
for num,hole in plan['pico_pins'].items():
 x,y=xy(hole);rect(x-4,y-4,8,8,'#d8c27a',0)
 if num in used:
  tx=x+9 if hole[0]=='c' else x-48
  text(tx,y+4,used[num],'pin','#fff')
text(752,281,'pin 1','tiny');text(872,281,'40','tiny')
end()
# Passive components occupy two separate holes, drawn with leads and body/value callouts.
for part in plan['placements']:
 ref=part['ref'];p,q=[xy(h) for h in part['terminals'].values()];x,y=p;xx,yy=q
 group(part['step'],ref)
 path([p,q],'#8d928a',3)
 if part['type']=='capacitor':
  # A small radial ceramic with adjacent-row leads.
  a.append(f'<ellipse cx="{x+13}" cy="{(y+yy)/2}" rx="13" ry="9" fill="#d89936" stroke="#8f5b18"/>')
 elif part['type']=='diode':
  rect(x-8,y+28,16,44,'#303841',3)
  rect(x-8,y+61,16,7,'#cbd3d9',0)
 else:
  rect(x-7,y+29,14,42,'#d6c79f',4)
  bands=['#78432b','#111','#111','#e47921','#78432b'] if part['value'].startswith('100') else ['#efcd3c','#8646a0','#111','#b83228','#78432b'] if part['value'].startswith('47') else ['#78432b','#111','#111','#78432b','#78432b']
  for offset,color in zip((34,41,48,55,65),bands):rect(x-7,y+offset,14,3,color,0)
 dot(*p,'#6c6358');a[-1]=a[-1].replace('<circle ',f'<circle data-bb-endpoint="{list(part["terminals"].values())[0]}" ');dot(*q,'#6c6358');a[-1]=a[-1].replace('<circle ',f'<circle data-bb-endpoint="{list(part["terminals"].values())[1]}" ')
 # Labels stay in the centre trench or immediately outside board; hole table is authoritative.
 if ref in ('D1','R_TOP','R_EN'):tx=460;ty=(y+yy)/2
 elif ref=='R_BOTTOM':tx=465;ty=(y+yy)/2+18
 elif ref=='C_ADC':tx=801;ty=y-12
 else:tx=938;ty=(y+yy)/2+7
 tag(tx,ty,ref,'#384d4d')
 end()
# Six low-current leads from exact breadboard holes to an identified terminal on external assembly.
# Lead endpoints are along a tidy terminal bank; external motor wiring is not routed through the breadboard.
lead_y={'L1':330,'L2':1480,'L3':430,'L4':660,'L5':880,'L6':1080}
for lead in plan['leads']:
 group(lead['step'],lead['id']);p=xy(lead['hole']);yy=lead_y[lead['id']];color=netcolor(lead['net'])
 # Short visual routes through reserved vertical channels on each side of the board.
 lane={'L1':525,'L2':535,'L3':545,'L4':565,'L5':1250,'L6':1280}[lead['id']]
 if lead['id'] in ('L1','L3'):
  top=180 if lead['id']=='L1' else 195
  pts=[p,(lane,p[1]),(lane,top),(1305,top),(1305,yy),(1370,yy)]
 elif lead['id']=='L2':pts=[p,(lane,p[1]),(lane,1595),(1330,1595),(1330,yy),(1370,yy)]
 elif lead['id']=='L4':pts=[p,(lane,p[1]),(lane,1625),(1310,1625),(1310,yy),(1370,yy)]
 else:pts=[p,(lane,p[1]),(lane,yy),(1370,yy)]
 path(pts,color,4);dot(*p,color);a[-1]=a[-1].replace('<circle ',f'<circle data-bb-endpoint="{lead["hole"]}" ');dot(1370,yy,color)
 tag(1335,yy-13,lead['id'],color)
 end()
# Separate power harness, logical terminal cards (not a guessed PCB footprint).
rect(1350,220,760,1320,'#fffdf8',12)
text(1372,257,'BESIDE THE BREADBOARD','label')
text(1372,286,'Existing power harness · follow board silkscreen','small')
# Redraw exposed lead plugs on top of the harness background.
for lead in plan['leads']:
 yy=lead_y[lead['id']];color=netcolor(lead['net']);dot(1370,yy,color)
 text(1384,yy-2,f'{lead["id"]} · {lead["net"]}','label',color)
 text(1384,yy+22,f'Breadboard {lead["hole"]}','small',color)
# Right-side power topology, one supply chain and continuous ground.
for x,y,w,h,title,lines in [
 (1600,320,460,100,'Battery → fuse → RCY → MASTER',['Master VIN receives fused battery positive.']),
 (1600,470,460,100,'REGULATOR · Pololu 2574',['VIN ← PACK_SW    VOUT → regulated 5 V']),
 (1600,620,460,100,'SERVO GATE · Pololu 2810',['VIN ← 5 V    VOUT → servo +    ON ← L4']),
 (1600,810,460,120,'SERVO 0',['Power → switched 5 V; ground → PGND','Only signal wire → L5 / breadboard j35']),
 (1600,1010,460,120,'SERVO 1 · optional',['Power → switched 5 V; ground → PGND','Only signal wire → L6 / breadboard j45'])]:
  if title.startswith('SERVO 1'):group(5,'external_servo1')
  rect(x,y,w,h,'#fff1e5');text(x+15,y+28,title,'label')
  for k,line in enumerate(lines):text(x+15,y+60+k*25,line,'small')
  if title.startswith('SERVO 1'):end()
# Physical power splice points are explicit labels. All traces carry their node names.
path([(1830,420),(1830,470)],'#b37316',5);text(1845,451,'PACK_SW','small')
path([(1830,570),(1830,620)],'#ca4225',5);text(1845,600,'5 V','small')
path([(1830,720),(1830,810)],'#ca4225',5);text(1845,788,'SERVO_5V','small')
path([(2078,755),(2078,990),(1830,990),(1830,1010)],'#ca4225',5);path([(1830,755),(2078,755)],'#ca4225',5);dot(1830,755,'#ca4225')
# Off-board parts have specific lead instructions, with polarity clearly stated.
rect(1590,1180,480,190,'#edf1ec')
text(1605,1210,'KEEP THESE ON THE POWER HARNESS','label')
for y,t in [(1243,'C1 470 µF: + to 5 V, − stripe to PGND'),(1273,'D2 1N5819: stripe to SERVO_5V; other to PGND'),(1303,'R_BLEED 1 kΩ: SERVO_5V to PGND'),(1339,'Short, insulated 22 AWG motor power wires.')]:text(1605,y,t,'small')
text(1590,1420,'PGND joins battery −, both switches, regulator,','small');text(1590,1447,'both servos and the three passive returns above.','small')
text(1590,1480,'MASTER ON unused · REG ENABLE unused','small');text(1590,1507,'Servo-gate physical slider stays OFF.','small')
# Left hole table readable beside diagram: no ambiguous component value locations.
text(40,575,'COMPONENTS · TWO HOLES EACH','label')
for i,p in enumerate(plan['placements']):
 yy=615+i*68;text(45,yy,p['ref']+' · '+p['value'],'label');text(45,yy+26,' → '.join(p['terminals'].values())+(' · stripe at a35' if p['ref']=='D1' else ''),'body')
text(40,1150,'PICO PINS USED','label')
for i,(pin,hole,signal) in enumerate([(39,'h4','VSYS'),(38,'h5','GND'),(20,'c22','GP15'),(21,'h22','GP16'),(22,'h21','GP17'),(31,'h12','GP26 / ADC')]):text(45,1187+i*34,f'{pin:2} · {signal:12} · {hole}','body')
text(40,1430,'Check that your board has the same row labels.','small')
text(40,1456,'Do not mirror or rotate the Pico relative to this view.','small')
text(40,1482,'Bands show nominal 1% parts; verify actual values.','small')
text(40,1510,'Leads shown as routes, not pre-cut wire lengths.','small')
text(40,1657,'Bench layout only. It is not the soldered Perma-Proto layout inside the printed enclosure. Verify continuity before applying power.','body')
# Machine-readable hole occupancy is generated independently of decorative wire curves.
for ref,hole in plan['terminal_bindings'].items():a.append(f'<metadata data-bb-terminal="{ref}" data-bb-hole="{hole}"/>')
a.append('</svg>')
(ROOT/'hardware/wiring/breadboard/layout.svg').write_text('\n'.join(a)+'\n')
rows=[]
for p in plan['placements']:rows.append(dict(id=p['ref'],kind='component',value=p['value'],start=list(p['terminals'].values())[0],end=list(p['terminals'].values())[1],step=p['step'],optional=p.get('optional',False),note=p.get('note','')))
for j in plan['jumpers']:rows.append(dict(id=j['id'],kind='jumper',value=j['net'],start=j['a'],end=j['b'],step=j['step'],optional=j['optional'],note='Male/male jumper; plug only the endpoints.'))
for l in plan['leads']:rows.append(dict(id=l['id'],kind='external lead',value=l['net'],start=l['hole'],end=l['node'],step=l['step'],optional=l['optional'],note=l['note']))
buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=['id','kind','value','start','end','step','optional','note'],lineterminator='\n');writer.writeheader();writer.writerows(rows)
(ROOT/'hardware/wiring/breadboard/placements.csv').write_text(buf.getvalue())
print('Rendered breadboard layout.svg and placements.csv')
