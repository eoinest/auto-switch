"""V4 flat-bed carrier + separate screw-on Command bracket; concept fit unverified. Units mm.
blender --background --python hardware/cad/electronics-retention-v4/generate.py
"""
import sys, math, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from cadlib import *

assembly=bpy.data.collections.new('V4 ASSEMBLED — FIT UNVERIFIED')
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

# Separate rear bracket: continuous wall-facing pad surfaces, all z=-13.
# Carrier still starts at z=0; no integrated feet or suspended underside floor.
bracket=part(fuse([box('left strip pad',(-50,0,-11.5),(20,144,3)),box('right strip pad',(50,0,-11.5),(20,144,3)),box('H crossmember',(0,0,-11.5),(100,10,3))],'05 screw-on wall bracket • continuous Command pads',TEAL),-35)
for x in [-53,53]:
    for y in [-65,65]:
        bracket=boolean(bracket,box('bracket standoff',(x,y,-5),(14,12,10),TEAL),'UNION')
        # Blind bore, leaving rear adhesive plane continuous. Slot loads nut from inward side.
        drill(bracket,(x,y,-4.5),1.7,10)
        cut(bracket,((50 if x>0 else -50),y,-6),(14,6,2.8))
        drill(base,(x,y,1.5),1.7,8)
        bolt('M3 x 12 carrier attachment',x,y,3,3,12)
        nut=hexnut('M3 attachment nut — side loaded',x,y,-5.9,5.5,2.4,3)
        nut.rotation_euler.z=math.pi/6  # Flat faces against slot sides; default cylinder is point-up.
        # No modeled washer; nuts must enter before attaching tray.

import struct,hashlib
STLS=OUT/'stl-concept';STLS.mkdir(exist_ok=True)
objects=sorted([o for o in assembly.objects if o.get('part_type')=='PRINTED CONCEPT'],key=lambda o:o.name)
assert len(objects)==7
filenames=['01_carrier_base_CONCEPT.stl','02_battery_bar_1_CONCEPT.stl','03_battery_bar_2_CONCEPT.stl','04_converter_floor_CONCEPT.stl','05_converter_jaw_left_CONCEPT.stl','06_converter_jaw_right_CONCEPT.stl','07_wall_bracket_CONCEPT.stl']
placements=[(5,5),(5,175),(5,190),(115,175),(155,175),(180,175),(130,5)]
layout=bpy.data.collections.new('V4 PRINT LAYOUT — seven pieces on A1 bed');scene.collection.children.link(layout)
reports=[];all_triangles=[];assembly_triangles=[]
def write_stl(path,triangles):
    with path.open('wb') as f:
        f.write(b'auto-switch v4 CONCEPT; millimetres; physical component fit unverified'.ljust(80,b' '));f.write(struct.pack('<I',len(triangles)))
        for a,b,c in triangles:
            n=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
def bounds(pts):return Vector([min(p[i] for p in pts) for i in range(3)]),Vector([max(p[i] for p in pts) for i in range(3)])
for o,filename,xy in zip(objects,filenames,placements):
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True)
    assert bad==0 and vol>0,(o.name,bad,vol)
    bm.to_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    mesh=bpy.data.meshes.new(filename);bm.to_mesh(mesh);bm.free()
    world=[o.matrix_world@v.co for v in mesh.vertices]
    assembly_triangles.extend(tuple(world[i] for i in p.vertices) for p in mesh.polygons)
    rotation=Matrix.Rotation(math.pi/2,4,'X') if 'jaw' in filename else Matrix.Identity(4)
    rotated=[rotation@p for p in world];lo,hi=bounds(rotated)
    centered=[p-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)) for p in rotated]
    triangles=[tuple(centered[i] for i in p.vertices) for p in mesh.polygons]
    write_stl(STLS/filename,triangles)
    offset=Vector((xy[0]-lo.x,xy[1]-lo.y,-lo.z))
    packed=[p+offset for p in rotated]
    all_triangles.extend(tuple(packed[i] for i in p.vertices) for p in mesh.polygons)
    dupe=bpy.data.objects.new(o.name+' • bed',mesh.copy());layout.objects.link(dupe)
    for v,p in zip(dupe.data.vertices,packed):v.co=p
    for mat in o.data.materials:dupe.data.materials.append(mat)
    dupe['part_type']='PRINT LAYOUT';dupe['source_object']=o.name
    pmin,pmax=bounds(packed)
    reports.append({'file':filename,'source_object':o.name,'dimensions_mm':[round(x,4) for x in hi-lo],'non_manifold_edges':bad,'volume_mm3':round(vol,4),'triangles':len(triangles),'rotation_x_degrees':90 if 'jaw' in filename else 0,'layout_min_mm':list(pmin),'layout_max_mm':list(pmax),'world_rotation_then_translation_mm':list(offset),'sha256':hashlib.sha256((STLS/filename).read_bytes()).hexdigest()})
    bpy.data.meshes.remove(mesh)
write_stl(OUT/'electronics-wall-mount-ALL-PIECES-v4-CONCEPT.stl',all_triangles)
write_stl(OUT/'electronics-wall-mount-ASSEMBLED-v4-CONCEPT.stl',assembly_triangles)
for i,a in enumerate(reports):
    for b in reports[i+1:]:
        assert any(a['layout_max_mm'][k] <= b['layout_min_mm'][k] or b['layout_max_mm'][k] <= a['layout_min_mm'][k] for k in [0,1]),(a['file'],b['file'])
report={'status':'CONCEPT — actual component fit unverified','units':'mm','parts':reports,'master_file':'electronics-wall-mount-ALL-PIECES-v4-CONCEPT.stl','master_bounds_mm':[[5,5,0],[250,233,26]],'bed_mm':[256,256],'assembly_carrier_bottom_z_mm':0,'wall_contact_plane_z_mm':-13,'pad_face_size_mm':[20,144],'minimum_old_fastener_tip_to_pad_front_clearance_mm':4,'attachment':'4 x M3 x 12 bolts + 4 standard M3 nuts; no washers','supports':'Carrier and rear pads flat on bed. Bracket nut pockets have 6 mm roof bridges: inspect bridging in slicer, no generated support expected. Existing jaws are side-down and have a 1 mm recess; slicer may request local support.','component_fit':'Preserved v3 holder/S2 geometry; converter remains unmeasured placeholder. This revision verifies mounting geometry only.'}
(OUT/'export-manifest.json').write_text(json.dumps(report,indent=2)+'\n')

# Render and save two intentionally distinct scenes; assembly hardware never enters print export.
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.86,.9,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
for loc in [(0,-150,260),(160,100,200),(-160,-100,-200)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=220000;light.data.size=180
    light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(190,-250,260));cam=bpy.context.object;scene.camera=cam
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=240
scene.render.engine='CYCLES';scene.cycles.samples=20
scene.render.resolution_x=1500;scene.render.resolution_y=1500;scene.render.resolution_percentage=100
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
layout.hide_render=True;layout.hide_viewport=True
scene['review_status']='V4 two-part mounting structure. Strip pads and fastener clearances modeled; physical fit of purchased electronics unverified.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'electronics-retention-v4.blend'))
scene.render.filepath=str(OUT/'assembled-v4.png');bpy.ops.render.render(write_still=True)
cam.location=(180,-240,-260);cam.rotation_euler=(Vector((0,0,-5))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'rear-pads-v4.png');bpy.ops.render.render(write_still=True)
assembly.hide_render=True;assembly.hide_viewport=True;layout.hide_render=False;layout.hide_viewport=False
cam.location=(127,119,330);cam.rotation_euler=(0,0,0);cam.data.ortho_scale=275
scene.render.filepath=str(OUT/'print-layout-v4.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'electronics-print-layout-v4.blend'));bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
