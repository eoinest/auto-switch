"""Blender-only parametric prototype. One Blender unit = one millimetre.
Run: blender --background --factory-startup --python hardware/cad/generate.py
No addons or external Python packages needed. See docs/mechanics.md.
"""
import bpy, bmesh, json, math, struct
from pathlib import Path
from mathutils import Vector, Matrix
ROOT = Path(__file__).resolve().parent
C = json.loads((ROOT / 'config.json').read_text())
OUT = ROOT / 'generated'
OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=.001
scene.unit_settings.length_unit='MILLIMETERS'
REPORT=[]

def material(name, rgb, metallic=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*rgb,1); p.inputs['Metallic'].default_value=metallic
    p.inputs['Roughness'].default_value=.45
    return m
TEAL=material('PETG • ocean blue',(.035,.30,.37)); ORANGE=material('PETG • moving yoke',(.96,.36,.08))
WHITE=material('Existing wallplate • reference only',(.8,.81,.76)); GREY=material('Servo • reference only',(.22,.23,.24),.5)
GREEN=material('Pico • reference envelope',(.08,.38,.15)); BLACK=material('Battery holder • reference envelope',(.07,.08,.095))
RED=material('Silicone pad • add separately',(.85,.13,.12)); GOLD=material('Stock servo horn • reference',(.7,.57,.23),.6)

def box(name, loc, size, mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name
    o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if mat:o.data.materials.append(mat)
    return o

def cyl(name, loc, radius, depth, axis='Z', mat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name
    if axis=='X':o.rotation_euler[1]=math.pi/2
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    if mat:o.data.materials.append(mat)
    return o

def boolean(a,b,op):
    bpy.context.view_layer.objects.active=a
    m=a.modifiers.new(op,'BOOLEAN');m.operation=op;m.solver='EXACT';m.object=b
    bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(b,do_unlink=True)
    return a

def fuse(parts,name,mat):
    a=parts[0]
    for b in parts[1:]:boolean(a,b,'UNION')
    a.name=name;a.data.materials.clear();a.data.materials.append(mat)
    return a

def cut(a,loc,size):return boolean(a,box('cut',loc,size),'DIFFERENCE')
def drill(a,loc,r,depth,axis='Z'):return boolean(a,cyl('drill',loc,r,depth,axis),'DIFFERENCE')

def export(o,name,rotate=False):
    # Export each printable in mm, centred XY, on bed Z=0. Independently validate topology.
    mesh=o.data.copy(); bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
    bm.to_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bad=sum(not e.is_manifold for e in bm.edges)
    vol=bm.calc_volume(signed=True)
    visited=set(); components=0
    for v in bm.verts:
        if v in visited:continue
        components+=1;todo=[v];visited.add(v)
        while todo:
            u=todo.pop()
            for e in u.link_edges:
                w=e.other_vert(u)
                if w not in visited:visited.add(w);todo.append(w)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    rot=Matrix.Rotation(math.pi/2,4,'Y') if rotate else Matrix.Identity(4)
    pts=[rot @ (o.matrix_world @ v.co) for v in mesh.vertices]
    lo=Vector([min(p[i] for p in pts) for i in range(3)]); hi=Vector([max(p[i] for p in pts) for i in range(3)])
    offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));pts=[p-offset for p in pts]
    with (OUT/(name+'.stl')).open('wb') as f:
        f.write(b'auto-switch; mm; provisional dimensions'.ljust(80,b' '));f.write(struct.pack('<I',len(mesh.polygons)))
        for face in mesh.polygons:
            a,b,c=[pts[i] for i in face.vertices];n=(b-a).cross(c-a).normalized()
            f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
    REPORT.append(dict(file=name+'.stl',dimensions_mm=[round(x,3) for x in hi-lo],non_manifold_edges=bad,connected_components=components,volume_mm3=round(vol,2),triangles=len(mesh.polygons)))
    if bad or components!=1 or vol<=0:raise RuntimeError('Invalid printable '+name+': '+str(REPORT[-1]))
    bpy.data.meshes.remove(mesh)

def ring(g,cx,height=9):
    w=C['plate_widths'][str(g)]+2*C['plate_clearance_per_side'];h=C['plate_height']+2*C['plate_clearance_per_side'];t=C['frame_wall']
    o=box('ring',(cx,0,height/2),(w+2*t,h+2*t,height),TEAL)
    cut(o,(cx,0,height/2),(w,h,height+4));return o,w,h

def build(g,cx):
    start=set(bpy.data.objects)
    frame,w,h=ring(g,cx,C['skirt_depth']);parts=[frame]
    # Broad wall adhesive pads; skirt is clearance, not a hidden undercut snap.
    for sign in (-1,1):
        parts.append(box('adhesive landing',(cx+sign*(w/2+10),0,1.5),(20,78,3)))
    pw=C['pod_internal_width'];ph=C['pod_internal_height'];pd=C['pod_internal_depth'];py=h/2+ph/2
    pod=box('pod',(cx,py,(pd+4)/2),(pw+4,ph+4,pd+4))
    cut(pod,(cx,py,25),(pw,ph,42)) # floor top=4, open top
    # Wire port towards switch, above wallplate.
    cut(pod,(cx,py-ph/2,15),(18,8,8))
    for sx in (-1,1):
        for sy in (-1,1):
            p=(cx+sx*(pw/2-3.5),py+sy*(ph/2-3.5),20)
            boolean(pod,cyl('lid boss',p,3.8,36),'UNION');drill(pod,(p[0],p[1],34),1.25,12)
    # Header clearance under Pico, held with two cable ties rather than guessed screw pattern.
    for sx in (-18,18):
        boolean(pod,box('Pico riser',(cx+sx,py+46.5,8),(5,24,10)),'UNION')
    for sx in (-24,24):
        for yy in (py-32,py+7,py+30,py+56):cut(pod,(cx+sx,yy,3),(4,2.8,10))
    parts.append(pod)
    # Top pod and outer ring overlap 2 mm; stress flows into wall pads.
    centres=[cx] if g==1 else [cx-C['gang_spacing']/2,cx+C['gang_spacing']/2]
    for i,xc in enumerate(centres):
        sign=1 if g==1 or i==1 else -1
        # Output axis X; pods face outward so two servos never share a paddle's space.
        bodyx=xc+sign*29;by=-C['servo_axis_offset_y'];pz=C['pivot_z']
        railx=cx+sign*(w/2+1.5)
        support=box('servo pedestal',((bodyx+railx)/2,by,14.25),(abs(bodyx-railx)+12,30,14))
        parts.append(support)
        # Cradle floor z=23.9. MG90S face width=12.2 along Z.
        parts.append(box('servo floor',(bodyx,by,22.55),(30,32.8,2.7)))
        for dy in (-15,15):parts.append(box('cradle side rail',(bodyx,by+dy,26.2),(30,2,7)))
        # References do not get exported; use ties in four floor/pedestal through-slots.
        servo=box('REFERENCE MG90S '+str(g)+'g '+str(i),(bodyx,by,pz),C['servo_body'],GREY)
        cyl('REFERENCE output spline',(xc+sign*15,0,pz),2.5,6,'X',GOLD)
        # Use supplied double-arm horn between shaft and printed hub plate.
        horn=box('REFERENCE supplied horn',(xc+sign*12,0,pz),(2,22,5),GOLD)
        hubx=xc+sign*9
        yoke=fuse([box('yoke beam',(xc,0,pz),(8,58,6)),box('hub bridge',(xc+sign*4,0,pz),(12,12,6)),box('horn flange',(hubx,0,pz),(4,23,14)),*[box('pad post',(xc,dy,pz-9),(8,8,12.2)) for dy in (-C['pad_radius'],C['pad_radius'])]],'PRINT yoke '+str(g)+'g '+str(i),ORANGE)
        drill(yoke,(hubx,0,pz),2.2,30,'X')
        for yy in (-C['horn_fastener_radius'],C['horn_fastener_radius']):drill(yoke,(hubx,yy,pz),1.1,10,'X')
        export(yoke,f'{g}g_yoke_{i+1}',rotate=True)
        for obj in (yoke,horn):
            for frame,angle in [(1,0),(25,10),(40,0),(65,-10),(80,0),(100,0)]:
                obj.rotation_euler[0]=math.radians(angle);obj.keyframe_insert(data_path='rotation_euler',frame=frame)
            obj.rotation_euler[0]=0
        for yy in (-C['pad_radius'],C['pad_radius']):
            pad=box('REFERENCE 2 mm silicone contact',(xc,yy,pz-16),(8,8,2),RED)
            pad.parent=yoke;pad.matrix_parent_inverse=yoke.matrix_world.inverted()
        box('REFERENCE existing rocker',(xc,0,8),(C['rocker_width'],C['rocker_height'],4),WHITE)
    chassis=fuse(parts,'PRINT chassis '+str(g)+'g',TEAL)
    for i,xc in enumerate(centres):
        sign=1 if g==1 or i==1 else -1;bodyx=xc+sign*29;by=-C['servo_axis_offset_y']
        for xx in (-8,8):
            for yy in (-12.8,12.8):cut(chassis,(bodyx+xx,by+yy,12),(3.5,2.8,30))
    export(chassis,f'{g}g_chassis')
    lid=box('PRINT electronics lid '+str(g)+'g',(cx,py,pd+5.5),(pw+4,ph+4,3),TEAL)
    for sx in (-1,1):
        for sy in (-1,1):drill(lid,(cx+sx*(pw/2-3.5),py+sy*(ph/2-3.5),pd+5.5),1.65,10)
    # Cable exit and inspection vents.
    for xx in (-24,-12,0,12,24):cut(lid,(cx+xx,py+30,pd+5.5),(3,14,8))
    export(lid,f'{g}g_electronics_lid');lid.hide_render=True;lid.hide_set(True)
    ref=box('REFERENCE existing wallplate '+str(g)+'g',(cx,0,3),(C['plate_widths'][str(g)],C['plate_height'],6),WHITE)
    # Simplified commercially bought holder and board envelopes; no printable electrical contacts.
    box('REFERENCE 4AA holder envelope 64x60x22',(cx,py-20,15),(64,60,22),BLACK)
    box('REFERENCE power board envelope 43x21x10',(cx,py+23,11),(43,21,10),GREEN)
    box('REFERENCE Pico with headers 51x21x18',(cx,py+46.5,22),(51,21,18),GREEN)
    # Fit-only thin surround at separate preview location.
    fit,_,_=ring(g,cx,2);fit.name='PRINT fit ring '+str(g)+'g';export(fit,f'{g}g_fit_ring');fit.hide_render=True;fit.hide_set(True)
    col=bpy.data.collections.new(f'{g}-gang prototype');scene.collection.children.link(col)
    for o in set(bpy.data.objects)-start:
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o)
    return chassis

build(1,-110);build(2,110)
scene.frame_end=100;scene.frame_set(1)
# Labelled scene, dimensions remain editable in config. Text is never in STL.
for x,t in [(-110,'ONE GANG'),(110,'TWO GANG')]:
    bpy.ops.object.text_add(location=(x-38,-78,1));o=bpy.context.object;o.name='Label '+t;o.data.body=t;o.data.size=7;o.data.extrude=.1;o.data.materials.append(WHITE)
# Orthographic front-oblique inspection view.
bpy.ops.object.camera_add(location=(280,-350,600));camera=bpy.context.object
camera.rotation_euler=(Vector((0,35,5))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=520;scene.camera=camera
for loc,power,size in [((0,-100,400),1500000,300),((-300,180,250),1000000,250),((300,150,200),800000,200)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,40,0))-o.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.18,.18,.18);scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1600;scene.render.resolution_y=1250;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
# Pleasant solid viewport defaults; frame both assemblies on opening.
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.shading.color_type='MATERIAL'
        area.spaces.active.region_3d.view_distance=430
        area.spaces.active.region_3d.view_location=(0,35,10)
        area.spaces.active.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
(OUT/'validation.json').write_text(json.dumps({'configuration':C,'parts':REPORT,'limits':'Topology/dimensions checked digitally. Fit, torque, clearance through motion and adhesion require physical validation.'},indent=2)+'\n')
scene.render.filepath=str(OUT/'assembly.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'auto-switch.blend'))
bpy.ops.render.render(write_still=True)
print('CAD_COMPLETE',json.dumps(REPORT))
