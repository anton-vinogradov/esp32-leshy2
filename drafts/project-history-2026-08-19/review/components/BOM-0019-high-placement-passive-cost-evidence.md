# BOM-0019 — high-placement passive and discrete cost-evidence batch

- Статус: **проведено ревью седьмой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005BS`](../reviews/REV-0005BS-high-placement-passive-cost-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `C0402C330J5GACTU` | 5 | 0.0213 | DigiKey exact-MPN cut-tape tier |
| `GRM21BR60J226ME39L` | 5 | 0.1341 | DigiKey exact-MPN cut-tape tier; only five shown in stock at check time |
| `RC0402FR-07169KL` | 5 | 0.0097 | DigiKey exact-MPN cut-tape tier; DigiKey stock was zero at check time |
| `RC0402FR-0749R9L` | 5 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-075K1L` | 5 | 0.0103 | DigiKey exact-MPN cut-tape tier; conservative loose-part route rather than Digi-Reel |
| `2N7002DW-7-F` | 4 | 0.1277 | DigiKey exact-MPN cut-tape tier; DigiKey stock was zero at check time |
| `BAT54-7-F` | 4 | 0.0698 | DigiKey exact-MPN cut-tape tier |
| `BLM18PG181SN1D` | 4 | 0.0431 | DigiKey exact-MPN cut-tape tier |
| `GRM1555C1H221JA01D` | 4 | 0.0177 | DigiKey exact-MPN cut-tape tier |
| `GRM155R71H472KA01D` | 4 | 0.0098 | DigiKey exact-MPN cut-tape tier |
| `GRM188R71E474KA12D` | 4 | 0.0496 | DigiKey exact-MPN cut-tape tier |
| `GRM21BR71E225KE11L` | 4 | 0.0612 | DigiKey exact-MPN cut-tape tier |
| `BAT54ALT1G` | 4 | 0.0577 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-0752R3L` | 4 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-0768KL` | 4 | 0.0097 | DigiKey exact-MPN cut-tape tier |

Batch delta: **15 lines / 65 placements / USD 2.7495** per base device.

The machine-generated subtotal, rather than a hand sum, is authoritative.
This batch deliberately prioritizes placement coverage: low-cost passives and
dual/single discretes account for 65 more supplied placements without changing
any accepted circuit value, package, pin, rail or role.

## Procurement watch

The exact DigiKey snapshots for `GRM21BR60J226ME39L`,
`RC0402FR-07169KL` and `2N7002DW-7-F` do not show enough current stock for a
100-device build. Their published quantity-100 prices remain valid evidence for
the cost snapshot, while their separate dated orderability sources or
substitution classes remain authoritative for procurement. No alternate is
silently promoted: an exact replacement still has to pass the existing
electrical, package and policy gates.

## Current snapshot

- cost evidence: **91/187 purchase lines**;
- covered placements: **708/857**;
- partial `base_product` subtotal: **USD 133.4711**;
- remaining unpriced: **96 lines**, eight with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates.

The current successor is
[`BOM-0026`](BOM-0026-high-q-rf-capacitor-cost-evidence.md): 175/187 lines,
829/857 placements and USD 157.3727 partial base subtotal.
