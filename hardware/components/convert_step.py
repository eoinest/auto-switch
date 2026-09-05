#!/usr/bin/env python3
"""Optional source-CAD conversion; run in a venv with cadquery-ocp==8.0.1.0.0.

Preserves assembly transforms and named parts. A single color per part is used;
parts without a label color use neutral gray. Does not synthesize missing parts.
Generated vendor geometry retains Raspberry Pi's original terms (see NOTICE).
"""
import argparse, hashlib, json, re
from zipfile import ZipFile
from pathlib import Path
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorSurf, XCAFDoc_ColorGen
from OCP.collections import Sequence_TDF_Label
from OCP.TDF import TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.Quantity import Quantity_Color

parser = argparse.ArgumentParser(description='Tessellate the original licensed Pico W STEP into named OBJ objects (millimetres).')
parser.add_argument('--source', type=Path, default=Path(__file__).parent/'vendor/PicoW-step.zip')
parser.add_argument('--output', type=Path, default=Path(__file__).parent/'vendor')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
import tempfile
with ZipFile(args.source) as archive:
    source_data = archive.read('PicoW.stp')
temp = tempfile.NamedTemporaryFile(suffix='.stp')
temp.write(source_data); temp.flush()
r=STEPCAFControl_Reader();r.SetNameMode(True);r.SetColorMode(True)
d=TDocStd_Document(TCollection_ExtendedString('PicoW'))
r.ReadFile(temp.name);r.Transfer(d)
st=XCAFDoc_DocumentTool.ShapeTool_s(d.Main());ct=XCAFDoc_DocumentTool.ColorTool_s(d.Main())
roots=Sequence_TDF_Label();st.GetFreeShapes(roots)
parts=[]
def walk(l,loc=TopLoc_Location(),path=''):
 n=TDataStd_Name();name=n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),n) else ''
 path=(path+'_'+name).strip('_')
 if st.IsReference_s(l):
  ref=TDF_Label();st.GetReferredShape_s(l,ref)
  walk(ref,loc.Multiplied(st.GetLocation_s(l)),path)
 elif st.IsAssembly_s(l):
  children=Sequence_TDF_Label();st.GetComponents_s(l,children)
  for i in range(1,children.Length()+1):walk(children.Value(i),loc,path)
 else:
  shape=st.GetShape_s(l).Moved(loc)
  box=Bnd_Box();BRepBndLib.AddOptimal_s(shape,box,False,False)
  color=Quantity_Color();found=ct.GetColor_s(l,XCAFDoc_ColorSurf,color) or ct.GetColor_s(l,XCAFDoc_ColorGen,color)
  rgb=[color.Red(),color.Green(),color.Blue()] if found else [0.5,0.5,0.5]
  parts.append((re.sub('[^A-Za-z0-9_-]','_',path),shape,(box.CornerMin().X(),box.CornerMin().Y(),box.CornerMin().Z(),box.CornerMax().X(),box.CornerMax().Y(),box.CornerMax().Z()),rgb))
for i in range(1,roots.Length()+1):walk(roots.Value(i))
result=[];out=args.output
with (out/'PicoW.obj').open('w') as obj,(out/'PicoW.mtl').open('w') as mtl:
 obj.write('# Raspberry Pi Pico W official STEP tessellation; source units millimetres\nmtllib PicoW.mtl\n')
 offset=0
 for name,shape,bbox,color in parts:
  BRepMesh_IncrementalMesh(shape,0.03,False,0.2,True)
  obj.write('o '+name+'\nusemtl '+name+'\n')
  mtl.write('newmtl '+name+'\nKd '+' '.join(map(str,color))+'\n')
  vertices=triangles=0
  ex=TopExp_Explorer(shape,TopAbs_FACE)
  while ex.More():
   face=TopoDS.Face(ex.Current());loc=TopLoc_Location();tri=BRep_Tool.Triangulation_s(face,loc)
   if tri:
    for i in range(1,tri.NbNodes()+1):
     p=tri.Node(i).Transformed(loc.Transformation());obj.write('v %.7f %.7f %.7f\n'%(p.X(),p.Y(),p.Z()))
    for i in range(1,tri.NbTriangles()+1):
     a,b,c=tri.Triangle(i).Get()
     if face.Orientation()==TopAbs_REVERSED:b,c=c,b
     obj.write('f %d %d %d\n'%(a+offset,b+offset,c+offset))
    offset+=tri.NbNodes();vertices+=tri.NbNodes();triangles+=tri.NbTriangles()
   ex.Next()
  result.append({'name':name,'bbox_mm':bbox,'color_rgb':color,'vertices':vertices,'triangles':triangles})
(out/'PicoW-mesh-metadata.json').write_text(json.dumps({'source':'PicoW.stp','source_sha256':hashlib.sha256(source_data).hexdigest(),'obj_sha256':hashlib.sha256((out/'PicoW.obj').read_bytes()).hexdigest(),'mtl_sha256':hashlib.sha256((out/'PicoW.mtl').read_bytes()).hexdigest(),'generator':'convert_step.py; cadquery-ocp 8.0.1.0.0','tessellation_linear_deflection_mm':0.03,'tessellation_angular_deflection_radians':0.2,'units':'mm','parts':result},indent=2)+'\n')
print('Exported', len(result), 'named parts to', out)
