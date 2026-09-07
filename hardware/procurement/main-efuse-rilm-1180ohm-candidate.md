# Main eFuse current-limit resistor — candidate, not accepted

Checked **2026-09-07 14:44 UTC** on the live JLCPCB assembly-parts page,
not the older search-engine stock snapshot. No purchase or reservation made.

| Field | Live observation |
| --- | --- |
| Manufacturer / exact MPN | UNI-ROYAL (Uniroyal Elec), `0402WGF1181TCE` |
| JLC number | `C270651` |
| Value / package | 1.18 kΩ, ±1%, ±100 ppm/°C, 0402, 62.5 mW |
| Assembly | Extended; SMT Assembly; Economic **and Standard** PCBA |
| Source | JLCPCB |
| Stock / available order quantity | 31 / 12 |
| MOQ / reel | 1 / 10,000 |
| Published unit price | USD 0.0005 at 1+; the quantity widget displays USD 0.01 |

[Exact JLCPCB assembly page](https://jlcpcb.com/partdetail/260031-0402WGF1181TCE/C270651).
This factory-placeable candidate avoids external procurement. Availability must
be rechecked at architecture freeze and immediately before order; 12 available
pieces is not reserved inventory or a promise about assembly attrition allowance.

The current RF R67 is still **1.65 kΩ**, not this part. The 1.18-kΩ candidate
matches the nominal used in H1's main-rail calculation, but accepting it requires
reconciling the complete current-limit, converter, inductor, thermal and PGTH
envelope against the native circuit. Changing only the resistor to make a
margin calculation pass is not a completed power-design correction.

## Русский

На живой странице JLCPCB **07.09.2026, 14:44 UTC** подтверждён кандидат
`UNI-ROYAL 0402WGF1181TCE / C270651`: 1,18 кОм ±1%, ±100 ppm/°C,
0402, 62,5 мВт; Extended, SMT, Standard PCBA. Склад — 31 шт., доступно
к заказу — 12, MOQ — 1, опубликованная цена — $0,0005 за деталь
(виджет количества показывает $0,01). Ничего не заказано и не зарезервировано.

Это **не принятая замена**: на текущей схеме R67 остаётся 1,65 кОм.
Перед заменой нужно согласовать расчёт ограничения тока с фактическими
преобразователем, дросселем, нагревом и порогом Power Good. Наличие повторно
проверяется при заморозке архитектуры и непосредственно перед заказом.
