"""Read the saved Blender assembly and exported STL triangles independently.
Usage: blender --background generated/auto-switch.blend --python audit_fit.py
Checks nominal purchased-part geometry against actual exported print meshes and
probes actual holes/ports; it does not certify physical fit or electrical layout.
"""
import bpy, bmesh, csv, hashlib, json, math, struct
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generated'
C=json.loads((ROOT/'config.json').read_text())
CHECKS=[]
def result(name,passed,detail,**extra):
    row=dict(name=name,passed=bool(passed),detail=detail,**extra);CHECKS.append(row);return row

def read_stl(path,matrix):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    verts=[];faces=[];cache={}
    for i in range(n):
        row=struct.unpack_from('<12fH',data,84+i*50);face=[]
        for j in (3,6,9):
            xyz=tuple(row[j:j+3])
            if xyz not in cache:cache[xyz]=len(verts);verts.append(matrix @ Vector(xyz))
            face.append(cache[xyz])
        faces.append(face)
    mesh=bpy.data.meshes.new('AUDIT STL '+path.stem);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(ob);ob.hide_render=True
    tree=BVHTree.FromPolygons(verts,faces,all_triangles=True)
    return ob,tree

def bbox(ob):
    pts=[ob.matrix_world @ Vector(v) for v in ob.bound_box]
    return [min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]
def crosses(a,b):
    aa,ab=bbox(a);ba,bb=bbox(b)
    return all(min(ab[i],bb[i])-max(aa[i],ba[i])>.02 for i in range(3))
def volume_intersection(a,b):
    dup=a.copy();dup.data=a.data.copy();bpy.context.scene.collection.objects.link(dup)
    bpy.context.view_layer.objects.active=dup
    mod=dup.modifiers.new('audit nominal part against exported STL','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(dup.data);value=abs(bm.calc_volume());bm.free()
    mesh=dup.data;bpy.data.objects.remove(dup,do_unlink=True);bpy.data.meshes.remove(mesh)
    return value

def vertical_surface(tree,x,y,z=60):
    hit=tree.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),100)
    return None if hit[0] is None else float(hit[0].z)

def is_empty_segment(tree,a,b):
    a=Vector(a);b=Vector(b);delta=b-a
    hit=tree.ray_cast(a,delta.normalized(),delta.length)
    return hit[0] is None

printed_by_g={}
for gang in (1,2):
    col=bpy.data.collections[f'{gang}-gang source-dimensioned assembly']
    printed={}
    for o in col.objects:
        if o.get('role')!='printed' or 'coupon' in o.get('print_name','') or 'fit_ring' in o.get('print_name',''):continue
        arr=list(o['stl_to_world']);matrix=Matrix([arr[i:i+4] for i in range(0,16,4)])
        key=o['print_name'];ob,tree=read_stl(OUT/(key+'.stl'),matrix)
        printed.setdefault(key,[]).append((ob,tree))
    printed_by_g[gang]=printed
    # Ignore cosmetic pad artwork and illustrative wires: these are not routed harnesses.
    components=[]
    for o in col.objects:
        if o.type!='MESH' or not o.get('component_group') or o.get('role') not in ('fixed','moving'):continue
        if o.name.startswith(('HARNESS','COMPONENT perfboardpad','COMPONENT regulator solderpad','COMPONENT2810pad')):continue
        if o.name.startswith(('COMPONENT existing wallplate','COMPONENT installed rocker')):continue
        components.append(o)
    clashes=[];tested=0
    for component in components:
        for name,entries in printed.items():
            for ob,tree in entries:
                if not crosses(component,ob):continue
                v=volume_intersection(component,ob);tested+=1
                if v>.05:clashes.append({'component':component.name,'group':component.get('component_group'),'stl':name+'.stl','intersection_mm3':round(v,4)})
    result(f'{gang}-gang nominal component meshes versus exported STLs',not clashes,
           'Exact Boolean volume intersections after bounding-box filtering; >0.05 mm³ reported. Coplanar seating contact allowed. Geometry is nominal; unidentified servo and cosmetic internal details remain provisional.',
           component_meshes=len(components),candidate_intersections_tested=tested,clashes=clashes)
printed=printed_by_g[1]
# Direct STL ray probes establish holes at correct coordinates and supporting rims.
cx=-160;ph=C['plate_height']+2*C['plate_clearance_per_side'];py=ph/2+20+C['pod_internal_height']/2+2
px,sy,z=C['layout']['pico'];px+=cx;sy+=py
pod,podtree=printed['electronics_pod'][0]
postrows=[]
for hx in(-23.5,23.5):
    for hy in(-5.7,5.7):
        center=vertical_surface(podtree,px+hx,sy+hy)
        radii=[vertical_surface(podtree,px+hx+dx,sy+hy+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)]]
        good=center is not None and center<4 and all(v is not None and abs(v-z)<.03 for v in radii)
        postrows.append(dict(center_xy_mm=[round(px+hx,3),round(sy+hy,3)],pilot_bottom_z_mm=center,rim_heights_z_mm=radii,passed=good))
result('Pico four M2 pilot holes and support rims in pod STL',all(x['passed'] for x in postrows),'47×11.4mm source pitch; nominal 1.6 mm pilot must be tapped M2×0.4. Probes verify center cavity and support at 1 mm radius.',posts=postrows)
# Check USB clearance using actual port at right wall and a grid inside plug reserve.
end=cx+C['pod_internal_width']/2+5;start=px+26.85+.1;usbz=z+2
usb=[]
for dy in(-6.9,0,6.9):
    for dz in(-5.9,0,5.9):usb.append(is_empty_segment(podtree,(start,sy+dy,usbz+dz),(end,sy+dy,usbz+dz)))
result('USB insertion rays through exported pod wall',all(usb),'Nine rays sample a 14×12 mm provisional plug corridor from socket mouth to exterior. Actual cable molded shell and neck length still require measurement.',rays_passed=sum(usb),rays_total=len(usb))
# Positive and negative controls catch an all-zero or wrongly transformed Boolean test.
bpy.ops.mesh.primitive_cube_add(size=1,location=(cx,py,2));control=bpy.context.object;control.dimensions=(2,2,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
positive=volume_intersection(control,pod);control.location.z=30
negative=volume_intersection(control,pod);bpy.data.objects.remove(control,do_unlink=True)
result('STL collision detector controls',abs(positive-4)<.02 and negative<.01,'Known 4 mm³ probe inside floor must intersect; same probe in free air must not.',positive_volume_mm3=positive,negative_volume_mm3=negative)
# Actual solders are unknown; verify reserved volume corners/centre clear of pod.
solder=[]
for dx in(-18,0,18):
    for dy in(-11,0,11):
        solder.append(is_empty_segment(podtree,(px+2+dx,sy+dy,5.1),(px+2+dx,sy+dy,7.9)))
result('Headerless underside solder reserve probes',all(solder),'Nine vertical rays in 3 mm design reserve; excludes mounting rims. Actual solder/wire routing must be checked.',rays_passed=sum(solder),rays_total=len(solder))
# Nominal volume for loaded holder checked against actual STL, not just pod bounds.
bx,by,bz=C['layout']['battery'];bx+=cx;by+=py
bpy.ops.mesh.primitive_cube_add(size=1,location=(bx,by,bz+11));probe=bpy.context.object;probe.dimensions=(63,58,22);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
v=volume_intersection(probe,pod);bpy.data.objects.remove(probe,do_unlink=True)
result('Loaded-holder reserved body versus actual pod STL',v<.05,'63×58×22mm allowance, not measured loaded holder. Nominal feet meet its base; locators remain outside.',intersection_mm3=round(v,4))
# Probe every modeled fuse/harness tie passage in the actual pod export.
fx,fy,fz=C['layout']['fuse'];fx+=cx;fy+=py
anchor_rays=[]
for dx in(-8,8):
    for dy in(-14,14):
        for zz in(6.0,7.0,8.0):anchor_rays.append(is_empty_segment(podtree,(fx+dx-3.2,fy+dy,zz),(fx+dx+3.2,fy+dy,zz)))
for xx,yy in[(0,-68),(-8,30),(3,-15),(58,-22)]:
    for zz in(6.0,7.0,8.0):anchor_rays.append(is_empty_segment(podtree,(cx+xx,py+yy-2.7,zz),(cx+xx,py+yy+2.7,zz)))
result('Fuse and harness tie channel probes',all(anchor_rays),'Twenty-four rays sample the paired fuse eyes and four wire-tie eyes. Chosen 2.5 mm ties use nominal 3.5×2.4 mm openings; latch heads and actual routes remain a physical check.',rays_passed=sum(anchor_rays),rays_total=len(anchor_rays))
cap=[o for o in bpy.data.collections['1-gang source-dimensioned assembly'].objects if o.name.startswith('KEEPOUT 470uF maximum seated allowance')][0]
cap_intersections=[volume_intersection(cap,ob) for entries in printed_by_g[1].values() for ob,_ in entries if crosses(cap,ob)]
result('Capacitor maximum seated height allowance',all(v<.05 for v in cap_intersections),'9×9×13mm reserve above PCB, including the 13 mm maximum seated height rather than only 11.5 mm nominal can height.',intersection_volumes_mm3=cap_intersections)
# Shaft length beneath bearing face must leave a closed back and sufficient thread.
result('Selected Pico screw depth',abs((z+1-6)-3)<.01,'M2×6 screw begins at PCB top 9 mm; tip at 3 mm leaves 3 mm between tip and wall-side back. Pilot bottom is 2.5 mm, leaving 0.5 mm screw-tip allowance; pre-tap without piercing the closed back.')
# BOM coverage and quantities; purchasing items are not automatically approved by a mesh pass.
with (ROOT.parent/'bom.csv').open() as source: rows=list(csv.DictReader(source))
missing=[]
for row in rows:
    for name in filter(None,row['stl_files'].split(';')):
        if not (OUT/name).is_file():missing.append({'part':row['id'],'missing_stl':name})
result('Every BOM STL reference exists',not missing,'Reads hardware/bom.csv directly; coupons are reference artifacts and not installed duplicates.',missing=missing)
installed_counts={}
for gang,printed in printed_by_g.items():
    counts={name+'.stl':len(entries) for name,entries in printed.items()}
    installed_counts[str(gang)]=counts
    result(f'{gang}-gang installed print quantity map',counts.get('docking_strap.stl')==2 and len(counts)==8+gang,
           'One surround, one yoke per servo, pod, lid, four retainers, and two docking straps.',counts=counts)
# Hash evidence ties the report to files actually checked.
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.stl'))}
report={'revision':C.get('revision'),'automated_checks_passed':all(x['passed'] for x in CHECKS),'physical_fit_verified':False,
        'installed_print_counts':installed_counts,'checks':CHECKS,'stl_sha256':files,'bom_sha256':hashlib.sha256((ROOT.parent/'bom.csv').read_bytes()).hexdigest(),
        'limits':['Both assembled gang variants tested at neutral; complete dynamic motion is not collision solved.',
                  'Nominal component geometry is not proof of manufacturing tolerance, actual servo/horn fit, all wire routing, thermal performance, or printed thread strength.',
                  'Full electrical board pad routing and complete wire harness placement are not modeled.',
                  'Screw threads and all fastener bodies are not modeled; selected interfaces use nominal hole/depth checks.',
                  'Current textured-wall mounting and exact horn-to-yoke fasteners remain unresolved.'],
        'input_sha256':{str(p.relative_to(ROOT.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'audit_fit.py',ROOT/'generate.py',ROOT/'component_models.py',ROOT/'fit_model.py',ROOT/'config.json',OUT/'auto-switch.blend',ROOT.parent/'components/power-parts.json']},
        'remaining_measurements':C['required_checks_before_print'],'purchased_part_count':len(rows)}
(OUT/'bom-fit-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if not report['automated_checks_passed']:raise RuntimeError('BOM/STL nominal checks failed; see generated/bom-fit-report.json')
