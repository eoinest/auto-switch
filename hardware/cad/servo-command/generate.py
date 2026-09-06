"""Blender 5.x generator. All coordinates millimetres. See docs/servo-command-mount.md.
Run /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/servo-command/generate.py
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
from mathutils.bvhtree import BVHTree
PURPLE=material('LOLIN purple PCB',(.28,.07,.47)); SILVER=material('USB shell',(.6,.65,.7),.8)
PINK=material('Unknown converter reserved space',(.8,.18,.45))
LABEL=material('Text',(.025,.04,.055))
PRINTS=[]; REFERENCES=[]

def ref(o,confidence):
    o['role']='reference_only';o['source_confidence']=confidence;REFERENCES.append(o);return o

def printable(o,name,rotate=False):
    o['role']='print';PRINTS.append(o);export(o,name,rotate);return o

def label(body,loc,size=3):
    bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.name='LABEL '+body;o.data.body=body;o.data.size=size;o.data.extrude=.01;o.data.materials.append(LABEL);return o

def slot(o,p,length,width,depth,axis='Z'):
    # Straight slot runs along Y; cutter axis Z or X.
    if axis=='X':cut(o,p,(depth,length,width))
    else:cut(o,p,(width,length,depth))
    for d in(-1,1):drill(o,(p[0],p[1]+d*length/2,p[2]),width/2,depth,axis)

def wire(points,mat,name):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=.65;cu.bevel_resolution=2
    s=cu.splines.new('POLY');s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*v,1)
    ob=bpy.data.objects.new(name,cu);scene.collection.objects.link(ob);ob.data.materials.append(mat)

# Two full flat rear landing pads on the face of a single switch plate.
p=C['plate'];m=C['mount'];pw=m['pad_width'];pl=m['pad_length'];px=m['pad_center_x'];back=m['back_z'];th=m['base_thickness']
assert pw>=m['strip_width']+1 and pl>=m['strip_length']+2
assert px-pw/2 > m['bezel_width_assumption']/2
assert px+pw/2 < p['width']/2

def mount_base(thickness):
    elements=[box('left/right strip landing pad',(x,0,back+thickness/2),(pw,pl,thickness)) for x in(-px,px)]
    # Crossbars clear the assumed bezel; no lower skirt blocks strip removal.
    elements += [box('crossbar',(0,y,back+thickness/2),(2*px,8,thickness)) for y in(-40,40)]
    return fuse(elements,'two-pad mounting base',TEAL)
frame=mount_base(th);parts=[frame]
coupon=mount_base(1.2);printable(coupon,'01_plate_and_strip_fit_test');coupon.hide_render=True;coupon.hide_set(True)
# TowerPro reference: shaft points left parallel to wall, actual servo may differ.
s=C['servo'];pivot=C['paddle']['pivot_z'];tip=17;basex=tip+s['base_to_shaft_tip'];by=-s['shaft_offset_y'];earx=basex-s['base_to_ear_under']-s['ear_thickness']/2
body=ref(box('MG90S body',(basex-s['case_height']/2,by,pivot),(s['case_height'],s['case_length'],s['case_width']),GREY),'TowerPro case envelope; front gearbox simplified')
ear=box('MG90S ears',(earx,by,pivot),(s['ear_thickness'],s['ear_span'],s['case_width']),GREY)
for yy in(-1,1):drill(ear,(earx,by+yy*s['ear_hole_pitch']/2,pivot),1.1,8,'X')
ref(ear,'Ear span/source; thickness and hole pitch unmeasured')
shaft=ref(cyl('MG90S shaft',(tip+2.05,0,pivot),2.4,4.1,'X',GOLD),'Spline diameter cosmetic; no printed spline')
supportx=basex-s['base_to_ear_under']+3
parts.append(box('servo foot',(supportx,by,back+2),(10,39,4)))
for yy in(-1,1):
    tower=box('ear tower',(supportx,by+yy*(s['ear_hole_pitch']/2+.5),(back+39)/2),(5,5,39-back))
    slot(tower,(supportx,by+yy*(s['ear_hole_pitch']/2+.5),pivot),1.6,2.2,10,'X');parts.append(tower)
chassis=fuse(parts,'PRINT wall chassis',TEAL);printable(chassis,'02_servo_mount')
# Supplied horn receives printed flange through two adjustable holes. Center screw stays accessible.
h=C['horn'];horn=ref(fuse([box('horn arm',(14,0,pivot),(2,h['arm_span'],h['arm_width'])),cyl('horn hub',(15,0,pivot),h['hub_diameter']/2,4,'X')],'MG90S supplied horn',GOLD),'Illustrative stock horn; verify actual arm and holes')
drill(horn,(14,0,pivot),1.1,10,'X')
yoke=fuse([box('paddle',(0,0,pivot),(8,60,6)),box('offset',(5,0,pivot),(14,12,6)),box('flange',(11,0,pivot),(4,24,14)),*[box('contact foot',(0,y,pivot-9),(8,8,12.2)) for y in(-26,26)]],'PRINT actuator paddle',ORANGE)
drill(yoke,(11,0,pivot),2.4,36,'X')
for yy in(-7,7):slot(yoke,(11,yy,pivot),4,2.2,10,'X')
printable(yoke,'03_factory_horn_paddle',True)
pads=[]
for yy in(-26,26):pads.append(ref(cyl('soft contact pad',(0,yy,pivot-16.2),3.95,2.2,'Z',RED),'3M SJ5302 nominal 7.9 diameter x2.2; add physical pads, not STL'))
for ob in(yoke,horn,*pads):
    old=ob.matrix_world.copy();pt=Vector((0,0,pivot));ob.data.transform(Matrix.Translation(-pt)@old);ob.matrix_world=Matrix.Translation(pt)
    for fr,ang in[(1,0),(25,10),(45,0),(65,-10),(85,0)]:ob.rotation_euler[0]=math.radians(ang);ob.keyframe_insert(data_path='rotation_euler',frame=fr)
plate=ref(box('existing plate',(0,0,3),(p['width'],p['height'],6),WHITE),'Default standard single-gang envelope; actual plate unmeasured')
rocker=ref(box('existing rocker',(0,0,8),(31.5,65,4),WHITE),'Photo proxy; travel and dimensions unmeasured')

bezel=ref(box('rocker bezel - measure yours',(0,0,6.75),(m['bezel_width_assumption'],m['bezel_height_assumption'],1.5),WHITE),'35 x70 assumed bezel; check fit coupon')
stripmat=material('Command interlocking strips - purchased separately',(.88,.88,.83))
strips=[]
for side,x in [('LEFT',-px),('RIGHT',px)]:
    strip=ref(box('Command 17207 '+side+' pair',(x,0,8),(m['strip_width'],m['strip_length'],4),stripmat),'3M nominal outline; mated thickness 4 mm is an assumption, measure actual pair')
    strips.append(strip)
    strip['purchase_quantity']='one mating pair here = two individual strips'
# Reference screw heads, omitted from print exports.
for y in(-48,48):ref(cyl('plate screw reference',(0,y,6.5),3,1,'Z',SILVER),'screw position approximate; never remove plate for this mount')
# Mesh intersection check: paddle must avoid printed chassis at every intended angle.
scene.frame_set(1)
def tree(o):
    return BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get())
# BVH common world coordinates via transformed meshes.
def wt(o):
    me=o.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];fs=[list(p.vertices) for p in me.polygons];t=BVHTree.FromPolygons(vs,fs);o.to_mesh_clear();return t
collisions=[]
for angle in range(-10,11):
    yoke.animation_data_clear();yoke.rotation_euler[0]=math.radians(angle);bpy.context.view_layer.update()
    if wt(yoke).overlap(wt(chassis)):collisions.append(angle)
yoke.rotation_euler[0]=0
for fr,ang in[(1,0),(25,10),(45,0),(65,-10),(85,0)]:yoke.rotation_euler[0]=math.radians(ang);yoke.keyframe_insert(data_path='rotation_euler',frame=fr)
scene.frame_set(1)
servo_body_collisions=len(wt(body).overlap(wt(chassis)))
if servo_body_collisions:raise RuntimeError('Servo body intersects chassis')
if collisions:raise RuntimeError('Paddle/frame collision angles '+str(collisions))

# Additional fit checks on the actual revised mesh, beyond the inherited motion check.
plate_collisions=len(wt(chassis).overlap(wt(plate)))
bezel_collisions=len(wt(chassis).overlap(wt(bezel)))
assert not plate_collisions and not bezel_collisions
report={'status':'fit-test prototype; physical plate, horn and adhesive fit NOT VERIFIED','parts':REPORT,'servo_body_chassis_surface_intersections':servo_body_collisions,'paddle_chassis_mesh_collision_angles':collisions,'sampled_angles_degrees':list(range(-10,11)),'plate_chassis_surface_intersections':plate_collisions,'bezel_chassis_surface_intersections':bezel_collisions,'mount':m,'strip_margin_per_side_mm':(pw-m['strip_width'])/2,'strip_margin_each_end_mm':(pl-m['strip_length'])/2,'caveat':'Dimensions only: no rating for servo peel load. Actual flat plate area, paired-strip thickness, MG90S ears and horn require dry fit.'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
# Organize the isolated actuator; electronics are absent from this file.
for name in ['01 PRINTED PARTS','02 SERVO AND HORN','03 SWITCH REFERENCE','04 COMMAND STRIP PAIRS','05 FIT TEST - hidden']:
    col=bpy.data.collections.new(name);scene.collection.children.link(col)
for ob in list(scene.objects):
    if ob==coupon:dest='05 FIT TEST - hidden'
    elif ob in PRINTS:dest='01 PRINTED PARTS'
    elif ob in strips:dest='04 COMMAND STRIP PAIRS'
    elif ob.name.startswith(('existing','rocker bezel','plate screw')):dest='03 SWITCH REFERENCE'
    else:dest='02 SERVO AND HORN'
    for col in list(ob.users_collection):col.objects.unlink(ob)
    bpy.data.collections[dest].objects.link(ob)
scene.frame_end=85;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
floor=box('studio surface',(0,0,-2),(400,400,2),WHITE)
for loc,power,size in [((50,-40,200),160000,150),((-90,-30,120),90000,100),((0,0,-130),90000,100)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,15))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(120,-160,240));cam=bpy.context.object;cam.rotation_euler=(Vector((4,0,15))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=155;scene.camera=cam
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
bpy.ops.object.select_all(action='DESELECT');chassis.select_set(True);bpy.context.view_layer.objects.active=chassis
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'servo-command.blend'))
scene.render.filepath=str(OUT/'assembly.png');bpy.ops.render.render(write_still=True)
# Rear view with switch removed reveals the two full-length strips on their pads.
for o in bpy.data.collections['03 SWITCH REFERENCE'].objects:o.hide_render=True
floor.hide_render=True
cam.location=(100,-120,-240);cam.rotation_euler=(Vector((0,0,14))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'rear-pads.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
