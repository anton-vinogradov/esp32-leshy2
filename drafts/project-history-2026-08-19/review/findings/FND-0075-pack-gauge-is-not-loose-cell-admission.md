# FND-0075 — a pack gauge is not a loose-cell admission controller

- Статус: **Подтверждено; correction находится в текущем IMP-0054**
- Дата: 2026-08-18
- Requirement: [`DEC-0062`](../decisions/DEC-0062-individually-replaceable-2s-cells.md)
- Option review: [`PWR-0005`](../architecture/PWR-0005-replaceable-2s-manager-options.md)

## Finding

The accepted two-slot behavior has two distinct jobs that must not be collapsed
into one label:

1. a pack gauge/protector measures an already connected stack or common bus, protects it,
   counts charge, balances cells and drives the normal CHG/DSG FETs;
2. an admission controller keeps those FETs open until the particular loose-cell
   pair passes presence, voltage, temperature, mismatch and diagnostic-load
   checks.

A normal integrated gauge does the first job but does not execute Leshy2's
product-specific second job. In particular, an ordinary untagged 18650 exposes
only two power terminals: its exact manufacturer MPN and chemistry cannot be
electrically authenticated at insertion. Voltage and short diagnostic pulses
can reject many unsafe pairs, but cannot prove the label or chemistry.

This is not fixed by fuel-gauge learning. Replacing one cell changes the pack
whose learned capacity/resistance history was accumulated. Treating old pack
SOC/SOH as the new pair's truth would therefore be an unsafe inference; a
successful single-cell replacement must enter a fresh admission/relearning
state.

## Consequence

- the target needs a fail-closed always-on admission controller in addition to
  the integrated pack gauge/protector;
- its default hardware state must hold both pack FETs open before firmware runs;
- if that hold depends on a gauge NVM option, factory assembly must program,
  checksum and read back the protected gauge image before cells may energize
  the assembly; a blank gauge is not silently assumed safe;
- the gauge must expose separate cell voltage and temperature channels and a
  hardware-compatible FET override;
- an exact supported cell profile remains a procedural/identity boundary. The
  later cell-MPN selection must state whether identity comes from an approved
  single SKU plus user confirmation, or from a tagged single-cell carrier. It
  cannot claim automatic chemistry recognition from two battery contacts;
- after either cell is replaced, reported SOC/SOH stays `estimating/unknown`
  until the new pair has been admitted and relearned.

## Evidence

- [ADI MAX17320 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max17320.pdf):
  separate cell measurements, up to four thermistors, high-side CHG/DIS FETs,
  pin/I2C FET override, ModelGauge learning and an always-on output intended for
  small housekeeping controllers;
- [TI BQ28Z620 product and datasheet](https://www.ti.com/product/BQ28Z620):
  integrated 1–2S gauge/protection and high-side FET drive, but only one
  external thermistor input and no separate alert/override contact in its
  12-pin package;
- [`DEC-0062`](../decisions/DEC-0062-individually-replaceable-2s-cells.md):
  explicitly requires observation and fail-closed pair admission before
  CHG/DSG closure rather than repair by balancing.
