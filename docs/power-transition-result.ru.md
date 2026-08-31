# Переходы питания и аварийное отключение · итог H3-R2.2

[English](power-transition-result.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Startup](power-transition-sequences.ru.md) · [Handover](power-handover.ru.md) · [Inrush](inrush-load-step.ru.md) · [Watchdog](watchdog-fault-display.ru.md)

Вся цепочка H3-R2.2 проверена на текущей R2-архитектуре: физический запуск и KILL → USB/pack/DPM/brownout → eFuse/inrush/load-step → watchdog, аппаратная защёлка и сохранённая причина.

| Результат | Проверено |
| --- | ---: |
| Startup/reset/recovery | 14 / 14 |
| USB/pack/DPM/brownout | 7316 / 7316 |
| Защищённые rail startups | 5 / 5 |
| Rail load-step envelopes | 4 / 4 |
| Watchdog/fault-display | 10 / 10 |

Исправлены две найденные ревью ошибки: янтарный индикатор переведён с `FAULT_ASSERT_N` на настоящий latched `FAULT_KILL`; у TPS3435 разделены `500 мкс` запуска ИС и нулевая задержка запуска watchdog-окна. Аналитических failures и путей автоматического re-arm — `0`.

Результат не разрешает placement, routing, закупку или печать. H6 повторит расчёты с извлечёнными паразитиками, H8 измерит перечисленные waveform/fault-injection cases.

**Следующая точка:** `H3-R2.3` — analog corners дисплея, аудио, IR, аккумулятора и Airband.

[Машинный пакет](../hardware/verification/generated/H3-R2-transition-result.json).
