# REV-0002H — ревью пререквизитов System/UI/storage

- Статус: **Проведено ревью**
- Подшаг: 2H — prerequisite audit, не финальное ревью requirement set
- Артефакты: `FND-0008`, draft `REQ-SYS-0001`, `IMP-0011`
- Дата: 2026-08-16

## Проверено

- все `C-SYS-01`–`C-SYS-11` сопоставлены будущим требованиям и не потеряны;
- добавлены пересекающиеся `C-X-01`, `C-X-02`, `C-X-09` и UI/performance candidates;
- BadUSB помещён только в Controlled Zone и не смешан с обычным USB service;
- C5 OTA отвязан от неподтверждённого legacy `SPI3`;
- local input остаётся достаточным без телефона/BLE;
- MSC не допускает двух одновременных writers одного носителя;
- M5 GPS `PORT.C`, U214/`EXT-RF14` и generic Grove I²C не названы взаимозаменяемыми;
- legacy hot-plug promise заменён qualification gate;
- STOP behavior задан как requirement, но hardware STOP не назван реализованным;
- pin-map/`IMP-0010` не возвращены на преждевременное решение;
- обновлённые технические утверждения сверены с первичной документацией Espressif;
- открыто ровно одно новое owner-level улучшение: `⚠️ IMP-0011`.

## Результат

Аудит пререквизитов проведён ревью. `REQ-SYS-0001` остаётся **«На ревью»** до решения `IMP-0011`; после него требуется propagation check и только затем статус всего System/UI capability-среза **«Проведено ревью»**.
