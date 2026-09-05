# Thermal, единичные отказы и длительная работа · H3-R2.6

[English](thermal-fault-electrical-verification.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md)

`H3-R2.6` проведён ревью: **25 checks**, `56` thermal-профилей и `30` single-fault сценариев проходят без открытых аналитических findings. Итоги H3-R2.7, H4-R2 и H5-R1 также проведены ревью; текущий маркер — `H6.0.3-R1`.

## Тепло

Для длительной thermal-квалификации допускается только support-нагрузка `SUPPORT_IDLE`; внешний 5-В порт ограничен 1,00 А. Худший непрерывный расчётный профиль — `VOICE/PTT_TX_MAX/SUPPORT_IDLE`: консервативно `7.418 Вт` внутри корпуса. При 35 °C H6 должен обеспечить не хуже `4.044 K/W` до предупреждения 65 °C. Сам этот TX-профиль остаётся ограниченной сессией до H8, а не разрешением на unattended TX. Абсолютный electrical corner `VOICE/PTT_TX_MAX/SUPPORT_WORST` даёт `16.596 Вт`, но не разрешён как длительный режим. Три NTC, пороги warning/kill/rearm и charger `TREG=60 °C`, `TSHUT=85 °C` остаются независимыми защитами. Это параметрическая верхняя граница, не обещание температуры готового корпуса.

## Единичные отказы

Все 30 сценариев имеют обнаружение, основной и независимый/fail-safe путь, безопасный исход и физическое восстановление. Максимальный бумажный detection deadline — 1760 мс у независимого watchdog. Автоматического или программного re-arm нет; fault-plane проверяется при каждом физическом `KILL → RUN`.

## Длительная работа

Долгая работа питается от квалифицированного USB-PD. `24/48 часов` — длительность неразрушающего H8 soak и интервал полной проверки, а не обещание автономности. Настройка доступна только локально; по умолчанию 48 часов. Просрочка сначала снимает TX leases, затем останавливает сессию и требует физический re-arm. Watchdog и температурные пределы этой настройкой не меняются.

## Что осталось физическим

- H6: solve the routed copper, vias, component spreading and enclosure thermal network; meet every admitted profile's 35-C resistance ceiling
- H6: keep RUN_PERMIT and FAULT_ASSERT_N routes, pads, returns and endpoint buffers physically independent
- H8: map POWER, RF/VOICE, UI/display, both cells, charger and external surfaces at each admitted sustained profile
- H8: inject SF-R2-01 through SF-R2-30 with current-limited fixtures/emulators and verify safe output, retained cause and physical-only re-arm
- H8: calibrate all thermal/evidence thresholds and measure watchdog, eFuse, reset, QOD and residual-energy timing
- H8: run ordinary non-destructive 24/48-hour qualified-USB soak plus battery-to-protected-cutoff measurement without converting it into an uptime promise
- H8: interrupt each journal boundary and verify last-valid-slot or explicit AON-loss fallback

Placement/routing, закупку, печать и итоговые thermal/safety заявления этот результат не разрешает.

[Машинное evidence](../hardware/verification/generated/H3-R2-thermal-fault.json).
