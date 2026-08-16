# Аппаратная часть Leshy2 — текущее состояние проработки

> Снимок: 2026-08-17. Здесь указана доказанная зрелость. Образ готового
> продукта — в [целевом hardware README](../../README.ru.md), software — в
> [целевом firmware README](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md).

- Канонические evidence: [журнал ревью](../review/README.md)
- English version: [current-state.md](current-state.md)
- Исправленная gate chain: [`FLOW-0001`](../review/architecture/FLOW-0001-product-to-cad-gates.md)

## Ход ревью

| Gate | Состояние |
|---|---|
| 0. Review baseline | Проведено ревью |
| 1. Product intent и safety/legal boundaries | Проведено ревью |
| 2. Capabilities, exclusions, concurrency/failure needs | **Требуется повторное ревью**: прежние 125 leaves сохранены, competitor delta открыт (`FND-0040`) |
| 3. Target physical/product design | Research активен; final review ждёт закрытия этапа 2 |
| 4–6. Whole-device alternatives, optimality и conceptual co-design | Не начаты в исправленном процессе |
| 7. Atomic architecture | **Переоткрыта** решением `DEC-0032` |
| 8. Components/BOM | Заблокирован; прежние evidence только candidate/reference |
| 9. Electrical/CAD/firmware architecture | Заблокирован; активного canonical KiCad нет |
| 10–11. PCB, fabrication и bring-up | Не начаты |

Каноническая таблица — [`stages.md`](../review/stages.md).

## ⚠️ Открытые competitor-delta предложения

- `W-EXTRA-11` закрыт: [`DEC-0033/REQ-IBTN-0001`](../review/decisions/DEC-0033-external-m5-ibutton-profile.md)
  принимает внешний пассивный M5-style Port-B iButton adapter без base pad;
- infrastructure закрыт [`DEC-0034/REQ-EXT-0001`](../review/decisions/DEC-0034-m5-first-two-tier-expansion.md): M5-first Unit/Cap плюс отдельный high-throughput class, без native M5-Bus;
- former `W-EXTRA-12` FIDO acceptance удалён из target решением [`DEC-0039`](../review/decisions/DEC-0039-radio-key-scope-correction.md);
- `W-EXTRA-13` закрыт [`DEC-0036`](../review/decisions/DEC-0036-no-product-haptic.md): в продукте нет haptic, мотора, специального профиля или mount;
- `W-EXTRA-14` закрыт [`DEC-0037`](../review/decisions/DEC-0037-optional-external-imu-measurement-pose.md)/[`REQ-IMU-0001`](../review/requirements/REQ-IMU-0001-external-measurement-pose.md);
- `W-EXTRA-15` закрыт [`DEC-0038`](../review/decisions/DEC-0038-phone-assisted-text-no-integrated-keyboard.md): no integrated keyboard, bounded phone-assisted text;
- `W-EXTRA-16` generic High-Speed USB host rejected `DEC-0039`; остаётся только RF-derived transport;
- `W-EXTRA-17` 6 GHz/Wi-Fi 6E полностью отклонён `DEC-0040`; принятые
  автономные 2.4/5 GHz остаются без изменений.

`REV-0002AS` закрывает повторное G2 review. Активен G3 target product design.

## Что остаётся проверенным

- all-in-one автономный field-product, акт о ненападении и модель
  Main/Lab/Controlled Zone;
- консервативные TX defaults, явный выбор максимума, hard STOP без automatic
  re-arm и отдельное actual-TX evidence;
- полный self-review 125 wishlist leaves и правило снижения стоимости без потерь;
- три полнофункциональных nRF24 с одновременным приёмом;
- требования обычных Wi-Fi 2.4/5 ГГц, IEEE 802.15.4, native BLE и
  Wi-Fi 2.4/ESP-NOW;
- packet Sub-GHz, broadcast receive, analog voice, audio, IR, внешние
  GNSS/LoRa/NFC, внешний iButton/1-Wire adapter и их safety/evidence boundaries;
- open owner-controlled signed updates и независимые programming/recovery/
  diagnostics каждого в итоге выбранного programmable chip.

Это входы продукта. Exact MCU/module ownership, pins, buses, board count,
connectors, parts и enclosure не приняты.

## Завершённое исправление

[`FND-0039`](../review/findings/FND-0039-architecture-frozen-before-product-design.md)
зафиксировал, что прежняя цепочка пропустила target physical design,
whole-product optimality и conceptual placement. Владелец выбрал вариант A в
[`DEC-0032`](../review/decisions/DEC-0032-reopen-product-design-before-cad.md).

Последствия:

- `DEC-0028/PKG-0001/SYN-3A` — historical candidate/reference, а не target;
- C5 revision, compute ownership, pin и three-domain service studies являются
  только условными candidate facts;
- прежняя active C-001…005 KiCad library вместе с CI сохранена в
  [`premature-compute-cad-2026-08-16`](../../drafts/premature-compute-cad-2026-08-16/README.md);
- прерванный до коммита C-006 experiment отмечен как discarded в
  [`premature-service-cad-2026-08-16`](../../drafts/premature-service-cad-2026-08-16/README.md), без ложного обещания воспроизводимого snapshot;
- active [`hardware/kicad`](../../hardware/kicad/README.md) содержит только
  upstream gate, без symbols, schematic или PCB.

`REV-0004H` проверяет это исправление, но не новый product design.

## Следующий активный артефакт

[`AUD-0005`](../review/audits/AUD-0005-m5-expansion-ecosystem-coverage.md)
провёл ревью M5 ecosystem: после исключения rejected haptic, keyboard и generic
host profiles из live denominator и исправления external IMU на partial
M5-only закрывает 20.0% relevant classes полностью и 46.7% с partial/custom
iButton, поэтому 90%
требует отдельного
high-speed tier, принятого `DEC-0034`.
[`AUD-0004`](../review/audits/AUD-0004-current-competitor-capability-gap.md)
теперь закрывает delta по одному. `AUD-0007` проверил haptic и исправил
external-module coverage; `DEC-0036/REV-0002AJ` исключают его из product scope.
[`AUD-0008`](../review/audits/AUD-0008-imu-instrument-value-and-placement.md)
и `DEC-0037/REQ-IMU-0001` закрывают `W-EXTRA-14` как optional external
measurement-pose profile. [`AUD-0009`](../review/audits/AUD-0009-physical-keyboard-product-archetype.md)
и `DEC-0038/REV-0002AN` закрывают `W-EXTRA-15`: у base нет permanent keyboard,
а bounded phone-assisted text не становится local authority.
`AUD-0010/DEC-0039/REV-0002AP` закрывают `W-EXTRA-16`, не удаляя transport,
который позже может вывести конкретный RF/SDR profile. `AUD-0011` подтверждает,
что другое active base hardware не оправдано unrelated functionality; BadUSB
остаётся optional software-only exception.
Параллельный G3 research отталкивается от уже проверенных capabilities и задаёт физический
продукт без выбора electronics: form factor/use posture, control/connector
surfaces, display, battery/charging, external-module attachment, antenna
volumes, service access, environment/repairability и target cost. Только после
нового G2 review и owner review G3 строятся complete architecture alternatives.
