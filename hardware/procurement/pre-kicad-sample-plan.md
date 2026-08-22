# Pre-KiCad evidence sample plan

This is a parked engineering working artifact, not a finished-product page,
not the next project step and not an order authorization. It defines the
smallest later purchase that can close residual physical-only evidence gates.
Before it may be proposed for approval, P1–P6 of the
[`LESHY2-PREORDER-1` contract](../verification/preorder-verification-contract.json)
must pass: industrial/mechanical design review, current schematic and ERC,
virtual electrical analysis, executable firmware simulation, target
build/emulation and joined pre-layout review. Prices are public reference values
checked on 22 August 2026; freight, tax and RFQ-only items are deliberately
excluded from totals.

## First evidence lot

| Exact item | Qty | Public reference | Why this quantity is the minimum useful lot | Gate closed by receipt |
|---|---:|---:|---|---|
| Elecrow `DLE06235B` / QDtech `ES3C35P` complete display donor containing `HMX035CTFT-001` | 5 | $20.90 each; $104.50 material | one intact reference, three independently measured display flexes and one handling/HIL spare | actual display/flex envelope, markings, FPC contact side/thickness/stiffener, first `FH12` mate and electrical HIL |
| M5Stack `U214` | 1 | $14.50 | the same non-destructive specimen can close geometry, pin section, bottoming, retention and functional Cap-Bus checks | received-Cap envelope and exact host-socket mating stack |
| Samtec `SSW-107-02-S-D` | 5 | $3.013 manufacturer q1 reference; $15.065 reference material | one dock specimen plus four fit/alignment/repeated-mating coupons; exact part is stocked by Mouser | host footprint/body/tail truth, received-U214 insertion depth and retention |
| Hirose `FH12-40S-0.5SH(55)` | 5 | $3.55 DigiKey q1 reference; $17.75 material | one connector per received display flex, so a damaged latch or extraction does not collapse the evidence set | exact flex insertion, contact orientation and repeatability |
| Ebyte `E01-ML01IPX` | 4 | $2.02 official-store reference; availability confirmation required | three simultaneous full-function nRF24 paths plus one untouched identity/connector/spare specimen | module envelope, exact `IPX` mating family, pigtail choice and three-radio HIL setup |
| NiceRF `SA518` | 2 | RFQ | one installed RF/thermal specimen and one retained comparison/spare specimen | exact contact-7 geometry, land pattern, short antenna-feed corridor and first RF/thermal HIL |

The currently computable reference material is **$151.815**, covering the
display donors, U214, five Samtec sockets and five Hirose connectors. The Ebyte
store price would add **$8.08** if exact stock is confirmed. No complete-lot
total is stated until NiceRF quotes `SA518` and Ebyte resolves the contradictory
in-stock/pre-order state; shipping and taxes also remain destination-dependent.

Ordering references:

- [Elecrow display donor](https://www.elecrow.com/3-5-esp32-s3-display-320x480-capacitive-ips-touchscreen-with-speaker-mic-bat-interface-supports-ai-voice-chat.html);
- [M5Stack U214 at DigiKey](https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/U214/29291633);
- [exact Samtec socket at Mouser](https://www.mouser.fr/ProductDetail/Samtec/SSW-107-02-S-D?qs=XtX6y9BSeMh%252BITruJPqgTA%3D%3D) and [manufacturer price/drawing page](https://www.samtec.com/products/ssw-107-02-s-d);
- [exact Hirose connector at DigiKey](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/FH12-40S-0-5SH-55/1110328);
- [Ebyte E01-ML01IPX official store page](https://ebyteiot.com/products/ebyte-e01-ml01ipx-nrf24l01p-rf-2-4g-smd-wireless-transceiver-module-iot-electronic-components-ebyte-e01-ml01ipx-spi-interface-antenna-ipex-smd);
- [NiceRF SA518 manufacturer/RFQ page](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html).

## Acceptance records

Every received item is photographed with packaging, lot code and markings
before use. Measurements are retained as raw CSV/photos plus a short signed
acceptance record; a pass/fail summary alone is not enough to authorize KiCad.

1. **Display:** retain one donor intact; disassemble and measure at least three;
   prove FPC pitch, thickness, exposed-contact side, stiffener, insertion,
   retention, QSPI, touch `0x38`, reset/IRQ, backlight current and temperature.
2. **Cap Bus:** measure U214 and every SSW socket; record mating post section,
   exposed length, insertion depth, bottoming clearance and force over repeated
   cycles; verify all 14 contacts and the protected hot-plug sequence.
3. **nRF24:** identify the actual miniature coax family under magnification and
   with a received mate; select the exact pigtail only afterward; operate all
   three modules simultaneously in RX, TX and mixed traffic while adjacent
   inactive interfaces remain hardware-quiet.
4. **SA518:** measure the real pad coordinates and module envelope, build the
   shortest straight contact-7-to-SMA coupon, then verify current, temperature,
   receive, transmit, audio and actual-RF evidence behavior.

## Supplier actions that remain parallel

- Send the prepared [`HMX035CTFT-001` standalone-assembly RFQ](HMX035CTFT-001-display-rfq.md).
  Donor measurements may authorize a prototype footprint, but they do not
  establish raw-panel production orderability, price, lifecycle or tolerances.
- Ask Ebyte to confirm immediate supply of four exact `E01-ML01IPX` units and
  name the mating connector series used by the current production lot.
- Ask NiceRF for two `SA518` engineering samples, a quantity-100/500 quote,
  current land-pattern/inspection drawing, lead time, lifecycle and PCN/EOL
  terms.

## Release rule

Sample ordering remains unauthorized until the pre-order contract reaches P7.
KiCad remains unauthorized for PCB placement/routing until the
measurements above are either accepted or recorded as an explicit architectural
exception. A received mismatch returns to the machine architecture and
dimensioned mockup first; it is not patched silently in PCB layout.
