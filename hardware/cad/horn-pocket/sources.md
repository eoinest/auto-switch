# Horn interface dimensions

The existing servo model describes the **supplied plastic servo horn**, which fits the servo shaft and is retained by its original center screw. The printed paddle attaches to that horn. The locating pocket should align the horn's outside shape; it does not reproduce the shaft spline.

[TowerPro's MG90S product page](https://towerpro.com.tw/product/mg90s-3/) confirms that arms and screws are included and supplies servo case dimensions. It does not establish the supplied horn's detailed outline, hole spacing or molding tolerances. Checked 2026-09-05.

The existing project file `../servo-command/config.json` assumes a 22 mm arm span, 5 mm arm width, 2 mm arm thickness, 7 mm hub diameter and fastening positions 7 mm from center. Its horn `measured` flag is false. Those numbers are a provisional design envelope, not a verified manufacturer horn drawing. Confirmation of the single-switch mounting dimensions does not identify the supplied horn shape.

A locating pocket needs the actual mating-face outline and any raised center boss, as well as arm thickness and the fastening-hole center positions. Printed clearance must also account for the printer and material; a small coupon can establish this without reprinting the entire paddle or frame.

Keep the original horn's axial position and spline engagement when adding a pocket. Preserve the center-screw access hole, the two outer fastening paths and sufficient material behind the recess. The pocket locates the parts during assembly; screws provide retention.

## Physical fit check

1. Compare the actual horn to the provisional straight two-ended outline before printing a coupon. A cross-shaped, single-ended, tapered or different-size horn needs its own outline.
2. Use a spare loose horn, or remove it with the servo unpowered; do not force the shaft through its gearing to test the seat.
3. The horn should reach the pocket floor by hand without flexing the rim. The seat locates it; tightening screws must not pull an oversized horn into the recess.
4. Verify the original center screw remains accessible and the two outer horn holes line up with the paddle slots. A tight outer outline cannot correct incorrect hole positions.
5. Keep the material, nozzle, layer settings and orientation used for the successful coupon when printing the revised paddle. No coupon clearance is a guaranteed fit for every printer.

A symmetric two-ended seat establishes horn-to-paddle alignment, not the servo's absolute neutral angle. Set neutral using the existing calibration workflow before final assembly.
