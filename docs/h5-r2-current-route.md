# H5-R2 global result · current component route

**H5-R2.1 is reviewed.** The current R2 surface contains **250 purchasable groups / 1218 articles**: 205 routes inherit the complete H5-R1 audit and 45 are current H2 additions or replacements. No group is unmapped.

```mermaid
flowchart LR
  A["250 current groups<br/>1218 articles"] --> B["205 inherited<br/>H5-R1 routes"]
  A --> C["45 new or replaced<br/>exact routes"]
  B --> D["H6 · placement / routing"]
  C --> D
  C --> E["1 global-sourcing gate<br/>WBC16-1TLC"]
  C --> G["6 pre-orders<br/>confirm before order"]
  E -. "before order" .-> F["JLCPCB sourcing<br/>or qualified replacement"]
```

## What changed

- The cost report and H5 now consume the same native R2 inventory instead of the historical 210-line BOM.
- The 2026-09-08 recomposition includes exact [RUN/KILL SA](../hardware/procurement/h6-js102011saqn-selection-review.json), [IR TR](../hardware/procurement/h6-tsmp95000tr-candidate-review.json) and [audio SJ43515TS](../hardware/procurement/h6-sj43515ts-selection-review.json) replacements. IR and audio use explicit preorder, not allocated assembly stock. This date does not renew the other retained availability/price snapshots.
- The 2026-09-09 unification combines four USB-C ports into one GCT USB4105-GF-A group: the [fresh C3020560 route](../hardware/verification/jlcpcb-usb-unification-2026-09-09.json) is pre-order, minimum 9 pieces for approximately $9.59 while four are fitted. This is a separate current purchase snapshot; the retained historical quantity-100 planning price is not a quote for the single prototype.
- The 2026-09-14 C5 ECO adds exact TS3USB221ERSER / C129313 (1 fitted), SN74LV20APWR / C2862070 (2 fitted) and NX3008NBKS,115 / C396098 (3 fitted). The first and third have retained stock/Standard-PCBA captures; the NAND has **zero stock and explicit pre-order MOQ 21**, estimated at $0.4265 each / $8.9565 minimum, not the cost of two fitted pieces. NAND lead time, final price and allocation are still unconfirmed. All three records are reused from the [device registry](../hardware/architecture/devices.json) with their exact capture timestamps; this generator does not query the factory again.
- Corrected known electronics are **$312.04**; known external antennas are **$138.32**; combined they are **$450.35** before PCB, assembly, enclosure, delivery and 5 unpriced component groups / 2 unpriced antenna groups.
- `WBC16-1TLC` remains the exact schematic part but JLCPCB live stock is now zero. `H3-TC16-161T+` is a mass-market candidate, but it does not enter the BOM without pin-map, RF and exact factory-route qualification.

## Boundary

H6 may continue placement with the accepted footprints. Order release remains fail-closed until the `WBC16-1TLC` JLCPCB sourcing/private-library route or a fully qualified replacement is confirmed, and MOQ, final price, lead time and allocation are confirmed for all 6 pre-order routes, including the NAND. Recheck every exact part before order. Silent substitution is forbidden.

[Machine result](../hardware/verification/generated/H5-R2-current-route-revalidation.json) · [current cost top 20](h1-r2-cost.md)
