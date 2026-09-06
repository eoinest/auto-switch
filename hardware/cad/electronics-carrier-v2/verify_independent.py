"""Independent STL audit, standard library only; does not import CAD generator.

Tests exported triangles rather than trusting validation.json. Physical hardware
and real connector/strap paths remain outside what a triangle audit can verify.
Run: python3 hardware/cad/electronics-carrier-v2/verify_independent.py
"""
import collections
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'generated'
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
            assert len(incidents) == 2, 'Non-manifold edge'
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


files = ['electronics_carrier_v2_DRAFT_FIT_TEST.stl', 'holder_fit_ring.stl', 's2_corner_support_coupon.stl']
meshes = [STL(OUT / name) for name in files]
tray, holder_coupon, s2_coupon = meshes
assert all(m.result['downfacing_area_over_45_degrees_above_bed_mm2'] == 0 for m in meshes)

# Independent sample coordinates for this revision, not the generator's manifest.
# Five sample points across each slot prove usable width at 3 longitudinal points.
slots = [(x, y, 4.5, 2, 'holder') for x in (-39, 5) for y in (-71.1, 11.1)]
slots += [(x, 44, 3.5, 14, 'S2') for x in (-50.7, -15.3)]
slots += [(-8, y, 3.5, 2, 'wire') for y in (20, 30)]
slots += [(x, 44, 3.5, 22, 'converter') for x in (5, 55)]
slot_results = []
for x, y, width, straight, purpose in slots:
    for dx in (-width/2+.2, -.5, 0, .5, width/2-.2):
        for dy in (-straight/2+.1, .173, straight/2-.1):
            assert not tray.vertical_intersections(x+dx, y+dy), (purpose, x+dx, y+dy, 'blocked slot')
    # A section at an off-center longitudinal position finds each actual aperture edge.
    measured_edges = []
    for direction in (-1, 1):
        low = 0; high = width
        for _ in range(24):
            mid = (low+high)/2
            if tray.vertical_intersections(x+direction*mid, y+.173): high=mid
            else: low=mid
        measured_edges.append((low+high)/2)
    actual_width = sum(measured_edges)
    assert abs(actual_width-width) < .005, (purpose, actual_width)
    edge = min(C['tray']['width']/2-abs(x)-actual_width/2,
               C['tray']['height']/2-abs(y)-(straight+width)/2)
    assert edge >= C['minimum_edge_ligament']-.005
    slot_results.append({'purpose':purpose, 'center_mm':[x,y], 'measured_width_mm':round(actual_width,4), 'clearance_for_2_5_mm_tie_mm':round(actual_width-2.5,4), 'edge_ligament_mm':round(edge,3)})

# Dense samples in the entire reserved converter rectangle must hit only 3mm floor.
converter_samples = 0
for ix in range(21):
    for iy in range(19):
        hits = tray.vertical_intersections(10+ix*2+.013, 26+iy*2+.017)
        assert len(hits)==2 and abs(hits[0])<EPS and abs(hits[1]-3)<EPS, hits
        converter_samples += 1

# Nominal holder envelope is unobstructed above its 6mm saddles; locators permit liftout.
battery_samples = 0
for ix in range(35):
    for iy in range(33):
        x = -17-68.7/2+.05+ix*(68.7-.1)/34
        y = -30-64.2/2+.05+iy*(64.2-.1)/32
        assert tray.top(x,y) <= 6+EPS
        battery_samples += 1

# Check exported rest tops and center underside clearance on both parts.
for sx, sy, mesh in [(-33,44,tray),(0,0,s2_coupon)]:
    for dx in (-11.2,11.2):
        for dy in (-15.15,15.15):
            assert abs(mesh.top(sx+dx,sy+dy)-10)<EPS
    assert abs(mesh.top(sx+.137,sy+.217)-3)<EPS

# Physical locator spacing: side walls actually start .7mm outside the holder.
for direction in (-1,1):
    boundary = -17+direction*(68.7/2+.7)
    assert tray.top(boundary-direction*.05,-29.827) <= 6+EPS
    assert tray.top(boundary+direction*.05,-29.827) > 8

# USB keepout is above bare floor (or beyond tray), directed away from battery.
for x in (-38.8,-33,-27.2):
    for y in (62.3,68,74,79.8,82):
        height = tray.top(x,y)
        assert height is None or height <= 3+EPS

report = {
    'status':'Independent exported-mesh audit passed; physical fit remains unverified',
    'physical_fit_verified':False,
    'parts':[m.result for m in meshes],
    'through_slot_sample_rays':len(slots)*15,
    'slots':slot_results,
    'converter_continuous_3_mm_floor_sample_points':converter_samples,
    'holder_nominal_envelope_clear_above_6_mm_sample_points':battery_samples,
    'S2_rest_top_mm':10, 'S2_floor_to_pcb_clearance_mm':7,
    'nominal_solder_allowance_mm':3, 'remaining_clearance_away_from_corner_rests_mm':4,
    'S2_corner_rests_to_nominal_pad_rows_minimum_Y_gap_mm':4.06,
    'USB_route':'Illustrative plug keepout checked against actual tray mesh; positive Y outboard route clear. Actual cable unmeasured.',
    'known_old_issues_fixed':['Blind/roofed slots','2 mm slots for 2.5 mm ties','Converter edge rails replaced with continuous under-board floor','USB directed at battery'],
    'remaining_fit_blockers':[
        'B0GCW44FDL converter actual length, width, height, underside parts, solder and lead exits unknown; reserved 40 × 36 × 18 mm is not a model.',
        'Converter requires a suitable insulating spacer and retained strap path based on actual module; bare PCB is not ready to install.',
        'User S2 Mini underside component keepouts and solder joints at four corner rests unverified; nominal pad-row clearance is not an underside audit.',
        'S2 top-side strap path could load components; inspect and test retention without pressing components or antenna.',
        'Holder 68.7 × 64.2 × 22.5 mm is seller nominal, not measured; switch, lid, lead exit and strap path require dry fit; switch/lid access requires removing holder.',
        'Actual USB plug dimensions, wire bends and harness retention need fit check.',
        'No slicer or physical print inspection performed; topology and axial surface checks do not prove print quality, strength or fit.',
        'Tray is an independent bench prototype; wall/Command-strip mounting is not provided.'
    ]
}
(OUT/'independent-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
