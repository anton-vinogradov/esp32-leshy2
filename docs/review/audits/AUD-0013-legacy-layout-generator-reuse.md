# AUD-0013 — legacy physical-layout generator reuse audit

- Статус: **Проведено ревью источника; выбран как working geometry baseline**
- Дата: 2026-08-17
- Решение о порядке: [`DEC-0041`](../decisions/DEC-0041-electrical-feasibility-before-physical-layout.md)
- Source:
  [`leshy2_layout.py`](../../../drafts/legacy-2026-08-15/docs/img/leshy2_layout.py)
- Specification:
  [`layout-spec.ru.md`](../../../drafts/legacy-2026-08-15/docs/layout-spec.ru.md)

## Что уже сделано хорошо и переиспользуется

Генератор описывает воспроизводимую двухплатную clamshell-гипотезу с двумя
платами примерно `75×150 mm`, дисплеем, двумя 18650, внутренним зазором,
внешними/внутренними видами и боковым сечением. Полезнее самого рисунка его
автоматические проверки:

1. rectangle/text collision;
2. доступность buried interfaces только у достижимой кромки;
3. пересечения стрелок и labels;
4. достаточность межплатного зазора;
5. mounting-hole clearance;
6. конфликт боковых выходов двух плат после реального X-mirror при складывании;
7. совпадение обеих половин mezzanine в device coordinates.

Спецификация отдельно различает part frame, render mirror и физический fold.
Это важная механическая логика, которую не следует повторно изобретать.

## Что нельзя наследовать

| Legacy assumption | Текущее состояние |
|---|---|
| `MAIN=S3`, `C5 board=co-processor` и прежние owners | переоткрыты; определяются новым `G2F` |
| три nRF и IR автоматически принадлежат C5 | только историческая раскладка |
| onboard LoRa и его antenna | исключены; LoRa внешний U214/Unit profile |
| девять board antennas | пересчитываются по exact RF candidates |
| generic `nRF+PA/LNA` footprint | недопустим без exact MPN; реальные варианты существенно различаются |
| крупные generic component zones | не доказывают packing, keepout, cable bend, thermal или service access |
| прежние connector/pin counts | пересчитываются после нового semantic demand и device provenance |
| только прежний M5/Grove surface | расширяется full U214 Cap-Bus и M5-first Unit A/B/C/custom contract |

## Предлагаемый способ дальнейшего использования

Генератор пока остаётся в legacy snapshot неизменным. Открытое
[`IMP-0035`](../improvements/IMP-0035-single-source-pin-and-layout-generator.md)
предлагает после выбора способа создать активную версию, в которой:

- device inventory является единственным источником MPN, размеров, высот,
  интерфейсов и antenna/cable keepout;
- semantic nets связываются с owner/controller/exact exposed pin;
- один запуск генерирует pin ledger, block/board diagrams и physical SVG;
- электрические проверки уникальности/strap/recovery/controller coexistence
  выполняются до геометрических проверок;
- ручная подпись внутри SVG не может расходиться с таблицами.

До решения по `IMP-0035` это направление не считается принятым. При варианте B
те же cross-checks выполняются отдельной review matrix вручную.

## Результат

Старый макет экономит повторную работу над clamshell geometry и её проверками,
но не задаёт архитектуру. Следующий артефакт — не новый корпус: сначала
`DEM-0001/SRC-0002`, затем полные electrical candidates, и только после их
review активная адаптация этого генератора.
