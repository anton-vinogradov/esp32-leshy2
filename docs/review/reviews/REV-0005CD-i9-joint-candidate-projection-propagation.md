# REV-0005CD — I9 joint candidate-projection propagation

Статус: **проведено ревью I9 working-candidate paper scope**.

| Проверка | Результат |
|---|---|
| internal prerequisites | pass: I1…I8 have reviewed paper-scope outputs and explicit downstream reopen gates |
| pin/contact/resource accounting | pass: S3 `33/3/0`, C5 `14/6/1`, RP `48/0/0`, slow I/O `24/0/0`, UI I/O `7/1/0`; no collision or hidden free assignment |
| physical projection | pass: 858/858 architecture instances; one device per node; BOM boundary remains 857 supplied placements |
| abstract closure | pass: 970 occurrences / 59 unique labels; class counts `14 + 2 + 24 + 18 + 1`; zero missing, duplicate or stale labels |
| owner decisions | pass: zero unresolved decisions inside the working candidate; downstream product/optimality choice remains deliberately outside I9 |
| stale-stage repair | pass: XTAR/NTC/nRF cost evidence now points to G8/G11 rather than closed I8 |
| firmware boundary | pass: 19 runtime/landing regression tests preserve safety, RF, expansion, controls and recovery contracts |
| hardware regression | pass: generated-artifact check, 72 architecture tests and whitespace check |
| authorization boundary | pass: candidate handoff permits G3 only; G4…G8, KiCad and HIL claims remain unauthorized |

## Verdict

[`I9-0001`](../architecture/I9-0001-joint-candidate-paper-projection-review.md)
receives **«Проведено ревью»**. [`FND-0116`](../findings/FND-0116-i9-abstract-and-stage-labels-were-not-closed.md)
is fixed. The result is a joint internally consistent working candidate, not
the G7 atomic architecture.

Per `DEC-0058`, the paused integrated G3 product/mockup work may resume from
the reviewed candidate and existing legacy-layout input. Any physical conflict
reopens its owning G2F block before propagation. KiCad remains unauthorized.
