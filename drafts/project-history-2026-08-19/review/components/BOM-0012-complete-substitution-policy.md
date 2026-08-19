# BOM-0012 — complete substitution/no-silent-replacement policy

- Статус: **проведено ревью policy coverage 187/187; exact alternate qualification stays per-line**
- Дата: 2026-08-19
- Decision: [`DEC-0104`](../decisions/DEC-0104-complete-no-silent-substitution-policy.md)
- Review: [`REV-0005BK`](../reviews/REV-0005BK-substitution-policy-propagation.md)
- Generated review: [`G2F-3I-target-bom-review`](generated/G2F-3I-target-bom-review.md)

## Что закрыто

Каждая из 187 purchase lines имеет один machine-validated disposition class.
CSV содержит class id рядом с exact first-target MPN. Generated Markdown
раскрывает узкими `<details>`-карточками полный список строк, equivalence
envelope и обязательные повторные проверки.

| Class | Lines | Правило |
|---|---:|---|
| `SUB-RF` | 28 | no drop-in до RF/clock requalification |
| `SUB-PWR-PASSIVE` | 16 | converter/rail stability, loss, thermal and EMI requalification |
| `SUB-CTRL-PASSIVE` | 56 | controlled parametric substitution с worst-placement calculation/HIL |
| `SUB-DISCRETE-PROT` | 13 | pin/polarity/off-state/fault and ESD/signal requalification |
| `SUB-LOGIC-ANALOG` | 26 | exact truth/default/Ioff/analog/interface equivalence and HIL |
| `SUB-PWR-SAFETY` | 17 | complete owning safety/power subblock reopen |
| `SUB-COMPUTE-RF` | 15 | owner/pin/firmware/recovery/RF full requalification |
| `SUB-MECH-OPTICAL` | 16 | received-sample mate/fit/human/environmental qualification |

## Что это не означает

- `187/187` не означает наличие 187 second-source MPN;
- class не разрешает фабрике менять производителя только по value/footprint;
- «no worse» проверяется по всем placements одной MPN-line, а не по самому
  простому применению;
- RF, safety, battery, display and compute first targets remain locked until a
  named alternate passes the specified evidence.

## Cost-down use

Следующий cost pass может сначала искать one-stop/volume savings внутри
`SUB-CTRL-PASSIVE` and `SUB-PWR-PASSIVE`, но экономия принимается только после
envelope/requalification. Это позволяет уменьшать стоимость без скрытого
ослабления безопасности, RF performance, автономности или serviceability.
