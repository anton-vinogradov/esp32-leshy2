# Leshy2 Hardware — current engineering state

> Snapshot: 2026-08-16. This page describes what is proven now. The intended finished product is described in the [hardware target README](../../README.md); the [firmware target README](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.md) describes the finished software product.

- Canonical evidence: [review ledger](../review/README.md)
- Russian version: [current-state.ru.md](current-state.ru.md)
- Legacy reference only: [`drafts/legacy-2026-08-15/`](../../drafts/legacy-2026-08-15/README.md)

## Review progress

| Stage | State |
|---|---|
| 0. Review system and baseline | Reviewed |
| 1. Vision and boundaries | Reviewed, including three-tier clarification |
| 2. Capabilities and exclusions | In progress |
| 3–10 | Not started |

The canonical stage table is [`docs/review/stages.md`](../review/stages.md).

## Accepted target decisions already reflected in the product page

- all-in-one field-tool profile, non-aggression pledge, and three functional levels (`DEC-0002`, `DEC-0010`);
- conservative TX defaults and explicit maximum-power selection (`DEC-0003`);
- zero-loss total-cost optimization (`DEC-0005`);
- external M5 GNSS and external U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- onboard mono ES8311 audio architecture with fail-safe analog bypass (`DEC-0009`);
- C5 target ownership of 3×nRF24 and IR (`DEC-0001`), without claiming a working inter-MCU architecture.
- owner-controlled signed S3/C5 updates with rollback and an open developer lifecycle (`DEC-0013`), without enabling irreversible hardware lockdown.

## Open engineering state

- `FND-0001`: C5's single GP-SPI cannot serve the legacy nRF-master and S3↔C5-slave roles simultaneously.
- `FND-0002`: the BLE owner still differs between legacy repositories.
- `FND-0003`: audio architecture is accepted, but pin/electrical/firmware/HIL proof is pending.
- `FND-0006`: the original key-matrix proposal and audio controls collide on `U13.P10..P17`.
- `FND-0007`: the current STOP button is only an I²C-expander input, not an independent hardware TX kill.
- `FND-0009`: legacy GNSS is tied to u-blox AssistNow/UBX while the accepted M5 Unit/U214 use AT6668; the possible CASIC workaround awaits `IMP-0012` and proof on the actual firmware revisions.
- Existing tsCircuit/KiCad files remain legacy implementation artifacts until their producing stages are reviewed and regenerated.

## Current review work

The System/UI/storage capability slice is **Reviewed** under `REV-0002I`.

The current GNSS/navigation slice is defined by [`REQ-GNSS-0001`](../review/requirements/REQ-GNSS-0001-navigation-integrity.md). Its prerequisite audit `REV-0002J` is Reviewed and found `FND-0009`: the old u-blox mechanisms cannot be sent to AT6668. The official CASIC protocol nevertheless defines native assistance and jamming/spoofing messages.

⚠️ **Proposal `IMP-0012`:** keep the low-cost NMEA baseline and qualify an advanced CASIC profile separately for Unit GPS v1.1 and U214; unsupported/unknown must never be shown as “no threat.” `REQ-GNSS-0001` remains **In review** until the owner decides.

## Deferred architecture gate

[`IMP-0010`](../review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) remains open, but [`DEC-0012`](../review/decisions/DEC-0012-defer-imp-0010-to-pin-budget.md) defers the A/B choice to stage 3. No owner decision is requested until a consolidated pin/GPIO/resource budget covers both MCUs, expanders, fixed-function pins, inter-MCU transport, audio, UI/touch, external modules, and genuinely freed onboard GNSS/LoRa lines.

`FND-0006` and `FND-0007` remain open. The deferral neither selects `U14`/the 3×3 matrix nor proves a hardware STOP.
