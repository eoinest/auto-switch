"""Three provisional XL63070 retention concepts. Intentionally exports no STL."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
BLUE=material('XL63070 PCB — photo approximation',(.015,.07,.21));SILVER=material('Solder pad',(.66,.68,.70),.75)
LABEL=material('Labels',(.05,.06,.08));ALT=material('Alternative concept',(.35,.39,.43))
W,L,T=C['pcb_mm'];bottom=C['pcb_underside_z'];top=bottom+T;floor=C['carrier_floor_z'];ft=C['adapter_floor_thickness'];hole=C['mount_hole_pitch_mm']/2
objects={}
def label(txt,x,y,size=2.5):
    bpy.ops.object.text_add(location=(x,y,0));o=bpy.context.object;o.name=txt;o.data.body=txt;o.data.size=size;o.data.align_x='CENTER';o.data.materials.append(LABEL);return o
def module(cx):
    obs=[]
    obs.append(box('PCB 16x30x1.2 — PROVISIONAL',(cx,0,bottom+T/2),(W,L,T),BLUE))
    for x in [-5.15,5.15]:
        for y in [-13.55,13.55]:obs.append(box('Corner solder pad — keep clear',(cx+x,y,top+.05),(5.25,2.9,.1),SILVER))
    obs.append(box('Inductor approximate',(cx-3.4,-2.2,top+1.8),(6.5,7.2,3.6),GREY))
    obs.append(box('Controller approximate',(cx+2,-3.1,top+.6),(3.2,3.7,1.2),BLACK))
    for y in [-8,-5,0,3,6,9]:
        obs.append(box('Right-edge parts — approximate',(cx+6.6,y,top+.35),(1.5,1.7,.7),GREY))
    for y in [2.7,5,7.2,9.4]:obs.append(box('Capacitors — approximate',(cx+.2,y,top+.45),(3.8,1.1,.9),GOLD))
    obs.append(box('Input capacitor — approximate',(cx-.1,-10.2,top+1),(4.1,2.4,2),GOLD))
    for o in obs:o['role']='REFERENCE ONLY; photo reconstruction, not exact component geometry'
    return obs

def adapter(cx,tag):
    p=box(tag+' compact open adapter',(cx,0,floor+ft/2),(20,36,ft),TEAL)
    cut(p,(cx,0,floor+ft/2),(12,23,ft+2))
    for y in [-hole,hole]:
        boolean(p,box('Mount ear',(cx,y,floor+ft/2),(12,12,ft),TEAL),'UNION')
    # Support only short sections of substrate edges. Underside and solder-pad zones open.
    for sign in [-1,1]:
        for y in [-7,7]:boolean(p,box('Sparse underside edge support',(cx+sign*(W/2-.5),y,(floor+ft-.1+bottom)/2),(1,5,bottom-floor-ft+.1),TEAL),'UNION')
    return p

def screw(cx,y,z,name='Existing M3 mounting point'):
    return fuse([cyl('head',(cx,y,z+1.5),2.75,3,mat=GREY),cyl('shaft',(cx,y,z-C['mount_screw_length_mm']/2),1.5,C['mount_screw_length_mm'],mat=GREY)],'M3x16 mounting screw — provisional stack',GREY)

def end_toes(cx):
    p=adapter(cx,'C')
    # Low side guides contact only the cut substrate edge, never the populated top face.
    for sign in [-1,1]:
        for y in [-7,7]:boolean(p,box('Low substrate side guide',(cx+sign*(W/2+C['side_clearance_mm']+.6),y,(floor+ft-.1+bottom+T*.6)/2),(1.2,5,bottom+T*.6-floor-ft+.1),TEAL),'UNION')
    toes=[]
    # Short center-only end stops constrain length without blocking corner terminals.
    for sign in [-1,1]:boolean(p,box('Between-pad substrate end stop',(cx,sign*(L/2+.8),(floor+ft-.1+bottom+.6*T)/2),(C['toe_width_mm'],1.2,bottom+.6*T-floor-ft+.1),TEAL),'UNION')
    seatshim=C['seat_height_shim_mm']
    for sign in [-1,1]:boolean(p,box('End toe underside support',(cx,sign*(L/2-C['end_support_depth_mm']/2),(floor+ft-.1+bottom)/2),(C['toe_width_mm'],C['end_support_depth_mm'],bottom-floor-ft+.1),TEAL),'UNION')
    for sign in [-1,1]:
        # Integral shoulder provides a positive screw stop below a replaceable height shim.
        shoulder=box('C clamp hard seat',(cx,sign*hole,(floor+ft-.1+top-seatshim)/2),(7.8,11,top-seatshim-floor-ft+.1),TEAL);boolean(p,shoulder,'UNION');drill(p,(cx,sign*hole,top),1.7,12)
        shim=box('C 0.4 mm seat-height shim',(cx,sign*hole,top-seatshim/2),(7.8,11,seatshim),GOLD);drill(shim,(cx,sign*hole,top),1.7,5)
        # Key walls keep toe from twisting when one screw is tightened.
        for side in [-1,1]:boolean(p,box('C anti-rotation guide',(cx+side*5,sign*hole,(floor+ft-.1+top+1.5)/2),(1.4,11,top+1.5-floor-ft+.1),TEAL),'UNION')
        foot=box('C slotted clamp foot',(cx,sign*hole,top+1),(8.2,10,2),ORANGE)
        inner=L/2-C['toe_overlap_mm'];outer=hole-4.5
        toe=box('C narrow bare-end tongue',(cx,sign*(inner+outer)/2,top+1),(C['toe_width_mm'],outer-inner,2),ORANGE)
        j=fuse([foot,toe],'C end-center retaining finger',ORANGE)
        cut(j,(cx,sign*hole,top+1),(3.4,2,6));drill(j,(cx,sign*hole-1,top+1),1.7,6);drill(j,(cx,sign*hole+1,top+1),1.7,6)
        screw(cx,sign*hole,top+2,'M3x16 mounting screw')
        toes.extend([j,shim])
    objects['C']=[p]+toes+module(cx)
    label('C  NARROW END FINGERS',cx,35);label('Recommended: clear corner pads + low guides',cx,-37,1.65)
    return p,toes
import hashlib
adapter_part,loose=end_toes(0)
# Every physical part has its own export even when its dimensions are shared.
printables=[adapter_part,loose[0],loose[2],loose[1],loose[3]]
names=['01_adapter','02_lower_end_finger','03_upper_end_finger','04_lower_height_shim_0p4','05_upper_height_shim_0p4']
for o,n in zip(printables,names):o.name=n+' — FIT-TEST';o['role']='PRINTABLE FIT-TEST';o['fit_status']=C['status']
for yy in [-hole,hole]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=5.5/math.sqrt(3),depth=2.4,location=(0,yy,-1.2));nut=bpy.context.object;nut.name='M3 nut under existing carrier';nut.data.materials.append(GREY);drill(nut,(0,yy,-1.2),1.5,5)
# Small existing-carrier reference is excluded from every export.
carrier_ref=box('Existing carrier surface — reference only',(0,0,1.5),(32,64,3),WHITE)
for yy in [-hole,hole]:drill(carrier_ref,(0,yy,1.5),1.7,7)
for ob in list(scene.objects):
    if ob.type=='FONT':bpy.data.objects.remove(ob,do_unlink=True)

def audit(o):
    bpy.context.view_layer.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);remain=set(bm.verts);cc=0
    while remain:
        cc+=1;stack=[remain.pop()]
        while stack:
            for e in stack.pop().link_edges:
                for v in e.verts:
                    if v in remain:remain.remove(v);stack.append(v)
    assert bad==0 and cc==1 and vol>0,(o.name,bad,cc,vol)
    bm.to_mesh(o.data);bm.free();return dict(name=o.name,non_manifold_edges=bad,connected_components=cc,volume_mm3=vol)
reports=[audit(o) for o in printables]
def setup(scale,target):
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
    for loc in [(70,-90,160),(-90,30,120)]:
        bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=110000;ob.data.size=120;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=Vector(target)+Vector((55,-80,100)));camera=bpy.context.object;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=scale;scene.camera=camera
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
setup(80,(0,0,5));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'booster-retention-v1-assembly-FIT-TEST.blend'));scene.render.filepath=str(OUT/'booster-retention-v1-assembly-FIT-TEST.png');bpy.ops.render.render(write_still=True)
for ob in list(scene.objects):
    if ob not in printables:bpy.data.objects.remove(ob,do_unlink=True)
STL=OUT/'stl-fit-test';STL.mkdir(exist_ok=True)
# These are flat extrusions/vertical shoulders. No part needs an upside-down bridge.
placements=[(5,5),(31,5),(45,5),(31,28),(45,28)]
all_tri=[];manifest=[]
def write(path,tris):
    with path.open('wb') as f:
        f.write(b'auto-switch BOOSTER FIT-TEST; mm; unmeasured 16x30x1.2 PCB'.ljust(80,b' '));f.write(struct.pack('<I',len(tris)))
        for a,b,c in tris:f.write(struct.pack('<12fH',*((b-a).cross(c-a).normalized()),*a,*b,*c,0))
for o,name,xy,report in zip(printables,names,placements,reports):
    bpy.context.view_layer.update();o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4)
    lo=Vector([min(v.co[k] for v in o.data.vertices) for k in range(3)]);hi=Vector([max(v.co[k] for v in o.data.vertices) for k in range(3)])
    o.data.transform(Matrix.Translation(Vector((-lo.x+xy[0],-lo.y+xy[1],-lo.z))));o.data.update()
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    tris=[[o.data.vertices[i].co.copy() for i in f.vertices] for f in o.data.polygons]
    f=name+'-FIT-TEST.stl';write(STL/f,tris);all_tri.extend(tris)
    report.update(file='stl-fit-test/'+f,quantity=1,dimensions_mm=list(hi-lo),print_min_z=0);manifest.append(report)
write(OUT/'booster-retention-v1-ALL-FIVE-FIT-TEST.stl',all_tri)
report={'status':C['status'],'config':C,'parts':manifest,'master':'booster-retention-v1-ALL-FIVE-FIT-TEST.stl','hardware':'2 M3x16 screws + 2 ordinary M3 nuts; provisional16mm stack, measured fit still required','screw_underhead_z':top+2,'screw_tip_z':top+2-C['mount_screw_length_mm'],'nut_bottom_z':-2.4,'existing_carrier_holes_world_xy':[[22,22],[22,68]],'pcb_support_z':bottom,'pcb_top_and_toe_bottom_z':top,'fixed_seat_z':top-C['seat_height_shim_mm'],'shim_thickness':C['seat_height_shim_mm'],'no_stl_reference_objects':True,'limits':['Board16x30x1.2 is assumed, not measured.','End-center2.8x0.6 contact patches and underside support zones remain unverified.','Print and dry-fit unpowered; do not force or bend PCB.','This export is a fit test, not production approval.']}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
box('Print bed reference',(35,36,-1),(76,78,2),GREY);setup(100,(30,32,0));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'booster-retention-v1-print-layout-FIT-TEST.blend'));scene.render.filepath=str(OUT/'booster-retention-v1-print-layout-FIT-TEST.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
