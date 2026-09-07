"""Independent checks of final saved assembly and exported bar. Does not save CAD."""
import bpy,bmesh,json,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'generated/battery-retention-v6-assembly-PREVIEW.blend'))
obs=list(bpy.context.scene.objects)
bar=next(o for o in obs if o.name.startswith('V6 SINGLE'))
carrier=next(o for o in obs if o.name.startswith('EXISTING V4'))
holder=next(o for o in obs if o.name.startswith('AA body'))
finger=next(o for o in obs if o.name.startswith('Switch finger'))
wire=next(o for o in obs if o.name.startswith('Illustrative wire corridor'))
def volume(a,b):
    d=a.copy();d.data=a.data.copy();bpy.context.scene.collection.objects.link(d);bpy.context.view_layer.objects.active=d
    m=d.modifiers.new('independent intersection','BOOLEAN');m.operation='INTERSECT';m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name)
    bm=bmesh.new();bm.from_mesh(d.data);v=abs(bm.calc_volume(signed=True));bm.free();bpy.data.objects.remove(d,do_unlink=True);return v

def ray(o,start,direction):
    tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
    p=tree.ray_cast(Vector(start),Vector(direction))[0];assert p is not None,(o.name,start);return list(p)
checks=[]
for other in [carrier,holder,finger,wire]:
    bar.location.z+=.001;bpy.context.view_layer.update()
    checks.append({'other':other.name,'intersection_mm3':volume(bar,other)})
    bar.location.z-=.001;bpy.context.view_layer.update()
seats=[]
for x in [-43,43]:
    # Offset from the center hole samples solid bearing surfaces.
    q=x+2.4
    top=ray(carrier,(q,-12,40),(0,0,-1))[2]
    underside=ray(bar,(q,-12,15),(0,0,1))[2]
    front=ray(bar,(q,-12,40),(0,0,-1))[2]
    seats.append({'x_mm':x,'post_top_z_mm':top,'bar_seat_z_mm':underside,'bar_front_z_mm':front})
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.5,depth=40,location=(x,-12,15));probe=bpy.context.object
    for other in [bar,carrier]:checks.append({'other':other.name,'probe':'M3 mounting shaft','x_mm':x,'intersection_mm3':volume(probe,other)})
    bpy.data.objects.remove(probe,do_unlink=True)
land=ray(bar,(0,-12,15),(0,0,1))[2]
case_top=ray(holder,(0,-12,40),(0,0,-1))[2]
p=ROOT/'generated/battery-retention-v6-SINGLE-CROSSBAR-PREVIEW.stl'
data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*n
verts=[];suspended_down_area=0;bed_area=0
for i in range(n):
    q=struct.unpack_from('<12fH',data,84+50*i);a,b,c=[Vector(q[j:j+3]) for j in (3,6,9)];verts.extend([a,b,c]);cross=(b-a).cross(c-a)
    if cross.normalized().z < -0.01:
        if max(a.z,b.z,c.z)<.001:bed_area+=cross.length/2
        else:suspended_down_area+=cross.length/2
bounds=[[min(v[k] for v in verts) for k in range(3)],[max(v[k] for v in verts) for k in range(3)]]
assert all(c['intersection_mm3']<.001 for c in checks),checks
assert all(abs(s['post_top_z_mm']-26)<.001 and abs(s['bar_seat_z_mm']-26)<.001 and abs(s['bar_front_z_mm']-29)<.001 for s in seats),seats
assert abs(land-22.2)<.001 and abs(case_top-22)<.001,(land,case_top)
assert abs(bounds[0][2])<.001 and suspended_down_area<.001,(bounds,suspended_down_area)
report={'status':'PASS nominal single-crossbar geometry','checks':checks,'mounting_seats':seats,'land_bottom_z_mm':land,'nominal_case_top_z_mm':case_top,'nominal_vertical_clearance_mm':land-case_top,'stl_bounds_mm':bounds,'flat_bed_contact_area_mm2':bed_area,'suspended_downward_facing_area_mm2':suspended_down_area,'limits':['Bearing contact separated by 0.001 mm for Boolean checks.','Seller nominal case dimensions, not physical measurement.','Existing lateral clearance remains; optional shims can address it.','No physical load or print-fit test.']}
(ROOT/'generated/independent-mechanical-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
