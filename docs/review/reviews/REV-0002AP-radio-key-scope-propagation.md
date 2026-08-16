# REV-0002AP — radio/key mission scope propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-17
- Решение: [`DEC-0039`](../decisions/DEC-0039-radio-key-scope-correction.md)
- Requirement: [`REQ-SCOPE-0001`](../requirements/REQ-SCOPE-0001-radio-key-product-boundary.md)

## Проверка

| Проверка | Результат |
|---|---|
| Core radio/communication/key mission explicit | да |
| Generic High-Speed USB host still accepted | no |
| Concrete RF high-throughput transport silently deleted | no; derived later |
| Personal FIDO remains in target/architecture gates | no; historical only |
| BadUSB claimed zero software/test cost | no |
| BadUSB adds base hardware or architecture score | no |
| Product USB service/recovery accidentally removed | no |
| M5 coverage denominator corrected | да |
| Hardware/firmware target and current EN/RU propagated | да |
| Exact chip/connector/pin selected | no |

## Итог

Scope correction receives **«Проведено ревью»**. `W-EXTRA-12` and
`W-EXTRA-16` are closed under `DEC-0039`; the only remaining current-competitor
delta is the radio question `W-EXTRA-17`, 6 GHz/Wi-Fi 6E.
