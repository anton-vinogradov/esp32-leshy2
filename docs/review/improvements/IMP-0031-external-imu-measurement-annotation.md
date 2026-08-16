# IMP-0031 — optional external IMU for measurement-pose annotation

- Статус: **⚠️ Требуется решение владельца**
- Дата: 2026-08-16
- Delta: `W-EXTRA-14`
- Evidence: [`AUD-0008`](../audits/AUD-0008-imu-instrument-value-and-placement.md)
- Finding: [`FND-0045`](../findings/FND-0045-external-six-axis-imu-is-not-device-heading-or-rf-bearing.md)

## Контекст

В отличие от haptic, IMU может поддержать основной instrument scope: отметить,
что RF measurement window проходил при стабильном/известном наклоне или во
время управляемого поворота. Это улучшает воспроизводимость nRF hunt, scan и
logging, но не измеряет RF direction.

Current M5 U095 — доступный $7.50 6-axis Port-A Unit. Он не даёт absolute yaw,
не выводит interrupt через HY2.0 и становится датчиком pose самого Leshy2 только
с жёстким keyed/indexed mount. Более функциональный U171 с magnetometer уже EOL.

## Options

### A — optional external measurement-pose profile

Принять IMU только как optional passive instrument accessory через уже принятый
M5 Port A. U095 — current prototype/catalog baseline, но production profile не
замораживает MPU6886 навсегда. G3 проектирует общий rigid indexed attachment;
requirement ограничивается motion flag, pitch/roll and short-term relative
rotation with timestamps/calibration/axis transform.

- Плюсы: нет sensor в base BOM; есть конкретная польза для receiver/analyzer
  records; можно обновить exact accessory без переделки main board.
- Минусы: $7.50 module + mount/NRE; порт занят; нет absolute heading; polling
  and cable/mount add time-alignment and mechanical error.

### B — integrated base 6-axis IMU

Принять measurement pose как обязательный result каждого устройства и выбрать
current-production sensor only after G3/G4 whole-product comparison.

- Плюсы: фиксированный axis transform, более точная синхронизация, нет внешнего
  кабеля/порта.
- Минусы: base BOM/area/power/calibration/HIL растут для каждого unit; это
  преждевременно, пока ценность pose metadata не доказана; magnetometer всё
  равно не следует добавлять молча.

### C — no IMU product support

Не вводить IMU profile/driver/mount; использовать manual level/turn procedure
and operator markers.

- Плюс: нулевой hardware/software/mechanical burden.
- Минус: RF records не получают автоматического motion/pose validity context.

## ⚠️ Recommendation

**A**. Это минимальный способ получить именно instrument benefit без роста base
BOM. Acceptance не обещает heading, direction finding, tamper/fall detection or
gesture UX. Любой magnetometer/absolute-heading result остаётся отдельным
future proposal с magnetic-placement HIL.

## Acceptance boundary for A

- optional, passive Main-level accessory; raw RF function works without it;
- rigid keyed/indexed mount and versioned sensor→enclosure→antenna transform;
- current U095 baseline plus lifecycle-qualified replaceability;
- monotonic timestamp/sample age, calibration and motion-quality in every
  associated record;
- only pitch/roll, raw accel/gyro and relative angular delta are claimed;
- no RF bearing/dBm/distance, absolute yaw, tamper, fall or destructive action;
- missing/removal/bus fault invalidates pose metadata, never RF data or safety;
- privacy-visible capture/export toggle and bounded retention;
- exact I²C/power/hot-plug/address sharing follows `REQ-EXT-0001`.
