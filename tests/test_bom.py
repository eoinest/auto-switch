"""BOM checks catch missing purchases, stale mesh evidence and unsafe fit claims."""
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('verify_bom',ROOT/'tools/verify_bom.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class BOMTests(unittest.TestCase):
    def test_selected_quantities_and_actual_stl_evidence(self):
        self.assertEqual(module.validate(),[])
    def test_changed_purchase_quantity_rejects_stale_evidence(self):
        import csv, tempfile
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);hardware=root/'hardware';hardware.mkdir()
            (hardware/'components').symlink_to(ROOT/'hardware/components',target_is_directory=True)
            (hardware/'cad').symlink_to(ROOT/'hardware/cad',target_is_directory=True)
            with (ROOT/'hardware/bom.csv').open() as f:rows=list(csv.DictReader(f))
            rows[0]['quantity_one_gang']='2'
            with (hardware/'bom.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
            errors=module.validate(root)
            self.assertTrue(any('quantity differs' in error for error in errors))
            self.assertIn('Stale BOM hash in fit report',errors)
    def test_explicit_unresolved_interfaces(self):
        import csv
        with (ROOT/'hardware/bom.csv').open() as f:rows={r['id']:r for r in csv.DictReader(f)}
        for key in ('horn_yoke_screws','wall_mount'):
            self.assertIn('BLOCKED',rows[key]['fit_status'])
        self.assertNotIn('pico_socket_carrier',rows)
        self.assertIn('headerless',rows['pico']['part'])
if __name__=='__main__':unittest.main()
