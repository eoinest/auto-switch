"""Independent read-only interface audit of saved provisional Blender close-up."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'generated/horn-seat-closeup-PROVISIONAL.blend'))
seat=bpy.data.objects['SEATED HORN'];horn=bpy.data.objects['SEATED HORN reference']
def intersect_volume(a,b):
    dupe=a.copy();dupe.data=a.data.copy();bpy.context.scene.collection.objects.link(dupe)
    bpy.context.view_layer.objects.active=dupe
    mod=dupe.modifiers.new('independent intersection','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(dupe.data);value=abs(bm.calc_volume(signed=True));bm.free();bpy.data.objects.remove(dupe,do_unlink=True);return value
checks={'nominal_horn_seat_intersection_mm3':intersect_volume(seat,horn)}
for name,y,radius in [('center_tool',0,2.39),('outer_fastener_negative',-7,1.0),('outer_fastener_positive',7,1.0)]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=20,location=(11,y,0),rotation=(0,1.5707963267948966,0));tool=bpy.context.object
    checks[name+'_path_intersection_mm3']=intersect_volume(seat,tool)
    bpy.data.objects.remove(tool,do_unlink=True)
vertices=[seat.matrix_world@v.co for v in seat.data.vertices]
tree=BVHTree.FromPolygons(vertices,[list(p.vertices) for p in seat.data.polygons])
a=tree.ray_cast(Vector((0,12.8,6.5)),Vector((1,0,0)))[0]
b=tree.ray_cast(a+Vector((.001,0,0)),Vector((1,0,0)))[0]
checks['floor_thickness_mm']=b.x-a.x
checks['seat_front_extent_x_mm']=max(v.x for v in vertices)
checks['rim_depth_above_original_plane_mm']=checks['seat_front_extent_x_mm']-13
report={'status':'PASS for nominal provisional reference only','checks':checks,'not_verified':['Actual supplied horn outline and underside boss','Real horn hole sizes and fastener selection','Servo spline engagement and loaded behavior','Full production paddle motion and print geometry']}
assert all(checks[k]<.0001 for k in checks if 'intersection' in k),checks
assert abs(checks['floor_thickness_mm']-4)<.001,checks
assert abs(checks['rim_depth_above_original_plane_mm']-1.2)<.001,checks
(ROOT/'generated/independent-interface-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
