# DEM-0001 — current hardware-neutral semantic signal demand

- Статус: **Проведено ревью требований; exact-device qualification открыта**
- Дата: 2026-08-17
- Gate: `FLOW-0001/G2F`, шаг 1
- Inputs: reviewed requirements through `REV-0002AS`, `DEC-0041`
- Не входы: legacy owners/pins, former `SYN-3A`, `PIN-0002` allocations

## Назначение

Этот документ считает не GPIO конкретного MCU, а обязательные **семантические
концы сигналов**. Shared bus может физически сократить число проводов, latch
может сжать outputs, а IRQ logic — объединить входы, но только с доказательством
сохранения каждой перечисленной функции, reset state, deadline и source
identity. Владелец ни одного блока здесь не выбран.

## Радио и timing-critical demand

| Группа | Обязательные semantic endpoints | Допустимое sharing/сжатие | Нельзя потерять |
|---|---|---|---|
| 3× full-function nRF24 | общие либо раздельные `SCK/MOSI/MISO`; по `CE/CSN/IRQ` на каждый из трёх | общий SPI; reset-safe output latch; protected IRQ aggregation после proof | независимые mode/channel/rate/address/FIFO, любой одновременный `3R/1T2R/2T1R/3T` mix без peer standby/gaps, source identity, bounded FIFO service |
| CC1101 | `SCK/MOSI/MISO`, `CSn`, `GDO0`, `GDO2` candidate endpoints | общий radio SPI после exact electrical proof | FIFO/event deadlines, выбранные modulation/RX/TX modes, safe deselect/power |
| dual-path consumer IR | robust-demod RX, carrier-learning RX, carrier TX | owner peripheral выбирается candidate | два одновременных RX path, 30–60 kHz measurement path, hardware TX inhibit |
| native 2.4/5 + 802.15.4 | внутренняя radio function exact candidate SoC/module | coexistence внутри одного silicon допускается только по manufacturer contract | обычные 2.4/5 Wi-Fi и reviewed 802.15.4 behavior; 6 GHz отсутствует |
| native 2.4/BLE/ESP-NOW | внутренняя radio function exact candidate SoC/module | owner открыт | reviewed BLE и 2.4/ESP-NOW scope, RF coexistence evidence |
| analog voice module | UART TX/RX, `PTT`, power-down, high/low-power select, squelch/status; отдельные physical PTT и actual-TX evidence | slow non-deadline controls могут использовать safe local logic | local dead-man, STOP dominance, RX default, actual TX не выводится из команды |

Для трёх nRF минимальная абстракция — `3 shared bus + 9 per-device = 12`
semantic logic lines. Это не обещание 12 MCU GPIO: любой вариант compression
сравнивается по стоимости, latency, fault isolation и безопасному reset.

## Storage, display, audio and internal links

| Группа | Baseline endpoints | Варианты, которые сравниваются |
|---|---|---|
| removable microSD | `CLK/CMD/D0` + card/power/status slow path | 1-bit (3 timing pins) против 4-bit (`D1/D2/D3`, итого 6 timing pins) с измеренным throughput |
| display | SPI-write `SCK/MOSI/CS`, `DC`, PWM backlight; reset-safe reset; dirty/tiled updates; critical/menu first visible response `≤100 ms` | read/TE/MISO только если exact panel даёт измеримую пользу; full-frame rate не является demand (`DEC-0043`) |
| touch | shared/isolated I²C; source IRQ только если polling не проходит latency/power | exact controller и glove/noise behavior открыты |
| codec/audio | `BCLK/WS/DOUT/DIN`, shared I²C, safe enable/reset и analog-bypass selects | exact codec/package подтверждается отдельно |
| broadcast receiver | shared I²C/control plus exact receiver IRQ/reset/audio contract | exact Si4732 orderable variant/package и patch behavior открыты |
| inter-domain link | control/event/bulk/liveness/recovery semantics | SDIO, SPI, UART/USB или отсутствие link при иной consolidation; каждый вариант считает fixed pins/controllers |

## External M5 and other expansion

| Surface | Реальный контракт контактов | Следствие |
|---|---|---|
| U214 Cap LoRa-1262 | LoRa `NSS/MISO/MOSI/SCK/BUSY/IRQ/RST`; GPS TX/RX; SCL/SDA; 5V in/out; GND | полный 14-pin Cap-Bus, а не «один SPI» |
| U214 downstream Port A | GND/5V/SDA/SCL | доступен одновременно с U214 в принятой важной конфигурации |
| additional M5 Unit | GND/5V + два configurable signals | base surface должен реализовать A/I²C, C/UART, B/custom GPIO и precise 1-Wire profile через mux/isolation и exact voltage proof |
| iButton adapter | direct bidirectional/open-drain timing endpoint на Unit B/custom | I²C GPIO expander не является доказанным timing path; read/emulate/write имеют разные safety levels |
| high-throughput RF-derived tier | пока нет exact transport/connector/endpoints | строка является blocker для final pin closure, но не поводом резервировать произвольный USB host |

Generic M5 connector доказывает только два сигнала и питание. Каждый реально
поддерживаемый Unit SKU затем проходит собственную connector/power/protocol/
revision проверку.

## UI, safety, power and service endpoints

| Группа | Обязательство |
|---|---|
| ordinary local controls | полная навигация/confirm/back/menu/shortcuts без телефона; допускается local scanned/I²C controller |
| PTT | отдельный direct foreground input, не единственный бит slow expander |
| STOP/re-arm | non-programmable latched kill, deliberate physical re-arm, sense лишь наблюдает и не является kill path |
| TX control/evidence | reset-safe CE/CS/PTT/power defaults, per-domain inhibit/gates и независимое actual-TX evidence |
| sensing/status | battery/current/thermal/light и ordinary indicators могут использовать mux/ADC/slow control после exact latency/safety proof |
| programmable target service | у каждого выбранного chip независимые programming, recovery, reset/boot и diagnostics; USB/pads/header считаются по exact package/module |
| external power | 5 V M5 profiles, `VVOICE≈4 V`, RF/logic/audio domains и current limits считаются вместе с exact modules |

## Не создающие pin burden функции

Integrated keyboard, haptic motor, personal FIDO, generic USB host, 6 GHz,
onboard GNSS, onboard LoRa и onboard HF NFC frontend исключены. BadUSB остаётся
software-only поверх уже выбранного USB-device path.

## Closure rule

Следующая candidate map обязана поместить все строки или показать конкретный
hard fail. Нельзя объявить карту complete, пока:

- `SRC-0002` не подтверждает exact exposed contacts каждого считаемого device;
- controller-instance и strap/recovery ledgers не сходятся;
- high-throughput tier либо получает exact профиль, либо остаётся явно
  изолированным reopen gate вне base pin map;
- memory/traffic/power/service burdens посчитаны вместе с pin map.
