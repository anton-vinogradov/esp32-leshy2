# H6.0.3-R1 · Placement repair

[Русский](h6-r2-placement-repair.ru.md) · [Interface review](h6-r2-interface-review.md)

**2026-09-08. The microphone is restored to the RF-inner bottom edge, with six
related parts relocated inside. Fresh native DRC/parity, placement, labels and
20 intent checks pass; views are refreshed. H6.0.3-R1 remains open; this is not
fabrication or whole-device acceptance.**

## What we want

The holder must be centred, the encoder must really be on the left, the PTT
on the right, and ordinary electronics inside the sandwich. Ports, microphone,
speaker and their support circuits must be represented in the correct place.
A mirrored picture, an oversized reserve drawn as a body, or a part-count check
does not establish that result.

All positions below use native PCB coordinates. For the RF assembly transform,
`x_assembly = 80 − x_native`; native poses are not mirrored again. The selected
MPNs, electrical functions, board size and logical pin/net identities are unchanged.

## What was decided and corrected

| Area | Repair and limit |
| --- | --- |
| Holder / NTC | BT1 **F90 [40,85]**, removing the former +2.99-mm X displacement; R33/R34 **F90 [30.45,85] / [49.55,85]** follow the two nominal cell axes. Fab now distinguishes the real nominal **77.06 × 39.78 mm plastic body** from the dashed **86-mm pad-span reserve**. The already-corrected contact polarity is retained. This does not invent exact SMT lands, locator holes or thermal contact. |
| Internal power corridor | F2 stays inside at **B270 [53.37,47.87]**, near the centred BT1.3. U51 moves only **1.20 mm left**, U39 **0.20 mm left**, with a bounded group of existing support parts. The original **2-mm fuse-owner locality** is not waived; the actual BT1.3–F2.1 span is **4.2731 mm**, below its 4.5-mm bound. |
| Encoder / PTT | SW3 becomes **F270 [9.25,81.25]**: left and explicitly **31 mm lower** than its former [71,50.25] shaft. Its ordinary support parts remain inside. PTT SW4 stays on the right. Rotation changes pad coordinates, not E/D or A/B/C identity. The existing engineering footprint is retained, not converted into a manufacturer-approved rounded-slot pattern. |
| Product USB | RF J1 becomes **B180 [16.47,146.2]**: the shell mouth is Y149.8, **0.2 mm nominally inside** the Y150 edge, replacing the previous 0.5-mm overhang. This 0.70-mm inward move is our placement choice, not a new JAE mounting recommendation. Plug-overmould fit remains open. |
| Headset / microphone | U83 **SJ-43515TS-SMT-TR** remains inside at **B0 [0.8,99.9]**. MK1 is **B0 [47,147.4]**, with its maximum body rim **0.5 mm inside** the bottom board edge. Its top port faces the inter-board space, with sound access through the designed open bottom gap; this does not turn the port normal downward or qualify acoustic performance. The former **F180 [8,112]** position between the service controls was an incorrect replacement of the intended inner/bottom placement and is superseded. |
| Actual supply locality | The UI moves remote bypass/bulk capacitors back toward their real owners: backlight switch, SD supply/card and three nRF modules. The checks name actual power pads, not whichever same-net pad is nearest. RF C259 becomes **B90 [61.275,82.125]** in the slot freed by the coordinated C230 relocation; its distances to U106.27 and .31 are **5.4200 / 7.3550 mm**, each bounded by 7.5 mm. C260/C261 remain separate local 100-nF bypasses. |
| Speaker representation | The wired **PUI Audio AS02404PO** body is registered on **UI B at [15.7,124]**, maximum **12.2 × 24.2 × 4.8 mm**. RF LS1 remains its electrical wire termination, not a second speaker body. C54 stays B0 and moves only **+0.30 mm Y** to **[14.805,136.905]**; its actual supply span improves to 3.8733 mm. Body registration is not acoustic or attachment qualification. |
| Microphone label | **UI F `MIC` [33,148.9]** identifies the RF microphone's bottom access: X33 = 80 − RF X47. It is a cross-board label, not an invented UI footprint. The abbreviation keeps the normal **1-mm text / 0.15-mm stroke** without overlapping `DOWN`. The RF `RF RP` / `BOOT` captions return to their uniform positions **[6,114.2] / [6,116.3]**; the former microphone-specific offset is withdrawn. |

This follow-up moves exactly **seven RF references: MK1, R206, C232, R205,
U85, C229 and R202**, all on B. The preceding **15 UI / 105 RF** package remains
the historical scope, not a new change list. The resulting RF inventory is **12 on F /
768 on B**; UI stays 30 on F / 398 on B. Selected MPNs, pad/net identities and
all **857 copper objects (UI92 + RF765)** are unchanged by this follow-up.

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

- Both corrected boards pass fresh native DRC: **0 rule violations / 0 schematic-parity
  findings**. All **1216 footprints**, including mounts, pass source/library pad
  parity. **1208 electrical positions** have zero placement conflicts;
  **326 locality pairs / 72 actual-pad critical spans** pass.
- Native user-label audits and **20 intent checks** pass, including the RF-inner
  bottom microphone and actual UI `MIC` text. The incorrect F-only microphone
  condition is replaced. Component, routing and product views are refreshed and
  visually reviewed; H1 remains an explicitly linked concept archive.
- All **50 SMA lands** have no foreign-pad contacts or body/courtyard candidates
  in the bounded solder-access screen. Five microcoax paths retain at least
  **5.22 mm nominal service slack**. This is not solder-process or assembled-3D approval.
- Copper remains **857 objects: UI92 + RF765**; **197 connections are resolved /
  3071 remain unrouted**. This follow-up changes no copper. Independent graph checks
  preserve connected pad/net identities on both boards, source pad multisets
  and copper.
- Repository suite: **1383 tests, OK, 95 environment-dependent skips**. The separate
  KiCad-native H6 run passes **808 tests, without skips**.

The [current-routing audit](../hardware/layout/generated/H6-R2-current-routing-audit.json)
owns the live PCB hashes and source-bound checks; no old hash table is copied here.

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
[left encoder](../hardware/layout/h6-r2-encoder-left-candidate.json) and
[the separate speaker body](../hardware/layout/h6-r2-speaker-body.json).
Candidate records retain their original scope/status; they are not fresh native
receipts. The [current routing](h6-r2-current-routing.md) and
[component views](h6-r2-component-views.md) bind the actual promoted boards.

Earlier [holder-polarity evidence](../hardware/layout/h6-r2-holder-polarity-review.json)
and [encoder fit review](h6-r2-encoder-engineering-fit.md) remain source evidence,
not authority to restore their superseded placements. Current drawing fixes
do not make their remaining mechanics manufacturing-ready.
