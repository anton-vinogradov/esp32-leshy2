# REV-0005AA — switched-rail PG qualification propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0070`](../decisions/DEC-0070-enable-qualified-switched-rail-pg.md)
- Analysis: [`PWR-0009`](../architecture/PWR-0009-enable-qualified-switched-rail-pg.md)

| Surface | Result |
|---|---|
| exact devices | pass: machine source contains two physical instances of exact `MMBT3904-7-F`, contacts `1 B / 2 E / 3 C` |
| fault routes | pass: direct optional `PG → POWER_FAULT_N` routes are absent; collectors expose `VOICE_4V_FAULT_QUAL_N` and `EXT_5V_FAULT_QUAL_N` |
| enable dominance | pass: each base is driven through its own 68-kOhm series resistor from the same STOP-dominant safe EN as its converter |
| truth table | pass on paper: only `EN=1, PG=0` sinks; optional-off states release the aggregate |
| electrical level | pass at datasheet-screen level: conservative 0.6-V low remains below 0.99-V P25 input limit |
| visible diagrams | pass: both target README diagrams and the generated atlas show two separate MPN+role transistor boxes |
| firmware | pass: runtime treats qualified low during start as bounded pending evidence, then latches timeout/fault; normal off is not a fault |
| cost/function | pass: no GPIO or diagnostic function is lost; checked recurring addition is about `$0.032` per board before assembly |

Generator/checks guard the exact instances and reject restoration of the two
direct PG routes. Exact passive MPN, temperature/HIL levels and transition
deadlines remain I3 work; this review does not authorize KiCad.
