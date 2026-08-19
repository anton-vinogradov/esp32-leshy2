# BOM-0018 — audio, power and mechanical cost-evidence batch

- Статус: **проведено ревью шестой партии; full I8 remains open**
- Дата проверки цен: 2026-08-19
- Basis: exact MPN, USD, published tier applicable to a 100-piece purchase
- Review: [`REV-0005BR`](../reviews/REV-0005BR-audio-power-mechanical-cost-propagation.md)

## Числовые строки

| Device | Qty/device | USD @100 | Evidence route |
|---|---:|---:|---|
| `ES8311` | 1 | 0.3024 | JLCPCB exact `C962342` PCBA-only `100+` tier |
| `TS5A63157DCKR` | 2 | 0.2330 | DigiKey exact-MPN cut-tape tier; current stock is zero |
| `TLV9061IDBVR` | 2 | 0.3940 | DigiKey exact-MPN cut-tape tier |
| `PAM8302AASCR` | 1 | 0.3605 | DigiKey exact-MPN cut-tape tier |
| `TPS3839K33DBZR` | 2 | 0.3940 | DigiKey exact-MPN cut-tape tier |
| `CMEJ-0413-42-SMT-TR` | 1 | 0.3909 | DigiKey exact-MPN cut-tape tier |
| `SJ1-3515-SMT-TR` | 1 | 1.1166 | DigiKey exact-MPN cut-tape tier |
| `AS02404PO` | 1 | 2.5294 | DigiKey `50+` bulk tier, applicable at quantity 100 |
| `TCA9534APWR` | 2 | 1.0212 | DigiKey exact-MPN cut-tape tier |
| `MWSA0503S-2R2MT` | 1 | 0.5751 | DigiKey exact-MPN cut-tape tier |
| `WPN201612H2R2MT` | 1 | 0.0426 | JLCPCB exact `C97025` PCBA-only `100+` tier |
| `MWSA0503S-4R7MT` | 1 | 0.5751 | DigiKey exact-MPN cut-tape tier |
| `CSD87313DMST` | 1 | 1.4735 | DigiKey exact-MPN cut-tape tier |
| `1048P` | 1 | 8.5700 | Mouser exact-MPN tray tier at 100 |
| `TPD2EUSB30ADRTR` | 2 | 0.4219 | DigiKey exact-MPN cut-tape tier |

Batch delta: **15 lines / 20 placements / USD 20.8643** per base device.

The `ES8311` and `WPN201612H2R2MT` figures are intentionally scoped to
JLCPCB assembly inventory, which cannot be shipped as loose parts. `1048P` is
the dominant new line in this batch; its exact quantity-100 tray evidence adds
USD 8.57 to the partial material subtotal. The corrected exact DigiKey route
for `TPD2EUSB30ADRTR` is product `2520830`; the previous `3752964` URL did not
identify this order code.

## Нечисловые gates

- `Y78B23214FP`: the exact authorized source exposes a regional AUD table and
  skips from 25 to 250 pieces. The USD baseline therefore records
  `quantity_100_rfq_required` instead of applying an implicit FX conversion.
- `MWSA0503S-3R3MT`: the exact assembly listing publishes CNY tax-inclusive
  tiers. It also receives `quantity_100_rfq_required`; a CNY value is not
  silently converted into the USD contract.

## Sixth-batch checkpoint

- cost evidence: **76/187 purchase lines**;
- covered placements: **643/857**;
- partial `base_product` subtotal: **USD 130.7216**;
- remaining unpriced: **111 lines**, eight with explicit gates;
- one standalone orderability gap, four physical-family gaps and specific
  alternate qualification remain open.

This is component material only, not complete COGS. PCB, PCBA, test, enclosure,
yield, tooling, freight, tax, batteries and optional accessory pricing remain
separate until their correct gates.

The current successor is
[`BOM-0022`](BOM-0022-rf-timing-indicator-passive-cost-evidence.md): 133/187
lines, 787/857 placements and USD 143.6995 partial base subtotal.
