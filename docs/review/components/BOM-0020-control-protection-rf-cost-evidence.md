# BOM-0020 — control, protection and RF-passive cost-evidence batch

- Статус: **проведено ревью восьмой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005BT`](../reviews/REV-0005BT-control-protection-rf-cost-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `DMN2056U-7` | 3 | 0.1490 | DigiKey exact-MPN cut-tape tier |
| `SESD0402X1UN-0020-090` | 3 | 0.3794 | DigiKey exact-MPN cut-tape tier |
| `LQG15HS10NJ02D` | 3 | 0.0310 | DigiKey exact-MPN cut-tape tier |
| `74LVC1G32GV,125` | 3 | 0.0523 | DigiKey exact-MPN cut-tape tier |
| `B57332V5103F360` | 3 | 0.1157 | DigiKey exact-MPN cut-tape tier |
| `CGA5L1X7R1E475K160AC` | 3 | 0.1419 | DigiKey exact-MPN cut-tape tier |
| `SN74LVC2G66DCUR` | 3 | 0.3930 | Mouser exact-MPN cut-tape tier |
| `RC0402FR-0733KL` | 3 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-073K32L` | 3 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `CRM2512-FX-20R0ELF` | 2 | 0.1840 | DigiKey exact-MPN cut-tape tier |
| `MMBT3904-7-F` | 2 | 0.0597 | DigiKey exact-MPN cut-tape tier; DigiKey stock was zero at check time |
| `C0402C102K5RACTU` | 2 | 0.0150 | DigiKey exact-MPN cut-tape tier |
| `0451005.MRL` | 2 | 1.4488 | DigiKey exact-MPN cut-tape tier |
| `GRM1555C1H220JA01D` | 2 | 0.0025 | LCSC exact-MPN quantity-100 tier |
| `GRM1555C1H390JA01D` | 2 | 0.0140 | Mouser exact-MPN cut-tape tier; only 63 shown in stock at check time |

Batch delta: **15 lines / 39 placements / USD 7.2931** per base device.
The exact `0451005.MRL` pair contributes USD 2.8976 and is the largest new
line subtotal. No price changes a device identity, value, package or role.

## New explicit gate

`GJM1555C1H101JB01D` is the accepted high-Q 100-pF RF DC-block part. Current
exact-MPN evidence exposes RFQ inventory but no published comparable
quantity-100 USD tier. It therefore receives `quantity_100_rfq_required`.
Changing it merely to obtain a published price would require RF matching and
substitution requalification, so no numeric value or replacement is invented.

## Current snapshot

- cost evidence: **106/187 purchase lines**;
- covered placements: **747/857**;
- partial `base_product` subtotal: **USD 140.7642**;
- remaining unpriced: **81 lines**, nine with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates.

The current successor is
[`BOM-0022`](BOM-0022-rf-timing-indicator-passive-cost-evidence.md): 133/187
lines, 787/857 placements and USD 143.6995 partial base subtotal.
