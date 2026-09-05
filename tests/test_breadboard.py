"""Independent connectivity checks, including deliberate build mistakes."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import csv
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_breadboard", ROOT / "tools/verify_breadboard.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class BreadboardTests(unittest.TestCase):
    def setUp(self):
        self.layout = json.loads(CHECK.LAYOUT.read_text())
        self.harness = json.loads(CHECK.HARNESS.read_text())

    def test_rendered_insertions_match_exact_plan_holes(self):
        svg = ET.parse(ROOT / "hardware/wiring/breadboard/layout.svg").getroot()
        holes = {e.get("data-hole"): (float(e.get("cx")), float(e.get("cy")))
                 for e in svg.iter() if e.get("data-hole")}
        self.assertEqual(len(holes), 630)
        items = {e.get("data-bb-item"): e for e in svg.iter() if e.get("data-bb-item")}
        expected = {p["ref"]: list(p["terminals"].values()) for p in self.layout["placements"]}
        expected.update({j["id"]: [j["a"], j["b"]] for j in self.layout["jumpers"]})
        expected.update({l["id"]: [l["hole"]] for l in self.layout["leads"]})
        for ref, addresses in expected.items():
            markers = [e for e in items[ref].iter() if e.get("data-bb-endpoint")]
            self.assertCountEqual([e.get("data-bb-endpoint") for e in markers], addresses)
            for marker in markers:
                self.assertEqual((float(marker.get("cx")), float(marker.get("cy"))),
                                 holes[marker.get("data-bb-endpoint")], ref)
        with (ROOT / "hardware/wiring/breadboard/placements.csv").open() as f:
            rows = {r["id"]: r for r in csv.DictReader(f)}
        self.assertEqual(set(rows), set(expected))
        for ref, addresses in expected.items():
            self.assertEqual(rows[ref]["start"], addresses[0])
            if len(addresses) == 2:
                self.assertEqual(rows[ref]["end"], addresses[1])

    def test_full_layout_implements_every_harness_net(self):
        result = CHECK.validate_layout(self.layout, self.harness)
        self.assertEqual(result["nets"], len(self.harness["nets"]))
        self.assertEqual(result["terminals"], sum(map(len, self.harness["nets"].values())))
        self.assertEqual(result["pico_pins"], 40)
        self.assertFalse(result["physical_build_verified"])

    def test_one_servo_omits_whole_second_signal_and_power_branch(self):
        before = copy.deepcopy(self.layout)
        layout, harness = CHECK.profile(self.layout, self.harness, 1)
        self.assertNotIn("R_PWM1", [p["ref"] for p in layout["placements"]])
        self.assertNotIn("J5", [j["id"] for j in layout["jumpers"]])
        self.assertNotIn("L6", [j["id"] for j in layout["leads"]])
        self.assertNotIn("PICO.pin22_GP17", layout["terminal_bindings"])
        self.assertFalse(any("SERVO1." in t for pair in layout["external_wires"] for t in pair))
        self.assertEqual(len(layout["pico_pins"]), 40)
        result = CHECK.validate_layout(self.layout, self.harness, 1)
        self.assertEqual(result["nets"], 11)
        self.assertEqual(result["jumpers"], 7)
        self.assertEqual(result["leads"], 5)
        self.assertEqual(self.layout, before)
        CHECK.validate_layout(layout, harness)

    def test_short_between_5v_and_ground_is_rejected(self):
        self.layout["jumpers"].append({"id": "BAD", "a": "e30", "b": "e60", "net": "5V"})
        with self.assertRaisesRegex(CHECK.LayoutError, "Short between nets"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_two_leads_in_one_hole_is_rejected(self):
        self.layout["jumpers"][0]["a"] = "a35"  # Already occupied by D1's cathode.
        with self.assertRaisesRegex(CHECK.LayoutError, "Duplicate hole a35"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_open_ground_return_is_rejected(self):
        self.layout["jumpers"] = [j for j in self.layout["jumpers"] if j["id"] != "J2"]
        with self.assertRaisesRegex(CHECK.LayoutError, "Open circuit: net GND"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_supply_connected_to_unused_gpio_is_rejected(self):
        self.layout["jumpers"].append({"id": "BAD", "a": "b3", "b": "e30", "net": "5V"})
        with self.assertRaisesRegex(CHECK.LayoutError, "Unused Pico pin 1"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_shifted_vsys_binding_is_rejected(self):
        self.layout["terminal_bindings"]["PICO.pin39_VSYS"] = "h3"
        with self.assertRaisesRegex(CHECK.LayoutError, "does not match its physical Pico pin"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_hole_outside_board_is_rejected(self):
        self.layout["jumpers"][0]["a"] = "b64"
        with self.assertRaisesRegex(CHECK.LayoutError, "Invalid hole"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_resistor_legs_must_not_share_conductive_strip(self):
        self.layout["placements"][1]["terminals"]["2"] = "c40"
        self.layout["terminal_bindings"]["R_TOP.2"] = "c40"
        with self.assertRaisesRegex(CHECK.LayoutError, "Short between nets"):
            CHECK.validate_layout(self.layout, self.harness)


if __name__ == "__main__":
    unittest.main()
