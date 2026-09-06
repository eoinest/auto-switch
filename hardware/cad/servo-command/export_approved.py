"""Export the user-approved print layout, excluding every display/reference object.

Run in Blender background mode. One coordinate unit is one millimetre.
The review scene is preserved; a separate exported scene records approval.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
# cadlib initializes an empty scene; import it before opening the approved scene.
import cadlib
import bpy

OUT = ROOT / "generated"
source = OUT / "print-layout-review.blend"
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
parts = {
    "PRINT wall chassis": "02_servo_mount",
    "PRINT actuator paddle": "03_factory_horn_paddle",
}
for name, filename in parts.items():
    obj = bpy.data.objects[name]
    # The reviewed scene already has the approved rotation. Only centre XY
    # and place Z=0; never apply the old assembly paddle rotation again.
    cadlib.export(obj, filename, rotate=False)
    if "review_only" in obj:
        del obj["review_only"]
    obj["export_status"] = "User approved STL export"

manifest_path = OUT / "validation.json"
manifest = json.loads(manifest_path.read_text())
updated = {part["file"]: part for part in cadlib.REPORT}
manifest["parts"] = [updated.get(part["file"], part) for part in manifest["parts"]]
manifest["print_orientation_source"] = source.name
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

for obj in bpy.data.objects:
    if obj.type == "FONT":
        if obj.data.body == "PRINT LAYOUT / REVIEW":
            obj.data.body = "PRINT LAYOUT / EXPORTED"
        elif "no STL export yet" in obj.data.body:
            obj.data.body = "Two parts  |  millimetres  |  STL export approved"
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "print-layout-exported.blend"))

report = {
    "status": "User-approved STL export; physical fit still requires a dry fit",
    "source": source.name,
    "source_sha256": source_hash,
    "units": "mm",
    "parts": cadlib.REPORT,
    "stl_sha256": {name + ".stl": hashlib.sha256((OUT / (name + ".stl")).read_bytes()).hexdigest()
                   for name in parts.values()},
    "excluded": "Build plate, labels, camera, lights, electronics and servo reference",
}
(OUT / "approved-export.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
