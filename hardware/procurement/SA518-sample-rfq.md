# Sample/RFQ — NiceRF SA518

Recipient: `sales@nicerf.com`  
Requested quantity: 2 engineering samples, followed by 100 and 500 units  
Target product: Leshy2 handheld radio instrument

## Message

Subject: SA518 Rev 1.1 samples, controlled land pattern and production quote

Hello,

We are evaluating the exact current-production `SA518` dual-band module for one
136–174/400–470 MHz analog voice path in a new handheld product. Please quote
two engineering samples and later quantities of 100 and 500 units.

We are using your May 2026 product specification Rev 1.1. Before ordering,
please answer the following:

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
4. Resolve the Rev 1.1 contact-17 contradiction: the table marks `UPDATE` as an
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
8. Quote unit prices for 2 samples, 100 and 500 units, MOQ, packaging, sample and
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
- [SA518 specification Rev 1.1, May 2026](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf).
