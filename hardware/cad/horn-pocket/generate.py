"""Provisional stock-horn locating seat. Blender only; millimetres.
Exports fit coupons, never production paddles. Existing models remain untouched.
"""
import sys, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
from mathutils.bvhtree import BVHTree
H=dict(C['horn']);S=C['seat']; REPORT=[]; COUPONS=[]; VARIANTS=[]
OUT=ROOT/'generated';OUT.mkdir(exist_ok=True)
# Remove only this generator's obsolete coupon meshes, never other production files.
for old in OUT.glob('horn-fit-coupon*.stl'):old.unlink()
INK=material('Labels',(.07,.09,.12)); LILAC=material('Provisional stock horn reference',(.63,.54,.86))
def tag(o,role):o['role']=role;return o
def label(body,loc,size=2.2):
    bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.name='LABEL '+body;o.data.body=body;o.data.size=size;o.data.extrude=.01;o.data.materials.append(INK);o.rotation_euler=Matrix(((0,0,1),(1,0,0),(0,1,0))).to_euler();return tag(o,'display_only')
def silhouette(name,x,depth,clearance,extra=0,pivot=0):
    # Photo-informed tapered arms with semicircular ends and a circular hub.
    # Clearance expands the widths and radii; physical coupon testing determines the final fit.
    delta=clearance+extra
    root_half=H['arm_root_width']/2+delta;tip_radius=H['arm_tip_width']/2+delta
    tip_center=H['arm_span']/2-H['arm_tip_width']/2
    hub_radius=H['hub_diameter']/2+delta
    # root_width is the visible arm width where it emerges from the round hub.
    zq=root_half;q=math.sqrt(hub_radius*hub_radius-zq*zq);theta=math.atan2(zq,q)
    outline=[(-tip_center,-tip_radius),(-q,-zq)]
    outline += [(hub_radius*math.cos(t),hub_radius*math.sin(t)) for t in [math.pi+theta+(math.pi-2*theta)*i/24 for i in range(1,25)]]
    outline += [(tip_center,-tip_radius)]
    outline += [(tip_center+tip_radius*math.cos(t),tip_radius*math.sin(t)) for t in [-math.pi/2+math.pi*i/24 for i in range(1,25)]]
    outline += [(q,zq)]
    outline += [(hub_radius*math.cos(t),hub_radius*math.sin(t)) for t in [theta+(math.pi-2*theta)*i/24 for i in range(1,25)]]
    outline += [(-tip_center,tip_radius)]
    outline += [(-tip_center+tip_radius*math.cos(t),tip_radius*math.sin(t)) for t in [math.pi/2+math.pi*i/24 for i in range(1,24)]]
    n=len(outline);vertices=[(xx,y,pivot+z) for xx in [x-depth/2,x+depth/2] for y,z in outline]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return ob
def slot(ob,y,pivot):
    length=C['horn_attachment_slot_straight_length'];diam=C['horn_attachment_slot_diameter']
    cut(ob,(11,y,pivot),(20,length,diam))
    for d in (-1,1):drill(ob,(11,y+d*length/2,pivot),diam/2,20,'X')
def flange(name,clearance,pivot=0,holes=True):
    face=S['contact_plane_x'];back=S['flange_back_x'];depth=S['rim_depth']
    plate=box(name,(.5*(face+back),0,pivot),(face-back,S['flange_width'],S['flange_height']))
    # 0.2mm overlap below the face avoids coplanar union seams; floor remains4mm.
    rim=silhouette('raised locating rim',face+(depth-.2)/2,depth+.2,clearance,S['rim_wall'],pivot)
    result=fuse([plate,rim],name,ORANGE)
    inner=silhouette('open face pocket',face+(depth+1)/2,depth+1,clearance,0,pivot)
    boolean(result,inner,'DIFFERENCE')
    if holes:
        drill(result,(11,0,pivot),C['center_access_diameter']/2,24,'X')
        for y in C['horn_attachment_slot_centers_y']:slot(result,y,pivot)
    result['role']='printed_prototype';result['clearance_per_side_mm']=clearance;result['horn_contact_plane_x_mm']=face;result['floor_thickness_mm']=face-back
    return result
def horn(name,pivot=0):
    # The reference seated horn contact face staysX13, identical to baseline.
    o=fuse([silhouette('stock tapered double arm',13+H['arm_thickness']/2,H['arm_thickness'],0,0,pivot),cyl('stock hub',(13+H['hub_depth']/2,0,pivot),H['hub_diameter']/2,H['hub_depth'],'X')],name,LILAC)
    drill(o,(15,0,pivot),1.1,12,'X')
    for y in C['horn_attachment_slot_centers_y']:drill(o,(15,y,pivot),.65,12,'X')
    return tag(o,'reference_only')
def ramp(pivot):
    # Keep width growth at45degrees, beginning inside the unchanged paddle beam.
    half=S['flange_width']/2;start=9-(half-6)
    assert start>=-4,'Flange needs a revised paddle beam for support'
    vv=[(x,y,pivot+z) for x,hy,hz in [(start,6,3),(9,half,7)] for y,z in [(-hy,-hz),(hy,-hz),(hy,hz),(-hy,hz)]]
    me=bpy.data.meshes.new('45degree ramp');me.from_pydata(vv,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();ob=bpy.data.objects.new('flange support ramp',me);scene.collection.objects.link(ob);return ob
def paddle(name,raised=False):
    pivot=61 if raised else 31;contact_y=19 if raised else 26;bottom=14.2 if raised else 15.9
    f=flange('pocket flange',S['clearance_per_side'],pivot,False)
    ob=fuse([box('paddle beam',(0,0,pivot),(8,60,6)),box('offset',(5,0,pivot),(14,12,6)),ramp(pivot),f,*[box('contact leg',(0,y,(bottom+pivot-2.9)/2),(8,8,pivot-2.9-bottom)) for y in(-contact_y,contact_y)]],name,ORANGE)
    # Reopen access after fusing the supporting ramp.
    drill(ob,(11,0,pivot),C['center_access_diameter']/2,36,'X')
    for y in C['horn_attachment_slot_centers_y']:slot(ob,y,pivot)
    return tag(ob,'production_preview_NOT_EXPORTED')
def meshcheck(o):
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)

    if bad:print('BAD_EDGES',[(list(e.verts[0].co),list(e.verts[1].co),len(e.link_faces)) for e in bm.edges if not e.is_manifold])
    assert bad==0 and volume>0,(o.name,bad,volume)
    remain=set(bm.verts);components=0
    while remain:
        components+=1;stack=[remain.pop()]
        while stack:
            for e in stack.pop().link_edges:
                for v in e.verts:
                    if v in remain:remain.remove(v);stack.append(v)
    assert components==1,(o.name,components)
    bm.to_mesh(o.data);bm.free();return {'name':o.name,'non_manifold_edges':bad,'components':components,'volume_mm3':volume}
def studio(scale,target):
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.83,.86,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
    for loc,power,size in [((130,-70,150),170000,110),((150,100,40),90000,80)]:
        bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.size=size;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=Vector(target)+Vector((180,-95,130)));cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;scene.camera=cam
    scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False

# Close-up: empty pocket, seated stock horn and lifted horn, all actual contactX13.
for i,state in enumerate(['EMPTY SEAT','SEATED HORN','LIFTED HORN']):
    yy=(i-1)*40;seat=flange(state,S['clearance_per_side']);seat.location.y=yy;COUPONS.append(seat);REPORT.append(meshcheck(seat))
    if i:
        hh=horn(state+' reference');hh.location.y=yy
        if i==2:hh.location.x+=12
    label(state,(15,yy-13,-14),2)
label('PHOTO-ESTIMATED TAPERED HORN / VERIFY WITH FIT COUPON',(15,-51,20),2)
studio(165,(14,0,0))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'horn-seat-closeup-PROVISIONAL.blend'))
scene.render.filepath=str(OUT/'horn-seat-closeup.png');bpy.ops.render.render(write_still=True)

# In-context paddle family preview, no production STL export.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for name,y,raised,side in [('Single / right normal',-78,False,1),('Double left mirrored',0,False,-1),('Triple center raised',78,True,1)]:
    ob=paddle(name,raised);pivot=61 if raised else 31;hh=horn(name+' stock horn',pivot)
    T=Matrix.Translation((0,y,0))@Matrix.Rotation(math.pi if side<0 else 0,4,'Z')
    for item in (ob,hh):item.data.transform(T@item.matrix_world);item.matrix_world=Matrix.Identity(4)
    VARIANTS.append(ob);REPORT.append(meshcheck(ob));label(name,(20,y-27,-4),2.2)
label('PREVIEW ONLY / HORN DEPTH AND FIT UNCONFIRMED',(20,-84,83),3)
studio(285,(10,0,37))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'paddle-family-pocket-PREVIEW.blend'))
scene.render.filepath=str(OUT/'paddle-family-pocket.png');bpy.ops.render.render(write_still=True)

# Only the small fit-coupon set is exported. Print each cavity facing up.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
triangles_all=[];coupons=[]
for i,scale in enumerate(C['coupon_profile_scales']):
    H=dict(C['horn'])
    for key in ('arm_span','arm_root_width','arm_tip_width','hub_diameter'):H[key]*=scale
    clearance=S['clearance_per_side'];percent=round(scale*100)
    ob=flange(f'Coupon {percent}% profile / 0.3 mm clearance',clearance);check=meshcheck(ob)
    ob.data.transform(Matrix.Rotation(-math.pi/2,4,'Y')@ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
    lo=Vector([min(v.co[k] for v in ob.data.vertices) for k in range(3)]);hi=Vector([max(v.co[k] for v in ob.data.vertices) for k in range(3)])
    ob.data.transform(Matrix.Translation(Vector((i*22+8,8,0))-lo));ob.data.update()
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    triangles=[[ob.data.vertices[idx].co.copy() for idx in f.vertices] for f in ob.data.polygons]
    def write_stl(path,triangles):
        with path.open('wb') as f:
            f.write(b'PHOTO ESTIMATE horn FIT COUPON; not production paddle; mm'.ljust(80,b' '));f.write(struct.pack('<I',len(triangles)))
            for a,b,c in triangles:
                normal=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*normal,*a,*b,*c,0))
    filename=f'horn-fit-coupon-profile-{percent}pct-PHOTO-ESTIMATE.stl';write_stl(OUT/filename,triangles);triangles_all.extend(triangles)
    coupons.append({**check,'file':filename,'clearance_per_side_mm':clearance,'profile_scale':scale,'profile_span_mm':H['arm_span'],'dimensions_mm':list(hi-lo),'floor_thickness_mm':4,'bottom_z_mm':min(v.co.z for v in ob.data.vertices)})
    # Horizontal labels are display-only; their exact locations identify each coupon.
    bpy.ops.object.text_add(location=(i*22+8,S['flange_width']+13,0));txt=bpy.context.object;txt.name='DISPLAY label';txt.data.body=f'{percent}%' ;txt.data.size=2.5;txt.data.materials.append(INK);tag(txt,'display_only')
H=dict(C['horn'])
write_stl(OUT/'horn-fit-coupons-ALL-THREE-PHOTO-ESTIMATE.stl',triangles_all)
bed=box('Print bed reference',(37,25,-1),(90,60,2),GREY);tag(bed,'reference_only')
studio(110,(37,25,0));scene.camera.location=(95,-60,120);scene.camera.rotation_euler=(Vector((37,25,0))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'horn-fit-coupons-print-layout-PROVISIONAL.blend'))
scene.render.filepath=str(OUT/'horn-fit-coupons-print-layout.png');bpy.ops.render.render(write_still=True)
report={'status':'PHOTO-ESTIMATED: tapered double-arm identified; precise dimensions, depth and hole layout unconfirmed','config':C,'checks':REPORT,'coupons':coupons,'production_paddle_stls_exported':False,'baseline_contact_plane_preserved_mm':13,'source_config_sha256':hashlib.sha256((ROOT/C['baseline_source']).read_bytes()).hexdigest(),'limits':['Horn outline dimensions are estimated from a perspective photograph; thickness/depth remain provisional.','Actual seating face, underside boss, thickness and hole sizes need checking against the supplied horn.','Locating rim is not a snap-fit or torque-retaining substitute for screws.','Horn center screw and spline engagement remain the original servo parts.']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
