# REV-0004X — QSPI display decision propagation

- Статус: **Проведено ревью принятого QSPI-first working contract**
- Дата: 2026-08-17
- Decision: [`DEC-0052`](../decisions/DEC-0052-qspi-first-display-path.md)
- Proposal: [`IMP-0044`](../improvements/IMP-0044-qspi-first-fast-display-path.md)
- Closed finding: [`FND-0061`](../findings/FND-0061-stale-display-quantum-after-u214-move.md)

## Проверено

| Проверка | Результат |
|---|---|
| owner answer recorded | pass: `IMP-0044/A` accepted |
| machine pin source updated | pass: S3 GPIO41/42 allocated to QSPI D2/D3 |
| shared D1 represented honestly | pass: GPIO4 is bidirectional LCD D1/SD MISO with explicit high-Z/contention proof |
| stale byte limit removed | pass: `<=1 ms` measured occupancy replaces `256 B` |
| optional TE consumed silently | no: GPIO43 remains free until exact-panel/HIL proof |
| new compute/update domain added | no |
| pin accounting | pass: S3 `31/3/2`, C5 `14/6/1`, RP `48/0/0` |
| target/current-state and firmware propagation | pass |
| exact screen falsely accepted | no: `DSP-0003/IMP-0045` keep it open |
| generator regressions | pass |

## Результат

`DEC-0052` получает **«Проведено ревью распространения»**. Это обновляет
principled working map, но не закрывает exact display, optics, physical layout,
shared-bus SI/HIL or atomic architecture.
