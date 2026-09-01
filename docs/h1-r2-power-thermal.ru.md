# H1-R2.4 · питание и тепловой запас

Шесть вычислительных доменов и все взаимоисключающие сигнальные группы пересчитаны до production-ECAD. Это принятый рабочий силовой дизайн H1, а не разрешение начинать KiCad или заказ.

![H1-R2 rail and thermal architecture](images/h1-r2-power-thermal.svg)

## Результат

- Худшая группа — `NRF24`: `3.063 А` на `3V3_MAIN`. Приняты `3.75 А` continuously и `4.25 А` step; запас до continuous-границы — `0.687 А` (`22.4%`).
- `TPS566231PRQFR` сохраняет отдельный диагностический Power-Good и даёт 6-А класс. `TPS25974LRPWR` с `RC0402FR-071K18L` гарантирует порог `4.340–5.412 А`: step проходит, а eFuse срабатывает раньше минимального current-limit преобразователя.
- `PSPMAA0605H-2R2M-ANP` имеет 10-А RMS / 15-А saturation. Расчётный пик при принятом step — `5.002 А`.
- Три входных и три выходных `GRM32ER71E226KE15L` размещены отдельными корпусами. H3 обязан доказать не номинальную, а эффективную ёмкость не меньше 30/44 мкФ с bias, температурой и допуском.
- При 45°C ambient консервативная оценка eFuse на 3,75 А даёт `80.0°C`; H3 должен подтвердить КПД преобразователя не хуже `89.9%` и полный тепловой путь корпуса.

## Выбранные фабричные позиции

| Exact MPN | JLCPCB | Role / current route |
|---|---|---|
| `TPS566231PRQFR` | [`C3190178`](https://jlcpcb.com/partdetail/TexasInstruments-TPS566231PRQFR/C3190178) | 112 pieces, MOQ 1, USD 1.0478 at quantity 1, Extended SMT / Standard PCBA |
| `PSPMAA0605H-2R2M-ANP` | [`C2983088`](https://jlcpcb.com/partdetail/PRODTech-PSPMAA0605H2R2MANP/C2983088) | 627 pieces, MOQ 1, USD 0.1735 at quantity 1, Extended SMT / Standard PCBA |
| `TPS25974LRPWR` | [`C3662931`](https://jlcpcb.com/partdetail/TexasInstruments-TPS25974LRPWR/C3662931) | 2,915 pieces, MOQ 1, USD 0.9763 at quantity 1, Extended SMT / Standard PCBA |
| `RC0402FR-071K18L` | [`C273709`](https://jlcpcb.com/partdetail/YAGEO-RC0402FR071K18L/C273709) | 5,864 pieces, MOQ 1, USD 0.0025 at quantity 1, Extended SMT / Standard PCBA |
| `GRM32ER71E226KE15L` | [`C21397`](https://jlcpcb.com/partdetail/MurataElectronics-GRM32ER71E226KE15L/C21397) | 116,360 pieces, MOQ 1, USD 0.6222 at quantity 1, Extended SMT / Standard PCBA; recheck at freeze |
| `CL10B105KO8NNNC` | `C59782` | 631,719 pieces, MOQ 1, USD 0.0210 at quantity 1 |
| `CL05B104KB5NNNC` | `C960916` | 754,861 pieces, MOQ 1, USD 0.0093 at quantity 1 |
| `RC0402JR-070RL` | [`C60485`](https://jlcpcb.com/partdetail/YAGEO-RC0402JR070RL/C60485) | 4,551,848 pieces, MOQ 1, USD 0.0034 at quantity 1, Extended SMT / Standard PCBA |

## Что ещё проверяет H3

- DC-bias, tolerance and temperature effective capacitance at 6.0-8.4 V input and 3.222 V output
- WEBENCH or equivalent switching-loss model at 2.823-A worst enumerated load and 3.75-A admission limit
- extracted switch-loop and power-plane parasitics
- 0.1-to-4.25-A load-step simulation and protected-rail droop
- board-plus-enclosure thermal solution and sensor-map update

> Маркер результата: **H1-R2.4**. Включено в проведённое ревью H1-R2.38.
