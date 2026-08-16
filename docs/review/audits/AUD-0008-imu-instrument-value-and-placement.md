# AUD-0008 — IMU instrument value, placement and truthful measurement boundary

- Статус: **Проведено ревью фактов; product disposition открыт**
- Дата snapshot: 2026-08-16
- Delta: `W-EXTRA-14`
- Предложение: [`IMP-0031`](../improvements/IMP-0031-external-imu-measurement-annotation.md)
- Finding: [`FND-0045`](../findings/FND-0045-external-six-axis-imu-is-not-device-heading-or-rf-bearing.md)

## Какой результат полезен прибору

IMU имеет смысл для Leshy2 не как consumer gesture/fall sensor, а как источник
измерительной provenance во время scan/hunt/log sessions:

- отмечать, двигался ли прибор внутри RF measurement window;
- записывать pitch/roll и short-term angular delta, чтобы сравнивать измерения
  при воспроизводимом положении корпуса и антенн;
- сопровождать управляемый ручной поворот timestamps и motion-quality flags;
- помечать записи stale/invalid, если pose sample отсутствует, просрочен или
  движение вышло за принятый envelope.

Это поддерживает приём и анализ, но не создаёт новый RF measurement. IMU не
измеряет field strength, RSSI, distance, angle of arrival, VSWR или bearing.
Она знает только движение/положение sensor frame; связь с antenna frame должна
быть отдельно определена и проверена.

## Что даёт текущий M5 catalog

Актуальный официальный Unit Mini IMU `U095` стоит $7.50 и на момент snapshot
помечен `10+ In Stock`. Он содержит MPU6886: 3-axis accelerometer + 3-axis gyro,
I²C `0x68`, 24×24×8 mm, 3.2 g. HY2.0-4P Port-A выводит только `5V/GND/SDA/SCL`;
отдельный interrupt/timestamp signal на разъём не выведен. Поэтому профиль
подходит для polling-based pose annotation, но не для hard real-time trigger.

Официальный `U171` с BMI270+BMM150+BMP280 давал gyro/accel, magnetometer и
barometer, но теперь имеет статус EOL; M5 предлагает вместо него U095. Более
свежий BMI270 остаётся current-production silicon у Bosch, однако готового
актуального M5 Unit с BMI270+BMM150 на смену U171 каталог не показывает.
Поэтому U171 нельзя заморозить как production reference, а U095 следует считать
current catalog/prototype baseline, не вечным exact silicon requirement.

## Ограничения 6-axis

Accelerometer показывает gravity-derived tilt only when linear acceleration is
small enough. Gyro gives angular rate and short-term relative rotation, but its
integrated yaw drifts. NXP explicitly states that accelerometer-only orientation
cannot detect compass heading; absolute yaw needs an external reference such as
a magnetometer or suitable GNSS-derived heading while moving.

Magnetometer is not a free fix. It requires hard-/soft-iron calibration and is
sensitive to speaker magnets, enclosure magnets, ferromagnetic fasteners,
currents and nearby accessories. M5 itself warns that BMM150 readings are
disturbed by magnets. A future magnetometer profile therefore needs separate
placement/calibration/interference evidence and cannot be implied by accepting
a 6-axis U095 profile.

## Placement alternatives

### Integrated base IMU

The sensor-to-enclosure transform is fixed and samples can be tightly timestamped.
This is the strongest implementation if pose becomes a core measurement, but it
adds base BOM, PCB area, power, calibration, assembly strain/temperature risk,
firmware and HIL to every unit. An integrated magnetometer would additionally
sit close to audio, power and RF hardware and is not recommended without a
measured magnetic map.

### External M5 Unit

Keeps base BOM unchanged and reuses accepted Port A. It becomes device-pose
instrumentation only when held by a rigid, keyed/indexed mount with a versioned
axis transform to the enclosure/antenna frame. A Unit hanging on its cable is a
motion sensor for the cable/module, not evidence of Leshy2 antenna orientation.

The profile must record at least sensor/SKU/revision, mount ID, axis transform,
calibration state, monotonic timestamp/sample age, raw accel/gyro, derived
pitch/roll/relative rotation and motion-validity. Missing or invalid IMU data
must not suppress raw RF records; it only removes or invalidates pose metadata.

### No IMU

RF functions remain available with manual turn/level procedures and explicit
operator markers. This has zero hardware/software/mount burden, but removes an
automatic way to prove that compared measurement windows used a stable or known
physical pose.

## Safety, privacy and false automation

- passive pose sensing is Main-level, but capture/export must visibly state
  whether motion metadata is included;
- IMU must not silently trigger transmit, unlock Controlled Zone, erase secrets,
  claim tamper, or make a destructive/security decision;
- no fall/person tracking claim is accepted;
- RF UI/export must label pose as contextual metadata, never RF bearing;
- accessory removal, bus fault or stale sample degrades pose metadata only;
- exact I²C sharing/address collisions, power and hot-plug behavior remain
  governed by `REQ-EXT-0001`.

## Cost interpretation

`W-EXTRA-14` is a new optional result, not a preserved function. The external
route adds no sensor to base BOM, but is not zero-cost overall: current module
retail is $7.50 plus an indexed mount, driver, calibration flow and tests. The
integrated route is justified only if the pose metadata becomes mandatory for
a core measurement and beats the complete external implementation at G3/G4.

## Sources

- [M5Stack Unit Mini IMU U095 documentation](https://docs.m5stack.com/en/unit/imu)
- [M5Stack official U095 store page](https://shop.m5stack.com/products/6-axis-imu-unitmpu6886)
- [M5Stack U171 EOL store notice](https://shop.m5stack.com/products/6-dof-imu-pro-mini-unit-bmi270-bmm150-bmp280)
- [M5Stack U171 documentation and magnetic-interference warning](https://docs.m5stack.com/en/unit/IMU%20Pro%20Mini%20Unit)
- [Bosch BMI270 current product page](https://www.bosch-sensortec.com/en/products/motion-sensors/imus/bmi270)
- [NXP AN5021 orientation matrices](https://www.nxp.com/docs/en/application-note/AN5021.pdf)
- [NXP AN4248 tilt-compensated eCompass and hard-/soft-iron effects](https://www.nxp.com/docs/en/application-note/AN4248.pdf)

## Audit gate

- [x] instrument result separated from generic consumer sensing;
- [x] current M5 SKU, stock/price, dimensions, interface and lifecycle checked;
- [x] 6-axis tilt/relative rotation separated from absolute heading;
- [x] sensor frame separated from enclosure/antenna frame;
- [x] false RF bearing, tamper and safety automation excluded;
- [x] base, external and no-IMU alternatives compared at equal result;
- [x] prior M5 direct-coverage overcount identified and corrected;
- [ ] owner disposition through `IMP-0031`.
