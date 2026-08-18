# PIN-0003 — G2F-3I principled pinout review

- Статус: **Проведено ревью принципиальной распиновки leading paper candidate; I1…I5 and I6/nRF subblock paper reviewed, I6 active**
- Дата: 2026-08-17
- Machine source: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)
- Generated atlas: [`G2F-3I principled pinout`](generated/G2F-3I-principled-pinout.md)
- Full candidate ledger: [`G2F-pin-ledger`](generated/G2F-pin-ledger.md)
- Findings: [`FND-0059`](../findings/FND-0059-stale-pin-budget-after-quiet-state.md),
  [`FND-0060`](../findings/FND-0060-abstract-electrical-endpoints-block-final-pinout.md)
- Review: [`REV-0004V`](../reviews/REV-0004V-principled-pinout-self-review.md)
- Working-design decision: [`DEC-0051`](../decisions/DEC-0051-principled-pinout-as-working-design.md)
- Display-path amendment: [`DEC-0052`](../decisions/DEC-0052-qspi-first-display-path.md) /
  [`REV-0004X`](../reviews/REV-0004X-qspi-display-decision-propagation.md)
- Exact display fit: [`DSP-0005`](DSP-0005-hmx035ctft-electrical-fit.md) /
  [`REV-0005A`](../reviews/REV-0005A-hmx-display-electrical-fit.md)
- Exact display endpoint: [`DSP-0006`](DSP-0006-exact-display-rail-backlight-and-mate-profile.md) /
  [`REV-0005AO`](../reviews/REV-0005AO-display-endpoint-propagation.md)
- Exact microSD endpoint: [`STO-0001`](STO-0001-exact-isolated-microsd-endpoint.md) /
  [`REV-0005AP`](../reviews/REV-0005AP-microsd-endpoint-propagation.md)
- Exact codec fit: [`AUDIO-0001`](AUDIO-0001-es8311-exact-electrical-fit.md) /
  [`REV-0005B`](../reviews/REV-0005B-es8311-digital-fit-and-analog-gap.md)
- Complete audio decision: [`DEC-0054`](../decisions/DEC-0054-fail-safe-complete-audio-path.md) /
  [`REV-0005D`](../reviews/REV-0005D-audio-decision-propagation.md)
- Exact audio/receiver endpoint: [`AUDIO-0003`](AUDIO-0003-exact-audio-and-receiver-endpoint.md) /
  [`REV-0005AU`](../reviews/REV-0005AU-i5-audio-receiver-propagation.md)
- Service/IPC amendment: [`DEC-0059`](../decisions/DEC-0059-full-service-over-1bit-sdio.md) /
  [`REV-0005L`](../reviews/REV-0005L-full-service-1bit-sdio-propagation.md)
- Safety/evidence amendment: [`DEC-0061`](../decisions/DEC-0061-aon-stop-and-per-path-tx-evidence.md) /
  [`SAFE-0002`](SAFE-0002-accepted-aon-stop-and-evidence-circuit.md)
- Three-nRF electrical amendment: [`DEC-0091`](../decisions/DEC-0091-exact-three-nrf-electrical-endpoint.md) /
  [`REV-0005AV`](../reviews/REV-0005AV-i6-three-nrf-propagation.md)

## Что здесь называется принципиальной распиновкой

Это слой между wishlist и KiCad:

1. функция получает owner;
2. каждый MCU net получает реально выведенный contact exact module/package;
3. fixed-mux, strap, controller, PIO/DMA и service/recovery проверяются;
4. каждый endpoint либо указывает exact device contact, либо честно остаётся
   `abstract:*` blocker;
5. diagram и human-readable tables генерируются из того же JSON.

Это уже не legacy-набросок и не свободная block diagram. Но это ещё не
электрическая принципиальная схема: номиналы, protection, level shifting,
load switches, clocks, RF matching и exact unfrozen peripheral MPN должны быть
закрыты до KiCad.

## Текущая owner topology

| Owner | Ответственность | Независимость |
|---|---|---|
| `ESP32-S3-WROOM-1U-N16R2` | UI, display+microSD scheduler, I²S audio, internal I²C, M5 Unit profile, native 2.4/BLE/ESP-NOW | отдельные SPI2, SPI3, SD/MMC, I²S0, I²C0 и Unit-controller profile |
| `ESP32-C5-WROOM-1U-N8R8` | native 2.4/5 GHz, IEEE 802.15.4, dual-path IR | dedicated 1-bit SDIO to S3; native USB+UART service; IR uses RMT and direct evidence/power contacts |
| `RP2354B A4/QFN80` | 3×nRF, CC1101, U214 LoRa/GNSS/I²C, SA518 control/PTT, deterministic event service | five physical PIO SPI groups, hardware UART0/UART1/I²C0/SPI1, direct IRQ/CE/CSN/GDO |
| `TCA6424ARGJR` | reset/select/power/status main slow plane | 21/24 assigned; P03…P05 are free and no radio FIFO/PTT deadline lives here |
| `TCA9534APWR #UI` | D-pad/OK/BACK/OPT/F1/F2/encoder-push 4×3 matrix | P0…P6 assigned; P7 local reserve; all-low idle produces hardware interrupt |

The generated atlas contains the exact pad/contact table for all 91 exposed
compute GPIO plus the 24 main slow and eight UI-matrix contacts. Every
programmer/recovery path is
outside normal application dependency:

- S3: native USB Serial/JTAG + default UART0 + `EN/BOOT`;
- C5: native USB Serial/JTAG + permanent UART0 + `EN/BOOT/ROM-log strap`;
- RP: SWD + `RUN` + native USB + `BOOTSEL`;
- SA518: exact `UPDATE/UART_TX/UART_RX/PD` fixture breakout, with UPDATE drive
  forbidden until the rev-1.1 direction/timing ambiguity passes specimen proof.

## Current pin budget

| Domain | Used | Reserved | Free | Total exposed/allocatable |
|---|---:|---:|---:|---:|
| S3 | 33 | 3 | 0 | 36 |
| C5 | 14 | 6 | 1 | 21 |
| RP | 48 | 0 | 0 | 48 |
| main slow I/O | 21 | 0 | 3 | 24 |
| UI matrix I/O | 7 | 1 | 0 | 8 |

The `RP=0` result is deliberate and visible. `GPIO15` and `GPIO23` implement
the accepted nRF-group and CC quiet-state power gates. SWD/USB/RUN/BOOTSEL are
separate fixed service contacts and are not lost. Any new direct RP function
must trigger a remap; it cannot be added as a hidden «free pin».

`DEC-0059` originally left GPIO47 as the only free S3 contact. `DEC-0086` now
uses it with GPIO39 as the dedicated PCNT0 quadrature pair for the restored
encoder. S3 GPIO43/44 remain permanent UART0 service, C5 GPIO13/14 remain
native USB, and the M5 Unit UART profile continues on GPIO7/8.

## Exact peripheral contacts now instantiated

This pass removes two important abstractions without changing GPIO ownership:

- `NiceRF SA518 rev 1.1`: RP UART/PTT/activity now terminate on exact module
  pins `UART_RX=3`, `UART_TX=2`, `PTT=14`, `AUDIO_ON=18`; `HL=12`, `PD=13`,
  `UPDATE=17`, `MIC_IN=1` and `AFOUT=16` are present in fixed routes/service;
- `Si4732-A10-GS`: S3 I²C terminates on exact `SDIO=15`, `SCLK=13`; exact
  `RST=9`, `GPO2/INTB=5`, `SENB=14`, `RCLK=16`, audio outputs and separate
  `FMI=1`/`AMI=3` antenna routes are represented.

nRF contacts, CC1101 contacts, U214 Cap-Bus, TCA4307 and TCA6424A were already
exact in the source. Their production choice and electrical/RF qualification
are still separate gates.

The Hirose microSD socket now terminates through the complete
`STO-0001/DEC-0085` endpoint: SCK/CMD/CS use a card-powered Ioff triple buffer, DAT0/MISO
returns only while card CS is low, CMD/DAT0…DAT3 have switched pulls, all seven
non-ground card contacts plus detect have exact ESD channels, and detect stays
readable with card power off. This changes no allocation; GPIO4/5/35/36 remain
the same scheduled display/storage group. Physical access, real media and HIL
remain open.

The display path now also terminates on exact `HMX035CTFT-001` contacts from
the official QDtech schematic. Its QSPI path uses GPIO4/35/36/38/41/42, while
slow `P06/P07` provide display/touch reset. `DEC-0086` moves TP_INT through a
pin-compatible open-drain polarity-adapter footprint into shared `SYS_INT_N`
on GPIO37, releasing former direct GPIO39 for encoder phase A. Subsequent
`AUDIO-0002/FND-0067` consumes slow P27 for the previously
omitted `RX_AUDIO_SOURCE_SEL`. `DEC-0090/AUDIO-0003` later use P00/P01/P02
for capture source, reset-off speaker enable and headphone absence, leaving
P03…P05 free.
`DSP-0006/DEC-0084` later place the exact first ZIF connector candidate
between those nets and the panel, add reset-low defaults and close the exact
latch-protected PWM-backlight circuit without changing the pin budget.

The audio digital path now terminates on exact `ES8311` QFN-20 contacts:
GPIO1/2 are `CDATA/CCLK`, GPIO15/16/17/18 are
`SCLK/LRCK/DSDIN/ASDOUT`. `MCLK` is explicit NC under the BCLK-derived clock
contract. Slow `P10` is corrected to external `CODEC_PWR_EN`; physical `CE`
is an address strap for `0x19`, not reset/enable. `DEC-0054` now terminates
`OUTP/OUTN`, `MIC1P/MIC1N`, the RX selector, speaker selector, TX selector,
active capture buffer, reset-safe gate and PAM8302A on exact IC contacts.
`RX_AUDIO_SOURCE_SEL` is on slow P27; direct S3 GPIO6 is active-high
`AUDIO_ARM`. `AUDIO-0003/DEC-0090` now close exact codec/receiver/voice
power-domain isolation, all first-target analog values and exact microphone,
speaker and switched-headphone endpoints. GPIO43/44 are UART0 service;
GPIO39/47 now capture encoder phases with PCNT0, leaving no free S3 GPIO.
Acoustic, RF, powered-state and concurrency HIL remain open.

## Digital non-interference result

- every nRF has its own `SCK/MOSI/MISO/CSN/CE/IRQ` and PIO state machine;
- CC1101 and U214 do not share a radio data bus with nRF or display;
- S3↔RP and S3↔C5 use different dedicated controllers;
- display+microSD are the only high-rate scheduled pair and have bounded
  service: direct-QSPI display occupancy is `<=1 ms`, SD uses separate CS and
  per-device mode; no radio FIFO or IPC deadline uses that controller;
- PIO is `5/12`, RP DMA `13/16`, S3 GDMA TX/RX `3/5` with explicit reserves;
- all three nRF remain simultaneously active for every required PTX/PRX mix.

This is a paper proof of controller/pin independence, not physical RF or
signal-integrity proof.

`DEC-0051` publishes this reviewed result in the root target document as the
current principle-level design for G3. The generated atlas remains the complete
exact-contact projection and this publication does not freeze G7 architecture.
`DEC-0052` later amends the visible map with QSPI D2/D3 on S3 GPIO41/42 and
`DEC-0054` subsequently adds GPIO6 `AUDIO_ARM`; the current S3 budget is
`33/3/0` without changing owners.

## Remaining final-pinout blockers

[`FND-0060`](../findings/FND-0060-abstract-electrical-endpoints-block-final-pinout.md)
lists every remaining `abstract:*` endpoint. The material groups are:

- final real-tail display mate, standalone panel sourcing and display HIL;
  current display/backlight/audio/receiver paper circuits are exact;
- exact IR receiver/learning receiver/LED driver and optical front end; IR
  evidence detector MPN/paper routing is now exact;
- AON source/hold-up, branch power/current/thermal circuits and RF detector
  taps/threshold values; hard STOP latch/gates/evidence active devices are now exact;
- exact nRF/CC/voice/receiver RF feeds, matching, protection and coexistence;
- audio/receiver/voice specimen, acoustic, RF-immunity and concurrent-load HIL;
- M5 Unit protection/mux and final service connector mechanics.

The next pass closes these abstractions one group at a time against real parts,
then regenerates this atlas. KiCad remains blocked until no target-critical
`abstract:*` endpoint is silently unresolved and the later physical/product
gates have passed.
