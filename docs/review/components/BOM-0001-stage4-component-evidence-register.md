# BOM-0001 — stage-4 component evidence register

- Статус: **Candidate/reference register; component stage blocked by `DEC-0032`**
- Дата: 2026-08-16
- Пререквизиты: `PKG-0001/SYN-3A`, `DEC-0028`, `REV-0003U`
- Review: [`REV-0004A`](../reviews/REV-0004A-stage4-entry-register.md)

> Exact rows below preserve the superseded `SYN-3A` evidence snapshot. They are
> no longer architecture-locked targets and cannot be consumed by CAD,
> schematic or procurement until the corrected product/architecture gates pass.

## Что означает статус строки

| Code | Смысл |
|---|---|
| `A` | historical architecture-locked target from the superseded package; now candidate/reference only |
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
| `P-002` | F | exact `TPS564252DRLR + MWSA0503S-3R3MT` common 3.3 V buck ≥2.5 A continuous/3.0 A transient; exact 45.3/10-kOhm feedback, energy/Cff and EN/fault passives | E2; E3 partial | effective-capacitance, efficiency/transient/thermal/EMI at accepted scenarios; no RF/audio collapse |
| `P-003` | F | five exact `TPS22919DCKR` packet-RF/storage/audio branch switches with QOD | E1 | independent fault containment, inrush, no-back-power and measured discharge ordering |
| `P-004` | F | exact `TPS564252DRLR + MWSA0503S-3R3MT + TPS25974LRPWR + MMBT3904-7-F` dedicated protected `VVOICE=4.0 V` ≥1.25/1.5 A with exact feedback/energy and post-buck ILM/OVLO/dVdt/ITIMER/PGTH/output parts | E2; E3 partial | SA518 startup/TX transient, protected-PG truth, trip energy, ripple, hot loss and STOP dominance HIL |
| `P-005` | F | exact `TPS564252DRLR + MWSA0503S-4R7MT + MMBT3904-7-F + TPS259470LRPWR` protected `5V_EXT`: exact 220/30-kOhm feedback, energy/Cff, EN/PG/base passives, 1.25 A continuous, controlled startup and bounded 2.0-A post-start transient; eight exact eFuse passives | E2; E3 partial | effective-capacitance/inrush/hot-loss/OVLO/fault/discharge HIL, high-current geometry, connector fault and per-profile isolation |
| `P-006` | F | exact `TPS629203DRLR + WPN201612H2R2MT + TPS25961DRVR` protected `AON_SAFE`, direct SYS enable, fixed 3.3 V, exact ILIM/OVLO/bypass, protected-side 47-kOhm PG and 10-kOhm POR into `TPS3808G33DBVR`, plus 100-kOhm main fail-low | E2; E3 partial | high-side-short trip energy, capacitor hold-up and AON-PG/SENSE/CT/POR/main transition through brownout |
| `P-009` | F | exact `TPS564252DRLR #MAIN + TPS25974LRPWR #MAIN` raw/protected 3.3-V boundary with exact 1.65-kOhm ILM, 191/100-kOhm 0.1% OVLO, dVdt/ITIMER, PGTH and output capacitor | E2; E3 partial | 3-A load-step, protected-PG, high-side-short containment, hot loss and source-transition HIL |
| `P-007` | F | latched STOP, recessed RE-ARM, TX_KILL fan-out and reset/enable drivers | E0 | asynchronous truth table, stuck/open/short fault analysis, independent actual-TX indication and fault injection |
| `P-008` | F | exact `MAX17320G20+T + MSPM0C1104SDGS20R` manager; 2×`XTAR 18650 4000mAh` first-target cells; corrected `TPUL2G223BQBR` dual-channel cascade with `GRM31C5C1H224JE02L`, `RC0402FR-07620KL`, `C1608X7R1C105K080AC`, `DMN2056U-7` and 2×`CRM2512-FX-20R0ELF`; 10-Ohm load, 25-50-ms pulse, `>=350-ms` hardware lockout and exact PA25/PA26 frontends | E2; E3 partial | exact assembly certification/specimen profile, ADC/droop thresholds, timer/load lot and hot-copper HIL, insertion/removal/source-handover and thermal/fault HIL; no unaccepted recovery or full-load claim |

## 3. UI, display, storage and service I/O

| ID | Type | Exact/candidate function | Current evidence | Следующий обязательный proof |
|---|---:|---|---:|---|
| `U-001` | historical F | former 480×320 display candidate | E0 | not target; new G3 compares display/control archetypes before any exact component proof |
| `U-002` | historical F | former touch controller/panel candidate | E0 | not mandatory; compare touch and non-touch complete candidates at G3/G5 |
| `U-003` | historical F | former rotary encoder/push and named controls | E0 | not mandatory; exact field-control surface follows G3/G5 usability and whole-product comparison |
| `U-004` | F | direct PTT, STOP and recessed RE-ARM mechanics | E0 | independent routing, human factors, debounce where allowed and abuse/fault behavior |
| `U-005` | F | exact isolated microSD endpoint: `DM3AT-SF-PEJM5`, switched rail, Ioff buffers, mandatory pulls, full contact/detect ESD | E2 paper reviewed `DEC-0085/STO-0001`; physical/media HIL open | socket placement/access, shared-SPI throughput/contention, hot removal, endurance/profile, ESD/short/brownout and recovery UX |
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
| old 3×3 matrix/extra expander and later touch+encoder+six-control map remain in source ideas | `DEC-0038` excludes the keyboard; no other exact ordinary UI surface is accepted; autonomous core control plus dedicated safety/voice semantics are fixed | return touch/encoder/D-pad/display alternatives to G3/G5; do not carry either old map into target BOM |
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
