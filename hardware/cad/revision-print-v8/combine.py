"""Combine current replacement pieces, retaining separate flat-bed solids. Units mm."""
from pathlib import Path
import importlib.util, json, struct, hashlib
ROOT=Path(__file__).resolve().parent
CAD=ROOT.parent
OUT=ROOT/'generated'; OUT.mkdir(exist_ok=True)
PARTS=OUT/'parts'; PARTS.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('audit',CAD/'electronics-retention-v4/verify_stl_independent.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def write(path,triangles):
    with path.open('wb') as f:
        f.write(b'auto-switch v8 replacement set FIT-TEST; units mm; booster fit unverified'.ljust(80,b' '))
        f.write(struct.pack('<I',len(triangles)))
        for a,b,c in triangles:
            u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
            n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            length=sum(x*x for x in n)**.5;n=[x/length for x in n]
            f.write(struct.pack('<12fH',*n,*a,*b,*c,0))

sources=[(CAD/'battery-retention-v7/generated/01_NEW-CARRIER-v7.stl',5,5),
         (CAD/'battery-retention-v7/generated/02_FLAT-CROSSBAR-v7.stl',5,175)]
boost=sorted((CAD/'booster-retention-v1/generated/stl-fit-test').glob('*.stl'))
assert len(boost)>=3,'Booster individual fit-test pieces must exist'
y=5
for p in boost:
    report,_,_=mod.audit(p)
    width=report['bounds_mm'][0][1]-report['bounds_mm'][0][0]
    height=report['bounds_mm'][1][1]-report['bounds_mm'][1][0]
    assert width<106 and y+height<=246,'Booster parts exceed reserved bed area'
    sources.append((p,140,y));y+=height+8
alltris=[]; manifest=[]
for i,(p,x,y) in enumerate(sources,1):
    a,tris,_=mod.audit(p)
    assert a['connected_solids']==1
    assert a['above_bed_downfacing_area_mm2']<.01,'Unexpected unsupported down-facing surface'
    delta=[x-a['bounds_mm'][0][0],y-a['bounds_mm'][1][0],-a['bounds_mm'][2][0]]
    shifted=[tuple(tuple(v[k]+delta[k] for k in range(3)) for v in tri) for tri in tris]
    dst=PARTS/(f'{i:02d}_'+p.name)
    write(dst,shifted);alltris.extend(shifted)
    manifest.append({'source':str(p.relative_to(CAD)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'packed_file':str(dst.relative_to(OUT)), 'translation_mm':delta,'quantity':1})
master=OUT/'auto-switch-ALL-NEW-PIECES-v8-FIT-TEST.stl'
write(master,alltris)
summary,_,_=mod.audit(master)
assert summary['connected_solids']==len(sources)
(OUT/'manifest.json').write_text(json.dumps({'status':'FIT-TEST: received booster thickness and underside unmeasured','master':master.name,'parts':manifest,'reuse':'Existing separate Command wall bracket; no electronics or metal fasteners in STL','units':'mm'},indent=2)+'\n')
print(json.dumps(summary,indent=2))
