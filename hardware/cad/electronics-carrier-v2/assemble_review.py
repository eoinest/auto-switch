"""Combine approved actuator geometry and electronics v2 without rewriting either source."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generated'
ACT=ROOT.parent/'servo-command'/'generated'
# Verify the actuator export bytes are still the approved bytes.
manifest=json.loads((ACT/'approved-export.json').read_text())
for filename, expected in manifest['stl_sha256'].items():
    assert hashlib.sha256((ACT/filename).read_bytes()).hexdigest()==expected, filename
bpy.ops.wm.open_mainfile(filepath=str(ACT/'servo-command.blend'))
scene=bpy.context.scene
scene.frame_set(1)
# Exclude original presentation objects only; preserve actuator geometry/transforms.
for o in list(scene.objects):
    if o.type in {'CAMERA','LIGHT','FONT'} or o.name=='presentation surface':
        bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(OUT/'electronics-carrier-v2.blend'),link=False) as (source,target):
    assert 'ELECTRONICS_V2_ASSEMBLY' in source.collections
    target.collections=['ELECTRONICS_V2_ASSEMBLY']
collection=target.collections[0]
scene.collection.children.link(collection)
for o in collection.all_objects:
    if o.parent is None:o.location.x+=140
# Labels explicitly separate approved actuator export from fit-pending electronics.
for body,loc in [('APPROVED ACTUATOR GEOMETRY',(-40,-89,0)),('ELECTRONICS V2 / FIT PENDING',(80,-89,0))]:
    bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.data.body=body;o.data.size=3
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.86,.9,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
for loc in [(20,-90,230),(200,80,180)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=200000;o.data.size=200
bpy.ops.object.camera_add(location=(255,-290,360));cam=bpy.context.object
cam.rotation_euler=(Vector((80,-5,12))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=330;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='MATERIAL'
scene['review_status']='Electronics physical fit pending; actuator geometry matches approved exports'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'full-assembly-review.blend'))
scene.render.filepath=str(OUT/'full-assembly-review.png')
bpy.ops.render.render(write_still=True)
