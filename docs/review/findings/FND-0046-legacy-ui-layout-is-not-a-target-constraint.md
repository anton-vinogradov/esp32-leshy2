# FND-0046 — legacy UI layout is not a target-product constraint

- Статус: **Исправлено; product boundary закрыт `DEC-0038`**
- Дата: 2026-08-17
- Обнаружено: [`AUD-0009`](../audits/AUD-0009-physical-keyboard-product-archetype.md)
- Затрагивает: `REQ-SYS-02`, blocked `BOM-0001`, `W-EXTRA-15`, G3/G4/G5

## Несоответствие

Although `DEC-0032` reopened product design, two artifacts could still import a
superseded UI layout:

- `REQ-SYS-02` could be read as simultaneously mandating touch, physical
  buttons and encoder;
- blocked historical `BOM-0001` said the accepted UI uses a 480×320 display,
  touch, encoder and six named controls.

The owner accepted autonomous core local control, PTT/STOP and safety semantics,
not those exact surfaces/counts. `DEC-0038` later permits a phone for declared
text-dependent scenarios. Treating the old map as a prerequisite would
bias the physical-keyboard comparison and eventually the pin/BOM/layout.

## Исправление

- `REQ-SYS-02` now requires the selected local surfaces collectively to provide
  complete phone-independent core/safety/recovery control; `DEC-0038` later
  excludes the keyboard while touch/encoder/D-pad remain G3 variables;
- `REQ-SYS-12` now defines the bounded phone-assisted text exception and local
  authority boundary;
- `BOM-0001 U-001..003` and its mismatch row are explicitly historical former
  candidate details, not target functions/parts;
- exact display, touch, encoder, D-pad and action-key surfaces return to G3
  whole-product comparison; the integrated keyboard is no longer a candidate;
- dedicated STOP/PTT and clear cancel/confirmation remain non-negotiable.

## Exit criteria

- [x] neutral requirement wording propagated;
- [x] historical component register no longer calls former UI accepted;
- [x] no exact UI resources enter new architecture before G3/G5;
- [x] owner selected no integrated keyboard plus phone-assisted text through
  `DEC-0038`.
