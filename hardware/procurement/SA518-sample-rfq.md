# Sample/RFQ — NiceRF SA518

Recipient: `sales@nicerf.com`  
Requested quantity: 1 engineering sample, followed by 100 and 500 units
Target product: Leshy2 handheld radio instrument

## Channel safety gate

The JLCPCB short quote form currently maps bare `SA518` to generic
`JLCPCB Assembly C9900300438` (stock 0, MOQ 442, estimated `$0.0203` each).
That row does not prove NiceRF manufacturer identity, the current datasheet or
the production revision. Do not submit or accept it as the selected module.
This request may be sent directly to NiceRF or through a JLCPCB support/new-part
channel only when the channel preserves every identity field below.

## Message

Subject: SA518 sample, controlled land pattern and production quote

Hello,

We are evaluating the exact current-production `SA518` dual-band module for one
136–174/400–470 MHz analog voice path in a new handheld product. Please quote
one engineering sample and later quantities of 100 and 500 units.

Before ordering, please answer the following:

1. Provide the current supplier-controlled outline and recommended PCB land
   pattern with explicit datums, pad dimensions and X/Y coordinates for every
   contact. In particular, show the exact contact-7 `ANT` pad centre and edge
   offset; the published artwork does not dimension that RF launch completely.
2. Provide the recommended 50-ohm contact-7 launch, ground-via and copper
   keepout geometry, permitted stackup assumptions and any maximum feed length
   before an external SMA connector.
3. Confirm the exact orderable variant. Does one delivered module support both
   0.5 W and 1 W through contact 12 `H/L`, or are those separate factory
   options? We require the 1-W-capable version while retaining the documented
   low-power selection.
4. Resolve the published contact-17 contradiction: the table marks `UPDATE` as an
   output, while its description says to pull it low during power-up to enter
   serial update mode. State its true direction, internal bias, voltage limits,
   required timing and safe external fixture circuit.
5. Confirm that standard contact 4 `VOXEN` has no function and that host-side
   microphone/data operation remains available without a custom VOX firmware
   variant.
6. Identify the current firmware version/marking and provide the complete
   update/recovery protocol or the required vendor programming fixture/tool.
7. Provide conducted output-power, harmonic/spurious, receive-sensitivity and
   occupied-bandwidth test data for both VHF and UHF at 4.0 V, at both H/L
   settings and across the published -30 to +70 degrees C range.
8. Confirm the exact document revision and production revision that govern the
   quoted sample. The live product page and downloadable document identity must
   be tied to the delivered module marking.
9. Quote unit prices for 1 sample, 100 and 500 units, MOQ, packaging, sample and
   production lead times, lifecycle status, country of origin, RoHS/REACH and
   PCN/EOL notification terms.

Please keep the sample RF hardware and firmware identical to the quoted
production configuration, or list every difference explicitly.

Thank you.

## Acceptance use

The response closes paper geometry, variant identity and purchasing evidence.
Received samples still undergo contact measurement, land-pattern coupon,
module-to-SMA VNA, power/thermal, audio, RX/TX, fault-kill and actual-RF-evidence
HIL before schematic/BOM freeze.

Public references:

- [current manufacturer product/RFQ page](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html);
- [current downloadable SA518 specification](https://www.nicerf.com/upload/20260430/391f11abcc1d835ac5ed151613fdae68.pdf).
