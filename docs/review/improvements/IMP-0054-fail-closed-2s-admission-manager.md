# IMP-0054 — fail-closed 2S admission manager

- Статус: **⚠️ Ожидает решения владельца после `DEC-0065`**
- Дата: 2026-08-18
- Context: [`PWR-0005`](../architecture/PWR-0005-replaceable-2s-manager-options.md)
- Finding: [`FND-0075`](../findings/FND-0075-pack-gauge-is-not-loose-cell-admission.md)
- Affects: `I3`, battery startup, safety, SOC/SOH, service and firmware images
- Revalidation: [`REV-0005U`](../reviews/REV-0005U-exact-2s-manager-revalidation.md)

## Context

`DEC-0062` keeps two individually replaceable 18650 cells and requires both
CHG and DSG to remain open until the pair is checked. An integrated gauge alone
cannot run the product-specific pre-admission algorithm, and S3 cannot perform
it because battery-only startup occurs after the pack FETs close.

The checked complete choices are therefore:

### A — MAX17320 plus always-on admission MCU — recommended

- exact `MAX17320G20+T`: 2S high-side protector/gauge, two independent cell
  temperatures, SOC/SOH, balancing, hardware ALRT FET override and <2-mA
  always-on output;
- exact `MSPM0C1104SDGS20R`: reset-default admission state machine, diagnostic
  pulse, watchdog, system-status bridge and independent SWD/UART recovery;
- the factory fixture must program/check/read back the MAX17320 protected NVM
  image and `OvrdEn=1` before an energized cell assembly is permitted; after
  that gate, a blank/reset/watchdog admission MCU is held fail-closed by the
  external ALRT circuit;
- the MCU runs inside a measured `<2 mA` AOLDO startup/steady-state budget;
  the fixture may supply its VDD for initial SWD programming;
- visible 100-piece active-pair subtotal about `$4.47`; gauge is currently
  stocked by two checked authorized distributors;
- exact `G20` is the I2C order code without SHA-256; no authentication secret
  or irreversible lock is required.

This option directly implements fail-closed battery-only startup. It costs
about `$1.12` more than the superficial B two-IC subtotal, before parts common
to both options.

### B — BQ28Z620 plus admission MCU

- exact `BQ28Z620DRZR` is smaller and about `$2.88/100` for the gauge;
- it has only one external thermistor and no separate FET-override/alert pin;
- matching A's second-cell autonomous thermal protection and reset-default
  hold-open behavior adds circuitry and verification burden;
- both checked distributors currently show zero stock/backorder.

The apparent saving is not retained at equivalent safety and supply risk.

### C — discrete monitor/protector plus separate gauge and MCU

A fresh monitor such as the BQ76905 class can implement low-level protection,
but still needs SOC/SOH and the admission controller. It also uses low-side
FET drive, which is undesirable around USB and external accessory grounds.
It adds parts and interfaces without improving the accepted behavior.

## Recommendation

Accept **A** and immediately continue with exact FET/fuse/NTC/shunt/diagnostic-
load selection and calculations. Keep the raw-cell identity policy as the next
separate owner gate: no two-contact circuit can prove an untagged 18650's MPN
or chemistry.

## Owner decision

Reopened because `DEC-0065` selected supervised 2S. Choose `A`, `B` or `C`.
