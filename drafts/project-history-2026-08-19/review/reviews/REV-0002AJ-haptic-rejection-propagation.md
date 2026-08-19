# REV-0002AJ — распространение отказа от product haptic

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Решение: [`DEC-0036`](../decisions/DEC-0036-no-product-haptic.md)

## Проверка

| Проверка | Результат |
|---|---|
| Owner selected option C | да |
| Motor/haptic removed from target promises | да; never entered target README |
| Special U059 profile/mount/power/HIL retained accidentally | no; stale 0.5 A Unit-port floor derived from U059 removed from `AUD-0005` |
| Generic M5 Port-B capability removed | no; remains generic only |
| Prior M5 coverage correction lost | no; catalog fact retained |
| Base BOM/resource demand increased | no |
| Hardware/firmware current state and delta queue propagated | да |

## Итог

`W-EXTRA-13` receives `rejected-by-owner` and **«Проведено ревью»**. No
`REQ-HAP-*` is created because there is no product requirement. G2 continues
with `W-EXTRA-14` IMU/orientation, evaluated only against the clarified core
instrument use cases.
