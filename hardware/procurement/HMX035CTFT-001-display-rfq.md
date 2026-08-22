# RFQ — standalone HMX035CTFT-001 LCD/CTP assembly

Supplier route: Shenzhen QDtech / LCDWIKI product channel  
Public contact: `Lcdwiki@163.com`, `goodtft@163.com`  
Target product: Leshy2 handheld radio instrument  
Requested quantities: 5 engineering samples, then 100 and 500 production units

## Current evidence and prototype route

QDtech's current product page and its official one-page front/back outline
confirm the `ES3C35P` donor, a drawing date of `2025-07-24`, the
`54.50 × 83.00 mm` CTP/LCD envelope and the CTP/LCD/glue/PCB stack. That
outline describes the **complete donor board**; it does not disclose the raw
`HMX035CTFT-001` flex outline, contact side, stiffener or standalone order
identity and therefore does not replace the requested approval drawing.

Elecrow currently lists the complete `DLE06235B/ES3C35P` donor in stock at
USD 20.90. Five donors provide a USD 104.50 published-material route for
specimen measurement and electrical HIL before a raw-panel quote arrives.
This route may prove the received flex and connector fit, but it must never be
used as evidence of standalone production price, lifecycle or lot supply.

Donor acceptance sequence:

1. retain one board intact as the electrical and visual reference;
2. photograph panel, flex and lot markings before disassembly;
3. measure at least three flexes, including outline, pitch, thickness,
   exposed-contact side, stiffener and bend keepout;
4. prove insertion, retention and contact orientation in
   `FH12-40S-0.5SH(55)`;
5. run QSPI, touch `0x38`, reset, IRQ, backlight-current and temperature HIL.

## Supplier request

Please quote the **standalone display and capacitive-touch assembly marked
`HMX035CTFT-001`** used on the QDtech `ES3C35P` product. We do not need the
complete ES3C35P ESP32-S3 PCB, speaker, enclosure or accessories.

The reference design identifies:

- 3.5-inch IPS, portrait `320×480`;
- Sitronix `ST77922` display and touch TDDI;
- four-data-line QSPI display interface;
- I2C capacitive touch at 7-bit address `0x38`;
- 40 electrical contacts, including separate display/touch reset and touch IRQ;
- nominal backlight current `120 mA`;
- published LCD/CTP screen-body envelope `54.50±0.20 × 83.00±0.20 ×
  3.20±0.10 mm`, explicitly excluding flex and adhesive.

Please confirm whether `HMX035CTFT-001` is the supplier-controlled production
MPN. If it is only an internal marking, provide the exact orderable MPN and
state whether its electrical and mechanical configuration is identical.

## Required quotation data

Please include:

1. unit prices for 5 samples, 100 units and 500 units;
2. MOQ, sample lead time, production lead time and Incoterms;
3. lifecycle status plus PCN/EOL notification terms;
4. country of origin, RoHS/REACH declarations and lot traceability;
5. available brightness, cover-lens, bonding and surface-treatment options;
6. operating/storage temperature and reliability/test reports;
7. packing format and shipping dimensions.

## Required approval drawing

The quotation is not sufficient without a supplier-controlled approval drawing
for the standalone assembly. It must show:

- LCD, CTP, backlight and active/viewing areas with tolerances;
- total stack including adhesive and any stiffener;
- integral FPC outline, exit location, unfolded/folded keepout and minimum bend
  radius;
- FPC contact count, `0.50-mm` pitch, thickness, exposed-contact side, stiffener
  side/length/thickness and insertion direction;
- pin numbering as viewed from both the display front and the FPC contact side;
- the complete 40-contact electrical table;
- mating-connector recommendation and validated insertion thickness;
- backlight LED topology, `Vf`, nominal/maximum current and thermal limits;
- touch address, reset timing, IRQ polarity/clear behaviour and I2C maximum
  frequency;
- QSPI mode, maximum clock, power-up/reset timing and all strap defaults.

The current host connector candidate is `Hirose FH12-40S-0.5SH(55)`, a
bottom-contact 40-position 0.5-mm ZIF for 0.30-mm FPC. Please explicitly state
whether this exact connector is compatible. A logical 40-contact match alone
is not acceptance.

## Sample acceptance

Samples will be checked for marking/lot identity, drawing dimensions, FPC mate
and retention, QSPI operation, `0x38` touch identity, reset/IRQ behaviour,
backlight current and temperature. Production approval is conditional on those
checks and on a signed drawing revision matching the quoted MPN.

## Public reference evidence

- QDtech ES3C35P official schematic:
  <https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf>
- QDtech ES3C35P V1.0 specification:
  <https://www.lcdwiki.com/res/ES3C35P/3.5inch_IPS_ESP32-S3_Specification_V1.0.pdf>
- Current QDtech product page:
  <https://www.lcdwiki.com/3.5inch_ESP32-S3_Display>
- QDtech complete-donor front/back and stack outline, V1.0 dated 2025-07-24:
  <https://www.lcdwiki.com/res/ES3C35P/3.5inch_ESP32-S3_touch_Size.pdf>
- Current Elecrow donor listing:
  <https://www.elecrow.com/3-5-esp32-s3-display-320x480-capacitive-ips-touchscreen-with-speaker-mic-bat-interface-supports-ai-voice-chat.html>
