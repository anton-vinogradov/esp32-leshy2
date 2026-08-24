# Leshy2 fault shutdown

[Русский](fault-shutdown.ru.md) · [Home](../README.md) · [Quiet state](quiet-state.md)

Emergency shutdown does not depend on S3, the menu or the main application and never restarts transmitters automatically.

| Source | Hardware result |
|---|---|
| RUN moved to KILL or conductor opens | asynchronous latch; TX/power gates safe; C5/RP reset |
| heartbeat missing or invalid | TPS3435 or lease monitor latches the fault |
| TX without a valid lease | physical evidence latches the fault |
| POWER or RF/VOICE overheats | every hazardous path off; cool UI reports the cause |
| UI/DISPLAY overheats | UI also off; independent amber FAULT LED remains |
| AON brownout | supervisor and off-safe pulls hold the safe state |

## H2.5.5 result

✅ **Reviewed:** 56 safety nets match complete KiCad netlists; all 33 required diagnostic points now exist as copper.

[Machine evidence](../hardware/ecad/generated/H2-REV55-fault-kill.json).
