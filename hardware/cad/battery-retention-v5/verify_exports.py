"""Independent STL topology/layout audit using the established binary reader.

Unlike the generator, this reads the exported triangles; repeated shim copies in
the master are checked against the quantities in its layout manifest.
"""
from collections import Counter
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stl_reader", ROOT.parent / "electronics-retention-v4/verify_stl_independent.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

def main():
    out = ROOT / "generated"
    manifest = json.loads((out / "validation.json").read_text())
    counts = Counter(item["source_file"] for item in manifest["layout"])
    parts = []
    for name, qty in counts.items():
        summary, _, _ = reader.audit(out / name)
        assert summary["connected_solids"] == 1, name
        summary["master_quantity"] = qty
        parts.append(summary)
    master, tris, components = reader.audit(out / manifest["master_file"])
    assert len(components) == sum(counts.values()) == manifest["master_piece_count"]
    assert master["triangles"] == sum(p["triangles"] * p["master_quantity"] for p in parts)
    assert abs(master["volume_mm3"] - sum(p["volume_mm3"] * p["master_quantity"] for p in parts)) < .15
    boxes = []
    for comp in components:
        points = [p for i in comp for p in tris[i]]
        box = [[min(p[k] for p in points), max(p[k] for p in points)] for k in range(3)]
        assert abs(box[2][0]) < 1e-5
        assert all(0 <= box[k][0] < box[k][1] <= 256 for k in (0, 1))
        boxes.append(box)
    gaps = [max(max(a[k][0]-b[k][1], b[k][0]-a[k][1]) for k in (0, 1))
            for i, a in enumerate(boxes) for b in boxes[i+1:]]
    assert min(gaps) >= 1
    report = {"status": "PASS: exported mesh topology and print layout; physical fit untested",
              "parts": parts, "master": master, "minimum_part_spacing_mm": min(gaps),
              "all_parts_on_bed": True, "all_parts_within_256mm_bed": True,
              "master_matches_individuals_with_quantities": True}
    (out / "independent-stl-audit.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": report["status"], "pieces": len(components), "spacing_mm": min(gaps)}))

if __name__ == "__main__":
    main()
