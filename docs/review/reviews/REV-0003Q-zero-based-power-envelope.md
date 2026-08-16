# REV-0003Q — ревью zero-based power envelope

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3, шаг 5c
- Артефакт: `PWR-0001`

## Проверка

| Gate | Результат |
|---|---|
| Scenario-derived | rail peaks выведены из `CON-0001`, не из суммы несовместимых TX maxima |
| Primary values | S3/C5/nRF/CC/SA518/U214/U216/RP comparison values traceable to manufacturer documents |
| Voice decision | 4.0 V, 1.25 A continuous/1.5 A transient и STOP-dominant behavior сохранены без legacy 5 V substitution |
| Accessory power | U214/GNSS и U216 помещаются в 0.75 A/1.0 A current-limited 5 V envelope; unknown profile default-off |
| Core/RF separation | один 3.3 V converter допускается ради стоимости, но packet/audio branches имеют isolation, observation and default state |
| Candidate equality | 2.5 A/3.0 A common rail включает 100 mA RP allowance; `3A` не получает скрытый дополнительный regulator |
| Safety order | hardware kill precedes best-effort logging; rail-on is never arming |
| Honest status | exact converter, battery, thermal and kill-time measurements перечислены как eight open HIL gates |

## Саморевью

Сумма `S3 450 + C5 500 + 3×nRF 150 + CC 50 + RP 100 + UI/storage/audio` является component-envelope проверкой, но не разрешённым simultaneous operating mode. Поэтому выбран 2.5 A continuous 3.3 V floor с 3.0 A transient, а не необоснованный rail по сумме всех TX. Отдельные branch limits и scheduler не позволяют этой экономии превратиться в brownout или скрытое ограничение функции.

`SYN-3A` объективно имеет худший idle/active-energy potential из-за третьего MCU. Это не paper fail: дополнительный ток включён в общий converter floor и будет сравниваться Wh/session в одинаковом workload. `SYN-2A/2B` не объявлены экономичнее до измерения.

## Итог

Power topology, rail floors, sequencing, fault behavior и test matrix получают статус **«Проведено ревью»**. Все три candidates переходят к RF zoning/coexistence; component selection и физический HIL остаются открытыми доказательствами, а не вопросами к владельцу.
