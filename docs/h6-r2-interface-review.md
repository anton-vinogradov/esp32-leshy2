# H6.0.3-R1 · Interfaces, cutouts and silkscreen

[Русский](h6-r2-interface-review.ru.md)

**2026-09-08: MAIN includes 24 local solder-access relocations around SMA, following the SMA/microSD spacing correction, engineering EC11 footprint, nine LED-anode routes and native C5 pair protection. Fresh DRC on both native boards reports 0 violations / 0 schematic-parity findings. H6 remains open; manufacturing is not authorized.**

The UI IR cluster and 15 front buttons, and the RF bottom ports, service switches,
PTT and ordinary-SMT headset jack now use the corrected native geometry. This
closes those specific placement defects, not all mechanical or electrical work.
H1 remains a concept drawing, not a complete parity view of the current PCB.
Planar fit and a clean DRC do not prove assembled STEP clearance or prototype boot.

## What we want and what was checked

Ports and controls must be accessible with the boards assembled. M1 must mate
without force; the display tail must exit upward without twisting, with slack
and a clear adhesive landing. Holes, footprints and labels must describe the
actual parts, not merely reproduce the mockup.

The initial inventory enumerated **31 J-designated connectors plus 43 other
interfaces: 74 records** on two 80 × 150 mm boards. This is an inventory, not
74 completed functional or dimensional verifications. The headset is **RF U83**;
the remaining records include buttons, BT1, encoder, indicators, IR and acoustics.

The repeated current-native check finds **74/74 present exactly once**, on the
side and at the pose recorded by the current placement audit. The component
views also cover the complete **1208-position instance ledger**, including the
processors, radios and power/safety parts, plus eight mounting footprints.
New regressions guard both scopes. The old H1 picture is not used as a placement
authority. [Four-face views](h6-r2-component-views.md) now expose the reverse-side
USB, Cap and encoder copper lands as well as SMA lands; drilled holes alone
were an incomplete depiction. Display, cells, loose coax and speaker bodies
still require their separate assembly representations and clearance checks.

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
| RF USB J1 | Its **0.5 mm shell protrusion** beyond the ordinary bottom edge is intentional and unchanged. The SMA/card correction does not move J1 or establish plug-overmould clearance. |

The larger SMA pitch improves the available connector spacing, but real antenna
bases, the assembled inter-row Z separation, screw-head access, two-sided solder
prongs and microcoax bends must still be checked together. Local U.FL/support
repositioning is part of this correction; it does not qualify assembled cable fit.
The separate **1.75 ± 0.10 mm slot versus 1.60 ± 0.16 mm PCB** issue remains
open: this envelope still permits **0.11 mm interference**.

## What is now in the native boards

The latest SMA relief moves **10 UI positions and 14 RF positions**, not the
SMA connectors themselves. UI J4 stays B0 at [19.04,3.48], J13 moves to
[3.65,3.875], and S3 shifts 0.5 mm left with local support adjustments. Its cable
retains the existing R7 forming allowance, positive R3 inspection clearance
and **5.223 mm** nominal calculated reserve. RF neighbours are moved as a
local group, including the four parts with existing routed connections.
[All 50 SMA lands](h6-r2-component-views.md#sma-solder-site-checks) now have
**zero candidates** in the unchanged 1-mm per-axis screen, down from nine
flagged lands. This does not qualify the soldering process or 3D tool approach.

The RF S3 LC route grows from 1.95 to 3.92 mm; C126 to U33 VCC14 has a
4.02-mm direct pad span instead of 3.77 mm. These remain explicit RF/local
power-layout review items, not a claim that clearance alone preserves measured
RF response. The footprint/net inventory and board envelope are unchanged.

| Integrated slice | Exact scope and remaining boundary |
| --- | --- |
| UI IR: 11 references | D11, U23/U24 and eight local support parts have corrected footprints/poses. U23 is **TSMP95000TR**, the side-view taped version; the receiver and emitter axes point toward the left edge. This is source/planar integration, not a measured optical aperture, range or emitter-witness qualification. [Vishay TSMP95000](https://www.vishay.com/docs/82907/tsmp95000.pdf), [TSOP752](https://www.vishay.com/docs/82494/tsop752.pdf), [VSMY14940](https://www.vishay.com/docs/84209/vsmy14940.pdf). |
| UI B3S: 15 buttons | SW3–SW17 use the actual actuator datum, not the courtyard centre. The former **0.75 mm** offset is accounted for; the F-key columns are mirrored physically, and the seven lower buttons retain the intended actuator positions. Labels follow the actual axes. Pads, electrical numbering and MPN remain unchanged. [OMRON B3S, p2](https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3s.pdf). |
| RF bottom ports: 16 references | J1/J4/J11 and 13 local support parts are integrated. JAE J1 is B180 at **[16.47,146.90]**, GCT J4 B180 at **[37.47,146.325]**, Grove J11 B180 at **[57.0,144.3]**. The ports face the bottom edge with corrected body/PCB-edge datums. JAE EdgeSilk changes only silk, not lands. Closed-stack plug/overmould access remains open. [GCT](https://gct.co/files/drawings/usb4105.pdf), [JAE-authored SJ121836](https://www.mikrocontroller.net/attachment/650878/SJ121836.pdf), [Seeed Grove](https://statics3.seeedstudio.com/fusion/opl/datasheet/320110032.pdf). |
| RF service / RUN-KILL: 3 references | SW2 reset B90 **[1.825,108.25]** and SW1 boot B90 **[1.825,115.25]** now face the native left edge. SW5 is the side-actuated **JS102011SAQN**, B270 **[78.2,114.1]**, facing right. Common2 and throws1/3 retain their fail-safe nets. The manufacturer's conflicting A/B direction caption remains gated: **no directional RUN/KILL silk is accepted**. [C&K JS, p4](https://www.littelfuse.com/assetdocs/littelfuse-c-k-slide-js-series-datasheet?assetguid=aba42b08-0d2c-423b-813d-a2faa5a3bb14). |
| RF PTT: 1 reference | SW4 uses the corrected B3S actuator datum and accepted rear-side position; existing copper remains intact. This is not an enclosure/button-force qualification. |
| RF audio: 4 references | U83 is **SJ-43515TS-SMT-TR**, F0 **[0.8,99.0]**, with C144/C199/U116 locally repositioned; U116 is **[10.5,110.0]**, F90. This ordinary-SMT jack needs locator holes but **no under-body PCB cutout**. The old SJ-43504 cutout errors are historical findings, not a current blocker. Plug access and retention remain open. [Same Sky exact TS model, p2](https://www.sameskydevices.com/product/resource/digikeypdf/sj-4351x-smt.pdf). |

The earlier RF slices total **24 references**: 16 + 3 + 1 + 4. Their integration,
the ten exterior indicators and M1 remain in place. The new SMA/microSD slice
above is the subsequent change; its card-access envelope is not merely the socket
courtyard.

The subsequent [holder-polarity correction](../hardware/layout/h6-r2-holder-polarity-integration.json)
updates another **four RF references: BT1, F2, U91 and C241**. Cell1 positive
contact BT1.3 is now at [52.54,44]; its local fuse F2 follows to B0 [56.5,47.75].
U91 and its bypass C241 move together to clear that position. All 766 RF copper
objects and complete existing pad/track adjacency remain unchanged. This corrects
the polarity contradiction, not the unresolved holder land/hole pattern or thermal
contact. The new positive/fuse and buffer connections still require routing.

The final refinement moves only the four USB owner labels — UI HUB RP/C5 and
RF S3/RF RP — from y138.0 to **y138.2**; their function labels remain at y140.0.
Footprints, pads and copper are unchanged. This gives the UI HUB RP ink a
verified mask clearance rather than relying on a loose text bounding box.

M1 retains UI J18 B0 [42.5,122.25] and RF J12 B180 [37.5,122.25]. All 80
contact assignments, polarization/planar registration and nominal 11 mm mating
height are guarded. Generic body models do not close exact assembled Z.
[Hirose plug](https://www.hirose.com/product/p/CL0578-0523-1-92),
[receptacle](https://www.hirose.com/en/product/p/CL0578-0823-5-92).

## What the checks establish

| Check | Result and limit |
| --- | --- |
| Copper preservation | SMA relief changes only **four reviewed routes / 11 segments**: the UI C2↔U52 segment and three RF nets. The other **846 copper objects are byte-identical**: UI91 + RF755. Existing connected-pad relationships are preserved, and the RF AM/LW route has no new redundant branch. Total remains **857 objects: 682 segments and 175 vias** (UI92 + RF765). Nine LED-anode nets remain routed; FAULT is excluded. This is not completed interface routing. [Earlier LED review](../hardware/layout/h6-r2-led-routing-review.json). |
| Fresh native DRC | Both current boards, including the combined SMA relief, report **0 violations and 0 schematic-parity findings** for the hashes below. Each returns **499 unconnected items**, at the report cap; this is neither an exact remaining-airwire count nor completed routing. |
| Production provenance | Fresh schema2 receipts explicitly request `--schematic-parity` and bind PCB/pro/dru, root/child SCH, library tables and repository-controlled libraries. The actual command uses repository-relative board/report paths under the recorded repository-root working directory; copying identical files does not rewrite its evidence. Standard installed libraries remain an explicit environment boundary. A different PCB or changed hashed source invalidates the receipt. |
| Native/library pad parity | The refreshed audit checks **1216/1216 footprints with zero pad-geometry drift**, bound to both promoted hashes. Agreement with the selected library does not qualify its unresolved holder/encoder geometry. |
| Safe native integration | The staging guard rejects duplicate raw UUIDs, unexpected pad removals, changed unlisted footprints and changed copper. Changed-footprint UUIDs are regenerated collision-free; schematic paths and untouched objects are preserved. |
| Electrical boundary | The earlier U83 correction removed only its unused old terminal6: **4066 connected logical endpoint tuples remain identical**, with 4070 connected physical pins and 235 NC pins. The encoder maps old `S1→E`, `S2→D` while retaining all five world pad/net pairs. H3 permits only a bounded electrical transfer for TR and the five-contact audio jack, not optical/mechanical or whole-board approval. |
| Silkscreen | The refreshed audit binds **65 required labels: UI48 + RF17**, with zero unresolved geometry candidates and status `pass_scoped`. Five UI findings are resolved explicitly: four clear the exact B3S body with its dimensional tolerance, and HUB RP's actual strokes clear pad SW8.5's mask by **0.239819–0.239820 mm**, above the 0.15 mm screening requirement. Antenna labels follow their connectors; RF labels bind to signal nets, not list order. DISPLAY/PSA use corner marks. These are geometry proofs, not blanket waivers or closed-device readability qualification. |

Current [H3 is `review_required`](h3-r2-acceptance.md): retained calculations are
provisional and do not qualify the installed power circuit. They do not replace
the open native electrical-semantics, power/startup, remaining routing or
assembled-mechanics gates. No prototype has been demonstrated to boot by this review.

## What is still open

| Item | Remaining work — not waived by DRC |
| --- | --- |
| Cap U214/U219 | Resolve the published mating-face/numbering ambiguity and header-to-housing registration. Logical M5 numbering must not be copied directly onto Samtec's alternating physical rows. No speculative permutation is accepted. The clarification inquiry remains pending. |
| **Keystone 1048P: geometry and power routing** | The [same-end-positive defect](../hardware/layout/h6-r2-holder-polarity-review.json) is **[corrected in native R2](../hardware/layout/h6-r2-holder-polarity-integration.json)**, with F2 moved beside the corrected contact and existing 2S/sense nets retained. Exact SMT lands, complete locator/hole registration and the new physical power routes remain open. The polarity-only library definition is explicitly not a manufacturing-ready land pattern; no guessed drilling or battery energization is approved. |
| **Cell-to-NTC contact** | [Reopened height review](h6-r2-mechanical-stack.md): the previously assumed 3.3-mm cell floor is a retaining-post projection below the PCB. The 20% compression claim is withdrawn; actual cell height, channel fit and pad compression remain unverified. The two NTC XY positions are not proof of thermal contact. |
| Alps EC11E18244AU encoder | The [reviewed engineering footprint](h6-r2-encoder-engineering-fit.md) now uses the exact nominal 12.5 mm mounting-lug pitch and unchanged native shaft axis. Its rounded PTH profile, physical insertion, solder strength and assembled Z clearance remain open; DRC is not production-fit approval. |
| Other through-pad solder access | The exposed USB shell, Cap and encoder lands have no foreign pad/body overlap in the planar screen. Close neighbours at the encoder mounting lugs and Cap header still need an actual solder-access and assembly-order check. The 1-mm screen is an engineering aid, not a factory requirement; a marginally larger gap alone does not justify moving whole functional blocks. L32's two exposed endpoints are an unrouted NFC reserve, not leads of a fitted component. |
| SMA thickness | Reconcile the 1.75 ± 0.10 mm connector slot with finished PCB thickness; the earlier 1.60 ± 0.16 mm envelope permits 0.11 mm interference. Do not assume the prongs can be spread. |
| SMA antennas and microSD access | The wider 14.7 mm bank and nominal recessed-card geometry do not qualify actual antenna bases, assembled inter-row Z, finger/tool and screw access, cable bends, card/connector tolerances or enclosure access. The PCB notch is a project choice, not a manufacturer requirement. |
| Display/FPC/PSA | The native 27 × 1.2 mm slot and ZIF orientation exist, but the real fold, slack, rear-panel flatness, adhesive thickness and assembly tolerance still require closure. |
| Microphone/speaker | RF MK1's acoustic path, the real speaker body/mount and lead strain relief remain open. A bounded microphone-cluster candidate exists below but is **not adopted**. LS1 represents wire termination, not the speaker body. |
| C5 service path | Physical USB and BOOT controls are present, but [the mux selector/enable defect](h6-r2-c5-mux-control-review.md) is open. Separately, U14.15/GPIO28 is still NC while C5_BOOT_N reaches R76/R79, so the drawn BOOT button does not establish the download strap. C5/Hub reset under KILL also needs reconciliation with the firmware update policy before functional acceptance. These are electrical work items, not missing component drawings. |
| RUN/KILL direction | Resolve the manufacturer's conflicting physical A/B caption before accepting directional markings. The electrical pairs are known; the lever direction is not silently inferred. |
| Assembled interfaces | Check exact bodies, opposite-face solder/locator protrusion, microcoax bends, inserted plugs, card/finger access and optical apertures together. Planar clearance does not close STEP or received-part checks. |

The [microphone-cluster candidate](../hardware/layout/h6-r2-microphone-island-review.json)
places **10 support parts plus MK1** on the RF exterior, without changing MPNs
or topology. Its isolated fit preserves the 766 baseline copper objects; a
separate six-segment, via-free MIC_RAW witness reaches U85 in **14.527 mm**.
That is a scratch route, not production copper or full audio qualification.
The 10 mm direct-pad locality target is an engineering target, not a manufacturer
limit or the routed length. Ground return, remote headset branches, noise,
enclosure acoustics and adoption of the candidate remain separate work.

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

The current combined SMA-relief PCB hashes below match fresh DRC receipts.
They identify the checked native boards, not manufacturing approval:

| Board | SHA-256 |
| --- | --- |
| [UI native PCB](../hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb) | `3c0071b28c2c2dec2a4d95fa0047a83d30bd9302a0e5083ea90cc5a0efe99aad` |
| [RF native PCB](../hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb) | `cb5855cf3d9c534bfdbd5190a86f54f4d800b8c594c717257463fd81033f4e9f` |

The fresh MAIN DRC records are `work/sma-relief-joint/ui-drc.json`
and `work/sma-relief-joint/rf-drc.json`, with their provenance sidecars.
The current-routing audit binds the executed command and exact repository inputs;
changed boards, rules, schematics or controlled libraries require a new DRC run.
Earlier stage records retain their original status; the later hash-bound DRC
receipts establish the scoped result, not manufacturing approval.

- Current owners: [placement contract](../hardware/layout/h6-r2-placement-contract.json), [native instance ledger](../hardware/ecad/generated/H2-R2-native-instance-ledger.json), [assembly coordinates](../hardware/product-design/assembly-coordinate-model.json), [display contract](../hardware/product-design/display-mount.json).
- Derived audits: [current routing](../hardware/layout/generated/H6-R2-current-routing-audit.json), [pad parity](../hardware/layout/generated/H6-R2-footprint-pad-parity.json), [native user labels](../hardware/layout/generated/H6-R2-user-silkscreen-audit.json). Check their recorded source hashes: a reproducible stale snapshot is not evidence for the two hashes above. The pad-parity and scoped label audits have been rebound to both promoted boards.
- Component images: the refreshed [view manifest](../hardware/layout/generated/H6-R2-component-views.json) matches both promoted PCB hashes and all five published SVG hashes: four faces plus overview. The actual card notch is shown; the ejected-card position is a dashed explanatory overlay, not silkscreen or part of the PCB outline. Native component views do not qualify assembled bodies or full H1-to-PCB parity.
- Electrical proof: [bounded analog transfer](../hardware/verification/generated/H3-R2-analog-corners.json), [NC6 removal and connected-tuple baseline](../hardware/verification/h3-r2-input-freeze-contract.json), [typed electrical review](../hardware/verification/generated/H6-R2-electrical-semantics.json).
- Open mechanics: [Cap](../hardware/layout/h6-r2-cap-mating-review.json), [holder/encoder](../hardware/layout/h6-r2-holder-encoder-geometry-evidence.json), [B3S datum](../hardware/layout/h6-r2-b3s-actuator-datum-review.json), [audio placement](../hardware/layout/h6-r2-audio-placement-proposal.json). Source-review/candidate snapshots retain their original status; source-selection tags such as `native_integration_open` describe that original selection snapshot, not the subsequent native status recorded on this page.
- Historical discovery snapshots: [mechanical review, 2026-09-07 16:21:55 UTC](../hardware/layout/h6-r2-interface-review-findings.json), [74-row inventory, 16:24:49 UTC](../hardware/layout/h6-r2-connector-review-findings.json), [interface datums](../hardware/layout/h6-r2-interface-datum-review.json), [old mid-mount audio corrections](../hardware/layout/h6-r2-audio-datum-review.json). Their old defects must not be presented as current placements, nor their old DRC as fresh acceptance.

Next: close the exact holder/encoder, Cap, SMA and assembled display/acoustic/access boundaries and
continue routing. H6.0.7 assembled-body verification and the overall H6 phase
remain open. No purchase, manufacturing release or full functional sign-off is implied.
