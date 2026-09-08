# H6.0.3-R1 · Interfaces, cutouts and silkscreen

[Русский](h6-r2-interface-review.ru.md)

**2026-09-08: the [verified placement-repair package](h6-r2-placement-repair.md) recentres the holder, restores the left encoder and internal headset, recesses product USB and corrects local supplies and speaker representation. Fresh native DRC and schematic parity pass on both final boards. H6.0.3-R1 remains open and is not fabrication-ready.**

H1 remains a concept drawing, not a complete parity view of the current PCB.
A part being present in an image does not prove the right placement, a functioning
interface or assembled clearance. The new package corrects those distinctions
without changing selected MPNs or electrical functions.

## What we want and what was checked

Ports and controls must be accessible with the boards assembled. M1 must mate
without force; the display tail must exit upward without twisting, with slack
and a clear adhesive landing. Holes, footprints and labels must describe the
actual parts, not merely reproduce the mockup.

The initial inventory enumerated **31 J-designated connectors plus 43 other
interfaces: 74 records** on two 80 × 150 mm boards. This is an inventory, not
74 completed functional or dimensional verifications. The headset is **RF U83**;
the remaining records include buttons, BT1, encoder, indicators, IR and acoustics.

The inventory guard requires **74/74 present exactly once**, with identities
and poses compared against current native data. Component views cover the
**1208-position instance ledger**, including processors, radios and power/safety
parts, plus eight mounting footprints. This is coverage, not assembly approval.
[Four-face views](h6-r2-component-views.md) expose reverse-side USB, Cap, encoder
and SMA lands; drilled holes alone were an incomplete depiction. Display, cells,
loose coax and the wired speaker need separate assembly representations and
clearance checks; their absence as soldered footprints is not a missing component.

| Connector group | UI references | RF references | Count |
| --- | --- | --- | ---: |
| Antenna SMA | J3, J7, J12, J14, J16 | J5–J9 | 10 |
| Board-local U.FL | J4, J8, J13, J15, J17 | — | 5 |
| USB | J9, J11 | J1, J4 | 4 |
| Internal debug/service | J2, J6, J10 | J2, J3, J13 | 6 |
| Display ZIF / microSD | J1 / J5 | — | 2 |
| M1 interboard pair | J18 | J12 | 2 |
| Cap dock / Grove | — | J10 / J11 | 2 |

Coordinates below are native PCB millimetres, not H1 callout coordinates.
With both antenna edges upward, the RF assembly transform is
`x_assembly = 80 − x_native`, `y_assembly = y_native`. A back-layer editor view
is not a substitute for that physical transform. Explicit native overrides and
frozen poses must not be mirrored a second time.

## What changed in connector spacing and card access

| Interface | Integrated geometry and exact limit |
| --- | --- |
| Both five-SMA banks | Native X centres are **[10.6,25.3,40,54.7,69.4]**: **14.7 mm pitch**, instead of 11.75 mm. With the **9 mm connector bodies**, the nominal adjacent-body gap grows from 2.75 to **5.7 mm**. This provides more room around the connectors; it is not a measurement of antenna-base diameter or proof of finger/tool access with all antennas fitted. Antenna assignments, outward direction and exact MPNs are unchanged. |
| UI microSD J5 and six support parts | The group moves **−1.8 mm in Y**; J5 becomes B180 **[61.005,140.075]**, card axis X61.43. Shell mouth: **Y148.2**. Card edge when locked: **Y149.8**, nominally **0.2 mm inside the ordinary Y150 board edge**; fully pressed: **Y149.0**; ejected: Y153.8. The separate 0.8 mm push stroke and 4.0 mm ejection travel are retained. All these positions are nominal, not tolerance bounds. |
| UI card-access notch | An open **10 × 1.2 mm, R0.6** recess occupies X[56.43,66.43], Y[148.8,150]. Its local edge at **Y148.8** leaves the nominal card edge accessible in both locked and fully pressed positions. This is our PCB access choice, **not a Hirose-mandated notch**. The 80 × 150 mm outer envelope, mounting holes and display-FPC slot are unchanged. Actual card/connector tolerances and closed-device finger access remain open. |
| RF USB J1 | The new repair changes the previous 0.5-mm overhang to a **0.2-mm nominal recess**: B180 **[16.47,146.2]**, shell mouth Y149.8. The 0.70-mm inward move is a project-specific placement, not a revised JAE recommendation or proof of plug-overmould access. |

The larger SMA pitch improves the available connector spacing, but real antenna
bases, the assembled inter-row Z separation, screw-head access, two-sided solder
prongs and microcoax bends must still be checked together. Local U.FL/support
repositioning is part of this correction; it does not qualify assembled cable fit.
The separate **1.75 ± 0.10 mm slot versus 1.60 ± 0.16 mm PCB** issue remains
open: this envelope still permits **0.11 mm interference**.

## Current placement repair

The [placement-repair report](h6-r2-placement-repair.md) owns the exact current
poses, finite 15-UI/105-RF change list and combined verification results. It
replaces the earlier displaced holder, right-hand encoder and exterior audio
placement. Existing button symmetry, SMA pitch, card recess and display slot
are retained; the report distinguishes corrected positions from assembly limits.

## Earlier integrations — historical scope

The earlier RF 24-reference slice covered bottom ports, service switches, PTT
and the first TS-headset integration. Its outward-facing ports and correct
electrical identities are retained, but the former **F-side U83/supports** and
**J1 overhang** are superseded above. The subsequent holder-polarity correction
fixed the same-end-positive error; its old displaced holder/F2 coordinates
are also superseded by the centring package, not restored from old snapshots.
[Polarity integration](../hardware/layout/h6-r2-holder-polarity-integration.json),
[exact TS audio drawing](https://www.sameskydevices.com/product/resource/digikeypdf/sj-4351x-smt.pdf).

The preceding SMA solder-access correction moved 10 UI and 14 RF neighbours,
not the SMA banks. It retained the S3 cable's **5.223 mm** nominal calculated
reserve and removed the then-nine flagged lands in the finite 1-mm axis-expansion
screen. That record does not qualify tools, antenna bases or the soldering process.
[Current SMA access screen](h6-r2-component-views.md#sma-solder-site-checks).

M1 retains UI J18 B0 [42.5,122.25] and RF J12 B180 [37.5,122.25]. Its 80
contact assignments, planar registration and nominal 11-mm mating height are
guarded; generic body models do not close actual assembled Z.
[Hirose plug](https://www.hirose.com/product/p/CL0578-0523-1-92),
[receptacle](https://www.hirose.com/en/product/p/CL0578-0823-5-92).

## What the checks establish

| Check | Result and limit |
| --- | --- |
| Combined repair | Fresh DRC/schematic parity, source/library pad parity, user labels, current views and both test suites pass on the integrated boards; exact scope and counts are in the [repair report](h6-r2-placement-repair.md). The [current-routing audit](../hardware/layout/generated/H6-R2-current-routing-audit.json) owns live PCB hashes and hash-bound receipts. |
| Copper / routing | The package retains **857 copper objects: UI92 + RF765**. Holder centring needs one explicitly reviewed via and its two attached segments to move; unaffected copper and connected-pad adjacency are guarded. **3071 connections remain unrouted**; retained copper is not completed routing. |
| Native integration | Finite reference/graphic/copper allowlists reject unlisted changes, lost pads and duplicate UUIDs. Pin/net identity, unchanged footprints and exact source/library pad parity have been checked on the combined boards. |
| Electrical scope | No selected MPN, signal function, GPIO or logical net is changed by these placements. The encoder's physical pad coordinates change with its real move, but E/D and A/B/C identities do not swap. Existing electrical defects are not repaired by relocating or drawing their parts. |
| Labels and images | Fresh label and component-view audits bind the current PCB hashes. Fab bodies, assembly reserves and explanatory annotations are not silkscreen, routed copper or fitted cells/cables. The prior scoped label pass is not silently reused after relocation. |
| DRC scope | DRC means design-rule and schematic-parity checks. The capped unconnected-items list is not the exact remaining-connection count. Installed standard libraries and actual assembled/measured behaviour remain separate boundaries. |

Current [H3 is `review_required`](h3-r2-acceptance.md): retained calculations are
provisional and do not qualify the installed power circuit. They do not replace
the open native electrical-semantics, power/startup, remaining routing or
assembled-mechanics gates. No prototype has been demonstrated to boot by this review.

## What is still open

| Item | Remaining work — not waived by DRC |
| --- | --- |
| Cap U214/U219 | Resolve the published mating-face/numbering ambiguity and header-to-housing registration. Logical M5 numbering must not be copied directly onto Samtec's alternating physical rows. No speculative permutation is accepted. The clarification inquiry remains pending. |
| **Keystone 1048P: geometry and power routing** | The [same-end-positive defect](../hardware/layout/h6-r2-holder-polarity-review.json) is **[corrected in native R2](../hardware/layout/h6-r2-holder-polarity-integration.json)**, with F2 moved beside the corrected contact and existing 2S/sense nets retained. Exact SMT lands, complete locator/hole registration and the new physical power routes remain open. The polarity/body-corrected library definition is still not a manufacturing-ready land pattern; no guessed drilling or battery energization is approved. |
| **Cell-to-NTC contact** | [Reopened height review](h6-r2-mechanical-stack.md): the previously assumed 3.3-mm cell floor is a retaining-post projection below the PCB. The 20% compression claim is withdrawn; actual cell height, channel fit and pad compression remain unverified. The two NTC XY positions are not proof of thermal contact. |
| Alps EC11E18244AU encoder | The [reviewed engineering footprint](h6-r2-encoder-engineering-fit.md) uses the exact nominal 12.5 mm mounting-lug pitch; the new left/down shaft placement is recorded in the repair report, not its earlier fit snapshot. Its rounded PTH profile, physical insertion, solder strength and assembled Z clearance remain open; DRC is not production-fit approval. |
| Other through-pad solder access | The exposed USB shell, Cap and encoder lands have no foreign pad/body overlap in the planar screen. Close neighbours at the encoder mounting lugs and Cap header still need an actual solder-access and assembly-order check. The 1-mm screen is an engineering aid, not a factory requirement; a marginally larger gap alone does not justify moving whole functional blocks. L32's two exposed endpoints are an unrouted NFC reserve, not leads of a fitted component. |
| SMA thickness | Reconcile the 1.75 ± 0.10 mm connector slot with finished PCB thickness; the earlier 1.60 ± 0.16 mm envelope permits 0.11 mm interference. Do not assume the prongs can be spread. |
| SMA antennas and microSD access | The wider 14.7 mm bank and nominal recessed-card geometry do not qualify actual antenna bases, assembled inter-row Z, finger/tool and screw access, cable bends, card/connector tolerances or enclosure access. The PCB notch is a project choice, not a manufacturer requirement. |
| Display/FPC/PSA | The native 27 × 1.2 mm slot and ZIF orientation exist, but the real fold, slack, rear-panel flatness, adhesive thickness and assembly tolerance still require closure. |
| Microphone/speaker | The outward MK1 and separate UI speaker body now have explicit placement targets, but quiet audio routing, real acoustic openings, speaker fixation/insulation and wire strain relief remain open. RF LS1 still represents wire termination, not the UI speaker body. |
| C5 service path | Physical USB and BOOT controls are present, but [the mux selector/enable defect](h6-r2-c5-mux-control-review.md) is open. Separately, U14.15/GPIO28 is still NC while C5_BOOT_N reaches R76/R79, so the drawn BOOT button does not establish the download strap. C5/Hub reset under KILL also needs reconciliation with the firmware update policy before functional acceptance. These are electrical work items, not missing component drawings. |
| RUN/KILL direction | Resolve the manufacturer's conflicting physical A/B caption before accepting directional markings. The electrical pairs are known; the lever direction is not silently inferred. |
| Assembled interfaces | Check exact bodies, opposite-face solder/locator protrusion, microcoax bends, inserted plugs, card/finger access and optical apertures together. Planar clearance does not close STEP or received-part checks. |

The earlier [exterior microphone-cluster candidate](../hardware/layout/h6-r2-microphone-island-review.json)
and its temporary MIC_RAW route are historical, **not the adopted audio layout**.
The new repair keeps the microphone outside and ordinary support circuitry inside.
Its placement does not qualify ground return, remote headset branches, noise or
enclosure acoustics.

The display slot is x[26.5,53.5], y[31.5,32.7], R0.6. UI J1 at [40,35.4],
B0, opens toward it. Explicit mating remains panel contact `n` → Hirose `51−n`.
The fold target still requires a neutral-axis path ≤24.66 mm to retain ≥5 mm
slack from the minimum 29.66 mm tail, folded stack ≤0.714 mm and adhesive
clearance ≥0.20 mm. Dry-fit the received display before irreversible bonding.
[Panel drawing](https://www.buydisplay.com/download/manual/ER-TFT035IPS-6_Datasheet.pdf),
[Hirose drawing](https://www.hirose.com/en/product/document?clcode=CL0580-1266-2-50&documentid=0001483059&documenttype=2DDrawing&lang=en&productname=FH34SRJ-50S-0.5SH%2850%29&series=FH34SRJ).

Both boards retain four Ø2.7 NPTH mounting holes at [5,11], [75,11], [5,145]
and [75,145]. Per-board transformed validation rejects missing, duplicate or
moved holes; this does not itself qualify screw heads or assembled body clearances.
The six internal debug headers are accessed after opening the device.

## Evidence: current state versus historical findings

Use the [current-routing audit](../hardware/layout/generated/H6-R2-current-routing-audit.json)
for the current UI/RF hashes, executed DRC commands and source-bound receipts,
and the [repair report](h6-r2-placement-repair.md) for this package's status.
This page intentionally does not duplicate a PCB hash table or treat scratch-stage
receipts as fresh MAIN evidence. Changed boards, rules, schematics or controlled
libraries require new checks; historical records retain their original status.

- Current owners: [placement contract](../hardware/layout/h6-r2-placement-contract.json), [native instance ledger](../hardware/ecad/generated/H2-R2-native-instance-ledger.json), [assembly coordinates](../hardware/product-design/assembly-coordinate-model.json), [display contract](../hardware/product-design/display-mount.json).
- Derived audits: [current routing](../hardware/layout/generated/H6-R2-current-routing-audit.json), [pad parity](../hardware/layout/generated/H6-R2-footprint-pad-parity.json), [native user labels](../hardware/layout/generated/H6-R2-user-silkscreen-audit.json). Check their recorded source hashes against current native files: a reproducible stale snapshot is not evidence for the repair.
- Component images: the [view manifest](../hardware/layout/generated/H6-R2-component-views.json) binds both PCB hashes and all five published SVG hashes: four faces plus overview; it must be refreshed with the repair. The actual card notch is shown; the ejected-card position is a dashed explanatory overlay, not silkscreen or part of the PCB outline. Native component views do not qualify assembled bodies or full H1-to-PCB parity.
- Electrical proof: [bounded analog transfer](../hardware/verification/generated/H3-R2-analog-corners.json), [NC6 removal and connected-tuple baseline](../hardware/verification/h3-r2-input-freeze-contract.json), [typed electrical review](../hardware/verification/generated/H6-R2-electrical-semantics.json).
- Open mechanics: [Cap](../hardware/layout/h6-r2-cap-mating-review.json), [holder/encoder](../hardware/layout/h6-r2-holder-encoder-geometry-evidence.json), [B3S datum](../hardware/layout/h6-r2-b3s-actuator-datum-review.json), [audio placement](../hardware/layout/h6-r2-audio-placement-proposal.json). Source-review/candidate snapshots retain their original status; source-selection tags such as `native_integration_open` describe that original selection snapshot, not the subsequent native status recorded on this page.
- Historical discovery snapshots: [mechanical review, 2026-09-07 16:21:55 UTC](../hardware/layout/h6-r2-interface-review-findings.json), [74-row inventory, 16:24:49 UTC](../hardware/layout/h6-r2-connector-review-findings.json), [interface datums](../hardware/layout/h6-r2-interface-datum-review.json), [old mid-mount audio corrections](../hardware/layout/h6-r2-audio-datum-review.json). Their old defects must not be presented as current placements, nor their old DRC as fresh acceptance.

Next: close the exact holder/encoder, Cap, SMA and assembled display/acoustic/access boundaries and
continue routing. H6.0.7 assembled-body verification and the overall H6 phase
remain open. No purchase, manufacturing release or full functional sign-off is implied.
