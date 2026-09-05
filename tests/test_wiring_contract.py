"""Cross-check published assembly nets against firmware and supply isolation.

Physical pin mapping: Raspberry Pi Pico W / Pico 2 W official pinout.
These checks cannot replace continuity, polarity, or powered bench tests.
"""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WiringContractTests(unittest.TestCase):
    def setUp(self):
        self.harness = json.loads((ROOT / "hardware/wiring/harness.json").read_text())
        self.nets = self.harness["nets"]
        self.config = json.loads((ROOT / "firmware/config.example.json").read_text())

    def test_documented_gpio_physical_pins_match_default_firmware(self):
        # Physical pin numbers are not interchangeable with GPIO numbers.
        physical = {15: 20, 16: 21, 17: 22, 26: 31}
        expected = [("SERVO_ENABLE", self.config["power_enable_pin"])]
        expected += [("PWM%d_RAW" % i, channel["pin"])
                     for i, channel in enumerate(self.config["channels"])]
        for net, gpio in expected:
            self.assertIn("PICO.pin%d_GP%d" % (physical[gpio], gpio), self.nets[net])
        self.assertIn("PICO.pin31_GP26", self.nets["ADC"])
        self.assertIn("PICO.pin39_VSYS", self.nets["VSYS"])
        self.assertIn("PICO.pin38_GND", self.nets["GND"])

    def test_or_diode_clamp_and_divider_use_correct_supply_branches(self):
        self.assertIn("D1.anode", self.nets["5V"])
        self.assertIn("D1.cathode", self.nets["VSYS"])
        self.assertNotIn("PICO.pin39_VSYS", self.nets["SERVO_5V"])
        self.assertIn("D2.anode", self.nets["GND"])
        self.assertIn("D2.cathode", self.nets["SERVO_5V"])
        self.assertIn("MASTER.VOUT", self.nets["PACK_SW"])
        self.assertIn("REG.VIN", self.nets["PACK_SW"])
        self.assertIn("R_TOP.1", self.nets["PACK_SW"])
        self.assertIn("R_TOP.2", self.nets["ADC"])
        self.assertIn("R_BOTTOM.1", self.nets["ADC"])
        self.assertIn("R_BOTTOM.2", self.nets["GND"])
        self.assertIn("GATE.ON", self.nets["SERVO_ENABLE"])
        self.assertIn("R_EN.1", self.nets["SERVO_ENABLE"])
        self.assertIn("R_EN.2", self.nets["GND"])
        self.assertIn("REG.ENABLE", self.harness["leave_unconnected"])
        self.assertIn("MASTER.ON", self.harness["leave_unconnected"])
        self.assertIn("PICO.pin40_VBUS", self.harness["leave_unconnected"])
        self.assertIn("PICO.pin36_3V3_OUT", self.harness["leave_unconnected"])

    def test_no_endpoint_has_two_net_assignments(self):
        seen = set()
        for net, terminals in self.nets.items():
            for terminal in terminals:
                self.assertNotIn(terminal, seen, (net, terminal))
                seen.add(terminal)
        self.assertFalse(seen.intersection(self.harness["leave_unconnected"]))


if __name__ == "__main__":
    unittest.main()
