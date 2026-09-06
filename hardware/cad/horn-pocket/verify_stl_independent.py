"""Independent binary-STL check of the three provisional horn fit coupons."""
import importlib.util
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mesh_audit', ROOT.parent / 'electronics-retention-v4/verify_stl_independent.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
out = ROOT / 'generated'
parts = [module.audit(p)[0] for p in sorted(out.glob('horn-fit-coupon-profile-*pct-PHOTO-ESTIMATE.stl'))]
assert len(parts) == 3 and all(p['connected_solids'] == 1 for p in parts)
master, tris, components = module.audit(out / 'horn-fit-coupons-ALL-THREE-PHOTO-ESTIMATE.stl')
assert len(components) == 3
assert sum(p['triangles'] for p in parts) == master['triangles']
assert abs(sum(p['volume_mm3'] for p in parts) - master['volume_mm3']) < .1
assert all(0 <= master['bounds_mm'][k][0] < master['bounds_mm'][k][1] <= 256 for k in (0, 1))
boxes=[]
for comp in components:
    ps=[p for i in comp for p in tris[i]]
    bounds=[[min(p[k] for p in ps), max(p[k] for p in ps)] for k in range(3)]
    assert abs(bounds[2][0]) < 1e-5
    boxes.append(bounds)
gaps=[]
for i,a in enumerate(boxes):
    for b in boxes[i+1:]:
        gap=max(max(a[k][0]-b[k][1], b[k][0]-a[k][1]) for k in (0,1))
        assert gap >= 1
        gaps.append(gap)
report={'status':'PASS: provisional coupon meshes and layout only; actual horn fit unknown',
        'parts':parts, 'master':master, 'individual_master_triangle_and_volume_match':True,
        'all_parts_on_bed':True, 'fits_A1':True, 'minimum_gap_mm':min(gaps)}
(out / 'independent-stl-audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(report['status'], master['bounds_mm'], 'gap', min(gaps))
