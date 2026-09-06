"""Independent binary STL audit: topology, bed contact, A1 bounds and master content."""
from pathlib import Path
import collections, hashlib, json, math, struct, sys

def audit(path):
    data=path.read_bytes(); n=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*n, 'invalid STL byte count'
    verts=[]; lookup={}; faces=[]; edges=collections.defaultdict(list)
    volume=bed=down=0.; tris=[]
    for i in range(n):
        row=struct.unpack_from('<12fH',data,84+50*i)
        tri=[tuple(row[j:j+3]) for j in (3,6,9)]; ids=[]
        assert all(math.isfinite(c) for p in tri for c in p)
        for p in tri:
            key=tuple(round(c,5) for c in p)
            if key not in lookup:lookup[key]=len(verts);verts.append(p)
            ids.append(lookup[key])
        assert len(set(ids))==3, 'collapsed triangle'
        a,b,c=tri;u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
        normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        area=math.sqrt(sum(x*x for x in normal))/2;assert area>1e-9
        volume+=sum(a[k]*normal[k] for k in range(3))/6
        if max(abs(p[2]) for p in tri)<1e-5:bed+=area
        if min(p[2] for p in tri)>1e-5 and normal[2]<-2*area*math.sqrt(.5):down+=area
        for j,k in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((j,k)))].append((i,j,k))
        faces.append(ids);tris.append(tri)
    neighbors=[[] for _ in faces]
    for pair in edges.values():
        assert len(pair)==2, 'non-manifold edge'
        a,b=pair;assert a[1]==b[2] and a[2]==b[1], 'inconsistent winding'
        neighbors[a[0]].append(b[0]);neighbors[b[0]].append(a[0])
    seen=set();components=[]
    for f in range(n):
        if f in seen:continue
        todo=[f];seen.add(f);component=[]
        while todo:
            i=todo.pop();component.append(i)
            for j in neighbors[i]:
                if j not in seen:seen.add(j);todo.append(j)
        components.append(component)
    bounds=[[min(p[k] for p in verts),max(p[k] for p in verts)] for k in range(3)]
    assert abs(bounds[2][0])<1e-5, 'not on bed'
    assert volume>0 and bed>0
    summary={'file':path.name,'sha256':hashlib.sha256(data).hexdigest(),'triangles':n,'connected_solids':len(components),'closed_consistent_winding':True,'bounds_mm':bounds,'volume_mm3':volume,'bed_contact_area_mm2':bed,'above_bed_downfacing_area_mm2':down}
    return summary,tris,components

if __name__=='__main__':
    directory=Path(sys.argv[1]); master=Path(sys.argv[2])
    reports=[]; counts=[]; volumes=[]
    for path in sorted(directory.glob('*.stl')):
        summary,_,_=audit(path);assert summary['connected_solids']==1
        reports.append(summary);counts.append(summary['triangles']);volumes.append(summary['volume_mm3'])
    result,tris,components=audit(master)
    assert len(components)==len(reports)
    assert sum(counts)==result['triangles']
    assert abs(sum(volumes)-result['volume_mm3'])<.15
    assert all(0<=result['bounds_mm'][k][0]<result['bounds_mm'][k][1]<=256 for k in (0,1))
    boxes=[]
    for comp in components:
        points=[p for i in comp for p in tris[i]]
        boxes.append([[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)])
        assert abs(min(p[2] for p in points))<1e-5
    gaps=[]
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:
            gap=max(max(a[k][0]-b[k][1],b[k][0]-a[k][1]) for k in (0,1))
            assert gap>=1, 'overlap or insufficient spacing';gaps.append(gap)
    output={'status':'PASS: mesh and layout checks; physical fit and slicer bridging unverified','parts':reports,'master':result,'master_matches_individual_triangle_count_and_volume':True,'each_part_on_bed':True,'minimum_pairwise_bounding_box_gap_mm':min(gaps),'fits_256mm_bed':True}
    (master.parent/'independent-stl-audit.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))
