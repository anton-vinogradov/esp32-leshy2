# FND-0019 — текущий 3×nRF24 artifact не принадлежит C5, не fail-safe и не квалифицирован

- Статус: **Частично исправлено консервативно; implementation finding открыт**
- Серьёзность: architecture/safety/RF/traceability blocker
- Затрагивает: `DEC-0001`, `DEC-0003`, `FND-0001`, `C-N24-01`–`C-N24-10`, `hardware/tscircuit/{c5-buses,rf,indicators}.tsx`
- Обнаружено и частично исправлено: 2026-08-16

## Несоответствие

Текущие источники называли RF и MCU/bus sheets `FAB-READY`, хотя:

1. `SPI_*`, общий `nRF24_CE`, `HC138_A/B/C` и суммарный `nRF24_IRQ` подключены к `U10`/ESP32-S3, а `DEC-0001` требует физического и программного владения C5;
2. `U11` одновременно декодирует S3 CS для SD/CC1101/LoRa/LCD и трёх nRF24, поэтому перенос одних net labels не создаёт C5-local bus;
3. C5 уже использует единственный GP-SPI как legacy S3↔C5 slave (`FND-0001`); C5-local nRF master transport и pin map отсутствуют;
4. `U20/U21/U22` — одинаковые геометрические 2×4 placeholders с названием «nRF24L01+PA/LNA module», но без exact manufacturer/MPN/revision, BOM, chip identity, PA/LNA truth table, conducted power, receive gain, current transient, antenna land и regulatory evidence;
5. общий `CE` не имел внешнего reset/high-Z default; exact module power нельзя отключить независимо, а отдельный hardware STOP/TX-kill не доказан;
6. `TXDET_NRF1..3` нигде не генерируются RF coupler/detector circuit: текущие Q51–Q53/LED подключены к односторонним floating stubs и не являются hardware TX-live indication;
7. три 150 µF placeholders и общий 2 A rail не заменяют min/nom/max load-step proof точных PA/LNA modules;
8. прежний pin budget считал IR как две линии, но `DEC-0018` теперь резервирует два RX path и один TX path. Старое «C5 fits» более не является доказательством.

## Выполненное безопасное исправление

- `FAB-READY` снято с `rf.tsx` и `c5-buses.tsx`, ограничения отражены прямо в source headers;
- в `rf.tsx` добавлен `Rce_off=100 kΩ` от общего `nRF24_CE` к GND, задающий standby input при reset/high-Z;
- `indicators.tsx` больше не называет односторонние `TXDET_*` nets реализованными analog detector taps;
- parts-engine readable-netlist подтверждает `Rce_off` между `nRF24_CE` и GND и общий CE всех трёх placeholders.

Исправление не выбирает transport/pins/module и не делает legacy artifact производственным.

## Что остаётся открытым

- C5-local SPI/CS/CE/IRQ topology после выбора S3↔C5 transport и полного stage-3 GPIO/resource budget;
- exact одинаковый qualified module/AVL либо документированная эквивалентность разных frontends;
- conservative per-module conducted-power map и запрет превращать raw IC `RF_PWR` в module dBm без измерения;
- hardware STOP/dead-man, power/reset/update/link-loss state machine и фактический TX detector каждого тракта;
- rail/load-step, self-desense, three-radio simultaneous RX/TX, antenna isolation, emissions/spurs и enclosure HIL.

## Критерий закрытия

Находка закрывается только target schematic/netlist/BOM/pin budget и HIL, где все три модуля принадлежат C5, power-on до explicit action остаются RF-off, STOP физически прекращает любую передачу, exact module power/sensitivity доказаны, а TX-live наблюдает RF, не команду firmware.

## Первичные источники

- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)
- [ESP32-C5 datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [ESP32-C5 SPI slave API](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-reference/peripherals/spi_slave.html)

