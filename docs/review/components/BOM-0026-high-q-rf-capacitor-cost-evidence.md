# BOM-0026 — exact high-Q RF-capacitor cost evidence

- Статус: **проведено ревью четырнадцатой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005CA`](../reviews/REV-0005CA-high-q-rf-capacitor-cost-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `GJM1555C1H100JB01D` | 1 | 0.0417 | DigiKey exact-MPN cut-tape quantity-100 tier |
| `GJM1555C1H1R2BB01D` | 1 | 0.0310 | DigiKey exact-MPN cut-tape quantity-100 tier |
| `GJM1555C1H6R2DB01D` | 1 | 0.0210 | Mouser filtered table, exact-MPN cut-tape quantity-100 tier |
| `GJM1555C1H8R0DB01D` | 1 | 0.0207 | DigiKey exact-MPN cut-tape quantity-100 tier |
| `GJM1555C1HR47BB01D` | 1 | 0.0346 | DigiKey exact-MPN cut-tape quantity-100 tier |
| `GJM1555C1HR60BB01D` | 1 | 0.0310 | DigiKey exact-MPN cut-tape quantity-100 tier |

Batch delta: **6 lines / 6 placements / USD 0.1800** per base device.
Every row retains its exact capacitance, tolerance code, voltage, package and
RF role; no commodity-capacitor price was copied by analogy.

## Current snapshot

- cost evidence: **175/187 purchase lines**;
- covered placements: **829/857**;
- partial `base_product` subtotal: **USD 157.3727**;
- remaining unpriced: **12 lines, all twelve with explicit gates**;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates. The numeric price-search pass has no silent
unknowns left: each unpriced line now exposes its exact RFQ/retail boundary.
