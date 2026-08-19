# BOM-0023 — logic, interface and IR cost-evidence batch

- Статус: **проведено ревью одиннадцатой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005BW`](../reviews/REV-0005BW-logic-interface-ir-cost-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `TCA4307DGKR` | 1 | 2.0137 | DigiKey exact-MPN cut-tape tier |
| `TMUX1136DGSR` | 1 | 2.0581 | DigiKey exact-MPN cut-tape tier |
| `SN74LVC1G06DCKR` | 1 | 0.0749 | DigiKey exact-MPN cut-tape tier |
| `SN74LVC1G125DCKR` | 1 | 0.0583 | DigiKey exact-MPN cut-tape tier; exact line was out of stock at check time |
| `SN74LVC1G3157DBVR` | 1 | 0.1301 | DigiKey exact-MPN cut-tape tier |
| `SN74LVC3G07DCUR` | 1 | 0.4087 | DigiKey exact-MPN cut-tape tier |
| `SN74LVC3G34DCUR` | 1 | 0.2616 | DigiKey exact-MPN cut-tape tier |
| `TXS0102DCUR` | 1 | 0.3480 | Mouser exact-MPN cut-tape tier |
| `BAV70LT1G` | 1 | 0.0460 | DigiKey exact-MPN cut-tape tier |
| `VEMD1060X01` | 1 | 0.5371 | DigiKey exact-MPN cut-tape tier |
| `VSMY14940` | 1 | 0.5035 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-07133KL` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier; exact line was out of stock at check time |
| `RC0402FR-07196KL` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-071K65L` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-07220RL` | 1 | 0.0097 | DigiKey exact-MPN cut-tape tier; exact line was out of stock at check time |

Batch delta: **15 lines / 15 placements / USD 6.4788** per base device.
No price changes a device identity, value, package or role.

## Current snapshot

- cost evidence: **148/187 purchase lines**;
- covered placements: **802/857**;
- partial `base_product` subtotal: **USD 150.1783**;
- remaining unpriced: **39 lines**, ten with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates.

The current successor snapshot is [`BOM-0024`](BOM-0024-resistor-cost-evidence.md):
162/187 lines, 816/857 placements and USD 150.4157 partial base subtotal.
