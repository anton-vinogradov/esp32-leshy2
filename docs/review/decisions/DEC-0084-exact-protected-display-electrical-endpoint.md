# DEC-0084 — exact protected display electrical endpoint

- Status: **accepted; Проведено ревью for paper electrical scope**
- Finding: [`FND-0088`](../findings/FND-0088-display-endpoint-still-contained-abstract-circuits.md)
- Architecture: [`DSP-0006`](../architecture/DSP-0006-exact-display-rail-backlight-and-mate-profile.md)
- Propagation review: [`REV-0005AO`](../reviews/REV-0005AO-display-endpoint-propagation.md)

## Decision

1. Keep `HMX035CTFT-001` as the exact current paper assembly and all 40
   published contacts as its electrical boundary.
2. Instantiate `FH12-40S-0.5SH(55)` as the first exact connector candidate and
   map the 40 contacts 1:1. This is not a mechanical or footprint freeze.
3. Power VDDI/VDD and the QSPI strap from protected `3V3_MAIN` with exact
   10-uF plus 100-nF local decoupling. Do not switch the whole logic rail
   without complete interface isolation.
4. Protect `LEDA` alone with `TPS2553DRVR-1`, 133-kOhm current setting, exact
   local capacitors, pulled-up fixture fault and no auto-retry.
5. Join the three LEDK contacts through exact `ERJ-P08F10R0V` and
   `DMN2056U-7`; GPIO40 drives the gate through 100 Ohm and a 10-kOhm
   reset-off pull-down.
6. Give display reset and touch reset separate exact 10-kOhm default-low
   resistors. Firmware observes at least 120-ms display and 100-ms touch
   post-release intervals.
7. Reuse the single existing SYS_I2C pull-up pair; do not add panel-local
   duplicates. Leave TP_INT without an assumed populated pull until specimen
   HIL proves its electrical mode.
8. Reserve QSPI tuning footprints DNP. No value becomes an exact populated BOM
   item before shared display/microSD measurements.

## Consequences

- S3/slow-I/O GPIO budgets do not change.
- Backlight short/thermal faults fail closed and require power-cycle recovery.
- A panel logic short remains contained by the existing main-rail eFuse rather
  than a back-power-prone local switch.
- Connector orientation, standalone orderability and all listed HIL remain
  blockers for physical freeze and KiCad authorization.

