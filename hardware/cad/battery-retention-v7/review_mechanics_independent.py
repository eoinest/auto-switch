"""Independent saved-mesh V7 carrier and flat bar verification; no CAD save."""
import bpy,bmesh,json,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent

def volume(a,b,operation='INTERSECT'):
    d=a.copy();d.data=a.data.copy();bpy.context.scene.collection.objects.link(d);bpy.context.view_layer.objects.active=d
    m=d.modifiers.new('independent audit','BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name)
    bm=bmesh.new();bm.from_mesh(d.data);v=abs(bm.calc_volume(signed=True));bm.free();bpy.data.objects.remove(d,do_unlink=True);return v

def ray(o,start,direction):
    tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
    p=tree.ray_cast(Vector(start),Vector(direction))[0];assert p is not None,(o.name,start);return list(p)

def box(location,dimensions):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o

def cylinder(location,radius,depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=location);return bpy.context.object

def stl_audit(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n
    verts=[];suspended=0;bed=0
    for i in range(n):
        q=struct.unpack_from('<12fH',raw,84+50*i);a,b,c=[Vector(q[j:j+3]) for j in [3,6,9]];verts.extend([a,b,c]);cross=(b-a).cross(c-a)
        if cross.normalized().z<-.01:
            if max(a.z,b.z,c.z)<.001:bed+=cross.length/2
            else:suspended+=cross.length/2
    bounds=[[min(v[k] for v in verts) for k in range(3)],[max(v[k] for v in verts) for k in range(3)]]
    return {'file':path.name,'bounds_mm':bounds,'flat_bed_contact_mm2':bed,'suspended_downward_area_mm2':suspended}

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'generated/battery-retention-v7-assembly.blend'))
obs=list(bpy.context.scene.objects)
carrier=next(o for o in obs if o.name.startswith('V7 NEW CARRIER'))
bar=next(o for o in obs if o.name.startswith('V7 FLAT'))
holder=next(o for o in obs if o.name.startswith('AA case body'))
base_sections=[{'xy_mm':[x,y],'bottom_z_mm':ray(carrier,(x,y,-10),(0,0,1))[2],'top_z_mm':ray(carrier,(x,y,40),(0,0,-1))[2]} for x,y in [(0,-72),(-55,-40),(55,-40)]]
assert all(abs(s['bottom_z_mm'])<.001 and abs(s['top_z_mm']-3)<.001 for s in base_sections),base_sections
old_checks=[]
for x in [-43,43]:
    for y in [-52,-12]:
        # The old footprint overlaps the preserved cradle wall by 0.05 mm; exclude that wall.
        probe=box((x,y,15.0005),(9.89,12,23.999));v=volume(carrier,probe);bpy.data.objects.remove(probe,do_unlink=True)
        hole=cylinder((x,y,1.5),1.5,2.998);missing=volume(hole,carrier,'DIFFERENCE');bpy.data.objects.remove(hole,do_unlink=True)
        old_checks.append({'center_xy_mm':[x,y],'old_post_remaining_above_z3_mm3':v,'unfilled_old_hole_mm3':missing})
seats=[];shaft_checks=[]
for x in [-43,43]:
    seats.append({'x_mm':x,'y_mm':-32,'post_top_z_mm':ray(carrier,(x+2.4,-32,40),(0,0,-1))[2],'bar_bottom_z_mm':ray(bar,(x+2.4,-32,15),(0,0,1))[2],'bar_top_z_mm':ray(bar,(x+2.4,-32,40),(0,0,-1))[2]})
    p=cylinder((x,-32,12),1.5,35)
    for o in [bar,carrier]:shaft_checks.append({'x_mm':x,'other':o.name,'intersection_mm3':volume(p,o)})
    bpy.data.objects.remove(p,do_unlink=True)
# Test constant underside across center and both end sections.
underside=[{'x_mm':x,'z_mm':ray(bar,(x,-32,15),(0,0,1))[2]} for x in [-46,-35,-20,0,20,35,46]]
case_top=ray(holder,(0,-32,40),(0,0,-1))[2]
bar.location.z+=.001;bpy.context.view_layer.update()
intersections=[{'other':o.name,'volume_mm3':volume(bar,o)} for o in [carrier,holder]]
# Photo-derived access envelopes, matching preceding nominal holder orientation.
for name,loc,size in [('finger',(28.88,-53.44,31),(18,22,18)),('wire',(43,-2,17),(21,5,10))]:
    p=box(loc,size);intersections.append({'other':name,'volume_mm3':volume(bar,p)});bpy.data.objects.remove(p,do_unlink=True)
bar.location.z-=.001;bpy.context.view_layer.update()
# Compare the saved V4 carrier outside the two allowed battery-post strips.
config=json.loads((ROOT/'config.json').read_text())
with bpy.data.libraries.load(str(ROOT/config['source_carrier']),link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n.startswith('01 carrier base') and 'bed' not in n]
old=dst.objects[0];bpy.context.scene.collection.objects.link(old);bpy.context.view_layer.update()
def unchanged_outside_post_strips(a,b):
    d=a.copy();d.data=a.data.copy();bpy.context.scene.collection.objects.link(d);bpy.context.view_layer.objects.active=d
    m=d.modifiers.new('difference','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=b;bpy.ops.object.modifier_apply(modifier=m.name)
    for x in [-43,43]:
        mask=box((x,-32,15),(10.2,56,50));bpy.context.view_layer.objects.active=d
        m=d.modifiers.new('exclude allowed post changes','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=mask;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(mask,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(d.data);v=abs(bm.calc_volume(signed=True));bm.free();bpy.data.objects.remove(d,do_unlink=True);return v
preservation={'new_minus_original_outside_post_strips_mm3':unchanged_outside_post_strips(carrier,old),'original_minus_new_outside_post_strips_mm3':unchanged_outside_post_strips(old,carrier)}
assert max(preservation.values())<.01,preservation
files=['01_NEW-CARRIER-v7.stl','02_FLAT-CROSSBAR-v7.stl','battery-retention-v7-NEW-CARRIER-AND-BAR.stl']
stls=[stl_audit(ROOT/'generated'/f) for f in files]
assert all(c['old_post_remaining_above_z3_mm3']<.001 and c['unfilled_old_hole_mm3']<.001 for c in old_checks),old_checks
assert all(abs(s['post_top_z_mm']-22)<.001 and abs(s['bar_bottom_z_mm']-22)<.001 and abs(s['bar_top_z_mm']-25)<.001 for s in seats),seats
assert all(abs(s['z_mm']-22)<.001 for s in underside),underside
assert abs(case_top-22)<.001,case_top
assert all(c['intersection_mm3']<.001 for c in shaft_checks),shaft_checks
assert all(c['volume_mm3']<.001 for c in intersections),intersections
assert all(abs(s['bounds_mm'][0][2])<.001 and s['suspended_downward_area_mm2']<.001 for s in stls),stls
report={'status':'PASS nominal V7 centered two-post carrier and flat bar','non_battery_geometry_preservation':preservation,'actual_base_sections':base_sections,'removed_old_posts_and_filled_holes':old_checks,'centered_mounting_seats':seats,'mounting_shafts':shaft_checks,'bar_underside_samples':underside,'nominal_case_top_z_mm':case_top,'designed_vertical_gap_mm':underside[3]['z_mm']-case_top,'bar_intersections':intersections,'stl_print_orientation':stls,'M3x30_stack':{'head_bearing_z_mm':25,'tip_z_mm':-5,'ordinary_nut_bottom_z_mm':-2.4,'tip_projection_below_nut_mm':2.6,'existing_wall_pad_front_z_mm':-10,'tip_to_pad_front_clearance_mm':5},'limits':['Nominal seller 19 mm body, physical fit untested.','No designed vertical clearance; do not force an oversized case or compensate by overtightening.','Other component attachment fit not revalidated.','Coincident bearing contact separated by 0.001 mm for Boolean checks.']}
(ROOT/'generated/independent-mechanical-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
