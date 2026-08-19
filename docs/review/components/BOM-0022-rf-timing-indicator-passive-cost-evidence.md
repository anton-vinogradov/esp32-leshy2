# BOM-0022 — RF, timing, indicator and passive cost-evidence batch

- Статус: **проведено ревью десятой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005BV`](../reviews/REV-0005BV-rf-timing-indicator-passive-cost-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `GJM1555C1H150JB01D` | 2 | 0.0392 | DigiKey exact-MPN cut-tape tier |
| `ABM8-26.000MHZ-10-D-1-G-T` | 1 | 0.3257 | DigiKey exact-MPN cut-tape tier |
| `LTST-C190KFKT` | 1 | 0.0637 | DigiKey exact-MPN cut-tape tier |
| `LTST-C190KRKT` | 1 | 0.0675 | DigiKey exact-MPN cut-tape tier |
| `GRM1555C1H102JA01D` | 1 | 0.0181 | DigiKey exact-MPN cut-tape tier; exact line was out of stock at check time |
| `GRM155R71A474KE01D` | 1 | 0.1771 | DigiKey exact-MPN cut-tape tier |
| `GRM31C5C1H224JE02L` | 1 | 0.3198 | DigiKey exact-MPN cut-tape tier |
| `GRM31CR71A226KE15L` | 1 | 0.1884 | DigiKey exact-MPN cut-tape tier |
| `LQG15HS15NJ02D` | 1 | 0.0310 | DigiKey exact-MPN cut-tape tier |
| `LQG15HS2N2S02D` | 1 | 0.0310 | DigiKey exact-MPN cut-tape tier |
| `LQG15HS3N3S02D` | 1 | 0.0310 | DigiKey exact-MPN cut-tape tier |
| `LQG15HS3N6S02D` | 1 | 0.0310 | DigiKey exact-MPN cut-tape tier |
| `LQG15HS6N8J02D` | 1 | 0.0310 | DigiKey exact-MPN cut-tape tier |
| `LQW15AN56NJ00D` | 1 | 0.0724 | DigiKey exact-MPN cut-tape tier |
| `C1608X7S2A104K080AB` | 1 | 0.0526 | DigiKey exact-MPN cut-tape tier |

Batch delta: **15 lines / 16 placements / USD 1.5187** per base device.
No price changes a device identity, value, package or role.

## Current snapshot

- cost evidence: **133/187 purchase lines**;
- covered placements: **787/857**;
- partial `base_product` subtotal: **USD 143.6995**;
- remaining unpriced: **54 lines**, ten with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates.

This artifact preserves the reviewed tenth-batch checkpoint. Current coverage
is in [`BOM-0025`](BOM-0025-specialty-cost-and-gates.md): 169/187
lines, 823/857 placements and partial base subtotal USD 157.1927.
