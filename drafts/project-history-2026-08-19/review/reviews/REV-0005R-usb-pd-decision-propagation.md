# REV-0005R — sink-only USB-PD decision propagation

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0063`](../decisions/DEC-0063-sink-only-30w-usb-pd-power-path.md)
- Exact fit: [`PWR-0004`](../architecture/PWR-0004-accepted-usb-pd-front-end.md)

## Reviewed propagation

| Check | Result |
|---|---|
| target product EN/RU | pass: sink-only 30 W and no power-bank/source promise |
| vertical living diagram | pass: USB-C, TVS, TPS, EEPROM, BQ, two cells and still-TBD manager are separate physical boxes with roles |
| real contacts | pass: exact four device/package maps in machine source and generated atlas |
| S3 budget | pass: existing I2C0 + wired-low IRQ; GPIO47 stays free |
| S3 USB2 | pass: direct GPIO19/20; TPS USB/LD low and BQ DP/DM disconnected |
| reset/fault default | pass on paper: EEPROM write-protected and charger disabled without valid policy |
| configuration recovery | pass on architecture: blank-device direct pads plus signed dual-region field policy; HIL remains named |
| sourcing | pass for first-target selection snapshot; I8 alternate/RFQ still open |
| firmware consumer | pass: runtime/config/update/recovery contracts propagated to firmware repository |
| regressions | pass: machine validation, generated artifacts and both repository suites |

## Result

`IMP-0053/B` is closed and the USB-PD frontend portion of `I3` has
**Проведено ревью**. Whole `I3` remains active for the cell manager, rail tree,
exact passives/connector, loss/thermal/fault calculation and HIL. No KiCad
authorization or atomic-architecture acceptance is implied.
