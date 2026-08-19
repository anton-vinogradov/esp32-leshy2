# FND-0088 — the display endpoint still contained abstract circuits

- Status: **исправлено на бумажном уровне; physical-mate and electrical HIL remain open**
- Scope: I4 display/touch endpoint
- Decision: [`DEC-0084`](../decisions/DEC-0084-exact-protected-display-electrical-endpoint.md)
- Architecture: [`DSP-0006`](../architecture/DSP-0006-exact-display-rail-backlight-and-mate-profile.md)

## Finding

The prior map correctly exposed all 40 `HMX035CTFT-001` contacts and proved
the S3 GPIO budget, but it still ended on three abstractions:

- `qualified-display-3v3` did not identify local capacitance or fault boundary;
- `qualified-backlight-supply/sink` did not identify a switch, current limit,
  PWM transistor or reset default;
- no physical connector instance sat between the board nets and the panel
  assembly.

This was not enough to claim a complete paper electrical endpoint.

## Self-review correction

An initially attractive whole-panel latch-off switch was rejected during the
review. If it removed VDD/VDDI while QSPI, I2C or reset contacts remained high,
the panel could be back-powered through its signal pads. Correct isolation of
every path would cost multiple active devices and add delay and routing risk.

The corrected profile therefore keeps panel logic on the already protected
`3V3_MAIN` rail and independently protects only `LEDA`, which has no digital
back-power path. This gives meaningful short/thermal containment without a new
GPIO or a large isolation BOM.

## Corrected state

`DSP-0006/DEC-0084` now instantiate the first exact 40-contact connector
candidate, local logic capacitance, both reset pull-downs, latch-off backlight
switch, current-limit and fault components, the reference-equivalent LEDK
resistor and an exact low-side PWM MOSFET. Every physical component is a
separate machine instance and diagram node.

The connector is not mechanically frozen: a real panel tail still must prove
0.30-mm thickness, bottom-contact orientation, insertion direction, stiffener,
retention and installed envelope before any footprint or KiCad authorization.

