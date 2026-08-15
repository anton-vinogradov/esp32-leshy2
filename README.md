# Leshy2

The Leshy2 design documentation is being rebuilt from first principles, one reviewed stage at a time.

## Authoritative state

- The review ledger lives in [`docs/review/`](docs/review/README.md).
- Only accepted decisions and artifacts marked **Reviewed** are authoritative.
- Earlier documentation is preserved under [`drafts/legacy-2026-08-15/`](drafts/legacy-2026-08-15/README.md) for reference only.
- Existing tsCircuit and KiCad files are legacy implementation artifacts until their producing stage is reviewed and they are regenerated from the new design.

## Current status

| Stage | Status |
|---|---|
| 0. Review system and baseline | Reviewed |
| 1. Vision and scope | Reviewed |
| 2. Capabilities and exclusions | In progress |
| Later stages | Not started |

Accepted so far: Leshy2 is an all-in-one field tool whose security-research functions live only in **Lab** and progress from low-impact observation to the most serious authorized tests. Initial setup requires acceptance of the non-aggression pledge.

All transmitters boot off, every Lab tool starts disarmed, and initial TX uses a conservative profile. Maximum TX power is available only after an explicit user choice; it is never the global default.

Full product cost is optimized under `DEC-0005`, but a cheaper implementation is accepted only after proving no loss of capability, performance, safety, reliability, autonomy, serviceability, or testability.

For the three nRF24 radios and IR, only the **target C5-ownership constraint** is accepted—not a working architecture. Its feasibility remains unproven: the legacy topology assigns the C5's sole general-purpose SPI controller two incompatible roles. The inter-MCU transport must be replaced or independently proven at stage 3; see `FND-0001`.

*Русская версия: [README.ru.md](README.ru.md).*
