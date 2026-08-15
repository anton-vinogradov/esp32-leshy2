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
| 1. Vision and scope | Decision required |
| Later stages | Not started |

Accepted so far: the ESP32-C5 owns the three nRF24 radios and IR. The inter-MCU transport is deliberately unresolved because the ESP32-C5 has only one general-purpose SPI controller.

*Русская версия: [README.ru.md](README.ru.md).*
