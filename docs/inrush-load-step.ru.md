# Inrush и скачки нагрузки

[English](inrush-load-step.md) · [На главную](../README.ru.md) · [Итог H3.2](power-transition-result.ru.md)

Ёмкости больше не переписываются вручную: генератор собирает все реальные capacitor instances, подключённые к каждой шине, прямо из единой карты компонентов и сетей. Сейчас учтено `98` установленных конденсаторов.

| Шина | Номинальная C, мкФ | Worst active load, мА | Итог |
|---|---:|---:|---|
| `AON_SAFE_3V3` | 24.0 | 89.5 | pass_current_limited_start |
| `3V3_MAIN` | 59.7 | 2493.0 | pass |
| `VVOICE_4V` | 10.0 | 900.0 | pass |
| `5V_U214_PROTECTED` | 2.2 | 1250.0 | pass |
| `5V_UNIT_PROTECTED` | 2.2 | 1250.0 | pass |

AON eFuse при необходимости входит в current-limited ramp и остаётся с положительным запасом. Main/voice/external dV/dt ограничивают ёмкостный inrush; даже вместе с принятым worst active load минимальный current limit не пересекается.

Это доказывает current envelope, но не амплитуду короткой просадки closed-loop buck. Effective MLCC C, rail minimum и settling при named load steps остаются H8 waveforms.

**Статус:** `H3.2.3` проверено; 5/5 startup envelopes проходят. [Machine evidence](../hardware/verification/generated/H3-VRF23-inrush-load-step.json).
