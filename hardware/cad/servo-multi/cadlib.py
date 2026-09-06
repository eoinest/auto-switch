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
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.001)
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
