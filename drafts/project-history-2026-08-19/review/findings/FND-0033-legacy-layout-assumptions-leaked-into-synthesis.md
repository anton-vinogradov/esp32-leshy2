# FND-0033 — legacy layout assumptions leaked into architecture synthesis

- Статус: **Исправлено на document-control level; new synthesis started by `DEC-0027`**
- Дата: 2026-08-16
- Серьёзность: architecture-method error
- Обнаружено: owner review

## Несоответствие

Этап 3 формально начался с `INV-0004`, но фактически оптимизировал legacy net map. Это видно по трём признакам:

1. candidates были заранее заданы как S3-heavy/C5-heavy/balanced вместо вывода аппаратных ролей из хотелок;
2. legacy GPIO, buses и места модулей рассматривались как то, что нужно «освободить», а не как один из необязательных исходников;
3. `REQ-N24-0001` объявлял owner открытым, но всё ещё содержал C5-specific dead-man/driver wording и требование one-MCU placement.

В результате synthesis искал лучшее исправление старой схемы, а не лучшую архитектуру продукта.

## Исправление

- 11 legacy-derived stage-3 artifacts перенесены в `drafts/stage3-legacy-derived-2026-08-16/` и заменены архивными указателями;
- `REQ-N24-0001` очищен от C5/one-MCU placement assumptions;
- новый активный вход этапа 3 — `CAP-0001`, а не прежний pin/layout model;
- legacy documents, current PCB/source и найденные там идеи могут вернуться только как сравнительные candidates после independent derivation.

## Запрет регрессии

Ни одна новая architecture row не может иметь обоснование «так уже было разведено». Она обязана ссылаться на capability, concurrency, safety, cost или primary-source hardware ceiling.
