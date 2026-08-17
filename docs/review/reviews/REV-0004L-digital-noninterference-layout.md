# REV-0004L — digital non-interference layout

- Статус: **Проведено ревью бумажной цифровой компоновки**
- Дата: 2026-08-17
- Decision: [`DEC-0044`](../decisions/DEC-0044-delegated-noninterference-layout.md)
- Artifact: [`NIF-0001`](../architecture/NIF-0001-digital-noninterference-layout.md)
- Machine source: [`G2F-3I`](../../../hardware/architecture/candidates/G2F-3I.json)

## Проверки

| Проверка | Результат |
|---|---|
| exact S3/C5 module and RP2354B QFN80 contacts exist | pass |
| every programmable exposed GPIO is used/reserved/free exactly once | pass: S3 `29/3/4`, C5 `13/6/2`, RP `46/0/2` |
| every TCA6424 allocatable contact classified | pass: `23/1/0` |
| duplicate JSON keys fail before semantic validation | pass |
| every strap allocation has explicit reset proof | pass |
| every programmable peer link reciprocates the same net | pass |
| each domain has independent programming/recovery/diagnostics | pass on contacts: S3 USB, C5 UART0+EN/BOOT/strap, RP USB+SWD+RUN+BOOTSEL |
| RP2354B PIO data pins obey the real shared base window | pass: PIO0 and PIO1 select `GPIO16…GPIO47`; all PIO data are `GPIO30…GPIO46` |
| fixed-function mux contacts match exact-device groups | pass: S3 USB, C5 4-bit SDIO, RP SPI1/UART0/UART1/I²C0 contracts |
| RP PIO state-machine capacity | pass: `5/12`, seven reserve |
| RP DMA worst-case persistent capacity | pass: `13/16`, three reserve |
| S3 directional GDMA capacity | pass: TX `3/5`, RX `3/5`; two reserve in each direction |
| 3×nRF24, CC1101 and U214 share a data bus | no; five physical buses/state machines |
| C5 IPC shares controller with microSD | no; C5 exclusively uses S3 SD/MMC host |
| RP IPC shares controller with display/storage | no; dedicated SPI3/SPI1 |
| remaining scheduled resources declare arbiter/deadline/proof gate | pass: display+SD and internal slow I²C only |
| generator tests | pass: 19 tests, including GPIO-window, fixed-mux and capacity-overbooking regressions |

## Найдено и исправлено в ходе перебора

| Несоответствие | Исправление |
|---|---|
| RP2354A forced four compatibility radios onto one 10 Mbit/s bus | RP2354B/QFN80 and four independent PIO0 buses |
| first B-package map put C5 and microSD on one S3 host | microSD moved to SPI2; C5 gets exclusive 4-bit SDIO |
| proposed RP UART gave only 1.6 MB/s raw against ≥1.5 MB/s framed gate | rejected; RP returns to dedicated 20 MHz SPI |
| proposed C5 UART ignored exact 5 Mbit/s device limit | rejected using official ESP-IDF SoC capability |
| first RP2354B pin map crossed the physical PIO GPIO-base window | all five PIO data groups moved into `GPIO16…GPIO47`; CS/CE/IRQ remain direct GPIO; machine regression added |
| 16-port slow plane did not cover 19…27 demand | accepted 24-port envelope; 23 endpoints routed, one reserve |
| old validator could not detect duplicate JSON keys or service alternatives | parser/validator and regression tests extended |

## Review boundary

Статус относится к **бумажной цифровой компоновке и её machine checks**, а не
к complete target architecture. Physical RF coexistence, electrical signal
integrity, exact peripheral MPNs, power, mechanics, cost and HIL remain open.
Следующий шаг — RF self-desense/coexistence proof; неизбежную взаимную
деградацию нельзя закрыть этим ревью.
