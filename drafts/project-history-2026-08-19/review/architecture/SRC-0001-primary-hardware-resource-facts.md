# SRC-0001 — primary hardware resource facts before synthesis

- Статус: **Проведено ревью прежнего candidate fact set; дополнен обязательным SRC-0002 provenance gate**
- Дата: 2026-08-16
- Этап: 3, пререквизит полного `SYN-*`
- Входы: reviewed `CAP-0001`, `CON-0001`, `RES-0001`
- Источники: только актуальные datasheet/product documentation производителей
- Не входы: legacy schematic/source, прежние owner/pin maps и прежний список архитектурных вариантов

## Назначение

Этот baseline не выбирает архитектуру. Он фиксирует физические факты, которые каждый новый synthesis обязан учитывать до утверждения, что вариант «сходится»: точную module variant, выведенные наружу GPIO, memory-reserved и strapping pins, аппаратные controllers, recovery interfaces и сигналы принятых периферийных блоков.

Общее количество GPIO само по себе ничего не доказывает. В `PIN-*` вывод считается доступным лишь после исключения module-internal memory, boot straps, native USB/recovery, fixed-function interfaces и электрически несовместимых ролей.

`FND-0049` уточняет границу этого review: `SRC-0001` хорошо проверял compute
module resources и semantic peripheral interfaces, но не выбирал exact
carrier/device для всей периферии. Любой новый pin map дополнительно обязан
закрыть [`SRC-0002`](SRC-0002-real-device-pin-provenance.md).

## ESP32-S3 application/native-2.4/BLE domain

Первичный источник: [ESP32-S3-WROOM-1/WROOM-1U datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf). Peripheral behavior дополнительно проверяется по официальным [SPI](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/spi_master.html), [I2S](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/i2s.html), [SDMMC](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdmmc_host.html) и [USB](https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_device.html) documentation.

| Fact ID | Проверенный факт | Следствие для synthesis |
|---|---|---|
| `SF-S3-01` | WROOM-1 module выводит GPIO0…21 и GPIO35…48; GPIO26…32 принадлежат module memory path, а не являются свободными board GPIO | candidate pin map строится по выводу конкретного модуля, не по maximum SoC GPIO |
| `SF-S3-02` | `N16R2` содержит 16 MB Quad flash и 2 MB Quad PSRAM; `N16R8` — 16 MB Quad flash и 8 MB Octal PSRAM | memory variant является архитектурным параметром, а не прозрачной BOM substitution |
| `SF-S3-03` | у Octal-PSRAM variants GPIO35…37 недоступны приложению; Quad-PSRAM `N16R2` их сохраняет | переход R2→R8 покупает 6 MB PSRAM ценой трёх GPIO; сравниваются обе стороны trade-off |
| `SF-S3-04` | strapping pins — GPIO0, GPIO3, GPIO45, GPIO46 | любой внешний pull/driver на них обязан доказать корректный reset/boot state |
| `SF-S3-05` | native USB использует GPIO19/20; USB-OTG и USB-Serial/JTAG делят internal PHY | USB/recovery резервируется до произвольного GPIO allocation; два одновременных native USB-интерфейса не предполагаются |
| `SF-S3-06` | SPI0/1 заняты memory; для general-purpose use доступны SPI2 и SPI3 | количество независимых SPI scheduling domains ограничено двумя до software/PIO-style alternatives |
| `SF-S3-07` | SoC имеет два I2S controllers | full-duplex codec path можно отделить от второго synchronous stream, но exact DMA/pin coexistence ещё доказывается |
| `SF-S3-08` | SDMMC host предоставляет два slots и допускает GPIO-matrix routing | microSD и второй SD/SDIO endpoint являются проверяемой возможностью, но их одновременность, pin map и throughput не считаются доказанными без candidate/HIL |

### Memory lower bound, не выбор variant

Для reference UI 320×240 RGB565 один полный framebuffer требует `320 × 240 × 2 = 153 600 B`, двойной — `307 200 B` без metadata. Это показывает, что 2 MB PSRAM нельзя автоматически объявить недостаточными; одновременно это не доказывает достаточность `N16R2` для всех capture/decoder/crypto scenarios. Каждый `SYN-*` обязан разложить PSRAM по consumer и оставить измеримый reserve.

## ESP32-C5 dual-band/802.15.4/IR domain

Первичные источники: [ESP32-C5-WROOM-1/WROOM-1U datasheet](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf), [ESP32-C5 SoC datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.pdf) и официальная [SDIO slave documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c5/api-reference/peripherals/sdio_slave.html).

| Fact ID | Проверенный факт | Следствие для synthesis |
|---|---|---|
| `SF-C5-01` | WROOM-1U PSRAM variants выводят GPIO0…14 и GPIO23…28; GPIO15 занят `SPICS1` package PSRAM и недоступен | для `N8R8/N16R8` practically available set начинается с 21 module GPIO до reservations, не с рекламного «up to 22» |
| `SF-C5-02` | `N8R8` содержит 8 MB Quad flash и 8 MB Quad PSRAM; `N16R8` увеличивает flash до 16 MB | variant выбирается после update partitions и runtime memory budget; PSRAM pin cost одинаков для этих двух variants |
| `SF-C5-03` | C5 имеет один general-purpose SPI controller, SPI2; SPI0/1 относятся к memory | два независимых внешних GP-SPI roles нельзя назначить C5 без sharing, bit/parallel engine, bridge или дополнительного controller proof |
| `SF-C5-04` | SDIO slave 1-bit использует GPIO9/10/8/7 (`CLK/CMD/DAT0/DAT1`); 4-bit добавляет GPIO13/14 | 1-bit path оставляет native USB, 4-bit path электрически пересекается с ним |
| `SF-C5-05` | native USB Serial/JTAG использует GPIO13/14; Espressif прямо разрешает его совместно с single-SPI/1-bit SDIO, но не с quad/4-bit SDIO | recovery и high-width IPC сравниваются как взаимосвязанный package, не как независимые решения |
| `SF-C5-06` | SDIO controller не поддерживается chip revisions v0.0/v0.1 | любой SDIO-candidate фиксирует minimum silicon revision ≥1.0 и проверяет marking/boot report в production test |
| `SF-C5-07` | RMT предоставляет два TX и два RX channels | принятые два одновременных IR RX занимают оба RX channel; один carrier TX оставляет один TX channel, но не дополнительные capture channels |
| `SF-C5-08` | boot mode использует GPIO26/27/28; SDIO edge/JTAG/ROM behavior затрагивает GPIO25, GPIO3, GPIO2, GPIO7/27 | эти pins не запрещены после boot, но attached circuitry и defaults проверяются как strap-sensitive |
| `SF-C5-09` | WROOM-1U по умолчанию использует ANT1; ANT2 требует отдельного заказного variant/path | внешний antenna connector сам по себе не создаёт две одновременно доступные RF chains |

## Принятые внешние и packet-radio interfaces

| Блок | Первичный факт | Минимум, который обязан учесть synthesis |
|---|---|---|
| 3×nRF24L01+ | [Nordic product specification](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/nRF24L01P_5F00_PS_5F00_v1.0.pdf) задаёт `CE`, `CSN`, `SCK`, `MOSI`, `MISO`, `IRQ`; SPI до 10 Mbit/s | при одной общей SPI data/clock группе остаются три независимых `CSN`, три reset-safe `CE` и три source-identifiable IRQ states; иная compression logic обязана сохранить те же semantics |
| CC1101 | [TI datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf) задаёт 4-wire SPI, `CSn` и programmable `GDO0/GDO2`, при этом `GDO1` делит pin с SPI `SO` | shared SPI допустим только при отдельном select и bounded event/FIFO service; GDO topology выбирается по mode set, а не по минимальному числу проводов |
| U214 Cap LoRa-1262 | [M5Stack U214 documentation](https://docs.m5stack.com/en/cap/Cap_LoRa-1262) выводит LoRa `NSS/MISO/MOSI/SCK/BUSY/IRQ/RST`, GNSS UART TX/RX, I²C SCL/SDA, 5 V и GND через Cap-Bus | «поддержать Cap» означает разместить весь 14-pin electrical/mechanical profile; LoRa и GNSS не сворачиваются в один generic SPI connector |
| Unit GPS v1.1 | [M5Stack Unit GPS documentation](https://docs.m5stack.com/en/unit/Unit-GPS%20v1.1) задаёт 5 V и UART, default 115200 bit/s, navigation output до 10 Hz | отдельный GPS profile требует 5 V power control и UART pair; advanced status зависит от exact revision/firmware qualification |
| Unit NFC U216-class | [M5Stack Unit NFC documentation](https://docs.m5stack.com/en/unit/Unit_NFC) задаёт 5 V Grove/PORT.A profile и I²C | base connector обязан безопасно дать 5 V, 3.3 V-compatible control, removal state и STOP-reachable RF-field/power inhibit |

Сами interface facts не выбирают владельца. Например, общая SPI группа nRF24 может принадлежать S3, C5, отдельному controller или иной доказанной локальной логике; `SRC-0001` запрещает только терять независимые `CE/CSN/IRQ` semantics.

## Дополнительный deterministic-controller search space

Legacy-документация ограничивалась S3/C5 placement. Zero-based synthesis обязан также проверить, выгоднее ли дешёвый локальный controller набора expander/latch/decoder и критических remote loops.

Первичные источники: [RP2350/RP2354 product page](https://www.raspberrypi.com/products/rp2350/), [RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) и [официальное сообщение об A4/RP2354](https://www.raspberrypi.com/news/rp2350-a4-rp2354-and-a-new-hacking-challenge/).

| Fact ID | Проверенный факт | Архитектурная граница |
|---|---|---|
| `SF-AUX-01` | RP2354A: QFN60 7×7 mm, 30 GPIO, 2 MB stacked flash, 520 KB SRAM | это реальный third-domain candidate без отдельной external flash, а не принятый component |
| `SF-AUX-02` | доступны 2×SPI, 2×UART, 2×I²C, USB 1.1 и 12 PIO state machines | прямые radio controls и bounded edge service технически возможны; exact mux/pin/update map всё равно обязателен |
| `SF-AUX-03` | silicon поддерживает optional ROM-enforced signed boot и owner-programmed OTP | необратимый ROM lockdown не включается baseline-архитектурой: открытый owner-controlled update/recovery contract `DEC-0013` остаётся доминирующим |
| `SF-AUX-04` | A4 исправляет известный A2 GPIO high-impedance erratum и обновляет security behavior | candidate обязан называть exact A4 stepping/MPN; generic `RP2350/RP2354` в BOM недостаточен |

Добавление controller проходит только если полный ledger учитывает его firmware, signed update, independent recovery, IPC, idle/active power, PCB area, HIL и sourcing. Экономия на GPIO expanders без этих строк недействительна.

## Что эти факты намеренно не решают

- кто владеет 3×nRF24, CC1101, codec, voice, display, storage или U214;
- нужен ли третий programmable domain;
- какой S3/C5 memory variant является оптимальным;
- будет ли междоменный link SDIO, SPI, UART, USB или комбинацией;
- сколько buses следует физически разделить;
- exact display/touch MPN и connector pinout (последующий `DSP-0005` закрыл
  assembly contact map как paper candidate, но не production connector);
- окончательную цену, доступность, RF module/PA/LNA variant и PCB dimensions.

Эти решения допустимы только в полном `SYN/PIN/PKG` package. Цена и наличие являются нестабильными данными и фиксируются отдельным датированным supplier snapshot одинакового quantity/region для всех candidates.

## Review checklist

- [x] MCU/module facts взяты из первичных manufacturer documents;
- [x] SoC maximum GPIO не подменяет module-exposed GPIO;
- [x] flash/PSRAM variant связан с lost pins и update/memory budget;
- [x] USB, SDIO, strapping и silicon-revision constraints перечислены до pin allocation;
- [x] nRF/CC1101/U214/GPS/NFC signal contracts разложены без owner assignment;
- [x] третий controller добавлен только в search space, не принят заранее;
- [x] прежние S3-heavy/C5-heavy/balanced maps не использованы;
- [x] никакой факт не объявлен готовой архитектурой.

`SRC-0001` получает статус **«Проведено ревью»** и становится обязательным фактологическим входом для каждого нового `SYN-*`.
