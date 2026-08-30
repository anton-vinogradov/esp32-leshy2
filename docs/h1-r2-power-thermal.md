# H1-R2.4 · rail and thermal headroom

All six compute domains and every mutually exclusive signal group have been recalculated before production ECAD. This is the accepted H1 working power design, not authorization to start KiCad or order boards.

![H1-R2 rail and thermal architecture](images/h1-r2-power-thermal.svg)

## Result

- The worst group is `NRF24` at `3.063 A` on `3V3_MAIN`. The accepted envelopes are `3.75 A` continuous and `4.25 A` step, leaving `0.687 A` (`22.4%`) to the continuous admission limit.
- `TPS566231PRQFR` preserves a separate diagnostic Power-Good and provides the 6-A class. `TPS25974LRPWR` with `RC0402FR-071K18L` guarantees `4.340–5.412 A`: the step passes and the eFuse trips below the converter minimum current limit.
- `PSPMAA0605H-2R2M-ANP` is rated 10-A RMS / 15-A saturation. Calculated peak at the accepted step is `5.002 A`.
- Three input and three output `GRM32ER71E226KE15L` bodies are placed individually. H3 must prove at least 30/44 µF effective capacitance after bias, temperature and tolerance rather than accepting nominal values.
- At 45°C ambient, the conservative eFuse bound at 3.75 A is `80.0°C`; H3 must show at least `89.9%` converter efficiency and close the enclosure thermal path.

## Selected factory parts

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

## H3 evidence still required

- DC-bias, tolerance and temperature effective capacitance at 6.0-8.4 V input and 3.222 V output
- WEBENCH or equivalent switching-loss model at 2.823-A worst enumerated load and 3.75-A admission limit
- extracted switch-loop and power-plane parasitics
- 0.1-to-4.25-A load-step simulation and protected-rail droop
- board-plus-enclosure thermal solution and sensor-map update

> Result marker: **H1-R2.4**. Included in the reviewed H1-R2.37 result.
