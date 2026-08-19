# REV-0002AL — optional external IMU decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Решение: [`DEC-0037`](../decisions/DEC-0037-optional-external-imu-measurement-pose.md)
- Requirement: [`REQ-IMU-0001`](../requirements/REQ-IMU-0001-external-measurement-pose.md)

## Проверка

| Проверка | Результат |
|---|---|
| Owner selected option A | да |
| Base IMU/magnetometer added | no |
| U095 frozen as permanent silicon | no; baseline only |
| Indexed mount/axis transform required | да |
| Six-axis called absolute heading | no |
| IMU called RF bearing/RSSI/distance | no |
| Missing accessory breaks RF/safety | no; metadata degrades only |
| Tamper/fall/gesture/destructive automation added | no |
| Hardware/firmware target and current EN/RU propagated | да |
| Release claimed complete | no; G3/G4/G7/G9/G11 gates explicit |

## Итог

`W-EXTRA-14` and `REQ-IMU-0001` receive **«Проведено ревью»** at the
product-requirement level. The next current-competitor delta is `W-EXTRA-15`,
physical text keyboard/product control archetype.
