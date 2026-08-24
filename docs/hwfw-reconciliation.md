# Leshy2 end-to-end hardware/firmware reconciliation

[Русский](hwfw-reconciliation.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

H2.7 binds physical H1, production ECAD and the firmware F2 input into one verifiable contract.

| Boundary | Reviewed | Result |
|---|---:|---|
| H1 ↔ instance ledger ↔ symbols | 1048 rows / 1046 identities | 0 MPN/contact mismatches |
| root hierarchy nets | 268 | all present in native netlists |
| M1 UI ↔ RF | 80 contacts / 51 nets | row-for-row identical |
| architecture ↔ KiCad | 130 allocations | 0 pin/net mismatches |
| H2 export ↔ firmware F2 | 125 MCU contacts | byte-identical, temporary pins forbidden |

## Corrected mismatches

- `H2.7.2-F01` — the instance ledger called logical-function counts physical contacts for ten expanded-pad/module cases → every row now carries logical_contact_count and physical_pcb_contact_count separately; contact_count follows the actual carrier/package land count
- `H2.7.4-F01` — PACK UART allocations used PACK_SERVICE_UART_TX/RX while KiCad, fixture pads and fixed routes used PACK_ADMISSION_UART_TX/RX → the two allocation/F2 names now use the established PACK_ADMISSION_UART_TX/RX canonical nets

✅ **Reviewed:** H2.7 is closed with no end-to-end mismatch remaining.

[Machine evidence](../hardware/ecad/generated/H2-REV75-hwfw-consolidated.json).
