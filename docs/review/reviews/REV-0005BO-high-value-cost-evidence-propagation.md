# REV-0005BO — high-value IC/RF cost-evidence propagation

Статус: **проведено ревью четвёртой партии; full I8 remains open**.

| Проверка | Результат |
|---|---|
| exact identity | pass: all 13 prices resolve to exact current purchase-line MPNs |
| comparable basis | pass: published USD quantity-100 cut-tape tiers only |
| arithmetic | pass: 52/187 lines, 614/857 placements, base partial subtotal USD 102.2205 |
| delta | pass: +13 lines, +36 placements and +USD 23.1545 versus the reviewed third batch |
| missing-cost honesty | pass: 135 lines remain unpriced; five retain explicit non-numeric gates |
| scope | pass: optional U214 and regional cells remain outside the base subtotal |
| function/pins/diagram | unchanged; no device, signal, contact, rail, pin or diagram node changed |
| regression | pass: generated-artifact check and 69 hardware architecture tests |

## Verdict

[`BOM-0016`](../components/BOM-0016-high-value-ic-rf-cost-evidence.md)
receives **«Проведено ревью»**. The higher-value batch materially improves the
partial subtotal without changing architecture or fabricating unavailable
quotes.

I8 remains open for 135 prices, one standalone orderability line, four
uninstantiated physical families, specific alternate qualification and full
factory COGS.

Subsequent `BOM-0020/REV-0005BT` preserve this fourth-batch checkpoint and
advance current coverage to 106/187 lines / 747 placements / USD 140.7642;
81 prices and nine explicit gates remain.
