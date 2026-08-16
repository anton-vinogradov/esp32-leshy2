# ADR-0001 — реестр взаимозависимых решений этапа 3

- Статус: **Проведено ревью; обязательный вход единого architecture package**
- Дата: 2026-08-16
- Входы: `DEC-0023`, `DEC-0026`, `DM-0001`, `BUD-0001`, `PIN-0001`, `SC-0001`, `LAY-*`, current findings
- Назначение: не допустить локального решения, которое делает другой участок архитектуры невозможным

## Классы состояния

- `fixed` — уже принято и не переоткрывается внутри этапа 3;
- `package-choice` — обязано получить ровно одно значение в общем package;
- `package-contract` — topology/boundary фиксируется сейчас, exact MPN либо численное доказательство остаётся следующей стадии;
- `later-proof` — не меняет architecture при соблюдении уже зарезервированной границы;
- `out-of-base` — не расходует base-board ресурсы и не блокирует пакет.

## Реестр

| ID | Узел | Состояние до synthesis | Зависит от | Обязательный выход package | Если не сходится |
|---|---|---|---|---|---|
| `AR-01` | S3 module/memory | `package-choice` | owner nRF, link pins, buffers | exact S3 module, flash/PSRAM class, pin consequences, memory kill gate | пересчитать owner/link, не удалять функции |
| `AR-02` | C5 module/revision | `package-choice` | link, native USB, integrated RF load | exact N8R8 module/revision and unavailable pins | reject incompatible lot/revision |
| `AR-03` | third compute/RF MCU | `package-choice` | nRF real-time proof, BOM, update/recovery | present or absent; no hidden mezzanine controller | third domain only after two-MCU hard fail |
| `AR-04` | owner 3×nRF24 | `package-choice` | `AR-01..03`, SPI/link/IRQ/STOP | one owner of all three full-function radios | no split and no one-radio+switch fallback |
| `AR-05` | S3↔C5 transport | `package-choice` | memory pins, C5 GP-SPI, USB recovery | exact controller roles, pins, framing/goodput/latency gates | whole package reopens on failure |
| `AR-06` | local nRF service | `package-contract` | owner, shared-bus load, IRQ source | CS/CE/IRQ topology, reset states and numeric service bounds | hard fail `HF-02/08/10` |
| `AR-07` | S3 main peripheral bus | `package-contract` | display, SD, CC1101, U214, possible nRF | controller, decoded selects, arbitration and bounded chunks | reallocate controller/owner, never hide loss |
| `AR-08` | C5 IR resources | `fixed` + `package-contract` | C5 pin/link map | two RX RMT + one TX RMT exact pins, off-state and STOP boundary | hard fail `HF-03` |
| `AR-09` | native BLE/Wi-Fi/802.15.4 owners | `fixed` | RF coexistence and memory | S3 BLE/Wi-Fi, C5 Wi-Fi/802.15.4, C5 BLE default-off | hard fail `HF-04` |
| `AR-10` | nine ordinary UI keys | `package-choice` | expander lines, audio controls, recovery | point-to-point expander or diode 3×3 matrix; STOP separate | keep `U14` if equivalence cannot be proven |
| `AR-11` | `U12/U13/U14` map | `package-choice` | UI, C5 recovery, audio, U214 RESET, cost | every expander line exactly once with boot defaults | hard fail `HF-08`; no line called free twice |
| `AR-12` | touch IRQ/reset | `package-contract` | `AR-10/11`, GPIO48 aggregation | electrically valid interrupt aggregation and recoverable reset/power path | retain dedicated control capacity |
| `AR-13` | ES8311/I²S/audio bypass | `fixed` + `package-contract` | S3 pins, selectors, codec enable | exact four-wire I²S, default-to-analog selectors and safe control map | hard fail `HF-05` |
| `AR-14` | VOX | `package-choice` | ADC/audio selector/control budget, voice backend | remain `defer-release` with no base hardware, or add complete mic evidence path | cannot promise host VOX without capture |
| `AR-15` | voice module/power | `fixed` + `package-contract` | `DEC-0016/0025`, STOP | SA518 target, separate SA868S stuffing, VVOICE and PTT/H-L defaults | unknown profile is RX-only/TX-disabled |
| `AR-16` | `PORT.C-GNSS` | `package-contract` | UART pins, 5 V power/protection | physical 5 V UART profile and one-active-backend rule | GNSS unavailable, never implicit 3.3 V compatibility |
| `AR-17` | `EXT-RF14/U214` | `package-contract` | SPI2, GNSS UART, reset, 5 V, mechanics | 14-pin bus signals, default-off power, RESET, descriptor and antenna gate | unknown module remains unpowered/TX-disabled |
| `AR-18` | `PORT.A-NFC` | `package-choice` | 5 V port power, I²C levels, generic Units | fixed dedicated 5 V NFC port or safely selected per-port profile | current 3.3 V Grove artifact is rejected |
| `AR-19` | generic I²C expansion | `package-contract` | `AR-18`, address/rail conflicts | separately labelled 3.3 V-safe descriptor/profile; no blanket M5 claim | unknown accessory remains off |
| `AR-20` | hardware STOP fan-out | `fixed` + `package-contract` | every MCU/TX/accessory rail | latch, physical re-arm, reset and independent inhibit/power class per domain | hard fail `HF-06` |
| `AR-21` | actual-TX evidence | `package-choice` | antenna feeds, IR optics, external accessories, indicators | per-domain evidence class, physical indication/readout and unknown/fault behavior | hard fail `HF-07`; Controlled TX inhibited |
| `AR-22` | rail tree | `fixed` + `package-contract` | power envelope, STOP, accessories | 3.3 V/5 V/VVOICE/battery class, default states and load-control boundaries | hard fail `HF-13` |
| `AR-23` | accessory power/hot-plug | `package-contract` | `AR-16..19/20/22` | current-limited default-off ports, direction, attach/remove policy | power-off attach only until HIL |
| `AR-24` | RF coexistence | `package-choice` | every RF owner/antenna, power and scheduler | pairwise allowed/degraded/forbidden matrix and lease authority | unmeasured simultaneous TX forbidden |
| `AR-25` | antennas/placement | `package-contract` | nRF modules, enclosure, coexistence | one physical path per simultaneous radio, detector/tap reservations, stage-5/9 gates | no antenna combining as silent saving |
| `AR-26` | exact RF/IR modules | `later-proof` | reserved interfaces/power/area | stage-4 MPN/AVL/calibration within package ceilings | failed part returns to BOM qualification, not architecture improvisation |
| `AR-27` | recovery/debug | `package-choice` | link pins, matrix line release, USB topology | native USB + physical BOOT/RESET for S3/C5; any third MCU independent too | hard fail `HF-11` |
| `AR-28` | signed update/rollback | `fixed` + `package-contract` | compute domains, transport, flash partitions | two slots, independent target verification, rollback and open owner-key lifecycle | no image activation; no vendor-only recovery |
| `AR-29` | irreversible lockdown | `fixed` | `DEC-0013` | absent from baseline; only future owner opt-in after separate review | never enabled by production default |
| `AR-30` | firmware ownership/API | `package-contract` | `AR-04/05/09/24/28` | typed service boundaries, TX leases, reset/link-loss states, versioned IPC | mismatched protocol is safe-off/receive-only |
| `AR-31` | base-cost topology | `package-choice` | third MCU, U14, onboard vs external parts, test burden | structural additions/removals and quote gates without fictitious currency score | cheaper non-equivalent variant rejected |
| `AR-32` | onboard GNSS/LoRa | `fixed` | `DEC-0006/0008` | absent; only connectors/protection/profile remain on base PCB | no silent reintroduction into base BOM |
| `AR-33` | optional BLE sniffer/Mesh | `out-of-base` | `DEC-0023` defer-release boundary | no internal pins/BOM reservation; future qualified accessory/software adapter | does not block core architecture |
| `AR-34` | conditional Wi-Fi EAPOL/PMKID | `out-of-base` for hardware | C5 public capture proof and privacy storage | uses accepted C5/link/storage envelopes; UI remains hidden until proof | no private patch or extra radio assumed |

## Проверяемое покрытие demand model

| Demand rows | Владеющие architecture rows |
|---|---|
| `DM-CORE-01`, `DM-CORE-02` | `AR-01`, `AR-02`, `AR-27..30` |
| `DM-LINK-01` | `AR-05`, `AR-30` |
| `DM-UI-01`, `DM-STO-01` | `AR-07`, `AR-31` |
| `DM-UI-02` | `AR-10..12` |
| `DM-SAFE-01`, `DM-SAFE-02` | `AR-20`, `AR-21` |
| `DM-USB-01` | `AR-27..29` |
| `DM-AUD-01`, `DM-AUD-02` | `AR-13`, `AR-14` |
| `DM-RX-01` | `AR-07`, `AR-11`, `AR-13` |
| `DM-VHF-01` | `AR-13..15`, `AR-20..22` |
| `DM-SUB-01` | `AR-07`, `AR-20..25` |
| `DM-N24-01` | `AR-04`, `AR-06`, `AR-20..26` |
| `DM-IR-01` | `AR-08`, `AR-20..22`, `AR-25/26` |
| `DM-RF-01` | `AR-21`, `AR-24`, `AR-25`, `AR-30` |
| `DM-IND-01` | `AR-21`, `AR-22` |
| `DM-PWR-01` | `AR-20`, `AR-22`, `AR-23` |
| `DM-EXP-01` | `AR-06`, `AR-10..12`, `AR-20` |
| `DM-EXT-01` | `AR-16`, `AR-23`, `AR-32` |
| `DM-EXT-02` | `AR-07`, `AR-17`, `AR-23..25`, `AR-32` |
| `DM-EXT-03`, `DM-EXT-04` | `AR-18`, `AR-19`, `AR-23` |
| `DM-EXT-05` | `AR-19`, `AR-23`, `AR-33` |

| Hard-fail rows | Владеющие architecture rows |
|---|---|
| `HF-01` | все `AR-01..34`; frozen scope не меняется внутри layout |
| `HF-02` | `AR-04`, `AR-06`, `AR-25/26` |
| `HF-03` | `AR-08`, `AR-20/21`, `AR-25/26` |
| `HF-04` | `AR-09`, `AR-24`, `AR-30` |
| `HF-05` | `AR-13..15` |
| `HF-06`, `HF-07` | `AR-20`, `AR-21` |
| `HF-08` | `AR-01..13`, `AR-16..19`, `AR-27` |
| `HF-09`, `HF-10` | `AR-01..07`, `AR-30` |
| `HF-11` | `AR-27..29` |
| `HF-12` | `AR-16..19`, `AR-23`, `AR-32` |
| `HF-13` | `AR-20..26` |
| `HF-14` | `AR-26`, `AR-28..31`, plus evidence gate каждой строки |

## Граф критического пути

1. `AR-01..05` выбирают compute/owner/transport skeleton.
2. Skeleton ограничивает `AR-06..13` — controllers, exact direct pins, expanders, UI и audio.
3. Эта карта обязана одновременно вместить `AR-16..19` external profiles и `AR-27` recovery.
4. Только после этого замыкаются `AR-20..25` safety/power/actual-TX/coexistence/physical boundaries.
5. `AR-28..31` проверяют update, firmware failure semantics и стоимость всей получившейся системы.
6. `AR-26`, stage-4 MPN/AVL и stage-5/9 measurements доказывают уже зарезервированные границы, но не меняют их молча.

## Найденные пересечения

| Ошибочно локальный вопрос | Реальное пересечение |
|---|---|
| nRF owner | S3 PSRAM pins, C5 GP-SPI, IPC, USB recovery, cost and RF scheduler |
| matrix/`U14` | audio controls, C5 BOOT recovery, U214 RESET, touch IRQ/reset and production test |
| actual-TX LED | antenna layout, detector/readback BOM, Controlled-Zone arm policy and STOP HIL |
| NFC port voltage | 5 V rail, generic 3.3 V Unit safety, current limiting and connector labelling |
| VOX | mic ADC path, selector line, audio concurrency, false-trigger safety and voice-module variant |
| external LoRa | SPI arbitration, GNSS UART, 5 V power, STOP, antenna presence and enclosure mechanics |

## Gate к synthesis

- [x] каждый `DM-*` hardware/accessory domain сопоставлен с package row;
- [x] все hard fails `HF-01..14` имеют хотя бы один владеющий row;
- [x] open stage-3 findings `FND-0001/0006/0007/0013/0015/0017/0019/0022..0024/0029/0032` перенесены как choice, contract либо later-proof;
- [x] deferred software/accessory proposals отделены от base-board resource graph;
- [x] ни owner, transport, matrix, recovery или cost choice не помечен принятым отдельно.

Реестр получает статус **«Проведено ревью»**. Следующий артефакт обязан заполнить каждую строку `package-choice/package-contract` одной согласованной целевой конфигурацией.
