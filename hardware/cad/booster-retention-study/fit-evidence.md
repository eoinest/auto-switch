# Received XL63070 board: mounting evidence and options

Reviewed user photos `IMG_3222.JPG` (top) and `IMG_3223.JPG` (side), and the current v4 converter cassette reused by the later carrier designs. **No production STL generated.**

## What is now established

The received board is labeled **XL63070**, with four terminal pad groups at the corners, a central inductor, and EN/PS/ADJ/output-selection pads along one long edge. It visibly does not match the old 40 × 36 mm placeholder. Its plated terminal holes are electrical connections, not identified mounting holes.

The photographed printed floor corresponds to the v4 26 × 36 mm center floor. Comparing the board to that floor gives a rough **30 × 16 mm PCB estimate**. This is an image-based estimate, not an exact measurement: camera perspective, board height above the reference, feature selection, and actual print scale all affect it. The side photo confirms a thin substrate with taller parts above it; it does not establish substrate thickness.

An independent vendor's own [5 V XL63070/TPS63070 product description](https://www.roboter-bausatz.de/p/tps63070-buck-boost-modul-automatische-step-up-step-down-spannungsregelung-5v-dc) and [RBS18349 datasheet](https://www.roboter-bausatz.de/datasheet/RBS18349.pdf) specify **30 × 16 mm** for its module. This agrees with the photo estimate but does not prove the dimensions or tolerances of the user's Amazon unit. The [selected Teyleten Robot Amazon listing](https://www.amazon.com/dp/B0GCW44FDL) and its previously inspected detail images provide no verified PCB-thickness drawing. Exact substrate thickness and populated height remain unknown.

## Why the current cradle fails

`electronics-retention-v4/generate.py` defines 40 mm opposing jaw spacing with approximately ±3 mm travel per jaw: roughly 34–46 mm nominal width accommodation. A board around 30 × 16 mm cannot be retained in either orientation by that arrangement. The end-stop gap is 37 mm, leaving a roughly 30 mm board free to move longitudinally too.

The existing clip throat is 2.0 mm: shelf top Z8, lip underside Z10. Its 1.6 mm PCB model therefore has 0.4 mm nominal play. The 18 mm placeholder is total populated height, **not PCB thickness**. These values are hard-coded in the v4 generator; editing descriptive config dimensions alone will not resize the clips.

## Keepouts visible in the received-board photos

- **All four corners:** terminal pads and future solder/wire joints. Avoid default corner clamps here.
- **One long edge:** the inductor sits near the edge. A continuous upper rail or tall side wall could contact it.
- **Other long edge:** selection jumpers, small parts, EN/PS/ADJ pads. A broad upper lip can block them or press solder joints.
- **Short-end centers:** small blue-board regions between the terminal pairs are possible narrow finger-contact locations. Their usable width/depth must be checked; they are candidates, not verified keepouts.
- **Underside:** the new photos do not show it. The seller's unsoldered underside looked mostly flat, but the actual soldered assembly requires inspection. Support contact should align below hold-down contact so the PCB is not bent.

## Comparing no-hole retention

| Approach | Benefit | Fit problem on this board |
|---|---|---|
| Continuous slide-in edge rails | Simple one-piece housing; positive vertical capture | Requires known thickness and continuous clear edge margins; insertion can scrape solder/components and become difficult after wiring |
| Adjustable opposed jaws | Accommodates dimensional variation; removable | Needs completely new small-board travel range and narrow verified contacts; screw force must not bow the board or press components |
| Shallow locating nest plus removable fingers | Drops in from above; independent lateral location and vertical capture; solder terminals remain accessible | Needs measured outline and two real bare-PCB contact patches; small separate retainers/fasteners |

**Preferred concept to investigate:** a shallow open-top nest, with two short removable fingers reaching the **centers of the short ends**, between terminal pairs, if those patches are sufficiently clear. Use matching support beneath those contacts, leave the terminal corners and component top open, and give wires their own strain relief. Screws belong in the printed mount, never through the electrical terminal holes. Hard stops should limit finger travel; the PCB should be captured, not squeezed by arbitrary screw torque. If those end-center patches are too small, choose another verified edge location or a custom open frame instead.

## Minimum missing measurements

1. PCB **length × width × exposed-edge substrate thickness**, preferably calipers. Do not measure thickness over the inductor or solder.
2. Actual underside photo and the planned/final solder-wire exits.
3. Width and inward depth of each proposed bare end-center contact patch; a close top photo with a ruler helps locate it.

A small replaceable nest/clip-gap coupon should validate those interfaces before committing to a full holder. The photo estimate is sufficient for a clearly labeled concept comparison, not for a claim of snug final fit.
