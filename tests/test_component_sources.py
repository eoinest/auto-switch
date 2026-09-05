"""Catch changes to checked vendor artifacts and their provenance metadata.

These checks establish file consistency, not physical manufacturing tolerance.
"""
import hashlib
import json
from pathlib import Path
import unittest
from zipfile import ZipFile


COMPONENTS = Path(__file__).resolve().parents[1] / "hardware/components"


class ComponentSourceTests(unittest.TestCase):
    def test_original_archive_and_derived_mesh_hashes(self):
        source = json.loads((COMPONENTS / "board-servo.json").read_text())
        meta = json.loads((COMPONENTS / "vendor/PicoW-mesh-metadata.json").read_text())
        archive = COMPONENTS / "vendor/PicoW-step.zip"
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),
                         source["sources"]["pico_w_step"]["sha256"])
        with ZipFile(archive) as original:
            self.assertEqual(hashlib.sha256(original.read("PicoW.stp")).hexdigest(),
                             meta["source_sha256"])
        for extension in ("obj", "mtl"):
            actual = hashlib.sha256((COMPONENTS / ("vendor/PicoW." + extension)).read_bytes()).hexdigest()
            self.assertEqual(actual, meta[extension + "_sha256"])

    def test_obj_named_parts_and_mesh_indices_match_record(self):
        meta = json.loads((COMPONENTS / "vendor/PicoW-mesh-metadata.json").read_text())
        parts = {}
        vertices = 0
        current = None
        for line in (COMPONENTS / "vendor/PicoW.obj").read_text().splitlines():
            if line.startswith("o "):
                current = line[2:]
                self.assertNotIn(current, parts)
                parts[current] = {"vertices": 0, "triangles": 0}
            elif line.startswith("v "):
                vertices += 1
                parts[current]["vertices"] += 1
            elif line.startswith("f "):
                indices = list(map(int, line.split()[1:]))
                self.assertEqual(len(indices), 3)
                self.assertTrue(all(1 <= index <= vertices for index in indices))
                parts[current]["triangles"] += 1
        self.assertEqual(len(parts), 11)
        self.assertEqual(set(parts), {p["name"] for p in meta["parts"]})
        for part in meta["parts"]:
            self.assertEqual(parts[part["name"]], {"vertices": part["vertices"],
                                                 "triangles": part["triangles"]})


if __name__ == "__main__":
    unittest.main()
