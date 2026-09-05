#!/usr/bin/env python3
"""Check breadboard copper/wires against the project netlist, without simulating parts.

Each a-e or f-j strip is conductive. Component legs are *not* joined through
resistors, capacitors, diodes, switches, the regulator or Pico internals. Thus
this verifies assembly connectivity, not powered behavior or physical clearance.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "hardware/wiring/breadboard/layout.json"
HARNESS = ROOT / "hardware/wiring/harness.json"


class LayoutError(ValueError):
    """The physical layout does not implement its declared circuit."""


class Conductors:
    def __init__(self):
        self.parent = {}

    def find(self, node):
        self.parent.setdefault(node, node)
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    def join(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def profile(layout, harness, gangs=2):
    """Return independent one/two-servo copies; keep all 40 physical Pico pins."""
    if gangs not in (1, 2):
        raise LayoutError("gangs must be 1 or 2")
    layout, harness = deepcopy(layout), deepcopy(harness)
    if gangs == 1:
        omitted = set(harness["one_gang_omit"])
        def omit_terminal(terminal):
            return terminal.split(".")[0] in omitted or terminal == "PICO.pin22_GP17"
        layout["placements"] = [p for p in layout["placements"] if p["ref"] not in omitted]
        layout["jumpers"] = [j for j in layout["jumpers"] if not j.get("optional")]
        layout["leads"] = [lead for lead in layout["leads"] if not lead.get("optional")]
        layout["terminal_bindings"] = {t: h for t, h in layout["terminal_bindings"].items() if not omit_terminal(t)}
        layout["external_wires"] = [pair for pair in layout["external_wires"] if not any(omit_terminal(t) for t in pair)]
        harness["nets"] = {net: [t for t in terminals if not omit_terminal(t)] for net, terminals in harness["nets"].items()}
        harness["nets"] = {net: terminals for net, terminals in harness["nets"].items() if terminals}
    return layout, harness


def validate_layout(layout, harness, gangs=2):
    layout, harness = profile(layout, harness, gangs)
    errors = []
    board = layout["board"]
    rows, columns = board["rows"], board["columns"]
    groups = board["connected_groups"]
    if rows != 63 or columns != "abcdefghij" or groups != ["abcde", "fghij"]:
        errors.append("Expected the specified 63-row a-e / f-j breadboard topology")
    if board.get("power_rails_used") is not False:
        errors.append("This checker requires unused side power rails")
    if layout.get("harness_revision") != harness.get("revision"):
        errors.append("Layout harness revision is stale")
    circuit = Conductors()
    valid_holes = {f"{column}{row}" for column in columns for row in range(1, rows + 1)}
    for row in range(1, rows + 1):
        for group in groups:
            for column in group:
                circuit.join(f"hole:{column}{row}", f"strip:{group}:{row}")
    occupancy = {}
    conductive_nodes = []

    def hole_node(hole, owner, occupy=True):
        if hole not in valid_holes:
            errors.append(f"Invalid hole {hole!r} for {owner}")
        if occupy:
            if hole in occupancy:
                errors.append(f"Duplicate hole {hole}: {occupancy[hole]} and {owner}")
            else:
                occupancy[hole] = owner
        return f"hole:{hole}"

    expected_pins = {}
    start = board["pico_start_row"]
    left, right = board["pico_columns"]
    if (left, right) != ("c", "h"):
        errors.append("Pico headers must use c/h to match their 17.78 mm separation")
    for offset in range(20):
        expected_pins[str(offset + 1)] = f"{left}{start + offset}"
        expected_pins[str(40 - offset)] = f"{right}{start + offset}"
    if layout["pico_pins"] != expected_pins:
        errors.append("Pico physical pins do not match USB-at-top numbering")
    for pin, hole in layout["pico_pins"].items():
        hole_node(hole, f"PICO physical pin {pin}")

    physical_terminals = {}
    seen_parts = set()
    for part in layout["placements"]:
        if part["ref"] in seen_parts:
            errors.append(f"Duplicate component reference {part['ref']}")
        seen_parts.add(part["ref"])
        for leg, hole in part["terminals"].items():
            terminal = f"{part['ref']}.{leg}"
            physical_terminals[terminal] = hole
            hole_node(hole, terminal)

    terminal_nets = {}
    for net, terminals in harness["nets"].items():
        for terminal in terminals:
            if terminal in terminal_nets:
                errors.append(f"Harness terminal {terminal} appears in multiple nets")
            terminal_nets[terminal] = net
    bindings = layout["terminal_bindings"]
    active_pins = set()
    for terminal in terminal_nets:
        if terminal.startswith("PICO.") and terminal not in bindings:
            errors.append(f"Missing physical Pico binding for {terminal}")
    for terminal, hole in bindings.items():
        if terminal not in terminal_nets:
            errors.append(f"Unexpected bound terminal {terminal}")
        if terminal.startswith("PICO."):
            match = re.fullmatch(r"PICO\.pin(\d+)_.+", terminal)
            pin = match.group(1) if match else None
            if pin is None or layout["pico_pins"].get(pin) != hole:
                errors.append(f"Binding {terminal} does not match its physical Pico pin")
            active_pins.add(pin)
        elif physical_terminals.get(terminal) != hole:
            errors.append(f"Binding {terminal} does not match the component placement")
        circuit.join(f"terminal:{terminal}", hole_node(hole, terminal, occupy=False))
    for terminal, hole in physical_terminals.items():
        if bindings.get(terminal) != hole:
            errors.append(f"Missing or wrong binding for placed terminal {terminal}")

    # External aliases (PACK/P5V/PGND/MOTOR) are junctions, not additional parts.
    represented = set(bindings)
    def external(node):
        if "." in node:
            if node in bindings:
                errors.append(f"External wire to bound terminal {node} bypasses hole occupancy; use a lead")
            if node not in terminal_nets:
                errors.append(f"Unexpected external terminal {node}")
            represented.add(node)
            return f"terminal:{node}"
        return f"junction:{node}"

    labels = []
    identifiers = set()
    for jumper in layout["jumpers"]:
        identifier = jumper["id"]
        if identifier in identifiers:
            errors.append(f"Duplicate wire identifier {identifier}")
        identifiers.add(identifier)
        a = hole_node(jumper["a"], f"{identifier}.a")
        b = hole_node(jumper["b"], f"{identifier}.b")
        circuit.join(a, b)
        labels.append((identifier, a, jumper["net"]))
        conductive_nodes.append((identifier, a))
    for lead in layout["leads"]:
        identifier = lead["id"]
        if identifier in identifiers:
            errors.append(f"Duplicate wire identifier {identifier}")
        identifiers.add(identifier)
        a = hole_node(lead["hole"], identifier)
        circuit.join(a, external(lead["node"]))
        labels.append((identifier, a, lead["net"]))
        conductive_nodes.append((identifier, a))
    for index, pair in enumerate(layout["external_wires"]):
        if len(pair) != 2:
            errors.append(f"External wire {index} must have two endpoints")
            continue
        a, b = map(external, pair)
        circuit.join(a, b)
        conductive_nodes.append((f"external wire {index + 1}", a))
    missing = set(terminal_nets) - represented
    if missing:
        errors.append("Missing harness terminals: " + ", ".join(sorted(missing)))

    roots_to_nets = {}
    for terminal, net in terminal_nets.items():
        root = circuit.find(f"terminal:{terminal}")
        roots_to_nets.setdefault(root, set()).add(net)
    for nets in roots_to_nets.values():
        if len(nets) > 1:
            errors.append("Short between nets: " + ", ".join(sorted(nets)))
    for net, terminals in harness["nets"].items():
        roots = {circuit.find(f"terminal:{terminal}") for terminal in terminals}
        if len(roots) != 1:
            errors.append(f"Open circuit: net {net} has {len(roots)} disconnected groups")
    for identifier, node, expected in labels:
        actual = roots_to_nets.get(circuit.find(node), set())
        if actual != {expected}:
            errors.append(f"{identifier} label {expected} disagrees with connected nets {sorted(actual)}")
    for identifier, node in conductive_nodes:
        if circuit.find(node) not in roots_to_nets:
            errors.append(f"Unassigned conductor: {identifier}")
    for pin, hole in layout["pico_pins"].items():
        if pin not in active_pins:
            connected = roots_to_nets.get(circuit.find(f"hole:{hole}"), set())
            if connected:
                errors.append(f"Unused Pico pin {pin} joins active nets {sorted(connected)}")
    if errors:
        raise LayoutError("\n".join(errors))
    return {
        "gangs": gangs,
        "terminals": len(terminal_nets),
        "nets": len(harness["nets"]),
        "occupied_holes": len(occupancy),
        "pico_pins": len(layout["pico_pins"]),
        "jumpers": len(layout["jumpers"]),
        "leads": len(layout["leads"]),
        "physical_build_verified": False,
        "scope": "Breadboard strips and wires only; no component internals or powered simulation",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", type=Path, default=LAYOUT)
    parser.add_argument("--harness", type=Path, default=HARNESS)
    args = parser.parse_args()
    layout = json.loads(args.layout.read_text())
    harness = json.loads(args.harness.read_text())
    try:
        reports = [validate_layout(layout, harness, gangs=gangs) for gangs in (1, 2)]
    except (LayoutError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"Breadboard verification failed:\n{error}\n")
    for report in reports:
        print(f"{report['gangs']}-servo: {report['terminals']} terminals / {report['nets']} nets; "
              f"{report['occupied_holes']} unique occupied holes; unused Pico pins isolated.")
    print("Both layouts match the harness. Physical build and powered tests remain required.")


if __name__ == "__main__":
    main()
