# One-servo AA demo — price calculation

Researched **2026-09-05**, **USD**, for the current one-servo bench BOM. **Budget about $160 before tax and shipping**, with a working range of **$147.79–$181.79**. This is a purchase budget including retail packs and spares, not the value of only the pieces installed in one switch.

Reuse the user's Pico, one MG90S, and soldering kit. Assume the existing programming cable is reusable. The main total includes new solid/stranded wire sets and heat-shrink because the specifications of the user's existing wire and kit contents are unknown. A multimeter is needed for assembly checks; its ownership is unknown, so its purchase is shown separately.

Observed prices came from supplier pages or indexed Amazon offer text; none is a live checkout quote. Four Amazon prices remain unverified and use explicit allowances. Tax, shipping, cart tariffs, seller changes, coupons and subscriptions are excluded. **Do not interpret an allowance as a confirmed Amazon offer or maximum price.** Nothing was purchased.

| Material | Buy quantity | Purchase cost | Price basis / source |
| --- | --- | ---: | --- |
| [Existing Pico W / Pico 2 W](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) | Reuse | $0.00 | Owned; no new purchase |
| [Existing MG90S + horn/screw](https://towerpro.com.tw/product/mg90s-3/) | Reuse one | $0.00 | Owned; no new purchase |
| [Four eneloop AA cells + charger](https://www.amazon.com/dp/B00JHKSMJU) | 1 kit | $29.00–$37.00 | Allowance; Amazon price unavailable. Exact-kit retailer references below. |
| [ELEGOO 830-point breadboards](https://www.amazon.com/dp/B01EV6LJ7G) | 1 three-pack | $8.99 | Observed Amazon indexed one-time price; excludes Subscribe & Save |
| [WAGO 221-415](https://www.amazon.com/dp/B06XH47DC2) | 1 ten-pack; use 3 | $8.00–$15.00 | Allowance; Amazon price unavailable. Exact-part retailer references below. |
| [TUOFENG 22 AWG solid-wire kit](https://www.amazon.com/dp/B07TX6BX47) | 1 six-color set | $16.00–$25.00 | Allowance; Amazon price unavailable. Same-ASIN retailer reference below. |
| [BNTECHGO 22 AWG stranded-wire kit](https://www.amazon.com/dp/B01M0O1NXM) | 1 ten-color set | $13.28 | Observed Amazon indexed one-time price; excludes Subscribe & Save |
| [Pololu 1153 AA holder](https://www.pololu.com/product/1153) | 1 | $2.99 | Observed Pololu quantity-1 price |
| [Pololu 2574 5 V regulator](https://www.pololu.com/product/2574) | 1 | $29.95 | Observed Pololu quantity-1 price; no coupon assumed |
| [Pololu 2810 master switch](https://www.pololu.com/product/2810) | 1 | $4.49 | Observed Pololu quantity-1 price |
| [Pololu 2180 RCY pigtail](https://www.pololu.com/product/2180) | 1 | $2.95 | Observed Pololu quantity-1 price |
| [Pololu 2181 RCY pigtail](https://www.pololu.com/product/2181) | 1 | $2.95 | Observed Pololu quantity-1 price |
| [Pololu 2169 servo extension](https://www.pololu.com/product/2169) | 1 | $5.25 | Observed Pololu quantity-1 price |
| [Littelfuse 01500274Z fuse holder](https://www.digikey.com/en/products/detail/littelfuse-inc/01500274Z/29453) | 1 | $4.00 | Observed DigiKey quantity-1 price |
| [SCHURTER 0001.2507 fuses](https://www.digikey.com/en/products/detail/schurter-inc/0001-2507/639706) | 3; install 1 | $3.15 | 3 × $1.05 at DigiKey |
| [CHANZON 1N5819 diodes](https://www.amazon.com/dp/B079KG1TN2) | 1 100-pack; use 1 | $5.00–$10.00 | Planning allowance only; no usable price obtained for this exact Amazon listing |
| [Panasonic EEU-FR1A471 capacitors](https://www.digikey.com/en/products/detail/panasonic-electronic-components/EEU-FR1A471/9921021) | 2; install 1 | $1.42 | 2 × $0.71 at DigiKey |
| [Yageo 1 kΩ resistors](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-1K/13011) | 10; install 1 | $0.42 | 10 × $0.042 at DigiKey quantity-10 tier |
| [Optional separate jumper kit](https://www.adafruit.com/product/1957) | Do not buy | $0.00 | Make jumpers using the solid wire already counted |
| [Adafruit 344 heat-shrink pack](https://www.adafruit.com/product/344) | 1 pack | $4.95 | Observed manufacturer search listing; skip if already owned |
| [USB data cable](https://www.adafruit.com/product/3879) | Reuse | $0.00 | Assumed existing MicroPython programming cable; replacement excluded |
| [Multimeter](https://www.adafruit.com/product/850) | Reuse, otherwise add below | $0.00 | Ownership unknown; conditional $24.95 purchase below |
| Soldering kit and hand tools | Reuse | $0.00 | Existing kit; any missing tools excluded |
| Cable ties + nonconductive bench base | Small supply allowance | $5.00–$10.00 | Planning allowance; reuse stock to reduce this |

## Calculation

- Pololu parts: $2.99 + $29.95 + $4.49 + $2.95 + $2.95 + $5.25 = **$48.58**.
- DigiKey fuse holder, three fuses, two capacitors and ten resistors: $4.00 + $3.15 + $1.42 + $0.42 = **$8.99**.
- Observed Amazon breadboard and stranded-wire packs: $8.99 + $13.28 = **$22.27**.
- Heat-shrink manufacturer listing: **$4.95**.
- **Observed-price subtotal: $84.79**. This excludes the unpriced items; it is not a complete build price.
- Allowances: battery kit $29–37 + WAGO pack $8–15 + solid wire $16–25 + diode pack $5–10 + ties/base $5–10 = **$63–97**.
- **Total: $84.79 + $63–97 = $147.79–$181.79** before checkout extras.

| Purchase scenario | Before tax, shipping and tariffs |
| --- | ---: |
| Buy listed materials; reuse Pico, servo, soldering tools, USB cable and meter | $147.79–$181.79 |
| Same, but also buy the [Adafruit 850 multimeter](https://www.adafruit.com/product/850) at its observed $24.95 price | $172.74–$206.74 |
| Existing solid/stranded wire meets the BOM specifications and heat-shrink is already available; reuse meter | $113.56–$138.56 |
| Reuse suitable wire and heat-shrink, but buy that meter | $138.51–$163.51 |

If a USB cable, wire stripper, cutters or another tool is missing, add its actual purchase cost. An installed 3D-printed chassis, adhesive, mounting fasteners, filament, and print electricity are **not included**: this is the present bench build, and the revised enclosure has not been finalized. No invented print mass is used.

## Evidence and unverified Amazon prices

- [Amazon ELEGOO B01EV6LJ7G](https://www.amazon.com/dp/B01EV6LJ7G): indexed offer text explicitly lists **One-Time Price $8.99**; $8.54 is a subscription offer and was not used.
- [Amazon BNTECHGO B01M0O1NXM](https://www.amazon.com/dp/B01M0O1NXM): indexed offer text explicitly lists **One-Time Price $13.28**; $12.62 is a subscription offer and was not used.
- Battery kit allowance: [Walmart exact K-KJ17MCA4BA kit](https://www.walmart.com/ip/39111784) shows **$28.99**, sold/shipped by marketplace seller MY BATTERY SUPPLIER. [Best Buy exact kit](https://www.bestbuy.com/product/panasonic-eneloop-charger-and-4-aa-batteries-kit-white/J7SVP2JWPZ/sku/12562373) shows **$36.94 but sold out**. These are reference prices only; neither establishes the Amazon price or seller authenticity.
- WAGO allowance: [Ace exact 221-415 ten-pack](https://www.acehardware.com/departments/lighting-and-electrical/boxes-fittings-and-conduit/cable-connectors/3014063) shows **$7.99**. [DigiKey 221-415](https://www.digikey.com/en/products/detail/wago-corporation/221-415/13549457) shows **$1.17 each**, or **$9.91 for ten**. Buying only three from DigiKey would be **$3.51** before shipping. These are purchasing alternatives, not a change to the circuit.
- Solid wire allowance: [TekShack listing identifying B07TX6BX47](https://tekshack.com/products/22-awg-wire-solid-core-hookup-wires-6-different-colored-breadboard-wires-30ft) shows **$24.99**. The **$16 lower allowance is a budgeting assumption**, not a verified Amazon price.
- Diode pack: exact Amazon price unavailable; **$5–10 is solely a budgeting assumption**, not a sourced offer. A 100-pack is much more than this project needs; a small pack of the specified diode is sufficient, subject to the BOM's manufacturer/lead-size checks.
- [Adafruit 344 price-bearing manufacturer listing](https://www.adafruit.com/product/344?cPath=8) shows **$4.95**; [Adafruit 850](https://www.adafruit.com/product/850) shows **$24.95** in its indexed manufacturer listing.
- Pololu prices use quantity one. DigiKey uses the actual order quantities above, including the ten-resistor discount. Potential Pololu coupon savings were not applied; shipping and DigiKey cart tariff charges are not established.

## What drives the cost

The **$29.95 regulator** and the battery/charger kit are the largest individual entries. New wire sets and retail multipacks account for much of the first-build spending. The signal resistor costs **4.2 cents per piece at the selected quantity**, and a capacitor costs **71 cents**; these are not the expensive parts of this design.

The part numbers and wiring remain unchanged. Confirm the four missing Amazon prices before treating the total as an order-ready quote.
