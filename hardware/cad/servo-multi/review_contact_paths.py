"""Independent finite-pad sweep calculation; no Blender or third-party modules.
The pad is a cylindrical 7.9 mm x 2.2 mm bumper rotating about the X axis.
These equations bound the complete circular contact face, not only its center.
"""
import json, math
from pathlib import Path

def sweep(pivot_z, pad_y, pad_bottom_z, rocker_height=65, radius=3.95, thickness=2.2):
    zc=pad_bottom_z+thickness/2
    rows=[]
    for step in range(-1000,1001):
        angle=step/100
        a=math.radians(angle);s=math.sin(a);c=math.cos(a)
        for side in [-1,1]:
            y=side*pad_y
            cy=y*c-(zc-pivot_z)*s
            cz=pivot_z+y*s+(zc-pivot_z)*c
            half_y=radius*abs(c)+(thickness/2)*abs(s)
            half_z=radius*abs(s)+(thickness/2)*abs(c)
            rows.append({'angle_deg':angle,'side':side,'y_min':cy-half_y,'y_max':cy+half_y,'z_min':cz-half_z,'bottom_center_z':pivot_z+y*s+(pad_bottom_z-pivot_z)*c})
    extreme=max(rows,key=lambda r:max(abs(r['y_min']),abs(r['y_max'])))
    minz=min(rows,key=lambda r:r['z_min'])
    yreach=max(abs(extreme['y_min']),abs(extreme['y_max']))
    return {'pivot_z_mm':pivot_z,'contact_y_mm':pad_y,'neutral_pad_bottom_z_mm':pad_bottom_z,'pad_diameter_mm':2*radius,'pad_thickness_mm':thickness,'rocker_height_mm':rocker_height,'angle_samples':2001,'max_y_reach_mm':yreach,'remaining_y_margin_mm':rocker_height/2-yreach,'lowest_pad_edge_z_mm':minz['z_min'],'lowest_bottom_center_z_mm':min(r['bottom_center_z'] for r in rows),'worst_y_sample':extreme}

if __name__=='__main__':
    print(json.dumps({'outer_original':sweep(31,26,13.7),'outer_proposed':sweep(31,25.5,13.7),'center_proposed':sweep(61,19,12)},indent=2))
