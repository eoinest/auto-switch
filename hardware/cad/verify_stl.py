"""Independent binary STL checks; no Blender dependency. Run with Python 3."""
import json, struct
from collections import Counter
from pathlib import Path
root = Path(__file__).resolve().parent / 'generated'
results=[]
for path in sorted(root.glob('*.stl')):
    data=path.read_bytes(); count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*count, path
    edges=Counter();verts=set();volume=0
    for i in range(count):
        row=struct.unpack_from('<12fH',data,84+50*i)
        tri=[tuple(round(v,5) for v in row[j:j+3]) for j in (3,6,9)]
        assert len(set(tri))==3, f'Degenerate face in {path}'
        verts.update(tri)
        for a,b in zip(tri,tri[1:]+tri[:1]):edges[tuple(sorted((a,b)))]+=1
        a,b,c=tri
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    assert all(n==2 for n in edges.values()), f'Non-manifold edges in {path}'
    mins=[min(v[i] for v in verts) for i in range(3)]
    dims=[max(v[i] for v in verts)-mins[i] for i in range(3)]
    assert abs(mins[2])<.001, f'Not on print bed: {path}'
    assert all(0<d<=256 for d in dims), f'Outside A1 print volume: {path}'
    assert volume>0, f'Inverted volume: {path}'
    results.append({'file':path.name,'triangles':count,'dimensions_mm':[round(d,3) for d in dims],'manifold':True,'positive_volume':True,'on_bed':True,'fits_A1':True})
assert len(results)==9, 'Expected 9 generated STL files'
(root/'stl-verification.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
