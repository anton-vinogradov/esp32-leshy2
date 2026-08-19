# REV-0002Y — финальное ревью и распространение S3 native-BLE ownership

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 2 — возможности и исключения
- Входы: `REV-0002X`, ответ владельца «BLE на S3 — ок», `IMP-0017`, `IMP-0019`, draft `REQ-BLE-0001`
- Выход: `DEC-0021`

## Проверки

| Проверка | Результат |
|---|---|
| BLE owner | S3 единолично владеет baseline native BLE; C5 BLE default-off |
| Identity/security | один product identity, bond/key vault и allowlist на S3 |
| nRF24 boundary | full native nRF24 capability не сокращён; limited только experimental BLE-compatible subset |
| C5 coexistence | BLE снят с C5 ordinary profile, освобождая его shared radio-time для Wi-Fi/802.15.4 |
| Cross-repository | hardware/firmware target и current-state EN/RU синхронизированы |
| Overclaims | Classic, native connection-follow, stable identity и RSSI-distance не обещаны |
| Open extras | `IMP-0004`, ⚠️ `IMP-0020` и физический nRF24 owner не приняты автоматически |

## Итог

`IMP-0019/A` и native/native-compatibility часть `IMP-0017` приняты как `DEC-0021`. `FND-0002` закрыт на requirement-level, `REQ-BLE-0001` получил статус **«Проведено ревью»**. Выбор S3/C5 для трёх полнофункциональных nRF24 намеренно вынесен в отдельный `AUD-0003`/`IMP-0021`.

