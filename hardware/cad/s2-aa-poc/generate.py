"""Blender 5.x generator. All coordinates millimetres. See docs/s2-aa-mechanical.md.
Run /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python hardware/cad/s2-aa-poc/generate.py
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

# Wallplate fit ring and adhesive wings. Geometry intentionally uses replaceable fit parameters.
p=C['plate'];iw=p['width']+2*p['clearance'];ih=p['height']+2*p['clearance'];wall=3
frame=box('frame',(0,0,4.5),(iw+6,ih+6,9),TEAL);cut(frame,(0,0,4.5),(iw,ih,14))
ring=box('fit ring',(0,0,1),(iw+6,ih+6,2),TEAL);cut(ring,(0,0,1),(iw,ih,5));printable(ring,'01_plate_fit_ring');ring.hide_render=True;ring.hide_set(True)
parts=[frame]
for xx in(-iw/2-11,iw/2+11):parts.append(box('adhesive wing',(xx,0,1.5),(22,82,3)))
# TowerPro reference: shaft points left parallel to wall, actual servo may differ.
s=C['servo'];pivot=C['paddle']['pivot_z'];tip=17;basex=tip+s['base_to_shaft_tip'];by=-s['shaft_offset_y'];earx=basex-s['base_to_ear_under']-s['ear_thickness']/2
body=ref(box('MG90S body',(basex-s['case_height']/2,by,pivot),(s['case_height'],s['case_length'],s['case_width']),GREY),'TowerPro case envelope; front gearbox simplified')
ear=box('MG90S ears',(earx,by,pivot),(s['ear_thickness'],s['ear_span'],s['case_width']),GREY)
for yy in(-1,1):drill(ear,(earx,by+yy*s['ear_hole_pitch']/2,pivot),1.1,8,'X')
ref(ear,'Ear span/source; thickness and hole pitch unmeasured')
shaft=ref(cyl('MG90S shaft',(tip+2.05,0,pivot),2.4,4.1,'X',GOLD),'Spline diameter cosmetic; no printed spline')
supportx=basex-s['base_to_ear_under']+3
parts.append(box('servo foot',((supportx+iw/2)/2,by,8),(abs(supportx-iw/2)+10,39,4)))
for yy in(-1,1):
    tower=box('ear tower',(supportx,by+yy*(s['ear_hole_pitch']/2+.5),23),(5,5,32))
    slot(tower,(supportx,by+yy*(s['ear_hole_pitch']/2+.5),pivot),1.6,2.2,10,'X');parts.append(tower)
chassis=fuse(parts,'PRINT wall chassis',TEAL);printable(chassis,'02_wall_chassis')
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
ref(box('existing plate',(0,0,3),(p['width'],p['height'],6),WHITE),'Default standard single-gang envelope; actual plate unmeasured')
rocker=ref(box('existing rocker',(0,0,8),(31.5,65,4),WHITE),'Photo proxy; travel and dimensions unmeasured')
label('A / WALL ACTUATOR',(-53,-76,1),3.5)
label('Provisional plate fit',(-53,-83,1),2.7)

# Separate electronics carrier, placed beside actuator. Kept off breadboard in this stage.
# Battery has front access and is retained by reusable straps through floor slots.
tx=130;ty=0;tw=100;th=123
tray=box('electronics tray',(tx,ty,2),(tw,th,4),TEAL)
b=C['battery_holder'];bx=tx-8;byb=-22;bz=8
for xx in(-b['width']/2-.7-1.5,b['width']/2+.7+1.5):
    boolean(tray,box('battery side locator',(bx+xx,byb,7),(3,b['height']+1.4,10)),'UNION')
for yy in(-b['height']/2-.7-1.5,b['height']/2+.7+1.5):
    # Low end lips leave the lid and actual switch side accessible; lead notch at both ends.
    lip=box('battery end locator',(bx,byb+yy,5),(b['width']+7.4,3,6));cut(lip,(bx,byb+yy,7),(20,6,7));boolean(tray,lip,'UNION')
for xx in(-22,22):
    boolean(tray,box('battery raised saddle',(bx+xx,byb,6),(7,b['height'],4)),'UNION')
    for yy in(-b['height']/2-4,b['height']/2+4):slot(tray,(bx+xx,byb+yy,2),2,4,8)
# Holder cosmetic seam and switch; switch position is illustrative, full top remains accessible.
ref(box('DAIERTEK 4AA case',(bx,byb,bz+b['depth']/2),(b['width'],b['height'],b['depth']),BLACK),'Seller envelope 68.7 x64.2 x22.5; tolerances/switch exact location unverified')
ref(box('battery lid',(bx,byb,bz+b['depth']-.7),(b['width']-1,b['height']-1,1.4),GREY),'Cosmetic seam inside envelope')
ref(box('holder switch visual',(bx+22,byb-22,bz+b['depth']+.8),(10,5,1.6),BLACK),'Illustrative only; keep face accessible')
# S2 outline corners, open underside center and header clearance. No invented PCB screw holes.
sx=tx-24;sy=37;sz=24;sw=C['s2_mini']['width'];sh=C['s2_mini']['height']
for xx in(-sw/2+2,sw/2-2):
    for yy in(-sh/2+3,sh/2-3):boolean(tray,box('S2 corner rest',(sx+xx,sy+yy,(sz+4)/2),(3,4,sz-4)),'UNION')
# Universal strap slots beyond board perimeter; no clip touches unknown components.
for xx in(-sw/2-4,sw/2+4):slot(tray,(sx+xx,sy,2),14,3,8)
ref(box('LOLIN S2 mini PCB',(sx,sy,sz+.8),(sw,sh,1.6),PURPLE),'Official board outline; thickness provisional 1.6')
ref(box('S2 USB C',(sx,sy-sh/2+2.5,sz+3.4),(9,7,3.2),SILVER),'Cosmetic reference; USB component and plug exact envelope unmeasured')
ref(box('ESP32 S2 package',(sx,sy+1,sz+2.6),(7,7,2),BLACK),'Cosmetic simplified chip')
# Typical four 8-pin header rows, actual soldered combination unknown; ensure floor clearance.
for xx in(-11.43,-8.89,8.89,11.43):
    for k in range(8):ref(cyl('header reference',(sx+xx,sy-8.89+k*2.54,sz-3),.32,6,'Z',GOLD),'2.54 mm pitch reference; inspect actual pins before printing')
ref(box('antenna clearance marker',(sx,sy+sh/2-3,sz+2),(12,5,1),GOLD),'Illustrative antenna; keep battery and metal away from this edge')
# Generic reserved converter bay: do not fabricate an exact TPS63070 module model.
cx=tx+23;cy=37;cw=C['converter']['bay_width'];ch=C['converter']['bay_height']
for xx in(-cw/2,cw/2):
    boolean(tray,box('converter bay support',(cx+xx,cy,5),(3,ch,6)),'UNION')
    slot(tray,(cx+xx,cy,2),22,2,8)
# Wireframe dimension volume avoids presenting unknown geometry as the real board.
reserve=box('TPS63070 RESERVED BAY - not component dimensions',(cx,cy,13),(cw,ch,18),PINK)
wiremod=reserve.modifiers.new('Unknown outline wireframe','WIREFRAME');wiremod.thickness=.5
ref(reserve,'40 x36 x18 reserved space ONLY; module dimensions missing')
label('TPS63070\nFIT PENDING',(cx-15,cy-4,24),2.5)
# Independent adhesive landing pads on tray back; frame does not carry battery mass.
for xx in(-35,35):
    for yy in(-50,50):
        # Through slots can retain reusable straps or accept independent mounting ties.
        slot(tray,(tx+xx,yy,2),5,3,8)
printable(tray,'04_electronics_carrier')
label('B / ELECTRONICS CARRIER',(tx-50,-77,1),3.2)
label('Breadboard stays on bench for first POC',(tx-50,-84,1),2.4)
# Wiring is illustrative route clearance, electrical authority is new wiring diagram.
wr=material('Wire red',(.7,.02,.02));wb=material('Wire brown',(.08,.025,.012));wy=material('Wire orange',(.9,.35,.01))
wire([(basex-2,-18,pivot),(65,-27,30),(80,-20,26),(cx,-2,18),(cx,22,18)],wr,'servo 5V route')
wire([(basex-3,-18,pivot-2),(65,-30,28),(80,-24,24),(cx+3,-2,16),(cx+3,22,16)],wb,'servo ground route')
wire([(basex-4,-18,pivot+2),(63,-24,32),(78,-17,28),(sx-4,20,23)],wy,'servo signal route')

# Coupons let each unknown fit be checked with small prints.
# Battery perimeter ring tests outer case with nominal 0.7mm clearance per side.
cb=box('battery fit coupon',(0,0,1),(b['width']+7.4,b['height']+7.4,2),TEAL);cut(cb,(0,0,1),(b['width']+1.4,b['height']+1.4,5));printable(cb,'05_battery_fit_ring');cb.hide_render=True;cb.hide_set(True)
cs=box('S2 fit coupon',(0,0,1),(sw+7.4,sh+7.4,2),TEAL);cut(cs,(0,0,1),(sw+1.4,sh+1.4,5));printable(cs,'06_s2_outline_coupon');cs.hide_render=True;cs.hide_set(True)
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
report={'status':'prototype; physical fit NOT VERIFIED','parts':REPORT,'servo_body_chassis_surface_intersections':servo_body_collisions,'paddle_chassis_mesh_collision_angles':collisions,'sampled_angles_degrees':list(range(-10,11)),'contact_note':'Contact with unmeasured rocker is intentional and not a validated travel limit. Calibrate on actual switch.','component_fit':{'battery_clearance_per_side_mm':.7,'s2_outline_clearance_coupon_per_side_mm':.7,'converter':'NO EXACT MODEL: bay40x36x18, awaiting module dimension','breadboard':'Bench only; unknown model'},'sources':{'S2':'https://www.wemos.cc/en/latest/_static/files/dim_s2_mini_v1.0.0.pdf','holder':'https://www.amazon.com/dp/B09N1GDWQ9','servo':'https://towerpro.com.tw/product/mg90s-3/','converter':'https://www.amazon.com/dp/B0GCW44FDL'}}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
# Presentation scene.
scene.frame_end=85;scene.render.engine='CYCLES';scene.cycles.samples=32
scene.world.color=(.6,.6,.6)
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
floor=box('presentation surface',(60,0,-2),(430,250,2),WHITE)
for loc,power,size in[((60,-20,220),1800,180),((-100,-50,130),1100,100)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power*100;o.data.shape='DISK';o.data.size=size
bpy.ops.object.camera_add(location=(210,-255,330));cam=bpy.context.object;cam.rotation_euler=(Vector((60,0,9))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=285;scene.camera=cam
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');yoke.select_set(True);bpy.context.view_layer.objects.active=yoke
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'s2-aa-prototype.blend'))
scene.render.filepath=str(OUT/'assembly-preview.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
