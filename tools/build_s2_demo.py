#!/usr/bin/env python3
"""Bundle the S2 POC static page assets; no third-party geometry redistributed."""
import shutil
import zipfile
import re
from pathlib import Path
from render_s2_demo import render
ROOT=Path(__file__).resolve().parents[1]
render()
web=ROOT/'learn/assets/s2-aa-poc'
cad=ROOT/'hardware/cad/s2-aa-poc/generated'
for src,dst in [(ROOT/'docs/s2-aa-poc.md','guide.md'),(ROOT/'docs/s2-aa-mechanical.md','mechanics.md'),(cad/'assembly-preview.png','assembly-preview.png'),(cad/'s2-aa-prototype.blend','s2-aa-prototype.blend')]:
    if src.suffix=='.md':
        def link(m):
            target=m.group(2)
            if '://' in target or target.startswith('#'):return m.group(0)
            relative=(src.parent/target).resolve().relative_to(ROOT)
            return f'[{m.group(1)}](https://github.com/eoinest/auto-switch/blob/main/{relative.as_posix()})'
        (web/dst).write_text(re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,src.read_text()))
    else:shutil.copy2(src,web/dst)
with zipfile.ZipFile(web/'stls.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(cad.glob('*.stl')):z.write(p,p.name)
    z.write(ROOT/'docs/s2-aa-mechanical.md','READ-ME-FIRST.md')
print('Bundled S2 map, guides, Blender file and six STLs. Rasterize SVG for PNG if changed.')
