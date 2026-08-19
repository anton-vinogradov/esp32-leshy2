# REV-0005Z — latch-off eFuse propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0069`](../decisions/DEC-0069-latch-off-external-efuse.md)

## Review result

| Check | Result |
|---|---|
| exact suffix | pass: machine source and visible target diagrams use `TPS259470LRPWR`; `TPS259470ARPWR` is no longer the target instance |
| real package | pass: RPW-10 contact map and footprint class are unchanged |
| fault behavior | pass: external power stays latch-off after thermal/latched fault until explicit enable-low or input cycle; no autonomous 110-ms retry remains |
| runtime behavior | pass: firmware latches `FLT`, isolates signals and forbids retry loops |
| current envelope | pass at requirement level: nominal limit is raised from the unsafe 1.25-A assumption to a tolerance-safe 1.50-A target; exact resistor/timer values remain the next passive gate |
| availability/cost | pass at decision time: exact L suffix is active and stocked; checked prices match A |
| diagrams and machine source | pass after regeneration and root README propagation |
| CAD boundary | pass: no KiCad authorization is implied |

## Conclusion

The owner-approved latch-off change receives **«Проведено ревью»**. Exact
`RILM`, `ITIMER`, `dVdt`, OVLO and discharge values continue in I3.
