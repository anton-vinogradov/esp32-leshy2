# REV-0005W — MAX17320 surrounding-circuit gate

- Статус: **Проведено ревью фактов; owner gate открыт**
- Дата: 2026-08-18
- Analysis: [`PWR-0007`](../architecture/PWR-0007-max17320-2s-surrounding-circuit.md)
- Finding: [`FND-0077`](../findings/FND-0077-max17320-prequal-is-a-linear-fet-mode.md)
- Proposal: [`IMP-0056`](../improvements/IMP-0056-deep-cell-recovery-boundary.md)

## Review result

| Check | Result |
|---|---|
| exact 2S connection | pass at principle level: ADI short-link/balancing-resistor rule and EV-kit stack mapping are recorded; floating unused CELL assumptions rejected |
| real package/device evidence | pass: all newly named parts are exact order codes; stale Murata/Panasonic NTC and EOL Diodes BAV70 are rejected |
| slot independence | pass at paper level: one fuse and one thermistor per physical cell remain distinct |
| current envelope | pass: 15-W/6.0-V/90% case gives 2.78 A; 3-A continuous and 4-A pulse floor retained |
| common-path loss | pass for comparison: fuse, shunt and both FET options are calculated without hiding contacts/copper/hot multiplier |
| reset-default safety | pass at topology level: dual-MOS hold asserts ALRT without MCU code; release is explicit through PA6 |
| MCU supply handover | pass at topology level: AOLDO, fixture and admitted system branches are diode-isolated; current and transition HIL remain open |
| independent cell evidence | pass: reserved PA24/PA25 can measure midpoint and stack, leaving three free GPIO; exact analog values/HIL remain open |
| recovery behavior | blocked: MAX17320 prequal linearly operates CHG FET, so `IMP-0056` must choose the product boundary before exact FET acceptance |
| target diagrams | unchanged intentionally: no new component is accepted into the working design before the coupled owner decision |
| firmware | unchanged intentionally: the product must not advertise either recovery policy before owner acceptance |
| CAD boundary | pass: no schematic/KiCad authorization implied |

## Conclusion

The prerequisite and invariant portion receives **«Проведено ревью»**.
`I3` remains active at one material owner gate: in-device deep-cell recovery.
After that choice, the exact FET and the independent first targets can be
propagated atomically into the machine source, vertical diagrams, product
behavior and firmware contract.

