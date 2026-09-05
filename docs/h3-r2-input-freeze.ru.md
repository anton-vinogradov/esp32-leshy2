# H3-R2.0.1 · фиксация входов виртуальной проверки

[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [English](h3-r2-input-freeze.md)

Проведено ревью точного входа H2-R2.1.5: `2` проекта, `22` листа, `1208` устанавливаемых symbols, `4306` физических pins и `789` nets. Все входы захешированы; любое изменение закрывает воспроизводимость до повторной генерации.

Freeze SHA-256: `0ea6b23c3e1cbe9000818a3f1584449afec15d9b3cbaf65ba5ca24f42db6bbd9`

| Работа | Основной охват | Листы | Критерий |
|---|---|---:|---|
| `H3-R2.1` | Worst-case DC, source, charge and power-state verification | 2 + 0 shared parameter groups | Every legal source/load state has positive voltage, current, thermal and protection margin at tolerance corners. |
| `H3-R2.2` | Startup, shutdown, handover, brownout, inrush and watchdog verification | 2 + 12 shared parameter groups | Every legal transition reaches a bounded safe state; every illegal or stalled transition fails closed with diagnosable state retention. |
| `H3-R2.3` | Display, audio, IR, battery and Airband analog-corner verification | 3 + 0 shared parameter groups | Every selected analog path meets its stated amplitude, bandwidth, noise, load and fail-off limits at reproducible corners. |
| `H3-R2.4` | Digital levels, timing, loading and direct-i8080 verification | 8 + 0 shared parameter groups | Every digital boundary has positive level/timing margin, deterministic ownership and a recoverable reset/service state without payload contention. |
| `H3-R2.5` | RF feeds, coexistence, quiet states and 3x nRF24 concurrency | 3 + 0 shared parameter groups | Each RF port has one bounded owner and quiet state; three nRF24 paths remain concurrently serviceable; no inactive path can transmit or load the active group unexpectedly. |
| `H3-R2.6` | Thermal, single-fault and unattended-operation verification | 2 + 0 shared parameter groups | No accepted single fault defeats the independent hard-off path; thermal/watchdog faults remove hazardous power while preserving a readable cause when energy remains. |
| `H3-R2.7` | Cross-check, physical residual register and phase report | 2 + 0 shared parameter groups | All prior H3 workstreams pass on one source revision and every remaining uncertainty is physical-only with one downstream owner. |

> Этот шаг разрешает только расчёты и симуляцию. Placement, routing, закупка и печать остаются запрещены.
