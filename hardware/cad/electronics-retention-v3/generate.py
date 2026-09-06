"""Inspectable retention concept; no release STL exports. Units mm.
blender --background --python hardware/cad/electronics-retention-v3/generate.py
"""
import sys, math, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from cadlib import *

assembly=bpy.data.collections.new('V3 ASSEMBLED — FIT UNVERIFIED')
scene.collection.children.link(assembly)
def collect(o,kind='PRINTED',explosion=0):
    for col in list(o.users_collection): col.objects.unlink(o)
    assembly.objects.link(o)
    o['part_type']=kind; o['explode_z_mm']=explosion
    return o
def part(o,explosion=0):return collect(o,'PRINTED CONCEPT',explosion)
def reference(o,explosion=0):return collect(o,'REFERENCE — NOT PRINTABLE',explosion)
def slot(o,x0,x1,y,z,r,depth):
    cut(o,((x0+x1)/2,y,z),(x1-x0,2*r,depth))
    drill(o,(x0,y,z),r,depth);drill(o,(x1,y,z),r,depth)
def hexnut(name,x,y,z,across,thickness,bore):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=across/math.sqrt(3),depth=thickness,location=(x,y,z))
    o=bpy.context.object;o.name=name;o.data.materials.append(GREY)
    drill(o,(x,y,z),bore/2,thickness+2)
    return reference(o,-9)
def bolt(name,x,y,head_z,diameter,length):
    o=fuse([cyl('shaft',(x,y,head_z-length/2),diameter/2,length),cyl('head',(x,y,head_z+diameter*.3),diameter*.85,diameter*.6)],name,GREY)
    return reference(o,40)

base=part(box('01 carrier base • 120 x 160 x 3',(0,0,1.5),(120,160,3),TEAL))
for x in [-54,54]:
    for y in [-73,73]:
        base=boolean(base,box('underside foot',(x,y,-3.5),(10,10,7),TEAL),'UNION')

# Battery sits on the base, supported by four walls and two rigid removable bars.
bx,by=0,-32
iw,ih=C['holder_cradle_inner_mm']
for x in [-(iw/2+1.5),iw/2+1.5]:
    base=boolean(base,box('battery x wall',(x,by,7),(3,ih+6,8),TEAL),'UNION')
for y in [by-(ih/2+1.5),by+(ih/2+1.5)]:
    base=boolean(base,box('battery y wall',(0,y,7),(iw,3,8),TEAL),'UNION')
# Wire exit in near wall; both back switch and cover are serviced by removing bars and lifting out.
cut(base,(0,by-ih/2-1.5,8),(14,5,8))
bar_bottom=3+C['holder_nominal_mm'][2]+C['holder_top_gap_mm']
for row,y in enumerate([by-20,by+20]):
    for x in [-43,43]:
        base=boolean(base,box('battery bar hard stop',(x,y,(3+bar_bottom)/2),(10,12,bar_bottom-3),TEAL),'UNION')
        drill(base,(x,y,15),1.7,40)
    bar=part(box('02 battery removable bar '+str(row+1),(0,y,bar_bottom+1.5),(96,10,3),ORANGE),30)
    for x in [-43,43]:
        drill(bar,(x,y,bar_bottom+1.5),1.7,8)
        bolt('M3 x 35 battery bolt',x,y,bar_bottom+3,3,35)
        hexnut('M3 nut — accessible underside',x,y,-1.2,5.5,2.4,3)
holder=reference(box('AA holder nominal envelope • verify actual body',(0,by,14.25),tuple(C['holder_nominal_mm']),BLACK),15)
# Reference shell lines make the service orientation legible without claiming internal cell geometry.
reference(box('holder rear service cover • lift holder out',(0,by,3.3),(59,55,.6),GREY),15)

# S2: factory two-hole retention, insulating supports underneath USB end, no extra metal over antenna.
sx,sy=-30,47
pcb_z=10.8; hole_y=sy-34.3/2+3.3
board=reference(box('S2 Mini PCB reference • 25.4 x 34.3',(sx,sy,pcb_z),(25.4,34.3,1.6),GREEN),18)
for x in [sx-10.2,sx+10.2]:
    drill(board,(x,hole_y,pcb_z),1,5)
    base=boolean(base,cyl('S2 insulating standoff',(x,hole_y,6.5),2,7,mat=TEAL),'UNION')
    drill(base,(x,hole_y,6),.9,22)
    bolt('M1.6 x 16 S2 bolt',x,hole_y,11.6,1.6,16)
    hexnut('M1.6 nut — accessible underside',x,hole_y,-.65,3.2,1.3,1.6)
for x in [sx-11.5,sx+11.5]:
    # Edge-only supports bear USB insertion load; actual underside solder pads must be checked.
    base=boolean(base,box('S2 USB-end edge support',(x,sy+14,6.5),(2.4,3,7),TEAL),'UNION')
reference(box('S2 USB-C reference envelope',(sx,sy+15,13.1),(9,7,3),GREY),18)
reference(box('S2 antenna region • keep clear',(sx,sy-13,11.75),(14,8,.3),GOLD),18)
reference(box('S2 component envelope • conceptual',(sx,sy-1,13.3),(16,19,3.4),BLACK),18)

# Converter cassette: placeholder module, captive edge by lip; jaw slides laterally and bolts to base.
cx,cy=22,45
floor=part(box('03 converter recessed floor • placeholder',(cx,cy,4),(26,36,2),TEAL))
# Floor fixed to base using two M3 bolts in external ears; no screws through module.
for y in [cy-23,cy+23]:
    floor=boolean(floor,box('floor mounting ear',(cx,y,4),(10,12,2),TEAL),'UNION')
    drill(floor,(cx,y,4),1.7,8);drill(base,(cx,y,1.5),1.7,8)
    bolt('M3 x 10 converter floor bolt',cx,y,5,3,10)
    hexnut('M3 floor nut — accessible underside',cx,y,-1.2,5.5,2.4,3)
for y in [cy-20,cy+20]:
    floor=boolean(floor,box('converter longitudinal end stop',(cx,y,7),(20,3,8),TEAL),'UNION')
for sign in [-1,1]:
    ex=cx+sign*20
    jaw=fuse([box('foot',(ex+sign*7,cy,4),(14,12,2)),box('upright',(ex+sign*1.5,cy,7.5),(3,10,9)),box('edge support ledge',(ex,cy,7),(6,10,2)),box('capture lip',(ex-sign*.25,cy,11),(4.5,10,2))],
        '04 converter sliding edge jaw '+str(sign),ORANGE)
    part(jaw,25)
    screw_x=ex+sign*8
    drill(jaw,(screw_x,cy,4),1.7,8)
    slot(base,screw_x-3,screw_x+3,cy,1.5,1.7,8)
    bolt('M3 x 10 converter jaw bolt',screw_x,cy,5,3,10)
    hexnut('M3 jaw nut — accessible underside',screw_x,cy,-1.2,5.5,2.4,3)
module=reference(box('CONVERTER PLACEHOLDER PCB — not measured',(cx,cy,8.8),(40,36,1.6),GREEN),16)
reference(box('CONVERTER PLACEHOLDER components',(cx,cy,17.8),(34,30,16.4),BLACK),16)

# Geometric checks describe this concept only; they cannot verify purchased component fit.
checks=[]
for o in assembly.objects:
    if o.get('part_type')!='PRINTED CONCEPT':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    bad=sum(not e.is_manifold for e in bm.edges)
    checks.append({'object':o.name,'non_manifold_edges':bad,'volume_mm3':round(bm.calc_volume(),3)})
    bm.free()
    if bad:raise RuntimeError('Non-manifold concept: '+o.name)
(OUT/'geometry-checks.json').write_text(json.dumps(checks,indent=2)+'\n')

# Exploded duplicate for visual review, never mixes reference components with print exports.
exploded=bpy.data.collections.new('V3 EXPLODED — assembly access review')
scene.collection.children.link(exploded)
for o in list(assembly.objects):
    dupe=o.copy();dupe.data=o.data.copy();exploded.objects.link(dupe)
    dupe.location.x+=155;dupe.location.z+=o.get('explode_z_mm',0)

def label(body,loc,size=3):
    bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.data.body=body;o.data.size=size;o.data.materials.append(BLACK)
label('ASSEMBLED RETENTION CONCEPT',(-59,-91,1))
label('EXPLODED / nuts accessible below',(96,-91,1))
label('V3: COMPONENT FIT NOT VERIFIED',(-50,92,0),4)
label('EXAMPLE PCB / dimensions pending',(0,75,3.1),2.4)
label('EXAMPLE PCB / dimensions pending',(155,75,3.1),2.4)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for loc in [(0,-100,230),(200,80,220)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=250000;o.data.size=200
bpy.ops.object.light_add(type='AREA',location=(80,-100,-230));lower=bpy.context.object
lower.rotation_euler=(Vector((75,0,0))-lower.location).to_track_quat('-Z','Y').to_euler()
lower.data.energy=150000;lower.data.size=200
bpy.ops.object.camera_add(location=(290,-340,380));cam=bpy.context.object
cam.rotation_euler=(Vector((75,0,14))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=340;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1800;scene.render.resolution_y=1250;scene.render.resolution_percentage=100
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='MATERIAL'
scene['review_status']='RETENTION CONCEPT. Factory hole offset, underside clearances, battery dimensions, converter geometry and bare edges need real-part verification.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'electronics-retention-v3.blend'))
scene.render.filepath=str(OUT/'electronics-retention-v3.png');bpy.ops.render.render(write_still=True)
# A separate underside view exposes nuts and bolt tips hidden in the main review camera.
original_location=cam.location.copy();original_rotation=cam.rotation_euler.copy()
cam.location=(270,-330,-350)
cam.rotation_euler=(Vector((75,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'electronics-retention-v3-underside.png');bpy.ops.render.render(write_still=True)
cam.location=original_location;cam.rotation_euler=original_rotation
