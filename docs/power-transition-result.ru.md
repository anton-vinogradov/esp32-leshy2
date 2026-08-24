# Результат проверки переходов питания

[English](power-transition-result.md) · [На главную](../README.ru.md) · [Startup/KILL](power-transition-startup.ru.md) · [Handover](power-handover.ru.md) · [Inrush](inrush-load-step.ru.md) · [Watchdog/UI](watchdog-fault-display.ru.md)

H3.2 сведена в одну проверенную цепочку: startup/KILL → USB↔pack/brownout → eFuse/inrush/load-step → watchdog/retained reason.

- `7` startup/shutdown последовательностей, `7` handover-состояний, `5` rail startup envelopes и `6` fault-сценариев проходят без незакрытых аналитических failures.
- Самый ранний re-arm — `48.444 мс`, запас после max POR — `20.444 мс`.
- Watchdog гарантированно обнаруживает отсутствие обслуживания не позже `1760 мс`.
- Исправлены две реальные source-ошибки: полярность/async inputs защёлки и неверная POR timing claim.
- Физические waveform, switch bounce, MLCC DC-bias, charger-loop droop и fault-injection не объявлены доказанными: они явно переданы H8.

**Статус:** `H3.2` проверено. Точный текущий маркер — `H3.4.2`: digital levels/defaults и no-back-power.

[Machine closure package](../hardware/verification/generated/H3-VRF25-transition-consolidation.json).
