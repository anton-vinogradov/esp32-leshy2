# FND-0031 — demand model дважды посчитал физический STOP

- Статус: **Закрыто исправлением `DM-UI-02`; проведено ревью**
- Дата: 2026-08-16
- Серьёзность: layout/pin-count mismatch без изменения product scope
- Затрагивает: `DM-0001`, `IMP-0010`, UI matrix/`U14`

## Несоответствие

Legacy control set содержит десять физических органов: D-pad `UP/DOWN/LEFT/RIGHT/OK`, `BACK`, `OPTIONS`, `F1`, `F2` и `STOP`. После `DEC-0024` STOP является отдельным latched hardware path и не входит в ordinary matrix.

`IMP-0010` поэтому корректно считает девять неаварийных кнопок, но `DM-UI-02` одновременно требовал «ten ordinary physical controls» и отдельный `DM-SAFE-01` STOP. Это создавало ложную одиннадцатую кнопку и лишний resource demand.

## Исправление

`DM-UI-02` теперь требует девять ordinary controls либо доказанный эквивалент, а `DM-SAFE-01` — отдельный physical STOP. Всего по-прежнему десять физических controls; ни одна пользовательская функция не удалена и новая не добавлена.

## Проверка

Control inventory после исправления: `5 + BACK + OPTIONS + F1 + F2 = 9 ordinary`; `+ STOP = 10 total`. Все layouts используют именно этот единый подсчёт.

