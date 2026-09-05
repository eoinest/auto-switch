"""Pure-Python design constraints and deliberately conservative service envelopes.
These calculations enforce clearances; they do not substitute for physical measurements.
"""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def load_config():return json.loads((ROOT/'config.json').read_text())
def bounds(c,size):return tuple(c[i]-size[i]/2 for i in range(3)),tuple(c[i]+size[i]/2 for i in range(3))
def overlap(a,b,tol=1e-7):return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>tol for i in range(3))
def contained(inner,outer,clearance=0):return all(inner[0][i]>=outer[0][i]+clearance and inner[1][i]<=outer[1][i]-clearance for i in range(3))
def validate_config(c):
    issues=[]
    s=c['servo'];gap=c['fit_clearance_per_side']
    if gap<.25:issues.append('Fit clearance must be at least0.25mm per side')
    if s['ear_span']<=s['case_length']+2*gap:issues.append('Servo ears do not extend beyond case clearance')
    if s['base_to_shaft_tip']<=s['case_height']:issues.append('Shaft tip must project beyond gearbox')
    if not 26<=s['ear_hole_pitch']<=29:issues.append('Servo mounting slots only accommodate26–29mm pitch; redesign mount')
    if c['pod_internal_width']<162 or c['pod_internal_height']<154:issues.append('Pod too small for source-dimensioned boards and service corridors')
    if c['battery_holder']['size'][0]>64 or c['battery_holder']['size'][1]>59:issues.append('Battery holder exceeds coupon/cradle specification')
    if c['battery_holder']['loaded_allowance_z']>28:issues.append('Loaded holder exceeds battery retention clearance')
    # Bottom rigid post at the descending end, accounting for X-axis rotation.
    a=math.radians(c['sweep_limit_degrees']);lowest=c['pivot_z']-(3+c['pad_post_height'])*math.cos(a)-(c['pad_radius']+4)*math.sin(a)
    if lowest<c['rocker_surface_z']+.05:issues.append('Rigid yoke post reaches rocker: reduce sweep or change pivot/pad geometry')
    return issues

def validate_or_raise(c):
    issues=validate_config(c)
    if issues:raise ValueError('; '.join(issues))

def envelope_report(c):
    """Nominal bought-part space checks, not a whole-assembly collision solver."""
    specs={
        'battery':(65,60,c['battery_holder']['loaded_allowance_z']),
        'pico':(52.35,21,4),
        'proto':(43,50.8,14.6),
        'regulator':(43.2,21,10),
        'servo_gate':(18.2,15.24,2.54),
        'master':(18.2,15.24,2.54),
        'fuse':(11.4,48.5,11.4),
        'battery_disconnect':(25,10,10),
    }
    centered={'fuse','battery_disconnect'}
    envelopes={}
    for key,size in specs.items():
        x,y,z=c['layout'][key]
        if key=='pico':x+=.675  # USB extends1.35mm beyond one end of51mm board.
        envelopes[key]=bounds((x,y,z if key in centered else z+size[2]/2),size)
    cavity=((-c['pod_internal_width']/2,-c['pod_internal_height']/2,4),(c['pod_internal_width']/2,c['pod_internal_height']/2,4+c['pod_internal_depth']))
    inside={k:contained(v,cavity) for k,v in envelopes.items()}
    clashes=[]
    names=list(envelopes)
    for i,key in enumerate(names):
        for other in names[i+1:]:
            if overlap(envelopes[key],envelopes[other]):clashes.append([key,other])
    retainers={}
    for key,w,h,th in [('proto',43,50.8,1.6),('regulator',43.2,21,1.6),('servo_gate',15.24,15.24,.8),('master',15.24,15.24,.8)]:
        x,y,z=c['layout'][key]
        retainers[key]=bounds((x,y,z+th+1.2),(w+14,h+14,2))
    retainer_issues=[]
    for key,env in retainers.items():
        if not contained(env,cavity):retainer_issues.append(key+' retainer outside cavity')
        for other,body in envelopes.items():
            if other!=key and overlap(env,body):retainer_issues.append(key+' retainer overlaps '+other+' body')
    names=list(retainers)
    for i,key in enumerate(names):
        for other in names[i+1:]:
            if overlap(retainers[key],retainers[other]):retainer_issues.append(key+' and '+other+' retainers overlap')
    for key,env in retainers.items():
        for sx in (-1,1):
            for sy in (-1,1):
                pillar=bounds((sx*(c['pod_internal_width']/2-4),sy*(c['pod_internal_height']/2-4),24),(7.6,7.6,40))
                if overlap(env,pillar):retainer_issues.append(key+' retainer overlaps lid pillar envelope')
    return {'scope':'Nominal component body envelopes inside pod and pairwise separation. Includes board retainer envelopes and lid pillar envelopes. Excludes other printed supports, full cable routes, USB insertion, fasteners, antenna RF performance and all actual measured fit.',
            'body_envelopes_mm':envelopes,'inside_cavity':inside,'body_envelope_overlaps':clashes,
            'retainer_envelopes_mm':retainers,'retainer_issues':retainer_issues,
            'passed':all(inside.values()) and not clashes and not retainer_issues,'pico_stack_reserved_height_mm':4,
            'loaded_holder_reserved_height_mm':c['battery_holder']['loaded_allowance_z'],
            'physical_fit_verified':False,'required_measurements':c['required_checks_before_print']}
