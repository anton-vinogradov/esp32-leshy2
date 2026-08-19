# REV-0005BQ — power/UI/RF cost-evidence propagation

Статус: **проведено ревью пятой партии; full I8 remains open**.

| Проверка | Результат |
|---|---|
| exact identity | pass: nine numeric records and one gate resolve to current exact purchase-line MPNs |
| comparable basis | pass: USD quantity-100 published tiers; Si4732 explicitly scoped to the selected PCBA supplier |
| missing-price honesty | pass: new TPUL2G223 records an RFQ gate instead of a reel-price estimate |
| arithmetic | pass: 61/187 lines, 623/857 placements, base partial subtotal USD 109.8573 |
| delta | pass: +9 lines, +9 placements and +USD 7.6368 versus the reviewed fourth batch |
| open residue | pass: 126 prices remain; six have explicit non-numeric gates |
| architecture/diagram | unchanged: no device, instance, role, pin, net, rail or diagram node changed |
| regression | pass: generated-artifact check, 69 architecture tests and whitespace check |

## Verdict

[`BOM-0017`](../components/BOM-0017-power-ui-rf-cost-evidence.md) receives
**«Проведено ревью»**. The batch advances comparable component-material cost
coverage without treating factory-only stock, absent quotes or full-reel MOQ as
interchangeable evidence.

I8 remains open for 126 prices, standalone display sourcing, four
uninstantiated physical families, specific alternate qualification and full
factory COGS.

`BOM-0023/REV-0005BW` preserve this fifth-batch checkpoint and advance current
coverage to 148/187 lines / 802 placements / USD 150.1783 partial base subtotal.
