"""V6 simple one-bar battery preview, preserving the printed V4 carrier.
Blender only. All coordinates millimetres. Preview STL is just the new crossbar.
"""
import sys, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
from mathutils.bvhtree import BVHTree

def ref(o):o['role']='reference_only';return o
def worldtree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
def overlaps(a,b):return bool(worldtree(a).overlap(worldtree(b)))
with bpy.data.libraries.load(str(ROOT/C['reuse_carrier']),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('01 carrier base') and 'bed' not in n]
assert len(dst.objects)==1
carrier=dst.objects[0];scene.collection.objects.link(carrier);ref(carrier);carrier.name='EXISTING V4 CARRIER — upper towers reused, lower pair unused'
hx,hy=C['holder_center_xy'];body_w,body_d,body_h=C['holder_body_mm'];base=C['base_top_z'];body_top=base+body_h
holder=ref(box('AA body — nominal19mm thickness',(hx,hy,base+body_h/2),C['holder_body_mm'],BLACK))
bev=holder.modifiers.new('Approximate molded corners','BEVEL');bev.width=.8;bev.segments=3;bpy.context.view_layer.objects.active=holder;bpy.ops.object.modifier_apply(modifier=bev.name)
ref(box('Approximate case cover seam',(hx,hy,base+5),(body_w+.1,body_d+.1,.18),GREY))
sx,sy=C['switch_center_xy']
ref(box('Switch recess — photo estimated',(sx,sy,body_top+.05),(3.882,8.999,.2),GREY))
ref(box('Switch protrusion — peak25.5',(sx,sy-1.8,body_top+C['switch_peak_above_body_mm']/2),(3.2,4.1,C['switch_peak_above_body_mm']),BLACK))
switch_window=ref(box('Switch finger access window',(sx,sy,31),(18,22,18),RED));switch_window.hide_render=True;switch_window.hide_set(True)
wire_window=ref(box('Illustrative wire corridor',(43,-2,17),(21,5,10),RED));wire_window.hide_render=True;wire_window.hide_set(True)
for yy,color in [(-1,RED),(-2.5,BLACK)]:ref(cyl('Insulated lead illustration',(42,yy,16),.65,17,'X',color))

# Flat front face gives a continuous print-bed surface. Center land fills the former4mm gap.
z=body_top+C['nominal_body_clearance_mm'];tower=C['support_tower_top_z'];bar_w,bar_d,bar_t=C['bar_mm'];front=tower+bar_t
bar_x=sum(v[0] for v in C['support_tower_centers_xy'])/2;bar_y=C['support_tower_centers_xy'][0][1]
assert all(y==bar_y for x,y in C['support_tower_centers_xy']), 'Tower pair must share Y'
assert z<tower, 'Contact land must be below tower seats'
bar=fuse([box('flat crossbar',(bar_x,bar_y,(tower+front)/2),(bar_w,bar_d,bar_t)),box('integral center contact land',(bar_x,bar_y,(z+tower+.2)/2),(C['contact_land_width_mm'],bar_d,tower+.2-z))],'V6 SINGLE BATTERY CROSSBAR — PREVIEW',ORANGE)
bar['role']='preview_print'
for x,y in C['support_tower_centers_xy']:
    drill(bar,(x,y,tower),C['mount_hole_diameter_mm']/2,14)
    ref(fuse([cyl('screw shank',(x,y,front-35/2),1.5,35),cyl('screw head',(x,y,front+1.5),2.75,3)],'REUSE M3x35 mounting screw',GREY))
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=5.5/math.sqrt(3),depth=2.4,location=(x,y,-1.2));nut=bpy.context.object;nut.name='REUSE ordinary M3 nut';nut.data.materials.append(GREY);drill(nut,(x,y,-1.2),1.5,4);ref(nut)
assert not overlaps(bar,holder),'Crossbar intersects nominalcase'
assert not overlaps(bar,switch_window),'Crossbar blocks switchaccess'
assert not overlaps(bar,wire_window),'Crossbar blocks wirecorridor'

bm=bmesh.new();bm.from_mesh(bar.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
remain=set(bm.verts);components=0
while remain:
    components+=1;stack=[remain.pop()]
    while stack:
        for e in stack.pop().link_edges:
            for vv in e.verts:
                if vv in remain:remain.remove(vv);stack.append(vv)
assert bad==0 and volume>0 and components==1,(bad,volume,components)
bm.to_mesh(bar.data);bm.free()

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
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'battery-retention-v6-assembly-PREVIEW.blend'))
scene.render.filepath=str(OUT/'battery-retention-v6-assembly.png');bpy.ops.render.render(write_still=True)

# Export only the new one-piece bar, flat-front-down. Original carrier is excluded.
for ob in list(scene.objects):
    if ob!=bar:bpy.data.objects.remove(ob,do_unlink=True)
bar.data.transform(Matrix.Rotation(math.pi,4,'X')@bar.matrix_world);bar.matrix_world=Matrix.Identity(4)
lo=Vector([min(v.co[k] for v in bar.data.vertices) for k in range(3)]);hi=Vector([max(v.co[k] for v in bar.data.vertices) for k in range(3)])
bar.data.transform(Matrix.Translation(Vector((-((lo.x+hi.x)/2),-((lo.y+hi.y)/2),-lo.z))));bar.data.update()
bm=bmesh.new();bm.from_mesh(bar.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(bar.data);bm.free()
filename='battery-retention-v6-SINGLE-CROSSBAR-PREVIEW.stl'
with (OUT/filename).open('wb') as f:
    f.write(b'auto-switch v6 ONE BAR PREVIEW; mm; nominal19mm case; fit unconfirmed'.ljust(80,b' '));f.write(struct.pack('<I',len(bar.data.polygons)))
    for face in bar.data.polygons:
        a,b,c=[bar.data.vertices[i].co for i in face.vertices];normal=(b-a).cross(c-a).normalized();f.write(struct.pack('<12fH',*normal,*a,*b,*c,0))
report={'status':C['status'],'config':C,'preview_stl':filename,'dimensions_mm':list(hi-lo),'non_manifold_edges':bad,'connected_components':components,'volume_mm3':volume,'nominal_body_clearance_mm':C['nominal_body_clearance_mm'],'case_top_z_mm':body_top,'contact_land_bottom_z_mm':z,'tower_heights_equal':True,'support_top_z_mm':[tower,tower],'switch_access_surface_collisions':0,'wire_corridor_surface_collisions':0,'case_surface_collisions':0,'carrier_modified':False,'carrier_source_sha256':hashlib.sha256((ROOT/C['reuse_carrier']).read_bytes()).hexdigest(),'limits':['Body19mm is seller nominal, not exact physical measurement.','Nominal0.2mmclearance may still permit slight vertical movement.','This single bar does not remove lateral cradle clearance; existingV5 shims are optional.','Existing lower tower pair remains unused.','Wire exit height and moldedcorner fit remain physical checks.']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
bed=ref(box('Print bed reference',(0,0,-1),(125,40,2),GREY))
studio(140,(0,0,0))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'battery-retention-v6-print-PREVIEW.blend'))
scene.render.filepath=str(OUT/'battery-retention-v6-print.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
