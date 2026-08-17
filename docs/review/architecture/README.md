# Product and architecture workspace

- Статус: **G2F logical/electrical feasibility active; architecture reopened**
- Correction: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)
- Sequencing refinement: [`DEC-0041`](../decisions/DEC-0041-electrical-feasibility-before-physical-layout.md)
- Integrated-mockup pause: [`DEC-0058`](../decisions/DEC-0058-internals-before-integrated-mockup.md)
- Method: [`FLOW-0001`](FLOW-0001-product-to-cad-gates.md)

## Canonical active chain

1. Reviewed intent/capability inputs from stages 1–2.
2. Logical/electrical feasibility: neutral semantic demand, real-device pin
   provenance and at least two complete owner/bus/GPIO candidates.
3. Owner-selected working electrical baseline, explicitly provisional.
4. Dependency-ordered internal closure through [`INT-0001`](INT-0001-internal-design-closure-sequence.md):
   compute/service, safety, power, UI/storage, audio, RF and expansion evidence.
5. Resume target physical/product mockup only after the joint internal paper
   review; any packing/RF/power conflict loops back visibly.
6. Whole-device optimality, conceptual co-design and owner decision.
7. Atomic architecture only after all prior gates pass.
8. Final components, electrical CAD, schematic and PCB afterwards.

The current active artifacts are `DEM-0001`, `SRC-0002`, `DSP-0001/0002`,
`CTL-0001`, [`NIF-0001`](NIF-0001-digital-noninterference-layout.md),
[`RFQ-0002`](RFQ-0002-g2f-3i-rf-concurrency-boundary.md) and the generated
`G2F-pin-ledger` plus focused
[`G2F-3I principled pinout`](generated/G2F-3I-principled-pinout.md).
`PIN-0003/REV-0004V` review the exact owner/contact projection;
`DEC-0052/REV-0004X` then allocate S3 GPIO41/42 to direct-QSPI D2/D3 and record
the then-current `S3=2, C5=1, RP=0, slow=P27` free-contact state. Subsequent
`AUDIO-0002/FND-0067` uses P27 for the omitted RX-audio source selector;
`DEC-0054/REV-0005D` then assigns S3 GPIO6 to reset-safe `AUDIO_ARM`. Current
free state is `S3=1 (GPIO47), C5=1, RP=0, slow=0` after `DEC-0059` restores
S3 UART0 and C5 native USB around the dedicated 1-bit SDIO link.
`DEC-0051` publishes that reviewed projection as the visible principle-level
working design in the root target document; it remains reopenable and is not
the G7 atomic architecture.
`DEC-0044/REV-0004L` make `G2F-3I` the leading reviewed paper
map under a digital no-neighbour-stall invariant. `FND-0053/REV-0004M` prove
that arbitrary cross-group co-located same-band TX↔RX cannot be promised;
`DEC-0045` selects one active group, while `SG-N24` explicitly requires every
simultaneous three-radio PTX/PRX mix. `DEC-0047` selects a qualified RF envelope.
`N24H-0001` separates ordered `L0 DIV↔DIV` pre-HIL from target `T1`, while
`N24M-0001/IMP-0040/DEC-0048` select three compact IPEX→external-SMA nRF paths
and external SMA for every onboard antenna endpoint; exact production lots,
feeds and measurements remain open.
`DEC-0046/QST-0001` require unused interfaces to
enter verified quiet states. It is not yet target: exact RF paths, power gates,
peripherals and HIL remain open; CAD stays blocked.
`AUDIO-0001/REV-0005B` close the exact ES8311 QFN-20 digital/contact fit:
S3 GPIO1/2/15/16/17/18 land on real I2C/I2S contacts, `CE` is address strap
`0x19`, and P10 is external `CODEC_PWR_EN`. `AUDIO-0002/REV-0005C` compare the
complete capture/playback/TX/reset path, add exact TAC5111IRGER reference
contacts and expose `FND-0067`; `DEC-0054` accepts the active-buffer ES8311
prototype plus direct arm and exact selector/gate/amp ICs. Passive analog
values, exact power circuit and HIL remain open.
`DEC-0058` now pauses the integrated mockup until the internal chain is jointly
reviewed. `INT-0001/I1` has **Проведено ревью** through
`DEC-0059/REV-0005L`: 1-bit C5 SDIO restores S3 UART0 and C5 native USB,
while M5 Unit UART moves to UART1 on the same pins. `I2` is active next.

## Active G2F artifacts

- [`INT-0001`](INT-0001-internal-design-closure-sequence.md) defines the
  dependency-ordered `I0…I9` paper/electrical closure required before the
  integrated physical mockup resumes;
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
- [`PIN-0003`](PIN-0003-g2f-3i-principled-pinout.md) and the generated
  [`pinout atlas`](generated/G2F-3I-principled-pinout.md) provide the requested
  principled owner/net/pad diagram and exact tables. `FND-0059` fixes stale
  pre-quiet-state budgets; `FND-0060` exposes every still-abstract electrical
  endpoint instead of presenting it as a finished schematic;
- [`REV-0005K`](../reviews/REV-0005K-vertical-living-principled-diagram.md)
  makes that diagram a narrow top-to-bottom living projection. Every accepted
  internals change must update both target README diagrams and the generated
  atlas in the same commit; regression checks current candidate MPN coverage;
- [`REV-0003Y`](../reviews/REV-0003Y-single-source-and-draft-pin-maps.md) reviews
  the generator foundation and explicitly leaves complete-candidate review open.
- [`DSP-0001`](DSP-0001-display-storage-real-device-evidence.md) replaces the
  inherited full-frame target with the accepted task/dirty-region contract;
- [`DSP-0002`](DSP-0002-fast-display-path-options.md) finds that display+SD is
  the only deliberately shared high-rate pair, exposes the stale U214-derived
  `256 B` quantum as `FND-0061`, and reviews direct S3 QSPI, EVE and fourth-MCU
  paths. `IMP-0044/A` is accepted by `DEC-0052`; the machine map now assigns
  S3 GPIO41/42 to QSPI D2/D3 and uses measured `<=1 ms` display occupancy;
- [`DSP-0003`](DSP-0003-exact-fast-display-shortlist.md) shows that the old
  4-inch ST7796S remains a valid A0 workload fixture but not a QSPI target.
  `DEC-0053` accepts the new 3.5-inch portrait `320×480` QSPI IPS+touch class;
  [`DSP-0004`](DSP-0004-display-part-number-register.md) lists every known
  display identifier and every production `TBD` without freezing a dev board;
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
  derive the physical acceptance envelope for all nRF PTX/PRX mixes;
- [`DEC-0047`](../decisions/DEC-0047-qualified-nrf-mix-with-external-observer.md)
  accepts the qualified-envelope option; [`N24H-0001`](N24H-0001-two-device-full-mix-fixture.md)
  uses the two ESP32-DIV units as `L0` pre-HIL and requires separate target
  `T1` DUT/observer evidence for production acceptance;
- [`QST-0001`](QST-0001-unused-interface-quiet-states.md) propagates
  [`DEC-0046`](../decisions/DEC-0046-unused-interface-quiet-by-default.md) into
  per-interface power-down, clock-parking and EMI proof contracts.
- [`ANT-0001`](ANT-0001-external-sma-path-inventory.md) reviews every onboard
  antenna endpoint against exact device pins. It finds two Si4732 input
  domains and rejects the legacy one-generic-port assumption;
  [`DEC-0049`](../decisions/DEC-0049-nine-dedicated-external-sma-paths.md)
  accepts nine labelled SMA with separate `RX-FM/SW` and `RX-AM/LW` paths.
- [`RFH-0001`](RFH-0001-module-to-external-sma-interface-review.md) separates
  five module-origin feeds from four PCB/frontend-origin feeds. It verifies
  first-generation U.FL/MHF I/AMC compatibility for S3/C5, records Ebyte
  `IPX` as unproven `FND-0057`, and opens external gender choice `IMP-0042`.
- [`RFH-0002`](RFH-0002-antenna-connector-ecosystem-review.md) checks actual
  antenna ecosystems instead of grouping only by frequency. It finds RP-SMA
  typical for native Wi-Fi, standard SMA in Ebyte's nRF ecosystem and both
  polarities in sub-GHz; `DEC-0050/REV-0004T` accept bounded
  `2 RP-SMA + 7 standard SMA` and made exact antenna sourcing the next gate.
- [`ANT-0002`](ANT-0002-current-orderable-antenna-shortlist.md) reviews exact
  current commercial candidates. It finds safe SKU sharing for S3/C5 and the
  three nRF paths, a combined 868/915 candidate, but no honest universal
  315–915 or full VHF/UHF radiator. `DEC-0055/REV-0005E` accept the profiled
  external kit and exact-MPN availability gate. `FND-0058` keeps production
  two-source and assembled-HIL qualification open; `MFG-0001/IMP-0047` cover
  one-stop PCBA plus loose-antenna kitting without yet constraining supplier.
- [`DSP-0002/REV-0004W`](DSP-0002-fast-display-path-options.md) review the
  display acceleration gate against the exact current pin budget. Direct QSPI
  fits with `GPIO41/42`; current RP/C5 display ownership and direct I80/RGB do
  not. `DEC-0052/REV-0004X` accept and propagate this path;
  `DEC-0053/REV-0004Z` accept the 3.5-inch display class while exact production
  assembly, optics and HIL remain open in `DSP-0004`.
- [`AUDIO-0001`](AUDIO-0001-es8311-exact-electrical-fit.md) records every
  ES8311 QFN-20 contact, proves the unchanged digital pin budget and corrects
  `CE` versus external power enable. [`AUDIO-0002`](AUDIO-0002-complete-audio-path-comparison.md)
  compares the whole fail-safe path; [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)
  is accepted as [`DEC-0054`](../decisions/DEC-0054-fail-safe-complete-audio-path.md)
  with propagation reviewed by `REV-0005D`.

## Deferred/reference G3 artifacts

- [`PD-0001`](../product-design/PD-0001-g3-physical-design-inputs.md) translates
  reviewed capabilities into physical field/control/safety/RF/expansion/service
  inputs and has received input review;
- [`LAY-0001`](../product-design/LAY-0001-form-factor-candidates.md) visualizes
  compact, balanced and field-service same-scope experiments. Its drawing
  content was reviewed, but its direction is superseded by `DEC-0041`; no owner
  choice among P1/P2/P3 is requested.
- [`PHY-0001`](../product-design/PHY-0001-u214-rear-dock-fit.md) retains the
  accepted bounded U214 rear-envelope decision; `DEC-0058` pauses further
  integrated mockup/control/enclosure work until `INT-0001/I9`.

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
