# How hardware is verified before fabrication

[Русский](verification-methods.ru.md) · [Home](../README.md) · [Virtual verification](virtual-verification.md) · [Parameters](parameter-model-register.md)

H3 uses reproducible worst-case analysis rather than optimistic typical values. Every result exposes input sources, evaluated states, the worst corner, numeric margin and the physical check still required after fabrication.

## Methods

| Scope | Method | Forbidden shortcut |
|---|---|---|
| H3.1, H3.3, H3.4 | Decimal interval arithmetic over min/max tolerances plus explicit discrete operating modes | typical values may be reported but can never prove a pass |
| H3.1 | closed-form KCL/KVL and efficiency/loss envelopes evaluated at every legal source/load state | rail loads may not be hidden in an aggregate unexplained allowance |
| H3.2, H3.3 | piecewise-linear or datasheet behavioral state model with Decimal time base, explicit initial conditions and dt/dt2 convergence check | a waveform without input provenance, timestep convergence and threshold markers is non-evidence |
| H3.2, H3.6 | deterministic enumeration of legal states, single faults, watchdog deadlines and recovery transitions | nominal happy-path simulation cannot close a safety requirement |
| H3.4 | level/pull/leakage/back-power predicates and worst-case timing/occupancy algebra for each interface | logic-family labels do not replace VIH/VIL/VOH/VOL and power-off behavior |
| H3.5 | source-to-antenna 50-ohm loss/mismatch budget plus reference-plane, corridor, isolation and coexistence constraints | pre-layout calculation cannot claim final impedance, isolation or radiated performance; those remain H6/H8 |
| H3.1, H3.3, H3.6 | worst-case dissipation and bounded thermal-resistance/capacitance network for board, enclosure and cells | unknown enclosure or interface resistance is a range, never a guessed scalar |
| H3.7 | machine join from every requirement and H2 net/device identity to an H3 result and downstream physical measurement | an unlinked result does not close a requirement |

## Common pass rules

- `PF-01` — Every normal and allowed degraded corner stays inside manufacturer recommended operating conditions; absolute maximum ratings are never design targets.
- `PF-02` — Steady rail/source current has at least 25% reserve over the enumerated worst-case load; exceptions require a named transient-only rating and separate H3.2 proof.
- `PF-03` — A regulated rail retains at least 5% of nominal-voltage headroom after source tolerance, distribution loss and steady droop, while every load remains inside its own supply range.
- `PF-04` — Worst-case timing and shared-resource occupancy use no more than 80% of the allocated deadline/budget; independent dedicated buses are checked for latency but are not combined artificially.
- `PF-05` — Power-off, reset and quiet-state combinations produce no back-power or unintended transmitter enable; any non-zero injection must remain below the exact published limit with 2x analytical reserve.
- `PF-06` — Predicted silicon junction temperature remains at least 20 C below the applicable maximum; battery charge/discharge temperature remains at least 10 C inside the exact cell/charger operating boundary.
- `PF-07` — Every enumerated single fault reaches a bounded-energy safe state without relying on the same firmware domain that may have failed, while a retained diagnostic reason remains recoverable.
- `PF-08` — Transient numerical evidence must agree at dt and dt/2 within 10% of the remaining pass margin; otherwise the timestep is reduced or the result fails unresolved.
- `PF-09` — RF pre-layout results pass only as layout constraints and loss/isolation budgets; final 50-ohm, matching, VNA, spectrum and coexistence claims remain H6/H8 measurements.
- `PF-10` — A missing min/max tolerance, applicability condition or model provenance is a fail/unresolved result, never an assumed pass.

## Reproducibility

The calculation core uses only the Python standard library, fixed-precision `Decimal`, and JSON/CSV/SVG. Network access and randomness do not participate in acceptance; every generator must provide `--write` and `--check`, input SHA-256 and tests.

**Status:** `H3.0.3` is reviewed. The current exact marker is `H3.3.3`, IR drive/receive/thermal corners.

[Machine method contract](../hardware/verification/generated/H3-VRF03-method-contract.json).
