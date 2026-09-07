# Independent booster retention design review

This is a design study, not a fit-approved model. It considers the actual XL63070-marked module shown in `IMG_3222.JPG` and `IMG_3223.JPG`, together with the existing V7 carrier geometry. A roughly **16 × 30 mm board** is a provisional photo estimate supplied by the parallel photo study; neither board thickness nor underside component/solder clearance is established.

## Recommended starting concept

Use a small replacement adapter on the existing carrier, with **two narrow removable fingers over the centers of the board's short ends**. Keep the terminal pads and most of the board exposed. Low side guides locate the long edges without overlapping their component faces. Relieved supports beneath verified bare areas carry the board; the fingers prevent it lifting out.

The top photo shows a blue center strip between the two terminal pad groups at each short end. Those two central patches appear more usable than the crowded long edges. The side photo also shows that the existing retaining walls are much taller than this actual low-profile module. Continuous long-edge retaining lips or broad end crossbars would risk touching parts or obstructing the four soldering areas.

A **2.8 mm wide finger with approximately 0.6 mm overlap** onto each short end is a reasonable provisional shape to preview. It is not yet an approved contact footprint: the available center-strip width, solder spread after wiring and real edge position must be checked. Each narrow tip should widen into its mounting body; avoid a long, uniformly thin tongue.

## How the board is restrained

| Motion | Restraint | Important detail |
|---|---|---|
| Sideways across board width | Two low side guides | Touch the cut substrate edge; do not assume a continuous bare top strip. |
| Along board length | Short-end shoulders or keyed finger bodies | The upper finger alone does not stop sliding unless it also includes an end stop. |
| Toward the carrier | Relieved supports under verified bare underside patches | Keep solder joints and through-pad wire ends clear of the support. |
| Away from the carrier | The two short-end center fingers | Small upper-face overlap, away from terminal pads and components. |
| In-plane rotation | Separated side guides and both end stops | One screw per finger needs a key/guide so the finger itself cannot pivot. |
| Pull from wiring | Separate strain relief attached to the adapter/carrier | The solder pads and narrow fingers should not carry cable tugging loads. |

The holder should geometrically capture the board. It should not depend only on squeezing it hard enough that friction prevents movement.

## Adjustment and screw load path

Make each finger a guided removable part, with an elongated mounting hole for modest length adjustment. A molded key or parallel guide walls constrain rotation; a lone screw in a round hole is insufficient for a predictable finger position. A guide must still allow the finger to retract far enough to insert and remove the board after the wires are soldered.

**The mounting screw should tighten the finger against a printed seat, not continue driving the finger into the circuit board.** Give the finger a defined underside height above the adapter's support surface. For initial fit tuning, small 0.2 mm increments of seat shims or a short set of finger-height variants are simpler to inspect than an unrestricted pressure screw:

- A shim under the finger's mounting foot raises its capture height.
- A shim under a verified board support raises the board toward a fixed finger; it must not sit under a solder joint or component.
- The final stack should remove perceptible lift without bending the board. Do not use mounting-screw torque to compensate for an incorrect height.

A lightly compliant finger could take up a small residual gap, but its travel must be limited by a hard stop. Its stiffness and long-term relaxation depend on geometry, material and temperature, so it is a secondary option requiring a printed trial. A free screw pressing directly on the board or a component is not the preferred design.

## Comparison of alternatives

| Option | Advantages | Weaknesses for this board |
|---|---|---|
| **Keyed short-end center fingers and low side guides** | Uses the apparently clear spaces between pad pairs; removable; exposes components; allows a small adapter. | Center contact patches and underside support areas still need verification; wire routing must pass beside the fingers. |
| Continuous grooved side rails | Captures vertical and sideways motion with few parts. | Right long edge is crowded; a groove assumes known PCB thickness and bare face margins. Sliding installation is awkward after wiring. |
| Four corner clips | Familiar positive capture. | All four corners contain terminal pads; clips could obstruct soldering or bear on solder/wires. Poor starting choice here. |
| Adhesive-backed cradle | Simple and tolerant of outline variation. | Underside topography and heating are unknown; replacement/inspection is less convenient; adhesive creep and removal forces complicate retention. |
| Strap across the module | Adjustable and easy to prototype. | A strap route can load the inductor or other components. It requires verified support/contact zones and should not become the default workaround. |

## Compatibility with the existing V7 carrier

The carrier already has two converter-floor mounting holes at **X22, Y22 and Y68 mm**, a **46 mm pitch**. A replacement adapter centered at **X22, Y45** can use those holes without reprinting the main carrier. For the provisional 30 mm board length, the board ends would be near Y30/Y60, leaving about 8 mm from each end to the corresponding mounting-screw center. That provides space for an outward mounting foot and a narrow finger reaching inward.

The existing side-jaw slots at X−6 and X50, Y45 are also available, but they are not required for the preferred small-adapter concept. Remove the obsolete oversized floor/jaws rather than stacking a second holder on top of them. The existing S2 mounts lie to the left; a provisional adapter around 24–26 mm wide, centered at X22, has ample modeled separation, subject to final wire routing.

Final screw length must follow the new adapter-foot thickness. As an example only, a 3 mm foot on the 3 mm carrier plus a 2.4 mm ordinary M3 nut gives an 8.4 mm stack; an M3×10 screw would project 1.6 mm beyond the nut. A thicker foot may require M3×12. Confirm the real foot, washer choice, nut access and wall-bracket clearance before listing final hardware. Existing screws cannot be assumed suitable just because the holes match.

## Printing and fit checks before production

Print the adapter on a broad flat base. Print removable fingers in an orientation that leaves their small lip supported by the bed, or split the part so the lip does not require a fragile support scar at its contact face. Include lead-in chamfers without eliminating the retaining overlap. Keep nut pockets and screw heads away from the board's conductive pads; ordinary fasteners should not touch the PCB.

Use a small interface coupon to check the actual printer's edge clearance and capture height before printing the full adapter. Candidate clearances such as 0.2–0.3 mm per side are starting values, not a fit guarantee. First-layer expansion, material and print orientation can change the effective gap. Keys should have deliberate sliding clearance while the mounting screw locks their final position.

The following information remains necessary for final dimensions:

1. Actual PCB width, length and thickness, including corner shape.
2. An unobstructed underside view and the highest underside solder/component projection, especially after wiring.
3. Width and usable depth of the two short-end center patches; confirm that 2.8 × 0.6 mm contact footprints avoid the pads and solder fillets.
4. Wire exit directions and insulation diameter, so the fingers and strain-relief points remain clear.
5. A printed fit trial confirming insertion, removal, no board bowing and no contact with components.

No STL collision, strength, thermal or physical-fit approval is claimed in this study. The preferred concept is designed to localize the next iteration to a small adapter and two fingers.
