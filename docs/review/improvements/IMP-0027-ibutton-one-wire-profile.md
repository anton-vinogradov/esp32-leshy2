# ⚠️ IMP-0027 — iButton/1-Wire capability and contact strategy

- Статус: **Предложение; требуется решение владельца**
- Дата: 2026-08-16
- Source gap: `AUD-0004/W-EXTRA-11`, `FND-0040`
- Competitor evidence: [Flipper Zero iButton documentation](https://docs.flipper.net/zero/ibutton)

## Контекст

Current Leshy2 scope has USB, external accessories and HF/LF RFID dispositions,
but no 1-Wire/iButton user result. Это отдельная проводная технология и contact
mechanics; ни NFC, ни Grove I²C не покрывают её автоматически.

Полезный честный scope:

- Main: generic owned 1-Wire sensor/identity read where it is not an access-
  control security action;
- Lab: passive read/identify/save access-control keys with protocol/evidence
  confidence and no automatic emulation;
- Controlled Zone `AUTHORIZED_TARGET`: emulate or write a supported rewritable
  key only for an explicitly authorized reader/key fixture, with per-action
  preview and no unattended replay;
- unsupported electrical/protocol profile remains explicit, never guessed;
- read, write and reader-side emulation are separately qualified; “Dallas,
  Cyfral and Metakom” is not inferred from a generic 1-Wire GPIO.

## Варианты

### A — integrated three-contact pad in the base device

Base enclosure includes a protected contact surface suitable for key-side read/
write and reader-side emulation.

- Плюс: strongest all-in-one parity, no adapter to lose.
- Минусы: permanent case opening/contact wear, corrosion/ESD/contamination,
  custom metal mechanics and valuable exterior surface before form factor is
  chosen.

### B — base electrical support plus passive keyed contact adapter

Base product exposes a protected, identified bidirectional timing/level profile
on the future durable accessory/service surface. A passive mechanical adapter
provides the exact three-contact pad; no extra programmable domain is added.

- Плюсы: retains the full technical function with little base BOM and avoids
  forcing one corrosion-prone pad into every enclosure; adapter mechanics can
  be replaced cheaply.
- Минусы: access-key contact use is not physically self-contained without the
  passive adapter; the base connector still needs ESD/back-power/wrong-profile
  proof.

### C — defer to a complete external active module

No base electrical promise; a future module owns contacts and protocol timing.

- Плюс: minimum immediate base impact.
- Минусы: weakest interoperability, extra powered hardware/firmware/update
  burden and no competitor parity in the first product.

## Рекомендация

**B**. It preserves the capability and open repair path without prematurely
spending enclosure surface or adding a programmable target. During `G3`, an
integrated-pad archetype may still beat the passive adapter on ergonomics and
be promoted to A; the electrical requirement itself remains implementation-
neutral until that comparison.

## Acceptance boundary if retained

- protected open-drain/bidirectional electrical states, current/voltage limits,
  short/ESD/back-power and wrong-adapter tests;
- exact supported protocol/device list and independent read/emulate/write
  corpus;
- touch/contact debounce and no operation on attach alone;
- sensitive key records encrypted with explicit export/delete/provenance;
- no claim of universal iButton/access-system compatibility;
- factory reset erases local secrets and cannot leave an emulation armed.
