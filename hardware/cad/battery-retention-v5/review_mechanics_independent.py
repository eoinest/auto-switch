"""Independent saved-mesh and fastener-range review. No CAD mutation is saved."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'generated/battery-retention-v5-assembly.blend'))
obs=list(bpy.context.scene.objects)
carrier=next(o for o in obs if o.name.startswith('EXISTING V4'))
rails=[o for o in obs if 'fixed battery edge rail' in o.name]
shoes=[o for o in obs if 'captured pressure shoe' in o.name]
finger=next(o for o in obs if o.name.startswith('FINGER ACCESS'))
wire=next(o for o in obs if o.name.startswith('WIRE ROUTE'))
nuts=[o for o in obs if o.name.startswith('NEW M3 adjustment nut')]
bolts=[o for o in obs if o.name.startswith('NEW M3x10 adjustment screw')]
def xcenter(o):return sum((o.matrix_world@v.co).x for v in o.data.vertices)/len(o.data.vertices)
def match(items,side):return next(o for o in items if (xcenter(o)>0)==(side>0))
def volume(a,b):
    dupe=a.copy();dupe.data=a.data.copy();bpy.context.scene.collection.objects.link(dupe);bpy.context.view_layer.objects.active=dupe
    mod=dupe.modifiers.new('independent overlap','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(dupe.data);v=abs(bm.calc_volume(signed=True));bm.free();bpy.data.objects.remove(dupe,do_unlink=True);return v

def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def material_segment(o,point,direction):
    t=tree(o);d=Vector(direction);a=t.ray_cast(Vector(point),d)[0]
    assert a is not None,(o.name,point)
    b=t.ray_cast(a+d*.001,d)[0];assert b is not None,(o.name,point,a)
    return list(a),list(b),(b-a).length

checks=[];ranges=[];measurements=[]
for side in [-1,1]:
    rail=match(rails,side);shoe=match(shoes,side);nut=match(nuts,side);bolt=match(bolts,side)
    for fixed in [carrier,finger,wire]:
        # Separate deliberately coplanar post/rail contact by one micrometre.
        rail.location.z+=.001;bpy.context.view_layer.update()
        overlap=volume(rail,fixed);rail.location.z-=.001;bpy.context.view_layer.update()
        checks.append({'part':rail.name,'other':fixed.name,'volume_mm3':overlap})
    nut.location.z-=.001;bpy.context.view_layer.update()
    checks.append({'part':nut.name,'other':rail.name,'volume_mm3':volume(nut,rail)})
    nut.location.z+=.001;bpy.context.view_layer.update()
    for y in [-52,-12]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.5,depth=40,location=(side*43,y,15));probe=bpy.context.object
        checks.append({'part':'M3 mounting shaft probe','other':rail.name,'volume_mm3':volume(probe,rail)})
        checks.append({'part':'M3 mounting shaft probe','other':carrier.name,'volume_mm3':volume(probe,carrier)})
        bpy.data.objects.remove(probe,do_unlink=True)
    measurements.append({'side':side,'adjuster_roof':material_segment(rail,(side*34.2,-32,25),(0,0,1)),
                         'mounting_bearing_stack':material_segment(rail,(side*45.4,-52,20),(0,0,1)),
                         'shoe_cup_floor':material_segment(shoe,(side*32,-32,20),(0,0,1))})
    for case_height in [18.5,19,20.5]:
        dz=case_height-19
        shoe.location.z+=dz;bolt.location.z+=dz+.001;bpy.context.view_layer.update()
        for a,b in [(shoe,rail),(shoe,finger),(shoe,wire),(bolt,rail),(bolt,shoe)]:
            checks.append({'case_height_mm':case_height,'part':a.name,'other':b.name,'volume_mm3':volume(a,b)})
        tip=case_height+3+1.2;head=tip+10
        ranges.append({'side':side,'body_height_mm':case_height,'head_under_z_mm':head,'tip_z_mm':tip,'tip_projection_below_nut_mm':26.6-tip,'head_clearance_above_rail_mm':head-31})
        shoe.location.z-=dz;bolt.location.z-=dz+.001;bpy.context.view_layer.update()

shim_checks=[]
for o in obs:
    if o.get('role')=='reference_only' and o.name.startswith('cradle shim'):
        o.location.z+=.001;bpy.context.view_layer.update();shim_checks.append({'name':o.name,'carrier_intersection_mm3':volume(o,carrier)});o.location.z-=.001
report={'status':'PASS for nominal mechanical geometry and stated screw range','intersection_checks':checks,'measured_sections':measurements,'adjuster_range':ranges,'illustrative_shim_checks':shim_checks,'limitations':['Coplanar contacts separated by1 micrometre for Boolean audit','No force, creep or physical fit test','Cable exit height unmeasured','Pressure shoes remain axially removable when screw tips disengage from cups']}
assert all(c['volume_mm3']<.01 for c in checks),[c for c in checks if c['volume_mm3']>=.01]
assert all(c['carrier_intersection_mm3']<.01 for c in shim_checks),shim_checks
for m in measurements:
    assert abs(m['adjuster_roof'][2]-2)<.001,m
    assert abs(m['mounting_bearing_stack'][2]-3)<.001,m
    assert abs(m['shoe_cup_floor'][2]-1.2)<.001,m
assert all(r['tip_projection_below_nut_mm']>=1.8 and r['head_clearance_above_rail_mm']>=1.6 for r in ranges)
(ROOT/'generated/independent-mechanical-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
