# FND-0113 — monolithic principled diagram exceeded GitHub's Mermaid limit

- Статус: **исправлено; проведено ревью документационного артефакта**
- Дата: 2026-08-19
- Scope: hardware target landing pages and generated `G2F-3I` atlas

## Несоответствие

Стартовые страницы передавали всю one-device-per-node проекцию — активные
компоненты, пассивы и связи — в один Mermaid block. После последовательного
закрытия I3…I7 исходник превысил лимит текста GitHub. Вместо целевой начинки
пользователь видел `Maximum text size in diagram exceeded`.

Это не электрическая или функциональная ошибка, но она разрушала основной
продуктовый артефакт и скрывала обновляемую принципиальную схему.

## Исправление

1. Обе стартовые страницы теперь содержат ограниченную вертикальную overview
   diagram: один физический компонент на box, exact/current MPN и роль.
2. Полная one-device-per-node проекция не удалена. Она остаётся скрытым raw
   source на landing pages и в generated atlas, а pin/net tables продолжают
   строиться из тех же machine sources.
3. Generated atlas больше не отправляет заведомо слишком большой source в
   Mermaid renderer.
4. Regression test проверяет current core MPN coverage, `flowchart TD`, размер
   rendered block `< 12000` characters и сохранение отдельных detailed nodes
   в raw projection.
5. Отдельная gate diagram в `docs/review/stages.md` показывает текущее место:
   internal I8 внутри gate 2F; I9, integrated mockup and KiCad remain blocked.

## Влияние

Component choices, instances, pins, rails, nets, owners, BOM quantities and
firmware contracts не изменены. Исправлен только способ публикации уже
существующей архитектурной информации.

