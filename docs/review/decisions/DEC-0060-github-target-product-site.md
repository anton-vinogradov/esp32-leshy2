# DEC-0060 — GitHub entrypoints являются целевым product site

- Статус: **Принято; проведено ревью распространения**
- Дата: 2026-08-17
- Основание: владелец принял `IMP-0051`
- Refinement: [`DEC-0011`](DEC-0011-target-readme-current-state.md)
- Finding: [`FND-0072`](../findings/FND-0072-target-readmes-contained-engineering-chronology.md)

## Решение

1. `README.md` и `README.ru.md` обоих репозиториев — целевые landing pages
   готового Leshy2, а не сокращённый review ledger.
2. Основной текст target page не содержит цепочек `DEC/REV/FND/IMP`, истории
   выбора, стадий зрелости, открытых findings или следующего engineering gate.
3. Принятые свойства переводятся в пользовательский результат. Exact MPN,
   интерфейс и pin mapping допустимы как техническая спецификация, если не
   сопровождаются хронологией выбора.
4. Current state и review ledger доступны через короткую навигацию, но их
   содержимое не копируется обратно.
5. Широкие таблицы не используются там, где раскрываемый список или отдельный
   atlas лучше читается на GitHub/mobile.
6. Hardware сохраняет узкую вертикальную living diagram; firmware публикует
   вертикальный safe-session flow. EN/RU пары остаются семантически одинаковыми.
7. Regression проверяет отсутствие review-prefix chronology и старого раздела
   `Development state / Состояние разработки` в target pages.

## Что остаётся каноническим

- Product landing объясняет целевой результат, но не принимает решения.
- `docs/status/current-state.*.md` каноничен для зрелости и открытых работ.
- `docs/review/` каноничен для требований, решений, источников и доказательств.
- Machine-readable architecture source и generated atlas каноничны для exact
  working pin/component projection.

## Reopen rule

Если target page снова требует знания review-ID для понимания продукта или
начинает перечислять незакрытые гейты, документационный контракт переоткрывается.
Прямая ссылка на ledger не считается нарушением; пересказ его хронологии —
считается.
