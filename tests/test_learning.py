"""Check educational references, generated assets and actual schematic geometry."""
import importlib.util
import json
import re
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def _on_segment(point, segment):
    """The renderer uses orthogonal wires; include endpoints and T junctions."""
    (x, y), ((ax, ay), (bx, by)) = point, segment
    return ((ax == bx == x and min(ay, by) <= y <= max(ay, by)) or
            (ay == by == y and min(ax, bx) <= x <= max(ax, bx)))


def _segments_touch(first, second):
    if any(_on_segment(point, second) for point in first):
        return True
    if any(_on_segment(point, first) for point in second):
        return True
    # Perpendicular crossings can occur in the interior of both segments.
    if first[0][0] == first[1][0] and second[0][1] == second[1][1]:
        crossing = (first[0][0], second[0][1])
    elif first[0][1] == first[1][1] and second[0][0] == second[1][0]:
        crossing = (second[0][0], first[0][1])
    else:
        return False
    return _on_segment(crossing, first) and _on_segment(crossing, second)


class LearningTests(unittest.TestCase):
    def connection_geometry(self):
        harness = json.loads((ROOT / "hardware/wiring/harness.json").read_text())
        svg = ET.parse(ROOT / "hardware/wiring/connection-map.svg").getroot()
        return harness, svg

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

    def test_connection_sheet_has_visible_unique_terminal_markers(self):
        harness, svg = self.connection_geometry()
        expected = {terminal: net for net, terminals in harness["nets"].items()
                    for terminal in terminals}
        markers = [node for node in svg.iter() if node.get("data-terminal")]
        self.assertEqual(len(expected), 46)
        self.assertEqual(len(markers), len(expected))
        self.assertEqual({node.get("data-terminal") for node in markers}, set(expected))
        for marker in markers:
            with self.subTest(terminal=marker.get("data-terminal")):
                self.assertEqual(marker.tag.rsplit("}", 1)[-1], "circle")
                self.assertGreater(float(marker.get("r")), 0)
                self.assertEqual(marker.get("data-net"), expected[marker.get("data-terminal")])
        self.assertEqual({node.get("data-nc") for node in svg.iter() if node.get("data-nc")},
                         set(harness["leave_unconnected"]))

    def test_connection_sheet_wires_draw_one_connected_geometry_per_net(self):
        harness, svg = self.connection_geometry()
        groups = [node for node in svg.iter()
                  if node.tag.rsplit("}", 1)[-1] == "g" and node.get("data-net")]
        self.assertEqual(len(groups), len(harness["nets"]))
        self.assertEqual({node.get("data-net") for node in groups}, set(harness["nets"]))
        for group in groups:
            net = group.get("data-net")
            with self.subTest(net=net):
                paths = [node for node in group.iter() if node.get("data-wire")]
                self.assertTrue(paths)
                segments = []
                for path in paths:
                    self.assertEqual(path.get("data-wire"), net)
                    self.assertNotIn(path.get("stroke"), (None, "none", "transparent"))
                    points = json.loads(path.get("data-points"))
                    # Check the drawn path itself, not just its descriptive metadata.
                    self.assertRegex(path.get("d"), r"^M[-\d. ]+(?:L[-\d. ]+)+$")
                    drawn = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", path.get("d"))]
                    self.assertEqual(drawn, [value for point in points for value in point])
                    for start, end in zip(points, points[1:]):
                        self.assertNotEqual(start, end, "zero-length wire segment")
                        self.assertTrue(start[0] == end[0] or start[1] == end[1],
                                        "wire must be orthogonal")
                        segments.append((start, end))
                # Flood-fill segment intersections, including T junctions, to reject
                # detached wire islands that merely reuse the same net label.
                reached = {0}
                pending = [0]
                while pending:
                    current = pending.pop()
                    for index, segment in enumerate(segments):
                        if index not in reached and _segments_touch(segments[current], segment):
                            reached.add(index)
                            pending.append(index)
                self.assertEqual(len(reached), len(segments), "disconnected wire island")
                for marker in svg.iter():
                    if marker.get("data-terminal") and marker.get("data-net") == net:
                        point = (float(marker.get("cx")), float(marker.get("cy")))
                        self.assertTrue(any(_on_segment(point, line) for line in segments),
                                        marker.get("data-terminal") + " has no drawn wire")

    def test_connection_geometry_checker_detects_a_disconnected_wire_island(self):
        # Guard against weakening the connectivity check to a terminal-count test.
        left = ((0, 0), (10, 0))
        tee = ((5, 0), (5, 10))
        island = ((20, 0), (30, 0))
        crossing = ((5, -5), (5, 5))
        self.assertTrue(_segments_touch(left, tee))
        self.assertTrue(_segments_touch(left, crossing))
        self.assertFalse(_segments_touch(left, island))
        self.assertFalse(_on_segment((11, 0), left))

    def test_connection_sheet_has_no_ambiguous_net_overlaps_or_junctions(self):
        _, svg = self.connection_geometry()
        segments = []
        for path in svg.iter():
            if path.get("data-wire"):
                points = json.loads(path.get("data-points"))
                segments.extend((path.get("data-wire"), (a, b))
                                for a, b in zip(points, points[1:]))
        for marker in svg.iter():
            if marker.get("data-junction"):
                point = (float(marker.get("cx")), float(marker.get("cy")))
                meeting_nets = {net for net, segment in segments if _on_segment(point, segment)}
                self.assertEqual(meeting_nets, {marker.get("data-junction")},
                                 "junction dot touches an unrelated net or no wire")
        for index, (net, first) in enumerate(segments):
            for other_net, second in segments[index + 1:]:
                if net != other_net:
                    shared_points = {tuple(point) for point in (*first, *second)
                                     if _on_segment(point, first) and _on_segment(point, second)}
                    self.assertLessEqual(len(shared_points), 1,
                                         f"{net} and {other_net} overlap along a wire")


if __name__ == "__main__":
    unittest.main()
