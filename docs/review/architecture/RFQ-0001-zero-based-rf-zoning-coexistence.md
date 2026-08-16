# RFQ-0001 — zero-based RF zoning and coexistence gates

- Статус: **Проведено ревью архитектурной RF-модели; layout/conducted/OTA HIL открыты**
- Дата: 2026-08-16
- Этап: 3, шаг 5d
- Входы: reviewed `CAP/CON/RES/SRC/SYN/PIN/BUD/PWR`, accepted three-level safety/legal policy
- Scope: одинаковые RF paths, antenna geometry и qualification rules для `SYN-2A`, `SYN-2B`, `SYN-3A`
- Не является: готовой PCB placement, matching network, antenna MPN, RF certification или разрешением TX

## Что фиксируется и что остаётся открытым

Архитектура обязана сохранить следующие независимые RF paths независимо от controller ownership:

| Path | Baseline role | Sharing boundary |
|---|---|---|
| `RF-S3-24` | S3 native 2.4 GHz Wi-Fi/BLE | одна native chain, Wi-Fi/BLE time-share |
| `RF-C5-DUAL` | C5 native 2.4/5 GHz Wi-Fi + 802.15.4 | один принятый dual-band module/ANT1 path; native modes time-share |
| `RF-N24-0..2` | три full-function nRF24 + три sector/calibration identities | три физических transceiver/antenna paths; один radio+switch запрещён |
| `RF-CC` | CC1101 sub-GHz | own matching/filter/antenna profile |
| `RF-RX` | Si4732 receive | own receive/frontend/antenna profile |
| `RF-VOICE` | SA518 VHF/UHF voice/modem | own TX-capable dual-band antenna profile |
| `RF-U214` | attached 868/915-class LoRa/FSK + GNSS | removable M5 profile with its own antennas/cable geometry |
| `RF-NFC` | attached 13.56 MHz U216-class near field | removable local-field profile, not a far-field antenna claim |

Exact antennas/connectors remain stage 4/5 choices. RF paths may share an enclosure but may not be collapsed through an RF switch/diplexer unless the replacement preserves required simultaneous receive, calibration, loss, fail-safe isolation and every supported band. In particular, merging `RF-CC`, `RF-RX` or `RF-VOICE` merely because some bands overlap is not zero-loss.

## Source-backed layout invariants

- [Espressif S3 layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html) requires antenna clearance/edge placement and end-product verification; high-frequency digital and crystal coupling can reduce sensitivity.
- [Espressif C5 guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/pcb-layout-design.html) requires a continuous adjacent ground plane, short 50 Ω RF routes, no nearby high-speed signals, dense ground vias and antenna/connector clearance.
- [C5 RF schematic guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html) treats 2.4 and 5 GHz matching separately and allows one qualified dual-band antenna/duplexer path; this does not create simultaneous C5 native radios.
- [Nordic nRF24L01+ specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf), [TI CC1101 datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf) and exact module reference layouts remain mandatory at component/layout stages.

All candidates therefore use at least four layers with an uninterrupted RF reference plane. No high-speed display, SDMMC/SDIO, USB, SPI, crystal or switching-power current loop may cross an antenna keep-out or run under a controlled-impedance RF path. A via, connector, ESD part, shield seam or test structure belongs to the tuned path and cannot be inserted as an uncosted generic footprint.

## Common physical zoning

The enclosure/PCB is partitioned by electromagnetic function before assigning exact coordinates:

| Zone | Contents | Placement rule |
|---|---|---|
| `Z-N24` | three nRF paths and their local decoupling/matching | three repeatable sector positions/orientations; maximum practical mutual separation; identical reference geometry where exact modules match |
| `Z-NATIVE-S3` | S3 module and 2.4 antenna feed/cable | antenna/radiator at a qualified enclosure edge, separated from nRF sectors and high-speed display/storage |
| `Z-NATIVE-C5` | C5 module and one dual-band antenna feed/cable | different edge/volume from S3/nRF where mechanics allow; 5 GHz cable/connector loss qualified |
| `Z-SUB` | CC1101 and its matching/filter | away from voice PA and switching inductors; no unqualified shared antenna |
| `Z-VOICE` | SA518, VVOICE bulk, harmonic filter and antenna feed | physical/high-current isolation from Si4732, CC1101, GNSS and audio input |
| `Z-RX-AUDIO` | Si4732 frontend, ES8311 analog and low-level audio | quiet-ground/analog routing; no voice/packet clock or converter loop through the zone |
| `Z-EXT` | U214/GPS/NFC connectors, power switch/isolation and cable exit | board edge with explicit cable/antenna placement; removable device cannot lie over native antenna keep-out |
| `Z-DIG/PWR` | S3 application/storage/display interconnect, optional RP, regulators | central/contained; clocked links kept short and ground-referenced; spread-spectrum/clock gating only after validation |

`Z-N24` antenna positions, enclosure material, battery/display state and calibration fixture are identical across candidates. Controller placement may change; antenna quality may not.

## Digital-owner consequences

| Candidate | Required route | RF consequence |
|---|---|---|
| `SYN-2A` | S3↔3×nRF/CC shared SPI and latch/event routes; S3 also serves display/SD/audio/native RF | long or star packet-bus routes may couple into multiple RF zones; owner is central but most digitally busy |
| `SYN-2B` | C5↔3×nRF/CC shared SPI and latch/event routes while C5 owns dual-band native RF/IR | greatest native-2.4/packet concentration and worst risk that one local load/clock desenses another |
| `SYN-3A` | RP placed adjacent to packet-radio control cluster; direct CE/CSN/IRQ and short SPI0; S3/RP IPC exits toward central digital zone | shortest deadline/control wiring and best isolation from Espressif stacks; adds RP clock/IPC emission source that must be gated/shielded |

This is an architecture risk comparison, not an RF pass. `SYN-3A` gains no assumed dB until the same board/enclosure fixture measures it.

## Coexistence classes instantiated

| Pair/session | Initial class | Qualification/fallback |
|---|---|---|
| nRF0 RX ↔ nRF1 RX ↔ nRF2 RX | `P` | mandatory simultaneous PRX/RPD; isolated and three-active calibration must both pass |
| S3 Wi-Fi ↔ S3 BLE | `T` | native coexistence scheduler; actual dwell/gaps visible |
| C5 2.4 ↔ C5 5 ↔ C5 802.15.4 | `T` | one native chain; selected mode and dwell visible |
| S3/C5 2.4 activity ↔ nRF RX | `Q` | exact pair HIL; otherwise scheduler uses `T/D`, never false full coverage |
| C5 5 GHz activity ↔ nRF/CC/Si4732/GNSS RX | `Q` | harmonics/clock/common-rail coupling still measured; band separation alone is not proof |
| CC RX ↔ voice TX; Si4732 RX ↔ voice TX | `Q` | conducted/OTA desense and false-decode test; fallback mutes/marks stale or time-shares |
| U214 GNSS ↔ U214 LoRa TX | `Q+A+D` | same attached/cable profile; fix may become stale/unknown during TX |
| external NFC field ↔ other receive/session | `Q+A` | power/bus/field coupling measured; removal or wrong profile disables field |
| any TX ↔ any other TX | `X` by default | only one exact contained pair may become `Q` after channel/power/duty/antenna/enclosure/load proof |

Being an authorized white-hat target satisfies only the ownership/authorization part of Controlled Zone. It does not waive spectrum, emission, exposure or no-leakage requirements. Dangerous RF tests remain conducted or inside the qualified shielded environment and still show the mandatory entry banner every time.

## Mandatory measurement paths

Every TX-capable RF path must support one production/development measurement method without relying on radiated guesswork:

- accessible conducted point, qualified temporary coax fixture or calibrated coupler before the final radiator;
- per-path power/current enable observation plus actual-TX evidence appropriate to the frontend;
- exact antenna/load identity and safe behavior for open/missing/wrong antenna where detectable;
- π/CLC matching placeholders only where the exact reference design and tuning plan require them;
- shield-can/ground-via boundary and local bulk footprints costed with the path, not added after layout failure;
- repeatable isolated-source/per-channel sensitivity and packet-error fixture for each nRF and native receiver.

Production self-test may detect gross missing/stuck hardware but must not label VSWR, radiated power, sensitivity or compliance without the necessary directional/coupled measurement hardware.

## Qualification thresholds

| Gate | Pass definition |
|---|---|
| `RFQ-01` isolated path | exact module/antenna/filter meets its manufacturer/project sensitivity, output, mask/harmonic and current profile over battery/temperature/enclosure |
| `RFQ-02` mandatory 3×nRF PRX | each radio remains within 3 dB of its isolated sensitivity reference, preserves `BUD-0002` latency/loss guarantee and reports source-specific RPD/calibration state |
| `RFQ-03` nRF sector comparison | reference-source rotations/channel/rate/power produce repeatable calibrated hit-rate ordering; no dBm/bearing/VSWR label is introduced |
| `RFQ-04` `Q` receive pair | both participants still meet their accepted exact-profile minimum; any degradation/false detect/stale interval is measured and visible |
| `RFQ-05` qualified TX pair | conducted/shielded fixture meets both spectral profiles, STOP/dead-man and no-leakage threshold; qualification names exact pair/channel/power/duty/layout/enclosure |
| `RFQ-06` digital aggression | display full updates, SD/SDIO/USB, RP IPC and every converter state do not violate isolated minimum or create false radio/GNSS/NFC evidence |
| `RFQ-07` antenna/user state | installed battery, display, enclosure, hand positions and every supported accessory/cable state are included; unsupported placement is shown or blocked |
| `RFQ-08` STOP/fault | reset, rail fault, IPC loss and STOP create no RF pulse outside the bounded measured kill interval; release does not resume TX |

The 3 dB requirement exists only for the mandatory equal-footing three-nRF receive set. Other receivers use their exact accepted minimum because applying one arbitrary dB delta across 13.56 MHz through 5 GHz would be technically false.

## Architecture comparison result

| Property | `SYN-2A` | `SYN-2B` | `SYN-3A` |
|---|---|---|---|
| same RF paths/antennas | yes | yes | yes |
| mandatory 3×nRF topology | credible; HIL open | credible; HIL open | credible; HIL open |
| packet digital-route risk | medium/high | highest | lowest |
| native-stack self-desense coupling | high on S3 | highest on C5 | lowest by placement |
| added oscillator/clock source | none beyond common | none beyond common | RP crystal/IPC; explicit emission gate |
| antenna/mechanical complexity | identical | identical | identical |
| paper RF winner | none | none | none; strongest layout prior only |

All three remain physically plausible, but `SYN-2B` has the hardest RF/scheduling concentration and `SYN-3A` the cleanest controllable partition. This comparison will become a score only after cost and implementation burden are placed beside it in the atomic package.

RF paths, zoning, equal-fixture rule, coexistence classes and eight qualification gates receive **«Проведено ревью»**. No unmeasured pair is promoted from `Q/X`, and no legacy antenna placement was inherited.
