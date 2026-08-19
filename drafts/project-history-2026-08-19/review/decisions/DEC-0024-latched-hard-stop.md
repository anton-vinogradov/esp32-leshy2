# DEC-0024 — latched hard STOP с физическим re-arm

- Статус: **Принято; проведено ревью**
- Дата: 2026-08-16
- Основание: владелец принял рекомендуемый вариант `IMP-0022/A`
- Этап: 3 — системная архитектура и владение
- Затрагивает: `DM-SAFE-01`, `FND-0007`, `IMP-0010`, все compute domains, каждый TX-capable domain

> Последующая архитектурная поправка 2026-08-17: историческое «оба MCU»
> означало S3+C5 до появления актуального трёхдоменного `G2F-3I`. Принятый
> hard-STOP invariant применяется также к `RP2354B RUN`; иначе продолжал бы
> работать владелец 3×nRF24, CC1101, voice и U214. Расхождение зафиксировано
> `FND-0071/REV-0005M`.

## Решение

1. Физический STOP асинхронно защёлкивает независимый hardware `TX_KILL`.
2. `TX_KILL` удерживает ESP32-S3, ESP32-C5 и RP2354B в reset через их
   hardware `CHIP_PU/RUN` paths.
3. Он отдельно power-cuts или аппаратно inhibits каждый внешний TX-capable RF/IR/accessory domain; одного reset MCU недостаточно.
4. Voice PTT принудительно возвращается в RX, разрешение PA снимается, IR driver получает независимый off path.
5. Защёлкнутый STOP имеет собственную видимую индикацию, не зависящую от UI.
6. Отпускание кнопки не снимает STOP. Re-arm требует отдельного физического действия при отпущенной кнопке либо power cycle; одна firmware-команда не может выполнить re-arm.
7. После re-arm все compute domains проходят обычный boot. Все TX остаются
   off, прежние channel/power/target/payload/session/lease не восстанавливаются.
8. STOP не задерживается ради записи журнала. Потеря активной UI/radio/capture session является принятой ценой независимого аварийного прекращения TX.

## Граница решения

- Exact latch/supervisor/load-switch/gate BOM, rail partition и measured kill time выбираются и доказываются на этапах 4–9.
- `DM-SAFE-02` actual-TX detection остаётся отдельным требованием: enable state и STOP state не выдаются за измерение фактического излучения.
- Решение принимает safety topology, но не принимает matrix/U14/pin-map часть `IMP-0010`.
- `FND-0007` закрыт на архитектурном уровне и остаётся открытым как implementation/HIL finding, пока legacy I²C-only artifact не заменён и fault injection не пройден.

## Обязательная проверка

HIL должен измерить прекращение каждого TX path при active TX, hung S3, hung
C5, hung RP, stalled I²C, update/reset, brownout и attached-accessory fault.
Ни отпускание STOP, ни reboot не могут автоматически восстановить передачу.
