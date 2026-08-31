# R2 power states

[Home](../README.md) · [Roadmap](roadmap.md) · [Methods](verification-methods.md) · [Русский](power-state-register.ru.md)

`H3-R2.1.1` is reviewed. The deterministic register enumerates `43` source/charge states, `56` operating profiles and `2266` complete legal R2 states.

## Included surface

- sole powered USB-C: absent, unknown 5-V fallback, 5 V × 3 A, 9 V × 3 A and 15 V × 2 A;
- pack absent, isolated, 2S low/nominal/full;
- all ten signal groups, including all three nRF24 paths in 3R/1T2R/2T1R/3T combinations;
- mutually exclusive U214 and receive-only U219 Cap profiles;
- mutually exclusive FM/SW, AM/LW and mandatory receive-only Airband submodes;
- safe-only and latched-fault modes with no payload transmission.

## Important boundary

This proves state completeness, not current sufficiency. Exact marker `H3-R2.1.2` now binds every powered instance to an explicit worst-case rail-load line; an unknown current must produce `unresolved_fail`, never a hidden allowance.

[Complete machine register](../hardware/verification/generated/H3-R2-power-state-register.json).
