# H5-R2 global result · current component route

**H5-R2.1 is reviewed.** The current R2 surface contains **249 purchasable groups / 1216 articles**: 206 routes inherit the complete H5-R1 audit and 43 are current H2 additions or replacements. No group is unmapped.

```mermaid
flowchart LR
  A["249 current groups<br/>1216 articles"] --> B["206 inherited<br/>H5-R1 routes"]
  A --> C["43 new or replaced<br/>exact routes"]
  B --> D["H6 · placement / routing"]
  C --> D
  C --> E["1 order-time gate<br/>WBC16-1TLC"]
  E -. "before order" .-> F["JLCPCB sourcing<br/>or qualified replacement"]
```

## What changed

- The cost report and H5 now consume the same native R2 inventory instead of the historical 210-line BOM.
- The 2026-09-08 recomposition includes exact [RUN/KILL SA](../hardware/procurement/h6-js102011saqn-selection-review.json), [IR TR](../hardware/procurement/h6-tsmp95000tr-candidate-review.json) and [audio SJ43515TS](../hardware/procurement/h6-sj43515ts-selection-review.json) replacements. IR and audio use explicit preorder, not allocated assembly stock. This date does not renew the other retained availability/price snapshots.
- Corrected known electronics are **$312.04**; known external antennas are **$138.32**; combined they are **$450.35** before PCB, assembly, enclosure, delivery and 5 unpriced component groups / 2 unpriced antenna groups.
- `WBC16-1TLC` remains the exact schematic part but JLCPCB live stock is now zero. `H3-TC16-161T+` is a mass-market candidate, but it does not enter the BOM without pin-map, RF and exact factory-route qualification.

## Boundary

H6 may continue placement with the accepted `WBC16-1TLC` footprint. Order release remains fail-closed until a confirmed JLCPCB sourcing/private-library route or a fully qualified replacement exists. Silent substitution is forbidden.

[Machine result](../hardware/verification/generated/H5-R2-current-route-revalidation.json) · [current cost top 20](h1-r2-cost.md)
