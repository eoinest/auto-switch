#!/usr/bin/env python3
"""Verify AA demo wires, breadboard strips and specified WAGO connector contacts.

This is an unpowered connectivity check. It does not simulate components, test
current capacity, certify polarity from a photograph, or prove a physical build.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import io
import importlib.util
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "hardware/wiring/aa-demo/layout.json"
HARNESS = ROOT / "hardware/wiring/aa-demo/harness.json"
_SPEC = importlib.util.spec_from_file_location("aa_demo_breadboard_engine", ROOT / "tools/verify_breadboard.py")
_BASE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_BASE)
LayoutError = _BASE.LayoutError
profile = _BASE.profile


def validate_layout(layout, harness, gangs=2):
    layout, harness = profile(layout, harness, gangs)
    errors = []
    if layout["board"]["pico_start_row"] != 3:
        errors.append("AA demo Pico must occupy c3-c22 and h3-h22")
    active_pico = {"PICO.pin39_VSYS", "PICO.pin38_GND", "PICO.pin21_GP16"}
    if gangs == 2:
        active_pico.add("PICO.pin22_GP17")
    actual_pico = {t for t in layout["terminal_bindings"] if t.startswith("PICO.")}
    if actual_pico != active_pico:
        errors.append("AA demo permits only VSYS, GND and the selected servo signal Pico bindings")
    forbidden = {"GATE", "R_TOP", "R_BOTTOM", "C_ADC", "R_EN", "R_BLEED", "D2"}
    if forbidden & set(harness["parts"]):
        errors.append("AA demo must not include the previous gated or ADC circuit")
    terminals = {t for ts in harness["nets"].values() for t in ts}
    required_nc = {"PICO.pin40_VBUS", "PICO.pin36_3V3_OUT", "PICO.pin20_GP15", "PICO.pin31_GP26", "MASTER.ON", "REG.ENABLE"}
    if not required_nc <= set(harness["leave_unconnected"]):
        errors.append("Missing required leave-unconnected terminal declaration")
    if terminals & set(harness["leave_unconnected"]):
        errors.append("A leave-unconnected terminal appears in the harness nets")

    # A WAGO 221-415 is five contacts on one conductor. Explicit numbered ports
    # make one-wire-per-port occupancy independently checkable before unioning.
    blocks = layout.get("connector_blocks", [])
    refs = [b["ref"] for b in blocks]
    if sorted(refs) != ["P5V", "PGND_A", "PGND_B"]:
        errors.append("Expected one positive and two ground WAGO connector blocks")
    all_ports = set()
    for block in blocks:
        expected = [f"{block['ref']}.{i}" for i in range(1, 6)]
        if block.get("part") != "WAGO 221-415" or block.get("ports") != expected:
            errors.append(f"{block['ref']}: expected the five numbered WAGO 221-415 ports")
        all_ports.update(expected)
    uses = Counter(t for pair in layout["external_wires"] for t in pair if t in all_ports)
    uses.update(lead["node"] for lead in layout["leads"] if lead["node"] in all_ports)
    for port, count in uses.items():
        if count > 1:
            errors.append(f"Duplicate connector port {port}: {count} inserted wires")
    if errors:
        raise LayoutError("\n".join(errors))
    for block in blocks:
        ports = block["ports"]
        layout["external_wires"].extend([[ports[0], port] for port in ports[1:]])
    report = _BASE.validate_layout(layout, harness, gangs=2)
    report.update({
        "gangs": gangs,
        "connector_blocks": len(blocks),
        "connector_ports": len(all_ports),
        "occupied_connector_ports": len(uses),
        "physical_build_verified": False,
        "scope": "Unpowered breadboard/wire/WAGO contact connectivity only; no powered simulation or hardware verification",
    })
    return report


def _path_points(path):
    """Parse the actual restricted SVG conductor geometry, not its labels."""
    tokens = re.findall(r"[ML]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", path)
    residue = re.sub(r"[ML]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?|[\s,]", "", path)
    if residue or len(tokens) < 6 or len(tokens) % 3 or tokens[0] != "M":
        raise LayoutError("Unsupported conductor path geometry; expected M/L coordinate pairs")
    points = []
    for i in range(0, len(tokens), 3):
        if tokens[i] != ("M" if i == 0 else "L"):
            raise LayoutError("Conductor path must be one continuous M/L stroke")
        points.append((float(tokens[i + 1]), float(tokens[i + 2])))
    return points


def _distance_to_segment(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_squared = dx * dx + dy * dy
    t = max(0, min(1, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / length_squared)) if length_squared else 0
    return math.hypot(point[0] - a[0] - t * dx, point[1] - a[1] - t * dy)


def validate_render(layout, harness, svg_text, render_map, csv_text, gangs=2):
    """Check displayed strokes, component pins and port occupancy against plan.

    Insulated wire crossings are not junctions. A stroke through a foreign
    terminal is ambiguous and rejected unless it is a pad on the same existing
    breadboard strip as the wire's inserted end. Powered behavior is not tested.
    """
    validate_layout(layout, harness, gangs)
    plan, harness = profile(layout, harness, gangs)
    svg = ET.fromstring(svg_text)
    parents = {child: parent for parent in svg.iter() for child in parent}
    errors = []

    def untransformed(element):
        current = element
        while current is not None:
            if current.get("transform"):
                errors.append("Transformed electrical geometry is not supported by this checker")
                break
            current = parents.get(current)

    def collect(attribute):
        result = {}
        for e in svg.iter():
            if e.get(attribute) is not None:
                name = e.get(attribute)
                if name in result:
                    errors.append(f"Duplicate SVG {attribute} {name}")
                result[name] = e
                untransformed(e)
        return result

    def center(e):
        return (float(e.get("cx")), float(e.get("cy")))

    hole_elements = collect("data-hole")
    expected_holes = {f"{c}{r}" for c in "abcdefghij" for r in range(1, 64)}
    if set(hole_elements) != expected_holes:
        raise LayoutError("Rendered breadboard must have exactly 630 uniquely addressed terminal holes")
    holes = {h: center(e) for h, e in hole_elements.items()}
    origin = holes["a1"]
    x_pitch = holes["b1"][0] - origin[0]
    y_pitch = holes["a2"][1] - origin[1]
    if x_pitch <= 0 or y_pitch <= 0:
        errors.append("Breadboard coordinates must run left-to-right and top-to-bottom")
    for hole, point in holes.items():
        column, row = "abcdefghij".index(hole[0]), int(hole[1:]) - 1
        expected = (origin[0] + (column + (2 if column >= 5 else 0)) * x_pitch,
                    origin[1] + row * y_pitch)
        if point != expected:
            errors.append(f"Rendered hole {hole} is outside its regular breadboard grid")
    terminal_elements = collect("data-terminal")
    drawn_terminals = {t: center(e) for t, e in terminal_elements.items()}
    metadata_terminals = {t: tuple(xy) for t, xy in render_map["terminals"].items()}
    bound = plan["terminal_bindings"]
    expected_terminal_ids = {t for ts in harness["nets"].values() for t in ts}
    expected_drawn = {t for t in expected_terminal_ids if not t.startswith("PICO.")}
    if set(drawn_terminals) != expected_drawn:
        errors.append("SVG component terminal set differs from the profiled harness")
    for terminal, point in drawn_terminals.items():
        if metadata_terminals.get(terminal) != point:
            errors.append(f"Render map position for {terminal} differs from actual terminal circle")
    for terminal, hole in bound.items():
        if metadata_terminals.get(terminal) != holes[hole]:
            errors.append(f"Terminal binding {terminal} does not coincide with hole {hole}")
        if not terminal.startswith("PICO.") and drawn_terminals.get(terminal) != holes[hole]:
            errors.append(f"Component leg {terminal} is not drawn at planned hole {hole}")

    # Actual Pico header squares must occupy every one of its 40 physical holes.
    pico = [e for e in svg.iter() if e.get("data-component") == "PICO"]
    if len(pico) != 1:
        errors.append("Expected exactly one drawn Pico")
    else:
        pin_squares = [e for e in pico[0].iter() if e.tag.endswith("rect") and e.get("width") == "10" and e.get("height") == "10"]
        actual_pins = Counter((float(e.get("x")) + 5, float(e.get("y")) + 5) for e in pin_squares)
        expected_pins = Counter(holes[h] for h in plan["pico_pins"].values())
        if actual_pins != expected_pins:
            errors.append("Drawn Pico header squares do not match all 40 physical pin positions")

    expected_wires = {f"E{i + 1}": tuple(pair) for i, pair in enumerate(plan["external_wires"])}
    expected_wires.update({j["id"]: ("hole:" + j["a"], "hole:" + j["b"]) for j in plan["jumpers"]})
    expected_wires.update({l["id"]: ("hole:" + l["hole"], l["node"]) for l in plan["leads"]})
    wire_elements = collect("data-wire")
    if set(wire_elements) != set(expected_wires):
        errors.append("Rendered wire identifiers differ from the full profiled wiring plan")
    route_rows = render_map["routes"]
    routes = {r["id"]: r for r in route_rows}
    if len(routes) != len(route_rows) or set(routes) != set(expected_wires):
        errors.append("Render map routes differ from the full profiled wiring plan")

    def node_point(node):
        return holes[node[5:]] if node.startswith("hole:") else drawn_terminals[node]

    def same_strip(node, other):
        def hole_for(n):
            return n[5:] if n.startswith("hole:") else bound.get(n)
        a, b = hole_for(node), hole_for(other)
        return bool(a and b and a[1:] == b[1:] and (a[0] in "abcde") == (b[0] in "abcde"))

    actual_paths = []
    svg_pairs = []
    all_conductor_paths = [e for e in svg.iter() if e.get("data-from") is not None or e.get("data-to") is not None
                           or (e.tag.endswith("path") and e.get("stroke-width") == "4.5" and e.get("fill") == "none")]
    for ref, group in wire_elements.items():
        paths = [e for e in group.iter() if e.tag.endswith("path")]
        electrical = [e for e in paths if e.get("data-from") is not None]
        if len(electrical) != 1 or len(paths) != 2:
            errors.append(f"Wire {ref} must have exactly one colored conductor and one matching clearance stroke")
            continue
        path = electrical[0]
        untransformed(path)
        actual_paths.append(path)
        endpoints = (path.get("data-from"), path.get("data-to"))
        svg_pairs.append(endpoints)
        if endpoints != expected_wires.get(ref):
            errors.append(f"Wire {ref} endpoints differ from plan")
            continue
        points = _path_points(path.get("d", ""))
        if points[0] != node_point(endpoints[0]) or points[-1] != node_point(endpoints[1]):
            errors.append(f"Wire {ref} actual path endpoints miss their terminal or hole")
        for node in endpoints:
            if metadata_terminals.get(node) != node_point(node):
                errors.append(f"Wire {ref} node position differs from drawn hole or terminal")
        clearance = next(e for e in paths if e is not path)
        if _path_points(clearance.get("d", "")) != points or float(clearance.get("stroke-width", 0)) <= float(path.get("stroke-width", 0)):
            errors.append(f"Wire {ref} clearance stroke does not follow actual conductor")
        if path.get("fill") != "none" or path.get("stroke") in (None, "none") or float(path.get("stroke-width", 0)) <= 0:
            errors.append(f"Wire {ref} is not visibly stroked")
        endpoint_dots = [center(e) for e in group.iter() if e.tag.endswith("circle")]
        if Counter(endpoint_dots) != Counter((points[0], points[-1])):
            errors.append(f"Wire {ref} endpoint dots do not match actual path ends")
        route = routes.get(ref, {})
        if (route.get("from"), route.get("to")) != endpoints or [tuple(p) for p in route.get("points", [])] != points:
            errors.append(f"Wire {ref} render-map geometry differs from SVG path")
        # A same-strip contact is already electrically joined. All other drawn
        # terminal contacts, including unused WAGO slots, must remain distinct.
        obstacles = dict(drawn_terminals)
        obstacles.update({node: node_point(node) for pair in expected_wires.values() for node in pair if node.startswith("hole:")})
        for node, point in obstacles.items():
            if node in endpoints or point in (points[0], points[-1]) or any(same_strip(end, node) for end in endpoints):
                continue
            if any(_distance_to_segment(point, a, b) < 6 for a, b in zip(points, points[1:])):
                errors.append(f"Wire {ref} crosses foreign terminal {node}")
    if set(actual_paths) != set(all_conductor_paths):
        errors.append("Extra or ungrouped SVG conductor path")
    if Counter(svg_pairs) != Counter(expected_wires.values()):
        errors.append("Actual SVG conductor pairs differ from planned wires (including RCY mating contacts)")

    # Every physical insertion in the printed table must also agree with plan.
    table = list(csv.DictReader(io.StringIO(csv_text)))
    expected_rows = {p["ref"]: tuple(p["terminals"].values()) for p in plan["placements"]}
    expected_rows.update({j["id"]: (j["a"], j["b"]) for j in plan["jumpers"]})
    expected_rows.update({l["id"]: (l["hole"], l["node"]) for l in plan["leads"]})
    expected_rows.update({f"E{i + 1}": tuple(pair) for i, pair in enumerate(plan["external_wires"])})
    actual_rows = {row["item"]: (row["from"], row["to"]) for row in table}
    if len(actual_rows) != len(table) or actual_rows != expected_rows:
        errors.append("Printed placements CSV differs from planned holes and external wire endpoints")
    if errors:
        raise LayoutError("\n".join(errors))
    return {"gangs": gangs, "svg_holes": len(holes), "svg_wires": len(actual_paths),
            "svg_terminals": len(drawn_terminals), "svg_pico_pins": 40,
            "physical_build_verified": False,
            "scope": "Actual SVG wire strokes/endpoints, drawn pins/holes, WAGO port use and placements table; not physical or powered verification"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", type=Path, default=LAYOUT)
    parser.add_argument("--harness", type=Path, default=HARNESS)
    parser.add_argument("--render-dir", type=Path, default=LAYOUT.parent)
    parser.add_argument("--skip-render", action="store_true", help="Check layout only while regenerating drawing assets")
    args = parser.parse_args()
    try:
        layout, harness = json.loads(args.layout.read_text()), json.loads(args.harness.read_text())
        reports = [validate_layout(layout, harness, gangs) for gangs in (1, 2)]
        rendered = []
        if not args.skip_render:
            for gangs in (1, 2):
                rendered.append(validate_render(layout, harness,
                    (args.render_dir / f"breadboard-{gangs}-servo.svg").read_text(),
                    json.loads((args.render_dir / f"render-map-{gangs}.json").read_text()),
                    (args.render_dir / f"placements-{gangs}-servo.csv").read_text(), gangs))
    except (LayoutError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"AA demo verification failed:\n{error}\n")
    for r in reports:
        print(f"{r['gangs']}-servo: {r['terminals']} terminals, {r['nets']} nets, "
              f"{r['occupied_holes']} occupied holes, {r['occupied_connector_ports']}/{r['connector_ports']} WAGO ports occupied; unused Pico pins isolated.")
    for r in rendered:
        print(f"{r['gangs']}-servo SVG: {r['svg_wires']} actual wire paths, {r['svg_holes']} holes and all Pico/connector endpoints checked.")
    print("Unpowered connectivity passed. Physical assembly, voltage, load and runtime tests remain required.")


if __name__ == "__main__":
    main()
