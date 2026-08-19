# BOM-0017 — power, UI and receiver cost-evidence batch

- Статус: **проведено ревью пятой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published quantity-100 component tier
- Review: [`REV-0005BQ`](../reviews/REV-0005BQ-power-ui-rf-cost-evidence-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `TPS2553DRVR-1` | 1 | 0.6093 | DigiKey exact-MPN cut-tape tier |
| `Si4732-A10-GSR` | 1 | 1.6785 | JLCPCB exact-MPN PCBA-only `100+` tier |
| `TCA6424ARGJR` | 1 | 1.7001 | DigiKey exact-MPN cut-tape tier |
| `TPD8E003DQDR` | 1 | 0.6445 | DigiKey exact-MPN cut-tape tier |
| `TPD4S201RUKR` | 1 | 0.7713 | DigiKey exact-MPN cut-tape tier |
| `TPS629203DRLR` | 1 | 0.6192 | DigiKey exact-MPN cut-tape tier |
| `TPS25961DRVR` | 1 | 0.4513 | DigiKey exact-MPN cut-tape tier |
| `CAT24C512WI-GT3` | 1 | 0.7133 | DigiKey exact-MPN cut-tape tier |
| `TVS2200DRVR` | 1 | 0.4493 | DigiKey exact-MPN cut-tape tier |

Batch delta: **9 lines / 9 placements / USD 7.6368** per base device.

The Si4732 figure is intentionally tied to the selected assembly supplier. The
page states that stocked parts remain in the JLCPCB library for PCBA and cannot
be shipped separately; it is therefore valid for the current factory-material
route, not a claim about standalone distributor availability.

## Нечисловой gate

`TPUL2G223BQBR` is an exact active-production part, but the current TI order
page publishes neither inventory nor a quantity-100 price. It now carries
`quantity_100_rfq_required`. No full-reel price, zero or estimated legacy logic
price enters the subtotal.

## Current snapshot

- cost evidence: **61/187 purchase lines**;
- covered placements: **623/857**;
- partial `base_product` subtotal: **USD 109.8573**;
- remaining unpriced: **126 lines**, six with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates.

This artifact preserves the reviewed fifth-batch checkpoint. Current coverage
is in [`BOM-0023`](BOM-0023-logic-interface-ir-cost-evidence.md): 148/187
lines, 802/857 placements and partial base subtotal USD 150.1783.
