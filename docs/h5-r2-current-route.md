# H5-R2 global result · current component route

**H5-R2.1 is reviewed.** The current R2 surface contains **249 purchasable groups / 1216 articles**: 209 routes inherit the complete H5-R1 audit and 40 are current H2 additions or replacements. No group is unmapped.

```mermaid
flowchart LR
  A["249 current groups<br/>1216 articles"] --> B["209 revalidated<br/>H5-R1 routes"]
  A --> C["40 new or replaced<br/>exact routes"]
  B --> D["H6 · placement / routing"]
  C --> D
  C --> E["1 order-time gate<br/>WBC16-1TLC"]
  E -. "before order" .-> F["JLCPCB sourcing<br/>or qualified replacement"]
```

## What changed

- The cost report and H5 now consume the same native R2 inventory instead of the historical 210-line BOM.
- Corrected known electronics are **$311.38**; known external antennas are **$138.32**; combined they are **$449.70** before PCB, assembly, enclosure, delivery and 5 unpriced component groups / 2 unpriced antenna groups.
- `WBC16-1TLC` remains the exact schematic part but JLCPCB live stock is now zero. `H3-TC16-161T+` is a mass-market candidate, but it does not enter the BOM without pin-map, RF and exact factory-route qualification.

## Boundary

H6 may continue placement with the accepted `WBC16-1TLC` footprint. Order release remains fail-closed until a confirmed JLCPCB sourcing/private-library route or a fully qualified replacement exists. Silent substitution is forbidden.

[Machine result](../hardware/verification/generated/H5-R2-current-route-revalidation.json) · [current cost top 20](h1-r2-cost.md)
