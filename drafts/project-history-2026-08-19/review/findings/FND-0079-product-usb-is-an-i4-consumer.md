# FND-0079 — product USB is an I4 consumer, not an I3 charger passive

- Статус: **Исправлено**
- Дата: 2026-08-18
- Corrected in: [`INT-0001`](../architecture/INT-0001-internal-design-closure-sequence.md), machine `G2F-3I`
- Propagation review: [`REV-0005AF`](../reviews/REV-0005AF-bq25798-passive-profile.md)

## Finding

`INT-0001` already defines product USB-C, USB2 protection and the UI/storage
electrical plane as `I4`, with `I3` as a prerequisite. The machine
`power_contract.remaining_i3` nevertheless still listed the exact product
USB-C receptacle and USB2 ESD as unfinished `I3` work.

That ordering is impossible: accepting an `I4` endpoint cannot be required to
finish its own prerequisite. It also obscured a real `I3` remainder — exact
TPS25751/CAT24C512 support passives and straps — behind an unrelated connector
task.

## Correction

- exact product USB-C receptacle and USB2 ESD/signal integrity move to the
  explicit machine `deferred_i4` list;
- exact BQ25798 passives close in `PWR-0014/DEC-0075`;
- TPS25751/CAT24C512 surrounding passives and configuration straps are named
  as the next real `I3` paper dependency;
- no physical route, GPIO, accepted USB role or product behavior changes.

This is a workflow/status correction, not a new product decision.
