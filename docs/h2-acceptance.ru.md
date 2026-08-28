# Исторический пакет приёмки production ECAD H2 · R1

[English](h2-acceptance.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Схемы](schematics.ru.md)

Этот принятый пакет сохранён как воспроизводимое evidence прежней одно-RP архитектуры R1. Он не является текущей R2-архитектурой и не разрешает R2 KiCad, закупку или печать.

## Что завершено

- четыре полные native KiCad-иерархии: UI, RF/power, display-adapter и LoRa Cap
- независимое power/recovery/isolation/quiet-state/fault-shutdown ревью
- нулевой native ERC и 202 физически сопоставленных намеренных NC
- 1 081 ledger-строк  1 079 сопоставленных электрических identities  270 root nets и 80 M1 contacts сверены
- 130 controller allocations совпадают с KiCad; 125 MCU-контактов семантически идентичны в firmware F2, а импорт помечен fail-closed historical R1
- два независимых SA818S-V/U тракта имеют собственные SMA и TX evidence; one-hot selector не расходует новый MCU или M1 contact

## Что сознательно остаётся за границей H2

- `H3` — виртуальные worst-case и timing/transient проверки
- `firmware F3` — сборка и emulator-прогон до заказа
- `H5` — проверка полученных образцов и land-fit
- `H6` — placement/routing/DRC
- `H8` — физический bring-up и HIL

**Исторический результат:** ✅ ревизия `H2.8.2-R1` была принята пользователем 2026-08-26 и остаётся связанной SHA-256. Она явно запрещена как authority для R2. Текущий аппаратный маркер — `H1-R2.32`.

[Машинный пакет](../hardware/ecad/generated/H2-REV81-acceptance-package.json).
