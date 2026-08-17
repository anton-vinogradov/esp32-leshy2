# FND-0066 — ES8311 line-input warning and PAM differential capability change the optimum

- Статус: **Открыто; IMP-0046 recommendation corrected**
- Серьёзность: audio-quality/BOM/topology blocker
- Обнаружено: 2026-08-17
- Artifact: [`AUDIO-0001`](../architecture/AUDIO-0001-es8311-exact-electrical-fit.md)
- Corrected proposal: [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)

## Находка

The first output-only review recommended converting ES8311 `OUTP/OUTN` to one
single-ended signal before both selectors. Complete legacy and manufacturer
review shows why that is premature:

1. Physical `PAM8302A` already has differential `IN+`/`IN-`; only the legacy
   circuit uses `IN+` as signal and AC-couples `IN-` to ground.
2. ES8311 differential full-scale DAC output is about `1.8 Vrms` at AVDD 3.3 V.
   Preserving both legs for the speaker is therefore natural.
3. SA518 documents a typical modulation input around `10 mV`; a high-impedance
   tap from one DAC leg needs large attenuation, not an active full-swing
   differential receiver.
4. The ES8311 user guide explicitly says its fully differential ADC input is a
   microphone interface and is not recommended for line input. Selected
   Si4732/SA518 RX sources are line/audio outputs.

## Consequence

- former `IMP-0046/A` recommendation is withdrawn before owner acceptance;
- dual-pole differential switching into PAM8302A becomes the leading output
  candidate, plus a separately attenuated one-leg TX branch;
- ES8311 remains a digital-fit candidate, but its ADC line-capture suitability
  is open until passive/active conditioning and a documented-line-input codec
  alternative are compared from measured source levels;
- GPIO budget remains unchanged; the uncertainty is analog BOM/quality/area.

## Closure evidence

1. Measure or bound Si4732 and SA518 AFOUT min/nominal/max voltage, source
   impedance and DC common mode.
2. Calculate passive and active `MIC1P/MIC1N` networks against the ES8311
   `6 kΩ` differential input and accepted recording SNR/clipping margin.
3. Compare at least one current documented-line-input codec at complete-circuit
   BOM, package, power, driver, bypass and pin cost.
4. Select the complete path only after SPICE/bench proof of gain, THD+N, noise,
   pop/click, reset defaults and RF desense.

## Primary sources

- [ES8311 product brief rev 17.0](https://www.everest-semi.com/pdf/ES8311%20PB.pdf)
- [ES8311 user guide, differential microphone-input warning](https://files.waveshare.com/wiki/common/ES8311.user.Guide.pdf)
- [Diodes PAM8302A datasheet](https://www.diodes.com/datasheet/download/PAM8302A.pdf)
- [NiceRF SA518 current product specification](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html)
