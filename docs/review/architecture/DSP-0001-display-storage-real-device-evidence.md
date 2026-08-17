# DSP-0001 — display, touch and removable-storage real-device evidence

> Последующее решение: `DEC-0052` принимает direct QSPI и measured `<=1 ms`
> display occupancy; `DSP-0003/IMP-0045` выбирают новый exact screen class.
> Historical ST7796S/shared-U214 evidence ниже сохраняется как A0 boundary.

- Статус: **Проведено ревью фактов и performance contract; exact target не выбран**
- Дата: 2026-08-17
- Gate: `FLOW-0001/G2F`, exact-peripheral pass
- Finding: [`FND-0051`](../findings/FND-0051-legacy-display-interface-and-throughput.md)
- Decision: [`DEC-0043`](../decisions/DEC-0043-task-based-display-performance.md)

## Проверенный function envelope

Текущим кандидатам нужен один локальный цветной дисплей, полный автономный
navigation/confirm path, читаемые safety/fault/TX states и bounded screen
traffic, который не блокирует U214, radio deadlines, audio или storage. Размер,
touch и exact part не приняты. Текущий электрический envelope резервирует
`SCK/MOSI/CS/DC`, reset-safe reset, PWM backlight и shared I2C для touch.

Touch не является единственным способом управления: выделенные STOP/PTT/re-arm
и согласуемые обычные controls остаются отдельными требованиями. Ввод длинного
текста допускается с телефона по `DEC-0038`.

## Реальные проверенные дисплейные границы

| Exact device | Реально выведенный интерфейс | Механика/оптика | Результат |
|---|---|---|---|
| Waveshare `3.5inch Capacitive Touch LCD`, SKU 29318 | 15-pin GH1.25 либо 18-pin 0.5 mm FPC; ST7796S `MISO/MOSI/SCLK/CS/DC/RST/BL`; FT6336U `SDA/SCL/INT/RST`; отдельный `SD_CS` | `61.00×92.44 mm`, IPS, active `48.96×73.44 mm`; 3.3/5 V carrier | точный и удобный prototype reference; встроенный TF делит SPI с LCD |
| Elecrow `DLS31040B1` (`MSP4031`) | 14-pin header/FPC; ST7796S SPI, FT6336U I2C, reset/IRQ/backlight и `SD_CS` | `60.88×108.0 mm`, 4.0-inch TN, 300 cd/m², 5 V recommended; conservative `14.8 mm` envelope with header | ближе всего к старой 4-inch геометрии и дешёвому prototype, но не outdoor/throughput proof |
| Riverdi `RVT35HITNWC00-B` | raw 50-pin 0.5 mm FPC; ILI9488 SPI or 24-bit RGB, ILI2130 I2C touch, separate 13.5–17 V/100 mA backlight | `59.56×93.34×5.66 mm`, IPS, optical bond, 1200 cd/m², `-20…70°C` | strong outdoor/production reference; добавляет boost, FPC and integration burden |

Каждый контакт этих трёх устройств внесён в
`hardware/architecture/devices.json`. Это подтверждает реальные разъёмы, но не
выбирает target part.

## Throughput check

У ST7796S минимальный паспортный период serial write clock равен `66 ns` для
3-wire и 4-wire SPI. Поэтому гарантированный silicon ceiling равен:

`1 / 66 ns = 15.15 Mbit/s = 1.89 MB/s` до command/CS/software overhead.

Один `320×480 RGB565` framebuffer равен `307,200 B`. Следовательно, даже
идеальный непрерывный поток даёт не более `1.89 / 0.3072 = 6.16` полных кадров
в секунду. Исторический budget требовал `10 full-frame-equivalents/s = 3.072
MB/s` и measured path `≥4.5 MB/s`. Он не может быть qualification gate для
ST7796S и не переносится в новые G2F-карты без отдельного решения.

Практика разгона конкретной платы выше datasheet ceiling не является
production proof. Аналогично, наличие QSPI в controller datasheet не доказывает,
что этот QSPI выведен на выбранном display module/carrier.

## Принятый task-based performance contract

`DEC-0043` заменяет synthetic full-frame rate на проверяемые задачи:

- critical safety/fault/actual-TX state и первый видимый menu feedback —
  `≤100 ms`;
- waterfall добавляет только новые строки/столбцы/области, допускает явное
  coalescing/drop evidence и не отнимает raw radio/audio capture;
- display transfers preemptible; полный redraw измеряется, но не выполняется
  периодически ради benchmark;
- при общем SPI с U214 pixel quantum `≤256 B`, а measured accessory
  IRQ-to-first-transfer `≤250 µs` при datasheet-valid display clock;
- провал scenario HIL переоткрывает interface/pin/power/cost comparison.

Для ориентира одна строка `320×RGB565` равна `640 B`, а область `100×40` —
`8,000 B`. Поэтому waterfall и меню не требуют полной пересылки `307,200 B`.
Это арифметическая достаточность low-pin envelope, но не квалификация exact
module, driver или shared-bus implementation.

## Legacy mismatch

Legacy `hardware/tscircuit/integration.tsx` описывает generic 24-position
0.5-mm bottom-contact connector `C19273968` и самостоятельно назначенный
24-pin panel pinout. Реальные ближайшие старому макету модули Waveshare и
Elecrow используют соответственно 15/18 и 14 contacts. Поэтому старый J_LCD
можно использовать только как геометрическую идею; его connector/net mapping
не является схемным входом.

## Removable microSD

Waveshare и Elecrow подключают onboard TF через тот же `MOSI/MISO/SCLK` и
отдельный `SD_CS`. Это SPI storage, а не текущий независимый S3 SDMMC path.
Подмена освободила бы GPIO, но одновременно связала display/storage arbitration
и пока не доказывает `1.5 MB/s` admitted recording, `4 MB/s` sustained read/write
gate и stall behavior. Такая экономия не проходит `DEC-0005` без HIL.

Для отдельного пути проверен exact socket `Hirose DM3AT-SF-PEJM5`: все восемь
card contacts, card-detect switch, `13.85×15.95×1.68 mm`, 10,000 cycles и
актуальные manufacturer drawings. Он является pin/mechanical candidate, не
production choice; 1-bit против 4-bit SDMMC и push-push против более дешёвого
push-pull сравниваются отдельно.

## Открытые gates

- exact target display, brightness/glove/water/cover-lens and temperature;
- exact touch interrupt/polling и ordinary-control IRQ/wake topology;
- display/microSD shared-SPI2 HIL с QSPI/SPI mode switching, CS-high high-Z,
  datasheet-valid clocks и `<=1 ms` display occupancy;
- 1-bit/4-bit microSD HIL, qualified cards, socket position and hot removal;
- lifecycle, authorised supply, unit price, assembly and repair comparison.

Ни exact display, ни microSD строка пока не получают target/Q status.

## Первичные источники

- [Waveshare 3.5inch Capacitive Touch LCD](https://www.waveshare.com/wiki/3.5inch_Capacitive_Touch_LCD)
- [Waveshare module schematic](https://files.waveshare.com/wiki/3.5inch%20Capacitive%20Touch%20LCD/3.5inch_Capacitive_Touch_LCD_Schematic.pdf)
- [Elecrow DLS31040B1/B2 specification](https://www.elecrow.com/download/product/DLS31040B/4.0inch_SPI_Module_Specification.pdf)
- [Riverdi RVT35HITNWC00-B Rev.1.1](https://download.riverdi.com/RVT35HITNWC00-B/DS_RVT35HITNWC00-B_Rev.1.1.pdf)
- [Sitronix ST7796S V1.0](https://dl.espressif.com/dl/schematics/ST7796S_SPEC_V1.0.pdf)
- [Hirose DM3AT-SF-PEJM5](https://www.hirose.com/product/p/CL0609-0031-0-00)
- [Legacy connector C19273968 actual identity](https://www.lcsc.com/product-detail/FFC-FPC-Flat-Flexible-Connector-Assemblies_Hong-Cheng-HC-FPC-0-5-24P-CXH20_C19273968.html)
