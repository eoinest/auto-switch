"""Validate BOM quantities/references and fail on stale actual-STL audit evidence.
Run from any directory: python3 tools/verify_bom.py
"""
import csv, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cad/generated'

def validate(root=ROOT):
    out=root/'hardware/cad/generated'
    with (root/'hardware/bom.csv').open() as source: rows=list(csv.DictReader(source))
    by_id={r['id']:r for r in rows}
    errors=[]
    if len(by_id)!=len(rows):errors.append('BOM ids are not unique')
    for row in rows:
        for k in ['quantity_one_gang','quantity_two_gang']:
            try:
                if int(row[k])<0:raise ValueError()
            except ValueError:errors.append(f'{row["id"]}: invalid {k}')
        if not row['fit_status'] or not row['notes']:errors.append(row['id']+': missing limitations')
        for name in filter(None,row['stl_files'].split(';')):
            if not (out/name).is_file():errors.append(row['id']+': missing '+name)
    manifest=json.loads((root/'hardware/components/power-parts.json').read_text())
    for p in manifest['parts']:
        if p['id'] in ('servo_headers','cells_and_charger'):continue
        if p['id'] not in by_id:errors.append('Selected part absent from BOM: '+p['id']);continue
        for k in ['quantity_one_gang','quantity_two_gang']:
            if int(by_id[p['id']][k])!=p[k]:errors.append(p['id']+': quantity differs from component manifest')
    if 'pico_socket_carrier' in by_id:errors.append('Obsolete socket carrier in current BOM')
    if int(by_id['aa_cells']['quantity_one_gang'])!=4 or int(by_id['aa_cells']['quantity_two_gang'])!=4:errors.append('Four cells required per device')
    for key,multiplier in [('servo',1),('stock_horn',1),('stock_shaft_screw',1),('horn_yoke_screws',2)]:
        if int(by_id[key]['quantity_one_gang'])!=multiplier or int(by_id[key]['quantity_two_gang'])!=2*multiplier:errors.append(key+': actuator quantity mismatch')
    per_unit=manifest['mechanical_hardware']['per_unit']
    aliases={'holder_ties_2_5x200':'holder_ties'}
    for key,count in per_unit.items():
        row=by_id[aliases.get(key,key)]
        if int(row['quantity_one_gang'])!=count or int(row['quantity_two_gang'])!=count:errors.append(key+': mechanical quantity mismatch')
    for key,count in manifest['mechanical_hardware']['per_servo'].items():
        row=by_id[key]
        if int(row['quantity_one_gang'])!=count or int(row['quantity_two_gang'])!=2*count:errors.append(key+': per-servo quantity mismatch')
    report=json.loads((out/'bom-fit-report.json').read_text())
    if not report['automated_checks_passed']:errors.append('Actual STL audit reports failed checks')
    if report['physical_fit_verified'] is not False:errors.append('Unmeasured hardware must not be labelled physically verified')
    for name,expected in report['stl_sha256'].items():
        if hashlib.sha256((out/name).read_bytes()).hexdigest()!=expected:errors.append('Stale fit report: '+name)
    if hashlib.sha256((root/'hardware/bom.csv').read_bytes()).hexdigest()!=report['bom_sha256']:errors.append('Stale BOM hash in fit report')
    for relative,expected in report['input_sha256'].items():
        if hashlib.sha256((root/relative).read_bytes()).hexdigest()!=expected:errors.append('Stale audit input: '+relative)
    stls={p.name for p in out.glob('*.stl')}
    if stls!=set(report['stl_sha256']):errors.append('Fit report STL set differs from current exports')
    for gang,counts in report['installed_print_counts'].items():
        if counts.get('docking_strap.stl')!=2:errors.append('Each device needs two docking straps')
        expected=int(gang)
        yokes=sum(q for name,q in counts.items() if name.endswith('_yoke.stl'))
        if yokes!=expected:errors.append('Wrong yoke print quantity for '+gang+' gang')
    return errors

if __name__=='__main__':
    errors=validate()
    if errors:raise SystemExit('\n'.join(errors))
    print('BOM quantities, current STL references and saved mesh-audit hashes verified.')
