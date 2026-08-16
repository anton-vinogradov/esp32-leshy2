# Product and architecture workspace

- Статус: **target product design active; architecture reopened**
- Correction: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)
- Method: [`FLOW-0001`](FLOW-0001-product-to-cad-gates.md)

## Canonical active chain

1. Reviewed intent/capability inputs from stages 1–2.
2. Target physical/product design: form factor, interaction, controls,
   interfaces, battery, antenna/service/environment/cost envelopes.
3. At least two complete whole-device candidates derived from those inputs.
4. Reviewed criteria weights, score/Pareto/sensitivity and owner decision.
5. Conceptual block/board/RF/power/thermal/service placement.
6. Atomic architecture only after all prior gates pass.
7. Exact components, electrical CAD, schematic and PCB afterwards.

The current active artifact is the product-design stage. Exact MCU ownership,
buses, pins, connector counts and CAD are intentionally open.

## Active reviewed prerequisites

- reviewed stage-1 intent and safety/legal decisions;
- reviewed `REQ-*` behavior, evidence, concurrency and failure obligations with
  owner/backend clauses reopened by `DEC-0032`;
- `INV-0002/0004` for the prior 125 leaves, the current-competitor delta in
  [`AUD-0004`](../audits/AUD-0004-current-competitor-capability-gap.md), and the
  M5 expansion audit [`AUD-0005`](../audits/AUD-0005-m5-expansion-ecosystem-coverage.md),
  plus the former FIDO audit retained only as superseded evidence
  [`AUD-0006`](../audits/AUD-0006-fido-authenticator-security-boundary.md),
  haptic prerequisite audit
  [`AUD-0007`](../audits/AUD-0007-haptic-product-mechanical-cost.md) and IMU
  instrument-value audit
  [`AUD-0008`](../audits/AUD-0008-imu-instrument-value-and-placement.md), plus
  physical-keyboard archetype audit
  [`AUD-0009`](../audits/AUD-0009-physical-keyboard-product-archetype.md), and
  High-Speed USB host audit
  [`AUD-0010`](../audits/AUD-0010-high-speed-usb-host-use-cases.md), and
  mission-scope audit
  [`AUD-0011`](../audits/AUD-0011-radio-key-product-scope.md), and 6 GHz/Wi-Fi
  6E fact review
  [`AUD-0012`](../audits/AUD-0012-6ghz-wifi6e-product-scope.md).

`W-EXTRA-11` is reviewed by `DEC-0033/REQ-IBTN-0001`; M5-first Unit/Cap plus a
separate high-throughput class without native M5-Bus is reviewed by
`DEC-0034/REQ-EXT-0001`. `W-EXTRA-12` is reviewed by
former `DEC-0035/REQ-FIDO-0001` is removed from target by `DEC-0039`; product
haptic is rejected by `DEC-0036`; optional
external IMU measurement pose is reviewed by `DEC-0037/REQ-IMU-0001`. G2
also closes `W-EXTRA-15` through `DEC-0038`: no integrated keyboard, bounded
phone-assisted text. `DEC-0039/REQ-SCOPE-0001` reject generic `W-EXTRA-16`,
retain only RF-derived high-throughput transport and classify BadUSB as a
software-only exception. `W-EXTRA-17` has reviewed prerequisites and remains
an owner placement decision through `IMP-0034`. G3 research
may proceed, but cannot receive final review until G2 closes.

## Candidate/reference studies

- Former [`CAP-0001`](CAP-0001-zero-based-capability-input.md),
  [`CON-0001`](CON-0001-hardware-neutral-concurrency-model.md),
  [`RES-0001`](RES-0001-hardware-neutral-resource-demand.md),
  [`SRC-0001`](SRC-0001-primary-hardware-resource-facts.md),
  [`SYN-0001`](SYN-0001-zero-based-whole-device-candidates.md),
  [`PIN-0002`](PIN-0002-zero-based-exact-pin-maps.md),
  [`BUD-0002`](BUD-0002-zero-based-memory-traffic-budget.md),
  [`PWR-0001`](PWR-0001-zero-based-power-safety-envelope.md),
  [`RFQ-0001`](RFQ-0001-zero-based-rf-zoning-coexistence.md),
  [`CST-0001`](CST-0001-dated-candidate-cost-burden.md) and
  [`PKG-0001`](PKG-0001-zero-based-target-architecture-proposal.md) preserve
  useful electronic-placement arithmetic and risks.

They were reviewed for internal consistency, but not against a prior physical
product design or whole-product optimality model. None is a final prerequisite.
`SYN-3A` is one candidate among future alternatives, not the target.

## Archives

- [premature compute CAD](../../../drafts/premature-compute-cad-2026-08-16/README.md);
- [premature service CAD](../../../drafts/premature-service-cad-2026-08-16/README.md);
- [earlier legacy-derived stage 3](../../../drafts/stage3-legacy-derived-2026-08-16/README.md).

Every later artifact receives **«Проведено ревью»** only for its own reviewed
scope; no status propagates automatically to the next gate.
