# REV-0005X — deep-cell policy propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0067`](../decisions/DEC-0067-no-in-device-deep-cell-recovery.md)
- Analysis: [`PWR-0007`](../architecture/PWR-0007-max17320-2s-surrounding-circuit.md)

## Review result

| Check | Result |
|---|---|
| owner choice | pass: `IMP-0056/A` is accepted; the product refuses cells below the qualified floor |
| recovery boundary | pass: ZVC/prequal are disabled in-product; research recovery is an external isolated Controlled-Zone fixture operation only |
| exact FET topology | pass: MAX17320 `CHG` is referenced to `IN` and `DIS` to `PCKP`; active `CSD87313DMST` provides the required common-drain pair |
| lifecycle | pass with correction: onsemi `FDMC8030` is rejected as `Last Shipments`; TI lists the accepted replacement as active production |
| exact physical contacts | pass: all eight CSD87313DMS package contacts, both fuses, shunt, NTCs, dual hold FET and source-isolation diodes exist in machine source |
| slot independence | pass at principle level: each physical cell has its own fuse and NTC box/path |
| reset default | pass at topology level: Q1 holds ALRT low without MCU code; Q2 releases only from admitted `PA6` |
| supply isolation | pass at topology level: AOLDO/fixture use BAV70 common-cathode OR; admitted system 3V3 uses a lower-drop BAT54 branch |
| GPIO budget | pass: PA24/PA25 are consumed as midpoint/stack ADC evidence; `12/3/3` accounts every admission-controller GPIO |
| machine/visible artifacts | pass: exact MPNs, routes, vertical atlas and both product diagrams derive from the same JSON source |
| firmware contract | pass at documentation level: no runtime recovery command; protected image and admission behavior remain fail-closed |
| remaining proof | open by design: passive values, diagnostic load, mechanical polarity/NTC coupling, hot loss, source handover and fault HIL |
| CAD boundary | pass: no KiCad authorization is implied |

## Conclusion

`DEC-0067` receives **«Проведено ревью»** at the principle/electrical-contract
level. The rail-tree continuation is now reviewed by
`PWR-0008/DEC-0068/REV-0005Y`; the listed passive and HIL closures remain
explicit prerequisites for atomic architecture acceptance.
