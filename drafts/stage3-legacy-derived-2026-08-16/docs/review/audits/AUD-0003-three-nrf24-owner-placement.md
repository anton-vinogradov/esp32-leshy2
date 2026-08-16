> Архивировано решением DEC-0027: этот документ оптимизировал legacy-derived раскладку и не является входом новой архитектуры. Сохранён только как источник идей и отрицательных результатов.

# AUD-0003 — сравнительный аудит владельца трёх полнофункциональных nRF24

- Статус: **Проведено ревью preliminary variants; full static comparison выполнено в `CMP-0001/REV-0003G`**
- Дата: 2026-08-16
- Этап: 2→3 ownership prerequisite
- Входы: actual tsCircuit net map, `DEC-0001`, `DEC-0009`, `DEC-0018`, `DEC-0021`, `FND-0001`, `FND-0019`, `REQ-N24-0001`, official S3/C5/nRF24/U214 sources

## Неподвижные инварианты

- остаются три одновременных exact-qualified nRF24 path;
- каждый radio сохраняет полный native nRF24L01+ feature set; BLE-compatible subset не определяет его потолок;
- один MCU владеет driver/scheduler/state, другой использует typed IPC;
- per-radio logical CE/CS и разные PTX/PRX/channel/rate/address обязательны;
- Main/Lab/Controlled Zone, conservative TX, hardware STOP и RF containment сохраняются;
- один radio, RF-switch вместо трёх, общий неразделимый CE или перенос security gates не считаются экономией без потерь.

## Реальные пересечения pin/resource

### S3

Текущий source назначает все 36 выведенных GPIO S3. Однако target-архитектура освобождает четыре линии, не сокращая принятые функции:

- IR TX/RX уходят на C5; dual-path IR C5 получает собственные три линии и не использует S3 GPIO2/GPIO42;
- legacy UART flash bridge S3→C5 не является requirement: C5 уже имеет собственный USB Serial/JTAG, physical BOOT/RESET и signed update/rollback через выбранный transport. После отдельного recovery proof GPIO43/GPIO44 могут стать двумя оставшимися I²S lines;
- тогда ES8311 получает четыре I²S GPIO из `2/42/43/44`, а nRF сохраняет текущие direct-control GPIO6/GPIO46.

Onboard LoRa/GNSS removal нельзя считать дополнительными свободными direct pins для S3: U214 использует SPI+NSS+BUSY+IRQ+RST и GNSS UART, а отдельный `PORT.C` сохраняет UART.

### C5

C5-WROOM выводит существенно меньше свободных GPIO и имеет один GP-SPI. Если nRF остаются C5, inter-MCU link должен уйти с GP-SPI — наиболее реалистично на 1-bit SDIO (`GPIO7..10`) после exact chip-revision proof. Вместе с USB `GPIO13/14`, тремя IR lines, nRF SPI/decode/CE/IRQ и straps/recovery бюджет становится плотным и почти не оставляет резерва.

## Варианты

| Вариант | Что требуется | Сильные стороны | Цена/риск | Вывод |
|---|---|---|---|---|
| A. S3 owner, общий SPI2 | существующая SPI/74HC138 разводка; reset-safe 3-bit CE latch/expander на текущем CE-control GPIO; существующий IRQ combiner; priority/chunked bus arbiter; убрать UART bridge только после C5 USB recovery proof | минимальная PCB-переделка; нет raw-frame IPC; `FND-0001` исчезает; BLE+nRF coexistence локально на S3; C5 освобождён для Wi-Fi/802.15.4+IR | display/SD/CC1101/U214 делят SPI; high-rate nRF capture требует latency/loss HIL; CE latch — новый малый BOM | **Предварительный S3-heavy кандидат; не выбран** |
| B. C5 owner, dedicated GP-SPI | S3↔C5 link переносится на 1-bit SDIO; C5 exact revision; новая C5-local SPI/decode/CE/IRQ разводка | nRF не конкурирует с S3 display/SD SPI; C5 локально планирует nRF+802.15.4 | tight C5 GPIO; SDIO/recovery/NRE; raw capture IPC; полная переразводка; exact-revision dependency | рабочий fallback, но не дешевле и не проще |
| C. S3 owner, отдельный SPI3 | inter-MCU link переносится на SDIO/UART, добавляется отдельная физическая nRF bus group | лучший bus isolation/throughput | дополнительные S3 pins конфликтуют с ES8311/U214/recovery; transport NRE | performance option только после провала A HIL |
| D. Разделить radio между S3/C5 | два drivers/schedulers и cross-owner aggregation | теоретическая параллельность | две state machines, сложная calibration/timebase/STOP, два transport paths; нет принятого use case | не рекомендован |
| E. Dedicated bridge/third MCU | отдельный radio controller | изоляция bus/real-time | новый BOM, firmware/update/trust/HIL и power | только если A/B не проходят proof |

## Почему общий SPI2 не означает урезанный nRF24

Все три radio могут одновременно находиться в PRX, потому что CE-state хранится независимо во внешнем latch, а IRQ объединяется с последующим чтением STATUS каждого radio. SPI нужен для configuration и FIFO service, а не для самого on-air RX. Полный feature set сохраняется, но максимальная без потерь packet rate при параллельной работе не обещается до измерения.

Acceptance варианта A требует:

1. reset/STOP принудительно очищает все CE независимо от S3 firmware;
2. CE latch не принимает случайное состояние от display/SD SPI traffic;
3. bus arbiter ограничивает максимальный непрерываемый display/SD/U214 transaction chunk;
4. worst-case three-radio 2 Mbit/s fixture измеряет FIFO overflow, IRQ latency, timestamp skew и coverage/loss;
5. UI показывает measured loss/coverage и не называет capture lossless без доказательства;
6. C5 USB/BOOT/RESET восстанавливают firmware без UART bridge и без работающей S3;
7. exact S3 pin table одновременно покрывает ES8311, U214, GNSS, C5 link, USB и nRF.

## Стоимость

Вариант A сохраняет текущую сторону MCU и большую часть nets. Его новый hardware-кандидат — маленький reset-safe CE latch/expander и decoupling; цена подтверждается только BOM quote. Вариант B добавляет SDIO routing/pull-ups/revision qualification и перенос всей nRF control-side. Поэтому на текущем неполном demand model A предварительно дешевле, но вывод пересчитывается после `INV-0002` freeze, а zero-loss статус появляется только после HIL.

## Первичные источники

- [ESP32-S3 datasheet: SPI2/SPI3 и GPIO](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-C5 datasheet: один GP-SPI и SDIO slave](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [ESP32-C5 SDIO fixed pins and revision condition](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html)
- [ESP32-C5 SDIO 1-bit connection](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-reference/peripherals/sdio_slave.html)
- [M5Stack U214 SPI/UART/IRQ/BUSY/RST pin map](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)

