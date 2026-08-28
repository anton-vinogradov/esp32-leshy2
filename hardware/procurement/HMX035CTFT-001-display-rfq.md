# No-order technical data request — HMX035CTFT-001 LCD/CTP assembly

Supplier route: Shenzhen QDtech / LCDWIKI product channel  
Public contact: `Lcdwiki@163.com`, `goodtft@163.com`  
Target product: Leshy2 handheld radio instrument  
Current request: controlled technical and lifecycle data only; no quotation,
sample or purchase order is authorized

## Current evidence

QDtech's current product page and its official one-page front/back outline
confirm the `ES3C35P` donor, a drawing date of `2025-07-24`, the
`54.50 × 83.00 mm` CTP/LCD envelope and the CTP/LCD/glue/PCB stack. That
outline describes the **complete donor board**; it does not disclose the raw
`HMX035CTFT-001` flex outline, contact side, stiffener or standalone order
identity and therefore does not replace the requested approval drawing.

The public QDtech resource package was rechecked before preparing this request.
Its STEP file models the controller PCB rather than the LCD/CTP flex, so it does
not close the missing tail geometry.

## Technical-data request

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

## Required lifecycle data

Please include:

1. lifecycle status plus PCN/EOL notification terms;
2. whether the standalone assembly can be ordered independently of `ES3C35P`;
3. country of origin, RoHS/REACH declarations and lot traceability;
4. available brightness, cover-lens, bonding and surface-treatment options;
5. operating/storage temperature and reliability/test reports.

## Required approval drawing

Please provide a supplier-controlled approval drawing for the standalone
assembly. It must show:

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

The current replaceable adapter uses `Hirose FH34SRJ-40S-0.5SH(99)`, a
top-and-bottom-contact 40-position 0.5-mm ZIF specified for 0.30-mm FPC. The
adapter reaches the main UI PCB through exact 40-position
`DF40C-40DP-0.4V(51)` / `DF40C(2.0)-40DS-0.4V(51)` board-to-board mates with a
direct one-to-one contact map. Please explicitly state whether the panel tail
thickness is compatible with this ZIF. If not, identify a compatible connector;
the project will revise only the replaceable adapter. A logical 40-contact
match alone is not acceptance.

Commercial quotation and sample acceptance are intentionally deferred until
this no-order technical request either closes the interface or proves that a
different display must be selected.

## Public reference evidence

- QDtech ES3C35P official schematic:
  <https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf>
- QDtech ES3C35P V1.0 specification:
  <https://www.lcdwiki.com/res/ES3C35P/3.5inch_IPS_ESP32-S3_Specification_V1.0.pdf>
- Current QDtech product page:
  <https://www.lcdwiki.com/3.5inch_ESP32-S3_Display>
- QDtech complete-donor front/back and stack outline, V1.0 dated 2025-07-24:
  <https://www.lcdwiki.com/res/ES3C35P/3.5inch_ESP32-S3_touch_Size.pdf>
