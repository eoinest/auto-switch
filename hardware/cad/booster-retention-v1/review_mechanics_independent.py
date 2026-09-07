"""Independent booster fit-test geometry review; no CAD save."""
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

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'generated/booster-retention-v1-assembly-FIT-TEST.blend'))
obs=list(bpy.context.scene.objects)
adapter=next(o for o in obs if o.name.startswith('01_adapter'))
fingers=[o for o in obs if o.name.startswith(('02_lower','03_upper'))]
shims=[o for o in obs if o.name.startswith(('04_lower','05_upper'))]
carrier=next(o for o in obs if o.name.startswith('Existing carrier surface'))
pcb=next(o for o in obs if o.name.startswith('PCB '))
components=[o for o in obs if o.get('role','').startswith('REFERENCE ONLY') and o != pcb]
checks=[]
for printed in [adapter,*fingers,*shims]:
    for component in components:
        checks.append({'part':printed.name,'reference':component.name,'intersection_mm3':volume(printed,component)})
# Isolate intended planar board and carrier bearing contacts from numeric noise.
for printed in [adapter,*fingers]:
    delta=-.001 if printed==adapter else .001
    printed.location.z+=delta;bpy.context.view_layer.update()
    checks.append({'part':printed.name,'reference':pcb.name,'intersection_mm3':volume(printed,pcb)})
    printed.location.z-=delta;bpy.context.view_layer.update()
for f in fingers:
    f.location.z+=.001;bpy.context.view_layer.update();checks.append({'part':f.name,'reference':adapter.name,'intersection_mm3':volume(f,adapter)});f.location.z-=.001;bpy.context.view_layer.update()
sections=[]
for sign in [-1,1]:
    f=next(o for o in fingers if (o.location.y>0)==(sign>0))
    shim=next(o for o in shims if (o.location.y>0)==(sign>0))
    shelf=ray(adapter,(0,sign*14.7,7),(0,0,-1))[2]
    toe=ray(f,(0,sign*14.7,6.6),(0,0,1))[2]
    stop=ray(adapter,(0,sign*15.8,10),(0,0,-1))[2]
    seat=ray(adapter,(2.2,sign*23,10),(0,0,-1))[2]
    shimlow=ray(shim,(2.2,sign*23,6),(0,0,1))[2];shimhigh=ray(shim,(2.2,sign*23,10),(0,0,-1))[2]
    key=ray(adapter,(0,sign*23,8),(1,0,0))[0]
    guide=ray(adapter,(0,sign*7,6.7),(1,0,0))[0]
    sections.append({'end':sign,'direct_support_top_z_mm':shelf,'finger_underside_z_mm':toe,'end_stop_top_z_mm':stop,'hard_seat_z_mm':seat,'shim_z_mm':[shimlow,shimhigh],'key_inner_x_mm':key,'side_guide_inner_x_mm':guide})
    shaft=cylinder((0,sign*23,2),1.5,22)
    for obj in [adapter,carrier,f,shim]:checks.append({'part':'M3 shaft','reference':obj.name,'intersection_mm3':volume(shaft,obj)})
    bpy.data.objects.remove(shaft,do_unlink=True)
    # Finger can lower to its hard seat when shim is removed, without hitting fixed stops.
    f.location.z-=.399;bpy.context.view_layer.update();checks.append({'part':f.name+' without shim','reference':adapter.name,'intersection_mm3':volume(f,adapter)});f.location.z+=.399;bpy.context.view_layer.update()
STL=ROOT/'generated/stl-fit-test';stls=[stl_audit(p) for p in sorted(STL.glob('*.stl'))]
assert len(stls)==5,stls
assert all(c['intersection_mm3']<.001 for c in checks),[c for c in checks if c['intersection_mm3']>=.001]
for s in sections:
    assert abs(s['direct_support_top_z_mm']-6.5)<.001 and abs(s['finger_underside_z_mm']-7.7)<.001,s
    assert abs(s['hard_seat_z_mm']-7.3)<.001 and abs(s['shim_z_mm'][1]-s['shim_z_mm'][0]-.4)<.001,s
    assert s['end_stop_top_z_mm']<7.3 and abs(s['key_inner_x_mm']-4.3)<.001 and abs(s['side_guide_inner_x_mm']-8.2)<.001,s
assert all(abs(s['bounds_mm'][0][2])<.001 and s['suspended_downward_area_mm2']<.001 for s in stls),stls
report={'status':'PASS only for assumed 16x30x1.2 mm reference board','intersection_checks':checks,'saved_mesh_sections':sections,'print_orientations':stls,'mounting_hole_pitch_mm':46,'M3x16_stack':{'underhead_z_mm':9.7,'tip_z_mm':-6.3,'nut_bottom_z_mm':-2.4,'tip_projection_mm':3.9,'wall_pad_front_z_mm':-10,'tip_to_pad_front_mm':3.7},'limits':['No measured PCB thickness or underside geometry.','Terminal pads and components are approximate photo references.','Board capture is nominal, not physically fit approved.','Coincident contact faces offset by 0.001 mm for intersection checks.']}
(ROOT/'generated/independent-mechanical-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
