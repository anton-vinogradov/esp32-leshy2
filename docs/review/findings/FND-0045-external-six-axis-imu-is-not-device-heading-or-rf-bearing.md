# FND-0045 — external 6-axis IMU is not automatically device heading or RF bearing

- Статус: **Исправление внесено; product boundary закрыт `DEC-0037`**
- Дата: 2026-08-16
- Обнаружено: [`AUD-0008`](../audits/AUD-0008-imu-instrument-value-and-placement.md)
- Затрагивает: `W-EXTRA-14`, `AUD-0005`, M5 coverage, nRF hunt records, G3 mechanics

## Несоответствие

`AUD-0005` засчитал M5 U095 как полное внешнее покрытие IMU/orientation. Unit
действительно измеряет acceleration и angular rate собственного sensor frame,
но штатно подключён кабелем. Без жёсткой индексированной фиксации его pose не
определяет pose корпуса или трёх antenna sectors Leshy2.

Кроме того, U095 — 6-axis accel+gyro. Он даёт tilt/relative motion, но не
absolute compass heading. Ни внешний, ни интегрированный IMU сам по себе не
превращает binary nRF24 RPD comparison в RF bearing/azimuth.

## Исправление

- U095 меняется с `full` на `partial until rigidly indexed to device frame`;
- after haptic rejection this finding produced a 17-class denominator; later
  `DEC-0038` removes the keyboard profile and makes the current denominator 16;
- current official direct result after both decisions: 3/16 = 18.8%;
- full+partial: 6/16 = 37.5%; with custom iButton: 7/16 = 43.8%;
- external pose profile requires mount ID, axis transform, calibration,
  timestamp/sample-age and motion-validity;
- absolute heading remains a separate magnetometer/GNSS-reference question;
- RF UI/export may use IMU only as contextual pose metadata.

## Exit criteria

- [x] M5 coverage corrected without changing `DEC-0034` two-tier conclusion;
- [x] current U095 and EOL U171 lifecycle distinction recorded;
- [x] 6-axis/yaw/RF-bearing claims bounded;
- [x] owner selected optional external profile through `DEC-0037`;
- G3 defines indexed mechanics and G4 compares exact accessory/base
  implementations; G11 verifies transforms, calibration, time alignment and
  interference.
