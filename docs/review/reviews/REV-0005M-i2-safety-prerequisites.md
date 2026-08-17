# REV-0005M — I2 safety prerequisites and option review

- Статус: **Проведено ревью пререквизитов; superseded by `DEC-0061/REV-0005O`**
- Дата: 2026-08-17
- Architecture: [`SAFE-0001`](../architecture/SAFE-0001-aon-stop-and-tx-evidence-options.md)
- Finding: [`FND-0071`](../findings/FND-0071-hard-stop-and-tx-evidence-coverage.md)
- Owner proposal: [`IMP-0050`](../improvements/IMP-0050-aon-stop-and-per-path-tx-evidence.md)

## Проверено

| Проверка | Результат |
|---|---|
| `I1` prerequisite | pass: `DEC-0059/REV-0005L`, three-domain recovery and links reviewed |
| STOP ownership | mismatch found and corrected in docs: RP `RUN` must join S3/C5 reset and all TX gates |
| release/re-arm behavior | non-programmable truth table derived; STOP dominates held re-arm and POR |
| loss of AON | no run command may result; per-output off-safe pulls and brownout HIL required |
| onboard TX inventory | seven RF paths plus one IR optical path enumerated |
| evidence gaps | 3×nRF and CC missing; existing four endpoints remain only abstract |
| RP pin budget | no new GPIO required: GPIO22 aggregate + local-I²C source mask |
| critical indication | hardware diode-isolated `ANY_TX` and STOP latch LED do not depend on I²C/UI |
| U214 boundary | base board cannot source-identify RF on a Cap-local antenna; unknown remains explicit |
| exact first targets | lifecycle/availability/spec range checked for latch, logic, detector, comparator, expander and photodiode candidates |
| cost-down | discrete BAT15 coupon is separable; shared/inferred evidence is not no-loss |
| HIL boundary | taps, matching, thresholds, latency, reverse current and faults remain explicitly assigned to I3/I6/HIL |

## Исправление по результатам ревью

`DEC-0024`, `IMP-0022`, `IMP-0010`, `FND-0007`, `RES-0001` and the relevant
`PWR-0001` scenario wording are amended to cover all three current compute
domains rather than the historical two-MCU wording. This is propagation of the
already-current architecture invariant, not an unapproved new feature.

## Почему этап ещё не закрыт

Владелец впоследствии принял `IMP-0050/A`. `SAFE-0002` документирует exact
fan-out/pulls/test points, а `REV-0005O` проверяет machine-source и
living-diagram propagation. Поэтому `I2` получил **«Проведено ревью»**; RF/IR
measured qualification остаётся named downstream `I6/HIL` gate.
