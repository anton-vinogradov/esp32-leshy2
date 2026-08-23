# Пакет приёмки production ECAD H2

[English](h2-acceptance.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Схемы](schematics.ru.md)

H2 готов к формальной пользовательской приёмке как вход H3. Приёмка означает согласие с production schematic-контрактом, а не разрешение KiCad layout, закупки или печати.

## Что завершено

- четыре полные native KiCad-иерархии: UI, RF/power, display-adapter и LoRa Cap
- независимое power/recovery/isolation/quiet-state/fault-shutdown ревью
- нулевой native ERC и 189 физически сопоставленных намеренных NC
- 1 028 ledger-строк, 1 026 электрических identities, 266 root nets и 80 M1 contacts сверены
- 130 controller allocations совпадают с KiCad; 125 MCU-контактов byte-identical в firmware F2

## Что сознательно остаётся за границей H2

- `H3` — виртуальные worst-case и timing/transient проверки
- `firmware F3` — сборка и emulator-прогон до заказа
- `H5` — проверка полученных образцов и land-fit
- `H6` — placement/routing/DRC
- `H8` — физический bring-up и HIL

**Текущий маркер:** `H2.8.2` — требуется решение пользователя принять H2 как вход H3 либо вернуть с конкретным замечанием.

[Машинный пакет](../hardware/ecad/generated/H2-REV81-acceptance-package.json).
