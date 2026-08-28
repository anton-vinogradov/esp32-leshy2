# Historical H2 production ECAD acceptance package · R1

[Русский](h2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Schematics](schematics.md)

This accepted package is retained as reproducible evidence for the former single-RP R1 architecture. It is not the current R2 architecture and does not authorize R2 KiCad, purchasing or fabrication.

## Completed

- four complete native KiCad hierarchies: UI, RF/power, display adapter and LoRa Cap
- independent power/recovery/isolation/quiet-state/fault-shutdown review
- zero native ERC findings and 202 physically reconciled intentional NCs
- 1,081 ledger rows, 1,079 reconciled electrical identities, 270 root nets and 80 M1 contacts reconciled
- 130 controller allocations agree with KiCad; 125 MCU contacts are semantically identical in firmware F2 and the import is marked fail-closed historical R1
- two independent SA818S-V/U paths have separate SMA and TX evidence; the one-hot selector consumes no new MCU or M1 contact

## Deliberately outside H2

- `H3` — virtual worst-case and timing/transient verification
- `firmware F3` — build and emulator execution before ordering
- `H5` — received-sample and land-fit checks
- `H6` — placement/routing/DRC
- `H8` — physical bring-up and HIL

**Historical result:** ✅ revision `H2.8.2-R1` was accepted by the user on 2026-08-26 and remains SHA-256 bound. It is explicitly forbidden as R2 authority. The current hardware marker is `H1-R2.31`.

[Machine package](../hardware/ecad/generated/H2-REV81-acceptance-package.json).
