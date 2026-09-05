"""Generate dimensioned Blender assembly, fit coupons, print STLs and fit evidence.
Run with Blender5.2: blender --background --factory-startup --python hardware/cad/generate.py
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
from component_models import *
from fit_model import validate_or_raise, envelope_report
validate_or_raise(C)
PRINTS=[];MOVING=[];FIXTURES=[];COUPONS=[]
POWER=json.loads((ROOT.parent/'components/power-parts.json').read_text())
PARTS={x['id']:x for x in POWER['parts']}

# The manifest is recreated; obsolete v1 STLs are removed, other artifacts preserved.
for old in OUT.glob('*.stl'):old.unlink()

def printable(o,name,rotate=False,export_it=True):
    PRINTS.append(o);o['role']='printed';o['print_name']=name
    if export_it:export(o,name,rotate)
    return o

def hexhole(o,p,across_flats,depth,axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=across_flats/math.sqrt(3),depth=depth,location=p)
    a=bpy.context.object
    if axis=='X':a.rotation_euler[1]=math.pi/2
    boolean(o,a,'DIFFERENCE')

def ring(g,cx,height=9):
    w=C['plate_widths'][str(g)]+2*C['plate_clearance_per_side'];h=C['plate_height']+2*C['plate_clearance_per_side'];t=C['frame_wall']
    o=box('frame',(cx,0,height/2),(w+2*t,h+2*t,height),TEAL)
    cut(o,(cx,0,height/2),(w,h,height+4));return o,w,h

def pod_floor_nut(pod,p):
    # Hexnut drops from the front; backing0.8mm prevents protrusion against wall.
    hexhole(pod,(p[0],p[1],2.8),5.8,2.5)
    drill(pod,(p[0],p[1],2.6),1.65,3.6)

def cradle_parts(x,y,w,h,base,thickness=1.6):
    gap=C['fit_clearance_per_side'];parts=[]
    # Four corner shelves, contact underside, outside columns for removable retainer.
    for sx in(-1,1):
        for sy in(-1,1):
            parts.append(box('board underside shelf',(x+sx*(w/2-1),y+sy*(h/2-2),(base+4)/2),(3,5,base-4)))
            col=cyl('retainer screw pillar',(x+sx*(w/2+4),y+sy*(h/2+4),(base+thickness+.2+4)/2),3,(base+thickness+.2-4))
            # A foot joins the shelf and pillar without touching the PCB.
            parts.append(box('board pillar foot',(x+sx*(w/2+1),y+sy*(h/2+1),5),(8,9,2)))
            parts.append(col)
    return parts

def retainer(x,y,w,h,z,name,master=False,export_it=True):
    o=box('PRINT '+name,(x,y,z+1),(w+14,h+14,2),TEAL)
    cut(o,(x,y,z+1),(w-1.6,h-1.6,4))
    for sx in(-1,1):
        for sy in(-1,1):
            drill(o,(x+sx*(w/2+4),y+sy*(h/2+4),z+1),1.4,5)
    if master:cut(o,(x+w/2+1,y,z+1),(14,10,5))
    printable(o,name,export_it=export_it)
    return o

def coupon_cradle(name,w,h,base=9,thickness=1.6,master=False):
    o=fuse([box('coupon base',(0,0,2),(w+18,h+18,4)),*cradle_parts(0,0,w,h,base,thickness)],'PRINT '+name,TEAL)
    for sx in(-1,1):
        for sy in(-1,1):drill(o,(sx*(w/2+4),sy*(h/2+4),base-1),1,8)
    printable(o,name);o.hide_render=True;o.hide_set(True);COUPONS.append(o)

def servo_model(xc,sign,prefix):
    s=C['servo'];pz=C['pivot_z'];tip=xc+sign*17;basex=tip+sign*s['base_to_shaft_tip'];by=-s['shaft_offset_y'];group=prefix+' MG90S reference'
    # Canonical axial z maps to world X: base farthest out, spline facing paddle.
    main_h=s['lower_case_height'];bodyx=basex-sign*main_h/2
    pb('COMPONENT MG90S lower case',(bodyx,by,pz),(main_h,s['case_length'],s['case_width']),GREY,group,'TowerPro overall dimensions; lower/upper case split unsourced')
    # Visible base cap and gearbox cover seams, within source overallcase dimensions.
    pb('COMPONENT MG90S base cap',(basex-sign*1.2,by,pz),(2.4,s['case_length']+.05,s['case_width']+.05),BLACK,group,'Cosmetic case seam')
    gear_h=s['case_height']-main_h
    pc('COMPONENT MG90S output gearbox',(basex-sign*(main_h+gear_h/2),0,pz),s['case_width']/2,gear_h,'X',GREY,group)
    pc('COMPONENT MG90S secondary gearbox',(basex-sign*(main_h+gear_h/2),by-5.0,pz),4,gear_h,'X',GREY,group)
    earx=basex-sign*(s['base_to_ear_under']+s['ear_thickness']/2)
    ear=box('COMPONENT MG90S mounting ears',(earx,by,pz),(s['ear_thickness'],s['ear_span'],s['case_width']),GREY)
    # Ears span acrosscase, so this is the actual mounting flange, not decorative wings.
    for sy in(-1,1):drill(ear,(earx,by+sy*s['ear_hole_pitch']/2,pz),s['ear_hole_diameter']/2,8,'X')
    tag(ear,group,'TowerPro32.1ear span,18.5base offset; thickness and hole pattern awaiting measurement')
    shaftlen=s['base_to_shaft_tip']-s['case_height']
    pc('COMPONENT MG90S output spline',(tip+sign*shaftlen/2,0,pz),s['shaft_diameter']/2,shaftlen,'X',GOLD,group)
    # Three individual insulated leads exit beyond the lower case and turn away from ears.
    for k,mat in enumerate((WIRE_BLACK,WIRE_RED,WIRE_YELLOW)):
        wire('HARNESS MG90S lead',[(basex-sign*3,by-s['case_length']/2,pz+(k-1)*1.5),(basex-sign*3,by-s['case_length']/2-8,pz+(k-1)*1.5),(basex+sign*5,by-s['case_length']/2-13,pz+(k-1)*1.5)],.65,mat,group)
    # Generic matinghousing is visible but not claimed as exactservo-owned part.
    pb('COMPONENT RC servo plug',(basex+sign*5,by-s['case_length']/2-18,pz),(8,10,4),BLACK,group,'RC three-pin connector measured fit pending')
    return dict(tip=tip,base=basex,ear=earx,by=by,pz=pz,group=group)

def servo_mount(xc,sign,w,h,cx,prefix,exportcoupon=False):
    s=C['servo'];m=servo_model(xc,sign,prefix);by=m['by'];pz=m['pz'];parts=[]
    # Behind ear underside;0.5mm assembly clearance taken up by washer if needed.
    supportx=m['base']-sign*s['base_to_ear_under']+sign*3
    railx=cx+sign*(w/2+1.5)
    parts.append(box('servo foundation',((supportx+railx)/2,by,9),(abs(supportx-railx)+8,36,4)))
    for sy in(-1,1):
        yy=by+sy*s['ear_hole_pitch']/2
        post=box('servo ear screw tower',(supportx,yy,(pz+6+7)/2),(5,4,pz+6-7))
        # Slottedpitch26–29mm. SlotaxisY, screwaxisX.
        cut(post,(supportx,yy,pz),(9,3.1,2.6))
        hexhole(post,(supportx+sign*1.8,yy,pz),4.2,2,'X')
        parts.append(post)
    # Eachaxisuses suppliedhorn, directcenter screw and separately clamped printedyoke.
    hornx=m['tip']-sign*3
    horn=fuse([box('suppliedhorn arm',(hornx,0,pz),(2,C['horn']['arm_span'],C['horn']['arm_width'])),cyl('suppliedhorn hub',(m['tip']-sign*2,0,pz),C['horn']['hub_diameter']/2,4,'X')],prefix+' supplied horn',GOLD)
    drill(horn,(hornx,0,pz),1.1,8,'X');tag(horn,prefix+' horn','Stock horn dimensions require user measurement',role='moving')
    hubx=xc+sign*11
    yoke=fuse([box('yoke stem',(xc,0,pz),(8,60,6)),box('yoke hub offset',(xc+sign*5,0,pz),(14,12,6)),box('horn flange',(hubx,0,pz),(4,23,14)),*[box('pad post',(xc,dy,pz-9),(8,8,12.2)) for dy in(-C['pad_radius'],C['pad_radius'])]],prefix+' PRINT yoke',ORANGE)
    drill(yoke,(hubx,0,pz),2.2,36,'X')
    for yy in(-C['horn']['fastener_radius'],C['horn']['fastener_radius']):drill(yoke,(hubx,yy,pz),1.1,8,'X')
    printable(yoke,prefix+'_yoke',True);yoke['component_group']=prefix+' moving yoke'
    pads=[]
    for yy in(-C['pad_radius'],C['pad_radius']):
        pad=pc('COMPONENT 3M SJ5302 pad',(xc,yy,pz-16.2),3.95,2.2,mat=RED,group=prefix+' contact pads',source='3M SJ5302 nominal diameter7.9 height2.2mm');pads.append(pad)
    for ob in(yoke,horn,*pads):
        # Make every movingobjectrotate aboutthe actual outputshaftline.
        pivot=Vector((xc,0,pz));old=ob.matrix_world.copy();ob.data.transform(Matrix.Translation(-pivot) @ old);ob.matrix_world=Matrix.Translation(pivot)
        for frame,angle in[(1,0),(25,10),(40,0),(65,-10),(80,0),(100,0)]:
            ob.rotation_euler[0]=math.radians(angle);ob.keyframe_insert(data_path='rotation_euler',frame=frame)
        ob.rotation_euler[0]=0
    MOVING.append(dict(yoke=yoke,horn=horn,pads=pads,pivot=(xc,0,pz),prefix=prefix,servo_group=m['group']))
    if exportcoupon:
        # Duplicate only mount, joined to a flatbase, centred atorigin forprinting.
        clones=[]
        for ob in parts:
            a=ob.copy();a.data=ob.data.copy();scene.collection.objects.link(a);clones.append(a)
        coupon=fuse([box('coupon flatback',(supportx,by,3.5),(20,40,7)),*clones],'PRINT servo mount fit coupon',TEAL)
        printable(coupon,'coupon_servo_ear_mount');coupon.hide_render=True;coupon.hide_set(True);COUPONS.append(coupon)
    return parts

def build_chassis(g,cx):
    frame,w,h=ring(g,cx,C['skirt_depth']);parts=[frame]
    for sign in(-1,1):parts.append(box('wall adhesive landing',(cx+sign*(w/2+10),0,1.5),(20,78,3)))
    # Front-accessnut pockets and two removablestraps jointhe separatelyprintedpod.
    parts.append(box('pod docking flange',(cx,h/2+8,2),(64,16,4)))
    centers=[cx] if g==1 else[cx-C['gang_spacing']/2,cx+C['gang_spacing']/2]
    for i,xc in enumerate(centers):
        sign=1 if g==1 or i==1 else-1
        parts.extend(servo_mount(xc,sign,w,h,cx,f'{g}g_servo{i+1}',exportcoupon=g==1))
        pb('COMPONENT installed rocker',(xc,0,8),(C['rocker_width'],C['rocker_height'],4),WHITE,f'{g}g rocker{i+1}','Wallphoto appearance only; measure mountedheight')
    chassis=fuse(parts,f'PRINT {g}g chassis',TEAL)
    for xx in(-24,24):pod_floor_nut(chassis,(cx+xx,h/2+8))
    printable(chassis,f'{g}g_chassis');FIXTURES.append(chassis)
    pb('COMPONENT existing wallplate',(cx,0,3),(C['plate_widths'][str(g)],C['plate_height'],6),WHITE,f'{g}g plate','Standardplate dimensions unmeasured onuserwall')
    fit,_,_=ring(g,cx,2);printable(fit,f'{g}g_fit_ring');fit.hide_render=True;fit.hide_set(True);COUPONS.append(fit)
    return h

def build_pod(g,cx,h):
    pw=C['pod_internal_width'];ph=C['pod_internal_height'];depth=C['pod_internal_depth'];py=h/2+20+ph/2+2
    # InteriorfloorZ4. Walltop44, lidunderside44.
    pod=box('pod shell',(cx,py,(depth+4)/2),(pw+4,ph+4,depth+4),TEAL)
    cut(pod,(cx,py,depth/2+5),(pw,ph,depth+2))
    # Motorleadexitattheloweredge; noleadisroutedbehindwall.
    cut(pod,(cx,py-ph/2,16),(24,8,12))
    pp=C['layout']['picowbell'];usbtop=pp[2]+9.14
    cut(pod,(cx+pw/2,py+pp[1],usbtop+1),(8,18,16))
    for sx in(-1,1):
        for sy in(-1,1):
            xx=cx+sx*(pw/2-4);yy=py+sy*(ph/2-4)
            boolean(pod,cyl('lid screw pillar',(xx,yy,24),3.8,40),'UNION')
            drill(pod,(xx,yy,42),1.25,8)
    # Componentcoordinatesrelativepodcentre; eachbaseisindependentlyspecified.
    loc={k:(cx+v[0],py+v[1],v[2]) for k,v in C['layout'].items()}
    # Boardwithrealholes: allfourPiCowBellpostsuseEaglecentres, notPico guessedholes.
    x,y,z=loc['picowbell'];holes=PARTS['pico_socket_carrier']['mounting_holes']['centers_mm']
    for hx,hy in holes:
        boolean(pod,cyl('PiCowBell M2.5standoff',(x+hx,y+hy,(4+z)/2),2.7,z-4),'UNION')
        drill(pod,(x+hx,y+hy,z-1.5),1.0,6)
    module_specs=[('proto',43.0,50.8,1.6),('regulator',43.2,21,1.6),('servo_gate',15.24,15.24,.8),('master',15.24,15.24,.8)]
    for name,w,hh,thick in module_specs:
        x,y,z=loc[name]
        for bit in cradle_parts(x,y,w,hh,z,thick):boolean(pod,bit,'UNION')
        for sx in(-1,1):
            for sy in(-1,1):drill(pod,(x+sx*(w/2+4),y+sy*(hh/2+4),z-1),1,8)
        retainer(x,y,w,hh,z+thick+.2,'retainer_'+name,master=name in('master','servo_gate'),export_it=g==1)
        if g==1:coupon_cradle('coupon_'+name+'_cradle',w,hh,z,thick,name=='master')
    # Holderlocatorsandstrapchannels. Straps travelabovefloor, neverbehindwall.
    x,y,z=loc['battery'];bw,bh,_=C['battery_holder']['size'];gap=C['fit_clearance_per_side']
    for xx in(-22,22):boolean(pod,box('holder raisedfoot',(x+xx,y,6),(8,bh,4)),'UNION')
    for sx in(-1,1):
        for sy in(-1,1):
            boolean(pod,box('holder corner stop',(x+sx*(bw/2+gap+1),y+sy*(bh/2-5),9),(2,10,10)),'UNION')
    for xx in(-20,20):
        for sy in(-1,1):
            loop=box('holder strap loop',(x+xx,y+sy*(bh/2+4),7),(7,5,6))
            cut(loop,(x+xx,y+sy*(bh/2+4),7),(3.5,8,2.4));boolean(pod,loop,'UNION')
    # Fuseclip cradles locate cylinder without claiming hiddenmount holes.
    x,y,z=loc['fuse']
    for yy in(-14,14):
        support=box('fuseclip',(x,y+yy,8.5),(15,5,9))
        boolean(support,cyl('fuse cavity',(x,y+yy,z),6.0,8,'Y'),'DIFFERENCE')
        boolean(pod,support,'UNION')
    for xx in(-24,24):pod_floor_nut(pod,(cx+xx,h/2+32))
    printable(pod,'electronics_pod',export_it=g==1);FIXTURES.append(pod)
    for xx in(-24,24):
        strap=box('PRINT removable docking strap',(cx+xx,h/2+20,5.5),(12,38,3),TEAL)
        for yy in(8,32):drill(strap,(cx+xx,h/2+yy,5.5),1.7,6)
        printable(strap,'docking_strap',export_it=g==1 and xx==-24)
    # Realcomponentsandseparatevisiblewiring/servicevolumes.
    battery(loc['battery'],f'{g}g battery')
    picowbell(loc['picowbell'],f'{g}g pico')
    regulator(loc['regulator'],f'{g}g regulator')
    proto(loc['proto'],f'{g}g proto')
    mosfet(loc['servo_gate'],f'{g}g gate')
    mosfet(loc['master'],f'{g}g master',True)
    fuse_and_connector(loc['fuse'],loc['battery_disconnect'],f'{g}g battery harness')
    # Examples followreservedcentralcorridors; assembly netlist remains source of connectivity.
    for k,mat in enumerate((WIRE_BLACK,WIRE_RED,WIRE_YELLOW)):
        wire('HARNESS example signal/power corridor',[(cx-15+k*2,py+25,18),(cx-15+k*2,py+3,18),(cx-7+k*2,py-6,18),(cx-7+k*2,py-ph/2+3,18)],.65,mat,f'{g}g harness')
    lid=box('PRINT electronics lid',(cx,py,depth+5.5),(pw+4,ph+4,3),TEAL)
    for sx in(-1,1):
        for sy in(-1,1):drill(lid,(cx+sx*(pw/2-4),py+sy*(ph/2-4),depth+5.5),1.7,7)
    mx,my,mz=loc['master'];cut(lid,(mx+6,my,depth+5.5),(20,14,7))
    for xx in(-45,-35,-25,-15,-5,5,15,25,35,45):cut(lid,(cx+xx,py+6,depth+5.5),(3,12,7))
    printable(lid,'electronics_lid',export_it=g==1);lid.hide_render=True;lid.hide_set(True)
    return pod

for g,cx in[(1,-160),(2,160)]:
    start=set(bpy.data.objects);h=build_chassis(g,cx);build_pod(g,cx,h)
    col=bpy.data.collections.new(f'{g}-gang source-dimensioned assembly');scene.collection.children.link(col)
    for ob in set(bpy.data.objects)-start:
        for oldcol in list(ob.users_collection):oldcol.objects.unlink(ob)
        col.objects.link(ob)
# Independentcomponentcouponsforactualparts, printedbeforelargemounts.
batw,bath,_=C['battery_holder']['size'];gap=C['fit_clearance_per_side']
bat=box('PRINT battery loadedheight coupon',(0,0,11),(batw+2*gap+4,bath+2*gap+4,22),TEAL)
cut(bat,(0,0,12),(batw+2*gap,bath+2*gap,26));printable(bat,'coupon_battery_holder');bat.hide_render=True;bat.hide_set(True);COUPONS.append(bat)
# Coupon forPiCowBell mountingholes+Pico headerstackandUSBopening.
cp=C['pico'];pw,ph=54.5,40.5
coupon=box('PRINT PiCowBell fit coupon',(0,0,2),(pw+8,ph+8,4),TEAL)
for hx,hy in PARTS['pico_socket_carrier']['mounting_holes']['centers_mm']:
    boolean(coupon,cyl('PiCowBell mount',(hx,hy,6),2.7,4),'UNION');drill(coupon,(hx,hy,6),1,6)
# Postsaretheactualmountingtest;theexternalUSBservicewindowisinthemainpod.
printable(coupon,'coupon_picowbell_mount');coupon.hide_render=True;coupon.hide_set(True);COUPONS.append(coupon)
scene.frame_end=100;scene.frame_set(1)
# Explicitlabelsandscale;perpartgeometrydoesnotgetscaledtofitrender.
for x,t in[(-160,'ONE GANG'),(160,'TWO GANG')]:
    bpy.ops.object.text_add(location=(x-40,-78,1));o=bpy.context.object;o.data.body=t;o.data.size=7;o.data.materials.append(WHITE)
# Physical100mmscalebar.
bar=box('REFERENCE100mm scale',(0,-95,1),(100,2,2),WHITE);label('100 mm',(-12,-108,1),5)
bpy.ops.object.camera_add(location=(300,-380,740));camera=bpy.context.object
camera.rotation_euler=(Vector((0,95,10))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.clip_end=5000;camera.data.type='ORTHO';camera.data.ortho_scale=680;scene.camera=camera
for p,power,size in[((0,-100,500),1800000,400),((-400,200,450),1400000,350),((400,200,350),1100000,300)]:
    bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,95,0))-o.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.18,.18,.18);scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1800;scene.render.resolution_y=1400;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.region_3d.view_distance=620;area.spaces.active.region_3d.view_location=(0,95,10);area.spaces.active.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
# ExplicitassemblyBOM+boundingboxesexcludecouponsandlighting.
(OUT/'validation.json').write_text(json.dumps({'configuration':C,'parts':REPORT,'limits':'Source geometry and digital checks; unknown user hardware dimensions remain gated. Read fit-checks.json and docs/mechanics.md.'},indent=2)+'\n')
fit=envelope_report(C)
if not fit['passed']:raise RuntimeError('Nominal component envelopes conflict: '+str(fit))
installed={}
for g in (1,2):
    col=bpy.data.collections[f'{g}-gang source-dimensioned assembly']
    obs=[o for o in col.objects if o.type=='MESH' and o not in COUPONS and (o.get('role') in ('printed','fixed','moving'))]
    pts=[o.matrix_world @ Vector(v) for o in obs for v in o.bound_box]
    lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
    installed[str(g)+'g']={'dimensions_mm':[round(hi[i]-lo[i],2) for i in range(3)],'scope':'Printed enclosure including closed lid, components and example servo leads; excludes insertion space and adhesive thickness.'}
fit['installed_assembly_bounds']=installed
(OUT/'fit-checks.json').write_text(json.dumps(fit,indent=2)+'\n')
scene.render.filepath=str(OUT/'assembly.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'auto-switch.blend'))
bpy.ops.render.render(write_still=True)
print('CAD_GENERATED',len(REPORT),'printables')
