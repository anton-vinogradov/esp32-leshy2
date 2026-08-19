# FND-0114 — hidden projection and USB-led overview obscured the architecture

- Статус: **исправлено; проведено ревью документационного артефакта**
- Дата: 2026-08-19
- Scope: target hardware landing pages, generated principled atlas and generator

## Несоответствие

Исправление `FND-0113` устранило ошибку GitHub Mermaid, но сделало это
неполно: исчерпывающая one-device-per-node проекция осталась скрытым text
block, а единственная отрисовываемая схема начиналась с USB/power chain.
Компоненты не были потеряны, однако читатель не мог сначала увидеть владельцев
функций и не мог отрисовать полную начинку по частям.

## Исправление

1. Стартовые EN/RU страницы теперь сначала показывают карту S3/C5/RP, затем
   отдельные вертикальные срезы S3, C5, RP и только после них power path.
2. Полная проекция генерируется как набор функциональных Mermaid-диаграмм.
   Большие домены автоматически режутся дальше; каждый block обязан быть меньше
   `12 000` символов.
3. Каждый физический instance сохраняет отдельный node с exact/current MPN и
   ролью. Контекстные owner nodes могут повторяться между срезами, но разные
   устройства никогда не объединяются в один node.
4. Монолитный machine source не удалён: генератор публикует
   `G2F-3I-principled-projection.mmd` для полного diff/review.
5. README-срезы теперь также генерируются из current candidate, поэтому замена
   MPN не может оставить на landing page старую ручную диаграмму.
6. При введении coverage-check найдено вторичное несоответствие: прежний raw
   projection не объявлял 44 уже существующих physical instances обвязки
   USB-PD и charger. Все 44 добавлены в power atlas; генератор теперь падает,
   если любой current candidate instance не получил отдельный node.

## Влияние

Device identities, quantities, pins, nets, rails, owners, BOM и firmware
contracts не изменились. Изменены навигация, размер Mermaid blocks и способ
публикации уже принятой paper architecture.
