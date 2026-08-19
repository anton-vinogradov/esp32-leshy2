# REV-0005BC — I6 consolidated proof propagation

- Статус: **Проведено ревью paper qualification scope; physical HIL open**
- Decision: [`DEC-0097`](../decisions/DEC-0097-one-group-i6-qualification-and-fixtures.md)
- Architecture: [`COX-0001`](../architecture/COX-0001-consolidated-i6-qualification-matrix.md)

## Проверка

| Consumer | Result |
|---|---|
| signal-group catalog | pass: all nine base/wildcard groups are covered exactly once; only declared intragroup concurrency remains |
| cross-group semantics | pass: all runtime pairs are prohibited; Laboratory injection cannot promote them |
| quiet states | pass after `FND-0104`: receiver, codec/audio and voice interfaces have independent measurable contracts |
| endpoint inputs | pass: nRF/native/CC/voice/IR/Si4732 remaining HIL now references foreign groups quiet plus system-plane aggression rather than another active group |
| fixtures | pass on paper: configuration, conducted, OTA, nRF observer, optical, digital timing, fault and thermal functions each have required outputs |
| no-stall | pass on paper: every existing resource deadline is named in the same acceptance trace set |
| STOP/evidence | pass on paper: seven RF plus one optical channel, false-negative rejection and ordered group shutdown are mandatory |
| budgets | pass: no new component, GPIO, rail, power or cost |
| physical evidence | explicitly open/not executed; failure reopens the owning I6 subblock |

## Result

I6 receives **«Проведено ревью»** for paper electrical and qualification scope.
This does not claim RF, optical, thermal, legal or timing measurements. I7 is
the next paper dependency; KiCad and the integrated mockup remain blocked until
the full internal chain and I9 self-review are complete.

