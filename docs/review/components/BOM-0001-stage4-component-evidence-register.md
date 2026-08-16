# BOM-0001 — stage-4 component evidence register

- Статус: **Проведено ревью реестра; component qualification открыта**
- Дата: 2026-08-16
- Пререквизиты: `PKG-0001/SYN-3A`, `DEC-0028`, `REV-0003U`
- Review: [`REV-0004A`](../reviews/REV-0004A-stage4-entry-register.md)

## Что означает статус строки

| Code | Смысл |
|---|---|
| `A` | exact architecture-locked target; stage 4 проверяет полный evidence, а не заново выбирает owner/function |
| `C` | conditional named candidate/fallback; выбор или сохранение conditional state ещё требует qualification |
| `F` | обязательная circuit function, exact part/topology ещё не выбрана |
| `X` | внешний qualified accessory profile; не base-BOM frontend, но board-side interface обязателен |

Evidence states: `E0` — строка только идентифицирована; `E1` — есть проверенные primary facts; `E2` — доказаны electrical/reset/pin/thermal fit и schematic contract; `E3` — current lifecycle/AVL/price/assembly evidence; `E4` — prototype/HIL/fault/substitution evidence; `Q` — строка получила отдельное **«Проведено ревью»**. `BOM-0001` не присваивает `Q` ни одной детали.

## 1. Compute, clock and recovery

| ID | Type | Exact/candidate function | Current evidence | Следующий обязательный proof |
|---|---:|---|---:|---|
| `C-001` | A | `ESP32-S3-WROOM-1U-N16R2` | E1 | module revision/land pattern, flash/PSRAM identity, boot straps, antenna connector, current/thermal, AVL and recovery fixture |
| `C-002` | A | `ESP32-C5-WROOM-1U-N8R8`, production silicon ≥v1.2; v1.0 engineering-only | E1; decision closed | revision-committed lot, SDIO/remaining-errata proof, straps, antenna path, current/thermal, AVL and native-USB fixture |
| `C-003` | A | `RP2354A A4`, exact `SC1511-A4` / packaging-equivalent `SC1511(13)-A4`, QFN60, stacked flash 2 MiB | E1; E3 partial | crystal/clock network, decoupling/thermal pad, USB/SWD/RUN fixture, quotes/traceability and assembly yield |
| `C-004` | A | TI `TCA9535PWR` | E1 | address/pulls/INT, preload-before-direction reset sequence, drive/current limits, exact footprint and AVL |
| `C-005` | C | RP reference `ABM8-272-T3` 12 MHz crystal and manufacturer-recommended passives | E1; E3 partial | exact passives, placement and startup/temperature/EMI proof versus USB and packet timestamp requirements; alternate only by equivalence HIL |
| `C-006` | F | 3×`USB4105-GF-A`, 3×`FTSH-105-01-L-DV-K-TR` DBG10, 6×`KMR221GULCLFS`, 3×`TPD2EUSB30ADRTR`; exact service passives | E1 partial; `DEC-0031/SVC-0001` | CAD/AVL/mechanics, CC/VBUS/ESD/series network, erased-image recovery and multi-host HIL |
| `C-007` | F | SDIO/SPI/alert inter-domain pulls, damping, test points and isolation provisions | E1 contract | 3.3 V/common-core compatibility, boot-safe defaults, signal integrity, fixture access and no accidental peer powering |

## 2. Always-on safety and power

| ID | Type | Exact/candidate function | Current evidence | Следующий обязательный proof |
|---|---:|---|---:|---|
| `P-001` | F | 2S cell/pack connector, protection, fuse, reverse/transient/input current path ≥12 W/15 W | E0 | pack/protection operating envelope, fault energy, connector/trace/thermal and service disconnect |
| `P-002` | F | common 3.3 V buck ≥2.5 A continuous/3.0 A transient | E0 | efficiency/transient/thermal/EMI at accepted scenarios; no RF/audio collapse |
| `P-003` | F | core, packet-RF and audio branch switches/filters/current observation/discharge | E0 | independent fault containment, inrush and STOP/brownout ordering |
| `P-004` | F | dedicated `VVOICE=4.0 V` ≥1.25/1.5 A | E0 | SA518 startup/TX transient, ripple, local bulk/discharge, STOP dominance |
| `P-005` | F | protected `5V_EXT` 0.75/1.0 A | E0 | conversion topology, current limit, backfeed, connector fault and per-profile isolation |
| `P-006` | F | `AON_SAFE` regulator/supervisor | E0 | valid STOP latch/indicator/gates through application-rail collapse and brownout |
| `P-007` | F | latched STOP, recessed RE-ARM, TX_KILL fan-out and reset/enable drivers | E0 | asynchronous truth table, stuck/open/short fault analysis, independent actual-TX indication and fault injection |
| `P-008` | F | battery measurement/charge/fuel-gauge/thermal policy | E0 | exact supported charging boundary and truthful SoC/fault reporting; no unaccepted charging claim |

## 3. UI, display, storage and service I/O

| ID | Type | Exact/candidate function | Current evidence | Следующий обязательный proof |
|---|---:|---|---:|---|
| `U-001` | F | 480×320 display and controller/module | E0 | interface mode, 3.3 V logic, backlight, reset, bandwidth ≥4.5 MB/s, lifecycle/optics/mechanics |
| `U-002` | F | touch controller/panel | E0 | I²C address/IRQ/reset, voltage, latency, noise and full non-touch fallback |
| `U-003` | F | rotary encoder/push, BACK/HOME/OPTIONS | E0 | detent/bounce/ESD/lifetime and TCA9535 interrupt/read-rate loss test |
| `U-004` | F | direct PTT, STOP and recessed RE-ARM mechanics | E0 | independent routing, human factors, debounce where allowed and abuse/fault behavior |
| `U-005` | F | microSD socket, detect/protection/pulls | E0 | 4-bit SDMMC signal integrity, hot removal, endurance/profile and exclusive ownership |
| `U-006` | F | S3 product USB connector/power/CC/ESD | E0 | device-only role, CDC/HID/MSC profiles, backfeed and recovery coexistence |
| `U-007` | F | non-safety reset/select/mute/enable support parts around TCA9535 | E0 | external safe pulls, glitch-free startup and sequencer independence |
| `U-008` | F | supervisor-managed power/wake control and user actuator | E0 | always-on current, short/long action semantics, hard-off/recovery behavior and independence from I²C-only state |

## 4. Audio and receive paths

| ID | Type | Exact/candidate function | Current evidence | Следующий обязательный proof |
|---|---:|---|---:|---|
| `A-001` | A | ES8311 mono codec | E1 | exact orderable suffix/package, clocks/I²S/I²C, analog levels, reset, noise, AVL and 48 kHz full-duplex HIL |
| `A-002` | F | RX-source mux and two hardware-default-to-analog selectors | E0 | exact topology/parts, off-state leakage, pop/click, reset/failure bypass and audio quality |
| `A-003` | F | microphone bias/input and speaker/headphone amplifier/output | E0 | levels, gain/noise, load/thermal, mute default, EMC and hearing-safe UI bounds |
| `R-001` | A | Si4732 receive IC/module function | E1 | exact orderable implementation, RF frontend/bands, reference clock, audio/control levels, lifecycle and SSB-patch compatibility |
| `R-002` | F | Si4732 antenna matching/filter/switch path | E0 | sensitivity, overload, ESD, coexistence and enclosure antenna contract |
| `I-001` | A | TSOP38238 robust 38 kHz IR RX | E1 | supply/filter/layout/optical aperture and ambient-light HIL |
| `I-002` | A | TSMP95000 30–60 kHz learning RX | E1 | carrier measurement accuracy, supply/filter/layout/aperture and HIL |
| `I-003` | C | TSAL6200 940 nm IR emitter | E1 | exact pulse current/driver/thermal/optics, eye safety and STOP/TX-state evidence |

## 5. Packet RF and analog voice

| ID | Type | Exact/candidate function | Current evidence | Следующий обязательный proof |
|---|---:|---|---:|---|
| `RF-001..003` | F | three independent nRF24L01+-compatible full-function RF paths/modules | E0 | genuine silicon/module identity, per-path PA/LNA/antenna/supply, direct CSN/CE/IRQ, 200 kB/s each, ≤3 dB sensitivity delta, lifecycle/AVL |
| `RF-004` | F | CC1101 exact IC/module and frontend | E0 | band variants/matching/filter/antenna, SPI/GDO timing, RSSI calibration, legal profiles and AVL |
| `RF-005` | F | four packet-RF branch gates/current detectors/actual-TX evidence | E0 | reset-safe off, per-source identity, STOP timing, detector thresholds and false-state analysis |
| `RF-006` | F | S3/C5 antenna connectors/feeds and all enclosure radiators | E0 | approved antenna sets, keep-outs, cable loss, coexistence and certification route |
| `V-001` | C | SA518 VHF/UHF 0.5/1 W voice module | E1 | exact revision/protocol/pinout, 4.0 V operation, conducted output/spurs, audio/PTT timing, lifecycle/AVL/rights |
| `V-002` | C | SA868S UHF-only stuffing/supply fallback | E1 | separate manifest and qualification; never automatic or labelled dual-band |
| `V-003` | F | voice RF filtering/matching/antenna/PTT/TX evidence | E0 | regional bands, conducted/shielded HIL, STOP/dead-man and isolation from receive/audio paths |

## 6. External profiles and connectors

| ID | Type | Exact/candidate function | Current evidence | Следующий обязательный proof |
|---|---:|---|---:|---|
| `X-001` | X | M5Stack Unit GPS v1.1 | E1 | exact revision/current/connector, NMEA, optional CASIC status and RF self-desense |
| `X-002` | X | M5Stack U214 LoRa+GNSS, 868–923 MHz | E1 | exact revision/interface/power, 868/915 regional profiles, reset, GNSS mux and conducted HIL |
| `X-003` | X | M5Stack Unit NFC U216 | E1 | exact revision/NRND lifecycle, 5 V current/interface, supported modes/rights and removal fault |
| `X-004` | F | dual-SPDT GNSS UART mux and power exclusivity | E0 | exact parts, voltage/bandwidth/leakage/default selection and never-two-powered proof |
| `X-005` | F | board-side M5 connectors, profile ID, load switch, current limit, isolation and ESD | E0 | pinout/keying/backfeed/hot-plug/unknown-accessory safe-off |
| `X-006` | C | alternate LoRa Cap/carrier profile | E0 | common 868/915 only; exact carrier is not required for base BOM and needs separate profile proof |

## Legacy implementation mismatches carried into stage 4

| Mismatch | Target correction already accepted | Stage-4 action |
|---|---|---|
| current source has no RP2354 domain | `DEC-0028` adds RP2354A A4 and direct packet/voice controls | qualify `C-003/C-005/C-006`, then regenerate schematic rather than patch legacy pin ownership |
| generic three-nRF placeholders use legacy S3 ownership and common CE | RP directly owns three CSN/CE/IRQ paths | `RF-001..005`; old source remains noncanonical |
| STOP is an I²C input in legacy artifact | independent latched `AON_SAFE` STOP/TX_KILL | `P-006/P-007`; no schematic readiness until fault proof |
| old 3×3 matrix/extra expander remains in source ideas | accepted UI uses touch+encoder+six named controls and one TCA9535 | `U-002..004/U-007`; do not carry old matrix/U14 into target BOM |
| legacy NFC port is 3.3 V | accepted U216 profile requires protected 5 V | `P-005/X-003/X-005` |
| legacy voice rail is 5 V | accepted SA518 target uses dedicated 4.0 V | `P-004/V-001`; SA868S stays separate conditional manifest |
| onboard/legacy GNSS or LoRa assumptions | base board has neither frontend | only board-side `X-004/X-005`; external `X-001/X-002` profiles |

These are known mismatches, not new owner questions. Their correction point is exact component/schematic regeneration after the relevant row reaches `Q`.

## Dependency order and completion rule

1. `BOM-0002`: `C-*` — the exact compute/recovery platform must close first.
2. `BOM-0003`: `P-*` — every later part depends on valid rails, STOP and fault boundaries.
3. `BOM-0004`: `U-*` — slow controls, storage and service I/O consume fixed rails and pins.
4. `BOM-0005`: `A/R/I-*` — audio and receive chains require the accepted power/UI/control baseline.
5. `BOM-0006`: `RF/V-*` — TX-capable hardware is qualified only after STOP/power/control prerequisites.
6. `BOM-0007`: `X-*` — external profiles close after board-side power/isolation is exact.
7. `BOM-0008`: every production row reaches `E3`; every safety/performance-critical row reaches `E4/Q`; consolidated BOM, DNP/variant and alternate manifests contain no silent substitution.

The entire stage receives **«Проведено ревью»** only when every base-BOM row is `Q`, each conditional/external row has an explicit disposition, all target functions map to exact parts/topologies, and no legacy-only part silently survives.
