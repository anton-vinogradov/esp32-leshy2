# REV-0005BL — first cost-evidence propagation

Статус: **проведено ревью первой партии; full cost coverage remains open**.

| Проверка | Результат |
|---|---|
| exact identity | pass: all 15 prices belong to current purchase-line MPNs |
| comparable basis | pass: USD purchase quantity 100; `1+` flat-price exception explicitly named only for SC1512-A4 |
| provenance | pass: every price has dated HTTPS published source and price-break wording |
| incomplete evidence | pass: missing price stays blank, never zero |
| arithmetic | pass: 15/187 lines, 22/857 placements, base partial subtotal USD 57.2502 |
| scope | pass: no optional U214 or regional cell-kit value is merged into the current base subtotal |
| generated Markdown | pass: narrow-screen details expose unit, line subtotal, basis, source and date |
| CSV | pass: eight explicit cost columns added without dropping quantity/placement/substitution data |
| function/pins/diagram | unchanged; this batch is procurement metadata only |
| regression | pass: generated-artifact check and 68 hardware architecture tests, including invalid currency/quantity/price/source/date rejection |

## Verdict

`DEC-0105` cost-evidence contract and the first 15-line batch receive
«Проведено ревью». I8 does not: 172 purchase lines, four uninstantiated
physical families, standalone display sourcing and complete factory COGS
remain open.
