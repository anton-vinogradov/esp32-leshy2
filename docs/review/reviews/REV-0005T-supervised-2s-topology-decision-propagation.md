# REV-0005T — supervised-2S topology decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0065`](../decisions/DEC-0065-supervised-2s-battery-topology.md)
- Comparison: [`PWR-0006`](../architecture/PWR-0006-one-or-two-cell-topology-comparison.md)
- Closed proposal: [`IMP-0055`](../improvements/IMP-0055-battery-electrical-topology-after-reopen.md)

## Review result

| Check | Result |
|---|---|
| owner intent | pass: option A accepted; two individually replaceable cells remain and battery operation requires an admitted 2S pair |
| arithmetic | pass: `6.0…8.4 V`, `2.22 A` continuous and `2.78 A` bounded transient at the stated 90% assumption are retained |
| safety boundary | pass at architecture level: reverse insertion, wrong cell, mismatch, one-cell state, reset and contact bounce remain fail-closed requirements |
| charger | pass at device-class level: exact `BQ25798RQMR` supports 2S and is now explicitly configured for two cells |
| downstream rails | pass at class level: 3.3/4/5-V base rails return to buck classes; exact MPN/loss/thermal work remains open |
| target-product pages | pass: root pages and the generated vertical diagram again state supervised 2S as a finished-product property without publishing review IDs |
| firmware projection | pass: runtime input and status pages require both cells admitted and do not offer a one-cell base-product mode |
| old alternatives | pass: controlled two-slot 1S and one-slot 1S remain comparison/future-SKU evidence, not hidden base requirements |
| CAD boundary | pass: no schematic/layout authorization is implied |

## Conclusion

The topology decision and its dependent product/runtime wording receive
**«Проведено ревью»**. `I3` advances to the exact fail-closed manager gate in
`PWR-0005/IMP-0054`; passives, rail calculations and HIL remain downstream.

