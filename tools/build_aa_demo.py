#!/usr/bin/env python3
"""Bundle AA demo assets for the existing local learning server."""
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'learn/assets/aa-demo'
OUT.mkdir(parents=True, exist_ok=True)
for p in (ROOT/'hardware/wiring/aa-demo').glob('*'):
    if p.suffix in ('.svg','.json','.csv','.png'):
        shutil.copyfile(p,OUT/p.name)
for src,name in [('docs/aa-demo-shopping.md','shopping.md'),
                 ('docs/aa-demo-plan.md','guide.md'),
                 ('docs/poc-wiring.md','poc-wiring.md'),
                 ('docs/poc-wiring.txt','poc-wiring.txt'),
                 ('docs/aa-demo-cost.md','aa-demo-cost.md'),
                 ('hardware/aa-demo-bom.csv','bom.csv'),
                 ('firmware/config.aa-demo.example.json','config.example.json')]:
    shutil.copyfile(ROOT/src,OUT/name)
with (ROOT/'hardware/aa-demo-bom.csv').open() as stream:
    rows=list(csv.DictReader(stream))
(OUT/'bom.json').write_text(json.dumps(rows,indent=2)+'\n')
print(f'Bundled {len(rows)} BOM rows and AA demo diagram assets')
