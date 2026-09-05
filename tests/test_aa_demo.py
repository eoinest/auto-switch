"""AA demo connectivity, including realistic breadboard and connector mistakes."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_aa_demo", ROOT / "tools/verify_aa_demo.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class AADemoTests(unittest.TestCase):
    def setUp(self):
        self.layout = json.loads(CHECK.LAYOUT.read_text())
        self.harness = json.loads(CHECK.HARNESS.read_text())

    def test_both_profiles_connect_all_terminals_without_mutating_inputs(self):
        before = copy.deepcopy((self.layout, self.harness))
        for gangs, holes, ports in ((1, 53, 12), (2, 58, 14)):
            with self.subTest(gangs=gangs):
                result = CHECK.validate_layout(self.layout, self.harness, gangs)
                self.assertEqual(result["pico_pins"], 40)
                self.assertEqual(result["occupied_holes"], holes)
                self.assertEqual(result["occupied_connector_ports"], ports)
                self.assertEqual(result["connector_ports"], 15)
                self.assertFalse(result["physical_build_verified"])
        self.assertEqual((self.layout, self.harness), before)

    def test_one_servo_omits_second_servo_but_keeps_all_physical_pico_pins(self):
        layout, harness = CHECK.profile(self.layout, self.harness, 1)
        self.assertNotIn("PICO.pin22_GP17", layout["terminal_bindings"])
        self.assertEqual(len(layout["pico_pins"]), 40)
        self.assertNotIn("J4", [j["id"] for j in layout["jumpers"]])
        self.assertNotIn("L4", [j["id"] for j in layout["leads"]])
        self.assertFalse(any(t.startswith("SERVO1.") for ts in harness["nets"].values() for t in ts))

    def test_power_ground_short(self):
        self.layout["jumpers"].append({"id":"BAD", "a":"e30", "b":"e50", "net":"5V"})
        with self.assertRaisesRegex(CHECK.LayoutError, "Short between nets"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_missing_pico_ground(self):
        self.layout["jumpers"] = [j for j in self.layout["jumpers"] if j["id"] != "J2"]
        with self.assertRaisesRegex(CHECK.LayoutError, "Open circuit: net GND"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_two_wires_in_one_hole(self):
        self.layout["jumpers"][0]["a"] = "a35"
        with self.assertRaisesRegex(CHECK.LayoutError, "Duplicate hole a35"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_resistor_leg_on_same_strip_shorts_signal_resistor(self):
        resistor = next(p for p in self.layout["placements"] if p["ref"] == "R_PWM0")
        resistor["terminals"]["2"] = "g30"
        self.layout["terminal_bindings"]["R_PWM0.2"] = "g30"
        with self.assertRaisesRegex(CHECK.LayoutError, "Short between nets"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_wrong_vsys_pin(self):
        self.layout["terminal_bindings"]["PICO.pin39_VSYS"] = "h3"
        with self.assertRaisesRegex(CHECK.LayoutError, "does not match its physical Pico pin"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_supply_to_unused_gpio(self):
        self.layout["jumpers"].append({"id":"BAD", "a":"b3", "b":"e30", "net":"5V"})
        with self.assertRaisesRegex(CHECK.LayoutError, "Unused Pico pin 1"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_one_servo_unused_gp17_remains_isolated(self):
        self.layout["jumpers"].append({"id":"BAD", "a":"i21", "b":"e30", "net":"5V"})
        with self.assertRaisesRegex(CHECK.LayoutError, "Unused Pico pin 22"):
            CHECK.validate_layout(self.layout, self.harness, 1)

    def test_missing_wago_ground_bridge(self):
        self.layout["external_wires"].remove(["PGND_A.4", "PGND_B.1"])
        with self.assertRaisesRegex(CHECK.LayoutError, "Open circuit: net GND"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_servo_power_in_ground_connector(self):
        wire = next(w for w in self.layout["external_wires"] if w == ["P5V.4", "SERVO0.power"])
        wire[0] = "PGND_B.5"
        with self.assertRaisesRegex(CHECK.LayoutError, "Short between nets"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_two_wires_in_single_wago_port(self):
        wire = next(w for w in self.layout["external_wires"] if w == ["P5V.4", "SERVO0.power"])
        wire[0] = "P5V.1"
        with self.assertRaisesRegex(CHECK.LayoutError, "Duplicate connector port P5V.1"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_missing_or_wrong_connector_contact_definition(self):
        self.layout["connector_blocks"][0]["ports"].pop()
        with self.assertRaisesRegex(CHECK.LayoutError, "five numbered WAGO"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_rcy_polarity_reversed(self):
        for wire in self.layout["external_wires"]:
            if wire == ["RCY.battery_positive", "RCY.load_positive"]:
                wire[1] = "RCY.load_negative"
            elif wire == ["RCY.battery_negative", "RCY.load_negative"]:
                wire[1] = "RCY.load_positive"
        with self.assertRaisesRegex(CHECK.LayoutError, "Short between nets"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_disconnected_rcy_contact(self):
        self.layout["external_wires"].remove(["RCY.battery_positive", "RCY.load_positive"])
        with self.assertRaisesRegex(CHECK.LayoutError, "Open circuit: net FUSED_BAT"):
            CHECK.validate_layout(self.layout, self.harness)

    def test_invalid_hole_rejected(self):
        self.layout["jumpers"][0]["a"] = "b64"
        with self.assertRaisesRegex(CHECK.LayoutError, "Invalid hole"):
            CHECK.validate_layout(self.layout, self.harness)


class AADemoRenderTests(unittest.TestCase):
    def setUp(self):
        self.layout = json.loads(CHECK.LAYOUT.read_text())
        self.harness = json.loads(CHECK.HARNESS.read_text())
        folder = CHECK.LAYOUT.parent
        self.svg = ET.fromstring((folder / "breadboard-1-servo.svg").read_text())
        self.render_map = json.loads((folder / "render-map-1.json").read_text())
        self.csv = (folder / "placements-1-servo.csv").read_text()

    def check(self):
        return CHECK.validate_render(self.layout, self.harness, ET.tostring(self.svg, encoding="unicode"), self.render_map, self.csv, 1)

    def group(self, ref):
        return next(e for e in self.svg.iter() if e.get("data-wire") == ref)

    def conductor(self, ref):
        return next(e for e in self.group(ref).iter() if e.get("data-from"))

    def test_actual_svg_geometry_matches_both_profiles(self):
        for gangs, wires in ((1, 22), (2, 26)):
            with self.subTest(gangs=gangs):
                folder = CHECK.LAYOUT.parent
                result = CHECK.validate_render(self.layout, self.harness,
                    (folder / f"breadboard-{gangs}-servo.svg").read_text(),
                    json.loads((folder / f"render-map-{gangs}.json").read_text()),
                    (folder / f"placements-{gangs}-servo.csv").read_text(), gangs)
                self.assertEqual(result["svg_holes"], 630)
                self.assertEqual(result["svg_wires"], wires)
                self.assertEqual(result["svg_pico_pins"], 40)
                self.assertFalse(result["physical_build_verified"])

    def test_actual_stroke_changed_with_metadata_unchanged(self):
        path = self.conductor("J1")
        points = CHECK._path_points(path.get("d"))
        points[-1] = (points[-1][0], points[-1][1] + 18)
        path.set("d", "M" + " L".join(f"{x},{y}" for x, y in points))
        with self.assertRaisesRegex(CHECK.LayoutError, "actual path endpoints miss"):
            self.check()

    def test_svg_interior_crosses_signal_terminal_even_with_consistent_metadata(self):
        group = self.group("J1")
        points = CHECK._path_points(self.conductor("J1").get("d"))
        points.insert(1, tuple(self.render_map["terminals"]["R_PWM0.2"]))
        d = "M" + " L".join(f"{x},{y}" for x, y in points)
        for path in group.iter():
            if path.tag.endswith("path"):
                path.set("d", d)
        next(r for r in self.render_map["routes"] if r["id"] == "J1")["points"] = points
        with self.assertRaisesRegex(CHECK.LayoutError, "crosses foreign terminal R_PWM0.2"):
            self.check()

    def test_wire_cannot_pass_through_empty_wago_port(self):
        group = self.group("E8")
        points = CHECK._path_points(self.conductor("E8").get("d"))
        points.insert(1, tuple(self.render_map["terminals"]["P5V.5"]))
        d = "M" + " L".join(f"{x},{y}" for x, y in points)
        for path in group.iter():
            if path.tag.endswith("path"):
                path.set("d", d)
        next(r for r in self.render_map["routes"] if r["id"] == "E8")["points"] = points
        with self.assertRaisesRegex(CHECK.LayoutError, "crosses foreign terminal P5V.5"):
            self.check()

    def test_missing_rcy_mating_wire(self):
        self.svg.remove(self.group("E3"))
        with self.assertRaisesRegex(CHECK.LayoutError, "Rendered wire identifiers differ"):
            self.check()

    def test_extra_actual_conductor_even_without_wire_group(self):
        self.svg.append(copy.deepcopy(self.conductor("L1")))
        with self.assertRaisesRegex(CHECK.LayoutError, "Extra or ungrouped SVG conductor"):
            self.check()

    def test_extra_wire_style_stroke_without_electrical_labels(self):
        extra = copy.deepcopy(self.conductor("L1"))
        del extra.attrib["data-from"]
        del extra.attrib["data-to"]
        self.svg.append(extra)
        with self.assertRaisesRegex(CHECK.LayoutError, "Extra or ungrouped SVG conductor"):
            self.check()

    def test_hole_label_moved_off_actual_board_grid(self):
        hole = next(e for e in self.svg.iter() if e.get("data-hole") == "a63")
        hole.set("cx", str(float(hole.get("cx")) + 3))
        with self.assertRaisesRegex(CHECK.LayoutError, "outside its regular breadboard grid"):
            self.check()

    def test_pico_header_square_moved_to_wrong_row(self):
        pico = next(e for e in self.svg.iter() if e.get("data-component") == "PICO")
        pin = next(e for e in pico.iter() if e.tag.endswith("rect") and e.get("width") == "10" and e.get("height") == "10")
        pin.set("y", str(float(pin.get("y")) + 18))
        with self.assertRaisesRegex(CHECK.LayoutError, "all 40 physical pin positions"):
            self.check()

    def test_component_leg_marker_moved(self):
        leg = next(e for e in self.svg.iter() if e.get("data-terminal") == "D1.cathode")
        leg.set("cy", str(float(leg.get("cy")) - 18))
        with self.assertRaisesRegex(CHECK.LayoutError, "not drawn at planned hole"):
            self.check()

    def test_csv_table_wrong_pin(self):
        self.csv = self.csv.replace("b35,j4", "b35,j3")
        with self.assertRaisesRegex(CHECK.LayoutError, "CSV differs"):
            self.check()

    def test_render_map_cannot_hide_different_actual_path(self):
        self.render_map["routes"][0]["points"][1][0] += 10
        with self.assertRaisesRegex(CHECK.LayoutError, "render-map geometry differs"):
            self.check()

    def test_transformed_wire_rejected(self):
        self.group("J1").set("transform", "translate(0 18)")
        with self.assertRaisesRegex(CHECK.LayoutError, "Transformed electrical geometry"):
            self.check()


if __name__ == "__main__":
    unittest.main()
