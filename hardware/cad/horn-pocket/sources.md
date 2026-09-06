# Horn interface dimensions from the supplied photo

The user supplied IMG_3198.JPG showing a loose, black, two-ended horn on the known printed single-switch mount. It identifies a **tapered double-arm shape with rounded ends**, replacing the old rectangular 22 mm placeholder.

The 96 × 14.5 mm printed pad is the scale reference, assuming it was printed at 100% scale. We analyzed the EXIF-corrected 4284 × 5712 image without copying the photo or its location metadata into the repository. [Measurements](photo-measurements.json) record pixel bounds, manually selected reference corners, threshold sensitivity and the source-file hash. [The script](estimate_from_photo.py) reproduces the estimates with Pillow and NumPy when given the original image locally.

| Feature | Current design estimate | Evidence limit |
|---|---:|---|
| Overall horn span | 31.5 mm | Simple scaling gives about 31.2 mm; a planar perspective correction gives about 32.0 mm. Allow roughly ±1 mm. |
| Hub outside diameter | 7.4 mm | Approximately 7.3–7.5 mm, sensitive to edge/shadow selection |
| Arm width near hub | 5.3 mm | Estimated from the visible silhouette |
| Width near rounded tips | 4.0 mm | Approximately 3.9–4.1 mm |
| Arm thickness | 2 mm placeholder | Not measurable from this view |
| Hub axial depth | 4 mm placeholder | Not measurable from this view |
| Outer fastening holes | Existing slots retained | Exact centers and diameters not established by this photo |

The horn is above the reference pad, so a planar perspective correction cannot remove all height parallax. Printed scale/shrinkage, rounded edges and shadows also limit accuracy. The modeled profile is symmetric: the apparent difference in arm lengths is not strong enough evidence to encode asymmetry.

The [TowerPro product page](https://towerpro.com.tw/product/mg90s-3/) confirms arms and screws are supplied but does not dimension this horn outline. The photo of the actual part takes precedence over assuming every MG90S kit uses identical horns.

## Fit coupons

The revised coupons use **97%, 100% and 103% profile scales**, each with 0.3 mm clearance per side. Their unexpanded horn spans are 30.555, 31.5 and 32.445 mm. This brackets the photo's dimensional uncertainty better than varying only a tenth of a millimetre of clearance. It does not change the assumed depth or establish a guaranteed fit.

Print the cavities upward and mark the samples before removing them from the bed. The loose horn should reach the pocket floor by hand without flexing the rim; do not use screws to force it into an undersized recess. Check the center opening and outer screw paths, then use the best-fit profile for the complete paddle. Confirm the real horn's seating face and boss do not bottom out prematurely.

The recess retains the existing X13 seating plane, 4 mm backing and original servo horn/spline. Its raised rim locates the horn; screws retain it. The symmetric seat aligns horn to paddle but does not establish servo neutral; keep using the existing calibration workflow.
