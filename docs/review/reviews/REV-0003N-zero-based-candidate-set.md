# REV-0003N — ревью zero-based whole-device candidate set

- Статус: **Проведено ревью набора candidates; архитектура не принята**
- Дата: 2026-08-16
- Этап: 3, шаг 4
- Артефакт: `SYN-0001`

## Проверка

| Gate | Результат |
|---|---|
| Input discipline | использованы только reviewed `CAP/CON/RES/SRC` и accepted product boundaries |
| Whole-device scope | каждый candidate размещает application, native radios, nRF/CC, UI, storage, audio, voice, expansion, safety, update и recovery |
| Independent derivation | candidates выведены из способов resource consolidation, а не из прежних owner maps |
| nRF neutrality | owner является следствием полной раскладки; split ownership сохраняется как conditional response на measured bus/load fail |
| Additional-controller fairness | RP2354A A4 учитывает собственные update/recovery/IPC/power/HIL costs и не принят заранее |
| Same product | ни один candidate не удаляет full-function nRF, dual IR, onboard audio, external profiles, STOP или open updates |
| Interface honesty | UI/display точный MPN не выдуман; одинаковый function-complete signal envelope резервируется всем candidates |
| Safety | hardware STOP/TX-off/actual-TX obligations одинаковы и не делегированы expander/firmware-only path |
| Premature decision | winner, module-memory winner, final transport score и price score не выбраны |

## Итог

Набор `SYN-2A/2B/3A` охватывает три недоминируемых способа закрыть один и тот же ресурсный граф и получает статус **«Проведено ревью набора candidates»**. Следующим пререквизитом comparison являются отдельные exact `PIN-*` maps и количественные budgets каждого candidate. Ни один target README пока не меняется.
