"""Make a review-only Blender print layout. Never exports or overwrites STL files."""
from pathlib import Path
import bpy, math, json, hashlib
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generated'
original_stls={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.stl')}
bpy.ops.wm.open_mainfile(filepath=str(OUT/'servo-command.blend'))
scene=bpy.context.scene;scene.frame_set(1)
names=['PRINT wall chassis','PRINT actuator paddle']
objects=[bpy.data.objects[n] for n in names]
for ob in list(bpy.data.objects):
    if ob not in objects:bpy.data.objects.remove(ob,do_unlink=True)
for col in list(bpy.data.collections):
    if not col.objects:bpy.data.collections.remove(col)
report=[]
for ob,angle,center in zip(objects,[0,-math.pi/2],[(-30,0),(40,0)]):
    # Bake original assembly transform, then put the selected flat face on Z=0.
    world=ob.matrix_world.copy();ob.animation_data_clear()
    ob.data.transform(Matrix.Rotation(angle,4,'Y')@world);ob.matrix_world=Matrix.Identity(4)
    lo=Vector([min(v.co[i] for v in ob.data.vertices) for i in range(3)])
    hi=Vector([max(v.co[i] for v in ob.data.vertices) for i in range(3)])
    shift=Vector((center[0]-(lo.x+hi.x)/2,center[1]-(lo.y+hi.y)/2,-lo.z))
    ob.data.transform(Matrix.Translation(shift));ob.data.update()
    area=sum(p.area for p in ob.data.polygons if all(abs(ob.data.vertices[v].co.z)<.001 for v in p.vertices))
    dim=hi-lo
    assert all(0<d<256 for d in dim)
    assert all(-128<v.co.x<128 and -128<v.co.y<128 and -.001<v.co.z<256 for v in ob.data.vertices)
    ob['review_only']='Print orientation prepared; STL export awaiting user approval'
    ob['orientation']='Flat adhesive back on bed' if angle==0 else 'Outer broad paddle side on bed; raised horn flange needs slicer support review'
    report.append({'part':ob.name,'dimensions_mm':[round(d,2) for d in dim],'bed_contact_area_mm2':round(area,2),'orientation':ob['orientation'],'bottom_z_mm':0})

def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);return m
bedmat=mat('Build plate reference - NOT PRINTED',(.07,.09,.12));ink=mat('Labels - NOT PRINTED',(.75,.83,.86))
refs=bpy.data.collections.new('DISPLAY ONLY - exclude from export');scene.collection.children.link(refs)
def display(ob):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 refs.objects.link(ob);ob['role']='display_only';ob.hide_select=True
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-1.1));bed=bpy.context.object;bed.name='A1 bed reference 256 x 256 mm';bed.dimensions=(256,256,2);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bed.data.materials.append(bedmat);display(bed)
for body,loc,size in [('SERVO MOUNT',(-65,-62,.03),4),('PADDLE',(27,-44,.03),4),('PRINT LAYOUT / REVIEW',(-88,89,.03),6),('Two parts  |  millimetres  |  no STL export yet',(-88,79,.03),3.5)]:
 bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.data.body=body;o.data.size=size;o.data.materials.append(ink);display(o)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.66,.73,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for loc,energy in [((40,-70,210),230000),((-130,50,120),150000)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=150;o.rotation_euler=(Vector((0,0,8))-o.location).to_track_quat('-Z','Y').to_euler();display(o)
bpy.ops.object.camera_add(location=(135,-205,280));cam=bpy.context.object;cam.rotation_euler=(Vector((0,10,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=260;scene.camera=cam;display(cam)
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1500;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
scene.frame_end=1
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'print-layout-review.blend'))
scene.render.filepath=str(OUT/'print-layout-review.png');bpy.ops.render.render(write_still=True)
assert original_stls=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.stl')}
(OUT/'print-layout-review.json').write_text(json.dumps({'status':'Awaiting user approval before STL export','parts':report,'existing_stls_unchanged':True,'stl_sha256':original_stls},indent=2)+'\n')
print(report)
