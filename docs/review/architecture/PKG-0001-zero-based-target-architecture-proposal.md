# PKG-0001 — zero-based target architecture proposal

- Статус: **⚠️ Предложение — готово к единому решению владельца; не принято**
- Дата: 2026-08-16
- Этап: 3, атомарный package по `DEC-0026/0027`
- Рекомендация: принять `SYN-3A` с `RP2354A A4` как единую target architecture
- Нормативные входы: reviewed `CAP/CON/RES/SRC/SYN/PIN/BUD/PWR/RFQ/CST`
- Запрет: нельзя принять отдельный owner, pin, transport или UI fragment без всего package

## Почему на решение выходит `SYN-3A`

Все три candidates покрывают 21 capability atom и проходят paper pin/memory/traffic/power gates. Различие появляется в инженерном риске и стоимости.

| Критерий | `SYN-2A` | `SYN-2B` | `SYN-3A` |
|---|---|---|---|
| recurring candidate delta, midpoint | $0.7063 | $0.5767 | $1.8109 |
| specific work packages | 4 | 5 | 8 |
| useful safe MCU GPIO reserve | 0 | 0 | 7 C5 GPIO |
| radio control | latch + aggregate IRQ | latch + aggregate IRQ | direct CE/CSN/IRQ/GDO |
| real-time owner contention | S3 native/UI/audio/SD | worst: single-core C5 native/IR/radio | isolated RP domain |
| RF route/concentration prior | medium/high | worst | best; new oscillator still qualified |
| programmable targets | 2 | 2 | 3 |

`SYN-2B` saves only about $0.13 over `2A`, but combines the highest C5 timing risk, the worst native/packet RF concentration and zero spare GPIO. This is not a convincing zero-loss saving.

`SYN-2A` is the strongest low-cost fallback and has the lowest implementation burden. Its price advantage over `3A` is real—about $1.10 midpoint per unit—and it avoids a third firmware target. It also places native Wi-Fi/BLE, display, audio, SD, voice and four packet-radio services on S3, uses compressed safety-sensitive radio control and leaves neither Espressif domain with usable pin reserve.

`SYN-3A` is recommended because this product has multiple TX-capable paths and a Controlled Zone: local deterministic nRF/CC/voice deadlines, direct source identity, direct safe controls and fault isolation are worth more than the approximately $0.95…1.25 recurring premium over `2A`. Seven free C5 GPIO also prevent the first exact-component discrepancy from forcing a complete board redesign. The premium is accepted only together with the third update/recovery/HIL burden and a sourcing kill-gate; it is not described as cost saving.

## Target compute domains and exact variants

| Domain | Exact target | Owned responsibilities |
|---|---|---|
| application | `ESP32-S3-WROOM-1U-N16R2` | product UI/policy, native 2.4 GHz Wi-Fi/BLE, display/touch/controls, microSD/files/USB, ES8311/Si4732/audio DSP, U214/selected GNSS/U216 manager, C5/RP orchestration |
| native dual-band/IR | `ESP32-C5-WROOM-1U-N8R8`, silicon with working SDIO, minimum rev ≥1.0 | 2.4/5 GHz Wi-Fi, IEEE 802.15.4, two-path IR capture, IR TX, native radio scheduling, local safety lease, SDIO slave |
| deterministic packet/voice | `RP2354A A4`, QFN60, 2 MiB stacked flash | 3×nRF24, CC1101, voice UART/PTT/PD/H-L/squelch/TX evidence, physical PTT, local dead-man, packet timestamps/FIFOs, direct STOP observation |

No nRF placement is inherited from legacy documentation. The owner follows from the complete resource/failure/cost comparison above.

## Inter-domain topology

### S3 ↔ C5

- S3 SDMMC slot 1 is host; C5 is 1-bit SDIO slave on fixed `CLK/CMD/D0/D1`.
- GPIO13/14 remain C5 native USB; silicon revision is verified in production.
- Typed `CH-CTL/EVT/BULK/LIVE/REC` queues carry native-radio/IR commands, events, bounded capture, lease/liveness and update/recovery data.
- Qualified framed payload floor is 1.5 MB/s, admitted occupancy ≤70%, control RTT ≤2 ms.
- Link loss expires TX leases; C5 never treats stale S3 state as permission.

### S3 ↔ RP2354A

- S3 GP-SPI3 master ↔ RP SPI1 slave at initial 20 MHz plus dedicated `RP_ALERT_N`.
- Same typed channels, source/time/sequence/drop metadata and 1.5 MB/s measured payload floor.
- RP owns radio/voice deadlines locally; SPI is a command/event/bulk boundary, never remote raw GPIO.
- Malformed/stalled peer expires local leases and cannot hold PTT/nRF/CC TX.

Cross-domain clocks are calibrated to common monotonic S3 time with uncertainty attached to every event. Wall-clock/GNSS jumps do not reorder safety evidence.

## Exact pin/controller closure

[`PIN-0002`](PIN-0002-zero-based-exact-pin-maps.md) `SYN-3A` rows are normative in full. Summary:

| Domain | Fixed controllers/pins | Ledger |
|---|---|---|
| S3 | SDMMC0 microSD GPIO4…9; SDMMC1 C5 GPIO10…13; I²S GPIO15…18; USB19/20; SYS-I²C1/2; display+U214 GP-SPI2 GPIO35…43; selected GNSS UART44/47; RP GP-SPI3 GPIO0/14/21/48 + alert3 | 34 used + straps45/46 reserved; no generic S3 spare |
| C5 | IR RX GPIO0/1, IR TX6; 1-bit SDIO7…10; USB13/14; fixed SDIO straps3/25 and recovery26/28 | 9 used + 5 strap/recovery reserved + 7 free GPIO2/4/5/11/12/23/24 |
| RP2354A | SPI0 radio data0/2/3; direct nRF controls/events1/4…11; CC12…14; STOP15; voice16…23; SPI1 IPC24…27; alert/health28/29 | 30/30 GPIO; dedicated USB/SWD/RUN preserved |

S3 GPIO0 remains pulled for normal boot; RP is held reset/high-Z during S3 strap sampling. C5 fixed edge straps are `GPIO25=0`, `GPIO3=1`; C5 v0.0/v0.1 is rejected. No irreversible JTAG/secure-boot eFuse is required by baseline.

## Local UI and physical controls

The target uses touch plus a small, complete physical set derived from the local-UI requirement rather than the legacy 3×3 matrix:

- rotary encoder `A/B/push` for navigate/select;
- `BACK` with long-hold software panic-stop;
- `HOME` and `OPTIONS`;
- touch interrupt and on-screen keyboard; every text/action remains reachable with encoder/buttons if touch fails;
- direct physical PTT on RP GPIO22, active only in an armed foreground voice session;
- independent latched hardware STOP;
- separate recessed physical `RE-ARM`, effective only after STOP release and safe-state checks;
- supervisor-managed power/wake control, not an ordinary I²C-only button.

One onboard TI [`TCA9535PWR`](https://www.ti.com/product/TCA9535) 16-bit I²C controller is selected for non-safety UI/slow control. Seven inputs are encoder A/B/push, BACK, HOME, OPTIONS and touch IRQ; the eighth observes accessory/power fault. Eight reset-safe outputs serve display/touch reset, two audio selectors, amp mute/enable, GNSS mux select, U214 reset and an external-profile power/isolation-sequencer request. All outputs have external safe pulls because the expander powers up as inputs; firmware preloads the inactive output latch before changing direction. The downstream sequencer independently enforces current limit, no-backfeed and safe-off, so this request is not the only isolation barrier. Stage 4 may qualify an exact second source only as a pin/reset/electrical/AVL-equivalent BOM substitution.

STOP, PTT, re-arm, TX gates and critical actual-TX/STOP indication never depend solely on this I²C controller. The old nine-button matrix and extra `U14` are not part of target; their user results remain covered with fewer parts and no ghosting state.

## Peripheral ownership

| Block | Target owner/path |
|---|---|
| display | S3 GP-SPI2, write-only baseline, PWM backlight, ≤1 KiB preemptible chunks |
| touch/local slow control | isolated S3 system I²C/TCA9535; touch does not replace physical cancel |
| microSD | S3 SDMMC 4-bit, exclusive writer/snapshot rules |
| ES8311 + Si4732 | S3 I²S/I²C and analog fabric; mono full-duplex, hardware-default bypass/mute |
| 3×nRF24 | RP SPI0, direct three CSN/CE/IRQ; common admitted timing, no latch/aggregate |
| CC1101 | RP SPI0 + direct CS/GDO0/GDO2 |
| analog voice | RP UART0/control/PTT/dead-man/evidence; audio samples/routing remain S3/ES8311 |
| U214 | S3 GP-SPI2 + slow control + selected GNSS UART; first 868/915-class external LoRa profile |
| Unit GPS | same selected GNSS UART through dual-SPDT mux; exactly one GNSS backend powered/active |
| U216 NFC/generic I²C | isolated/current-limited S3 external I²C profile; unknown/removal = RF/power off |

U214 and another LoRa carrier are runtime mutually exclusive. The base board carries no GNSS, LoRa or NFC frontend.

## Memory, flash and throughput contract

| Domain/path | Accepted architecture budget |
|---|---|
| S3 PSRAM | ≥1792 KiB usable floor = 896 KiB resident + 512 KiB worst overlay + 384 KiB reserve |
| S3 internal DMA | ≥192 KiB pool before foreground I/O; 160 KiB planned ceiling + 32 KiB reserve |
| C5 PSRAM | ≥7168 KiB usable; ≤2048 KiB resident, ≤2048 KiB queues, ≤1024 KiB overlay, ≥2048 KiB margin |
| RP SRAM | ≤416 KiB used, ≥104 KiB guard |
| S3/C5 flash | independent two-image owner-signed rollback; S3 16 MiB, C5 8 MiB |
| RP flash | 128 KiB verifier/recovery + 2×768 KiB images +64 KiB metadata +64 KiB HIL +256 KiB reserve |
| 3×nRF guarantee | simultaneous full-function PRX, 200 kB/s payload per radio, aggregate 600 kB/s; 57.6% of 10 Mbit/s bus with service factor |
| mixed nRF/CC | admitted nRF450 + CC60 kB/s; 49.2% bus |
| display | 480×320 RGB565 interface envelope, 10 full-frame-equivalents/s; ≥4.5 MB/s measured path |
| audio | 48 kHz mono 16-bit full-duplex =192 kB/s, zero unexplained DMA loss |
| storage | ≤1.5 MB/s admitted records, ≥4 MB/s qualified SD, ≥512 KiB queue across 250 ms stall |

The theoretical simultaneous maximum of 3×nRF plus CC would consume 79.5% of the shared bus before software margin and is not advertised as lossless. Native modes remain available; admission, gaps and overflow counters are explicit.

## Power and STOP topology

- accepted `BAT_2S=6.0…8.4 V`, ≥3 A continuous/4 A pulse pack/protection and ≥12 W/15 W power path;
- one 3.3 V buck, ≥2.5 A continuous/3.0 A transient, with independently switched/filtered/current-observed core, packet-RF and audio branches;
- each nRF path reserves 150 mA/200 mA transient until exact module qualification; CC branch 50/75 mA;
- `5V_EXT` 0.75 A continuous/1.0 A limited, backfeed protected, profile-switched;
- accepted `VVOICE=4.0 V`, 1.25 A continuous/1.5 A transient, local bulk/discharge;
- `AON_SAFE` powers STOP latch, supervisor, critical indicator and gates independently of application firmware.

STOP asynchronously asserts `TX_KILL`, drives RP `RUN`, S3/C5 reset/enable policy and nRF/CC/U214/NFC/voice/IR TX gates to safe state. It does not wait for UI/IPC/storage. Release does not re-arm; recessed physical re-arm or power cycle starts a new TX-off boot. Commanded TX, current draw, actual-TX evidence, STOP latch and fault remain distinct indications.

## RF architecture

All independent S3/C5/3×nRF/CC/Si4732/voice/U214/NFC paths and the common sector geometry from [`RFQ-0001`](RFQ-0001-zero-based-rf-zoning-coexistence.md) are normative.

- RP is placed in the central packet/voice control zone to keep direct radio SPI/CE/CSN/IRQ/PTT routes short.
- S3 and C5 antenna feeds occupy separately qualified enclosure edges/volumes; nRF sector radiators retain repeatable orientation and maximum practical mutual separation.
- RF, voice, quiet receive/audio, removable accessory and digital/power zones retain continuous reference ground and no high-speed crossings through antenna/RF keep-outs.
- three-nRF simultaneous PRX is `P` and each path must stay within 3 dB of isolated sensitivity while meeting traffic gates;
- all other cross-domain receive pairs begin `Q`; fallback is visible `T/D`;
- all TX pairs begin `X` and can be enabled only for one exact conducted/shielded profile after emission, STOP/dead-man and no-leakage proof.

Authorized white-hat status never replaces spectrum/containment proof. Controlled Zone entry shows the mandatory banner every time.

## Open owner-controlled update and recovery

| Target | Normal update | Independent recovery | Trust boundary |
|---|---|---|---|
| S3 | Wi-Fi/removable media/USB package, streamed signature verification, A/B rollback | native USB + physical GPIO0/EN | owner keys/open manifest; irreversible secure boot optional only |
| C5 | package transferred over SDIO, verified/installed by C5, A/B rollback | native USB13/14 + physical boot/EN | minimum silicon/identity reported; peer cannot bypass verification |
| RP2354A | package transferred over S3-RP SPI, verified by first-stage loader, A/B rollback | dedicated USB/SWD/RUN access | owner-signed normal images; ROM enforcement/OTP lockdown remains optional |

Updates are sequential, power-qualified and globally TX-off. Failed first boot rolls back. Developer images remain possible through intentional physical recovery; the device does not become closed.

## USB and storage profiles

- S3 USB is the product/service interface. Baseline profiles are service `CDC` plus explicitly armed HID where allowed, and storage export via read-only snapshot or exclusive MSC ownership.
- Autorun and import-triggered actions do not exist. HID Controlled-Zone action is per-run armed and STOP/disconnect bounded.
- Firmware and host never write the same filesystem simultaneously.
- C5 and RP USB are recovery/service interfaces, not extra normal user-drive claims.

## Three functional levels

The hardware architecture does not bypass the accepted UI/security split:

1. `Main` — ordinary owned-device, receive, navigation, files and safe remote use;
2. `Laboratory` — analysis and controlled experiments under the installation non-aggression pledge;
3. nested `Controlled Zone` — dangerous actions only with exact authorized target and/or conducted/shielded environment as the tool requires; fresh warning banner on every entry, then per-action preview/arm/lease/STOP.

Signed firmware does not turn captured/imported data into permission. Every replay/TX revalidates level, target, region, power, duration and evidence.

## Cost, sourcing and implementation consequences

- candidate-specific recurring delta: `$1.7359…1.8859` at the dated qty-500 snapshot;
- midpoint premium: about `$1.10` over recommended low-cost fallback `2A`;
- eight candidate-specific firmware/update/manufacturing/HIL work packages versus four for `2A`;
- no additional DC/DC rail; RP fits the common 3.3 V envelope;
- RP2350 official production horizon through at least January 2045, but observed immediate RP2354A stock below 500;
- production requires two independent source/allocation quotes, A4 stepping/lot traceability and QFN60 assembly/yield quote before schematic freeze.

This is the cost of the recommended safety/margin architecture. Cost reductions continue only on common exact components and qualified second sources; reducing radio count, direct safety, update/recovery, antenna paths or HIL is not accepted saving.

## Hard kill-gates and the only fallback rule

| Gate | Failure consequence |
|---|---|
| `KG-01` RP2354A A4 allocation/traceability and second source quote unavailable by schematic freeze | package reopens; `2A` is the first whole-package fallback candidate, not an automatic substitution |
| `KG-02` 600 kB/s three-nRF/latency test fails on RP shared bus | reopen split-bus/owner synthesis and every affected pin/update/cost contract |
| `KG-03` S3/C5/RP memory or DMA floors fail | optimize bounded allocation first; if contract still fails, reopen complete package, never silently change S3 to Octal PSRAM |
| `KG-04` SDIO or RP IPC throughput/liveness/lease proof fails | transport and pin/recovery package reopens |
| `KG-05` STOP kill, brownout, actual-TX evidence or rail fault isolation fails | architecture not buildable until hardware correction passes |
| `KG-06` mandatory three-nRF RFQ/sensitivity or enclosure zoning fails | mechanical/RF layout reopens; no one-radio/switch downgrade |
| `KG-07` owner-signed A/B/recovery fails on any target | release blocked; no unsigned automatic fallback |
| `KG-08` legal/regional/containment profile absent | affected TX function disabled; receive/legal product functions remain |

Fallback always means a complete new package/re-review. It is not a second shipping target hidden in firmware.

## Acceptance checklist

- [x] every capability/scenario has an owner/path/failure state;
- [x] exact S3/C5/RP variants and owners are named;
- [x] exact buses/controllers/pin map/straps/recovery are normative;
- [x] UI/control topology is complete without a phone and separates STOP/PTT/re-arm;
- [x] memory/traffic/storage/audio/display thresholds are numeric;
- [x] power domains and allowed scenario peaks are numeric;
- [x] RF paths/zones/coexistence and dangerous-test containment are explicit;
- [x] three open owner-controlled signed update/recovery lifecycles are defined;
- [x] dated recurring cost, NRE and sourcing shortfall are visible;
- [x] every unresolved physical measurement is a named kill-gate, not a guessed pass;
- [x] `2A/2B` are not independently accepted fragments.

`PKG-0001` is internally complete and ready for one owner decision. Until accepted, stage 3 and target READMEs remain unchanged.
