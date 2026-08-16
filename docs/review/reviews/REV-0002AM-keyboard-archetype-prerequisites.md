# REV-0002AM — physical-keyboard archetype prerequisite review

- Статус: **Проведено ревью фактов; product-design disposition открыт**
- Дата: 2026-08-17
- Input: `W-EXTRA-15`, `REQ-SYS-0001`, `FLOW-0001`, current official products
- Outputs: `AUD-0009`, `FND-0046`, `IMP-0032`

## Проверка

| Проверка | Результат |
|---|---|
| Existing local autonomy/text capability preserved | да |
| Keyboard mistaken for missing capability | no; recognized as product archetype |
| Safety/field/text/development task classes separated | да |
| Keyboard assumed to replace STOP/PTT/BACK | no |
| Current compact/landscape/field/external references checked | да |
| Display/grip/RF/mechanics/cost assessed together | да |
| Legacy touch/encoder/button layout treated as target | no; corrected `FND-0046` |
| Exact UI component/pin map selected | no |
| Equal-capability G3/G5 comparison defined | да |
| Target README changed before decision | no |

## Result

Fact/prerequisite slice receives **«Проведено ревью»**. `W-EXTRA-15` remains
`needs-owner` through `IMP-0032`. Recommendation B moves the question to the
correct G3/G5 whole-product comparison without silently accepting or excluding
a permanent keyboard.
