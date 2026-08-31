# Watchdog and clear shutdown reason · H3-R2.2.3

[Русский](watchdog-fault-display.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Power-transition result](power-transition-result.md)

The independent **Texas Instruments TPS3435CAKAGDDFR** monitors the always-on safety controller, not S3 directly. The safety controller must toggle WDI every `500 ms`; the minimum watchdog window is `1440 ms`, so service consumes only `34.722%` of the minimum deadline. If the controller stalls or WDI sticks, WDO pulls `FAULT_ASSERT_N` low within `1760 ms` and clears the RUN latch in hardware. The `180–220 ms` WDO-low interval is output duration after expiry, not extra detection latency.

S3 is covered by a separate heartbeat/lease monitor in the safety controller: two missed `500 ms` reports request a fault. An S3 stall is therefore covered without pretending that TPS3435 is wired directly to S3, while a stalled monitor is covered by TPS3435. Firmware, WDI or fault-source recovery cannot restart the product; physical KILL→RUN remains mandatory.

## What the user sees

- When `3V3_MAIN` and UI are safe, the safety controller may reset only S3 and boot the fault-only screen with a plain reason, zone, value/limit, action already taken and KILL instruction.
- UI overtemperature or an unsafe main rail intentionally keeps the screen off. The AON amber `FAULT` indicator is now correctly connected to `FAULT_KILL`, not the inverse fault request.
- Complete AON loss cannot promise a final write. A later boot uses the truthful “power disappeared before diagnostics could be committed” fallback when no exact record exists.

The cause uses two alternating 1-KB sectors in the MSPM0 lower-32-KB flash region. Guaranteed endurance is at least `200000` fault commits; an interrupted write cannot destroy the previous CRC-valid slot.

**Status:** `10/10` fault scenarios pass analytical review. Firmware imports the same machine contract; physical fault injection remains H8.

[Complete machine result](../hardware/verification/generated/H3-R2-inrush-watchdog.json).
