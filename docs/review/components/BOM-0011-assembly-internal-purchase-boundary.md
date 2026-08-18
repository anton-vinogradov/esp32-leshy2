# BOM-0011 — assembly-internal purchase boundary

- Статус: **проведено ревью corrected purchasing coverage**
- Дата: 2026-08-19
- Finding: [`FND-0112`](../findings/FND-0112-assembly-internal-controller-was-double-counted.md)
- Decision: [`DEC-0103`](../decisions/DEC-0103-separate-architecture-nodes-from-purchase-bom.md)
- Review: [`REV-0005BJ`](../reviews/REV-0005BJ-assembly-internal-bom-propagation.md)

## Corrected boundary

`ST77922` is still an exact named component inside the HMX assembly and remains
visible in the architecture diagram/contact evidence. It is excluded from the
purchase manifest because the target buys the complete
`HMX035CTFT-001` LCM+CTP, not a bare COG plus separately manufactured glass.

| Metric | Before correction | Current |
|---|---:|---:|
| architecture instances | 858 | 858 |
| assembly-internal evidence nodes | implicit 0 | explicit 1 |
| supplied/costed placements | 858 | 857 |
| purchase MPN lines | 188 | 187 |
| source evidence | 187/188 | 186/187 |
| cost evidence | 0/188 | 0/187 |
| alternate/no-substitution evidence | 1/188 | 1/187 |

Only the denominator and internal controller line change. Quantities for every
other device remain identical. The generated CSV is the corrected purchasing
view; the generated principle atlas remains the complete architecture view.
