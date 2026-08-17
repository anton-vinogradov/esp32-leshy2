# REV-0004R — module-to-SMA interface fact review

- Статус: **Проведено ревью фактов; `IMP-0042` ожидает решения**
- Дата: 2026-08-17
- Evidence: [`RFH-0001`](../architecture/RFH-0001-module-to-external-sma-interface-review.md)
- Finding: [`FND-0057`](../findings/FND-0057-ebyte-ipx-mating-family-unproven.md)
- Proposal: [`IMP-0042`](../improvements/IMP-0042-external-sma-gender-and-feed-policy.md)

## Проверено

| Проверка | Результат |
|---|---|
| S3 exact module | v1.8: first-generation connector; U.FL/MHF I/AMC mating compatibility explicit |
| C5 exact module | v1.2: first-generation `ANT1`; U.FL/MHF I/AMC explicit; `ANT2` default-disabled |
| Ebyte exact PDF | real 12×19×2 mm module and `IPX`/~50 Ω shown; generation/MPN/dimensions absent |
| Harness feasibility | official I-PEX evaluation and active Amphenol locked/bulkhead references exist |
| Scope split | 5 module-origin feeds and 4 PCB/frontend-origin feeds cannot share one generic BOM claim |
| Process order | mating convention can close in G2F; mount/length/IP/gasket remain G3 co-design |

## Результат

Fact scope получает **«Проведено ревью»**. Machine source corrected by
`FND-0057`; exact Ebyte mating remains a specimen blocker. Внешняя SMA
polarity/gender является owner choice `IMP-0042`, поэтому решение не
подменяется этим fact review.
