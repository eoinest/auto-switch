"""Three provisional XL63070 retention concepts. Intentionally exports no STL."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cadlib import *
BLUE=material('XL63070 PCB — photo approximation',(.015,.07,.21));SILVER=material('Solder pad',(.66,.68,.70),.75)
LABEL=material('Labels',(.05,.06,.08));ALT=material('Alternative concept',(.35,.39,.43))
W,L,T=C['pcb_mm'];bottom=C['pcb_underside_z'];top=bottom+T;floor=C['carrier_floor_z'];ft=C['adapter_floor_thickness'];hole=C['mount_hole_pitch_mm']/2
objects={}
def label(txt,x,y,size=2.5):
    bpy.ops.object.text_add(location=(x,y,0));o=bpy.context.object;o.name=txt;o.data.body=txt;o.data.size=size;o.data.align_x='CENTER';o.data.materials.append(LABEL);return o
def module(cx):
    obs=[]
    obs.append(box('PCB 16x30x1.2 — PROVISIONAL',(cx,0,bottom+T/2),(W,L,T),BLUE))
    for x in [-5.15,5.15]:
        for y in [-13.55,13.55]:obs.append(box('Corner solder pad — keep clear',(cx+x,y,top+.05),(5.25,2.9,.1),SILVER))
    obs.append(box('Inductor approximate',(cx-3.4,-2.2,top+1.8),(6.5,7.2,3.6),GREY))
    obs.append(box('Controller approximate',(cx+2,-3.1,top+.6),(3.2,3.7,1.2),BLACK))
    for y in [-8,-5,0,3,6,9]:
        obs.append(box('Right-edge parts — approximate',(cx+6.6,y,top+.35),(1.5,1.7,.7),GREY))
    for y in [2.7,5,7.2,9.4]:obs.append(box('Capacitors — approximate',(cx+.2,y,top+.45),(3.8,1.1,.9),GOLD))
    obs.append(box('Input capacitor — approximate',(cx-.1,-10.2,top+1),(4.1,2.4,2),GOLD))
    for o in obs:o['role']='REFERENCE ONLY; photo reconstruction, not exact component geometry'
    return obs

def adapter(cx,tag):
    p=box(tag+' compact open adapter',(cx,0,floor+ft/2),(20,36,ft),TEAL)
    cut(p,(cx,0,floor+ft/2),(12,23,ft+2))
    for y in [-hole,hole]:
        boolean(p,box('Mount ear',(cx,y,floor+ft/2),(10,12,ft),TEAL),'UNION');drill(p,(cx,y,floor+ft/2),1.7,10)
    # Support only short sections of substrate edges. Underside and solder-pad zones open.
    for sign in [-1,1]:
        for y in [-7,7]:boolean(p,box('Sparse underside edge support',(cx+sign*(W/2-.5),y,(floor+ft+bottom)/2),(1,5,bottom-floor-ft),TEAL),'UNION')
    return p

def screw(cx,y,z,name='Existing M3 mounting point'):
    return cyl(name+' — schematic head only; length not selected',(cx,y,z+1.5),2.75,3,mat=GREY)

def rails(cx):
    p=adapter(cx,'A')
    for sign in [-1,1]:
        # Deliberately illustrates why continuous upper lips crowd edge components.
        boolean(p,box('Continuous slide rail',(cx+sign*(W/2+.9),0,(floor+ft+top+1.2)/2),(1.4,L+1,top+1.2-floor-ft),ALT),'UNION')
        boolean(p,box('Continuous top lip — conflict risk',(cx+sign*(W/2-.25),0,top+.7),(1.4,L+1,1),ALT),'UNION')
    stop=box('A removable end stop',(cx,-hole,top+.7),(6,13,1.4),ORANGE);drill(stop,(cx,-hole,top+.7),1.7,5)
    screw(cx,-hole,top+1.4);screw(cx,hole,floor+ft)
    objects['A']=[p,stop]+module(cx)
    label('A  SLIDE-IN RAILS',cx,35);label('Edge parts + wired removal risk',cx,-37,1.65)

def split(cx):
    p=adapter(cx,'B')
    jaws=[]
    for sign in [-1,1]:
        # Short side lips reduce coverage but still require confirmed blank side windows.
        j=fuse([box('B sliding foot',(cx+sign*11.5,0,floor+ft+1),(9,7,2)),box('B low upright',(cx+sign*9,0,(floor+ft+top+1)/2),(2,7,top+1-floor-ft)),box('B short top lip',(cx+sign*7.7,0,top+.7),(2.4,5,1.4))],'B adjustable side jaw',ALT)
        cut(j,(cx+sign*12,0,floor+ft+1),(3,3.4,6));drill(j,(cx+sign*10.5,0,floor+ft+1),1.7,6);drill(j,(cx+sign*13.5,0,floor+ft+1),1.7,6)
        jaws.append(j);screw(cx+sign*12,0,floor+ft+2,'Additional adapter jaw screw — concept')
    for y in [-hole,hole]:screw(cx,y,floor+ft)
    objects['B']=[p]+jaws+module(cx)
    label('B  SPLIT SIDE CLAMPS',cx,35);label('Adjustable, but side contact uncertain',cx,-37,1.65)

def end_toes(cx):
    p=adapter(cx,'C')
    # Low side guides contact only the cut substrate edge, never the populated top face.
    for sign in [-1,1]:
        for y in [-7,7]:boolean(p,box('Low substrate side guide',(cx+sign*(W/2+C['side_clearance_mm']+.6),y,(floor+ft+bottom+T*.6)/2),(1.2,5,bottom+T*.6-floor-ft),TEAL),'UNION')
    toes=[]
    # Short center-only end stops constrain length without blocking corner terminals.
    for sign in [-1,1]:boolean(p,box('Between-pad substrate end stop',(cx,sign*(L/2+.8),(floor+ft+top)/2),(C['toe_width_mm'],1.2,top-floor-ft),TEAL),'UNION')
    seatshim=C['seat_height_shim_mm']
    for sign in [-1,1]:
        # Integral shoulder provides a positive screw stop below a replaceable height shim.
        shoulder=box('C clamp hard seat',(cx,sign*hole,(floor+ft+top-seatshim)/2),(7.8,11,top-seatshim-floor-ft),TEAL);boolean(p,shoulder,'UNION');drill(p,(cx,sign*hole,top),1.7,12)
        shim=box('C optional 0.2 mm seat-height shim',(cx,sign*hole,top-seatshim/2),(7.8,11,seatshim),GOLD);drill(shim,(cx,sign*hole,top),1.7,5)
        # Key walls keep toe from twisting when one screw is tightened.
        for side in [-1,1]:boolean(p,box('C anti-rotation guide',(cx+side*5,sign*hole,(floor+ft+top+1.5)/2),(1.4,11,top+1.5-floor-ft),TEAL),'UNION')
        foot=box('C slotted clamp foot',(cx,sign*hole,top+1),(8.2,10,2),ORANGE)
        inner=L/2-C['toe_overlap_mm'];outer=hole-4.5
        toe=box('C narrow bare-end tongue',(cx,sign*(inner+outer)/2,top+1),(C['toe_width_mm'],outer-inner,2),ORANGE)
        j=fuse([foot,toe],'C end-center retaining finger',ORANGE)
        cut(j,(cx,sign*hole,top+1),(3.4,2,6));drill(j,(cx,sign*hole-1,top+1),1.7,6);drill(j,(cx,sign*hole+1,top+1),1.7,6)
        screw(cx,sign*hole,top+2,'Existing M3 floor screw — length to be checked')
        toes.extend([j,shim])
    objects['C']=[p]+toes+module(cx)
    label('C  NARROW END FINGERS',cx,35);label('Recommended: clear corner pads + low guides',cx,-37,1.65)
    return p
rails(-43);split(0);end_toes(43)
label('XL63070 RETENTION STUDY — DIMENSIONS PROVISIONAL',0,43,2.25)
label('16 x 30 mm photo estimate | PCB thickness and underside NOT measured | NO STL',0,-44,1.8)
# Store explicit ownership and measurement status on every concept object.
for group,obs in objects.items():
    for o in obs:o['concept']=group;o['fit_status']='UNVERIFIED — photo-derived envelope'
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for loc in [(70,-90,200),(-120,20,140)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=150000;o.data.size=140;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(60,-100,220));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=170;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1800;scene.render.resolution_y=1250;scene.render.resolution_percentage=100
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'booster-retention-options-PROVISIONAL.blend'))
scene.render.filepath=str(OUT/'booster-retention-options-PROVISIONAL.png');bpy.ops.render.render(write_still=True)
# Closeup of the recommended candidate, leaving both end-pad pairs visible.
camera.location=(82,-63,90);camera.rotation_euler=(Vector((43,0,6))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=70
for o in list(scene.objects):
    if o.type=='FONT':o.hide_render=True
    elif o.type=='MESH' and o.location.x<22:o.hide_render=True
scene.render.resolution_x=1300;scene.render.resolution_y=1300;scene.render.filepath=str(OUT/'recommended-end-fingers-PROVISIONAL.png');bpy.ops.render.render(write_still=True)
print('Saved concept scene and two renders. No STL export.')
