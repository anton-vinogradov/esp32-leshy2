# FND-0111 — orderability audit exposed pseudo-MPN and display gap

- Статус: **несоответствие исправлено; sourcing residue локализован**
- Дата: 2026-08-19
- Scope: `G2F-3I`, `INT-0001/I8`

## Несоответствие

После закрытия inventory coverage 33 используемые BOM-линии не имели
датированного источника заказываемости. Повторная проверка показала два разных
класса проблемы:

1. строка контроллера `RP2354B A4 (exact RP2354B0A4 first target)` описывала
   семейство, корпус и silicon revision, но не являлась точным кодом заказа;
2. для дисплейной сборки `HMX035CTFT-001` официальная схема раскрывает marking
   и 40 контактов, но standalone drawing, lifecycle и открытый закупочный канал
   по этому exact assembly не доказаны.

Первый дефект опасен тем, что человек или factory RFQ могли бы попытаться
заказать несуществующую строку. Второй нельзя маскировать наличием похожих
3.5-inch модулей: совпадение диагонали, разрешения и контроллера ещё не доказывает
одинаковые FPC, pinout, touch, backlight, оптику и механический контур.

## Исправление

- Exact first-target order code контроллера заменён на `SC1512-A4`, то есть
  7-inch-reel order identity для `RP2354B0A4`; `SC1512(13)-A4` остаётся той же
  A4 silicon revision в другой упаковке и не подменяет первую target-строку.
- Текущие landing/generated/runtime артефакты получают одновременно order code
  и понятное functional identity `SC1512-A4 (RP2354B0A4)`.
- Для ещё 31 строки добавлены датированные exact-MPN источники. Источники
  классифицируются честно: stocked authorized aggregation/distributor,
  manufacturer product/RFQ либо production-parts supplier; наличие ссылки само
  по себе не объявляется factory quote или гарантией будущего stock.
- `HMX035CTFT-001` оставлен единственной незакрытой used sourcing line. Его
  нельзя автоматически заменить до проверки полного electrical/mechanical
  equivalence либо принятия изменённого display endpoint.

## Текущий результат

- 858 instantiated placements;
- 188 used exact-device/MPN lines;
- 187/188 lines с current orderability evidence;
- 1/188 unresolved: `HMX035CTFT-001`;
- 188/188 cost и, на момент этого source recheck, alternate dispositions
  открыты; subsequent `DSP-0008/BOM-0010` closes the display no-drop-in
  disposition only;
- четыре отдельные physical-gap families не смешиваются с used-line sourcing:
  SMA bodies, RF cable assemblies, M5 connector bodies и antenna kit.

## Следствие

Исправление `SC1512-A4` не меняет GPIO, QFN80 footprint class, firmware,
производительность или возможности продукта и принято автоматически в пределах
делегированного component-maintenance решения. Display sourcing становится
следующим локальным I8 work item. KiCad, physical freeze и общий I8 review
по-прежнему не разрешены.
