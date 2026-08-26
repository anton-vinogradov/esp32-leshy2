# H2 production ECAD acceptance package

[Русский](h2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Schematics](schematics.md)

The current H2 revision was accepted by the user as the immutable input for the repeated H3 run. Acceptance means agreement with the production-schematic contract, not authorization for KiCad layout, purchasing or fabrication; a later mismatch reopens the affected gate.

## Completed

- four complete native KiCad hierarchies: UI, RF/power, display adapter and LoRa Cap
- independent power/recovery/isolation/quiet-state/fault-shutdown review
- zero native ERC findings and 202 physically reconciled intentional NCs
- 1,081 ledger rows, 1,079 reconciled electrical identities, 270 root nets and 80 M1 contacts reconciled
- 130 controller allocations agree with KiCad; 125 MCU contacts are byte-identical in firmware F2
- two independent SA818S-V/U paths have separate SMA and TX evidence; the one-hot selector consumes no new MCU or M1 contact

## Deliberately outside H2

- `H3` — virtual worst-case and timing/transient verification
- `firmware F3` — build and emulator execution before ordering
- `H5` — received-sample and land-fit checks
- `H6` — placement/routing/DRC
- `H8` — physical bring-up and HIL

**Result:** ✅ revision `H2.8.2-R1` was accepted by the user on 2026-08-26; the exact baseline is bound by SHA-256 for every listed input and therefore does not depend on a not-yet-created commit hash. It supersedes the former SA518 revision. The next hardware marker is `H3.0.1-R1`.

[Machine package](../hardware/ecad/generated/H2-REV81-acceptance-package.json).
