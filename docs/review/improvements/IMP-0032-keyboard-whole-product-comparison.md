# IMP-0032 — physical keyboard whole-product comparison, not premature freeze

- Статус: **Принято C с phone-assisted text — `DEC-0038`**
- Дата: 2026-08-17
- Delta: `W-EXTRA-15`
- Evidence: [`AUD-0009`](../audits/AUD-0009-physical-keyboard-product-archetype.md)
- Finding: [`FND-0046`](../findings/FND-0046-legacy-ui-layout-is-not-a-target-constraint.md)

## Контекст

Leshy2 уже обязан работать без телефона и обеспечивать локальный text input.
Permanent keyboard therefore is not a missing capability by itself; it is a
whole-product choice affecting display, grip, enclosure, antennas, controls,
cost and repair.

Current evidence spans materially different viable products: 84×54 mm
Cardputer-Adv with 56 keys and 1.14-inch screen; 100×68 mm T-Deck Plus with
keyboard/trackball and 2.8-inch screen; autonomous Flipper-style D-pad and
T-Embed-style encoder instruments; and external 42-key U215. None proves the
optimal Leshy2 form factor alone.

## Options

### A — require an integrated physical text keyboard now

Every later product candidate must include a permanent keyboard. Exact matrix,
key count and display remain G3/G4 work.

- Плюсы: fastest standalone credentials, names, scripts and CLI; no accessory
  for sustained text.
- Минусы: prematurely removes display-first/one-hand candidates; keyboard does
  not replace dedicated field/safety controls and adds face area, openings,
  assembly, legends, matrix/controller and per-key HIL.

### B — require equal whole-product archetype comparison at G3/G5

Do not accept or reject the permanent keyboard yet. G3 must produce at least:

1. an integrated-keyboard autonomous candidate;
2. a display-first field-control candidate with complete on-screen text input;
3. optional landscape hybrid only if it is not already represented by #1.

Each candidate preserves the same capabilities, STOP/PTT, local text and
external-interface envelope. G5 compares actual task timing/error, display
readability, one-/two-hand and glove use, size/mass, RF/antenna impact,
mechanics, BOM, repair and test. U215 may be evidence/optional sub-option, not
an automatically accepted product profile.

- Плюсы: follows the agreed design-before-architecture process and lets the
  architecture converge as a whole rather than inheriting a legacy control map.
- Минус: one additional complete mechanical/UI candidate and usability fixture
  must be developed before final selection.

### C — exclude an integrated keyboard now

Base always uses field controls + on-screen text; long text uses optional
external/USB paths.

- Плюсы: protects display/front area and likely reduces openings/assembly.
- Минусы: may reject the best autonomous terminal form before measured task
  comparison; external U215 is an active 84.7×54.3 mm accessory, not free.

## Recommendation and decision

The audit originally recommended **B** to retain equal whole-product comparison.
The owner instead selected **C with phone-assisted text** in
[`DEC-0038`](../decisions/DEC-0038-phone-assisted-text-no-integrated-keyboard.md):
no permanent keyboard, while rare/long arbitrary text may use a qualified phone
companion. The phone sends characters and never supplies local authority for
safety, Controlled-Zone, TX, destructive, FIDO, trust or recovery decisions.

## Accepted boundary for C/phone-assisted text

- `W-EXTRA-15` closes as `rejected-integrated / accepted-phone-assisted`;
- core field, safety and recovery actions work without phone/accessory;
- a text-dependent optional workflow may be unavailable without a phone and
  must say so truthfully;
- dedicated physical STOP/PTT and reliable cancel/confirm exist in every candidate;
- incoming text and consequence-bearing values are reviewed locally before use;
- local pairing, visible peer, authenticated encryption, revoke and fail-closed
  disconnect/stale-input behavior are mandatory;
- integrated/external physical keyboard profiles are absent until a new proposal;
- exact touch/encoder/D-pad/action count/pins/BOM remain unselected until G5/G7.
