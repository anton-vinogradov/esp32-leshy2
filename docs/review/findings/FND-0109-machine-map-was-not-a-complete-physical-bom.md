# FND-0109 — machine map was not a complete physical BOM

- Статус: **I8 coverage исправлен; MAX17320 residue закрыт, qualification active**
- Дата: 2026-08-19
- Scope: `G2F-3I`, `INT-0001/I8`

## Несоответствие

До I8 количество `instances` ошибочно можно было принять за полный material
inventory. Исходный срез из 791 machine-instantiated placements / 185
используемых MPN-линий всё ещё скрывал за `abstract:*` и prose физические
покупные элементы:

- 9 внешних SMA bodies;
- 5 RF cable/pigtail assemblies;
- rear Cap-Bus и native HY2.0-4P connector bodies;
- 8 отдельных actual-TX threshold/hysteresis networks;
- часть обязательной MAX17320 support circuit — исправлено `DEC-0100`;
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

Генератор выпускает узкий responsive review и полный CSV. После exact
MAX17320 и последующего actual-TX threshold/domain-isolation repair тест
фиксирует текущий I8-срез: 858 placements, 188 used lines, 155 lines с current
orderability evidence, 33 без него и 0 machine-readable cost/alternate lines.
Исторический первый срез 816/187 сохранён в его propagation review, но больше
не является current BOM.
Эти нули не означают нулевую стоимость — они запрещают складывать разрозненные
старые оценки в ложный COGS.

## Следствие

- I8 inventory prerequisite теперь воспроизводим и **проведён ревью только по
  coverage**, но sourcing/cost/alternate qualification остаётся active.
- Узкий MAX17320 paper-support subblock исправлен и повторно просмотрен в
  [`PWR-0022`](../architecture/PWR-0022-exact-max17320-2s-support-profile.md),
  [`DEC-0100`](../decisions/DEC-0100-exact-max17320-2s-support-closure.md) и
  [`REV-0005BF`](../reviews/REV-0005BF-max17320-support-repair-propagation.md).
  I3 paper scope снова закрыт; physical/HIL evidence не заявляется.
- RF/M5 connector MPN могут быть first-target candidates с явным
  mechanics/specimen reopen gate; отсутствие final enclosure ещё не разрешает
  скрыть их из BOM.
- KiCad и total COGS остаются заблокированы.

## Сводная таблица исправлений MAX17320

| Было | Несоответствие | Исправлено |
|---|---|---|
| обязательные IN/CP/regulator parts только в prose | физический BOM и схема неполны | 25 exact placements, включая каждый отдельный capacitor/resistor |
| 2S support не воспроизводил Figure 24 | риск случайного 3S/4S ladder | CELL1/CELL2/CELL3 short, только RBAL1/RBAL4 и два filters |
| balance resistor без power closure | 0402 мог перегреться при 0,267 Вт | `ERJ-P08F49R9V`, 0,66 Вт, thermal HIL open |
| CSP/CSN только sense routes | отсутствовал явный силовой путь шунта | force path SLOT0_NEG→END1→END2→power ground плюс Kelvin |
| push-pull PFAIL напрямую в MSPM0 | возможен overdrive при более низком VDD | NMOS level translator и admission-referenced pull-up |
| PA23 подразумевался open-drain | PA23 является standard GPIO | внешний NMOS passive-drain к `SYS_INT_N` |
| MSPM0 VDD/NRST только подразумевались | support нельзя было перенести в схему | exact 10 µF + 100 nF, 47 kΩ + 10 nF и NRST test point |
