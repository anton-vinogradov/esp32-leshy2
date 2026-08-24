# Watchdog and clear shutdown reason

[Русский](watchdog-fault-display.ru.md) · [Home](../README.md) · [H3.2 result](power-transition-result.md)

The independent TPS3435 exact window is `1.44–1.76 s`; firmware services it on a nominal `500 ms` cadence. WDO directly joins the hardware fault plane, so a hung S3 or safety controller cannot cancel shutdown in software. WDO recovery cannot restart the product because the latch still needs KILL→RUN.

The safety controller stores the cause in a two-slot CRC journal in its own flash. Fault-only UI shows the reason, zone, value/limit, action already taken, event ID and instruction to move RUN to KILL. It may not enable C5, RP, TX/IR, voice PTT, external 5 V or clear the latch.

UI overtemperature intentionally sacrifices the screen to remove the unsafe zone; the amber FAULT LED and later service readout remain. Complete AON loss may physically prevent the final write, so the next start truthfully reports that power disappeared before diagnostics could be committed.

**Status:** `H3.2.4` reviewed; 6/6 fault scenarios pass. [Machine evidence](../hardware/verification/generated/H3-VRF24-watchdog-fault-display.json).
