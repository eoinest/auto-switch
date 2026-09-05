"""Source-dimensioned component models. Unsourced cosmetic internals are labelled.
Pico W geometry is vendor STEP tessellation; no replacement cuboid for that board.
"""
from cadlib import *
import xml.etree.ElementTree as ET
COPPER=material('Copper and header contacts',(.8,.51,.14),.7)
CELL=material('NiMH cells • nominal AA geometry',(.62,.67,.7),.6)
WIRE_RED=material('Positive wire',(.7,.025,.018));WIRE_BLACK=material('Ground wire',(.02,.02,.025))
WIRE_YELLOW=material('Signal wire',(.95,.7,.05));PCB=material('Blue prototyping PCB',(.015,.12,.36))
SILK=material('Silkscreen',(.85,.87,.85))
PHYSICAL=[];SERVICES=[]

def tag(o,group,source='reference geometry',role='fixed'):
    o['component_group']=group;o['dimension_basis']=source;o['role']=role
    PHYSICAL.append(o);return o

def pb(name,p,size,mat=BLACK,group=None,source='dimensioned envelope with unverified detail'):
    return tag(box(name,p,size,mat),group or name,source)
def pc(name,p,r,h,axis='Z',mat=GREY,group=None,source='dimensioned envelope with unverified detail'):
    return tag(cyl(name,p,r,h,axis,mat),group or name,source)

def wire(name,points,radius=0.7,mat=WIRE_RED,group='harness'):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=radius;cu.bevel_resolution=3
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for q,p in zip(sp.points,points):q.co=(*p,1)
    ob=bpy.data.objects.new(name,cu);scene.collection.objects.link(ob);cu.materials.append(mat)
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.select_set(False)
    return tag(ob,group,'routing example; insulation diameter and bend allowance are design assumptions')

def service(name,p,size,basis):
    ob=box('KEEPOUT '+name,p,size);ob.display_type='WIRE';ob.hide_render=True;ob['basis']=basis;SERVICES.append(ob);return ob

def board(name,p,size,holes=(),group=None,mat=GREEN):
    x,y,z=p;w,h,t=size;o=box(name,(x,y,z+t/2),size,mat)
    for hx,hy,d in holes:drill(o,(x+hx,y+hy,z+t/2),d/2,t+2)
    return tag(o,group or name,'manufacturer PCB dimensions; holes separately sourced')

def label(text,p,size=2.0):
    bpy.ops.object.text_add(location=p);o=bpy.context.object;o.name='MARK '+text;o.data.body=text;o.data.size=size;o.data.materials.append(SILK)
    return o

def pico_vendor(cx,cy,top,group):
    path=ROOT.parent/'components/vendor/PicoW.obj'
    if not path.exists():raise FileNotFoundError('Vendor Pico W OBJ missing: run conversion documented in components provenance')
    verts=[];objects=[];name='PicoW';faces=[]
    for line in path.read_text().splitlines():
        fields=line.split()
        if not fields:continue
        if fields[0]=='v':verts.append(tuple(float(v) for v in fields[1:4]))
        elif fields[0] in ('o','g'):
            if faces:objects.append((name,faces));faces=[]
            name='_'.join(fields[1:])
        elif fields[0]=='f':faces.append([int(v.split('/')[0])-1 for v in fields[1:]])
    if faces:objects.append((name,faces))
    materials=json.loads((path.parent/'PicoW-mesh-metadata.json').read_text())['parts']
    result=[]
    for j,(name,faces) in enumerate(objects):
        ids=sorted({v for f in faces for v in f});remap={a:b for b,a in enumerate(ids)}
        points=[(cx+verts[i][1]-25.5,cy-(verts[i][0]-10.5),top+verts[i][2]) for i in ids]
        mesh=bpy.data.meshes.new('Vendor '+name);mesh.from_pydata(points,[],[[remap[k] for k in f] for f in faces]);mesh.update()
        o=bpy.data.objects.new('VENDOR Pico W '+name,mesh);scene.collection.objects.link(o)
        meta=materials[min(j,len(materials)-1)];o.data.materials.append(material('Vendor '+name,tuple(meta['color_rgb'])))
        tag(o,group,'Raspberry Pi Pico W official STEP; tessellated0.03mm; excludes user headers');result.append(o)
    return result

def pico_headerless(p,group):
    x,y,z=p;top=z+1
    pico_vendor(x,y,top,group)
    # Four nominal nylon heads; tapped printed posts carry the board at its mounting holes.
    for xx in(-23.5,23.5):
        for yy in(-5.7,5.7):
            pc('COMPONENT Pico M2x6 nylon screw head',(x+xx,y+yy,top+.65),1.9,1.3,mat=WHITE,group=group,source='DIN84 nylon M2x6 nominal head3.8x1.3; threads not modeled')
    service('USB plug insertion',(x+26.85+16,y,top+1),(32,14,12),'External service allowance; cable shell must fit measured14x12 opening reserve')
    service('Antenna added-metal exclusion',(x-21,y,top+3),(29,34,24),'Manufacturer antenna cutout plus10mm design spacing; not measured RF performance')
    service('Pico underside solder and wire',(x+2,y,z-1.5),(41,23,3),'3mm solder/insulation allowance above floor; trim leads and verify actual protrusion')
    # Example soldered signal and supply leads: routed toward USB end, away from antenna.
    for k,mat in enumerate((WIRE_RED,WIRE_BLACK,WIRE_YELLOW)):
        wire('HARNESS Pico soldered wire',[(x+17-k*2.54,y+8.89,top),(x+17-k*2.54,y+15,top+2),(x+12-k*2.54,y+19,top+3)],.65,mat,group)
    label('Pico W • direct solder',(x-21,y+15,z+.3),1.7)
    return top

def battery(p,group):
    x,y,z=p;w,h,t=C['battery_holder']['size'];wall=1.2
    o=box('COMPONENT Pololu1153 open holder',(x,y,z+t/2),(w,h,t),BLACK)
    cut(o,(x,y,z+10),(w-2*wall,h-2*wall,17.6))
    # Four cell wells; cosmetic divider positions, terminals and springs require measurement.
    tag(o,group,'Pololu1153outer63x58x16; internal moulding illustrative')
    for i in range(4):
        xx=x+(i-1.5)*14.7
        pc('COMPONENT AA NiMH cell '+str(i+1),(xx,y,z+8.6),7.25,49.6,'Y',CELL,group,'AAmaximumdiameter14.5 and overalllength50.5; chemistry-selected label only')
        sign=1 if i%2==0 else -1
        pc('COMPONENT AA positive button',(xx,y+sign*25.05,z+8.6),2.5,.5,'Y',GREY,group)
        pc('COMPONENT battery spring envelope',(xx,y-sign*26.1,z+8.6),3.2,1.8,'Y',GREY,group)
    for i,(mat,dy) in enumerate(((WIRE_RED,0),(WIRE_BLACK,2))):
        wire('HARNESS battery '+('positive' if i==0 else 'negative'),[(x+w/2-3,y+h/2,z+3+dy),(x+w/2+3,y+h/2+5,z+3+dy),(x+w/2+10,y+h/2+5,z+7+dy)],.7,mat,group)
    service('Loaded holder allowance',(x,y,z+11),(65,60,22),'63x58x16holder plus loaded cells and moulding tolerance; verify actual cells')

def regulator(p,group):
    x,y,z=p
    # Mount holes are only drilled once supplied in sourceJSON; cradle uses edge capture instead.
    board('COMPONENT Pololu2574 S18V20F5',(x,y,z),(43.2,21.0,1.6),group=group,mat=PCB)
    pb('COMPONENT coupled inductor',(x,y,z+5.8),(13,13,8.4),BLACK,group,'Illustrative inductor inside vendor10mm overallZ')
    for dx in(-14,14):
        for dy in(-5,5):pb('COMPONENT regulator package',(x+dx,y+dy,z+3.3),(6,4,3.4),GREY,group)
    for dx in(-19,19):
        for dy in(-5,0,5):pc('COMPONENT regulator solderpad',(x+dx,y+dy,z+1.65),1,.1,mat=COPPER,group=group)
    label('5V S18V20F5',(x-19,y-9,z+1.71),1.5)
    service('Regulator wire bends',(x,y,z+7),(59,27,16),'43x21board plus8mm wire bends per soldered end; no terminal blocks')

def mosfet(p,group,master=False):
    x,y,z=p
    board('COMPONENT Pololu2810 '+('master' if master else 'servo gate'),p,(15.24,15.24,.8),group=group,mat=GREEN)
    pb('COMPONENT slide switch',(x+5.1,y,z+1.65),(4.5,7,1.7),GREY,group)
    pb('COMPONENT slider',(x+8.1,y+(1.2 if master else -1.2),z+1.65),(2,2,1),BLACK,group)
    pb('COMPONENT MOSFET',(x-1,y,z+1.45),(5,5,1.3),BLACK,group)
    for yy in(-5.08,5.08):
        for xx in(-5.08,-2.54,0,2.54,5.08):pc('COMPONENT2810pad',(x+xx,y+yy,z+.85),.75,.1,mat=COPPER,group=group)
    service(('Master switch access' if master else 'Servo gate slider guard'),(x+12,y,z+2),(8,10,8),'Finger/tool access or coveredOFF slider; unverified actuation travel')

def proto(p,group):
    x,y,z=p
    board('COMPONENT Adafruit1608 quarter PermaProto',p,(43.0,50.8,1.6),group=group,mat=PCB)
    for i in range(13):
        for j in range(17):pc('COMPONENT perfboardpad',(x+(i-6)*2.54,y+(j-8)*2.54,z+1.65),.65,.08,mat=COPPER,group=group)
    # Capacitor selection and limits are shared with power-parts.json when supplied.
    pc('COMPONENT470uF capacitor',(x-10,y+5,z+7.35),4,11.5,mat=BLACK,group=group)
    label('470uF',(x-13,y+3,z+13.2),1.2)
    service('470uF maximum seated allowance',(x-10,y+5,z+1.6+6.5),(9,9,13),'Maximum seated13mm abovePCB; nominal can geometry11.5mm')
    for i in range(5 if group.startswith('1g') else 6):
        dy=-15+i*5
        pc('COMPONENT resistor body',(x+5,y+dy,z+3.2),1.2,6.3,'X',GREY,group,'Selected axial resistor nominal6.3xdiameter2.4; leads illustrative')
        wire('HARNESS resistor leg',[(x+1.85,y+dy,z+3.2),(x,y+dy,z+1.6)],.25,COPPER,group)
        wire('HARNESS resistor leg',[(x+8.15,y+dy,z+3.2),(x+10,y+dy,z+1.6)],.25,COPPER,group)
    for dx in(-12,6):
        pc('COMPONENT 1N5819 Schottky diode',(x+dx,y+19,z+3.2),1.35,5.2,'X',BLACK,group,'DO41 conservative body envelope; lead routing illustrative')
    pb('COMPONENT ADC 100nF ceramic',(x-12,y-12,z+3.17),(3.81,2.54,3.14),GREY,group,'KEMET C315C104K5R5TA body dimensions; legs not routed')
    label('POWER / ADC',(x-18,y-24,z+1.7),2)

def fuse_and_connector(pf,pcn,group):
    x,y,z=pf
    pc('COMPONENT Littelfuse01500274Z',(x,y,z),5.5,47.5,'Y',BLACK,group,'Vendor47.5±1xdiameter11; cap seam illustrative')
    pc('COMPONENT fuse holder cap',(x,y+15,z),5.7,13,'Y',BLACK,group)
    for sign in(-1,1):wire('HARNESS fuse lead',[(x,y+sign*24,z),(x,y+sign*34,z)],1.25,WIRE_RED,group)
    service('Fuse withdrawal and lead bend',(x,y,z),(14,70,14),'Designserviceallowance; fuse must be disconnected and unclipped before unscrewing')
    x,y,z=pcn
    pb('COMPONENT RCY mated connector',(x,y,z),(25,10,10),WIRE_RED,group,'Pololu2180+2181mated envelope DESIGN ALLOWANCE; vendor shell drawing unavailable')
    service('Battery connector disconnect',(x,y,z),(43,14,14),'18mm axial unplug travel; selectedshell not yet measured')
