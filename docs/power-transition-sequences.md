# Startup, reset and recovery · H3-R2.2.1

[Русский](power-transition-sequences.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

`H3-R2.2.1` verification is complete: every startup and fault-recovery scenario passes without automatic restart. An ordinary fault removes hazardous domains and directly resets C5/RF RP, while S3 can keep a readable cause on screen whenever UI power remains available.

## Startup rule

Safety holds `SAFETY_FAULT_REQUEST` active after reset. Self-test must pass, physical `KILL` must remain continuous for 500 ms, and only the following `KILL→RUN` edge may clock the hardware `RUN_PERMIT` latch. USB, software reset and fault recovery create no such edge.

## Exact bounds

- TPS3808 with CT open: `12..28 ms`; reset assertion within `20 us`.
- TPS3435: device startup within `500 us`, watchdog-window startup delay `0 ms`; `1.44..1.76 s` timeout, `180..220 ms` WDO-low interval; heartbeat target `500 ms`.
- 100 kohm / 2.2 uF: analytical rise `96.888..283.86 ms`, tolerance-only guaranteed discharge `484.525 ms`; this is debounce, not the sole interlock.

## Verified scenarios

| Scenario | Result |
|---|---|
| `SEQ-01` · Cold start with switch at KILL | ✅ pass |
| `SEQ-02` · Cold start with switch already at RUN | ✅ pass |
| `SEQ-03` · RUN-at-boot followed by explicit KILL and RUN | ✅ pass |
| `SEQ-04` · Insufficient KILL dwell | ✅ pass |
| `SEQ-05` · Switch bounce fails closed | ✅ pass |
| `SEQ-06` · Physical KILL or open loop during RUN | ✅ pass |
| `SEQ-07` · Watchdog timeout and automatic WDO recovery | ✅ pass |
| `SEQ-08` · Safety-controller reset during RUN | ✅ pass |
| `SEQ-09` · Fault recovery while switch remains RUN | ✅ pass |
| `SEQ-10` · Independent S3 fault-UI reset | ✅ pass |
| `SEQ-11` · AON undervoltage or POR assertion | ✅ pass |
| `SEQ-12` · Self-test failure | ✅ pass |
| `SEQ-13` · USB attach cannot rearm a stopped product | ✅ pass |
| `SEQ-14` · Complete qualified recovery after fault | ✅ pass |

## Corrections

- S3 has an independent M1-36 reset and remains the fault UI; C5 and RF RP retain direct resets.
- PA23 gains an external 10-kohm pulldown by reusing the former unused position, so BOM and cost do not grow.
- Anti-auto-start now depends on qualified physical KILL rather than assumed RC-edge timing.

## Physical residuals

- H8 measures real switch bounce and break-before-make interval.
- H8 measures the populated 100-kohm/2.2-uF RC under DC bias and temperature; startup safety does not depend solely on this number.
- H8 captures POR assertion/release, direct C5/RF-RP reset and S3 fault-display retention at real rail corners.

**Result:** `14/14` scenarios and `51` endpoint checks pass. H3-R2.3, [H3-R2.4 digital verification](digital-electrical-verification.md), [H3-R2.5 RF verification](rf-electrical-verification.md), [H3-R2.6 thermal/fault verification](thermal-fault-electrical-verification.md), H3-R2.7 and the H4-R2.0.1 input freeze are reviewed; the **current marker is `H4-R2.2`**. Ordering and routing remain forbidden.

[Machine report](../hardware/verification/generated/H3-R2-transition-sequences.json).
