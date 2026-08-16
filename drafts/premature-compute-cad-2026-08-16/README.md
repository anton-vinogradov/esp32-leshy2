# Premature compute CAD snapshot

- Archived: 2026-08-16
- Source: exact tracked CAD/CI snapshot from commit `d997122` (`HEAD` when the architecture process was reopened)
- Status: **noncanonical draft/reference; do not use for implementation**
- Superseding decision: [`DEC-0032`](../../docs/review/decisions/DEC-0032-reopen-product-design-before-cad.md)

This snapshot preserves the former `SYN-3A` compute symbols, footprints, provenance,
validator and CI workflow for traceability. Its presence does not select S3, C5,
RP2354A, their package variants, their service topology or any interconnect.

Reusing any part requires a reviewed target product design, whole-device optimality
decision, conceptual placement and new atomic architecture review under `FLOW-0001`.
