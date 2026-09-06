"""Read-only independent assembled-Blender motion audit.
Blender -b --python review_motion_independent.py -- double|triple
Tests complete moving channel assemblies against every neighbor, independently posed.
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
variant=sys.argv[sys.argv.index('--')+1]
out=ROOT/'generated'/variant
bpy.ops.wm.open_mainfile(filepath=str(out/(variant+'-assembled-CONCEPT.blend')))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
n=2 if variant=='double' else 3
xs=[(i-(n-1)/2)*46 for i in range(n)]
def channel(o):
    name=o.name
    for i in range(1,n+1):
        if any(token in name for token in [f'paddle {i}',f'saddle {i}',f'MG90S {i} ',f'Stock horn {i}',f'Soft contact {i}']):return i-1
    return None

def moving(o):return any(t in o.name for t in ['paddle ','Stock horn ','Soft contact '])

def tree(group,T=Matrix.Identity(4)):
    vs=[];fs=[]
    for o in group:
        start=len(vs);vs.extend(T@o.matrix_world@v.co for v in o.data.vertices)
        fs.extend([start+i for i in p.vertices] for p in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs,all_triangles=False)

angles=list(range(-10,11)); groups=[]; caches=[]
for i,x in enumerate(xs):
    group=[o for o in objects if channel(o)==i and moving(o)]
    assert len(group)==4,(i,[o.name for o in group]);groups.append(group)
    pivot=61 if n==3 and i==1 else 31; side=-1 if i==0 else 1
    cache={}
    for angle in angles:
        T=Matrix.Translation((x,0,pivot))@Matrix.Rotation(math.radians(angle)*side,4,'X')@Matrix.Translation((-x,0,-pivot))
        cache[angle]=tree(group,T)
    caches.append(cache)
fail=[];combos=0
for i in range(n):
    for j in range(i+1,n):
        for a in angles:
            for b in angles:
                combos+=1
                if caches[i][a].overlap(caches[j][b]):fail.append({'moving_channels':[i+1,j+1],'angles':[a,b]})
static_combos=0
for i in range(n):
    for j in range(n):
        if i==j:continue
        fixed=[o for o in objects if channel(o)==j and not moving(o)]
        tf=tree(fixed)
        for angle in angles:
            static_combos+=1
            if caches[i][angle].overlap(tf):fail.append({'moving_channel':i+1,'static_channel':j+1,'angle':angle})
# Separately check moving paddle, including lower fingers, against every printed support.
supports=[o for o in objects if o.get('role')=='print' and not moving(o)]
ts=tree(supports); support_checks=0
for i,x in enumerate(xs):
    group=[o for o in groups[i] if 'paddle ' in o.name]
    pivot=61 if n==3 and i==1 else 31
    side=-1 if i==0 else 1
    for angle in angles:
        T=Matrix.Translation((x,0,pivot))@Matrix.Rotation(math.radians(angle)*side,4,'X')@Matrix.Translation((-x,0,-pivot))
        support_checks+=1
        if tree(group,T).overlap(ts):fail.append({'paddle_support':i+1,'angle':angle})
report={'variant':variant,'method':'Independent world-coordinate BVH surface intersection of whole moving channel (paddle, stock horn, both soft pads), pairwise independent angles; paddle vs every support checked separately','angle_samples_degrees':angles,'independent_channel_angle_combinations':combos,'moving_vs_neighbor_static_checks':static_combos,'paddle_vs_support_checks':support_checks,'collisions':fail,'limitation':'Discrete 1 degree poses, nominal mesh envelopes, no force/deflection verification. Surface intersection does not certify arbitrary solid containment.'}
(out/'independent-motion-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert not fail,fail
