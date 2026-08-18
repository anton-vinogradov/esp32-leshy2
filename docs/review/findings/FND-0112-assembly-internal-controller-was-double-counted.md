# FND-0112 — assembly-internal display controller was double-counted

- Статус: **исправлено; BOM coverage повторно проведено ревью**
- Дата: 2026-08-19
- Scope: `G2F-3I`, `INT-0001/I8`

## Несоответствие

Machine architecture намеренно содержит два отдельных узла:

- `display` → purchased `HMX035CTFT-001` LCM+CTP assembly;
- `display_touch_controller` → `Sitronix ST77922` COG внутри assembly.

Раздельные узлы нужны principle diagram и contact provenance: нельзя смешивать
роль панели и физического controller die в одном квадрате. Однако первоначальный
BOM generator считал каждый `instances` entry отдельной закупочной placement.
В результате internal ST77922 ошибочно попадал в CSV вместе с HMX, хотя
datasheet/architecture прямо говорят, что bare COG не является отдельной
Leshy2 purchase line.

## Исправление

`bom_audit.non_purchase_instances` теперь связывает internal evidence node с
его purchased parent. Generator:

1. сохраняет оба узла в architecture и principle diagram;
2. исключает только internal node из supplied/costed BOM lines;
3. публикует отдельный список исключённых assembly-internal nodes;
4. валидирует существование child/parent, запрет self-parent и дубликаты;
5. regression-тестом запрещает возврат `sitronix_st77922` в purchase CSV.

Проверка текстовых маркеров не нашла других current instances, которые сами
объявлены внутренними и одновременно считаются отдельной purchase line.

## Пересчитанный current snapshot

- 858 architecture instances;
- 1 explicit assembly-internal evidence instance;
- 857 supplied/costed placements;
- 187 used purchase lines;
- orderability `186/187`, единственный gap — standalone `HMX035CTFT-001`;
- cost `0/187`;
- alternate/no-substitution `1/187` after display no-drop-in disposition;
- four uninstantiated physical families remain separate.

## Влияние

Функции, GPIO, электрический endpoint, display controller, диаграмма и firmware
не меняются. Исправляются только procurement quantities and denominators. Это
автоматическое исправление несоответствия в пределах уже делегированных
полномочий; KiCad и I8 completion по-прежнему не разрешены.
