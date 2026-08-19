# REV-0002I — ревью System/UI/storage и распространения `A-open`

- Статус: **Проведено ревью**
- Подшаг: 2I — System/UI/storage capability requirements
- Решение: `DEC-0013`
- Артефакт: `REQ-SYS-0001`
- Дата: 2026-08-16

## Проверено

- все `C-SYS-01`–`C-SYS-11` покрыты стабильными requirement IDs;
- BadUSB находится только в Controlled Zone с `AUTHORIZED_TARGET` и отдельным arming;
- normal USB service/CLI/import не обходят пользовательские и safety-гейты;
- C5 OTA transport-neutral до этапа 3 и независимо проверяется на C5;
- штатные S3/C5 updates требуют owner-authorized signatures, validation и rollback;
- owner-controlled keys, offline build/signing и developer lifecycle сохраняют открытость устройства;
- vendor-only key/cloud не принят;
- Secure Boot/Flash Encryption/eFuse/anti-rollback lockdown не включён и остаётся отдельным opt-in gate;
- `FND-0008` закрыт на requirement-level, а architecture/HIL prerequisites сохранены как условные;
- hardware/firmware target и current-state EN/RU пары обновлены согласованно;
- `IMP-0010` не переоткрыт и остаётся отложен до сводного pin budget;
- относительные ссылки изменённых документов проходят проверку.

## Результат

System/UI/storage capability-срез этапа 2 получил статус **«Проведено ревью»**. Это принимает продуктовые требования, но не объявляет готовыми firmware, pin-map, USB composite profile, update lifecycle implementation или hardware STOP.
