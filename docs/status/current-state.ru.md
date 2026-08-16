# Аппаратная часть Leshy2 — текущее состояние проработки

> Снимок: 2026-08-16. Здесь указана доказанная зрелость. Образ готового
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

- текущий вопрос: [`IMP-0027/W-EXTRA-11`](../review/improvements/IMP-0027-ibutton-one-wire-profile.md) — iButton/1-Wire и способ контакта;
- затем по одному: `W-EXTRA-12` U2F/FIDO, `13` haptic, `14` IMU, `15`
  physical keyboard, `16` high-speed USB host и `17` 6 GHz/Wi-Fi 6E.

Ни один пункт не добавлен в target до решения владельца.

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
  GNSS/LoRa/NFC и их safety/evidence boundaries;
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

Сначала [`AUD-0004`](../review/audits/AUD-0004-current-competitor-capability-gap.md)
закрывает семь competitor-delta решений по одному. Параллельный G3 research
отталкивается от уже проверенных capabilities и задаёт физический
продукт без выбора electronics: form factor/use posture, control/connector
surfaces, display, battery/charging, external-module attachment, antenna
volumes, service access, environment/repairability и target cost. Только после
нового G2 review и owner review G3 строятся complete architecture alternatives.
