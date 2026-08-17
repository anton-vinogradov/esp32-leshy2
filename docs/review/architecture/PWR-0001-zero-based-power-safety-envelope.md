# PWR-0001 — zero-based power and safety envelope

- Статус: **Проведено ревью load envelope; supervised 2S confirmed by DEC-0065**
- Дата: 2026-08-16
- Этап: 3, шаг 5c
- Входы: reviewed `CAP/CON/RES/SRC/SYN/PIN/BUD`, accepted `DEC-0003/0024/0025`
- Scope: одинаковая power-policy и rail capacity для `SYN-2A`, `SYN-2B`, `SYN-3A`
- Не является: выбором charger/regulator/load-switch MPN, battery SKU или доказательством thermal/EMC

## Принцип расчёта

Power tree рассчитывается по разрешённым сценариям `CON-0001`, а не по арифметической сумме максимумов всех передатчиков. Незаквалифицированные simultaneous TX запрещены и не могут использоваться ни для завышения BOM, ни для уменьшения мощности реально принятого режима.

Три независимых понятия не смешиваются:

- `rail capacity` — ток, который не приводит к droop/reset/thermal fault в разрешённом сценарии;
- `RF output` — только conducted measurement exact radio/profile, а не ток или register bit;
- `TX safety` — аппаратный inhibit/cut и lease/dead-man, не software state питания.

## Проверочные первичные значения

| Блок | Manufacturer value | Architecture allowance |
|---|---|---|
| ESP32-S3 | [Espressif](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf): Wi-Fi peak до 340 mA при 3.3 V | 450 mA branch envelope с PSRAM/I/O/transient margin |
| ESP32-C5 | [Espressif](https://documentation.espressif.com/esp32-c5_datasheet_en.pdf): worst listed 5 GHz TX peak 381 mA, 5 GHz RX до 135 mA | 500 mA branch envelope |
| nRF24 IC | [Nordic specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf): about 11.3 mA TX at 0 dBm and 13.5 mA RX at 2 Mbit/s | exact module still stage 4; board envelope retains 150 mA per path |
| nRF PA/LNA comparison | [Ebyte E01-ML01DP5](https://www.ebyte.com/product/7.html): max 140 mA TX, 22 mA RX | shows why generic `PA/LNA` cannot be budgeted as bare IC |
| CC1101 | [TI datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf): about 34 mA at maximum listed output profile | 50 mA branch envelope |
| SA518 | [NiceRF SA518 rev 1.1](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf): max 900 mA at 4.0 V/1 W and 76 mA RX | accepted separate 1.25 A continuous / 1.5 A transient rail |
| U214 | [M5 U214](https://docs.m5stack.com/en/cap/Cap_LoRa-1262): 5 V/163.4 mA LoRa operation and 33.1 mA GNSS power-on figure | combined profile remains below a 0.75 A accessory rail envelope |
| U216 | [M5 Unit NFC](https://docs.m5stack.com/en/unit/Unit_NFC): about 67.65 mA continuous reading at 5 V | same current-limited accessory rail, separate profile |
| RP2354A | [Raspberry Pi RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf): workload-dependent, no guaranteed board maximum applicable here | 100 mA 3.3 V architecture allowance; exact build measured |

Allowances are rail sizing ceilings, not component acceptance and not permission to transmit at maximum output. A lower-power exact nRF module may reduce local bulk or converter loading only after equal RX/TX/calibration/AVL/safety proof under `REQ-N24-0001`.

## Power-domain topology

| Domain | Loads | Normal state | STOP/fault behavior |
|---|---|---|---|
| `BAT_2S_SUPERVISED` | two qualified replaceable series cells, protection, gauge, charger/power-path | always supervised; both cells required | protection/ship-mode/brownout force downstream TX-off |
| `3V3_CORE` | selected compute domains (current candidate S3, C5, RP), supervisor, UI, storage, control logic | on while device operates | STOP does not depend on software; current hard-STOP contract resets every compute domain and does not wait to log |
| `3V3_PKT` | 3×nRF, CC1101 and their TX-capable frontend | current-limited switched branch from common 3.3 V converter | reset default off or TX-inhibited; STOP asynchronously forces CE/PTX/TX path safe and may cut branch |
| `3V3_AUDIO` | ES8311, Si4732/control, analog mux/amp/mic frontend | pop-safe sequenced branch | mute/bypass state defined before MCU; RF fault cannot command TX |
| `5V_EXT` | exactly one qualified U214/Unit GPS/U216/generic profile as policy permits | off until identity/profile/power checks | current limit, reverse/backfeed block and removal detect; U214/NFC RF disabled by STOP |
| `VVOICE` | SA518 preferred or explicit fallback stuffing | default off; 4.0 V for SA518 | independent discharge/enable + PTT gate under STOP; no MCU-only kill |
| `AON_SAFE` | STOP latch, critical indicator, supervisor and required gates | live whenever battery connected outside ship mode | cannot be disabled by ordinary firmware or accessory fault |

`3V3_CORE`, `3V3_PKT` and `3V3_AUDIO` may share one efficient 3.3 V buck to avoid needless converter cost, but packet/audio branches require independent load switching/filtering/current observation. A short or reverse feed on a removable/radio branch may not defeat `AON_SAFE`; exact fault isolation is a schematic/HIL gate.

## Rail capacity envelopes

| Rail/path | Continuous design floor | Transient/current limit | Reason |
|---|---:|---:|---|
| combined 3.3 V converter | 2.5 A | ≥3.0 A non-destructive transient | covers allowed core/RX/TX/UI/storage scenarios plus 100 mA RP allowance |
| each nRF local branch | 150 mA | ≥200 mA short transient with local bulk | retains comparison space through 140 mA PA/LNA module; exact AVL later |
| CC1101 local branch | 50 mA | ≥75 mA | startup/TX margin and measurable isolation |
| `5V_EXT` | 0.75 A | 1.0 A current-limited | U214+GNSS and U216 values fit with cable/inrush/later-qualified profile margin |
| `VVOICE=4.0 V` | 1.25 A | 1.5 A | already accepted by `DEC-0025`, above SA518 900 mA max listed TX current |
| battery/power-path | ≥12 W | ≥15 W bounded transient | 2S minimum-current arithmetic is calculated in `PWR-0006/DEC-0065` |
| cell/slot protection | ≥3 A path target before margins | ≥4 A pulse target before exact qualification | must prevent low-cell droop or contact loss from masquerading as radio/firmware fault |

These floors are not promises that every rail may be loaded simultaneously.
Converter selection must satisfy its own input-voltage, efficiency,
loop/transient, SOA and thermal curves at the selected topology's minimum
battery voltage and enclosure temperature.

## Scenario ledger

| Scenario | Mandatory loads | Explicitly not assumed | Pass condition |
|---|---|---|---|
| boot/recovery/update | AON, every selected compute domain, UI, storage/USB as needed | every TX rail on | TX-off before application boot; reset/inrush does not false-arm |
| `CS-04` three-sector hunt | S3/C5, 3×nRF RX, UI, record, optional RP | three nRF PA TX peaks | no rail droop, clock/RPD corruption or uncounted FIFO loss |
| `CS-05` wardrive | selected native/RX producers, display, GNSS if attached, SD | all selectable transmitters at maximum | admission reports power/thermal profile and visible gaps |
| `CS-07` voice TX | core/UI/audio, `VVOICE` up to 1.25 A, PTT/dead-man/STOP | unrelated RF TX or 5 V accessory maximum | ≥10 s keyed test and duty/thermal profile without core reset; release/STOP bounded |
| `CS-09` U214 TX/GNSS | core/UI/storage, `5V_EXT`, U214 LoRa and GNSS state | voice or unrelated TX without pair qualification | cable/rail/drop/self-desense measured; removal/brownout disarms |
| `CS-11` contained pair | exact two qualified TX paths, core/UI/audit/STOP | a generic permission for any pair | one named fixture/channel/power/duty enclosure profile only |
| `CS-12` fault storm | AON, critical indication, bounded core record | successful log flush before kill | STOP and gates win over storage/accessory/IPC/MCU faults |

The system admission controller uses measured battery voltage under load, temperature, rail headroom and exact stuffing/profile. Low battery or hot converter removes high-power choices before undefined behavior; it never retries at maximum.

## Sequencing and brownout contract

1. `AON_SAFE` establishes TX kill and holds `3V3_PKT/5V_EXT/VVOICE` off before any MCU reset is released.
2. Core rails rise; S3/C5/RP report identity, boot reason and signed-image health while all TX remains disabled.
3. Radio/accessory branches enumerate one at a time under current observation. Unknown identity, unexpected inrush or missing discharge state leaves the branch off.
4. Firmware may request RX; TX requires a fresh higher-level arm plus local lease. Rail-on never means TX-armed.
5. STOP, brownout, watchdog, peer-link loss, update, accessory removal or supervisor fault first removes hardware TX permission, then performs best-effort logging/shutdown.
6. Release/recovery does not re-arm. The next boot repeats current and safe-state checks.

Each switched rail has voltage/current test points or an equivalent accessible measurement path. `TX commanded` and actual RF/power evidence remain distinct; current alone is not proof of legal RF output.

## Candidate comparison

| Property | `SYN-2A` | `SYN-2B` | `SYN-3A` |
|---|---|---|---|
| common rail sizing | pass | pass | pass, includes 100 mA RP allowance |
| extra active power | latch/IRQ/slow-control only | latch/IRQ/mux only | highest by one MCU; inside common 2.5 A floor |
| packet-RF branch control | S3 local + hardware STOP | C5 local + hardware STOP | RP direct + hardware STOP/RUN |
| fault isolation | two programmable domains | two domains; C5 native and packet faults coupled | best functional isolation; third reset/update domain |
| low-power potential | best paper BOM, measured firmware-dependent | similar | worst unless RP clock/sleep policy is proven |
| converter count | no candidate-specific converter | none | none; RP uses common 3.3 V rail |

No candidate is rejected by peak-power arithmetic. `SYN-3A` costs active/idle energy but does **not** require another DC/DC rail; `SYN-2A/2B` do not receive an assumed battery-life advantage until equal workload measurements exist.

## HIL gates

| Test | Required evidence |
|---|---|
| `HIL-PWR-01` | rail startup/inrush at every selected battery min/nom/max point, cold/hot, every stuffing profile |
| `HIL-PWR-02` | allowed-scenario load steps, droop, reset, converter temperature and efficiency |
| `HIL-PWR-03` | STOP/brownout/watchdog/link-loss kill timing on nRF, CC, U214/NFC and voice paths |
| `HIL-PWR-04` | three-nRF RX plus display/SD/native-radio stress without unexplained loss |
| `HIL-PWR-05` | SA518 0.5/1 W conducted power, 1.25 A rail margin, duty and enclosure thermal soak |
| `HIL-PWR-06` | 5 V wrong-profile, short, inrush, backfeed, hot-remove and U214/NFC RF inhibit |
| `HIL-PWR-07` | battery/protection/charger/power-path behavior at low cell, USB attach/remove and ship mode |
| `HIL-PWR-08` | comparative Wh/session and sleep current for the three candidate firmware loads |

The topology, scenario sizing and capacity floors receive **«Проведено ревью»**. Exact power components remain stage-4/6 work; measured failures reopen the affected candidate instead of deleting a capability or raising TX concurrency.
