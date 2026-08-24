# H2 production ECAD acceptance package

[Русский](h2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Schematics](schematics.md)

H2 was accepted by the user as the immutable H3 input. Acceptance means agreement with the production-schematic contract, not authorization for KiCad layout, purchasing or fabrication; a later mismatch reopens the affected gate.

## Completed

- four complete native KiCad hierarchies: UI, RF/power, display adapter and LoRa Cap
- independent power/recovery/isolation/quiet-state/fault-shutdown review
- zero native ERC findings and 189 physically reconciled intentional NCs
- 1,035 ledger rows, 1,033 electrical identities, 266 root nets and 80 M1 contacts reconciled
- 130 controller allocations agree with KiCad; 125 MCU contacts are byte-identical in firmware F2

## Deliberately outside H2

- `H3` — virtual worst-case and timing/transient verification
- `firmware F3` — build and emulator execution before ordering
- `H5` — received-sample and land-fit checks
- `H6` — placement/routing/DRC
- `H8` — physical bring-up and HIL

**Result:** ✅ `H2.8.2` was accepted by the user on 24 August 2026 at hardware commit `25d9ee2` and firmware commit `900bb2b`. The next hardware marker is `H3.0.1`.

[Machine package](../hardware/ecad/generated/H2-REV81-acceptance-package.json).
