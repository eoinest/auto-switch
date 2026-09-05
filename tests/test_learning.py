"""Check educational references, source/asset consistency and diagram connectivity labels."""
import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class LearningTests(unittest.TestCase):
    def test_curriculum_references_and_quiz_answers_are_complete(self):
        course = json.loads((ROOT / "docs/learn-content.json").read_text())
        ids = {s["id"] for s in course["sources"]}
        self.assertEqual(len(ids), len(course["sources"]))
        lessons = course["lessons"]
        self.assertEqual(len(lessons), 12)
        self.assertEqual(course["progression"], [l["id"] for l in lessons])
        quiz_ids = []
        for lesson in lessons:
            self.assertTrue(set(lesson["source_ids"]) <= ids)
            self.assertTrue(lesson["objective"] and lesson["concept"] and lesson["project"])
            self.assertEqual(len(lesson["quiz"]), 2)
            for quiz in lesson["quiz"]:
                quiz_ids.append(quiz["id"])
                self.assertTrue(set(quiz["source_ids"]) <= ids)
                self.assertTrue(quiz["explanation"])
                self.assertEqual(type(quiz["answer_index"]), int)
                self.assertTrue(0 <= quiz["answer_index"] < len(quiz["options"]))
        self.assertEqual(len(quiz_ids), len(set(quiz_ids)))
        for step in course["capstone"]["steps"]:
            self.assertTrue(set(step["source_ids"]) <= ids)

    def test_learning_bundle_matches_current_source_files(self):
        spec = importlib.util.spec_from_file_location("build_learning", ROOT / "tools/build_learning.py")
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        for path, expected in build.outputs().items():
            self.assertEqual((ROOT / path).read_text(), expected, path + " needs rebuilding")

    def test_master_output_has_separate_interactive_group(self):
        svg = ET.parse(ROOT / "hardware/wiring/power-map.svg").getroot()
        groups = {node.get("id"): node for node in svg.iter() if node.get("id")}
        self.assertIn("PACK_SW", " ".join(groups["path-pack-sw"].itertext()))
        self.assertNotIn("PACK_SW", " ".join(groups["path-battery"].itertext()))
        for group in ("path-usb", "path-pico-external", "path-vsys", "path-3v3", "path-motor-output"):
            self.assertIn(group, groups)

    def test_connection_sheet_contains_every_net_terminal(self):
        harness = json.loads((ROOT / "hardware/wiring/harness.json").read_text())
        svg = ET.parse(ROOT / "hardware/wiring/connection-map.svg").getroot()
        text = " ".join(svg.itertext())
        for net, terminals in harness["nets"].items():
            self.assertIn(net, text)
            for terminal in terminals:
                self.assertIn(terminal, text)


if __name__ == "__main__":
    unittest.main()
