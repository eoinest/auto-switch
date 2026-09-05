#!/usr/bin/env python3
"""Energy budget, not a battery-life guarantee. Currents are user assumptions.

Run from the monorepo root: python3 tools/battery_estimator.py --help
Only standard-library Python is required; this runs on your computer, not Pico.
"""

import argparse
import json
import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Budget:
    cells: int = 4
    cell_voltage: float = 1.2
    capacity_mah: float = 1900
    usable_fraction: float = 0.8
    efficiency: float = 0.85
    rail_voltage: float = 5.0
    active_ma: float = 50
    sleep_ma: float = 10
    wake_ma: float = 80
    # Assumed pack overhead: regulator ~1mA + master-switch LED ~1.008mA
    # at 4.8V + divider ~0.033mA, rounded. Replace with measurements.
    parasitic_pack_ma: float = 2.05
    servo_ma: float = 500
    servo_seconds: float = 1
    actions_per_day: float = 20
    # Zero means always connected. Nonzero models periodic gateway polling.
    interval_seconds: float = 0
    wake_seconds: float = 3


def estimate(budget):
    """Return explicit energy components, duty cycle and conditional runtime."""
    fields = asdict(budget)
    for name, value in fields.items():
        if not math.isfinite(value) or value < 0:
            raise ValueError(name + " must be finite and nonnegative")
    if budget.cells < 1 or int(budget.cells) != budget.cells:
        raise ValueError("cells must be a positive integer")
    for name in ("cell_voltage", "capacity_mah", "rail_voltage"):
        if fields[name] <= 0:
            raise ValueError(name + " must be positive")
    for name in ("usable_fraction", "efficiency"):
        if not 0 < fields[name] <= 1:
            raise ValueError(name + " must be in (0, 1]")
    if budget.active_ma < budget.sleep_ma or budget.wake_ma < budget.sleep_ma:
        raise ValueError("active_ma and wake_ma must be at least sleep_ma")
    actuation_seconds = budget.servo_seconds * budget.actions_per_day
    if actuation_seconds > 86400:
        raise ValueError("actuation time exceeds a day")
    if budget.interval_seconds:
        if budget.wake_seconds <= 0 or budget.wake_seconds > budget.interval_seconds:
            raise ValueError("wake_seconds must be positive and no longer than interval")
        polling_seconds = 86400 * budget.wake_seconds / budget.interval_seconds
        # Conservatively add actuation awake time to polling time; overlap is not assumed.
        awake_seconds = min(86400, polling_seconds + actuation_seconds)
    else:
        awake_seconds = 86400
    duty_cycle = awake_seconds / 86400
    awake_ma = budget.wake_ma if budget.interval_seconds else budget.active_ma
    logic_ma = awake_ma * duty_cycle + budget.sleep_ma * (1 - duty_cycle)
    logic_wh_day = budget.rail_voltage * logic_ma / 1000 * 24
    servo_wh_day = budget.rail_voltage * budget.servo_ma / 1000 * actuation_seconds / 3600
    pack_voltage = budget.cells * budget.cell_voltage
    parasitic_wh_day = pack_voltage * budget.parasitic_pack_ma / 1000 * 24
    nominal_wh = pack_voltage * budget.capacity_mah / 1000
    usable_wh = nominal_wh * budget.usable_fraction
    pack_wh_day = (logic_wh_day + servo_wh_day) / budget.efficiency + parasitic_wh_day
    if pack_wh_day <= 0:
        raise ValueError("a positive load is required to estimate runtime")
    return {
        "assumptions": fields,
        "mode": "always_on" if not budget.interval_seconds else "periodic_polling",
        "nominal_pack_wh": nominal_wh,
        "usable_pack_wh": usable_wh,
        "awake_fraction": duty_cycle,
        "polling_break_even_seconds": (budget.wake_seconds * (budget.wake_ma - budget.sleep_ma)
                                        / (budget.active_ma - budget.sleep_ma)
                                        if budget.active_ma > budget.sleep_ma else None),
        "logic_rail_wh_per_day": logic_wh_day,
        "servo_rail_wh_per_day": servo_wh_day,
        "parasitic_pack_wh_per_day": parasitic_wh_day,
        "total_pack_wh_per_day": pack_wh_day,
        "estimated_days": usable_wh / pack_wh_day,
        "estimated_hours": 24 * usable_wh / pack_wh_day,
        "notice": "Assumption-based energy estimate; not measured runtime. Does not prove peak-current capability.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    defaults = asdict(Budget())
    help_text = {
        "cells": "series cell count (capacity in mAh does not add in series)",
        "capacity_mah": "per-cell capacity in mAh",
        "usable_fraction": "fraction of nominal energy accessible before cutoff (0..1)",
        "efficiency": "load conversion efficiency, parasitics accounted separately (0..1)",
        "active_ma": "logic current at rail voltage while awake (assumed, not specification)",
        "sleep_ma": "logic current at rail voltage during radio-off wait (measure it)",
        "wake_ma": "average logic current during association/polling at rail voltage",
        "parasitic_pack_ma": "extra pack-input current, e.g. regulator quiescent and divider",
        "servo_seconds": "total powered time for press AND return per action",
        "actions_per_day": "total actions across all servos; on and off each count once",
        "interval_seconds": "0=always connected; positive=gateway poll interval",
        "wake_seconds": "association + DHCP + request + retry time per poll",
    }
    for name, value in defaults.items():
        parser.add_argument("--" + name.replace("_", "-"), type=int if name == "cells" else float,
                            default=value, help=help_text.get(name, name.replace("_", " ")))
    parser.add_argument("--json", action="store_true", help="emit all assumptions and components as JSON")
    args = vars(parser.parse_args())
    emit_json = args.pop("json")
    try:
        result = estimate(Budget(**args))
    except ValueError as exc:
        parser.error(str(exc))
    if emit_json:
        print(json.dumps(result, indent=2, allow_nan=False))
    else:
        print(result["notice"])
        print("Mode: " + result["mode"])
        print("Nominal pack: {:.2f} Wh; usable: {:.2f} Wh".format(result["nominal_pack_wh"], result["usable_pack_wh"]))
        print("Awake: {:.2%}; pack energy/day: {:.3f} Wh".format(result["awake_fraction"], result["total_pack_wh_per_day"]))
        print("Conditional runtime: {:.1f} hours ({:.1f} days)".format(result["estimated_hours"], result["estimated_days"]))
        print("Use --json to inspect every assumption; replace defaults with your measurements.")


if __name__ == "__main__":
    main()
