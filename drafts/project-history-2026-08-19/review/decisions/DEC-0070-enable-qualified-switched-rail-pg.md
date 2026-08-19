# DEC-0070 — enable-qualified switched-rail PG evidence

- Статус: **Принято владельцем; распространено**
- Дата: 2026-08-18
- Analysis: [`PWR-0009`](../architecture/PWR-0009-enable-qualified-switched-rail-pg.md)
- Propagation review: [`REV-0005AA`](../reviews/REV-0005AA-switched-rail-pg-qualification.md)

## Context

В accepted rail tree опциональные `VVOICE_4V` и `5V_EXT` выключены в quiet
state. Их `TPS564252.PG` при этом low, поэтому ранний прямой wired-low маршрут
в `POWER_FAULT_N` ошибочно объявлял штатное выключение аварией.

## Decision

1. Voice и accessory rail получают по одному отдельному физическому
   `Diodes Incorporated MMBT3904-7-F` в SOT-23.
2. Base каждого qualifier получает тот же STOP-dominant safe `EN` через
   68-kOhm 1% series resistor; emitter получает соответствующий open-drain
   `PG`; collector входит в общий wired-low `POWER_FAULT_N`.
3. Единственное fault-состояние qualifier — `EN=1 && PG=0`. `EN=0` всегда
   освобождает aggregate, поэтому штатно выключенная шина не является fault.
4. Direct `VOICE_4V_PG_N/EXT_5V_PG_N → POWER_FAULT_N` routes запрещены.
   Voice PG по-прежнему независимо удерживает локальный voice reset/PD.
5. Low во время включения является bounded transition evidence. Firmware ждёт
   release до measured deadline и только затем принимает rail либо защёлкивает
   timeout/fault; automatic retry запрещён.
6. Main-rail PG остаётся прямым evidence: без `3V3_MAIN` сам P25 diagnostic
   domain не работает, поэтому optional-off ambiguity к нему не относится.
7. [`DEC-0073`](DEC-0073-exact-converter-control-passives.md) subsequently
   closes the exact base, PG, EN and aggregate resistor MPNs. Thermal corners
   and HIL remain prototype gates; это решение не разрешает KiCad.

The accepted option preserves converter-specific hardware evidence, consumes
no GPIO and adds roughly `$0.032` per board at the checked 50-piece price.
