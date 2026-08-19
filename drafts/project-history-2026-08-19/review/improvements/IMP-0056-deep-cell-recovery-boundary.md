# IMP-0056 — deep-cell recovery boundary

- Статус: **Принято A; закрыто `DEC-0067`**
- Дата: 2026-08-18
- Context: [`PWR-0007`](../architecture/PWR-0007-max17320-2s-surrounding-circuit.md)
- Finding: [`FND-0077`](../findings/FND-0077-max17320-prequal-is-a-linear-fet-mode.md)
- Decision: [`DEC-0067`](../decisions/DEC-0067-no-in-device-deep-cell-recovery.md)
- Affects: `I3`, CHG/DIS MOSFET, battery admission, Controlled Zone and HIL

## Current state

The base product uses two individually replaceable 18650 cells in supervised
2S. `MAX17320G20+T + MSPM0C1104SDGS20R` must keep both charge and discharge
paths open until the installed pair passes voltage, temperature, contact and
impedance admission.

The remaining MOSFET choice is coupled to one product behavior. MAX17320 uses
the CHG FET linearly during prequal; enabling recovery of low-voltage cells
therefore adds a power-SOA and thermal problem, not just a firmware setting.
The product also cannot prove the history or chemistry of an untagged loose
cell from its two contacts.

## A — no in-device deep-cell recovery — recommended

- the product refuses a cell below the qualified admission floor and never
  enables MAX17320 zero-volt or prequal recovery in normal hardware;
- `3.0 V` relaxed/no-load per cell is the conservative paper starting point,
  not yet a production constant: the exact threshold follows the selected
  qualified cell profile, temperature and measurement-error budget;
- ordinary charging begins only after both cells pass admission;
- a separate isolated service fixture may characterize or attempt recovery,
  but only as a Controlled-Zone laboratory operation with the existing banner,
  authorization and physical containment rules; it is not a product menu
  shortcut;
- this permits a compact one-package switching path, subject to ordinary hot-
  loss and fault HIL; lifecycle and topology checks subsequently selected the
  active common-drain `CSD87313DMST`, not the obsolete `FDMC8030` paper part.

Material consequence: safer behavior for unknown replaceable cells, smaller
power path and less validation. The user must replace or externally inspect a
deeply discharged cell instead of asking the device to revive it.

## B — bounded in-device prequal for qualified cells

- the product may prequal only an exact approved cell family and only inside a
  narrow voltage/temperature/time envelope;
- the CHG FET must be selected and tested for linear-mode SOA at worst input,
  stack voltage, current and duration; PCB copper and enclosure temperature
  become part of the acceptance proof;
- two separate low-loss FETs such as `CSD17575Q3T` are only an analysis start,
  not automatic proof of a minute-scale linear interval;
- extra telemetry, timeout/fault cases and destructive thermal samples enter
  prototype HIL.

Material consequence: more convenience for a known but depleted cell, at the
cost of board area, placement, thermal work and a larger safety-validation
matrix. It still must reject unknown or damaged cells.

## Dominated behavior

Recovery of arbitrary unknown, zero-volt or visibly damaged loose cells inside
the handheld is not offered as an acceptance option. It conflicts with the
fail-closed replaceable-cell boundary; if researched at all, it belongs to a
separate contained Controlled-Zone fixture.

## Cost indication

Point-in-time authorized-channel pricing for the selected `CSD87313DMS` package
was about `$1.03/100` (`$0.658` at full reel) and two `CSD17575Q3T` parts were
roughly `$1.6…1.9/100` before extra placement and validation. These are
comparison inputs, not a fabrication RFQ.

## Recommendation

Accept **A**. It keeps the base product conservative, does not close the device
or prohibit laboratory research, and moves the dangerous recovery operation
to the already accepted Controlled-Zone boundary where containment and explicit
authorization are available.

## Owner decision

Accepted **A** by the owner on 2026-08-18 and propagated by `DEC-0067`.
