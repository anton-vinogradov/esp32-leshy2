# AUD-0007 — haptic feedback product, mechanical and cost boundary

- Статус: **Проведено ревью; haptic отклонён `DEC-0036`**
- Дата snapshot: 2026-08-16
- Delta: `W-EXTRA-13`
- Предложение: [`IMP-0030`](../improvements/IMP-0030-haptic-feedback-placement.md)
- Finding: [`FND-0044`](../findings/FND-0044-external-vibrator-is-not-automatically-device-haptics.md)
- Решение: [`DEC-0036`](../decisions/DEC-0036-no-product-haptic.md)

## Пользовательский результат

Haptic нужен не как «мотор присутствует», а как различимая тактильная обратная
связь основного устройства при ожидаемом grip/pocket/mount use:

- короткое подтверждение local action/key press без взгляда на экран;
- тихое уведомление и различимые success/warning/error patterns;
- дополнительное подтверждение security/destructive ceremony;
- accessibility channel для ситуаций, где звук неудобен.

Haptic никогда не является единственным признаком TX, STOP, destructive action,
FIDO RP/operation или Controlled-Zone state. Critical state остаётся явно
видимым и, где требуется, слышимым.

## M5 U059 — что покрывает фактически

Current official Unit Vibrator `U059` стоит $2.95 и содержит N20 brushed ERM с
metal eccentric mass, low-side MOSFET, GPIO/PWM control и LEGO-compatible holes.
Размер 32×24×8 mm, масса 10 g, комплектный HY2.0 cable — 20 cm. Official
operating point указан как 5 V/424.35 mA при 10 kHz, 50% PWM. Reverse braking
не поддерживается; start/stop зависит от mechanical inertia.

Это хороший дешёвый external vibration source и prototype reference. Но сам
разъём не передаёт вибрацию: свободно висящий Unit даёт feedback модулю/кабелю,
а не гарантированно руке через основной enclosure. Полноценный external haptic
profile требует жёсткого retained mount с проверенным mechanical coupling.

Поэтому прежняя строка `AUD-0005` исправлена с **full** на **partial until
mounted**. At that review point direct official-result coverage changed from
6/18 to 5/18 while full+partial remained 8/18 and 9/18 with custom iButton.
After `DEC-0036` removes haptic, `DEC-0038` removes the physical-keyboard profile
and `DEC-0039` removes generic host from the live denominator, with `FND-0045`
correcting external-IMU framing, current figures are 3/15 full, 6/15 partial and
7/15 with custom iButton. The two-tier conclusion does not change.

## Placement alternatives

### Integrated actuator

Даёт наиболее стабильный felt result и не занимает Unit port. G3/G4 должны
сравнить как минимум:

- low-cost ERM + protected switch/driver: minimum BOM and easy PWM, but slower
  edges, brush wear, more acoustic/EMI risk and weak pattern precision;
- LRA + closed-loop driver: faster/crisper patterns, braking/resonance tracking,
  lower brush EMI and potentially lower energy per event, but higher component
  cost and more calibration/mounting/driver work.

Current-production haptic drivers such as TI DRV2624/DRV2625 demonstrate the
LRA/ERM closed-loop path; DRV2605L remains useful evidence. No exact driver or
actuator is selected before whole-device alternatives and BOM qualification.

### External mechanically coupled Unit

Avoids actuator/driver in base BOM and follows `DEC-0034` M5-first. Product
design must include an optional rigid clip/rail/back shell location that:

- transmits vibration into the enclosure under expected grip/pocket use;
- retains the 32×24×8 mm/10 g Unit and protects the cable;
- does not collide with U214, antennas, controls or service access;
- prevents the eccentric mass or housing from rattling against the enclosure;
- budgets short 5 V current pulses and does not brown out other accessories.

Without that mount it is an external alerting motor, not reviewed device haptic.

## Cross-feature effects

- vibration corrupts IMU samples and calibration if `W-EXTRA-14` is accepted;
- brushed ERM can add acoustic and electromagnetic noise during mic/audio/RF
  measurement;
- mechanical resonance changes with enclosure, battery, grip and mounted
  accessories;
- a motor must default off after reset/update/brownout and have bounded maximum
  continuous runtime;
- user needs strength, pattern, quiet/off and accessibility controls;
- safety-critical feedback cannot disappear merely because haptic is disabled.

Firmware therefore requires arbitration/blanking windows for recording,
measurement and future IMU use, plus explicit pattern semantics rather than
arbitrary app-controlled continuous PWM.

## Cost interpretation

Haptic is a newly proposed scope item, not an already accepted function, so
adding it to the base is not «zero-loss cost». The external route keeps base
BOM unchanged and moves current retail module/mount cost to the kit that needs
it. Integrated haptic can still win later if G3 shows that frequent eyes-free
interaction materially improves the primary product and the full cost/space/
power burden is justified.

## Sources

- [M5Stack Unit Vibrator U059 documentation](https://docs.m5stack.com/en/unit/vibrator)
- [M5Stack official U059 store page](https://shop.m5stack.com/products/vibration-motor-unit)
- [TI DRV2605L product and datasheet](https://www.ti.com/product/DRV2605L)
- [TI haptic implementation considerations](https://www.ti.com/lit/an/sloa207a/sloa207a.pdf)
- [TI DRV2624 current product page](https://www.ti.com/product/DRV2624)
- [TI DRV2625 current product page](https://www.ti.com/product/DRV2625)

## Audit gate

- [x] user result separated from motor presence;
- [x] current M5 module, price, electrical and mechanical facts checked;
- [x] prior M5 coverage overcount corrected;
- [x] integrated ERM/LRA and external coupled alternatives retained;
- [x] cost, power, acoustic/RF/IMU and safety interactions identified;
- [x] owner selected C in `DEC-0036`;
- [x] no `REQ-HAP-*` created because haptic is outside product scope.
