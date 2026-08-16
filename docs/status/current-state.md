# Leshy2 Hardware — current engineering state

> Snapshot: 2026-08-17. This page describes proven maturity. The intended
> behavior is in the [hardware target README](../../README.md); software behavior
> is in the [firmware target README](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.md).

- Canonical evidence: [review ledger](../review/README.md)
- Russian version: [current-state.ru.md](current-state.ru.md)
- Corrected gate chain: [`FLOW-0001`](../review/architecture/FLOW-0001-product-to-cad-gates.md)

## Review progress

| Gate | State |
|---|---|
| 0. Review baseline | Reviewed |
| 1. Product intent and safety/legal boundaries | Reviewed |
| 2. Capabilities, exclusions, concurrency/failure needs | **Repeat review required**: prior 125 leaves retained, competitor delta open (`FND-0040`) |
| 3. Target physical/product design | Research active; final review waits for gate 2 |
| 4–6. Whole-device alternatives, optimality and conceptual co-design | Not started in the corrected process |
| 7. Atomic architecture | **Reopened** by `DEC-0032` |
| 8. Components/BOM | Blocked; previous evidence is candidate/reference only |
| 9. Electrical/CAD/firmware architecture | Blocked; no active canonical KiCad implementation |
| 10–11. PCB, fabrication and bring-up | Not started |

The canonical table is [`stages.md`](../review/stages.md).

## ⚠️ Open competitor-delta proposals

- `W-EXTRA-11` is closed: [`DEC-0033/REQ-IBTN-0001`](../review/decisions/DEC-0033-external-m5-ibutton-profile.md)
  accepts an external passive M5-style Port-B iButton adapter and no base pad;
- infrastructure is closed by [`DEC-0034/REQ-EXT-0001`](../review/decisions/DEC-0034-m5-first-two-tier-expansion.md): M5-first Unit/Cap plus a separate high-throughput class, without native M5-Bus;
- former `W-EXTRA-12` FIDO acceptance is removed from target by [`DEC-0039`](../review/decisions/DEC-0039-radio-key-scope-correction.md);
- `W-EXTRA-13` is closed by [`DEC-0036`](../review/decisions/DEC-0036-no-product-haptic.md): no product haptic, motor, dedicated profile or mount;
- `W-EXTRA-14` is closed by [`DEC-0037`](../review/decisions/DEC-0037-optional-external-imu-measurement-pose.md)/[`REQ-IMU-0001`](../review/requirements/REQ-IMU-0001-external-measurement-pose.md);
- `W-EXTRA-15` is closed by [`DEC-0038`](../review/decisions/DEC-0038-phone-assisted-text-no-integrated-keyboard.md): no integrated keyboard, bounded phone-assisted text;
- `W-EXTRA-16` generic High-Speed USB host is rejected by `DEC-0039`; only RF-derived transport remains;
- current question: `W-EXTRA-17` 6 GHz/Wi-Fi 6E; facts/prerequisites are
  reviewed in `AUD-0012/REV-0002AQ`, owner placement remains `IMP-0034`.

No remaining item becomes part of the target before owner disposition.

## What remains reviewed

- all-in-one autonomous field-product intent, non-aggression onboarding and the
  Main/Lab/Controlled-Zone safety model;
- conservative TX defaults, explicit maximum-power choice, hard STOP/no
  automatic re-arm and separate actual-TX evidence;
- the complete 125-leaf wishlist review and no-loss cost rule;
- three full-function nRF24 paths with simultaneous reception;
- ordinary 2.4/5 GHz Wi-Fi, IEEE 802.15.4, native BLE and 2.4 GHz/ESP-NOW
  capability requirements;
- packet Sub-GHz, broadcast receive, analog voice, audio, IR, external
  GNSS/LoRa/NFC, the external iButton/1-Wire adapter and their safety/evidence
  boundaries;
- open owner-controlled signed updates and the requirement that every selected
  programmable chip retain independent programming/recovery/diagnostics.

These are product inputs. Exact MCU/module ownership, pins, buses, board count,
connectors, parts and enclosure are not accepted.

## Correction completed

[`FND-0039`](../review/findings/FND-0039-architecture-frozen-before-product-design.md)
found that the former architecture chain skipped target physical design,
whole-product optimality and conceptual placement. The owner selected reopen
option A in [`DEC-0032`](../review/decisions/DEC-0032-reopen-product-design-before-cad.md).

Consequences:

- `DEC-0028/PKG-0001/SYN-3A` are historical candidate/reference evidence, not
  the target;
- C5 revision, compute ownership, pin and three-domain service studies are
  conditional candidate facts;
- the previously active C-001…005 KiCad library and CI are archived under
  [`premature-compute-cad-2026-08-16`](../../drafts/premature-compute-cad-2026-08-16/README.md);
- the pre-commit C-006 experiment is recorded as discarded in
  [`premature-service-cad-2026-08-16`](../../drafts/premature-service-cad-2026-08-16/README.md), without claiming a reproducible snapshot;
- active [`hardware/kicad`](../../hardware/kicad/README.md) contains only the
  upstream gate, not symbols, schematic or PCB.

`REV-0004H` reviews this correction. It does not review the new product design.

## Active next artifact

[`AUD-0005`](../review/audits/AUD-0005-m5-expansion-ecosystem-coverage.md)
reviews the M5 ecosystem: after rejected haptic, keyboard and generic-host
profiles leave the live denominator and external IMU remains correctly partial,
M5-only fully covers 20.0% of relevant classes and reaches 46.7% with partial/custom
iButton coverage, so the
90% attachment goal requires a separate high-speed tier, accepted in
`DEC-0034`. [`AUD-0004`](../review/audits/AUD-0004-current-competitor-capability-gap.md)
now resolves the delta one by one. `AUD-0007` reviewed haptic and corrected
the external-module coverage; `DEC-0036/REV-0002AJ` reject it from product
scope. [`AUD-0008`](../review/audits/AUD-0008-imu-instrument-value-and-placement.md)
and `DEC-0037/REQ-IMU-0001` close `W-EXTRA-14` as an optional external
measurement-pose profile. [`AUD-0009`](../review/audits/AUD-0009-physical-keyboard-product-archetype.md)
and `DEC-0038/REV-0002AN` close `W-EXTRA-15`: the base has no permanent
keyboard and bounded phone-assisted text never becomes local authority.
`AUD-0010/DEC-0039/REV-0002AP` close `W-EXTRA-16` without deleting a transport
later derived by a concrete RF/SDR profile. `AUD-0011` confirms no other active
base hardware is justified by unrelated functionality; BadUSB remains an
optional software-only exception.
Parallel G3 research starts from already reviewed capabilities and defines the physical
product without choosing electronics: form factor/use posture, control and
connector surfaces, display, battery/charging, external-module attachment,
antenna volumes, service access, environment/repairability and target cost.
Complete architecture alternatives require both the new G2 review and owner-
reviewed G3 output.
