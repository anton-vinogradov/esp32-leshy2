# REV-0005BM — second cost-evidence and explicit-gate propagation

Статус: **проведено ревью второй партии; full I8 remains open**.

| Проверка | Результат |
|---|---|
| exact identity | pass: all eight new numeric prices resolve to the current exact purchase-line MPN |
| comparable basis | pass: published USD cut-tape quantity-100 tiers only |
| current correction | pass: current TDK C1608X7R1C105K080AC tier is USD 0.0392; the stale USD 0.0404 observation was not committed |
| arithmetic | pass: 23/187 lines, 440/857 placements, base partial subtotal USD 68.8226 |
| missing-cost honesty | pass: five researched lines have explicit gates and no numeric value |
| mutual exclusion | pass: validator rejects any device carrying both `cost` and `cost_gate` |
| gate provenance | pass: status/reason/HTTPS source/date are mandatory; invalid status/source/date regressions fail |
| scope | pass: U214 remains optional and cells remain regional; neither enters the base subtotal |
| generated output | pass: narrow-screen Markdown and CSV expose gate fields separately from prices |
| function/pins/diagram | unchanged; no physical device, signal, pin, rail or role changed |
| regression | pass: generated-artifact check and 69 hardware architecture tests |

## Verdict

`DEC-0106` and `BOM-0014` receive **«Проведено ревью»**. The second batch
covers 418 additional placements without inventing RFQ numbers. I8 does not
receive final review: 164 price lines, one standalone orderability line, four
uninstantiated physical families, specific alternate qualification and full
factory COGS remain open.

`BOM-0017/REV-0005BQ` preserve this reviewed second-batch checkpoint and
advance the current snapshot to 61/187 lines / 623 placements / USD 109.8573
partial base subtotal.
