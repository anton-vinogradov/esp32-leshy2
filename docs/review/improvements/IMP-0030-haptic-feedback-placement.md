# ⚠️ IMP-0030 — haptic feedback placement and product scope

- Статус: **Предложение; требуется решение владельца**
- Дата: 2026-08-16
- Delta: `W-EXTRA-13`
- Evidence: [`AUD-0007`](../audits/AUD-0007-haptic-product-mechanical-cost.md)
- Finding: [`FND-0044`](../findings/FND-0044-external-vibrator-is-not-automatically-device-haptics.md)

## Контекст

Leshy2 уже имеет display/audio/LED, но не tactile channel. Haptic полезен для
eyes-free confirmation, pocket/quiet alerts and accessibility, однако не должен
становиться единственным safety indicator.

M5 U059 сохраняет base BOM, стоит $2.95 retail и подходит M5-first strategy,
но требует жёсткого крепления к enclosure: висящий на cable motor не равен
ощутимой отдаче корпуса. Integrated actuator лучше по UX, но добавляет новый
BOM/space/power/mechanical/interference burden.

## Options

### A — integrated on-device haptic

Принять tactile feedback как base product result. G3/G4 сравнят ERM и LRA,
точный actuator/driver выбирается только вместе с enclosure and architecture.

- Плюсы: гарантируемый coupling, свободный Unit port, лучший everyday UX.
- Минусы: base BOM/assembly/space/power растут; vibration влияет на mic, future
  IMU and sensitive measurements.

### B — optional mechanically coupled M5 haptic

Принять haptic как optional profile через U059/compatible Unit и обязательный
retained mount/clip that transfers vibration to Leshy2 enclosure. Base actuator
не ставить. Dangling mode честно называется remote vibration alert.

- Плюсы: base BOM не растёт; готовый $2.95 module; согласуется с M5-first и
  позволяет проверить реальную ценность до интеграции.
- Минусы: занимает Unit surface, требует 5 V pulse budget and mount; крупнее,
  шумнее и медленнее хорошего integrated LRA; haptic отсутствует без accessory.

### C — no haptic

Оставить visual/audio feedback и не вводить motor/mount/profile.

- Плюс: нулевой cost/power/mechanical burden.
- Минусы: нет tactile accessibility/quiet/pocket channel.

## Recommendation

**B**. На текущем product-intent уровне haptic полезен, но ещё не доказан как
настолько частый core interaction, чтобы увеличивать каждую базу. Coupled U059
сохраняет результат и даёт измеряемый field prototype; G3 может переоткрыть
integrated LRA только если whole-product UX score оправдает постоянный BOM.

## Acceptance boundary for B

- exact external profile and rigid retained/coupled mount;
- felt-pattern acceptance across grip/pocket/mount, not motor-spin evidence;
- bounded pulse/current/thermal/fault behavior and default-off reset state;
- quiet/off/strength/accessibility controls;
- haptic supplements but never replaces visible critical state;
- audio/RF/measurement and future IMU arbitration/blanking;
- base, field-kit and maximum-kit costs remain separate.

