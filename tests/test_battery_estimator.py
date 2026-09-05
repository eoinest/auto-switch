import math
import unittest
from dataclasses import replace

from tools.battery_estimator import Budget, estimate


class BatteryEstimatorTests(unittest.TestCase):
    def test_watt_hour_reference_and_series_cells(self):
        budget = Budget(cells=4, cell_voltage=1.2, capacity_mah=1000,
                        usable_fraction=1, efficiency=1, active_ma=100,
                        rail_voltage=5, actions_per_day=0, parasitic_pack_ma=0)
        result = estimate(budget)
        self.assertAlmostEqual(result["nominal_pack_wh"], 4.8)
        self.assertAlmostEqual(result["estimated_hours"], 9.6)
        self.assertAlmostEqual(estimate(replace(budget, cells=2))["estimated_hours"], 4.8)

    def test_conversion_loss_does_not_scale_pack_parasitics(self):
        budget = Budget(efficiency=.5, active_ma=0, sleep_ma=0, actions_per_day=0,
                        parasitic_pack_ma=10)
        self.assertAlmostEqual(estimate(budget)["total_pack_wh_per_day"], 4.8 * .01 * 24)

    def test_press_return_energy_is_total_across_channels(self):
        result = estimate(Budget(servo_ma=600, servo_seconds=2, actions_per_day=30))
        self.assertAlmostEqual(result["servo_rail_wh_per_day"], 5 * .6 * 60 / 3600)

    def test_association_cost_and_actuation_awake_time(self):
        result = estimate(Budget(interval_seconds=60, wake_seconds=3,
                                 actions_per_day=20, servo_seconds=1))
        self.assertAlmostEqual(result["awake_fraction"], .05 + 20 / 86400)
        slower = estimate(Budget(interval_seconds=300, wake_seconds=3))
        self.assertGreater(slower["estimated_days"], result["estimated_days"])

    def test_awake_fraction_capped_at_one(self):
        self.assertEqual(estimate(Budget(interval_seconds=3, wake_seconds=3))["awake_fraction"], 1)

    def test_association_break_even_and_radio_off_cost(self):
        budget = Budget(active_ma=50, sleep_ma=10, wake_ma=80,
                        wake_seconds=3, actions_per_day=0)
        always = estimate(budget)
        self.assertAlmostEqual(always["polling_break_even_seconds"], 5.25)
        equivalent = estimate(replace(budget, interval_seconds=5.25))
        self.assertAlmostEqual(always["total_pack_wh_per_day"], equivalent["total_pack_wh_per_day"])
        self.assertLess(estimate(replace(budget, interval_seconds=60))["total_pack_wh_per_day"], always["total_pack_wh_per_day"])

    def test_reject_invalid_and_nonfinite_assumptions(self):
        cases = [{"efficiency": 0}, {"efficiency": 1.1}, {"cells": 0}, {"cells": 1.5},
                 {"capacity_mah": -1}, {"active_ma": math.nan}, {"active_ma": math.inf},
                 {"interval_seconds": 2, "wake_seconds": 3}, {"interval_seconds": 10, "wake_seconds": 0},
                 {"servo_seconds": 86401}, {"usable_fraction": 0}, {"sleep_ma": 51}]
        for values in cases:
            with self.subTest(values=values), self.assertRaises(ValueError):
                estimate(replace(Budget(), **values))


if __name__ == "__main__":
    unittest.main()
