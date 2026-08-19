# FND-0044 — an external vibrator is not automatically on-device haptics

- Статус: **Coverage исправлено; product haptic отклонён `DEC-0036`**
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

- [x] owner selected no product haptic in [`DEC-0036`](../decisions/DEC-0036-no-product-haptic.md);
- [x] haptic mechanics/power/HIL obligations removed from the active product;
- [x] historical 6/18 → 5/18 correction retained; later live-denominator and
  external-IMU correction is recorded separately in `FND-0045`.

No G3/G4/G11 haptic work remains unless `DEC-0036` is explicitly reopened.
