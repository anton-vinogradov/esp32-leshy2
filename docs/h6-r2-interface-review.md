# H6.0.3-R1 · Interfaces, cutouts and silkscreen

[Русский](h6-r2-interface-review.ru.md)

**Review date: 2026-09-07. Status: physical defects found; corrections incomplete.**
This is an intermediate review, not a phase closure or permission to manufacture.
The initial native-board snapshots exposed inward-facing ports. Corrections to
four USB ports, microSD and M1's planar registration have reached both boards.
Grove, IR, RUN/KILL, the headset cutout and battery-holder geometry still need
work, alongside assembled 3D access and display-fold verification. A clean
electrical DRC does not establish that a plug fits or that a required cutout exists.

## What remains unresolved after the follow-up

The [Cap mating review](../hardware/layout/h6-r2-cap-mating-review.json)
found that logical M5 numbering was copied directly onto Samtec's alternating
odd/even rows. An explicit physical permutation is required. The published
U214/U219 callouts do not establish which mating face is shown and disagree
with one another; **no candidate map has been applied**. Header-to-housing
registration is also unresolved. [Two questions sent to M5Stack on 2026-09-07](../drafts/h6-cap-pinout-question.md);
technical clarification is pending. Sending the inquiry does not approve any map or close the gate.

The [holder/encoder drawing review](../hardware/layout/h6-r2-holder-encoder-geometry-evidence.json)
confirms an encoder mounting-lug pitch of 12.5 mm, versus 11.2 mm in the
currently bound generic footprint. A separate dimension fixture exists, but
its proposed oval slots are not qualified or bound to production. The holder's
SMT lands and mechanical holes also need correction; the small locator's
longitudinal position has not been established. These are explicit release
blockers, not issues waived by a zero-finding DRC.

The H1-world → native-PCB seed conversion is now explicit: UI preserves X;
RF transforms the whole box as `x_native = board_width - x_world - width`.
Native overrides, antenna anchors and frozen poses bypass that conversion.
This prevents another double mirror of M1, but does **not** relocate existing
RF controls or establish full H1/native correspondence. That reconciliation
remains open alongside the exact mechanical corrections.

## What we want

External ports and controls must be accessible in the assembled device; both
boards must mate without forcing them. The display must retain its upward,
untwisted tail, usable cable slack and a clear adhesive landing. Footprints,
holes, cutouts and user labels must describe the actual parts and mounting
faces, not just reproduce the mockup.

## What we checked

The review enumerates **31 J-designated connectors and 43 other native
interfaces: 74 records**, across the 80 × 150 mm UI and RF boards. Enumeration
is not complete dimensional, electrical or functional verification of every row.
Checks use actual KiCad footprints, pad/drill coordinates, board and footprint
`Edge.Cuts`, the assembly coordinate model and selected manufacturer drawings.

| Connector group | UI references | RF references | Count |
| --- | --- | --- | ---: |
| Antenna SMA | J3, J7, J12, J14, J16 | J5–J9 | 10 |
| Board-local U.FL | J4, J8, J13, J15, J17 | — | 5 |
| USB | J9, J11 | J1, J4 | 4 |
| Internal debug/service headers | J2, J6, J10 | J2, J3, J13 | 6 |
| Display ZIF / microSD | J1 / J5 | — | 2 |
| M1 interboard pair | J18 | J12 | 2 |
| Cap dock / Grove | — | J10 / J11 | 2 |

The headset connector is **RF U83**, not another J reference. The additional
inventory covers it, BT1, buttons, encoder, RUN/KILL, indicators, IR devices,
microphone and speaker connection.

Coordinates below are the inspected native-board coordinates in millimetres.
F.Cu is exterior; B.Cu is inside the sandwich. With both antenna edges upward,
rear-board assembly coordinates are `x = 80 − native_x`, `y = native_y`.
This physical assembly transform is different from merely displaying a back
copper layer in the editor.

## What we found

These are findings from the immutable snapshots listed below, not assertions
that an ongoing source edit has already reached the current generated boards.

| Interface | Finding and consequence | Required correction / remaining evidence |
| --- | --- | --- |
| Four USB ports: UI J9/J11, RF J1/J4 | In the snapshot, B.Cu/0° sent the mating direction inward, not toward the bottom edge. The three GCT mouths lay at y142.360 rather than the intended y150 edge. | Corrected native poses now follow the exact GCT/JAE edge datums and pass native DRC; see below. This closes the planar orientation defect, not complete plug access in the closed device. [GCT sheet 1](https://gct.co/files/drawings/usb4105.pdf), [JAE-authored SJ121836 Rev.3, sheet 2](https://www.mikrocontroller.net/attachment/650878/SJ121836.pdf). |
| Grove RF J11; microSD UI J5 | In the snapshot, Grove pointed inward and microSD opened left into the PCB rather than out the bottom. | microSD now has an explicit outward pose and card-motion envelope below. Grove still needs its incorrect centred body datum repaired: rotating the old pose alone would put mounting copper beyond the board edge. [Grove drawing](https://statics3.seeedstudio.com/fusion/opl/datasheet/320110032.pdf), [Hirose DM3 drawing](https://www.hirose.com/en/product/document?clcode=CL0609-0031-0-00&documentid=0000947170&documenttype=2DDrawing&lang=en&productname=DM3AT-SF-PEJM5&series=DM3). |
| M1: UI J18 / RF J12 | Snapshot native centres were [42.5,122.25] and [42.5,122.5], both B0. After the rear assembly transform their axes differed by 5 mm in X and 0.25 mm in Y; centring alone would still leave the end order/polarization wrong. | Corrected native poses retain UI B0 [42.5,122.25] and use RF B180 [37.5,122.25]. All 80 contact assignments and the assembly transform pass source regressions; native DRC is clean. Exact body models and assembled Z/clearance checks remain open. [Hirose plug](https://www.hirose.com/product/p/CL0578-0523-1-92), [receptacle](https://www.hirose.com/en/product/p/CL0578-0823-5-92). |
| Headset RF U83 | The selected mid-mount jack requires a PCB cutout, but the RF board has only its outer contour and no cutout in either board or footprint `Edge.Cuts`. | Materialize the exact asymmetric profile, including reliefs; inspect every copper layer and opposing-side body space. Manufacturer page 2 specifies a 6.80 mm basic width, 11.50 mm depth and R0.30 reliefs. [Same Sky drawing](https://www.sameskydevices.com/product/resource/sj-43504-smt-tr.pdf). |
| Battery holder RF BT1 | The footprint has four SMT pads and no drills, despite the 1048P's underside locating features. Its 4 × 6 mm lands also differ from the manufacturer's minimum 7.3 × 6.4 mm pattern. | Rebuild from the exact drawing datums, including locating/retaining holes and land positions. The separate body-fastener holes must not be confused with mandatory locator clearance. Recheck local copper and M1 after correction. [Keystone K75, p29, dual-cell SMT drawing](https://www.keyelco.com/userAssets/file/K75p29.pdf). |
| IR emitter UI D11 | Its lens points along the board rather than out the left edge. The custom “recommended” land pattern has the wrong dimensions and pitch. | Correct lands, polarity and lens/body datum before choosing the outward pose. Manufacturer lands are 0.90 × 1.40 mm on 2.70 mm centres. [Vishay VSMY14940, p5](https://www.vishay.com/docs/84209/vsmy14940.pdf). |
| IR receivers UI U24/U23 | U24's axis is parallel to the left edge; U23 points outward, but the custom body proxy does not establish the real lens-to-pad-row offset or tape presentation. | Resolve each exact package's optical datum; do not treat a rotation-only check as complete access verification. [TSMP95000, p4](https://www.vishay.com/docs/82907/tsmp95000.pdf), [TSOP752 package](https://www.vishay.com/docs/82494/tsop752.pdf). |
| RUN/KILL RF SW5 | Subsequent primary review confirms two defects: common terminal 2 belongs on the opposite package side, not in the current row with 1/3; the selected SC actuator projects normal to the PCB into the sandwich at B.Cu. An XY rotation cannot make it a side-exiting actuator. | Correct the physical lands and mounting/access solution. The recommended pads are 1.0 × 2.5 mm with terminal 2 opposite 1/3; nominal height including actuator is 5.5 mm, with 2 mm slide travel. No replacement MPN has been selected. [C&K/Littelfuse JS, 2026 revision, pp1/5](https://www.littelfuse.com/assetdocs/littelfuse-c-k-slide-js-series-datasheet?assetguid=aba42b08-0d2c-423b-813d-a2faa5a3bb14). |
| Microphone RF MK1; speaker LS1 | The top-port microphone opens into the sandwich. LS1 is a two-pad wire termination, not the actual 24 × 12 × 4.5 mm speaker body. | Define the sound path, speaker mount/diaphragm clearance and wire strain relief; document the assembly operation. Pad connectivity does not prove acoustic performance. [Microphone](https://www.sameskydevices.com/product/resource/cmej-0413-42-smt-tr.pdf), [speaker](https://api.puiaudio.com/filename/AS02404PO.pdf). |
| SMA thickness fit and assembled access | All ten SMA axes point outward, but the 1.75 ± 0.10 mm connector slot and 1.60 ± 0.16 mm PCB envelope can overlap by 0.11 mm at their worst endpoints. The 11 mm interboard gap is not full body/plug clearance evidence. | Resolve finished-thickness acceptance without assuming prongs may be spread. Complete opposing-body, solder-tail, cable and plug/finger clearance checks in the assembled frame. [GCT SMA31 drawing](https://www.mouser.com/datasheet/3/1507/1/RFPC-SMA31-FN.pdf), [SMA32 drawing](https://www.mouser.com/datasheet/3/1507/1/RFPC_SMA32_FN.pdf), [PCB capability](https://jlcpcb.com/capabilities/pcb-capabilities). |

The initial mechanical snapshot left M1's mixed coordinate frames unresolved.
The subsequent connector review resolves that interpretation and confirms the
mating defect; it does not silently rewrite the earlier observation.

## What was corrected / current verification

This section records work after the snapshots; it does not change their original
observations or mark the whole interface review as passed.

- Six service-button orientation corrections have reached the native boards:
  four on the UI right edge and two on the RF right edge. The two UI left-edge
  buttons already faced outward. All ten user indicators, **UI D1–D10**, have
  moved from interior B.Cu to the accepted exterior F.Cu design datums.
- Four USB ports and microSD have explicit B.Cu/180° targets locked against
  automatic rotation or repacking and have been applied to the native boards.
  The three GCT anchors retain X = 14.87 / 26.10 / 42.53 and
  use Y = 146.325, putting their manufacturer PCB-edge datum at Y = 150.
  JAE RF J1 uses [63.53,146.90]: its exact mounting pattern puts the PCB edge
  at Y = 150 and shell mouth at Y = 150.50; copper remains at or below
  Y = 149.35. The intended 0.50 mm shell overhang is not an off-board copper pad.
  JAE's local EdgeSilk variant now matches the controlled library without
  a mismatch exception; only silk was trimmed, not pads, nets or MPN.
- microSD UI J5 uses [61.005,141.875], with its shell mouth flush with Y = 150.
  The drawing gives **4.0 mm ejection travel** and a separate **0.8 mm inward
  push stroke**. The locked card protrudes 1.6 mm; the ejected card protrudes
  5.6 mm. These are explicit access envelopes, not extra body courtyard.
  Only its four local support parts U6/U7/R39/R41 were repositioned to clear
  the corrected socket; their side, rotation, nets and MPNs were preserved.
- Native user silkscreen now has 63 labels tied to actual controls
  and port roles, including distinct **UP** and **OK**. Text presence does not
  by itself prove readability or solder-mask clearance. DISPLAY/PSA borders
  use corner markers instead of continuous lines; their placement envelopes
  are unchanged.
- The follow-up antenna identity review corrected RF J6 to **UHF TX** and
  RF J7 to **VHF TX**. The former positional zip of H1 labels and H6 ports
  reversed these two names. All ten labels now follow their physical instance;
  the native audit also checks each signal pad 1 against its expected RF net.
  No antenna, net, footprint or copper geometry moved in this correction.
- Mounting-axis validation now requires all four distinct holes on **each**
  PCB, transformed separately into assembly coordinates. The former union
  could hide missing RF holes behind the UI set. Negative tests remove,
  duplicate and shift holes. A native M1 check reads all 80 pad pairs and
  rejects an in-memory RF rotation or offset without saving either board.
- The M1 correction is now native: RF J12 B180 [37.5,122.25], keeping UI J18
  unchanged. Only RF R235 [25.25,127.5], B0, and C253 [22.30,128.5], B90, were
  repositioned locally for clearance. Twelve regressions check all 80 contact
  assignments, the assembled-coordinate transform and the nominal 11 mm
  mating height. The corrected connector and both support parts are in the
  native RF PCB. Generic M1 models are not exact body proof: assembled Z and
  clearance remain open. [M1 regression scope](../hardware/architecture/tests/test_h6_r2_m1_mating.py).

The source-level candidate placed all 1208 instances without courtyard,
locality or critical pad-distance violations. The 27 targeted connector,
service-button and indicator tests passed. A native connectivity inspection
found no existing track/via connections to any of the five ports or four moved
SD support parts, so these moves do not detach a previously connected manual
route. Fresh DRC after integration is recorded separately below.
The native update preserved the exact signature of all 787 existing copper
objects; preservation alone is not a routing-completion claim.

Current verification is deliberately scoped:

| Check | Latest result / boundary |
| --- | --- |
| Native user-label audit | `pass_scoped`, 63 labels including all ten RF identities and signal-pad nets; UI control-label layout was also visually inspected. Not a complete package-silkscreen or closed-device readability pass. |
| UI native DRC | 0 violations, 0 schematic parity findings after integration. |
| RF native DRC | 0 violations, 0 schematic parity findings after integration; JAE EdgeSilk matches its controlled library without exceptions. |
| M1 | Native correction applied; 12 source regressions pass. All 80 contact assignments and planar assembly transform checked; exact 3D/Z remains open. |
| Whole checkpoint | Hardware: 766 tests, OK (1 native-extraction test skipped in system Python and run separately under KiCad Python). Firmware: 108 tests, OK (18 skips); metadata synchronization only, no target rebuilds. No manufacturing release. |

Still open: Grove and IR footprints/poses; RUN/KILL lands/access; the audio
cutout; holder drills/lands; SMA thickness fit; exact 3D bodies and assembled
clearances, acoustics and FPC folds. The 74-row inventory is exhaustive within
its stated scope, not 74 completed dimensional or functional verifications.
Labels for the still-moving Grove, audio, IR and RUN/KILL interfaces must be
finalized after their footprints and placement are corrected; the 63-label
result does not close that remaining work.
The placement
targets and test scope are recorded in the
[placement contract](../hardware/layout/h6-r2-placement-contract.json) and
[connector orientation regressions](../hardware/architecture/tests/test_h6_r2_connector_orientation.py).

## What is already established, within a limited scope

- The display slot exists in native UI `Edge.Cuts`: a 27 × 1.2 mm capsule,
  R0.6, x[26.5,53.5], y[31.5,32.7]. J1 at [40,35.4], B0, opens toward it;
  the nominal mouth gap is 0.8 mm. Explicit mating is panel contact `n` →
  Hirose contact `51−n`, preserving the untwisted upward-exit fold.
  [Panel drawing](https://www.buydisplay.com/download/manual/ER-TFT035IPS-6_Datasheet.pdf),
  [exact Hirose drawing](https://www.hirose.com/en/product/document?clcode=CL0580-1266-2-50&documentid=0001483059&documenttype=2DDrawing&lang=en&productname=FH34SRJ-50S-0.5SH%2850%29&series=FH34SRJ).
- That orientation is **not** final fold proof. The contract still needs a
  neutral-axis route no longer than 24.66 mm to retain at least 5 mm slack from
  the minimum 29.66 mm tail, the actual bend envelope, folded stack ≤0.714 mm
  and adhesive clearance ≥0.20 mm. Establish source-backed feasibility before
  manufacture; dry-fit the received display before irreversible bonding.
- The inspected PSA rectangle has no native front-face pad or via centres
  inside it. This is not a complete rear-of-panel flatness or body-height check.
- Both boards have four Ø2.7 NPTH mounting holes at [5,11], [75,11], [5,145]
  and [75,145]. The inspected pad bounding boxes remain outside the declared
  R4 screw-head keepouts; this does not qualify silk, real bodies or tolerances.
- M1 has SMT electrical contacts and NPTH plastic locators, not 80 through-hole
  electrical leads. USB shell tabs, the Cap socket and encoder do include
  through-hole terminals; their opposite-face protrusion still needs checking.
- The Cap socket's KiCad “Horizontal” name was a false alarm: its exact Samtec
  drawing shows vertical pass-through mating. This clears the direction
  suspicion only, not Cap keying, retention or installed body clearance.
  [Samtec, sheet 1 and section A–A](https://suddendocs.samtec.com/prints/hle-1xx-02-xx-dv-xe-xx-mkt.pdf).
- U.FL mates normal to the inner PCB surface. The six internal debug headers
  are intended for access after opening the device; inward placement is not
  itself a defect. Neither observation is a full cable/plug-access pass.

## Next repair order

Next correct the remaining Grove, IR and RUN/KILL footprints and datums;
retain the now-corrected USB, microSD and M1 planar registration. Add the required cuts
and holes, recheck both faces and every copper layer, and reroute affected nets.
After regeneration, repeat native DRC and the interface tests. Finally check
the assembled bodies, inserted plugs, display fold, optical/acoustic paths and
silkscreen together. The assembled-body work remains part of open H6.0.7.

These are engineering corrections, not a request to buy different parts or
increase the board size. No MPN substitution, order, full functional sign-off
or manufacturing release follows from this review.

## Evidence and snapshot boundary

- [Mechanical findings](../hardware/layout/h6-r2-interface-review-findings.json):
  2026-09-07 16:21:55 UTC; dimensions, drilled features, native hashes and
  per-finding evidence.
- [Connector/interface inventory and findings](../hardware/layout/h6-r2-connector-review-findings.json):
  2026-09-07 16:24:49 UTC; all 74 records, reviewed directions, primary sources
  and explicit limitations.
- [Subsequent JAE/Grove/RUN-KILL datum review](../hardware/layout/h6-r2-interface-datum-review.json):
  exact JAE mounting pattern, official Seeed CAD alignment and confirmed switch
  land/actuator defects, with source hashes and a separate implementation boundary.
- [Native user-silkscreen audit](../hardware/layout/generated/H6-R2-user-silkscreen-audit.json):
  scoped current-label checks bound to input hashes, not a whole interface release.
- [UI native board](../hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb),
  [RF native board](../hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb),
  [instance ledger](../hardware/ecad/generated/H2-R2-native-instance-ledger.json).
- [Assembly coordinate model](../hardware/product-design/assembly-coordinate-model.json)
  and [display mounting contract](../hardware/product-design/display-mount.json).

The JSON files bind their observations to the recorded board SHA-256 values.
Concurrent corrections already change native files: these snapshots must be
superseded or accompanied by fresh repair evidence, not presented as a live
all-clear result.
