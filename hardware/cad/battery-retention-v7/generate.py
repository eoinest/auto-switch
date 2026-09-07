"""V7: new carrier with only two centered towers and a separate flat bar. Units mm."""
import sys, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
def ref(o):o['role']='reference_only';return o
def bake(o):
    bpy.context.view_layer.update()
    o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4);o.data.update();return o
def bounds(o):
    ps=[o.matrix_world@v.co for v in o.data.vertices]
    return Vector([min(p[i] for p in ps) for i in range(3)]),Vector([max(p[i] for p in ps) for i in range(3)])
def audit(o):
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);remain=set(bm.verts);cc=0
    while remain:
        cc+=1;stack=[remain.pop()]
        while stack:
            for e in stack.pop().link_edges:
                for v in e.verts:
                    if v in remain:remain.remove(v);stack.append(v)
    assert bad==0 and cc==1 and vol>0,(o.name,bad,cc,vol)
    bm.to_mesh(o.data);bm.free();return {'name':o.name,'non_manifold_edges':bad,'components':cc,'volume_mm3':vol}
def intersection_volume(a,b):
    q=a.copy();q.data=a.data.copy();scene.collection.objects.link(q);r=b.copy();r.data=b.data.copy();scene.collection.objects.link(r);boolean(q,r,'INTERSECT');bm=bmesh.new();bm.from_mesh(q.data);vol=abs(bm.calc_volume());bm.free();bpy.data.objects.remove(q,do_unlink=True);return vol
# Rebuild the exact V4 carrier features instead of Boolean-patching through-hole seams.
# Dimensions below are copied from V4 config/generate.py; only battery towers change.
source_config=json.loads((ROOT/'../electronics-retention-v4/config.json').read_text())
base=C['base_top_z'];hx,hy=C['holder_center_xy'];bw,bd,bh=C['holder_body_mm'];top=base+bh
carrier=box('V7 NEW CARRIER — ONLY TWO CENTERED TOWERS',(0,0,base/2),(120,160,base),TEAL);carrier['role']='print'
iw,ih=source_config['holder_cradle_inner_mm']
for x in [-(iw/2+1.5),iw/2+1.5]:boolean(carrier,box('Preserved cradle X wall',(x,hy,7),(3,ih+6,8),TEAL),'UNION')
for y in [hy-(ih/2+1.5),hy+(ih/2+1.5)]:boolean(carrier,box('Preserved cradle Y wall',(0,y,7),(iw,3,8),TEAL),'UNION')
cut(carrier,(0,hy-ih/2-1.5,8),(14,5,8))
for x in [-40.2,-19.8]:
    boolean(carrier,cyl('Preserved S2 standoff',(x,47-34.3/2+3.3,6.5),2,7,mat=TEAL),'UNION')
    drill(carrier,(x,47-34.3/2+3.3,6),.9,22)
for x in [-41.5,-18.5]:boolean(carrier,box('Preserved S2 USB support',(x,61,6.5),(2.4,3,7),TEAL),'UNION')
for y in [22,68]:drill(carrier,(22,y,1.5),1.7,8)
for x in [-6,50]:
    cut(carrier,(x,45,1.5),(6,3.4,8));drill(carrier,(x-3,45,1.5),1.7,8);drill(carrier,(x+3,45,1.5),1.7,8)
for x in [-53,53]:
    for y in [-65,65]:drill(carrier,(x,y,1.5),1.7,8)
for x,y in C['post_centers_xy']:
    boolean(carrier,box('Centered case-height tower',(x,y,(base+top)/2-.05),(*C['post_footprint_mm'],top-base+.1),TEAL),'UNION')
    drill(carrier,(x,y,top/2),C['mount_hole_diameter_mm']/2,top+4)
barw,bard,bart=C['bar_mm'];bar=box('V7 FLAT BATTERY CROSSBAR',(hx,hy,top+bart/2),(barw,bard,bart),ORANGE);bar['role']='print'
for x,y in C['post_centers_xy']:
    drill(bar,(x,y,top+bart/2),C['mount_hole_diameter_mm']/2,bart+4)
    length=C['mount_screw_length_mm'];head=top+bart
    ref(fuse([cyl('shaft',(x,y,head-length/2),1.5,length),cyl('head',(x,y,head+1.5),2.75,3)],'M3x30 battery mounting screw',GREY))
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=5.5/math.sqrt(3),depth=2.4,location=(x,y,-1.2));nut=bpy.context.object;nut.name='Ordinary M3 nut';nut.data.materials.append(GREY);drill(nut,(x,y,-1.2),1.5,4);ref(nut)
holder=ref(box('AA case body — seller nominal 19 mm',(hx,hy,base+bh/2),C['holder_body_mm'],BLACK));bev=holder.modifiers.new('Approximate molded corners','BEVEL');bev.width=.8;bev.segments=3;bpy.context.view_layer.objects.active=holder;bpy.ops.object.modifier_apply(modifier=bev.name)
ref(box('Approximate cover seam',(hx,hy,base+5),(bw+.1,bd+.1,.18),GREY))
sx,sy=C['switch_center_xy'];projection=C['switch_peak_above_body_mm']
ref(box('Photo-estimated switch recess',(sx,sy,top+.05),(3.882,8.999,.2),GREY));ref(box('Switch slider',(sx,sy-1.8,top+projection/2),(3.2,4.1,projection),BLACK))
for yy,color in [(-1,RED),(-2.5,BLACK)]:ref(cyl('Illustrative insulated lead',(42,yy,16),.65,17,'X',color))
checks=[]
for x,y in C['old_post_centers_xy']:
    test=box('Old tower empty region',(x,y,15),(9.9,11.9,23.98));v=intersection_volume(carrier,test);checks.append({'old_tower_xy':[x,y],'remaining_above_base_mm3':v});bpy.data.objects.remove(test,do_unlink=True);assert v<.001,checks[-1]
assert intersection_volume(bar,holder)<.001
reports=[audit(carrier),audit(bar)]
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
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'battery-retention-v7-assembly.blend'))
scene.render.filepath=str(OUT/'battery-retention-v7-assembly.png');bpy.ops.render.render(write_still=True)
# Both parts already have broad flat rear faces; drop each to Z0, and separate on the bed.
for ob in list(scene.objects):
    if ob not in [carrier,bar]:bpy.data.objects.remove(ob,do_unlink=True)
all_tri=[]
for o,name,xy in [(carrier,'01_NEW-CARRIER-v7.stl',(5,5)),(bar,'02_FLAT-CROSSBAR-v7.stl',(5,175))]:
    bake(o);lo,hi=bounds(o);o.data.transform(Matrix.Translation(Vector((-lo.x+xy[0],-lo.y+xy[1],-lo.z))));o.data.update()
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    tris=[[o.data.vertices[i].co.copy() for i in f.vertices] for f in o.data.polygons]
    def write(path,triangles):
        with path.open('wb') as f:
            f.write(b'auto-switch v7; millimetres; nominal 19mm case, zero designed gap'.ljust(80,b' '));f.write(struct.pack('<I',len(triangles)))
            for a,b,c in triangles:f.write(struct.pack('<12fH',*((b-a).cross(c-a).normalized()),*a,*b,*c,0))
    write(OUT/name,tris);all_tri.extend(tris)
write(OUT/'battery-retention-v7-NEW-CARRIER-AND-BAR.stl',all_tri)
report={'status':C['status'],'config':C,'parts':reports,'old_tower_removal':checks,'new_tower_count':2,'tower_top_z_mm':top,'bar_bottom_z_mm':top,'bar_top_z_mm':top+bart,'designed_vertical_clearance_mm':0,'screw_tip_z_mm':top+bart-C['mount_screw_length_mm'],'print_master':'battery-retention-v7-NEW-CARRIER-AND-BAR.stl','print_bed_mm':[256,256],'layout_bounds_mm':[[5,5,0],[125,185,top]],'source_sha256':hashlib.sha256((ROOT/C['source_carrier']).read_bytes()).hexdigest(),'limits':['19 mm case thickness is seller nominal; physical case and printed fit must be checked.','Existing S2 and converter attachment geometry is preserved, not newly validated against actual parts.','Original side clearance remains; optional shims can address lateral play.']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
ref(box('A1 print bed reference',(128,128,-1),(256,256,2),GREY));studio(310,(110,108,0))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'battery-retention-v7-print-layout.blend'))
scene.render.filepath=str(OUT/'battery-retention-v7-print-layout.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
