# DSP-0002 — fast display path options

- Статус: **Проведено ревью; QSPI-first принят `DEC-0052`, class принят `DEC-0053`, production MPN открыт**
- Дата: 2026-08-17
- Current evidence: [`DSP-0001`](DSP-0001-display-storage-real-device-evidence.md)
- Finding: [`FND-0061`](../findings/FND-0061-stale-display-quantum-after-u214-move.md)
- Proposal: [`IMP-0044`](../improvements/IMP-0044-qspi-first-fast-display-path.md)
- Decision: [`DEC-0052`](../decisions/DEC-0052-qspi-first-display-path.md)
- Review: [`REV-0004W`](../reviews/REV-0004W-fast-display-path-options.md)

## Короткий ответ о текущем bottleneck

Экран с microSD на S3 SPI2 — единственная оставшаяся **намеренно разделяемая
high-rate** группа. Все radio buses и оба межпроцессорных IPC имеют отдельные
controllers/data paths. Internal I2C, status/control UART и slow expander
физически медленнее, но их принятые задачи состоят из коротких команд и событий;
они не являются bulk-throughput bottleneck.

Поэтому в пользовательском смысле экран — единственный интерфейс, где текущая
low-pin реализация заметно ограничивает скорость. Технически с ним связан и
microSD: card stall либо длинная storage transaction способна задержать UI,
пока общий SPI2 scheduler не доказан HIL. Остальные открытые RF, power, SI и
HIL gates не становятся закрытыми только от ускорения экрана.

## Почему текущий экран кажется медленнее необходимого

Проверенные дешёвые references на ST7796S используют 1-bit SPI. Паспортный
минимальный serial-write period `66 ns` задаёт silicon ceiling около
`15.15 Mbit/s = 1.89 MB/s` до protocol/software overhead. Полный
`320×480×RGB565` frame содержит `307,200 B`, но продукту нужны меню и waterfall
из малых изменённых областей, а не постоянное video-like обновление.

Дополнительно current resource contract режет каждый display transfer до
`256 B`. Этот лимит был нужен прежней карте с U214 на том же bus. В `G2F-3I`
U214 уже имеет dedicated RP PIO SPI, поэтому лимит устарел. Даже без смены
панели time-bounded quantum позволяет передать целую `640 B` строку waterfall
одной DMA transaction, если измеренная длительность и SD latency проходят
gate.

## Реальный GPIO envelope S3

Exact `ESP32-S3-WROOM-1U-N16R2` map до display decision имела четыре свободных,
реально выведенных контакта: `GPIO6`, `GPIO41`, `GPIO42`, `GPIO43`. C5 имеет
один свободный GPIO, RP2354B — ни одного. `DEC-0052` занимает GPIO41/42 под
QSPI D2/D3 и оставляет S3 GPIO6/43 свободными. Следовательно, перенос экрана
на текущие C5/RP без remap невозможен, а S3 расширяет data path до QSPI.

Принятый `DEC-0052` working net map:

| QSPI function | S3 contact | Current/reuse state |
|---|---|---|
| `LCD_SCK` | `GPIO35` | существующий shared display/SD clock |
| `LCD_D0` | `GPIO36` | существующий MOSI |
| `LCD_D1` | `GPIO4` | существующий SD MISO; допустимо только после CS-high tri-state proof |
| `LCD_D2` | `GPIO41` | свободный exact module contact |
| `LCD_D3` | `GPIO42` | свободный exact module contact |
| `LCD_CS_N` | `GPIO38` | существующий LCD CS |
| `LCD_TE`, optional | `GPIO43` | optional tear/sync input; нужен только если exact controller его выводит и HIL доказывает пользу |

`GPIO6` остаётся direct reserve; без TE свободными остаются `GPIO6/GPIO43`.
SD продолжает работать как обычный 1-bit SPI client. QSPI display transaction
допустима только при `SD_CS_N=1`, а SD transaction — при `LCD_CS_N=1`; card и
display должны доказанно отпускать общие линии вне выбора. Exact panel/module
обязан реально выводить D0…D3: наличие QSPI внутри controller silicon этого не
доказывает.

ESP32-S3 LCD peripheral официально поддерживает SPI, Quad SPI и Octal SPI с
DMA. QSPI pixel payload переносит четыре data bits за clock вместо одного;
raw ceiling равен `4 × f_clock / 8`, но production throughput задаётся меньшим
из пределов S3, exact controller/module, signal integrity и software path.

## Сравнение путей

| Вариант | Что разгружает | GPIO/BOM | Преимущества | Цена и риск |
|---|---|---|---|---|
| `A0` current 1-bit SPI + time quantum | только лишний transaction overhead | `+0 GPIO`, `+0 IC` | немедленная дешёвая проверка; вероятно достаточно для accepted menu/waterfall workload | full-redraw ceiling ST7796S почти не меняется; exact HIL обязателен |
| `A1` direct QSPI from S3 | в 4 раза расширяет raw pixel data width; DMA остаётся у S3 | `+2 GPIO`, optional `+1 TE`; без нового compute | лучший performance/price/power/firmware balance; сохраняет один owner и open update chain | нужен exact QSPI panel; shared D1 tri-state, mode switching, SI and SD-stall HIL |
| `B` BT817/BT818 EVE controller | widgets, command list, scanout и framebuffer memory уходят в display coprocessor | QSPI host, QFN64/controller/RGB panel/flash/power | настоящий display offload без четвёртого application firmware; хорошо для richer UI | заметно дороже и больше PCB/NRE; waterfall rows всё равно передаются; меняет panel/mechanics stack |
| `C` fourth display MCU | весь renderer и panel interface | MCU, flash/PSRAM, rails, recovery/service and IPC | максимальная изоляция и свобода RGB/I80 | максимальные BOM/area/power/update/signing/boot/failure costs; ещё один EMI source |
| `D` direct I80/RGB from current S3 | широкая или continuous pixel шина | минимум 8/16 data pins plus controls | высокий throughput без extra compute | не помещается ни в исходные 4, ни в current 2 free GPIO; RGB также нежелателен с current 2 MB Quad-PSRAM module; требует whole-map redesign |

Перенести экран на уже существующий RP или C5 нельзя считать вариантом
разгрузки: у них нет pin budget, и это снова связало бы UI service с real-time
radio owner. Добавлять четвёртый MCU до доказанного провала A/B противоречит
цели снизить стоимость без потерь.

## Реальные reference boundaries

- Waveshare `ESP32-S3-Touch-LCD-3.5B` показывает реально существующий
  `320×480` AXS15231B path с четырьмя QSPI data lines и capacitive touch. Это
  ecosystem/prototype proof, а не выбранная standalone production panel.
- Bridgetek BT817/BT818 имеет QSPI host до `30 MHz`, 1 MB graphics RAM,
  graphics engine и RGB panel output. Riverdi `RVT43HLBFWN00` — exact
  `480×272` BT817Q module с QSPI/SPI host and external flash; он доказывает
  готовый EVE путь, но несёт существенно иной panel/BOM/mechanical envelope.
- I80 ESP32-S3 требует 8/16 data lines, RGB — 8/16/24. Текущий GPIO budget
  исключает оба без архитектурной перекладки.

## Рекомендуемая последовательность проверки

1. На current ST7796S reference заменить только fixed-byte slicing на
   instrumented time budget; измерить whole-row/dirty-region latency,
   `<=100 ms` feedback, SD `>=4 MB/s`, admitted `1.5 MB/s` record и injected
   `250 ms` card stalls.
2. Параллельно квалифицировать один exact `320×480` QSPI panel/module и
   проверить D1/SD tri-state, per-device modes/clocks, DMA, signal integrity,
   full redraw and waterfall under the same scenario.
3. Принять direct QSPI, если он проходит workload и power/EMI/cost gates.
4. Перейти к BT817/BT818 EVE только при измеренном провале direct QSPI либо при
   принятом расширении UI до richer retained graphics.
5. Рассматривать четвёртый MCU только если не проходят и direct QSPI, и EVE,
   либо scope меняется на video/high-animation class.

## Первичные источники

- [Espressif SPI/Quad/Octal LCD and DMA API](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/spi_lcd.html)
- [Espressif LCD guide: QSPI lines, bandwidth and TE](https://docs.espressif.com/projects/esp-iot-solution/en/latest/display/lcd/lcd_guide.html)
- [Espressif I80 LCD interface](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/lcd/i80_lcd.html)
- [Espressif RGB LCD interface](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html)
- [ESP32-S3-WROOM-1/1U datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [Bridgetek BT817/BT818 datasheet](https://brtchip.com/wp-content/uploads/2022/04/DS_BT817_8.pdf)
- [Riverdi RVT43HLBFWN00 BT817Q module](https://download.riverdi.com/RVT43HLBFWN00/DS_RVT43HLBFWN00_Rev.1.7.pdf)
- [Waveshare ESP32-S3-Touch-LCD-3.5B QSPI reference](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-3.5B)
