#!/usr/bin/env python3
"""Connectivity check using breadboard strip/rail topology, not route colors."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'hardware/wiring/s2-aa-poc/wiring.json').read_text())
parent={}
def root(n):
    parent.setdefault(n,n)
    if parent[n]!=n:parent[n]=root(parent[n])
    return parent[n]
def join(a,b):parent[root(a)]=root(b)
for n in p['terminals']:root(n)
for prefix in ['P','G']:
    for start in [1,26]:
        for i in range(start+1,start+25):join(prefix+str(start),prefix+str(i))
for row in range(1,64):
    for cols in ['abcde','fghij']:
        for c in cols[1:]:join(cols[0]+str(row),c+str(row))
join('REG.GND_IN','REG.GND_OUT')
seen=set()
for w in p['routes']:
    assert w['id'] not in seen;seen.add(w['id'])
    assert w['from'] in p['terminals'] and w['to'] in p['terminals']
    assert w['points'][0]==p['terminals'][w['from']]['xy']
    assert w['points'][-1]==p['terminals'][w['to']]['xy']
    for x,y in w['points']:assert 0<=x<=p['width'] and 0<=y<=p['height']
    join(w['from'],w['to'])
required=[['BAT.red','REG.VIN'],['BAT.black','REG.GND_IN','REG.GND_OUT','S2.GND','SERVO.GND','G1','G50'],['REG.VOUT','S2.VBUS','SERVO.V+','P1','P50'],['S2.GPIO16','j38','i38','SERVO.S']]
for group in required:assert len({root(n) for n in group})==1,group
assert len({root(group[0]) for group in required})==4,'Short between required distinct nets'
assert len(seen)==12
# Reference pin geometry: USB down, GPIO16 above GND above VBUS, outer right.
pins=[p['terminals']['S2.'+s]['xy'] for s in ['GPIO16','GND','VBUS']]
assert len({pt[0] for pt in pins})==1 and pins[0][1]<pins[1][1]<pins[2][1]
print('PASS: 12 wires; both rail bridges; shared signal strip; four distinct required nets; reference pin order.')
