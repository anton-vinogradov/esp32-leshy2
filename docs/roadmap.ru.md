# Роадмап железа Leshy2

[Главная](../README.ru.md) · [Отчёты этапов](stage-results.ru.md) · [English](roadmap.md)

<!-- current-substep: H6.0.3-R1 -->

**Текущая аппаратная граница: `H6.0.3-R1`.**

Эта страница отвечает только за порядок работ и критерии перехода. Решения по
устройству описаны на [главной](../README.ru.md), подробности — в предметных
документах, а завершённые результаты — в [индексе отчётов](stage-results.ru.md).

## Последовательность

| Этап | Статус | Критерий выхода | Отчёт |
|---|---|---|---|
| H0 · Требования и архитектура | ✅ Проведено ревью · R2 | функции, владельцы и safety boundary непротиворечивы | [H0-R2](h0-r2-functional-architecture.ru.md) |
| H1 · Физический дизайн | ✅ Проведено ревью · `H1-R2.39` | внешний вид, точные тела, кабели и сборка помещаются | [H1-R2](h1-r2-acceptance.ru.md) |
| H2 · Production ECAD | ✅ Проведено ревью · `H2-R2.1.5` | две native-схемы, pin/net parity и ERC чисты | [H2-R2](h2-acceptance.ru.md) |
| H3 · Виртуальная электрическая проверка | ✅ Проведено ревью · `H3-R2.7` | все считаемые до layout углы пройдены, физические остатки назначены | [H3-R2](h3-r2-acceptance.ru.md) |
| H4 · Совместный pre-layout gate | ✅ Проведено ревью · `H4-R2.3` | hardware и firmware boundary сведены | [H4-R2](h4-r2-acceptance.ru.md) |
| H5 · Компоненты и маршруты закупки | ✅ Проведено ревью · `H5-R2.1` | все группы имеют контролируемый путь; order-time recheck обязателен | [H5-R2](h5-r2-current-route.ru.md) |
| **H6 · Placement, routing и release candidate** | **▶ Сейчас · `H6.0.3-R1`** | вся медь, повторные электрические/механические проверки и production outputs проходят | [Текущий срез](h6-r2-current-routing.ru.md) |
| H7 · Изготовление одного устройства | ⏳ Ожидает | получены две PCBA и комплект деталей для одного прототипа | — |
| H8 · Bring-up и физическая проверка | ⏳ Ожидает | безопасный запуск, программирование и физические evidence проходят | — |
| H9 · Manufacturing release | ⏳ Ожидает | исправления первого экземпляра сведены в воспроизводимый release | — |

## Текущий H6

| Подэтап | Статус | Выход |
|---|---|---|
| H6.0.1-R1 · Placement и механический стек | ✅ | 1 208/1 208 footprints, крепёж и microcoax помещаются |
| H6.0.2-R1 · Правила трассировки | ✅ историческая геометрия | классы и native KiCad rules зафиксированы |
| **H6.0.3-R1 · 80-мм разводка и parity** | **▶ Сейчас** | все nets проведены или явно NC; DRC и parity равны нулю |
| H6.0.4-R1 · Питание и тепло по меди | ⏳ | реальные copper/via/rail margins проходят |
| H6.0.5-R1 · Digital, USB и M1 SI | ⏳ | i8080‑8, USB и шины проходят |
| H6.0.6-R1 · RF и Airband | ⏳ | десять путей, matching, isolation и parasitics проходят |
| H6.0.7-R1 · STEP, корпус и кабели | ⏳ | assembled geometry и допуски проходят |
| H6.0.8-R1 · Production и bring-up outputs | ⏳ | Gerber/BOM/CPL/чертежи/прошивка готовы |
| H6.0.9-R1 · Независимый DFM/CPL-review | ⏳ | release candidate не имеет открытого blocker |

## Правила перехода

- Размер 80 × 150 мм сохраняется, пока проходит [машинный size gate](../hardware/layout/generated/H6-R2-current-routing-audit.json). При его срабатывании рассматривается 85 × 150 мм, после чего повторяются все H1/H6, ERC/DRC, электрические и firmware-проверки.
- Нельзя переносить незавершённую работу следующего этапа назад и называть её закрытой.
- Фабрика только изготавливает и населяет две PCBA; финальную непаяную сборку и первое включение выполняет владелец.
- Перед заказом все MPN повторно проверяются по live JLCPCB Standard PCBA surface.
- H7 начинается только после общего hardware/firmware pre-order gate и явного одобрения фактической сметы одного устройства.

Машинные источники: [hardware roadmap state](../hardware/verification/hardware-roadmap-state.json) · [H6 release plan](../hardware/verification/h6-layout-release-plan.json) · [pre-order contract](../hardware/verification/preorder-verification-contract.json).
