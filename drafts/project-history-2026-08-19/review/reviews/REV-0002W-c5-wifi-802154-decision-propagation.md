# REV-0002W — финальное ревью и распространение C5 Wi-Fi/802.15.4 решения

- Статус: **Проведено ревью**
- Подшаг: 2W — финализация capability contract после `DEC-0020`
- Входы: `REV-0002V`, `IMP-0018/A`, `DEC-0020`, `FND-0022`–`FND-0025`
- Выход: reviewed `REQ-W5-0001` и согласованные target/current-state EN/RU обоих репозиториев
- Дата: 2026-08-16

## Проверено

- OpenThread принят как открытый ordinary Thread baseline;
- официальный Zigbee backend остаётся optional conditional adapter и не требуется для core/raw/Thread build или recovery;
- proprietary binary получает отдельные provenance/rights/SBOM/version/hash/signature/update/rollback gates;
- Main ordinary networking, Lab passive capture и Controlled-Zone active/disruptive tests не смешаны;
- public Wi-Fi raw TX не расширен до deauth/disassoc, `AUTO` не назван simultaneous dual-band, DFS SoftAP не обещан;
- Wi-Fi/BLE/802.15.4 shared-radio coexistence и packet loss остаются измеримыми implementation/HIL gates;
- новый RF hardware не добавлен скрыто; dual-SoC оставлен будущим отдельным предложением только после измеренного провала;
- hardware/firmware target и current-state EN/RU согласованы без заявления о готовой реализации.

## Результат

`REQ-W5-0001` получил статус **«Проведено ревью»**. `FND-0025` закрыт на requirement-level. `FND-0022`–`FND-0024`, transport/BLE-owner/STOP, binary integration и coexistence HIL остаются открытой реализационной работой. `IMP-0003` и private patched Wi-Fi backend не приняты автоматически.

