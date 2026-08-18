# COX-0001 — consolidated I6 qualification matrix

- Статус: **Проведено ревью paper qualification scope; physical HIL open**
- Decision: [`DEC-0097`](../decisions/DEC-0097-one-group-i6-qualification-and-fixtures.md)
- Corrections: [`FND-0103`](../findings/FND-0103-cross-group-hil-could-reopen-forbidden-concurrency.md), [`FND-0104`](../findings/FND-0104-monolithic-receiver-audio-quiet-contract.md)
- Machine source: `hardware/architecture/candidates/G2F-3I.json`

## Non-negotiable runtime boundary

Exactly one top-level signal group is active. Cross-group simultaneous runtime
is prohibited and cannot be reopened by a successful HIL run. Contained
cross-group RF/optical injection is Laboratory characterization and fault
evidence only. Allowed concurrency is limited to declared members of one
manifest: all three `SG-N24` radios and every required PTX/PRX mix, visible
native S3/C5 TDM and exact U214 LoRa/GNSS support members.

Hard STOP/RE-ARM, UI, power/fault supervision and bounded required IPC remain
available system planes. GNSS, audio capture/decode/playback, recording and
service diagnostics are support planes only when the versioned active-group
manifest declares them.

## Group-to-quiet matrix

| Active group | Active signal members | Permitted support | Foreign boundaries that must be quiet |
|---|---|---|---|
| `SG-N24` | nRF0+nRF1+nRF2 in `3PRX`, `1PTX+2PRX`, `2PTX+1PRX`, `3PTX` | recording/audio only if declared | CC, U214/external, voice rail+interfaces, Si4732, IR, S3 RF and C5 RF; codec quiet unless declared |
| `SG-S3-24` | S3 Wi-Fi/BLE/ESP-NOW native TDM | declared recording/audio | nRF, CC, U214/external, voice rail+interfaces, Si4732, IR and C5 RF |
| `SG-C5-NATIVE` | C5 Wi-Fi 2.4/5 + IEEE 802.15.4 native TDM | declared recording/audio | nRF, CC, U214/external, voice rail+interfaces, Si4732, IR and S3 RF |
| `SG-CC` | CC1101 RX or one controlled TX phase | declared recording/audio | nRF, U214/external, voice rail+interfaces, Si4732, IR, S3 RF and C5 RF |
| `SG-VOICE` | SA518 RX or TX plus required voice interfaces | codec capture/playback only if declared | nRF, CC, U214/external, Si4732, IR, S3 RF and C5 RF |
| `SG-BROADCAST` | Si4732 one FM/SW/AM/LW mode | codec/audio/decode/recording only if declared | nRF, CC, U214/external, voice rail+interfaces, IR, S3 RF and C5 RF |
| `SG-U214` | exact U214 LoRa plus declared onboard-Cap GNSS support | recording only if declared | nRF, CC, voice rail+interfaces, Si4732, IR, S3 RF and C5 RF |
| `SG-IR` | dual receive learner or separate TX phase | recording/decode only if declared | nRF, CC, U214/external, voice rail+interfaces, Si4732, S3 RF and C5 RF |
| `SG-EXT-*` | one exact Unit/Cap/accessory manifest | only members named by that manifest | every base signal boundary not named by the exact profile; unknown accessory keeps group `NONE` |

Storage and service links are not blanket-on. They exercise the maximum valid
transaction pattern only when required by the scenario, then return to their
own `STORAGE_QUIET`/`SERVICE_IPC_QUIET` state.

## Fixture set

| Fixture | Required proof |
|---|---|
| `FX-I6-CFG` | signed DUT/PCB/enclosure/cell/firmware/feed/antenna/accessory/region/temperature manifest and calibration revision |
| `FX-I6-CONDUCTED` | VNA loss/return loss, output/sensitivity, spectrum/harmonics, coupler direction and actual-TX calibration into controlled loads |
| `FX-I6-OTA` | calibrated shielded wanted signal plus enclosure/battery/display/hand/accessory poses; isolated baseline, quiet-state degradation, false detect and recovery |
| `FX-I6-N24-T1` | target plus independent observer for every three-radio role mix, channel/rate/power/sensitivity/latency/loss/age point |
| `FX-I6-OPTICAL` | light-tight calibrated 30–60-kHz receive/TX waveform, optical range, thermal input, IEC 62471 input and independent actual-light evidence |
| `FX-I6-DIGITAL` | logic-analyzer/timestamp traces for FIFO/IRQ, IPC, display, storage, audio, UI and encoder deadlines |
| `FX-I6-FAULT` | STOP/reset/brownout/rail/stuck-line/evidence/antenna/accessory/transition fault injection |
| `FX-I6-THERMAL` | cold/hot/low-cell/high-load corners with per-profile current, temperature and duty-limit evidence |

Exact instrument MPNs and calibration providers are I8 procurement inputs. A
functional fixture class is fixed here so later purchasing cannot silently
weaken the proof.

## Test order and pass boundary

1. Freeze exact configuration and calibration identity.
2. Measure isolated conducted plus OTA/optical baseline for every accepted
   mode, band, channel, power and antenna/pod profile.
3. Repeat with every foreign signal boundary in its exact quiet contract.
4. Add maximum valid system-plane aggression: dirty display updates, storage
   throughput and 250-ms stall, S3↔RP/C5 IPC, audio, UI/encoder and telemetry.
5. Exercise every allowed intragroup concurrency case with member-specific
   gaps, loss, age and actual-TX evidence.
6. Exercise every ordered installed-group transition through `NONE`:
   revoke → actual-TX-off → controller stop → isolate → rail/discharge verify →
   new self-test → visible identity → separate TX arm.
7. Run contained cross-group injection only for overload, false evidence,
   residual energy and recovery. It cannot create a runtime permission.
8. Repeat STOP/reset/brownout/stuck/missing/wrong/thermal fault corners.

The raw traces must prove the existing resource contracts: no nRF FIFO miss;
CC service never waits for nRF/U214; U214 UART has no overflow; S3↔RP alert to
read is at most 250 us with at least 1.5 MB/s framed payload; S3↔C5 keeps at
least 1.5 MB/s, at most 70% admitted occupancy and at most 2-ms control RTT;
display non-preemptible occupancy is at most 1 ms; ordinary UI responds within
100 ms; audio DMA is continuous and encoder detents are neither lost nor
invented.

All seven RF evidence paths and the optical IR path must have no false negative
at minimum qualified output. Strong inbound energy may safely delay a group
transition, but may never authorize TX. Any unknown state, missed deadline,
unbounded pulse, emission/exposure/thermal failure or manifest mismatch leaves
`NONE`, rejects or derates only the exact profile and reopens its owning block.

## Result

The consolidated I6 paper qualification scope receives **«Проведено ревью»**.
No physical evidence is claimed: conducted/OTA/optical/no-stall/thermal/fault
HIL is still `not_executed` and can reopen I6. Fixture preparation is allowed;
KiCad and the paused integrated mockup are not.

