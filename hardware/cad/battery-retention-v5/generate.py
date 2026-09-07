"""Replacement-only retainers for the already-printed v4 electronics carrier.
Blender only. Millimetres. No older CAD files modified.
"""
import sys, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
from mathutils.bvhtree import BVHTree
PRINTS=[];REFS=[];SHIMS=[];REPORT=[]
def reference(o):o['role']='reference_only';REFS.append(o);return o
def printable(o):o['role']='replacement_print';PRINTS.append(o);return o
def hexsolid(name,x,y,z,across,depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=across/math.sqrt(3),depth=depth,location=(x,y,z));o=bpy.context.object;o.name=name;o.rotation_euler.z=math.pi/6;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);return o
def bolt(name,x,y,underhead,length):
    return reference(fuse([cyl('shaft',(x,y,underhead-length/2),1.5,length),cyl('head',(x,y,underhead+1.5),2.75,3)],name,GREY))
def nut(name,x,y,bottom):
    o=hexsolid(name,x,y,bottom+1.2,5.5,2.4);drill(o,(x,y,bottom+1.2),1.5,5);o.data.materials.append(GREY);return reference(o)
def transform(o,T):o.data.transform(T@o.matrix_world);o.matrix_world=Matrix.Identity(4);return o
def meshcheck(o):
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
    remain=set(bm.verts);components=0
    while remain:
        components+=1;stack=[remain.pop()]
        while stack:
            for e in stack.pop().link_edges:
                for vv in e.verts:
                    if vv in remain:remain.remove(vv);stack.append(vv)
    assert bad==0 and volume>0 and components==1,(o.name,bad,volume,components)
    bm.to_mesh(o.data);bm.free();return {'name':o.name,'non_manifold_edges':bad,'components':components,'volume_mm3':volume}
def intersection(a,b):
    def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
    return bool(tree(a).overlap(tree(b)))

# Import the existing carrier only, as unmodified non-printable assembly context.
with bpy.data.libraries.load(str(ROOT/C['reuse_carrier']),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('01 carrier base') and 'bed' not in n]
assert len(dst.objects)==1
carrier=dst.objects[0];scene.collection.objects.link(carrier);reference(carrier)
carrier.name='EXISTING V4 CARRIER — REUSE, DO NOT REPRINT'

# Correct body/switch split from seller dimension photo: 19mm body,22.5mm switch peak.
holder=reference(box('AA case — 68.7 x64.2 x19 body',(0,-32,12.5),(68.7,64.2,19),BLACK))
bev=holder.modifiers.new('Approximate molded case corners','BEVEL');bev.width=.8;bev.segments=3;bpy.context.view_layer.objects.active=holder;bpy.ops.object.modifier_apply(modifier=bev.name)
reference(box('Approximate cover seam',(0,-32,8.0),(68.8,64.3,.18),GREY))
sx,sy=C['switch_center_xy'];dx,dy=C['switch_opening_xy_mm']
switch=reference(box('Photo-estimated ON OFF switch recess',(sx,sy,22.05),(dx,dy,.2),GREY))
reference(box('Slide switch — protrusion3.5mm',(sx,sy-1.8,23.75),(dx*.82,dy*.46,3.5),BLACK))
keepout=reference(box('FINGER ACCESS KEEP-OUT — display only',(sx,sy,31),(18,22,18),RED));keepout.hide_render=True;keepout.hide_set(True)
wirekeep=reference(box('WIRE ROUTE CORRIDOR — exit height unconfirmed',(43,-2,17),(21,5,10),RED));wirekeep.hide_render=True;wirekeep.hide_set(True)
for yy,color in [(-1.0,RED),(-2.5,BLACK)]:
    # Raised routed stubs are illustrations, not measured exit coordinates.
    reference(cyl('Illustrative insulated wire stub',(42,yy,16),.65,17,'X',color))

rails=[];pads=[]
for side in (-1,1):
    # Build right-hand part, then mirror by a proper180degree rotation plus Y translation.
    # FrontfaceZ31 is flat; recessed mounting heads still bear atZ29.
    rail=fuse([box('outside spine',(43,-32,28.5),(10,52,5)),box('central pressure arm',(35.5,-32,29),(15,8,4))],('LEFT' if side<0 else 'RIGHT')+' fixed battery edge rail',TEAL)
    for yy in (-52,-12):
        drill(rail,(43,yy,28),1.7,12)
        drill(rail,(43,yy,31),3.2,4) # counterbore startsat29
    drill(rail,(32,-32,29),1.7,12)
    boolean(rail,hexsolid('bottom-load M3 nut pocket',32,-32,27.7,5.95,2.6),'DIFFERENCE') # roof29..31; upward adjuster load bears against this roof
    # Two small top lips guide the pressure shoe while leaving center screw access.
    pad=fuse([box('broad case contact pad',(32,-32,23),(8,10.8,2)),box('shoe side wall',(32,-37,28.6),(8,1.2,11.2)),box('shoe side wall',(32,-27,28.6),(8,1.2,11.2)),box('retaining lip',(32,-36.45,33.6),(8,2.3,1.2)),box('retaining lip',(32,-27.55,33.6),(8,2.3,1.2))],('LEFT' if side<0 else 'RIGHT')+' captured pressure shoe',ORANGE)
    # Blind recess stops the metal screw1.2mmabovecase, spreadingloadthroughplastic.
    drill(pad,(32,-32,24.2),1.8,2) # lowerlimit23.2 =0.8mmdeepfrom24
    if side<0:
        T=Matrix.Translation((0,-64,0))@Matrix.Rotation(math.pi,4,'Z')
        transform(rail,T);transform(pad,T)
    # Bake both handed variants before world-space travel transforms.
    transform(rail,Matrix.Identity(4));transform(pad,Matrix.Identity(4))
    printable(rail);printable(pad);rails.append(rail);pads.append(pad)
    for yy in (-52,-12):bolt('REUSE M3x35 mounting screw',side*43,yy,29,35);nut('REUSE M3 underside nut',side*43,yy,-2.4)
    bolt('NEW M3x10 adjustment screw',side*32,-32,33.2,10);nut('NEW M3 adjustment nut',side*32,-32,26.6)
    assert not intersection(rail,keepout),(rail.name,'switch access')
    assert not intersection(pad,keepout),(pad.name,'switch access')
    assert not intersection(rail,wirekeep),(rail.name,'wire corridor')
    REPORT.extend([meshcheck(rail),meshcheck(pad)])

# Check full specified shoe travel against fixed rails and switch-access volume.
height_checks=[]
for hh in [18.5+i*.25 for i in range(9)]:
    for pad in pads:
        pad.matrix_world=Matrix.Translation((0,0,hh-19))
        assert not any(intersection(pad,rail) for rail in rails),(pad.name,'travel collision',hh)
        assert not intersection(pad,keepout),(pad.name,'switch access',hh)
    height_checks.append(hh)
for pad in pads:pad.matrix_world=Matrix.Identity(4)

# Shims locate the case in BOTH horizontal axes. Each has an outward grip over the cradle wall.
def shim(thickness):
    o=fuse([box('shim blade',(6,4.25,thickness/2),(12,8.5,thickness)),box('outward grip',(6,8.9,(thickness+3.4)/2),(12,1.4,thickness+3.4))],f'cradle shim {thickness:.1f}mm',ORANGE)
    o['role']='shim_print_source';return o
for thickness in C['shim_thicknesses_mm']:
    o=shim(thickness);SHIMS.append(o);o.hide_render=True;o.hide_set(True);REPORT.append(meshcheck(o))
# Four0.6mmshims illustrated; finalchoice depends onactualfit(.6+.8 fillsnominal1.4).
for side in (-1,1):
    for axis in ('X','Y'):
        o=shim(.6);reference(o)
        if axis=='X':
            # localX tangent, localY upright, localZ outward.
            R=Matrix(((0,0,side),(side,0,0),(0,1,0))).to_4x4();origin=(side*(35.05-.6),-32-side*6,3)
        else:
            R=Matrix(((-side,0,0),(0,0,side),(0,1,0))).to_4x4();origin=(side*6,-32+side*(32.8-.6),3)
        transform(o,Matrix.Translation(origin)@R)

def studio(scale,target):
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
    for loc in [(140,-180,230),(-160,20,180)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=180000;o.data.size=160;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=Vector(target)+Vector((145,-165,205)));cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;scene.camera=cam
    scene.render.engine='CYCLES';scene.cycles.samples=20;scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
studio(180,(0,-28,12))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'battery-retention-v5-assembly.blend'))
scene.render.filepath=str(OUT/'battery-retention-v5-assembly.png');bpy.ops.render.render(write_still=True)

# Replacement-only export:2rails+2pressure shoes+4each of3shim sizes =16pieces.
for o in list(scene.objects):
    if o not in PRINTS and o not in SHIMS:bpy.data.objects.remove(o,do_unlink=True)
alltris=[];exports=[];xc=8;yc=8;rowh=0
def write_stl(path,tris):
    with path.open('wb') as f:
        f.write(b'auto-switch v5 replacement battery retainers; mm; fit check required'.ljust(80,b' '));f.write(struct.pack('<I',len(tris)))
        for a,b,c in tris:
            nn=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*nn,*a,*b,*c,0))
for i,o in enumerate([*PRINTS,*SHIMS]):
    o.hide_set(False);o.hide_render=False
    rot=Matrix.Rotation(math.pi,4,'X') if o in rails else (Matrix.Rotation(math.pi/2,4,'Y') if o in pads else Matrix.Identity(4))
    transform(o,rot)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    lo=Vector([min(v.co[k] for v in o.data.vertices) for k in range(3)]);hi=Vector([max(v.co[k] for v in o.data.vertices) for k in range(3)]);dim=hi-lo
    # IndividualfilescenteredXY,bedZ0.
    centered=[v.co-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)) for v in o.data.vertices]
    filename=(f'{i+1:02d}_'+o.name.replace(' ','_')+'.stl');tris=[tuple(centered[idx] for idx in f.vertices) for f in o.data.polygons];write_stl(OUT/filename,tris)
    copies=4 if o in SHIMS else 1
    for n in range(copies):
        if xc+dim.x>150:xc=8;yc+=rowh+7;rowh=0
        offset=Vector((xc,yc,0))-lo;packed=[v.co+offset for v in o.data.vertices]
        alltris.extend(tuple(packed[idx] for idx in f.vertices) for f in o.data.polygons)
        dupe=o.copy();dupe.data=o.data.copy();scene.collection.objects.link(dupe);dupe.name=o.name+f' print copy{n+1}'
        for vv,pos in zip(dupe.data.vertices,packed):vv.co=pos
        dupe['role']='print_layout';dupe.hide_render=False;dupe.hide_set(False)
        exports.append({'source_file':filename,'copy':n+1,'bounds_min_mm':[xc,yc,0],'dimensions_mm':list(dim),'quantity_in_master':copies})
        xc+=dim.x+7;rowh=max(rowh,dim.y)
    o.hide_render=True;o.hide_set(True)
write_stl(OUT/'battery-retention-v5-REPLACEMENT-ALL-PIECES.stl',alltris)
assert yc+rowh<248
report={'status':'Replacement ready for dry fit; supplier dimensions/photo estimates, actual fit pending','checks':REPORT,'config':C,'master_file':'battery-retention-v5-REPLACEMENT-ALL-PIECES.stl','master_piece_count':len(exports),'layout':exports,'tested_body_heights_mm':height_checks,'adjuster_nut_fixed_roof_mm':2.0,'adjuster_underhead_z_range_mm':[32.7,34.7],'adjuster_tip_to_case_min_plastic_mm':1.2,'switch_keepout_newpart_surface_collisions':0,'wire_corridor_newrail_surface_collisions':0,'original_carrier_modified':False,'assembly_source_sha256':hashlib.sha256((ROOT/C['reuse_carrier']).read_bytes()).hexdigest(),'limits':['Wire exit height is unconfirmed; stubs illustrate routing above the low cradle rim.','Pressure shoes slide onto central arms; keep screw tips engaged in blind seats during use.','Remove both rails to lift out holder; loosening adjusters does not remove edge obstructions.','Tighten adjusters only until play stops; do not crush the battery case.','Original carrier posts remain; switch finger-window margin near the post is small.']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
bed=box('A1 bed reference',(80,60,-1),(170,135,2),GREY);bed['role']='reference_only'
studio(205,(80,60,0))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'battery-retention-v5-print-layout.blend'))
scene.render.filepath=str(OUT/'battery-retention-v5-print-layout.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
