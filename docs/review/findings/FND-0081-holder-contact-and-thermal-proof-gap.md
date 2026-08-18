# FND-0081 — holder name did not prove contacts or NTC coupling

- Статус: **Исправлено на бумажном уровне; specimen/HIL gate сохранён**
- Дата: 2026-08-18
- Correction: [`PWR-0016`](../architecture/PWR-0016-keystone-1048p-holder-and-ntc-coupling.md)
- Decision: [`DEC-0077`](../decisions/DEC-0077-keystone-1048p-qualified-cell-profile.md)
- Review: [`REV-0005AH`](../reviews/REV-0005AH-battery-holder-and-ntc-coupling.md)

## Finding

The accepted battery behavior required mechanical polarity before electrical
admission, but the machine map still began at abstract positive terminals and
the physical fit still showed an `MPN TBD` `40 × 78 mm` holder. “Dual 18650”
did not prove whether four contacts were independently exposed or whether the
holder contained an unwanted link.

The two MAX17320 thermistors and the third BQ25798 TS thermistor had exact
electrical MPNs but no repeatable physical cell-contact geometry. The charger
sensor was merely called “representative worst case”, which is a claim, not a
selection method.

## Correction

- exact polarized `Keystone 1048P` is instantiated with four functional slot
  contacts and no invented manufacturer pad numbers;
- the 2S link exists only in PCB routing and each positive keeps its own fuse;
- the exact `39.8 × 86.0 mm` holder and `20.7 mm` installed reference envelope
  replace the placeholder in the bounded rear-fit artifact;
- both MAX sensors receive their own insulated compliant mid-can contact;
- one charger sensor receives two indexed possible sites, with exactly one
  populated after thermal worst-slot selection;
- if HIL cannot establish one worst slot, the BQ one-sensor topology reopens;
- target and firmware contracts explicitly reject arbitrary/raw flat-top
  cells and preserve exact-cell qualification.

Received-part continuity, drawing orientation, insertion cycling and thermal
response remain mandatory. The correction removes the architecture ambiguity
without pretending paper geometry is specimen proof.
