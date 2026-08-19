# BOM-0021 — control, logic and passive cost-evidence batch

- Статус: **проведено ревью девятой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005BU`](../reviews/REV-0005BU-control-logic-passive-cost-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `GRM155R71E473KA88D` | 2 | 0.0126 | DigiKey exact-MPN cut-tape tier |
| `GRM188R71E224KA88D` | 2 | 0.0306 | DigiKey exact-MPN cut-tape tier |
| `GRM188Z71A475ME15D` | 2 | 0.0899 | DigiKey exact-MPN cut-tape tier |
| `ERJ-2RKF27R0X` | 2 | 0.0155 | DigiKey exact-MPN cut-tape tier; exact line was out of stock at check time |
| `ERJ-P08F10R0V` | 2 | 0.0689 | DigiKey exact-MPN cut-tape tier |
| `SN74LVC08APWR` | 2 | 0.2127 | DigiKey exact-MPN cut-tape tier; exact line was out of stock at check time |
| `SN74LVC2G08DCUR` | 2 | 0.2296 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-07110KL` | 2 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-0712KL` | 2 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-072K21L` | 2 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-0730KL` | 2 | 0.0097 | DigiKey exact-MPN cut-tape tier |
| `RC0402FR-0745K3L` | 2 | 0.0097 | DigiKey exact-MPN cut-tape tier |

Batch delta: **12 lines / 24 placements / USD 1.4166** per base device.
No price changes a device identity, value, package or role.

## New explicit gate

`ERJ-P08F49R9V` remains the accepted exact 49.9-ohm, 0.66-W balance
resistor. Its authorized-distributor page exposes only a 5,000-piece full
reel; accessible quantity-100 reference pricing belongs to broker/RFQ routes.
It therefore receives `quantity_100_rfq_required` instead of a fabricated
quantity-100 value or a silent component substitution.

## Current snapshot

- cost evidence: **118/187 purchase lines**;
- covered placements: **771/857**;
- partial `base_product` subtotal: **USD 142.1808**;
- remaining unpriced: **69 lines**, ten with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates.

This artifact preserves the reviewed ninth-batch checkpoint. Current coverage
is in [`BOM-0023`](BOM-0023-logic-interface-ir-cost-evidence.md): 148/187
lines, 802/857 placements and partial base subtotal USD 150.1783.
