# DSP-0004 — display subsystem part-number register

- Статус: **Проведено ревью обозначений; production MPN gates явно открыты**
- Дата проверки: 2026-08-17
- Target-class decision: [`DEC-0053`](../decisions/DEC-0053-new-35in-qspi-display-class.md)
- Shortlist: [`DSP-0003`](DSP-0003-exact-fast-display-shortlist.md)
- Reviews: [`REV-0004Z`](../reviews/REV-0004Z-display-class-decision-propagation.md),
  [`REV-0005A`](../reviews/REV-0005A-hmx-display-electrical-fit.md),
  [`REV-0005AO`](../reviews/REV-0005AO-display-endpoint-propagation.md)

Этот реестр намеренно не использует широкую таблицу. Для каждого обозначения
указано, чем оно является: target part, HIL-only development reference,
fallback либо ещё не опубликованный production MPN. Controller name нельзя
считать MPN стекла или готового display assembly.

## Leshy2 target display subsystem

### Уже зафиксированные связанные parts

- Host module: Espressif `ESP32-S3-WROOM-1U-N16R2`.
- microSD socket на общей scheduled SPI2: Hirose `DM3AT-SF-PEJM5`.
- Target class: 3.5-inch portrait `320×480`, IPS, direct QSPI, capacitive
  touch. Это спецификация класса по `DEC-0053`, не заказываемый MPN.

### Production parts, которые ещё обязаны пройти qualification

- Display/panel assembly: current exact paper candidate
  **`HMX035CTFT-001`**. Marking раскрыт official QDtech `ES3C35P` schematic,
  но manufacturer attribution, standalone orderability, drawing, lifecycle и
  second source не подтверждены; поэтому production BOM ещё не принят.
- Integrated display/touch TDDI: exact **`Sitronix ST77922`** inside the
  assembly. It is not a separate purchase line; its exact touch address is
  `0x38` and the exact assembly specification defines active-low `TP_INT`.
- Display FPC/board connector: Hirose **`FH12-40S-0.5SH(55)`**, CL
  `CL0586-0527-7-55`, принят `DEC-0084` как exact first electrical/fit
  candidate. Он ещё не final mate и не разрешает footprint: tail
  thickness/contact side/stiffener/insertion должны быть доказаны specimen HIL.
- Separate touch controller: **not applicable** for this exact candidate;
  `ST77922` integrates the touch controller. `DSP-0007/DEC-0088` close its
  paper address, reset and interrupt contract.
- Backlight power/PWM path: exact `TPS2553DRVR-1`, `DMN2056U-7`,
  `ERJ-P08F10R0V` and exact support passives по `DSP-0006/DEC-0084`.
- Display/touch interface protection: internal-FPC ESD classification and
  populated QSPI tuning remain HIL; source-series/shunt tuning positions are
  DNP rather than invented BOM parts.
- Cover lens/optical bonding assembly: **custom/`TBD`**.

Ни одно из значений `TBD` не разрешено переносить в KiCad как generic footprint.

## Primary HIL — Elecrow/QDtech ST77922

- Retail/product identifier: Elecrow `DLE06235B`.
- Manufacturer/specification module identifier: QDtech `ES3C35P`.
- Display/touch controller marking: Sitronix `ST77922`.
- Exact display/touch assembly marking: `HMX035CTFT-001` in the official
  QDtech schematic; separate manufacturer attribution is not assumed.
- Separate touch-controller MPN: **not applicable**; exact `ST77922` is the
  assembly's integrated display/touch TDDI.
- Exact touch contract: 7-bit address `0x38`, maximum 400 kHz, active-low
  `TP_INT`; board normalization is specified by `DSP-0007/DEC-0088`.
- Role: exact current paper candidate и primary HIL specimen target; не
  production-accepted BOM part до sourcing/mechanics/HIL gates.
- Checked properties: 3.5-inch `320×480` IPS, QSPI display, I2C touch,
  300 cd/m², `-30…80 °C`, module outline `54.50×101.50×10 mm`.
- Exact contact/electrical fit: [`DSP-0005`](DSP-0005-hmx035ctft-electrical-fit.md).

## Secondary HIL — Waveshare AXS15231B

- Product name: Waveshare `ESP32-S3-Touch-LCD-3.5B`.
- Orderable SKU: Waveshare `31137`.
- Enclosed/camera variant: Waveshare `ESP32-S3-Touch-LCD-3.5B-C`, SKU `31334`.
- Display/touch controller marking: `AXS15231B`.
- Schematic assembly markings: `HXR35014C30` and `HXR35014C30_TOUCH`.
- Exact standalone orderability/drawing/lifecycle: **не подтверждены**.
- Role: secondary HIL/driver reference only; не target BOM part.

Parts на schematic готовой Waveshare board перечислены только для точной HIL
идентификации и **не входят автоматически в Leshy2 BOM**:

- power-management IC `AXP2101`;
- GPIO expander `TCA9554PWR`;
- audio codec `ES8311`;
- audio amplifier `NS4150B`;
- RTC `PCF85063ATL`;
- IMU `QMI8658`;
- TF socket marking `TF-07F`.

Waveshare описывает compute device как `ESP32-S3R8` с 16 MB flash и 8 MB
PSRAM, но reviewed page/schematic не дают достаточного orderable module MPN;
он поэтому не подменяется предположением.

## Raw-panel sourcing lead — not qualified

- OPL product-page identifier: product `226`, description “3.5 Inch
  `320×480` AXS15231B QSPI”.
- Controller marking: `AXS15231B`.
- Published LCM outline: `53.36×82.93×2.1 mm`; active area
  `48.96×73.44 mm`.
- Manufacturer panel MPN: **не опубликован**.
- Role: inquiry/sourcing lead only. До target нужны drawing, exact FPC pinout,
  touch option, samples, MOQ/lifecycle и независимый second source.

## Old 4-inch A0/control references

- Elecrow documentation family: `DLS31040B1` / `DLS31040B2`.
- Elecrow no-touch module variant: `MSP4030`.
- Elecrow capacitive-touch module variant: `MSP4031`.
- Display controller: Sitronix `ST7796S`.
- Touch controller: FocalTech `FT6336U`.
- Waveshare comparable old carrier: SKU `29318`, product name
  `3.5inch Capacitive Touch LCD`.
- Role: A0/control and fallback only. Эти references имеют 1-bit SPI display
  path и не реализуют target direct QSPI.

## EVE fallback part numbers

### Crystalfontz 4-inch

- Capacitive-touch module: `CFA480480E0-040TW`.
- Capacitive-touch development kit: `CFA480480E0-040TW-KIT`.
- No-touch module: `CFA480480E0-040TN`.
- No-touch development kit: `CFA480480E0-040TN-KIT`.
- EVE controller: Bridgetek `BT817`.
- Related raw-panel candidate listed by the same supplier:
  `CFAF480480A0-040TC`; состав конкретного EVE module этим совпадением не
  считается доказанным.
- Role: high-cost fallback, not baseline.

### Riverdi 4.3-inch

- No-touch module manufacturer MPN: `RVT43HLBFWN00`.
- No-touch store part number: `SM-RVT43HLBFWN00`.
- Capacitive-touch module manufacturer MPN: `RVT43HLBFWCA0`.
- Capacitive-touch store part number: `SM-RVT43HLBFWCA0`.
- EVE controller: Bridgetek `BT817Q`.
- Touch controller on the capacitive variant: Ilitek `ILI2132A`.
- Board connector shown in drawing: `648102131822`.
- Mating cable connector shown in drawing: `648002113322`.
- Role: outdoor/landscape fallback only; not baseline geometry or cost.

## Firmware component identifiers — not hardware MPNs

- Espressif component `espressif/esp_lcd_st77922`, reviewed stable version
  `2.0.2`.
- Espressif component `espressif/esp_lcd_axs15231b`, reviewed stable version
  `2.1.0`.

Эти package IDs снижают driver risk, но не определяют vendor init table,
точную панель, connector или production qualification.

## Primary sources

- [Elecrow/QDtech DLE06235B/ES3C35P specification](https://www.elecrow.com/download/product/DLE06235B/3.5inch_IPS_ESP32-S3_Specification.pdf)
- [QDtech ES3C35P official schematic with HMX035CTFT-001](https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf)
- [Hirose FH12-40S-0.5SH(55)](https://www.hirose.com/en/product/p/CL0586-0527-7-55)
- [Waveshare ESP32-S3-Touch-LCD-3.5B documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-3.5B)
- [Waveshare 3.5B schematic](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-3.5B/ESP32-S3-Touch-LCD-3.5B-Schematic.pdf)
- [OPL AXS15231B raw-panel sourcing page](https://www.opldisplaytec.com/product/226)
- [Elecrow DLS31040B family specification](https://www.elecrow.com/download/product/DLS31040B/4.0inch_SPI_Module_Specification.pdf)
- [Crystalfontz CFA480480E0-040TW](https://www.crystalfontz.com/product/cfa480480e0040tw-4-inch-480x480-cap-touch-solution)
- [Riverdi RVT43HLBFWN00 datasheet](https://download.riverdi.com/RVT43HLBFWN00/DS_RVT43HLBFWN00_Rev.1.7.pdf)
- [Riverdi RVT43HLBFWCA0 datasheet](https://download.riverdi.com/RVT43HLBFWCA0/DS_RVT43HLBFWCA0_Rev.1.4.pdf)
- [Espressif ST77922 component](https://components.espressif.com/components/espressif/esp_lcd_st77922)
- [Espressif AXS15231B component](https://components.espressif.com/components/espressif/esp_lcd_axs15231b)
