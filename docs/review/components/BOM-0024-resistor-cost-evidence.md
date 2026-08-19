# BOM-0024 — exact resistor cost-evidence batch

- Статус: **проведено ревью двенадцатой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005BX`](../reviews/REV-0005BX-resistor-cost-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `RC0402FR-07240KL` | 1 | 0.0009 | LCSC exact-MPN quantity-100 tier |
| `RC0402FR-07270KL` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-0730K1L` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-0742K2L` | 1 | 0.0049 | LCSC exact-MPN quantity-100 tier |
| `RC0402FR-0744K2L` | 1 | 0.0052 | LCSC exact-MPN quantity-100 tier |
| `RC0402FR-074K7L` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-0756KL` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier; exact line showed 26 units in stock at check time |
| `RC0402FR-075K23L` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-07620KL` | 1 | 0.0009 | LCSC exact-MPN quantity-100 tier |
| `RC0402FR-078K2L` | 1 | 0.0009 | LCSC exact-MPN quantity-100 tier |
| `RC0402JR-070RL` | 1 | 0.0048 | DigiKey exact-MPN cut-tape tier |
| `RC1206FR-0733RL` | 1 | 0.0247 | DigiKey exact-MPN cut-tape tier |
| `RT0402BRD07100KL` | 1 | 0.0646 | DigiKey exact-MPN cut-tape tier |
| `RT0402BRD07191KL` | 1 | 0.0820 | Mouser exact-MPN cut-tape tier |

Batch delta: **14 lines / 14 placements / USD 0.2374** per base device.
No price changes a device identity, resistance, tolerance, package or role.

## Current snapshot

- cost evidence: **162/187 purchase lines**;
- covered placements: **816/857**;
- partial `base_product` subtotal: **USD 150.4157**;
- remaining unpriced: **25 lines**, ten with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates. The low exact stock observed for
`RC0402FR-0756KL` is a procurement watch, not permission to substitute it.

The current successor snapshot is [`BOM-0025`](BOM-0025-specialty-cost-and-gates.md):
169/187 lines, 823/857 placements and USD 157.1927 partial base subtotal;
twelve unpriced lines have explicit gates.
