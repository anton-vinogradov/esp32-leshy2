# REV-0005O — I2 safety decision propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0061`](../decisions/DEC-0061-aon-stop-and-per-path-tx-evidence.md)
- Circuit: [`SAFE-0002`](../architecture/SAFE-0002-accepted-aon-stop-and-evidence-circuit.md)
- Machine source: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)

## Проверено

| Проверка | Результат |
|---|---|
| owner choice | pass: `IMP-0050/A` принят; B не выбран, C остаётся rejected |
| three-domain STOP | pass: exact fan-out завершает S3 `EN`, C5 `EN`, RP `RUN` |
| AON loss | pass on paper: Ioff buffer/logic plus local reset/enable pulls produce safe state |
| async truth table | pass: STOP `/PRE` dominates POR `/CLR`; held RE-ARM cannot release |
| TX gate inventory | pass: 3×nRF CE + nRF/CC/voice/accessory rails + IR waveform + active-low PTT accounted |
| evidence inventory | pass: seven RF detectors + one optical detector; no shared nRF proof |
| RP pin budget | pass: existing GPIO22 becomes aggregate; source mask shares local I²C0; budget remains `48/0/0` |
| critical indicators | pass: exact red ANY-TX and orange STOP devices; both independent of UI/firmware |
| U214 boundary | pass: accessory-local RF without evidence remains explicit unknown |
| exact added parts | pass: buffer, diode arrays and indicators checked for specs/lifecycle/dated availability |
| machine projection | pass: each new physical device is a separate instance/node with MPN and role |
| target site | pass: EN/RU hardware landing diagrams include accepted components without review chronology |
| current state | pass: EN/RU hardware/firmware pages separate completed I2 paper review from I3/I6/HIL work |
| structural checks | pass: generator check and architecture regression suite |

## Саморевью отказов

The initial option text said only that reset outputs would have off-safe pulls.
That was insufficient because module-side pull-ups could create an undefined
divider after AON loss. The accepted propagation adds `SN74LVC3G34DCUR` with
Ioff plus `1 kΩ` local reset pull-downs and an explicit `≥10 kΩ` upper bound on
any application-side pull-up. This correction preserves the owner's accepted
function and is now machine-recorded instead of remaining narrative intent.

`BAT54A,215` was screened for the hardware OR but had poor dated distributor
availability. Exact `BAT54ALT1G` provides the same dual-common-anode topology
with observed stock. This is a no-function-loss sourcing correction.

## Remaining downstream work

- `I3`: AON source/hold-up, all rail switches, discharge, charging/battery,
  reverse current, current/loss/thermal budget;
- `I6`: RF taps/matching, thresholds/hysteresis, IR analog front end, detector
  coupons and coexistence;
- HIL: every named fault and latency/decay/false-state pass condition.

These are assigned proofs rather than ambiguous paper holes. `I2` is therefore
**Проведено ревью**; `I3` becomes the active internal block.
