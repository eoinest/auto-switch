"""Estimate horn dimensions against the known printed pad (Pillow + NumPy).
Usage: python estimate_from_photo.py /path/to/IMG_3198.JPG
Outputs measurements only; never copies the user's photo or its location metadata.
Image-specific anchors assume this supplied composition, not arbitrary photos.
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

path = Path(sys.argv[1])
with Image.open(path) as original:
    image = np.asarray(ImageOps.exif_transpose(original).convert('RGB'))
height, width = image.shape[:2]
assert (width, height) == (4284, 5712), 'Anchors apply to the supplied EXIF-corrected photo only'
scale = width / 1368
# Independent review's manual pad corners, EXIF-corrected original pixels.
source = np.array([[2473,1876],[2757,1876],[2797,3816],[2495,3816]], dtype=float)
target = np.array([[0,0],[14.5,0],[14.5,96],[0,96]], dtype=float)
a, b = [], []
for (x,y),(u,v) in zip(source,target):
    a += [[x,y,1,0,0,0,-u*x,-u*y], [0,0,0,x,y,1,-v*x,-v*y]]
    b += [u,v]
homography = np.r_[np.linalg.solve(a,b), 1].reshape(3,3)
x0,x1,y0,y1 = [round(v*scale) for v in (815,877,660,890)]
roi = image[y0:y1,x0:x1]
measurements = []
for threshold in (85,110,135,160):
    ys,xs = np.where(roi.mean(axis=2) < threshold)
    pixels = np.c_[xs+x0,ys+y0,np.ones(len(xs))]
    mapped = pixels @ homography.T
    mm = mapped[:,:2] / mapped[:,2,None]
    measurements.append({
        'dark_threshold': threshold,
        'bounds_display_pixels': [(xs.min()+x0)/scale, (ys.min()+y0)/scale,
                                 (xs.max()+x0)/scale, (ys.max()+y0)/scale],
        'simple_span_mm': (ys.max()-ys.min()+1)/scale*96/621,
        'homography_width_span_mm': np.ptp(mm,axis=0).tolist(),
    })
result = {
    'source_file_name': path.name,
    'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'oriented_image_pixels': [width,height],
    'reference': 'Existing single mount: 14.5 mm wide by 96 mm long printed pad, assumed printed at 100 percent scale',
    'pad_corner_pixels': source.tolist(),
    'measurements': measurements,
    'selected_design_estimates_mm': {'span':31.5, 'hub_diameter':7.4,
                                    'near_hub_arm_width':5.3, 'tip_width':4.0},
    'span_uncertainty_mm_approx': 1.0,
    'unknown': ['arm thickness','underside boss','exact hole centers and diameters','printed scale/shrinkage'],
    'limitations': 'Manual corner picks, perspective, rounded edges, shadows and horn height above the pad limit precision. Planar homography does not remove height parallax. Symmetric tapered outline is an approximation, not a traced manufacturing drawing.',
}
output=Path(__file__).resolve().parent/'photo-measurements.json'
output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
