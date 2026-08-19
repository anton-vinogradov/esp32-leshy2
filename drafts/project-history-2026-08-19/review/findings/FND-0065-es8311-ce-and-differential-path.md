# FND-0065 — ES8311 CE is not enable and its analog path is differential

- Статус: **Digital/contact mismatch исправлено; topology принято DEC-0054, analog/HIL открыт**
- Серьёзность: schematic/audio-function blocker
- Обнаружено: 2026-08-17
- Исправление: [`AUDIO-0001`](../architecture/AUDIO-0001-es8311-exact-electrical-fit.md)
- Решение: [`DEC-0054`](../decisions/DEC-0054-fail-safe-complete-audio-path.md)

## Находка

Прежние документы называли третий slow-control `codec enable/reset` и
описывали DAC как один сигнал, входящий в один speaker selector. Exact ES8311
contact review показал:

1. `CE` (physical 20) выбирает I2C address; hardware enable/reset у ES8311 нет.
2. DAC — `OUTP/OUTN`, ADC — `MIC1P/MIC1N`; это дифференциальные пары.
3. Legacy RX mux, legacy PAM8302 wiring and SA518 `MIC_IN` are represented as
   single-ended paths. Direct «DAC → selector» leaves conversion and signal
   level undefined.

## Исправление

- exact QFN-20 contacts instantiated in `devices.json/G2F-3I`;
- S3 I2C/I2S peers now terminate on physical ES8311 contacts;
- `P10` renamed `CODEC_PWR_EN` and terminates on an external power switch;
- `CE` is explicitly strapped high through the documented `10 kΩ` reference
  for address `0x19`;
- `MCLK` is explicit NC under BCLK-derived-clock contract;
- differential analog pairs end on qualified conditioner/routing blocks.

Digital pin fit is corrected and regression-tested. `DEC-0054` subsequently
selects and instantiates the exact active buffer, selectors, safe gate and amp.
Passive values, power and analog/HIL proof remain open before schematic freeze.
