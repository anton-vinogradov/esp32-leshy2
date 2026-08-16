# FND-0044 — an external vibrator is not automatically on-device haptics

- Статус: **Coverage исправлено; product disposition открыт `IMP-0030`**
- Дата: 2026-08-16
- Обнаружено: [`AUD-0007`](../audits/AUD-0007-haptic-product-mechanical-cost.md)
- Затрагивает: `W-EXTRA-13`, `AUD-0005`, M5 coverage, G3 mechanics/power/UX

## Несоответствие

`AUD-0005` засчитал официальный M5 U059 как полное external haptic coverage.
Он действительно является готовым управляемым vibration source, но в штатном
комплекте соединяется 20 cm кабелем. Без жёсткого крепления и mechanical
coupling модуль не гарантирует тактильную отдачу через основной enclosure.

## Исправление

- U059 меняется с `full` на `partial until mechanically coupled`;
- direct M5 product matches: 6/18 → 5/18 = 27.8%;
- full+partial остаётся 8/18 = 44.4%, with custom iButton 9/18 = 50%;
- external haptic acceptance requires a retained/coupled mount, power and
  interference HIL;
- dangling Unit remains a remote vibration alert, not device-haptic proof.

## Exit criteria

- owner decides [`IMP-0030`](../improvements/IMP-0030-haptic-feedback-placement.md);
- G3 models enclosure coupling/retention and simultaneous accessory conflicts;
- G4 compares complete base/external implementations at equal user result;
- G11 measures felt response across grip/pocket/mount, noise, power/fault and
  future IMU interference.

