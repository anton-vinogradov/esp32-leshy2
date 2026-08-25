# H4 result · joined pre-layout gate

[Русский](h4-prelayout-gate-report.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

H4 is reviewed and closed. Accepted H1 mechanics, H2 production ECAD, H3 virtual verification and executable firmware F3 results now form one checkable boundary. Three documentation-only contradictions were corrected; no virtually testable contradiction remains open.

```mermaid
flowchart LR
  H1["H1<br/>mechanics"] --> H4["✅ H4<br/>joined pre-layout gate"]
  H2["H2<br/>ECAD"] --> H4
  H3["H3<br/>virtual electrical"] --> H4
  F3["F3<br/>builds and emulation"] --> H4
  H4 --> H5["▶️ H5<br/>research first,<br/>samples only if necessary"]
```

| Reviewed boundary | Result |
|---|---:|
| H1 M1 | 80 of 80 assigned; no NC |
| H2 electrical identities / root nets | 1,046 / 268 |
| HW↔FW BSP | 5 domains, 125 contacts, byte-identical contract |
| Firmware F3 | 52 reproducible artifacts; 10 memory gates; exact S3 QEMU |
| H3 physical-only registry | 85 rows; H5=9, H6=10, H8=78 |

## Corrections

| Finding | Correction | Effect |
|---|---|---|
| `H4-JOIN-001` | Removed the stale four-M1-NC narrative and regenerated every derivative | No pinout, schematic or BOM change |
| `H4-JOIN-002` | Bound public H2 totals to the current machine artifacts | Documentation and traceability only |
| `H4-JOIN-003` | Updated the public intentional-NC count from 189 to the current 191 | Documentation and traceability only |

## What H4 does not prove

- None of the 85 physical checks is closed; every H5/H6/H8 owner remains intact.
- Non-S3 boot, real peripherals, RF/antennas, thermal behavior, received-part fit and flash rollback remain physical gates.
- Purchase, PCB placement/routing and fabrication remain unauthorized.

The next exact position is `H5.0.1`: exhaust manufacturer documents and serial alternatives for the nine H5 residuals first. Only evidence that cannot be obtained otherwise may enter a separately cost-approved sample proposal.

Machine evidence: [`H4.1`](../hardware/verification/generated/H4-PLG11-joined-review.json), [`H4.2`](../hardware/verification/generated/H4-PLG12-correction-closure.json), [`H4.3`](../hardware/verification/generated/H4-PLG13-acceptance-package.json).
