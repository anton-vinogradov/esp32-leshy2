# DEC-0037 — optional external IMU measurement-pose profile

- Статус: **Принято владельцем; проведено ревью распространения**
- Дата: 2026-08-16
- Ответ владельца: **вариант A**
- Предложение: [`IMP-0031`](../improvements/IMP-0031-external-imu-measurement-annotation.md)
- Evidence: [`AUD-0008`](../audits/AUD-0008-imu-instrument-value-and-placement.md)
- Нормативный контракт: [`REQ-IMU-0001`](../requirements/REQ-IMU-0001-external-measurement-pose.md)

## Решение

1. Leshy2 поддерживает optional external IMU как passive Main-level instrument
   profile для motion/pose provenance в scan/hunt/log sessions.
2. Base device не получает обязательный IMU, magnetometer или связанный sensor
   BOM. Current M5 U095 — первый catalog/prototype baseline, но exact MPU6886
   не замораживается как production silicon.
3. Device-pose claim допустим только с жёстким keyed/indexed mount и versioned
   sensor→enclosure→antenna transform. Свободно висящий Unit даёт лишь собственный
   module pose.
4. Приняты только raw accel/gyro, pitch/roll, short-term relative rotation,
   motion/stability flag и их timestamp/quality/calibration metadata.
5. Не приняты absolute heading/yaw, RF bearing/azimuth/distance/RSSI/VSWR,
   tamper/fall/person tracking, gesture UX или IMU-triggered destructive/security
   actions.
6. Missing/stale/removed/faulted IMU invalidates pose metadata only; raw RF
   function and safety remain available.
7. Magnetometer or another absolute-heading source requires a new proposal,
   exact placement and magnetic-interference/calibration HIL.

## Последствия

- `W-EXTRA-14` закрыт как `accepted-external`;
- G3 must compare the indexed mount against other external surfaces and antenna
  geometry without reserving a base sensor;
- G4/G7 select exact accessory identity, electrical profile and time alignment;
- G11 validates transform, movement envelopes, sample age, removal/bus faults
  and truthful RF export semantics.
