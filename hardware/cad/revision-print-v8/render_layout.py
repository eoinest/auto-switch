"""Blender view of the exact packed STL parts; never exports references."""
from pathlib import Path
import bpy,json,struct
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'generated'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS'
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);return m
teal=material('Carrier and adapter',(.035,.30,.37));orange=material('Removable retaining parts',(.96,.36,.08));gold=material('Fit shims',(.7,.57,.23));grey=material('A1 bed reference',(.25,.27,.29))
for path in sorted((OUT/'parts').glob('*.stl')):
    d=path.read_bytes();n=struct.unpack_from('<I',d,80)[0];vs=[];fs=[]
    for i in range(n):
        r=struct.unpack_from('<12fH',d,84+50*i);base=len(vs);vs.extend([r[3:6],r[6:9],r[9:12]]);fs.append((base,base+1,base+2))
    mesh=bpy.data.meshes.new(path.stem);mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new(path.stem,mesh);s.collection.objects.link(o)
    mat=gold if 'shim' in path.name.lower() else orange if any(t in path.name.lower() for t in ['bar','finger']) else teal
    o.data.materials.append(mat);o['source_stl']=str(path);o['fit_status']='Booster dimensions provisional'
bpy.ops.mesh.primitive_cube_add(size=1,location=(128,128,-1));bed=bpy.context.object;bed.name='256 mm bed REFERENCE';bed.dimensions=(256,256,2);bed.data.materials.append(grey)
s.world.color=(.7,.7,.7)
for loc in [(100,50,300),(-80,-100,200)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=180000;o.data.size=180;o.rotation_euler=(Vector((125,120,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(128,128,360));cam=bpy.context.object;cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=278;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'all-new-pieces-v8-FIT-TEST.blend'))
s.render.filepath=str(OUT/'all-new-pieces-v8-FIT-TEST.png');bpy.ops.render.render(write_still=True)
