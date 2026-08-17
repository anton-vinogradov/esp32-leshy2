# REV-0005P — I3 power prerequisite review

- Статус: **Проведено ревью пререквизитов; owner decision открыт**
- Дата: 2026-08-18
- Artifact: [`PWR-0002`](../architecture/PWR-0002-i3-power-prerequisite-audit.md)
- Finding: [`FND-0073`](../findings/FND-0073-legacy-power-is-not-a-current-target.md)
- Proposal: [`IMP-0052`](../improvements/IMP-0052-safe-field-replaceable-2s-pack.md)

## Reviewed

| Check | Result |
|---|---|
| current hardware set | pass: deleted onboard GNSS/LoRa/SA868/WS2812 loads do not survive in target sizing |
| accepted I2 load | pass: AON continuous/transient minimum included |
| legal concurrency | pass: sizing uses named scenarios and SG-N24 full mix, not all-radio maximum fiction |
| 3.3-V floor | pass: retained `2.5 A` continuous / `3 A` load step; old 2-A rail rejected |
| voice | pass: accepted independent 4.0-V 1.25/1.5-A envelope retained |
| external 5 V | pass: reverse-safe profile branch separated from internal auxiliary loads |
| old charger facts | pass: BQ25887 ADC/balancing retained as facts; power-path/fuel-gauge claims rejected |
| Type-C input | pass: Rd role declaration separated from source-current detection |
| historical source handling | pass: old tsCircuit remains unmodified reference; no premature KiCad/BOM |
| extra legacy behavior | pass: separate loose-cell replacement is presented to owner, not silently removed |

## Result

The `I3` prerequisites are **Проведено ревью**. `I3` itself remains active.
The next dependency is one owner answer to `IMP-0052`; charger, pack manager,
rails and exact availability must not be frozen before it.

