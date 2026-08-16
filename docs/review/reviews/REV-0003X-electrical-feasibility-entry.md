# REV-0003X — electrical-feasibility entry and real-device rule

- Статус: **Проведено ревью исправления и входных артефактов**
- Дата: 2026-08-17
- Decision: [`DEC-0041`](../decisions/DEC-0041-electrical-feasibility-before-physical-layout.md)
- Finding: [`FND-0049`](../findings/FND-0049-exact-pin-map-lacked-device-provenance.md)
- Inputs: [`DEM-0001`](../architecture/DEM-0001-current-semantic-signal-demand.md),
  [`SRC-0002`](../architecture/SRC-0002-real-device-pin-provenance.md),
  [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md)

## Проверка

| Проверка | Результат |
|---|---|
| capability-first wishlist сохранён без старых owners | да; semantic endpoints перечислены отдельно от physical GPIO |
| exact-pin статус больше не выводится из SoC marketing count | да; обязательна полная package/module/carrier chain |
| реальный пример скрытого pin loss проверен | да; C5 N8R8 `GPIO15` занят internal PSRAM |
| три nRF не сведены к generic board | да; два реальных reference MPN показали разные size/power classes, production MPN открыт |
| U214 проверен как actual 14-pin Cap, а не generic SPI | да |
| старый layout используется без наследования его owner/net assumptions | да; только geometry/checking baseline |
| premature P1/P2/P3 требует owner choice | нет; переведён в reference |
| KiCad либо target architecture разрешены | нет |
| открытые exact components ошибочно объявлены free pins | нет; `SRC-0002` помечает их blocking |

## Результат

Исправление процесса, semantic signal ledger, первый real-device provenance
pass и аудит legacy generator получают **«Проведено ревью»** в указанном scope.
Вся electrical feasibility ещё не закрыта: следующий результат должен сравнить
не менее двух полных owner/bus/GPIO candidates и не сможет получить review,
пока применимые `SRC-0002` rows не подтверждены exact devices.

