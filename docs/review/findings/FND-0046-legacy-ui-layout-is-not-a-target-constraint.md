# FND-0046 — legacy UI layout is not a target-product constraint

- Статус: **Исправлено; G3 archetype decision открыт**
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

The owner accepted autonomous local control, text input, PTT/STOP and safety
semantics, not those exact surfaces/counts. Treating them as prerequisites would
bias the physical-keyboard comparison and eventually the pin/BOM/layout.

## Исправление

- `REQ-SYS-02` now requires the selected local surfaces collectively to provide
  complete phone-independent control; touch/encoder/keyboard remain optional
  archetype variables;
- `REQ-SYS-12` continues to require local text input, not a permanent keyboard;
- `BOM-0001 U-001..003` and its mismatch row are explicitly historical former
  candidate details, not target functions/parts;
- exact display, touch, keyboard, encoder, D-pad and action-key surfaces return
  to G3 whole-product comparison;
- dedicated STOP/PTT and clear cancel/confirmation remain non-negotiable.

## Exit criteria

- [x] neutral requirement wording propagated;
- [x] historical component register no longer calls former UI accepted;
- [x] no exact UI resources enter new architecture before G3/G5;
- [ ] owner chooses the G3 comparison disposition through `IMP-0032`.
