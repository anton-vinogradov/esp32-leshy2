# FND-0045 — external 6-axis IMU is not automatically device heading or RF bearing

- Статус: **Исправление внесено; product disposition открыт**
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
- после отказа от haptic live denominator M5 audit: 17 external-hardware
  classes, не 18;
- current official direct result: 4/17 = 23.5%;
- full+partial: 7/17 = 41.2%; with custom iButton: 8/17 = 47.1%;
- external pose profile requires mount ID, axis transform, calibration,
  timestamp/sample-age and motion-validity;
- absolute heading remains a separate magnetometer/GNSS-reference question;
- RF UI/export may use IMU only as contextual pose metadata.

## Exit criteria

- [x] M5 coverage corrected without changing `DEC-0034` two-tier conclusion;
- [x] current U095 and EOL U171 lifecycle distinction recorded;
- [x] 6-axis/yaw/RF-bearing claims bounded;
- [ ] owner chooses product disposition through `IMP-0031`;
- if accepted, G3 defines indexed mechanics and G4 compares exact accessory/base
  implementations; G11 verifies transforms, calibration, time alignment and
  interference.
