# DSP-0008 — display procurement boundary and exact RFQ packet

- Статус: **проведено ревью sourcing strategy; standalone production source открыт**
- Дата: 2026-08-19
- Current endpoint: [`DSP-0005`](DSP-0005-hmx035ctft-electrical-fit.md) /
  [`DSP-0007`](DSP-0007-exact-integrated-st77922-touch-endpoint.md)
- BOM result: [`BOM-0010`](../components/BOM-0010-display-procurement-and-alternate-disposition.md)
- Review: [`REV-0005BI`](../reviews/REV-0005BI-display-procurement-propagation.md)

## Результат проверки

Публичный рынок подтверждает две разные вещи, которые нельзя смешивать:

1. **Prototype specimen доступен сейчас.** Elecrow продаёт in-stock
   `DLE06235B`, а QDtech/QDTFT — `ES3C35P-QD`; official board schematic
   связывает установленную display/touch assembly с exact marking
   `HMX035CTFT-001`. Покупка complete board даёт нужный specimen для чтения
   маркировки, измерения FPC и electrical HIL.
2. **Standalone production panel не доказана.** Нет публичной страницы
   отдельной `HMX035CTFT-001`, supplier-controlled approval drawing, MOQ,
   quantity-100 quote, lifecycle или PCN/EOL contract. Цена complete board
   `$20.90` у Elecrow и supplier tiers полного `ES3C35P-QD` являются только
   потолком/каналом прототипной закупки, не raw-panel COGS.

Следовательно, used-line coverage честно остаётся `187/188`, но I8 больше не
заблокирован отсутствием доступного HIL specimen: заблокирован именно
production RFQ/approval package.

## Почему найденные near-matches не drop-in

### OPL product 226

- 3.5-inch `320×480`, BOE IPS, 300 cd/m², `AXS15231B`, interface list
  включает QSPI;
- public page не публикует manufacturer MPN, approval drawing, полный FPC
  register или подтверждённую CTP assembly;
- disposition: полезный direct-manufacturer inquiry lead, но не AVL line.

### Waveshare ESP32-S3-Touch-LCD-3.5B

- заказываемая complete board с `AXS15231B`, QSPI display и I2C capacitive
  touch;
- official brightness 210 cd/m² ниже 300-cd/m² current field target;
- schematic markings `HXR35014C30`/`HXR35014C30_TOUCH` не имеют доказанной
  standalone ordering и не совпадают с HMX contact/mechanical identity;
- disposition: secondary controller/HIL reference, not silent substitute.

### Leadtek LTK035P4046TX-09QC-V1

- настоящий inquiry MPN, 3.5-inch `320×480` IPS, 340 cd/m², CTP;
- public contract — MCU/SPI with expandable RGB, separate HY4633 touch and
  `70.80×102.80×6.20 mm` LCM+CTP outline;
- disposition: не сохраняет доказанный direct-QSPI/TDDI endpoint и механику;
  возможен только через полное architecture reopen.

Таким образом, current primary не заменяется. Для строки действует explicit
`no_drop_in_substitute`: альтернативой считается только прошедшая повторную
electrical, firmware, optics, mechanics, power, EMI и HIL qualification
assembly.

## Exact supplier RFQ packet

Запрос QDtech/QDTFT должен одновременно содержать:

1. quote на **standalone `HMX035CTFT-001` LCM+CTP**, не на `ES3C35P` board;
2. confirmation `ST77922`, `320×480`, IPS, QSPI display, I2C touch `0x38`,
   active-low IRQ и separate display/touch reset;
3. supplier-controlled approval drawing: complete outline, active/view area,
   cover glass, FPC pitch/width/length/thickness, contact side, stiffener,
   bend/keepout and pin-1 marking;
4. exact 40-contact register и electrical limits для VDD/VDDI/LEDA/LEDK,
   reset, QSPI and straps;
5. brightness ≥300 cd/m², viewing angle, backlight Vf/current bins,
   operating/storage temperature and optical-bond/cover-lens options;
6. samples `5/10`, MOQ, USD prices at `100/500/1000`, lead time, packaging,
   warranty and lot traceability;
7. lifecycle horizon, PCN/EOL notice, process/glass/controller substitution
   policy, RoHS/REACH declarations and reliability report.

## Acceptance

Paper sourcing gate closes only when the response names the exact raw assembly
and provides an approval drawing plus a quote. Production qualification still
requires received samples, FPC mate, init/touch/shared-bus/backlight/optics
tests and cover-lens integration. Until then no generic 40-pin panel is allowed
into KiCad.

## Primary sources

- [Elecrow DLE06235B product page](https://www.elecrow.com/3-5-esp32-s3-display-320x480-capacitive-ips-touchscreen-with-speaker-mic-bat-interface-supports-ai-voice-chat.html)
- [QDtech ES3C35P product/documentation page](https://www.lcdwiki.com/3.5inch_ESP32-S3_Display)
- [QDtech official schematic naming HMX035CTFT-001](https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf)
- [QDtech official outline drawing](https://www.lcdwiki.com/res/ES3C35P/3.5inch_ESP32-S3_touch_Size.pdf)
- [OPL product 226](https://www.opldisplaytec.com/product/226)
- [Waveshare ESP32-S3-Touch-LCD-3.5B](https://www.waveshare.com/product/esp32-s3-touch-lcd-3.5b.htm)
- [Leadtek LTK035P4046TX-09QC-V1](https://www.leadtekdisplay.com/35-inch-tft-lcd-display-p-2860.html)
