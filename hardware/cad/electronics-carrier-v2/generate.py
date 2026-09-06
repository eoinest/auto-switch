"""Electronics-only fit-test revision. Blender units are mm. Original CAD is preserved.
Run Blender --background --factory-startup --python this/file.py.
No component schematic detail is asserted by the reference envelopes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cadlib import *

for group in ('tray', 'holder', 's2', 'converter', 'ties'):
    for key, value in C[group].items():
        if isinstance(value, (int, float)):
            assert math.isfinite(value) and value > 0, (group, key)
assert C['converter']['width'] is None, 'Implement an inspected module insert before claiming exact fit'
assert C['ties']['slot_width'] > C['ties']['nominal_width']
assert C['s2']['underside_clearance'] > C['s2']['solder_allowance']

assembly = bpy.data.collections.new('ELECTRONICS_V2_ASSEMBLY')
scene.collection.children.link(assembly)
coupons = bpy.data.collections.new('ELECTRONICS_V2_COUPONS')
scene.collection.children.link(coupons)
presentation = bpy.data.collections.new('ELECTRONICS_V2_PRESENTATION')
scene.collection.children.link(presentation)
def move_to(o, collection):
    for old in list(o.users_collection): old.objects.unlink(o)
    collection.objects.link(o)
    return o
def reference(o, confidence):
    o['role'] = 'reference_only'; o['confidence'] = confidence
    move_to(o, assembly)
    return o
def note(text, loc, size=3):
    bpy.ops.object.text_add(location=loc)
    o=bpy.context.object; o.name='NOTE '+text; o.data.body=text; o.data.size=size
    o.data.materials.append(BLACK); move_to(o, presentation)
def printable(o, name, collection=assembly):
    o['role']='print'; move_to(o, collection); export(o, name)
    return o

tw=C['tray']['width']; th=C['tray']['height']; floor=C['tray']['floor']
tray=box('PRINT electronics carrier v2', (0,0,floor/2), (tw,th,floor), TEAL)
slot_specs=[]
def through_slot(center, width, straight, purpose):
    x,y=center
    # Full-depth cutter passes above every rest/locator, not merely through the floor.
    cut(tray,(x,y,10),(width,straight,40))
    for dy in (-straight/2,straight/2): drill(tray,(x,y+dy,10),width/2,40)
    edge=min(tw/2-abs(x)-width/2, th/2-abs(y)-(straight+width)/2)
    assert edge >= C['minimum_edge_ligament'], (purpose, edge)
    slot_specs.append(dict(center_mm=[x,y],width_mm=width,straight_length_mm=straight,
                           minimum_edge_ligament_mm=round(edge,3),purpose=purpose))

b=C['holder']; bx,by=b['center']; bw=b['width']; bh=b['height']; gap=b['clearance_each_side']
# Low side locators and broad floor-supported saddles; full holder lifts out for switch/lid access.
for dx in (-bw/2-gap-1.5,bw/2+gap+1.5):
    boolean(tray,box('holder side locator',(bx+dx,by,5.5),(3,bh+2*gap+6,5.4)),'UNION')
for dy in (-bh/2-gap-1.5,bh/2+gap+1.5):
    lip=box('holder end locator',(bx,by+dy,4.5),(bw+2*gap,3,3.4))
    cut(lip,(bx,by+dy,6),(22,5,6)); boolean(tray,lip,'UNION')
for dx in (-22,22):
    boolean(tray,box('holder saddle',(bx+dx,by,4.4),(7,bh,3.2)),'UNION')
    for dy in (-bh/2-9,bh/2+9): through_slot((bx+dx,by+dy),4.5,2,'holder strap')
reference(box('REF holder nominal envelope',(bx,by,6+b['depth']/2),(bw,bh,b['depth']),BLACK),b['source'])
# Do not invent the switch location or imply its back is accessible while strapped in.

s=C['s2']; sx,sy=s['center']; sw=s['width']; sh=s['height']; pcbz=floor+s['underside_clearance']
# These rests contact the outer corners beyond the nominal plated-row ends (+/-8.89mm).
# Their exact footprint still needs underside inspection of the user's clone.
rest_footprints=[]
for dx in (-sw/2+1.5,sw/2-1.5):
    for dy in (-sh/2+2,sh/2-2):
        boolean(tray,box('S2 corner rest',(sx+dx,sy+dy,(pcbz+floor-.05)/2),(2.4,3,pcbz-floor+.05)),'UNION')
        rest_footprints.append([sx+dx,sy+dy,2.4,3])
for dx in (-sw/2-5,sw/2+5): through_slot((sx+dx,sy),C['ties']['slot_width'],14,'S2 adjustable retention; inspect top components')
purple=material('S2 purple',(.3,.075,.46))
reference(box('REF headerless S2 PCB',(sx,sy,pcbz+s['pcb_thickness']/2),(sw,sh,s['pcb_thickness']),purple),s['source'])
# USB opening is on positive Y, away from the battery. Connector body is illustrative.
reference(box('REF USB C outward',(sx,sy+sh/2-2.5,pcbz+3.2),(9,7,3.2),GREY),'Illustrative connector envelope; verify plug')
plug=reference(box('KEEP OUT illustrative USB plug',(sx,sy+sh/2+11,pcbz+3),(12,20,10),GOLD),'20mm axial plug allowance, not a source-matched cable')
mod=plug.modifiers.new('wireframe keepout','WIREFRAME'); mod.thickness=.3
service=reference(box('KEEP OUT S2 wire service',(sx+sw/2+4,sy-9,pcbz+1),(8,10,5),GOLD),'8mm outward wire service loop allowance')
mod=service.modifiers.new('wireframe service space','WIREFRAME'); mod.thickness=.3
for dy in (-5,5): through_slot((-8,25+dy),C['ties']['slot_width'],2,'solder harness strain relief')

c=C['converter']; cx,cy=c['center']; cw=c['reserved_width']; ch=c['reserved_height']
# Continuous insulating support area accommodates smaller modules too. There is no pair
# of edge rails which a 30mm module would fail to span, and no guessed mounting holes.
for dx in (-cw/2-5,cw/2+5): through_slot((cx+dx,cy),C['ties']['slot_width'],22,'converter universal straps; insulating spacer pending')
pink=material('Unknown converter',(.8,.15,.4))
reserve=reference(box('KEEP OUT converter UNMEASURED',(cx,cy,floor+c['reserved_depth']/2),(cw,ch,c['reserved_depth']),pink),'Reserved volume only. Actual converter dimensions unknown; underside spacer/retention unresolved.')
mod=reserve.modifiers.new('wireframe unmeasured reserve','WIREFRAME'); mod.thickness=.45
tray.data.materials.clear(); tray.data.materials.append(TEAL)
for face in tray.data.polygons: face.material_index=0
printable(tray,'electronics_carrier_v2_DRAFT_FIT_TEST')

# Cheap silhouette ring checks the battery dimension before a large tray print.
coupon=box('PRINT holder fit ring',(0,0,1),(bw+2*gap+6,bh+2*gap+6,2),TEAL)
cut(coupon,(0,0,1),(bw+2*gap,bh+2*gap,6))
printable(coupon,'holder_fit_ring',coupons); coupon.hide_render=True; coupon.hide_set(True)
# A separate support coupon duplicates the PCB corner rests, including solder clearance.
coupon=box('PRINT S2 corner support coupon',(0,0,1.5),(sw+10,sh+10,3),TEAL)
for dx in (-sw/2+1.5,sw/2-1.5):
    for dy in (-sh/2+2,sh/2-2): boolean(coupon,box('coupon corner',(dx,dy,6.475),(2.4,3,7.05)),'UNION')
printable(coupon,'s2_corner_support_coupon',coupons); coupon.hide_render=True; coupon.hide_set(True)

# Independently ray-test every slot center: no concealed rail/roof may block it.
deps=bpy.context.evaluated_depsgraph_get(); deps.update()
evaluated=tray.evaluated_get(deps)
blocked=[]
for spec in slot_specs:
    x,y=spec['center_mm']; hit,*_=evaluated.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))
    if hit: blocked.append(spec['purpose']+str(spec['center_mm']))
assert not blocked, blocked
# Analytic non-overlap of component envelopes, with USB-facing clear route.
battery_top_y=by+bh/2; s2_bottom_y=sy-sh/2
assert s2_bottom_y > battery_top_y
assert sx+sw/2+s['wire_service_clearance'] < cx-cw/2
usb_bounds=[sx-6,sx+6,sy+sh/2+1,sy+sh/2+21]
assert usb_bounds[2] > battery_top_y
assert min(r[1]-r[3]/2-sy for r in rest_footprints if r[1]>sy) > 8.89+.7
report={
 'status': 'DRAFT FIT TEST ONLY; not physical fit approval', 'parts':REPORT,
 'physical_fit_verified':False,
 'measured_component_dimensions':[],
 'slot_center_rays_clear':not blocked,'slots':slot_specs,
 'all_prints_single_closed_component':True,
 'holder_clearance_each_side_mm':gap,
 'holder_access':'Lift out after removing straps for back switch and screw cover',
 'S2_underside_clearance_mm':s['underside_clearance'],
 'S2_solder_allowance_mm':s['solder_allowance'],
 'S2_corner_rest_footprints_mm':rest_footprints,
 'S2_corner_rests_clear_nominal_pad_rows':True,
 'S2_to_holder_gap_mm':round(s2_bottom_y-battery_top_y,3),
 'USB_faces_outboard':'positive Y; reserved plug extends beyond tray into free space',
 'USB_illustrative_keepout_XY_mm':usb_bounds,
 'converter':{'dimensions':None,'reserve_mm':[cw,ch,c['reserved_depth']],
              'requires':'Measure actual board and underside components, choose insulating spacer and strap path. The flat floor is not a finished converter mount.'},
 'retention_not_verified':['S2 top strap path and actual underside keepouts','converter spacer and strap path','holder switch/lid/lead location'],
 'mounting':'Independent bench tray. No wall adhesive mounting or Command-strip compatibility claimed.',
 'print_orientation':'Flat floor at Z0, supports rise vertically; through slots open on both faces.'
}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
note('ELECTRONICS CARRIER V2 / FIT TEST',(-60,-92,0),3)
note('Converter and physical fit pending',(-60,-98,0),2.6)
note('USB exits outward',(-58,78,0),2.3)
note('UNMEASURED\nCONVERTER',(cx-15,cy-4,23),2.3)
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for loc in ((-90,-80,180),(100,60,150)):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=150000;o.data.size=150;move_to(o,presentation)
bpy.ops.object.camera_add(location=(140,-210,270));cam=bpy.context.object;move_to(cam,presentation)
cam.rotation_euler=(Vector((0,-5,5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=230;scene.camera=cam
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');tray.select_set(True);bpy.context.view_layer.objects.active=tray
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'electronics-carrier-v2.blend'))
scene.render.filepath=str(OUT/'electronics-carrier-v2.png');bpy.ops.render.render(write_still=True)
print(json.dumps(report,indent=2))
