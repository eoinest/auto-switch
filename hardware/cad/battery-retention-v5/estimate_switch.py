"""Reproduce manual pixel measurements from the seller's dimension photograph.

No downloaded product photograph is redistributed. The coordinates refer to the
1500 x 1500 source image linked in photo-measurements.json. This is an estimate,
not a manufacturing drawing or measurement of the delivered battery holder.
"""
import json
from pathlib import Path

face = (182, 712, 724, 1296)
switch = (596, 742, 672, 775)
sx, sy = 64.2 / (face[2] - face[0]), 68.7 / (face[3] - face[1])
u = ((switch[0] + switch[2]) / 2 - face[0]) * sx
v = ((switch[1] + switch[3]) / 2 - face[1]) * sy
data = {
    "product": "DAIERTEK 4 AA switched holder, B09N1GDWQ9",
    "listing_url": "https://www.amazon.com/dp/B09N1GDWQ9",
    "dimension_photo_url": "https://m.media-amazon.com/images/I/61-SB+loQyL._AC_SL1500_.jpg",
    "switch_photo_url": "https://m.media-amazon.com/images/I/61zgOzS8JaL._AC_SL1500_.jpg",
    "cover_wire_photo_url": "https://m.media-amazon.com/images/I/714VLim1EKL._AC_SL1500_.jpg",
    "accessed": "2026-09-06",
    "image_size_px": [1500, 1500],
    "face_box_px_left_top_right_bottom": face,
    "switch_box_px_left_top_right_bottom": switch,
    "seller_dimensioned_face_width_height_mm": [64.2, 68.7],
    "seller_dimensioned_case_depth_mm": 19,
    "seller_dimensioned_depth_including_switch_mm": 22.5,
    "mm_per_pixel_xy": [sx, sy],
    "estimated_switch_center_from_face_left_top_mm": [round(u, 2), round(v, 2)],
    "estimated_switch_opening_width_height_mm": [round((switch[2]-switch[0])*sx, 2), round((switch[3]-switch[1])*sy, 2)],
    "carrier_transform": "X=34.35-v; Y=-32+32.1-u; Z=3+case depth (switch face outward)",
    "estimated_switch_center_carrier_xy_mm": [round(34.35-v, 2), round(-32+32.1-u, 2)],
    "uncertainty": "Allow at least +/-1 mm for photographic feature estimates, plus unquantified product variation. Seller dimensions are nominal; physical fit remains untested.",
    "wire": "Switch-face photo shows exit on top edge near left corner. After rotation, it exits the carrier's right case edge near its upper end. Existing bottom-center cradle notch is not aligned. Exit height is not dimensioned.",
    "interpretation": "The former 22.5 mm solid case reference included switch projection; a 19 mm case sits at Z22, leaving 4 mm below old bars at Z26. Keep the switch and finger approach free; do not clamp its protrusion."
}
if __name__ == "__main__":
    Path(__file__).with_name("photo-measurements.json").write_text(json.dumps(data, indent=2)+"\n")
