# IMP-0023 — dedicated 4.0 V rail для SA518

- Статус: **Принят вариант A как `DEC-0025`; проведено ревью**
- Дата: 2026-08-16
- Основание: `FND-0030`, `DEC-0016`, `BUD-0001`
- Затрагивает: power tree, voice backend stuffing, STOP, BOM, thermal/RF HIL

## Контекст

Принятый SA518 даёт целевые 0.5/1 W около 4.0 V. На legacy 5 V его таблица показывает 31.5–31.7 dBm и до 1.07 A, то есть примерно 1.5 W. На 3.3 V high-power около 27–28 dBm и уже не сохраняет 1 W result. Нужен честный electrical profile, а не переименование high/low bit.

## Вариант A — рекомендуется

Добавить отдельный STOP-dominant `VVOICE`:

- nominal 4.0 V, final trim window 3.9–4.1 V по conducted qualification;
- regulator rating не менее 1.25 A continuous и 1.5 A transient с local bulk;
- rail default-off, hardware load switch/inhibit под `DEC-0024`, PTT forced RX;
- current/voltage test points и per-band conducted calibration;
- SA518 target и SA868S fallback получают разные explicit stuffing descriptors. Если fallback действительно требует 5 V, он использует альтернативную regulator stuffing/configuration, а не runtime-неизвестный общий rail.

Legacy power architecture уже использует 2S `BAT=6.0–8.4 V`, поэтому `VVOICE` можно получить обычным отдельным buck напрямую от `BAT`; boost/buck-boost для принятого battery profile не нужен. Это добавляет один небольшой regulator domain с inductor/caps и STOP-controlled output switch либо эквивалентный qualified power stage. Exact BOM, возможность унификации regulator part и стоимость сравниваются на этапе 4; 5 V accessory rail сохраняется отдельно.

## Вариант B — оставить 5 V

Потребует принять новый приблизительно 1.5 W product class, пересчитать legal/RF/thermal/power profile и отказаться от прежнего 1 W обещания. Software-only limit без conducted proof не считается решением.

## Вариант C — использовать 3.3 V

Дешевле по power tree, но теряет принятую 1 W capability и поэтому не является zero-loss optimization.

## Рекомендация

**Принять A.** Дополнительный rail дешевле и проверяемее, чем неопределённая выходная мощность, сохраняет 0.5/1 W target и позволяет safety STOP физически обесточить voice PA.

## Решение владельца

Вариант A принят как `DEC-0025`. Варианты B/C не являются эквивалентными заменами принятого 1 W-class target.
