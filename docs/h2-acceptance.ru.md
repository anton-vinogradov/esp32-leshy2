# Пакет приёмки production ECAD H2

[English](h2-acceptance.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Схемы](schematics.ru.md)

Текущая ревизия H2 принята пользователем как неизменяемый исходный материал повторного прогона H3. Приёмка означает согласие с production schematic-контрактом, а не разрешение KiCad layout, закупки или печати; позднее несоответствие повторно открывает затронутый gate.

## Что завершено

- четыре полные native KiCad-иерархии: UI, RF/power, display-adapter и LoRa Cap
- независимое power/recovery/isolation/quiet-state/fault-shutdown ревью
- нулевой native ERC и 202 физически сопоставленных намеренных NC
- 1 081 ledger-строк  1 079 сопоставленных электрических identities  270 root nets и 80 M1 contacts сверены
- 130 controller allocations совпадают с KiCad; 125 MCU-контактов byte-identical в firmware F2
- два независимых SA818S-V/U тракта имеют собственные SMA и TX evidence; one-hot selector не расходует новый MCU или M1 contact

## Что сознательно остаётся за границей H2

- `H3` — виртуальные worst-case и timing/transient проверки
- `firmware F3` — сборка и emulator-прогон до заказа
- `H5` — проверка полученных образцов и land-fit
- `H6` — placement/routing/DRC
- `H8` — физический bring-up и HIL

**Результат:** ✅ ревизия `H2.8.2-R1` принята пользователем 2026-08-26; точный baseline связан SHA-256 всех перечисленных входов, поэтому не зависит от ещё не созданного commit hash. Предыдущая SA518-ревизия заменена. Следующий аппаратный маркер — `H3.0.1-R1`.

[Машинный пакет](../hardware/ecad/generated/H2-REV81-acceptance-package.json).
