"""Blender generator: double / triple isolated actuators, millimetres.
Run Blender -b --factory-startup --python this_file -- double|triple.
Never alters the confirmed single-switch model. No electronics references.
"""
import sys, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
from mathutils.bvhtree import BVHTree

variant=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'double'
cfg=C; original=json.loads((ROOT/cfg['inherit']).read_text()); s=original['servo']; h=original['horn']; m=original['mount']
v=cfg['variants'][variant]; N=v['gangs']; W=v['plate_width']; pitch=cfg['gang_pitch']
OUT=ROOT/'generated'/variant; OUT.mkdir(parents=True,exist_ok=True)
for stale in OUT.glob('*.stl'):stale.unlink()
PRINTS=[]; REFS=[]; PAD=[]; SERVOS=[]; PADDLES=[]; SADDLES=[]; MOTION=[]
def ref(o): o['role']='reference_only';REFS.append(o);return o
def printed(o):o['role']='print';PRINTS.append(o);return o
def move(o,x,side):
    # Proper 180-degree Z rotation, not negative-scale reflection.
    T=Matrix.Translation((x,0,0))@Matrix.Rotation(math.pi if side<0 else 0,4,'Z')
    o.data.transform(T@o.matrix_world);o.matrix_world=Matrix.Identity(4);return o
def slot(o,p,length,width,depth,axis='Z'):
    cut(o,p,(depth,length,width) if axis=='X' else (width,length,depth))
    for d in (-1,1):drill(o,(p[0],p[1]+d*length/2,p[2]),width/2,depth,axis)
def flange_ramp(pivot):
    vertices=[(x,y,pivot+z) for x,hy,hz in [(3,6,3),(9,12,7)] for y,z in [(-hy,-hz),(hy,-hz),(hy,hz),(-hy,hz)]]
    mesh=bpy.data.meshes.new('45degree printable horn transition');mesh.from_pydata(vertices,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update()
    ob=bpy.data.objects.new('horn flange support ramp',mesh);scene.collection.objects.link(ob);return ob
def worldtree(o):
    return BVHTree.FromPolygons([o.matrix_world@p.co for p in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
def intersect(a,b):return bool(worldtree(a).overlap(worldtree(b)))
padx=W/2-cfg['outer_pad_edge_inset']-cfg['pad_width']/2
back=cfg['frame_back_z']; ft=cfg['frame_thickness']; top=back+ft
pieces=[box('strip pad',(x,0,back+ft/2),(cfg['pad_width'],cfg['pad_length'],ft)) for x in (-padx,padx)]
pieces += [box('upper lower frame rail',(0,y,back+ft/2),(2*padx,8,ft)) for y in (-54,54)]
positions=[(i-(N-1)/2)*pitch for i in range(N)]
mount_centers=[]
for i,x in enumerate(positions):
    side=-1 if i==0 else 1
    sx=x+side*34
    mount_centers.append((sx,side))
    # Extend both frame rails out to each servo saddle screw, with 5mm edge margin.
    if abs(sx)+5>padx:
        for y in (-54,54):pieces.append(box('outboard rail extension',((sx+side*padx)/2,y,back+ft/2),(abs(sx-side*padx)+10,8,ft)))
frame=printed(fuse(pieces,variant.upper()+' 01 flat adhesive frame',TEAL))
for sx,_ in mount_centers:
    for y in (-54,54):drill(frame,(sx,y,back+ft/2),1.7,10)

for i,x in enumerate(positions):
    side=-1 if i==0 else 1; raised=cfg['center_pivot_raise'] if N==3 and i==1 else 0
    pivot=original['paddle']['pivot_z']+raised; tip=17; basex=tip+s['base_to_shaft_tip']; by=-s['shaft_offset_y']; earx=basex-s['base_to_ear_under']-s['ear_thickness']/2; supportx=basex-s['base_to_ear_under']+3
    assert abs(supportx-34)<.001
    saddleparts=[box('flat saddle foot',(supportx,0,top+2),(10,116,4))]
    for yy in (-1,1):
        tower=box('ear post',(supportx,by+yy*(s['ear_hole_pitch']/2+.5),(top+3.8+pivot+8)/2),(5,5,pivot+8-(top+3.8)))
        slot(tower,(supportx,by+yy*(s['ear_hole_pitch']/2+.5),pivot),1.6,2.2,10,'X');saddleparts.append(tower)
    saddle=fuse(saddleparts,f'{variant.upper()} {i+2:02} servo saddle {i+1}',TEAL)
    for yy in (-54,54):drill(saddle,(supportx,yy,top+2),1.7,12)
    printed(move(saddle,x,side));SADDLES.append(saddle)
    body=move(ref(box(f'MG90S {i+1} case',(basex-s['case_height']/2,by,pivot),(s['case_height'],s['case_length'],s['case_width']),GREY)),x,side)
    ear=box(f'MG90S {i+1} ears',(earx,by,pivot),(s['ear_thickness'],s['ear_span'],s['case_width']),GREY)
    for yy in (-1,1):drill(ear,(earx,by+yy*s['ear_hole_pitch']/2,pivot),1.1,8,'X')
    move(ref(ear),x,side)
    shaft=move(ref(cyl(f'MG90S {i+1} shaft',(tip+2.05,0,pivot),2.4,4.1,'X',GOLD)),x,side)
    SERVOS.extend([body,ear,shaft])
    horn=fuse([box('horn arm',(14,0,pivot),(2,h['arm_span'],h['arm_width'])),cyl('horn hub',(15,0,pivot),h['hub_diameter']/2,4,'X')],f'Stock horn {i+1}',GOLD)
    drill(horn,(14,0,pivot),1.1,10,'X');move(ref(horn),x,side)
    contact_y=19 if raised else 26
    contact_bottom=12 if raised else 13.7
    bottom=contact_bottom+2.2
    yoke=fuse([box('paddle',(0,0,pivot),(8,60,6)),box('offset',(5,0,pivot),(14,12,6)),box('flange',(11,0,pivot),(4,24,14)),flange_ramp(pivot),*[box('contact leg',(0,y,(bottom+pivot-2.9)/2),(8,8,pivot-2.9-bottom)) for y in(-contact_y,contact_y)]],f'{variant.upper()} {N+2+i:02} paddle {i+1}'+(' extended center' if raised else ''),ORANGE)
    drill(yoke,(11,0,pivot),2.4,36,'X')
    for yy in (-7,7):slot(yoke,(11,yy,pivot),4,2.2,10,'X')
    printed(move(yoke,x,side));yoke['mount_side']=side;PADDLES.append(yoke)
    pads=[move(ref(cyl(f'Soft contact {i+1}',(0,yy,contact_bottom+1.1),3.95,2.2,'Z',RED)),x,side) for yy in (-contact_y,contact_y)]
    MOTION.append((x,pivot,side,[yoke,horn,*pads]))
    ref(box(f'Rocker {i+1}',(x,0,8),(31.5,65,4),WHITE))
    ref(box(f'Bezel {i+1}',(x,0,6.75),(35,70,1.5),WHITE))
ref(box('Nominal wall plate',(0,0,3),(W,cfg['plate_height'],6),WHITE))
for x in(-padx,padx):
    PAD.append(ref(box('Command 17207 full pair outline',(x,0,8),(m['strip_width'],m['strip_length'],4),WHITE)))

# Check translated parts against fixed bodies and every combination of adjacent poses.
def pose(index,angle):
    x,pivot,side,objects=MOTION[index]
    T=Matrix.Translation((x,0,pivot))@Matrix.Rotation(math.radians(angle)*side,4,'X')@Matrix.Translation((-x,0,-pivot))
    for ob in objects:ob.matrix_world=T
collisions=[]
for i in range(N):
    for angle in range(-10,11):
        pose(i,angle)
        for fixed in [frame,*SADDLES,*SERVOS]:
            if intersect(PADDLES[i],fixed):collisions.append([i,angle,fixed.name])
    pose(i,0)
pair_collisions=[]
for i in range(N):
    for j in range(i+1,N):
        for a in range(-10,11):
            pose(i,a)
            for b in range(-10,11):
                pose(j,b)
                if intersect(PADDLES[i],PADDLES[j]):pair_collisions.append([i,j,a,b])
        pose(i,0);pose(j,0)
assert not collisions,collisions
assert not pair_collisions,pair_collisions

report={'variant':variant,'status':'CONCEPT — physical multi-gang fit and servo travel unverified','units':'mm','gang_pitch_mm':pitch,'plate_width_mm':W,'pad_size_mm':[cfg['pad_width'],cfg['pad_length']],'strip_pair_count':2,'center_pivot_raise_mm':cfg['center_pivot_raise'] if N==3 else 0,'moving_paddle_fixed_geometry_collisions':collisions,'independent_paddle_pose_collisions':pair_collisions,'sampled_angles_degrees':list(range(-10,11)),'source_single_config_sha256':hashlib.sha256((ROOT/cfg['inherit']).read_bytes()).hexdigest(),'saddle_fasteners':f'{2*N} M3x10 screws and {2*N} ordinary M3 nuts','servo_ear_fasteners':f'{2*N} M2x10 and {2*N} ordinary M2 nuts; reuse stock horn center screws','caveats':['Nominal gang spacing and plate width; single fit confirmation does not verify multi-gang plate.','Two outer strip pairs only; adhesive torque/peel capacity untested.','4mm mated strip thickness assumed.','Triple center actuator has longer contact legs; stiffness and movement must be tested.','Servo control electronics and multi-channel software are not included.','Paddle flange includes a 45-degree printable transition; horizontal M2 saddle holes bridge 2.2mm. Review slicer preview before printing.']}

def studio(scale,target):
    scene.render.engine='CYCLES';scene.cycles.samples=16
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.75,.8,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
    for loc,energy in [((50,-90,250),250000),((-130,70,160),180000)]:
        bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=energy;ob.data.size=160;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=Vector(target)+Vector((150,-220,280)));cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;scene.camera=cam
    scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False

for ob in PRINTS:ob['print_caveat']='Concept - verify multi-gang spacing and full pad contact'
studio(220 if N==2 else 270,(0,0,20))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(variant+'-assembled-CONCEPT.blend')))
scene.render.filepath=str(OUT/'assembly.png');bpy.ops.render.render(write_still=True)

# One master STL: all detached physical pieces, no reference hardware, arranged on A1 bed.
for ob in list(scene.objects):
    if ob not in PRINTS:bpy.data.objects.remove(ob,do_unlink=True)
PRINTS=[frame,*SADDLES,*PADDLES]
layout=[]; xcursor=8; ycursor=8; rowheight=0; alltris=[]
for index,ob in enumerate(PRINTS):
    R=Matrix.Rotation(-ob['mount_side']*math.pi/2,4,'Y') if ob in PADDLES else Matrix.Identity(4)
    ob.data.transform(R@ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
    # Recalculate outward normals before export; every intended part must be watertight and connected.
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert bad==0 and vol>0,(ob.name,bad,vol)
    todo=set(bm.verts);components=0
    while todo:
        components+=1; stack=[todo.pop()]
        while stack:
            for e in stack.pop().link_edges:
                for vv in e.verts:
                    if vv in todo:todo.remove(vv);stack.append(vv)
    assert components==1,(ob.name,components)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    lo=Vector([min(p.co[k] for p in ob.data.vertices) for k in range(3)]);hi=Vector([max(p.co[k] for p in ob.data.vertices) for k in range(3)]);dim=hi-lo
    # Rotating saddle footprint 90 degrees keeps the full kit within one 256mm plate.
    if ob in SADDLES:
        ob.data.transform(Matrix.Rotation(math.pi/2,4,'Z'));lo=Vector([min(p.co[k] for p in ob.data.vertices) for k in range(3)]);hi=Vector([max(p.co[k] for p in ob.data.vertices) for k in range(3)]);dim=hi-lo
    if xcursor+dim.x>248:xcursor=8;ycursor+=rowheight+6;rowheight=0
    shift=Vector((xcursor,ycursor,0))-lo;ob.data.transform(Matrix.Translation(shift));ob.data.update()
    triangles=[[ob.data.vertices[vi].co.copy() for vi in f.vertices] for f in ob.data.polygons]
    filename=f'{index+1:02d}_'+('frame' if ob==frame else ('saddle' if ob in SADDLES else 'paddle'))+'.stl'
    def write_stl(path,triangles):
        with path.open('wb') as f:
            f.write(b'auto-switch multi CONCEPT; mm; separate parts'.ljust(80,b' '));f.write(struct.pack('<I',len(triangles)))
            for a,b,c in triangles:
                normal=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*normal,*a,*b,*c,0))
    # Individual files retain their bed XY positions, so importing all preserves layout.
    write_stl(OUT/filename,triangles);alltris.extend(triangles)
    contact=sum(f.area for f in ob.data.polygons if all(abs(ob.data.vertices[vi].co.z)<.0001 for vi in f.vertices))
    layout.append({'name':ob.name,'file':filename,'bounds_min_mm':[xcursor,ycursor,0],'dimensions_mm':list(dim),'bed_contact_mm2':contact,'non_manifold_edges':bad,'connected_components':components,'volume_mm3':vol})
    xcursor+=dim.x+6;rowheight=max(rowheight,dim.y)
assert ycursor+rowheight<=248,('layout too tall',ycursor+rowheight)
write_stl(OUT/(variant+'-ALL-PIECES-CONCEPT.stl'),alltris)
report['print_parts']=layout;report['master_footprint_max_mm']=[max(p['bounds_min_mm'][0]+p['dimensions_mm'][0] for p in layout),ycursor+rowheight]
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
ref(box('A1 bed reference',(128,128,-1.1),(256,256,2),GREY))
studio(355,(128,128,0))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(variant+'-print-layout-CONCEPT.blend')))
scene.render.filepath=str(OUT/'print-layout.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
