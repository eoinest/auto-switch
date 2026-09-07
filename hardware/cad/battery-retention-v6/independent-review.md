# Independent single-crossbar review

**PASS for nominal geometry.** The final saved assembly and exported STL were checked with [review_mechanics_independent.py](review_mechanics_independent.py); numerical results are in [generated/independent-mechanical-review.json](generated/independent-mechanical-review.json).

The two reused upper posts are at X±43, Y−12 mm. Both post tops and both bar bearing faces measure **Z26** in the saved mesh; the bar front is **Z29** on both ends. The 3 mm end thickness therefore preserves the original two M3×35 screw stacks and ordinary underside nuts. Shaft probes confirm clearance through both new bar holes and both existing carrier holes. The unused lower post pair remains unchanged.

The center land is 64 mm wide with underside **Z22.2**. The nominal 19 mm holder rests on the 3 mm carrier and has its face at **Z22**, leaving **0.2 mm nominal vertical allowance**. This corrects the old roughly 4 mm gap without claiming a tight physical fit. The existing 1.4 mm total X/Y cradle clearance remains; optional V5 shims can address lateral movement.

Eight exact Boolean checks returned zero intersection volume: bar versus original carrier, nominal case, switch-access envelope and wire corridor, plus M3 shaft probes through both mounting stacks. Deliberately coincident bearing surfaces were separated by 0.001 mm for the Boolean checks. The crossbar lies at Y−17…−7, clear of the lower-right switch and modeled upper-right wire route. Actual wire exit height and bend radius remain unmeasured.

The STL measures **96 × 10 × 6.8 mm**, has its broad front face at bed Z0, and provides approximately **941.9 mm²** of flat bed contact. No downward-facing surfaces are suspended above the bed; near-vertical face normals are excluded with a small angular tolerance to avoid floating-point artifacts. This orientation needs no modeled support or bridging. Mesh closure and connectivity are also checked by the generator; the parent agent audits the binary STL independently.

This is a seller-dimension-based preview, not a physical fit or strength test. A single bar retains the holder near one end and does not eliminate every possible rocking motion. Do not compensate for fit error by overtightening against the plastic posts. Remove the bar to lift out the holder for battery service.
