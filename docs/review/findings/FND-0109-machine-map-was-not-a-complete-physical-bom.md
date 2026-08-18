# FND-0109 — machine map was not a complete physical BOM

- Статус: **обнаружено I8; coverage исправлен, строки закрываются**
- Дата: 2026-08-19
- Scope: `G2F-3I`, `INT-0001/I8`

## Несоответствие

До I8 количество `instances` ошибочно можно было принять за полный material
inventory. На самом деле 791 machine-instantiated placements дают 185
используемых MPN-линий, но за `abstract:*` и prose оставались физические
покупные элементы:

- 9 внешних SMA bodies;
- 5 RF cable/pigtail assemblies;
- rear Cap-Bus и native HY2.0-4P connector bodies;
- 8 отдельных actual-TX threshold/hysteresis networks;
- часть обязательной MAX17320 support circuit;
- 12 предметов внешнего antenna kit/variant.

Особенно существенен MAX17320: прежний текст I3 называл power paper scope
полностью закрытым, хотя machine route оставлял abstract hold pull-up и pack
IRQ, а обязательные IN/CP/AOLDO/REG2/REG3, CHG/DIS gate and 2S sense support
parts не были представлены всеми физическими instances. Это не HIL-only
остаток, а бумажная полнота схемы.

## Исправление coverage

`bom_audit` теперь отдельно учитывает:

1. уже установленные физические instances;
2. обязательные, но ещё не instantiated покупные items;
3. PCB-only features, которые требуют geometry/manufacturing rule, но не
   являются фиктивной закупочной строкой;
4. base-product, regional cell-kit, optional accessory и costed-variant scope.

Генератор выпускает узкий responsive review и полный CSV. Тест фиксирует
исходный I8-срез: 791 placements, 185 used lines, 151 lines с current
orderability evidence, 34 без него и 0 machine-readable cost/alternate lines.
Эти нули не означают нулевую стоимость — они запрещают складывать разрозненные
старые оценки в ложный COGS.

## Следствие

- I8 inventory prerequisite теперь воспроизводим и **проведён ревью только по
  coverage**, но sourcing/cost/alternate qualification остаётся active.
- Узкий MAX17320 paper-support subblock I3 считается переоткрытым до exact
  machine instantiation и повторного review; выбранные 2S topology, cells,
  manager и safety intent не отменены.
- RF/M5 connector MPN могут быть first-target candidates с явным
  mechanics/specimen reopen gate; отсутствие final enclosure ещё не разрешает
  скрыть их из BOM.
- KiCad и total COGS остаются заблокированы.

