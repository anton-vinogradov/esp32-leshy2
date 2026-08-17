# DSP-0003 — exact fast-display shortlist after QSPI decision

- Статус: **Проведено ревью; target class принят `DEC-0053`, production MPN открыт**
- Дата: 2026-08-17
- Decision: [`DEC-0052`](../decisions/DEC-0052-qspi-first-display-path.md)
- Class decision: [`DEC-0053`](../decisions/DEC-0053-new-35in-qspi-display-class.md)
- Finding: [`FND-0062`](../findings/FND-0062-old-four-inch-display-is-not-qspi.md)
- Accepted proposal: [`IMP-0045`](../improvements/IMP-0045-new-35in-qspi-display-class.md)
- Review: [`REV-0004Y`](../reviews/REV-0004Y-exact-fast-display-shortlist.md)
- Part-number register: [`DSP-0004`](DSP-0004-display-part-number-register.md)

## Что означает «подходит старый 4 дюйма»

Нужно разделять три свойства:

1. **Product workload:** подходит — menu и waterfall из малых областей можно
   реализовать даже на ST7796S 1-bit SPI.
2. **Accepted electrical direction:** не подходит — exact old module не
   выводит QSPI D2/D3 и не реализует `DEC-0052`.
3. **Physical idea:** portrait window около прежнего размера можно сохранить,
   но exact panel/enclosure должны быть повторно проверены; диагональ сама по
   себе не является архитектурой.

Old 4-inch reference имеет `320×480`, active area примерно `55.68×83.52 mm`,
carrier около `60.88×108 mm`, ST7796S 4-wire SPI, capacitive-touch variant и
typical 300 cd/m². Он остаётся дешёвым A0 control fixture для сравнения
renderer/quantum, но не direct-QSPI target.

## Проверенные актуальные варианты

Широкая сравнительная таблица заменена вертикальными карточками, чтобы
документ читался на узком экране. Полный реестр обозначений — в `DSP-0004`.

### Primary HIL — Elecrow/QDtech

- Part identifiers: Elecrow `DLE06235B`; QDtech `ES3C35P`.
- Path: 3.5-inch `320×480` IPS, capacitive touch, `ST77922`, QSPI display и
  I2C touch.
- Mechanics/optics: active `48.96×73.44 mm`; complete board
  `54.50×101.50×10.0 mm`; 300 cd/m²; `-30…80 °C`.
- Power evidence: 5 V complete board; display-only 0.97 W, backlight 120 mA.
- Disposition: **primary new-screen HIL**. Integrated S3 board не доказывает
  production panel, connector или touch MPN.

### Secondary HIL — Waveshare

- Part identifiers: `ESP32-S3-Touch-LCD-3.5B`, SKU `31137`.
- Path: 3.5-inch `320×480` IPS, `AXS15231B`, four-data-line QSPI, integrated
  capacitive touch.
- Optics: 210 cd/m², contrast 1000:1.
- Supply evidence: orderable complete development board.
- Disposition: **secondary HIL/driver reference**. Published brightness не
  позволяет заморозить его как field target.

### Raw-panel sourcing lead — OPL

- Page identifier: product `226`; manufacturer panel MPN не опубликован.
- Path: 3.5-inch `320×480`, QSPI-capable `AXS15231B`.
- Mechanics: LCM `53.36×82.93×2.1 mm`; active `48.96×73.44 mm`.
- Disposition: inquiry-only sourcing lead. FPC, touch option, MOQ, lifecycle и
  second source не доказаны.

### High-end fallback — Crystalfontz

- Part identifier: `CFA480480E0-040TW`.
- Path: 4-inch `480×480`, `BT817` EVE, host SPI/QSPI, capacitive touch.
- Mechanics/optics: `86×86×9.7 mm`; active примерно `71.86×70.18 mm`; не
  заявлен sunlight-readable.
- Cost evidence: `$104.08` at qty 1 on reviewed date.
- Disposition: technically valid **EVE fallback**, но дорогой и шире legacy
  75-mm body hypothesis.

### Outdoor/landscape fallback — Riverdi

- Part identifiers: no-touch `RVT43HLBFWN00`; capacitive-touch
  `RVT43HLBFWCA0`.
- Path: 4.3-inch `480×272`, `BT817Q`, host SPI/QSPI.
- Mechanics/optics: `106.30×83.98×9.05 mm`; no-touch variant 1000 cd/m²;
  landscape orientation.
- Disposition: outdoor/EVE evidence, но меняет width/aspect и BOM.

The old 4-inch current supplier class is listed from about `$13.50`; therefore
replacing it with a `$104` 4-inch EVE module is not a zero-loss cost
optimization. A 3.5-inch QSPI panel class is the only reviewed route that
preserves direct S3 ownership, portrait `320×480`, low pin count and plausible
consumer-scale cost.

## Controller/driver maturity

Both new 3.5-inch controller families have official Espressif components:

- `esp_lcd_axs15231b`, with SPI/QSPI support and integrated touch path;
- `esp_lcd_st77922`, with SPI/QSPI/RGB/MIPI support.

This lowers driver risk but does not qualify a vendor init table, exact glass,
FPC or touch implementation. Each specimen still needs readback/identity,
reset/init, rotation, partial-window, sleep/wake, touch, long-run and bus-sharing
tests.

## Accepted prototype and production boundary

1. Keep the existing old 4-inch ST7796S module as A0 control: it measures the
   free gain from the new `<=1 ms` quantum.
2. Use Elecrow/QDtech ST77922 3.5-inch QSPI as the primary new-screen HIL
   reference because its published 300 cd/m² and `-30…80°C` boundary are
   stronger than the Waveshare reference.
3. Use Waveshare AXS15231B 3.5B as a second-controller/driver/supply reference,
   not as an outdoor target.
4. `DEC-0053` calls the target only **3.5-inch portrait QSPI `320×480` IPS + capacitive
   touch class**. Do not freeze a complete dev board or raw FPC until two-source
   procurement, exact connector/pinout, brightness/cover-lens, power and shared
   SD HIL pass.

The 3.5-inch active area is about 23% smaller than the old 4-inch active area.
This can reduce enclosure width/height, but legibility, glove/control layout
and waterfall density must be checked in the adapted physical mockup before
production acceptance. Все известные part identifiers и честные `TBD`
перечислены в `DSP-0004`.

## Первичные источники

- [Elecrow DLE06235B product/specification](https://www.elecrow.com/3-5-esp32-s3-display-320x480-capacitive-ips-touchscreen-with-speaker-mic-bat-interface-supports-ai-voice-chat.html)
- [Elecrow/QDtech 3.5-inch ST77922 specification](https://www.elecrow.com/download/product/DLE06235B/3.5inch_IPS_ESP32-S3_Specification.pdf)
- [Waveshare ESP32-S3-Touch-LCD-3.5B](https://www.waveshare.com/product/esp32-s3-touch-lcd-3.5b.htm)
- [Espressif AXS15231B component](https://components.espressif.com/components/espressif/esp_lcd_axs15231b)
- [Espressif ST77922 component](https://components.espressif.com/components/espressif/esp_lcd_st77922)
- [OPL 3.5-inch AXS15231B raw-panel reference](https://www.opldisplaytec.com/product/226)
- [Elecrow old 4-inch ST7796 supplier class](https://www.elecrow.com/4-inch-480-320-spi-tft-lcd-module-with-st7796-driver.html)
- [Crystalfontz CFA480480E0-040TW](https://www.crystalfontz.com/product/cfa480480e0040tw-4-inch-480x480-cap-touch-solution)
- [Riverdi RVT43HLBFWN00 datasheet](https://download.riverdi.com/RVT43HLBFWN00/DS_RVT43HLBFWN00_Rev.1.7.pdf)
