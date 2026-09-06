"""Independent STL audit, standard library only; does not import CAD generator.

Tests exported triangles against source geometry-checks.json volumes. Physical hardware
and real connector/strap paths remain outside what a triangle audit can verify.
Run: python3 hardware/cad/electronics-retention-v3/verify_export_independent.py
"""
import collections
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'generated' / 'stl-concept'
C = json.loads((ROOT / 'config.json').read_text())
EPS = 1e-5


def subtract(a, b):
    return tuple(x-y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


class STL:
    def __init__(self, path):
        self.path = path
        self.data = path.read_bytes()
        count = struct.unpack_from('<I', self.data, 80)[0]
        assert len(self.data) == 84 + count*50, 'Invalid binary STL length'
        self.triangles = []
        self.faces = []
        self.vertices = []
        ids = {}
        edges = collections.defaultdict(list)
        volume = bed_area = unsupported_area = 0.0
        for i in range(count):
            values = struct.unpack_from('<12fH', self.data, 84+i*50)
            triangle = [tuple(values[j:j+3]) for j in (3, 6, 9)]
            assert all(math.isfinite(v) for p in triangle for v in p)
            self.triangles.append(triangle)
            face = []
            for point in triangle:
                key = tuple(round(v, 5) for v in point)
                if key not in ids:
                    ids[key] = len(self.vertices)
                    self.vertices.append(point)
                face.append(ids[key])
            assert len(set(face)) == 3, (self.path.name, 'Triangle vertices coincide at 0.00001 mm audit resolution')
            self.faces.append(face)
            a, b, c = triangle
            normal = cross(subtract(b, a), subtract(c, a))
            norm = math.sqrt(sum(v*v for v in normal))
            assert norm > 1e-9, 'Zero-area triangle'
            volume += sum(a[j]*normal[j] for j in range(3))/6
            if max(abs(v[2]) for v in triangle) < EPS:
                bed_area += norm/2
            if min(v[2] for v in triangle) > EPS and normal[2]/norm < -math.sqrt(.5):
                unsupported_area += norm/2
            for first, second in zip(face, face[1:]+face[:1]):
                edges[tuple(sorted((first, second)))].append((i, first, second))
        adjacency = [[] for _ in self.faces]
        for incidents in edges.values():
            assert len(incidents) == 2, (self.path.name, 'Non-manifold edge',len(incidents))
            a, b = incidents
            assert a[1] == b[2] and a[2] == b[1], 'Inconsistent winding'
            adjacency[a[0]].append(b[0]); adjacency[b[0]].append(a[0])
        seen = set(); components = []
        for i in range(count):
            if i in seen:
                continue
            pending = [i]; seen.add(i); total = 0
            while pending:
                j = pending.pop(); total += 1
                for k in adjacency[j]:
                    if k not in seen:
                        seen.add(k); pending.append(k)
            components.append(total)
        assert len(components) == 1, 'Disconnected printed solid'
        assert volume > 0
        self.bounds = [[min(v[j] for v in self.vertices), max(v[j] for v in self.vertices)] for j in range(3)]
        dimensions = [b-a for a, b in self.bounds]
        assert abs(self.bounds[2][0]) < EPS and all(0 < d <= 256 for d in dimensions)
        self.result = {
            'file': path.name, 'sha256': hashlib.sha256(self.data).hexdigest(),
            'triangles': count, 'connected_components': len(components),
            'closed_consistently_wound': True, 'zero_area_triangles': 0,
            'positive_volume_mm3': round(volume, 3),
            'dimensions_mm': [round(v, 4) for v in dimensions],
            'bed_z_mm': round(self.bounds[2][0], 6), 'fits_A1_256_mm': True,
            'bed_contact_area_mm2': round(bed_area, 3),
            'downfacing_area_over_45_degrees_above_bed_mm2': round(unsupported_area, 5),
        }

    def vertical_intersections(self, x, y):
        """Intersection Zs of actual triangles with a vertical line at (x,y)."""
        heights = []
        for a, b, c in self.triangles:
            den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
            if abs(den) < 1e-10:
                continue
            u = ((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
            v = ((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
            w = 1-u-v
            if min(u, v, w) >= -1e-7:
                z = u*a[2]+v*b[2]+w*c[2]
                if not any(abs(z-other) < EPS for other in heights):
                    heights.append(z)
        return sorted(heights)

    def top(self, x, y):
        values = self.vertical_intersections(x, y)
        return max(values) if values else None


files = sorted(OUT.glob('*.stl'))
assert len(files) == 6, ('Expected six separate concept STLs', len(files))
meshes = [STL(path) for path in files]
manifest = json.loads((OUT/'export-manifest.json').read_text())
expected = {part['file']: part['sha256'] for part in manifest['parts']}
assert expected == {mesh.path.name: mesh.result['sha256'] for mesh in meshes}, 'Export manifest hashes do not match audited STLs'
source = json.loads((ROOT/'generated'/'geometry-checks.json').read_text())
source_volumes = sorted(item['volume_mm3'] for item in source)
export_volumes = sorted(mesh.result['positive_volume_mm3'] for mesh in meshes)
assert len(source_volumes)==len(export_volumes)==6
for a,b in zip(source_volumes,export_volumes):
    assert abs(a-b)<.015, ('Source/export volume mismatch',a,b)
for mesh in meshes:
    levels = collections.defaultdict(float)
    for tri in mesh.triangles:
        a,b,c=tri
        normal=cross(subtract(b,a),subtract(c,a))
        norm=math.sqrt(sum(v*v for v in normal))
        if min(v[2] for v in tri)>EPS and normal[2]/norm < -math.sqrt(.5):
            levels[round(sum(p[2] for p in tri)/3,3)]+=norm/2
    mesh.result['downward_area_by_Z_mm']={str(z):round(area,3) for z,area in sorted(levels.items())}
    if mesh.result['downfacing_area_over_45_degrees_above_bed_mm2']>.01:
        mesh.result['slicer_support_review_required']=True
    else:
        mesh.result['slicer_support_review_required']=False
report={
    'status':'Exported concept mesh checks passed; actual hardware fit NOT verified',
    'physical_fit_verified':False,
    'export_manifest_hashes_match':True,
    'source_geometry_volume_multiset_matches_within_mm3':.015,
    'parts':[mesh.result for mesh in meshes],
    'limitations':[
        'Closed meshes and matched volumes do not prove no self-intersections, strength, printer tolerances or component fit.',
        'No slicer simulation or physical print was performed. Downward surface areas identify support concerns; slicer settings remain necessary.',
        'Converter dimensions, unobstructed PCB edge lands and actual adjustment fit remain unverified.',
        'Battery body/bar clearance and S2 mounting-hole placement/underside keepouts require measurements and dry fit.',
        'These six STLs contain only printed concept parts. Actual screws, nuts and electronic components are separate hardware.'
    ]
}
(OUT/'independent-stl-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
