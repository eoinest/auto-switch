"""Keep purchasing quantities and delivered viewer assets tied to the circuit."""
import csv
import io
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class AADemoBOMTests(unittest.TestCase):
    def test_quantities_cover_each_drawn_component(self):
        rows=list(csv.DictReader(io.StringIO((ROOT/'hardware/aa-demo-bom.csv').read_text())))
        bom={r['id']:r for r in rows}
        self.assertEqual(len(rows),len(bom))
        layout=json.loads((ROOT/'hardware/wiring/aa-demo/layout.json').read_text())
        for gangs,column in [(1,'quantity_one_servo'),(2,'quantity_two_servos')]:
            placements=[p for p in layout['placements'] if gangs==2 or not p.get('optional')]
            self.assertEqual(int(bom['R_PWM'][column]),sum(p['type']=='resistor' for p in placements))
            self.assertEqual(int(bom['D1'][column]),sum(p['type']=='diode' for p in placements))
            self.assertEqual(int(bom['servo'][column]),gangs)
            self.assertEqual(int(bom['servo_extension'][column]),gangs)
            self.assertEqual(int(bom['junctions'][column]),len(layout['connector_blocks']))
            for key in ('pico','battery_charger_kit','breadboard','holder','regulator','master','rcy_female','rcy_male','fuse_holder','fuse','C1'):
                self.assertEqual(int(bom[key][column]),1,key)

    def test_bundled_assets_match_sources(self):
        assets=ROOT/'learn/assets/aa-demo'
        for p in (ROOT/'hardware/wiring/aa-demo').iterdir():
            if p.suffix in ('.svg','.json','.csv','.png'):
                self.assertEqual(p.read_bytes(),(assets/p.name).read_bytes(),p.name)
        for source,name in [('hardware/aa-demo-bom.csv','bom.csv'),('docs/aa-demo-shopping.md','shopping.md'),('docs/aa-demo-plan.md','guide.md'),('firmware/config.aa-demo.example.json','config.example.json')]:
            self.assertEqual((ROOT/source).read_bytes(),(assets/name).read_bytes(),name)
        self.assertEqual(json.loads((assets/'bom.json').read_text()),list(csv.DictReader(io.StringIO((ROOT/'hardware/aa-demo-bom.csv').read_text()))))

    def test_example_firmware_uses_drawn_first_channel(self):
        config=json.loads((ROOT/'firmware/config.aa-demo.example.json').read_text())
        layout=json.loads((ROOT/'hardware/wiring/aa-demo/layout.json').read_text())
        self.assertEqual(config['hardware_profile'],'aa-demo')
        self.assertIsNone(config['power_enable_pin'])
        self.assertFalse(config['battery']['enabled'])
        self.assertEqual([c['pin'] for c in config['channels']],[16])
        self.assertEqual(layout['terminal_bindings']['PICO.pin21_GP16'],'h22')
        self.assertFalse(config['channels'][0]['enabled'])
        self.assertFalse(config['channels'][0]['calibrated'])

if __name__=='__main__': unittest.main()
