# Пакет приёмки production ECAD H2

[English](h2-acceptance.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Схемы](schematics.ru.md)

H2 принят пользователем как неизменяемый исходный материал H3. Приёмка означает согласие с production schematic-контрактом, а не разрешение KiCad layout, закупки или печати; позднее несоответствие повторно открывает затронутый gate.

## Что завершено

- четыре полные native KiCad-иерархии: UI, RF/power, display-adapter и LoRa Cap
- независимое power/recovery/isolation/quiet-state/fault-shutdown ревью
- нулевой native ERC и 189 физически сопоставленных намеренных NC
- 1 035 ledger-строк, 1 033 электрических identities, 266 root nets и 80 M1 contacts сверены
- 130 controller allocations совпадают с KiCad; 125 MCU-контактов byte-identical в firmware F2

## Что сознательно остаётся за границей H2

- `H3` — виртуальные worst-case и timing/transient проверки
- `firmware F3` — сборка и emulator-прогон до заказа
- `H5` — проверка полученных образцов и land-fit
- `H6` — placement/routing/DRC
- `H8` — физический bring-up и HIL

**Результат:** ✅ `H2.8.2` принят пользователем 24 августа 2026 года на hardware commit `25d9ee2` и firmware commit `900bb2b`. Следующий аппаратный маркер — `H3.0.1`.

[Машинный пакет](../hardware/ecad/generated/H2-REV81-acceptance-package.json).
