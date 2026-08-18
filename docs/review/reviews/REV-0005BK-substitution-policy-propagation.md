# REV-0005BK — substitution-policy propagation

Статус: **проведено ревью; specific alternate qualification remains evidence-driven**.

| Проверка | Результат |
|---|---|
| corrected purchase input | pass: 857 placements / 187 lines after assembly-internal exclusion |
| completeness | pass: 187/187 lines have exactly one disposition class |
| overlap | pass: duplicate device membership rejected |
| stale/internal line | pass: non-purchase ST77922 membership rejected |
| omission | pass: any uncovered current purchase device rejects the candidate |
| class content | pass: every class has title, disposition, equivalence envelope, requalification and exact members |
| generated Markdown | pass: narrow details cards expose all class members and gates |
| CSV | pass: `alternate_policy_class` present on every row |
| function/diagram/firmware | unchanged |
| regression | pass: generated-artifact check and 67 hardware architecture tests, including omission/overlap/internal-member rejection |

## Verdict

I8 alternate/no-substitution **policy** coverage receives «Проведено ревью».
This prevents silent substitutions and enables structured cost-down/RFQ work;
it does not claim that an unnamed or untested alternate is qualified.
