"""Export the six detachable printed pieces at their saved assembly transforms.

This is an assembly preview, not a fused or print-in-place model. For printing,
use electronics-wall-mount-all-pieces-CONCEPT.stl (the separated bed layout).
"""
import bpy
import bmesh
import hashlib
import itertools
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'generated/electronics-retention-v3.blend'
OUT = ROOT / 'generated/electronics-wall-mount-ASSEMBLED-CONCEPT.stl'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
collection = bpy.data.collections['V3 ASSEMBLED — FIT UNVERIFIED']
objects = sorted((o for o in collection.objects if o.get('part_type') == 'PRINTED CONCEPT'), key=lambda o: o.name)
assert len(objects) == 6
triangles = []
parts = []
for obj in objects:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), obj.name
    bm.transform(obj.matrix_world)
    volume = bm.calc_volume(signed=True)
    assert volume > 0
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    part_triangles = [[v.co.copy() for v in face.verts] for face in bm.faces]
    triangles.extend(part_triangles)
    parts.append({'object': obj.name, 'triangles': len(part_triangles), 'volume_mm3': volume,
                  'world_transform': [list(row) for row in obj.matrix_world],
                  'closed_manifold': True})
    bm.free()

# Intersection volume distinguishes overlapping solids from intended face contact.
overlaps = []
for first, second in itertools.combinations(objects, 2):
    temporary = first.copy()
    temporary.data = first.data.copy()
    bpy.context.scene.collection.objects.link(temporary)
    modifier = temporary.modifiers.new('assembly-intersection-audit', 'BOOLEAN')
    modifier.operation = 'INTERSECT'
    modifier.solver = 'EXACT'
    modifier.object = second
    evaluated = temporary.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.transform(temporary.matrix_world)
    volume = abs(bm.calc_volume(signed=True))
    overlaps.append({'first': first.name, 'second': second.name, 'intersection_volume_mm3': round(volume, 6)})
    bm.free()
    evaluated.to_mesh_clear()
    mesh_data = temporary.data
    bpy.data.objects.remove(temporary, do_unlink=True)
    bpy.data.meshes.remove(mesh_data)

with OUT.open('wb') as output:
    output.write(b'auto-switch ASSEMBLED CONCEPT; mm; preview only; NOT print-in-place'.ljust(80, b' '))
    output.write(struct.pack('<I', len(triangles)))
    for a, b, c in triangles:
        normal = (b-a).cross(c-a).normalized()
        output.write(struct.pack('<12fH', *normal, *a, *b, *c, 0))
bounds = [[min(p[i] for tri in triangles for p in tri), max(p[i] for tri in triangles for p in tri)] for i in range(3)]
report = {
    'file': OUT.name, 'units': 'mm', 'source': SOURCE.name,
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'parts': parts, 'bounds_mm': bounds, 'dimensions_mm': [b-a for a, b in bounds],
    'triangle_count': len(triangles), 'pairwise_intersection_checks': overlaps,
    'assembly_transforms_preserved': True, 'fused': False,
    'purpose': 'Assembled preview of six detachable pieces, NOT print-in-place. Face contacts may merge if a slicer repairs this assembly.',
    'print_layout_file': 'electronics-wall-mount-all-pieces-CONCEPT.stl',
    'physical_component_fit_verified': False,
}
OUT.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
