"""Independent connection-graph check of the received-board solder diagram."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'hardware/wiring/solder-prep'
d=json.loads((folder/'connections.json').read_text());t=d['terminals'];adj={x:set() for x in t}
def join(a,b):adj[a].add(b);adj[b].add(a)
# Internal continuity of the depicted split breadboard rails and converter ground.
for group in [('P.S2','P.A'),('P.B','P.IN','P.SERVO'),('G.S2','G.A'),('G.B','G.IN','G.SERVO'),('SIG.A','SIG.B'),('REG.GND_IN','REG.GND_OUT')]:
 for x in group[1:]:join(group[0],x)
for wire in d['wires']:
 a,b=wire['from'],wire['to'];assert wire['points'][0]==t[a]['xy'] and wire['points'][-1]==t[b]['xy']
 join(a,b)
seen=set();groups=[]
for node in adj:
 if node in seen:continue
 found=set();todo=[node]
 while todo:
  x=todo.pop()
  if x in found:continue
  found.add(x);todo.extend(adj[x]-found)
 seen.update(found);groups.append(found)
required=[{'BAT.red','REG.VIN'}, {'REG.VOUT','S2.VBUS','SERVO.V+','P.S2','P.A','P.B','P.IN','P.SERVO'}, {'BAT.black','REG.GND_IN','REG.GND_OUT','S2.GND','SERVO.GND','G.S2','G.A','G.B','G.IN','G.SERVO'}, {'S2.GPIO16','SIG.A','SIG.B','SERVO.S'}]
assert {frozenset(x) for x in groups}=={frozenset(x) for x in required},groups
assert len(d['wires'])==12
assert d['solder_groups']==7 and d['converter_groups']==4
assert set(x for x in t if x.startswith('S2.'))=={'S2.VBUS','S2.GND','S2.GPIO16'}
assert t['S2.VBUS']['xy'][0]==t['S2.GND']['xy'][0]==t['S2.GPIO16']['xy'][0]
assert t['S2.GPIO16']['xy'][1]<t['S2.GND']['xy'][1]<t['S2.VBUS']['xy'][1]
assert t['REG.VOUT']['xy'][0]<t['REG.GND_OUT']['xy'][0] and t['REG.VIN']['xy'][0]<t['REG.GND_IN']['xy'][0]
assert t['REG.VOUT']['xy'][1]<t['REG.VIN']['xy'][1] and t['REG.GND_OUT']['xy'][1]<t['REG.GND_IN']['xy'][1]
ET.parse(folder/'solder-prep.svg')
config=json.loads((ROOT/'firmware/config.s2-demo.example.json').read_text());assert [c['pin'] for c in config['channels']]==[16]
print('PASS: 7 solder groups, 12 wires, 4 isolated required nets, both rail bridges, photo orientation and GPIO16 firmware profile.')
