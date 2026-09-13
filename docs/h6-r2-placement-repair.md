# H6.0.3-R1 · Placement repair

[Русский](h6-r2-placement-repair.ru.md) · [Interface review](h6-r2-interface-review.md)

2026-09-09: the separate [four-port GCT unification](h6-r2-component-unification.md) is implemented, with fresh native DRC/parity and preservation checks passed. Its [two-reference integration record](../hardware/layout/h6-r2-usb-unification-integration.json) supersedes the earlier JAE mouth datum, not the other placement corrections below.

**2026-09-13. The same left-side encoder moves upward, directly below Cap:
F270 [9.25,54], with U39 at B90 [15.4,89] and the internal headset at B0 [0.8,39].
Native integration, DRC/parity, labels, refreshed views and the full test run pass.
H6.0.3-R1 stays open, not fabrication or whole-device acceptance.**

## What we want

The holder must be centred, the encoder must really be on the left under Cap, the PTT
on the right, and ordinary electronics inside the sandwich. Ports, microphone,
speaker and their support circuits must be represented in the correct place.
A mirrored picture, an oversized reserve drawn as a body, or a part-count check
does not establish that result.

All positions below use native PCB coordinates. For the RF assembly transform,
`x_assembly = 80 − x_native`; native poses are not mirrored again. The selected
MPNs were unchanged by these placement-only corrections. The separate USB follow-up replaces RF J1 with GCT; electrical functions, board size and logical pin/net identities are retained.

## What was decided and corrected

| Area | Repair and limit |
| --- | --- |
| Holder / NTC | BT1 **F90 [40,85]**, removing the former +2.99-mm X displacement; R33/R34 **F90 [30.45,85] / [49.55,85]** follow the two nominal cell axes. Fab now distinguishes the real nominal **77.06 × 39.78 mm plastic body** from the dashed **86-mm pad-span reserve**. The already-corrected contact polarity is retained. This does not invent exact SMT lands, locator holes or thermal contact. |
| Internal power corridor | F2 stays inside at **B270 [53.37,47.87]**, near the centred BT1.3. U51 retains its centring-package position **B90 [40.05,53.5]**; U39 now moves separately to **B90 [15.4,89]** to clear the upper encoder. The original **2-mm fuse-owner locality** is not waived; the actual BT1.3–F2.1 span is **4.2731 mm**, below its 4.5-mm bound. |
| Encoder / PTT | SW3 is now **F270 [9.25,54]**, directly below Cap on the same left rear-outer side. The earlier **[9.25,81.25]** left/down pose is historical, not the current target. PTT SW4 stays on the right at **F0 [72.1,67.42]**; ordinary support parts remain inside. The nominal 15-mm knob leaves **5.48 mm to Cap / 3.3 mm to the holder** in plan, not qualified finger or 3D access. E/D and A/B/C identities and the existing engineering footprint remain unchanged. |
| Product USB | The preceding JAE repair used B180 [16.47,146.2], mouth Y149.8. The approved [GCT follow-up](h6-r2-component-unification.md) instead uses **B180 [16.47,146.325]** nominally, mouth **Y150 flush**; U5 moves 0.15 mm inward. Fresh native DRC/parity and preservation checks pass. Neither nominal datum qualifies actual plug-overmould fit. |
| Headset / microphone | U83 **SJ-43515TS-SMT-TR** moves inside to **B0 [0.8,39]**, retaining the outward left mouth at X−0.7; the former **[0.8,99.9]** is historical. MK1 remains **B0 [47,147.4]**, with its maximum body rim **0.5 mm inside** the bottom board edge; U85 stays **B90 [16.5,113.75]**. The microphone top port faces the inter-board space, with sound access through the designed open bottom gap; this does not turn the port normal downward or qualify acoustics. The former incorrect **F180 [8,112]** position stays superseded. |
| Actual supply locality | The UI moves remote bypass/bulk capacitors back toward their real owners: backlight switch, SD supply/card and three nRF modules. The checks name actual power pads, not whichever same-net pad is nearest. RF C259 becomes **B90 [61.275,82.125]** in the slot freed by the coordinated C230 relocation; its distances to U106.27 and .31 are **5.4200 / 7.3550 mm**, each bounded by 7.5 mm. C260/C261 remain separate local 100-nF bypasses. |
| Speaker representation | The wired **PUI Audio AS02404PO** body is registered on **UI B at [15.7,124]**, maximum **12.2 × 24.2 × 4.8 mm**. RF LS1 remains its electrical wire termination, not a second speaker body. C54 stays B0 and moves only **+0.30 mm Y** to **[14.805,136.905]**; its actual supply span improves to 3.8733 mm. Body registration is not acoustic or attachment qualification. |
| Microphone label | **UI F `MIC` [33,148.9]** identifies the RF microphone's bottom access: X33 = 80 − RF X47. It is a cross-board label, not an invented UI footprint. The abbreviation keeps the normal **1-mm text / 0.15-mm stroke** without overlapping `DOWN`. The RF `RF RP` / `BOOT` captions return to their uniform positions **[6,114.2] / [6,116.3]**; the former microphone-specific offset is withdrawn. |

The [under-Cap review](../hardware/layout/h6-r2-encoder-under-cap-review.json)
enumerates **106 previously unrouted RF references**, including SW3/U39/U83 and
the internal J3 shift of **+0.25 mm X** to **B90 [30.425,106.92]**. Local support
groups move with their real owners; U68 and U100 use explicitly reviewed compact
cells. C197, R169 and R235 are reserved but unchanged. The change preserves exact
MPNs, pad/net identities and **765 RF copper objects plus the unchanged UI's 92**;
native integration confirms their preservation.

The **2026-09-08 seven-part microphone correction** and the earlier **15 UI /
105 RF** package are historical scopes, not the new change list. RF remains
**12 on F / 768 on B**; UI stays 30 on F / 398 on B. The bottom microphone,
centred holder, service controls and four USB ports are not moved by this step.

The new review records **33 exact named-pad pair measurements**, including
regressions—not 33 electrical-performance passes. The upper headset's
`HEADSET_MIC_RAW` U83.1 → U85.3 straight span grows **23.229 → 80.397 mm**.
The compact U68 cell shortens its local selected/bias connections, but remote
`CAPTURE_RX_BIASED` and `CODEC_CAPTURE_VMID` branches become longer. Deliberate
low-noise routing and complete return-path review remain required. The relocated
UHF module also needs its RF feed, ground plane, power-delivery and coupling
review; geometric fit does not establish RF performance.

The selected `MIC_RAW` physical pad 1 → U85.1 span is **43.704–44.357 mm**
across its pads: a straight-line lower bound, **not a routed length or a qualified
quiet connection**. The capsule has an internal FET with a **2.2-kΩ load**;
`MIC_RAW` is not an unbuffered electret element. No new audio route is asserted.
Ground/ESD return, remote branches and measured noise/acoustics remain open.

The speaker contract reserves at least **0.8 mm diaphragm motion** and a
maximum **1.12 mm insulated mounting bed**. Its present Z screen uses existing
opposing-height metadata; this is not complete toleranced 3D proof, an adopted
tape MPN, or measured retention. The side sound path, wires and strain relief
still need implementation and inspection.

The repair preserves the prior **front-button symmetry**, ten indicators,
**14.7-mm SMA pitch**, recessed microSD and its access notch, upward display
FPC slot, M1 pair and board outline. It does not move other controls to imitate
the old H1 concept.

## Verification status

- The **106-reference native integration passes**, with **0 DRC violations /
  0 schematic-parity findings** and all **35/35 required RF labels** matched,
  with no collision candidates. Geometry passes **326 locality pairs / 72 critical
  spans, 0 placement conflicts**; the 33 pair reviews retain explicit regressions.
- All current views are refreshed and visually checked. System suite: **1482 tests
  (124 skips)**; KiCad-native H6 suite: **886 tests, no failures**.
- The preserved routing baseline is **857 copper objects: UI92 + RF765**,
  **197 resolved / 3071 unrouted connections**; this is not completed routing.

Historical only: the 2026-09-08 placement/microphone package passed DRC/parity,
1216-footprint parity, 20 intent checks, a 1383-test system run (95 skips) and
808 KiCad-native tests. Its 50-land SMA screen and five coax paths with at least
5.22 mm nominal slack remain prior evidence, not fresh qualification of this step.

The [current-routing audit](../hardware/layout/generated/H6-R2-current-routing-audit.json)
owns the live PCB hashes and source-bound checks; no old hash table is copied here.

The [shared validation command](../hardware/layout/h6_r2_validate.py), run with
KiCad Python, supports `--check --tests` and `--refresh --tests`. Refresh writes
derived files only; logs stay in ignored `work/`, and PCB changes stop the run.

## What remains open

The incorrect placements above are distinct from the existing unqualified
engineering boundaries:

- **Holder:** complete lands/locator registration, physical power routing,
  cell-floor geometry and actual NTC compression/thermal contact.
- **Encoder:** conditional rounded-slot and signal-hole fit, opposite-face
  protrusion and actual solder access. Both metal mounting lugs must be soldered;
  nominal clearances do not prove insertion, strength or the manufacturing process.
- **Audio:** noise-sensitive routing, real ground/ESD return, remote
  U68/U72/headset branches, sound transfer through the open bottom gap, speaker attachment and measured
  acoustics. Placement and direct spans do not qualify the whole audio path.
- **Other interfaces:** Cap mating/numbering, SMA finished-board thickness and
  antenna/tool fit, display folds/adhesive, card/plug tolerances and closed-device
  access remain bounded by the [interface review](h6-r2-interface-review.md).
- **Electrical behaviour:** power/startup and typed-ERC findings remain open.
  C5 BOOT connectivity, mux SEL/OE control and recovery under KILL are not repaired
  by this package. No safety interlock is relaxed and no prototype boot is claimed.

## Reproducible owners

The [placement contract](../hardware/layout/h6-r2-placement-contract.json) owns
exact poses and actual-pad limits. Narrow records describe
[UI supplies](../hardware/layout/h6-r2-ui-supply-locality.json),
[C259](../hardware/layout/h6-r2-slow-io-bulk-review.json),
[internal audio](../hardware/layout/h6-r2-inner-audio-candidate.json),
[seven-reference bottom microphone review](../hardware/layout/h6-r2-microphone-bottom-candidate.json),
[historical left encoder](../hardware/layout/h6-r2-encoder-left-candidate.json),
[current encoder-under-Cap review](../hardware/layout/h6-r2-encoder-under-cap-review.json) and
[the separate speaker body](../hardware/layout/h6-r2-speaker-body.json).
Historical rows and proofs remain immutable; explicit supersession metadata names
the current replacement owner. They are not fresh native receipts. The [current routing](h6-r2-current-routing.md) and
[component views](h6-r2-component-views.md) bind the actual promoted boards.

Earlier [holder-polarity evidence](../hardware/layout/h6-r2-holder-polarity-review.json)
and [encoder fit review](h6-r2-encoder-engineering-fit.md) remain source evidence,
not authority to restore their superseded placements. Current drawing fixes
do not make their remaining mechanics manufacturing-ready.
