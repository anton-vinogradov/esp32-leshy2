# H4-R2 hardware/firmware contract reconciliation

[Русский](h4-r2-contract-reconciliation.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Input freeze](h4-r2-input-freeze.md)

`H4-R2.0.2` and the joined `H4-R2.1` cross-check are reviewed. The six-domain H2 contract, all 80 M1 contacts, current H3 imports, USB/service ownership, the 20-MHz direct i8080 contract and target-build claim boundaries agree across repositories.

The review found one bounded implementation-class issue with three domain owners: the generated F2 BSP still represents only `135` of the `173` current H2 controller rows. The missing `38` rows are firmware-generation omissions, not a hardware pinout change.

| Domain | H2 rows | Generated rows | Missing | Current mapping |
|---|---:|---:|---:|---|
| `s3` | 33 | 33 | 0 | `exact_pins` |
| `c5` | 14 | 6 | 8 | `partial_exact_pins` |
| `rf_rp` | 48 | 48 | 0 | `exact_pins` |
| `hub_rp` | 48 | 48 | 0 | `exact_pins` |
| `pack` | 13 | 0 | 13 | `identity_only` |
| `safety` | 17 | 0 | 17 | `identity_only` |

H4-R2.2 must regenerate complete exact maps for C5, Pack and Safety and make their owning targets fail closed on exact mapping/count. The separate F5/F6 display-driver obligation remains open by design; no H5/H6/H8 physical evidence is consumed.

**Current marker: `H4-R2.2`.** Purchase, placement, routing and fabrication remain unauthorized.

[Machine reconciliation](../hardware/verification/generated/H4-R2-contract-reconciliation.json) · [machine joined cross-check](../hardware/verification/generated/H4-R2-joined-crosscheck.json).
