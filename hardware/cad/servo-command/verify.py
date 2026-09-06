"""Validate binary STL exports independently of Blender. Python standard library only."""
from pathlib import Path
from collections import Counter
import json,struct
root=Path(__file__).resolve().parent/'generated'
manifest=json.loads((root/'validation.json').read_text())
results=[]
for part in manifest['parts']:
    p=root/part['file'];data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+n*50,p
    edges=Counter();vertices=set();volume=0
    for i in range(n):
        vals=struct.unpack_from('<12fH',data,84+i*50)
        tri=[tuple(round(v,5) for v in vals[j:j+3]) for j in(3,6,9)]
        assert len(set(tri))==3,f'degenerate triangle {p}'
        vertices.update(tri)
        for a,b in zip(tri,tri[1:]+tri[:1]):edges[tuple(sorted((a,b)))]+=1
        a,b,c=tri;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    assert all(v==2 for v in edges.values()),f'non-manifold {p}'
    lo=[min(v[i] for v in vertices) for i in range(3)];dim=[max(v[i] for v in vertices)-lo[i] for i in range(3)]
    assert abs(lo[2])<.001,p
    assert all(0<d<=256 for d in dim),p
    assert volume>0,p
    results.append({'file':p.name,'closed_two_faces_per_edge':True,'positive_volume_mm3':round(volume,2),'on_print_bed':True,'fits_A1_256mm':True,'dimensions_mm':[round(d,3) for d in dim]})
assert {p.name for p in root.glob('*.stl')}=={p['file'] for p in manifest['parts']}
(root/'stl-verification.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'{len(results)} STL files pass topology, orientation, bed placement and A1 envelope checks. Physical fit remains unverified.')
