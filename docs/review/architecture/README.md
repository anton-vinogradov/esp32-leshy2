# Product and architecture workspace

- Статус: **G2F logical/electrical feasibility active; architecture reopened**
- Correction: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)
- Sequencing refinement: [`DEC-0041`](../decisions/DEC-0041-electrical-feasibility-before-physical-layout.md)
- Method: [`FLOW-0001`](FLOW-0001-product-to-cad-gates.md)

## Canonical active chain

1. Reviewed intent/capability inputs from stages 1–2.
2. Logical/electrical feasibility: neutral semantic demand, real-device pin
   provenance and at least two complete owner/bus/GPIO candidates.
3. Owner-selected working electrical baseline, explicitly provisional.
4. Target physical/product design by adapting the checked legacy mockup; any
   packing/RF/power conflict loops back to the electrical candidates.
5. Whole-device optimality, conceptual co-design and owner decision.
6. Atomic architecture only after all prior gates pass.
7. Exact components, electrical CAD, schematic and PCB afterwards.

The current active artifacts are `DEM-0001`, `SRC-0002`, `DSP-0001`,
`CTL-0001`, [`NIF-0001`](NIF-0001-digital-noninterference-layout.md),
[`RFQ-0002`](RFQ-0002-g2f-3i-rf-concurrency-boundary.md) and the generated
`G2F-pin-ledger`. `DEC-0044/REV-0004L` make `G2F-3I` the leading reviewed paper
map under a digital no-neighbour-stall invariant. `FND-0053/REV-0004M` prove
that arbitrary cross-group co-located same-band TX↔RX cannot be promised;
`DEC-0045` selects one active group, while `SG-N24` explicitly requires every
simultaneous three-radio PTX/PRX mix. `FND-0054/IMP-0039` keep its exact RF
sensitivity envelope open. `DEC-0046/QST-0001` require unused interfaces to
enter verified quiet states. It is not yet target: exact RF paths, power gates,
peripherals and HIL remain open; CAD stays blocked.

## Active G2F artifacts

- [`DEM-0001`](DEM-0001-current-semantic-signal-demand.md) reconstructs current
  signal demand without inheriting an owner;
- [`SRC-0002`](SRC-0002-real-device-pin-provenance.md) requires the full
  SoC/package/module/carrier chain and records the first verified candidates;
- [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md) records which
  geometry/checks from the old drawing generator will be reused after pin review;
- [`REV-0003X`](../reviews/REV-0003X-electrical-feasibility-entry.md) reviews the
  sequencing correction and these inputs.
- [`DEC-0042`](../decisions/DEC-0042-single-source-architecture-data.md) accepts
  one machine-readable device/net source; [`G2F-pin-ledger`](generated/G2F-pin-ledger.md)
  renders three structurally checked maps including leading `G2F-3I`;
- [`REV-0003Y`](../reviews/REV-0003Y-single-source-and-draft-pin-maps.md) reviews
  the generator foundation and explicitly leaves complete-candidate review open.
- [`DSP-0001`](DSP-0001-display-storage-real-device-evidence.md) replaces the
  inherited full-frame target with the accepted task/dirty-region contract;
- [`CTL-0001`](CTL-0001-slow-control-and-external-i2c-boundary.md) proves that
  current validation closes MCU accounting only, derives the open slow-control
  envelope and records the required external-I²C fault boundary;
- [`DEC-0044`](../decisions/DEC-0044-delegated-noninterference-layout.md) accepts
  the 24-endpoint/separated-I²C invariant and delegates layout search;
  [`NIF-0001`](NIF-0001-digital-noninterference-layout.md) records the selected
  paper arrangement and rejected bandwidth/controller variants.
- [`RFQ-0002`](RFQ-0002-g2f-3i-rf-concurrency-boundary.md) applies real
  shared-chain/range/power facts to `G2F-3I`; [`FND-0053`](../findings/FND-0053-arbitrary-colocated-rf-concurrency-is-impossible.md)
  separates impossible arbitrary cross-group TX↔RX concurrency from mandatory
  three-nRF full-function concurrency,
  and [`IMP-0038`](../improvements/IMP-0038-visible-qualified-rf-arbiter.md)
  records the accepted group arbiter. [`FND-0054`](../findings/FND-0054-three-nrf-mix-needs-rf-acceptance.md)
  and [`IMP-0039`](../improvements/IMP-0039-three-nrf-full-mix-acceptance.md)
  reopen the physical acceptance envelope for all nRF PTX/PRX mixes;
- [`QST-0001`](QST-0001-unused-interface-quiet-states.md) propagates
  [`DEC-0046`](../decisions/DEC-0046-unused-interface-quiet-by-default.md) into
  per-interface power-down, clock-parking and EMI proof contracts.

## Deferred/reference G3 artifacts

- [`PD-0001`](../product-design/PD-0001-g3-physical-design-inputs.md) translates
  reviewed capabilities into physical field/control/safety/RF/expansion/service
  inputs and has received input review;
- [`LAY-0001`](../product-design/LAY-0001-form-factor-candidates.md) visualizes
  compact, balanced and field-service same-scope experiments. Its drawing
  content was reviewed, but its direction is superseded by `DEC-0041`; no owner
  choice among P1/P2/P3 is requested.

No electronic zone in `LAY-0001` assigns a chip, bus or pin. Former
`SYN/PIN/PKG` arithmetic may be reused only after exact-device revalidation.

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
software-only exception. `DEC-0040` rejects `W-EXTRA-17` 6 GHz/Wi-Fi 6E from
base and optional product scope. `REV-0002AS` closes repeated G2 review; G3
target product design is now the active gate.

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
