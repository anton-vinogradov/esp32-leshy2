# Leshy2 power states

[Русский](power-state-register.ru.md) · [Home](../README.md) · [Power](power-architecture.md) · [Methods](verification-methods.md)

Before calculating current, H3 enumerates every allowed source, charge and concurrent-load state so a rare condition cannot disappear into one ‘maximum power’ row.

## Sources

The sole external source is sink-only USB-C: 5 V fallback at source-advertised current, 5 V × 3 A, 9 V × 3 A or 15 V × 2 A. The autonomous source is only a complete series pack of two protected 18650 cells at 6.0–8.4 V. One cell is not an operating mode.

## Coverage

- `43` USB/pack/charge combinations.
- `10` mutually exclusive signal groups and `25` internal modes.
- `50` load profiles and `2032` complete legal states.
- `6` explicitly rejected pack conditions; invariant violations: `0`.

## Concurrent operation

Only one top-level signal group is active at a time. The exception is internal to `SG-N24`: all three nRF24 radios remain active in `3PRX`, `1PTX+2PRX`, `2PTX+1PRX` and `3PTX`. Display, waterfall, storage and group-legal audio remain concurrent support loads in the worst case.

**Status:** `H3.1.1` is complete and checked. Current marker is `H3.3.3`, IR drive/receive/thermal corners.

[Complete machine state register](../hardware/verification/generated/H3-VRF11-power-state-register.json).
