# Startup, shutdown and hardware FAULT_KILL

[Русский](power-transition-startup.ru.md) · [Home](../README.md) · [H3.2 result](power-transition-result.md)

H3.2.1 checks normal startup and fail-closed behavior through brownout, watchdog, recovered fault sources and a switch already held at RUN.

## Proven

- `Q=RUN_PERMIT`, `Q̅=FAULT_KILL`; asynchronous clear is `POR_N AND FAULT_ASSERT_N`, and `PRE_N` is fixed high.
- Earliest re-arm is `48.444 ms`, leaving `20.444 ms after the `28.0`-ms maximum POR.
- Holding RUN, resetting software, attaching USB or recovering a fault source cannot restart a latched device. A physical KILL→RUN cycle is required.
- Hold KILL at least `500 ms`; worst-case RC discharge to the negative threshold is `340.153 ms`.
- Hard fault removes TX without firmware grace. Only a warning receives a bounded 3-s lease-revoke, flush and record interval.

## Corrected by review

The original latch polarity made brownout select the permissive output and allowed forbidden `PRE_N=CLR_N=0`; the source map and schematics now use the fail-closed topology. The prior `≈57.6 ms` claim was also removed: the populated open TPS3808 CT specifies `12–28 ms`.

## Honest boundary

Power appearing while the maintained switch is already at RUN leaves the product safely off if self-test is not yet complete; the operator then cycles KILL→RUN. MLCC DC bias, switch bounce and physical shutdown order remain H8 measurements.

**Status:** `H3.2.1` reviewed. [Machine evidence](../hardware/verification/generated/H3-VRF21-startup-shutdown.json).
