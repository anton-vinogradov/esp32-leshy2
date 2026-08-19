# BOM-0025 — specialty component cost evidence and explicit gates

- Статус: **проведено ревью тринадцатой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005BY`](../reviews/REV-0005BY-specialty-cost-gate-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `Q13FC13500005` | 1 | 0.2154 | LCSC exact-MPN quantity-50 tier applicable to a 100-piece purchase |
| `74LVC2G14GW,125` | 1 | 0.0587 | DigiKey current Nexperia exact-MPN cut-tape tier |
| `SN74LVC1G74DCUR` | 1 | 0.3300 | Mouser exact-MPN cut-tape tier |
| `AEQ10410` | 1 | 3.0600 | Mouser exact-MPN quantity-100 tier |
| `B0310J50100AHF` | 1 | 0.9929 | DigiKey exact-MPN cut-tape tier |
| `TSMP95000TT` | 1 | 1.0600 | Mouser exact-MPN quantity-100 tier |
| `WSL25125L000FEA` | 1 | 1.0600 | Mouser exact-MPN cut-tape tier; backorderable with incoming stock |

Numeric delta: **7 lines / 7 placements / USD 6.7770** per base device.

## Новые явные gates

| Device | Gate | Почему нет числовой цены |
|---|---|---|
| `PESD24VY1BSF` | `quantity_100_rfq_required` | exact Nexperia tier на 100 штук не опубликован; одноимённый ElecSuper нельзя считать тем же accepted device |
| `TSOP95238TT` | `quantity_100_rfq_required` | authorized line публикует только full-reel 2200-piece tier |

`74LVC2G14GW,125` additionally moves from an obsolete NXP-era DigiKey page to
the current stocked Nexperia exact line. No identity, package, value or role
changes.

## Current snapshot

- cost evidence: **169/187 purchase lines**;
- covered placements: **823/857**;
- partial `base_product` subtotal: **USD 157.1927**;
- remaining unpriced: **18 lines**, twelve with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates.

