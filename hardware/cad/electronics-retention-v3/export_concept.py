"""Export only the six printed objects from the reviewed v3 assembly, in mm.
No component fit approval is implied; do not export references or exploded copies.
"""
import bpy,bmesh,math,struct,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'generated/electronics-retention-v3.blend'
OUT=ROOT/'generated/stl-concept';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
collection=bpy.data.collections['V3 ASSEMBLED — FIT UNVERIFIED']
objects=sorted([o for o in collection.objects if o.get('part_type')=='PRINTED CONCEPT'],key=lambda o:o.name)
assert len(objects)==6,[o.name for o in objects]
files=['01_carrier_base_CONCEPT.stl','02_battery_bar_1_CONCEPT.stl','03_battery_bar_2_CONCEPT.stl','04_converter_floor_CONCEPT.stl','05_converter_jaw_left_CONCEPT.stl','06_converter_jaw_right_CONCEPT.stl']
parts=[]
for o,filename in zip(objects,files):
    mesh=o.data.copy();bm=bmesh.new();bm.from_mesh(mesh)
    # Remove sub-micron Boolean slivers before float32 STL encoding.
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.0001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.0001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges),o.name
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    rotation=Matrix.Rotation(math.pi/2,4,'X') if 'jaw' in filename else Matrix.Identity(4)
    points=[rotation@(o.matrix_world@v.co) for v in mesh.vertices]
    low=Vector([min(p[i] for p in points) for i in range(3)])
    high=Vector([max(p[i] for p in points) for i in range(3)])
    offset=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
    points=[p-offset for p in points]
    assert all(0<d<=256 for d in high-low),(o.name,list(high-low))
    with (OUT/filename).open('wb') as f:
        f.write(b'auto-switch v3 CONCEPT ONLY; millimetres; physical fit unverified'.ljust(80,b' '))
        f.write(struct.pack('<I',len(mesh.polygons)))
        for poly in mesh.polygons:
            a,b,c=[points[i] for i in poly.vertices]
            n=(b-a).cross(c-a).normalized()
            f.write(struct.pack('<12fH',*n,*a,*b,*c,0))
    parts.append({'file':filename,'source_object':o.name,'dimensions_mm':[round(d,4) for d in high-low],'triangles':len(mesh.polygons),'rotation_x_degrees':90 if 'jaw' in filename else 0,'sha256':hashlib.sha256((OUT/filename).read_bytes()).hexdigest()})
    bpy.data.meshes.remove(mesh)
report={'status':'User-requested concept STL export; physical fit UNVERIFIED','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'units':'mm','parts':parts,'excludes':'All hardware/component references and exploded duplicates','supports':'Base feet-down requires supports below the raised floor; jaws lie on their side and may need support under 1 mm recessed faces. Inspect slicer preview.','fit_blocker':'Converter dimensions and edge lands, S2 underside, battery projections remain unverified.'}
(OUT/'export-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
