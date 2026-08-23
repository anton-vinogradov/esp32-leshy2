# Last-resort pre-KiCad evidence sample plan

This is a parked engineering working artifact, not a finished-product page,
not the next project step and not an order authorization. Purchasing is the
last resort, not the normal way to close an H1 source gap. The project first
exhausts manufacturer-controlled public sources, compares fully documented
function-preserving replacements and requests missing drawings or mating data
without an order. Only an uncertainty left after those three routes may enter
this plan, and it still requires separate user approval. Before any such
proposal, P1–P6 of the
[`LESHY2-PREORDER-1` contract](../verification/preorder-verification-contract.json)
must pass: industrial/mechanical design review, current schematic and ERC,
virtual electrical analysis, executable firmware simulation, target
build/emulation and joined pre-layout review. Prices are public reference values
checked on 22 August 2026; freight, tax and RFQ-only items are deliberately
excluded from totals.

## First evidence lot

| Exact item | Qty | Public reference | Why this quantity is the minimum useful lot | Gate closed by receipt |
|---|---:|---:|---|---|
| Elecrow `DLE06235B` / QDtech `ES3C35P` complete display donor containing `HMX035CTFT-001` | 5 | $20.90 each; $104.50 material | one intact reference, three independently measured display flexes and one handling/HIL spare | H5 actual display/flex envelope, markings, thickness/stiffener, adapter fit and electrical HIL |
| M5Stack `U214` | 1 | $14.50 | the same non-destructive specimen can close geometry, pin section, bottoming, retention and functional Cap-Bus checks | received-Cap envelope and exact host-socket mating stack |
| Samtec `HLE-107-02-G-DV-PE-LC` | 5 | $3.338 manufacturer q1 reference; $16.69 reference material | one dock specimen plus four fit/alignment/repeated-mating coupons; exact part is stocked by Samtec | pass-through footprint/body/tail truth, received-U214 insertion force and retention |
| Hirose `FH34SRJ-40S-0.5SH(99)` | 5 | $3.40 Mouser q1 reference; $17.00 material | one dual-contact ZIF per received display flex, so a damaged latch or extraction does not collapse the H5 evidence set | exact flex thickness, insertion, retention and repeatability |
| Hirose `DF40C(2.0)-40DS-0.4V(58)` | 5 | $1.36 Mouser q1 reference; $6.80 material | one exact fixed receptacle per display-adapter coupon | exact 2.0-mm stack, alignment and repeated mating |
| Hirose `DF40C-40DP-0.4V(51)` | 5 | $1.01 Mouser q1 reference; $5.05 material | one exact adapter plug per display-adapter coupon | exact 40-contact mate, continuity and repeated mating |
| Ebyte `E01-ML01IPX` | 4 | $2.02 official-store reference; availability confirmation required | three simultaneous full-function nRF24 paths plus one untouched identity/connector/spare specimen | module envelope, exact `IPX` mating family, pigtail choice and three-radio HIL setup |
| NiceRF `SA518` | 2 | RFQ | one installed RF/thermal specimen and one retained comparison/spare specimen | exact contact-7 geometry, land pattern, short antenna-feed corridor and first RF/thermal HIL |

The currently computable reference material is **$164.54**, covering the
display donors, U214, five Samtec sockets and five copies of each selected
Hirose display-interface connector. The Ebyte
store price would add **$8.08** if exact stock is confirmed. No complete-lot
total is stated until NiceRF quotes `SA518` and Ebyte resolves the contradictory
in-stock/pre-order state; shipping and taxes also remain destination-dependent.

Ordering references:

- [Elecrow display donor](https://www.elecrow.com/3-5-esp32-s3-display-320x480-capacitive-ips-touchscreen-with-speaker-mic-bat-interface-supports-ai-voice-chat.html);
- [M5Stack U214 at DigiKey](https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/U214/29291633);
- [exact Samtec pass-through socket](https://www.samtec.com/products/hle-107-02-g-dv-pe-lc);
- [exact dual-contact Hirose panel ZIF](https://www.mouser.com/ProductDetail/Hirose-Connector/FH34SRJ-40S-0.5SH99?qs=vcbW%252B4%252BSTIq%252BjF2my2YV5Q%3D%3D);
- [exact Hirose 2.0-mm main-board receptacle](https://www.mouser.com/ProductDetail/Hirose-Connector/DF40C2.0-40DS-0.4V58?qs=Gufeu08L%2Fl2S31N%2Fy6Rjyw%3D%3D);
- [exact Hirose adapter-board plug](https://www.mouser.com/ProductDetail/Hirose-Connector/DF40C-40DP-0.4V51?qs=eDUdFcBPps3ody6AX5VRNA%3D%3D);
- [Ebyte E01-ML01IPX official store page](https://ebyteiot.com/products/ebyte-e01-ml01ipx-nrf24l01p-rf-2-4g-smd-wireless-transceiver-module-iot-electronic-components-ebyte-e01-ml01ipx-spi-interface-antenna-ipex-smd);
- [NiceRF SA518 manufacturer/RFQ page](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html).

## Acceptance records

Every received item is photographed with packaging, lot code and markings
before use. Measurements are retained as raw CSV/photos plus a short signed
acceptance record; a pass/fail summary alone is not enough to authorize KiCad.

1. **Display:** retain one donor intact; disassemble and measure at least three;
   prove FPC pitch, thickness, exposed-contact side, stiffener, insertion,
   retention, QSPI, touch `0x38`, reset/IRQ, backlight current and temperature.
2. **Cap Bus:** measure U214 and every HLE socket; record mating post section,
   insertion/withdrawal force and continuity over repeated cycles; verify all
   14 contacts, retention engagement and the protected hot-plug sequence.
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

Sample ordering remains unauthorized until the pre-order contract reaches P7,
the research/replacement/data-request sequence is recorded as exhausted for
the exact unresolved item, and the user separately approves that last-resort
purchase.
KiCad remains unauthorized for PCB placement/routing until the
measurements above are either accepted or recorded as an explicit architectural
exception. A received mismatch returns to the machine architecture and
dimensioned mockup first; it is not patched silently in PCB layout.
