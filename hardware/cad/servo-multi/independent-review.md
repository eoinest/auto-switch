# Independent multi-switch mechanism review

Status: PASS for the final nominal geometry and modeled travel; physical multi-switch fit remains unverified. This review treats the single-switch fit as user-confirmed and treats the new multi-gang plate dimensions and 46 mm pitch as nominal.

## Contact motion

`review_contact_paths.py` independently rotates the complete 7.9 mm diameter × 2.2 mm thick soft-pad envelope about each servo X axis at 0.01° increments over ±10°.

| Position | Pivot Z | Contact centers Y | Neutral pad bottom Z | Maximum pad Y extent | Margin inside a 65 mm rocker | Pressed bottom-center Z |
|---|---:|---:|---:|---:|---:|---:|
| Outer baseline | 31 mm | ±26 mm | 13.7 mm | ±32.4991 mm | 0.0009 mm | 9.4480 mm |
| Raised triple center | 61 mm | ±19 mm | 12 mm | ±31.1101 mm | 1.3899 mm | 9.4451 mm |

The shortened center contact spacing compensates for the longer fingers' increased lateral sweep. Raising the pivot while retaining contacts at ±26 mm would not keep the complete pad on the nominal rocker. The selected center geometry approximately preserves the outer channel's press depth. The lowest tilted pad edge reaches Z≈8.759 mm; the neutral rocker reference surface is Z10. This is intended contact/interference for a moving rocker and compressible pad, not a force or travel calibration.

The inherited outer geometry fits only nominally: its complete pad envelope is essentially tangent to the rocker end at the lifted extreme. This remains a physical dry-fit limitation even though the single-switch mechanism is confirmed. No further single-switch measurement is required by this review. Do not infer a manufacturing tolerance allowance from the nominal calculation.

All pads retain X within ±3.95 mm of their own switch center. Rotation about X cannot move them sideways onto a neighboring rocker; independent channel angles therefore preserve that separation.

## Fasteners and adhesive contact

- Final rails and saddle holes are at Y=±54 mm, beyond the Command strip's ±46.37 mm outline. This corrects the initial Y±40 layout that placed hardware through adhesive areas.
- Two 14.5 × 116 mm outer pads accommodate the complete 12.6492 × 92.7354 mm narrow-strip outline. The frame projects 0.85 mm above and below a nominal 114.3 mm plate; the adhesive outline stays on the plate.
- Each saddle uses two M3 × 10 screws and ordinary M3 nuts. The modeled stack is 4 mm saddle + 3 mm frame + 2.4 mm nut, leaving 0.6 mm of nominal thread projection. No washers are included.
- With the modeled frame rear at Z10, screw tips end at Z7 and remain 1 mm above the nominal plate surface at Z6. Actual strip thickness and screw length must preserve this clearance.
- Screw heads are accessible axially at Y±54, clear of servo bodies and towers. Fit nuts before adhering the assembly to the plate. Centered strips and their tabs sit behind the longer printed pads. Separate the interlocking pairs and lift the frame away before pulling the wall-side strip tabs along the wall according to the manufacturer’s instructions.
- Horn center clearance remains 4.8 mm diameter: the helper's 2.4 argument is a radius. The center hole continues through the paddle, offset and flange for a straight screwdriver path. Actual supplied horn hardware remains the physical fit reference.

## Final saved-mesh checks

`review_motion_independent.py` loads the final assembled Blender files and checks complete moving channels: paddle, stock horn, and both soft pads. At each integer angle from −10° through +10°, every channel is posed independently of its neighbors.

| Variant | Independent moving-channel pose pairs | Moving versus neighbor fixed-geometry checks | Paddle versus every printed support checks | Collisions |
|---|---:|---:|---:|---:|
| Double | 441 | 42 | 42 | 0 |
| Triple | 1,323 | 126 | 63 | 0 |

This includes the raised center servo's lower support towers and independently positioned neighboring paddles. It is a discrete surface-intersection audit of nominal meshes, not a force or arbitrary solid-containment proof. Results are saved beside each model as `independent-motion-review.json`.

Final print-layout and assembled renders were visually inspected. An independent STL-normal check found **no above-bed downward faces steeper than 45° on any frame or paddle**, confirming that the added horn-flange transition ramps remove the previous flange support issue. Saddles retain short horizontal slotted M2 openings: the slot is 2.2 mm tall and approximately 3.8 mm long, so its roof needs a short bridge. Inspect those openings in the slicer; do not equate small bridges with a general no-support guarantee. The orientation report is `generated/independent-print-orientation.json`.

The root agent separately verified closed connected solids, positive volumes, matching individual/master triangle totals, all parts at Z=0, spacing, and A1 bed fit for the five-piece double and seven-piece triple kits.

## Remaining mechanical limits

The raised center fingers and towers are longer than the confirmed single version. Mesh clearance does not verify stiffness, servo torque, pad friction, adhesive peeling, or switch actuation force. Two outer adhesive pairs carry the complete frame; no additional middle-wall attachment or extra weight/torque rating is implied. Test individual channels first with small movements and no forced stall.
