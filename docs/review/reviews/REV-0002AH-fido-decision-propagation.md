# REV-0002AH — распространение решения open personal FIDO authenticator

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Решение: [`DEC-0035`](../decisions/DEC-0035-open-personal-fido-authenticator.md)
- Requirement: [`REQ-FIDO-0001`](../requirements/REQ-FIDO-0001-open-personal-authenticator.md)

## Проверка

| Проверка | Результат |
|---|---|
| Option A recorded | да |
| Modern CTAP target and U2F compatibility separated | да |
| Main function isolated from Lab/CZ | да; exclusive mode |
| User presence and PIN separated | да |
| General backup clones credentials | no; explicitly prohibited |
| Open firmware mistaken for certified/hardware-backed | no |
| Locked device or secure element forced | no |
| Target USB owner/MCU/pins selected prematurely | no |
| Hardware/firmware and target/current EN/RU propagated | да |
| Release claimed complete | no; G3/G4/G7/G9/G11 gates explicit |

## Итог

`W-EXTRA-12` и `REQ-FIDO-0001` получают статус **«Проведено ревью»** на
product-requirement level. Реализация и assurance claims остаются
неподтверждёнными до downstream evidence. Следующий current competitor delta —
`W-EXTRA-13` haptic feedback.

