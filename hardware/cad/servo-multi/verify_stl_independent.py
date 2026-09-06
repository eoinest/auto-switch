"""Audit actual binary STL exports with the separately authored v4 mesh auditor.
Run: python3 hardware/cad/servo-multi/verify_stl_independent.py
Checks each detached part, master equivalence, spacing, bed contact and A1 bounds.
Does not establish fit, strength, adhesion or motion under load.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_mesh_audit', ROOT.parent / 'electronics-retention-v4/verify_stl_independent.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

for variant, expected in [('double', 5), ('triple', 7)]:
    directory = ROOT / 'generated' / variant
    paths = sorted(directory.glob('[0-9][0-9]_*.stl'))
    assert len(paths) == expected, (variant, 'unexpected individual exports', paths)
    parts = [module.audit(path)[0] for path in paths]
    assert all(p['connected_solids'] == 1 for p in parts)
    master, tris, components = module.audit(directory / f'{variant}-ALL-PIECES-CONCEPT.stl')
    assert len(components) == expected
    assert sum(p['triangles'] for p in parts) == master['triangles']
    assert abs(sum(p['volume_mm3'] for p in parts) - master['volume_mm3']) < .15
    assert all(0 <= master['bounds_mm'][k][0] < master['bounds_mm'][k][1] <= 256 for k in (0, 1))
    boxes = []
    for component in components:
        points = [p for i in component for p in tris[i]]
        bounds = [[min(p[k] for p in points), max(p[k] for p in points)] for k in range(3)]
        assert abs(bounds[2][0]) < 1e-5
        boxes.append(bounds)
    gaps = []
    for i, a in enumerate(boxes):
        for b in boxes[i+1:]:
            gap = max(max(a[k][0]-b[k][1], b[k][0]-a[k][1]) for k in (0, 1))
            assert gap >= 1, ('overlap or insufficient spacing', gap)
            gaps.append(gap)
    report = {
        'status': 'PASS: exported mesh and bed layout; physical fit and slicing unverified',
        'parts': parts, 'master': master,
        'master_matches_individual_triangle_count_and_volume': True,
        'each_part_on_bed': True, 'fits_256mm_bed': True,
        'minimum_pairwise_bounding_box_gap_mm': min(gaps),
    }
    (directory / 'independent-stl-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(variant, 'PASS', len(components), 'closed solids;', master['bounds_mm'], 'gap', min(gaps))
