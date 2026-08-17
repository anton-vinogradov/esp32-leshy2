# PIN-0003 — G2F-3I principled pinout review

- Статус: **Проведено ревью принципиальной распиновки leading paper candidate; final electrical closure открыта**
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
| `ESP32-C5-WROOM-1U-N8R8` | native 2.4/5 GHz, IEEE 802.15.4, dual-path IR | dedicated 4-bit SDIO to S3; IR uses RMT and direct evidence/power contacts |
| `RP2354B A4/QFN80` | 3×nRF, CC1101, U214 LoRa/GNSS/I²C, SA518 control/PTT, deterministic event service | five physical PIO SPI groups, hardware UART0/UART1/I²C0/SPI1, direct IRQ/CE/CSN/GDO |
| `TCA6424ARGJR` | ordinary UI/reset/select/power/status slow plane | 23/24 assigned, P27 controlled reserve; no radio FIFO/PTT deadline lives here |

The generated atlas contains the exact pad/contact table for all 91 exposed
compute GPIO plus the 24 slow contacts. Every programmer/recovery path is
outside normal application dependency:

- S3: native USB Serial/JTAG + `EN/BOOT`;
- C5: permanent UART0 + `EN/BOOT/ROM-log strap` because SDIO consumes native
  USB pins at runtime;
- RP: SWD + `RUN` + native USB + `BOOTSEL`;
- SA518: exact `UPDATE/UART_TX/UART_RX/PD` fixture breakout, with UPDATE drive
  forbidden until the rev-1.1 direction/timing ambiguity passes specimen proof.

## Current pin budget

| Domain | Used | Reserved | Free | Total exposed/allocatable |
|---|---:|---:|---:|---:|
| S3 | 31 | 3 | 2 | 36 |
| C5 | 14 | 6 | 1 | 21 |
| RP | 48 | 0 | 0 | 48 |
| slow I/O | 23 | 1 | 0 | 24 |

The `RP=0` result is deliberate and visible. `GPIO15` and `GPIO23` implement
the accepted nRF-group and CC quiet-state power gates. SWD/USB/RUN/BOOTSEL are
separate fixed service contacts and are not lost. Any new direct RP function
must trigger a remap; it cannot be added as a hidden «free pin».

## Exact peripheral contacts now instantiated

This pass removes two important abstractions without changing GPIO ownership:

- `NiceRF SA518 rev 1.1`: RP UART/PTT/activity now terminate on exact module
  pins `UART_RX=3`, `UART_TX=2`, `PTT=14`, `AUDIO_ON=18`; `HL=12`, `PD=13`,
  `UPDATE=17`, `MIC_IN=1` and `AFOUT=16` are present in fixed routes/service;
- `Si4732-A10-GS`: S3 I²C terminates on exact `SDIO=15`, `SCLK=13`; exact
  `RST=9`, `GPO2/INTB=5`, `SENB=14`, `RCLK=16`, audio outputs and separate
  `FMI=1`/`AMI=3` antenna routes are represented.

nRF contacts, CC1101 contacts, U214 Cap-Bus, TCA4307, TCA6424A and the Hirose
microSD socket were already exact in the source. Their production choice and
electrical/RF qualification are still separate gates.

The display path now also terminates on exact `HMX035CTFT-001` contacts from
the official QDtech schematic. Its QSPI path uses GPIO4/35/36/38/41/42;
former GPIO39/DC is reused
as touch IRQ, while slow `P06/P07` provide display/touch reset. This consumes
no new contact, leaves S3 GPIO6/GPIO43 free and keeps TE conditional on HIL.

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
changes the current S3 budget to `31/3/2` without changing owners.

## Remaining final-pinout blockers

[`FND-0060`](../findings/FND-0060-abstract-electrical-endpoints-block-final-pinout.md)
lists every remaining `abstract:*` endpoint. The material groups are:

- production-qualified display connector/backlight/protection/sourcing and
  exact codec package; the current HMX display paper endpoint itself is exact;
- exact IR receiver/learning receiver/LED driver and TX evidence;
- hard STOP latch, actual-TX detectors and power/current/thermal supervisor;
- nRF/CC/voice/receiver load switches, isolation and level domains;
- audio selectors and matching;
- M5 Unit protection/mux and final service connector mechanics.

The next pass closes these abstractions one group at a time against real parts,
then regenerates this atlas. KiCad remains blocked until no target-critical
`abstract:*` endpoint is silently unresolved and the later physical/product
gates have passed.
