# IMP-0032 — physical keyboard whole-product comparison, not premature freeze

- Статус: **⚠️ Требуется решение владельца**
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

## ⚠️ Recommendation

**B**. This is not indecision: it closes the G2 delta as a G3/G5 design variable
with mandatory equal comparison and prevents old `touch+encoder+buttons` or a
new keyboard fashion from silently becoming architecture. The final keyboard
choice is made only together with display, grip, antennas, battery, connectors,
safety controls and cost.

## Acceptance boundary for B

- `W-EXTRA-15` becomes `design-candidate`, not an accepted base capability;
- local essential actions and text work without phone/accessory in every candidate;
- dedicated physical STOP/PTT and reliable cancel/confirm exist in every candidate;
- no candidate receives a smaller capability set to make its ergonomics look better;
- representative task fixture measures error/time with bare hand and declared
  glove class, standing/walking/bench posture and low-light/sunlight conditions;
- exact keyboard/touch/encoder/D-pad/count/pins/BOM remain unselected until G5;
- optional U215 requires a separate exact wired profile before target inclusion.
