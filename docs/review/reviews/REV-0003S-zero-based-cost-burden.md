# REV-0003S — ревью dated cost/implementation burden

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3, шаг 5e
- Артефакт: `CST-0001`

## Проверка

| Gate | Результат |
|---|---|
| Comparable basis | one supplier, USD, qty 500, same date; common product BOM cancels |
| Price vs stock | quantity-tier price is not called available inventory; RP immediate stock shortfall is explicit |
| Exact vs allowance | quoted ICs separated from $0.10…0.30 glue/passive ranges and unquoted assembly/PCB |
| Recurring result | `2B $0.5017…0.6517`, `2A $0.6313…0.7813`, `3A $1.7359…1.8859` |
| NRE | candidate-specific work packages counted separately; no fabricated engineer-week/dollar rate |
| No-loss filter | RP2040, external-flash RP2350A, unqualified cheap logic and reduced nRF topology not called equivalent savings |
| Lifecycle | RP2350 official 2045 statement recorded separately from current supplier allocation |
| No premature winner | cost ranks axes but leaves atomic architecture decision to `PKG-*` |

## Пересчёт midpoint

- `2A`: `(0.6313 + 0.7813)/2 = 0.7063` USD;
- `2B`: `(0.5017 + 0.6517)/2 = 0.5767` USD;
- `3A`: `(1.7359 + 1.8859)/2 = 1.8109` USD;
- `3A - 2B = 1.2342` USD;
- `3A - 2A = 1.1046` USD.

## Итог

`2B` — recurring-cost minimum, `2A` — implementation-burden minimum и стоит примерно на 13 центов дороже, `3A` — margin maximum с примерно $0.95…1.25 premium over `2A`, третьим update target и открытым qty-500 allocation gate.

Snapshot и burden model получают статус **«Проведено ревью»**. Открытых предложений владельцу этот шаг не создаёт: следующий вопрос допустим только как единый atomic package, где cost сравнивается с pins/timing/power/RF/update/recovery одновременно.
