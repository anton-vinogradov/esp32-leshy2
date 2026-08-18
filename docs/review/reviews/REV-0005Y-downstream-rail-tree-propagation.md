# REV-0005Y — downstream rail-tree propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0068`](../decisions/DEC-0068-separate-fixed-downstream-rails.md)
- Analysis: [`PWR-0008`](../architecture/PWR-0008-exact-downstream-rail-tree.md)

## Review result

| Check | Result |
|---|---|
| source boundary | pass: all four converters start at `BQ25798 SYS`; pack AOLDO remains local to admission |
| rail independence | pass: fixed 3.3/4.0/5.0-V feedback stages are physically separate; no shared 4/5-V selector exists |
| exact package contacts | pass with correction: `TPS564252DRLR` pin 4 is `PG`, integrated bootstrap means there is no external BST pin |
| current/ripple headroom | pass at paper level: all three accepted transient peaks stay below exact inductor saturation floors and the 4-A converter rating |
| AON capacity | pass: `TPS629203DRLR` and 1.7-A-saturation WPN inductor exceed the 5/8-mA safety envelope; MAX17320 AOLDO is rejected for this role |
| nRF concurrency | pass: one 1.5-A branch switch powers three independent radios without serializing SPI/CE/IRQ or weakening the full-mix requirement |
| quiet-state branches | pass at topology level: separate reset-off TPS22919 packages serve nRF, CC, SD, codec and receiver; QOD/fall time remains measured HIL |
| external backfeed/fault | pass at topology level, amended by `DEC-0069`: latch-off TPS259470L is last before the connector, blocks reverse current and exposes `FLT`; passive discharge remains value/HIL work |
| availability | pass at selection time: all exact active parts have manufacturer status and assembly/authorized-channel stock evidence |
| cost reduction | pass: identical buck and switch MPNs reduce line/setup count while independent packages preserve failure isolation |
| machine/visible artifacts | pass: exact packages and routes are represented separately in machine source and the generated vertical diagrams |
| firmware contract | pass at documentation level: fixed rail IDs, PG/fault sequencing and refusal states propagate to runtime input |
| remaining proof | open by design: passives/DC-bias, copper/thermal, source handover, discharge timing and fault-injection HIL |
| CAD boundary | pass: no KiCad authorization is implied |

## Conclusion

`DEC-0068` receives **«Проведено ревью»** for the active rail topology and
exact first targets. `I3` continues to passive values, hot loss and HIL rather
than moving to KiCad or the external mockup.
