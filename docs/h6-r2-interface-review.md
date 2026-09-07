# H6.0.3-R1 · Interfaces, cutouts and silkscreen

[Русский](h6-r2-interface-review.ru.md)

**2026-09-08: the reviewed interface corrections below are integrated into both native boards. H6 remains open; manufacturing is not authorized.**

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

## What is now in the native boards

| Integrated slice | Exact scope and remaining boundary |
| --- | --- |
| UI IR: 11 references | D11, U23/U24 and eight local support parts have corrected footprints/poses. U23 is **TSMP95000TR**, the side-view taped version; the receiver and emitter axes point toward the left edge. This is source/planar integration, not a measured optical aperture, range or emitter-witness qualification. [Vishay TSMP95000](https://www.vishay.com/docs/82907/tsmp95000.pdf), [TSOP752](https://www.vishay.com/docs/82494/tsop752.pdf), [VSMY14940](https://www.vishay.com/docs/84209/vsmy14940.pdf). |
| UI B3S: 15 buttons | SW3–SW17 use the actual actuator datum, not the courtyard centre. The former **0.75 mm** offset is accounted for; the F-key columns are mirrored physically, and the seven lower buttons retain the intended actuator positions. Labels follow the actual axes. Pads, electrical numbering and MPN remain unchanged. [OMRON B3S, p2](https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3s.pdf). |
| RF bottom ports: 16 references | J1/J4/J11 and 13 local support parts are integrated. JAE J1 is B180 at **[16.47,146.90]**, GCT J4 B180 at **[37.47,146.325]**, Grove J11 B180 at **[57.0,144.3]**. The ports face the bottom edge with corrected body/PCB-edge datums. JAE EdgeSilk changes only silk, not lands. Closed-stack plug/overmould access remains open. [GCT](https://gct.co/files/drawings/usb4105.pdf), [JAE-authored SJ121836](https://www.mikrocontroller.net/attachment/650878/SJ121836.pdf), [Seeed Grove](https://statics3.seeedstudio.com/fusion/opl/datasheet/320110032.pdf). |
| RF service / RUN-KILL: 3 references | SW2 reset B90 **[1.825,108.25]** and SW1 boot B90 **[1.825,115.25]** now face the native left edge. SW5 is the side-actuated **JS102011SAQN**, B270 **[78.2,114.1]**, facing right. Common2 and throws1/3 retain their fail-safe nets. The manufacturer's conflicting A/B direction caption remains gated: **no directional RUN/KILL silk is accepted**. [C&K JS, p4](https://www.littelfuse.com/assetdocs/littelfuse-c-k-slide-js-series-datasheet?assetguid=aba42b08-0d2c-423b-813d-a2faa5a3bb14). |
| RF PTT: 1 reference | SW4 uses the corrected B3S actuator datum and accepted rear-side position; existing copper remains intact. This is not an enclosure/button-force qualification. |
| RF audio: 4 references | U83 is **SJ-43515TS-SMT-TR**, F0 **[0.8,99.0]**, with C144/C199/U116 locally repositioned; U116 is **[10.5,110.0]**, F90. This ordinary-SMT jack needs locator holes but **no under-body PCB cutout**. The old SJ-43504 cutout errors are historical findings, not a current blocker. Plug access and retention remain open. [Same Sky exact TS model, p2](https://www.sameskydevices.com/product/resource/digikeypdf/sj-4351x-smt.pdf). |

The RF slices total **24 references**: 16 + 3 + 1 + 4. Earlier corrections to
UI USB/microSD, ten exterior indicators and M1 remain in place. microSD UI J5
is B180 at [61.005,141.875]; its access envelope includes 4.0 mm ejection travel
and a separate 0.8 mm push stroke, not merely the socket courtyard.

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
| Copper preservation | All **787 existing copper objects — 622 segments and 165 vias — are preserved**: UI 21, RF 766. This does not mean moved, previously unrouted pins are now connected. |
| Final staged DRC | Both final staged checks reported **0 violations and 0 schematic-parity findings**. Each still returned **499 unconnected items**, at the report cap; this is neither an exact remaining-airwire count nor completed routing. |
| Production provenance | Fresh production schema2 receipts for the two hashes below also report **0 violations / 0 schematic-parity findings**. They explicitly request `--schematic-parity` and bind PCB/pro/dru, root/child SCH, library tables and repository-controlled libraries. The actual command uses repository-relative board/report paths under the recorded repository-root working directory; copying identical files does not rewrite its evidence. Standard installed libraries remain an explicit environment boundary. A different PCB or changed hashed source invalidates the receipt. |
| Native/library pad parity | **1216/1216 footprints checked, zero pad-geometry drift.** Agreement with the selected library does not qualify that library's unresolved holder/encoder geometry. |
| Safe native integration | The staging guard rejects duplicate raw UUIDs, unexpected pad removals, changed unlisted footprints and changed copper. Changed-footprint UUIDs are regenerated collision-free; schematic paths and untouched objects are preserved. |
| Electrical boundary | Only the unused old U83 terminal6 was removed: **4066 connected logical endpoint tuples remain identical**, with 4070 connected physical pins and 235 NC pins. H3 permits only a bounded electrical transfer for TR and the five-contact audio jack, not optical/mechanical or whole-board approval. |
| Silkscreen | All **63 required labels** match their native bindings, including anchor/angle/side/footprint identity and actuator axis. Both boards now have **zero unresolved geometry candidates**, status `pass_scoped`. The five UI findings were resolved explicitly: four clear the exact B3S body with its dimensional tolerance, and HUB RP's actual strokes clear pad SW8.5's mask by **0.239819–0.239820 mm**, above the 0.15 mm screening requirement. These are geometry proofs, not blanket waivers. RF antenna labels bind to signal nets, not list order; DISPLAY/PSA use corner marks. Closed-device readability remains outside this audit. |

The current H3 checks pass within their model boundaries. They do not replace
the open native electrical-semantics, power/startup, remaining routing or
assembled-mechanics gates. No prototype has been demonstrated to boot by this review.

## What is still open

| Item | Remaining work — not waived by DRC |
| --- | --- |
| Cap U214/U219 | Resolve the published mating-face/numbering ambiguity and header-to-housing registration. Logical M5 numbering must not be copied directly onto Samtec's alternating physical rows. No speculative permutation is accepted. The clarification inquiry remains pending. |
| **Keystone 1048P: polarity and geometry** | **[Critical open correction](../hardware/layout/h6-r2-holder-polarity-review.json):** the manufacturer's two cells face opposite directions; the current footprint maps both positive contacts to the same local end. The SLOT1 polarity/physical-land registration and affected power paths must be verified together before cells may be connected. Exact SMT lands and complete locator/hole registration also remain open; no guessed drilling or battery energization is approved. |
| Alps EC11E18244AU encoder | The exact 12.5 mm mounting-lug pitch differs from the bound generic 11.2 mm footprint. A separate dimension/slot-process candidate is not an accepted production footprint or proof of solder-joint strength. |
| SMA thickness | Reconcile the 1.75 ± 0.10 mm connector slot with finished PCB thickness; the earlier 1.60 ± 0.16 mm envelope permits 0.11 mm interference. Do not assume the prongs can be spread. |
| Display/FPC/PSA | The native 27 × 1.2 mm slot and ZIF orientation exist, but the real fold, slack, rear-panel flatness, adhesive thickness and assembly tolerance still require closure. |
| Microphone/speaker | RF MK1's acoustic path, the real speaker body/mount and lead strain relief remain open. A bounded microphone-cluster candidate exists below but is **not adopted**. LS1 represents wire termination, not the speaker body. |
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

This report's integrated PCB snapshot is:

| Board | SHA-256 |
| --- | --- |
| [UI native PCB](../hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb) | `82e0b4ae6cbbad5241984a476c057ea7ecf2d593b382bcc06feceb26a73cbfe1` |
| [RF native PCB](../hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb) | `cd306f5f39649fd0c24c0a1f79931716f646e9c72959788a9127098d44eca1fe` |

- Current owners: [placement contract](../hardware/layout/h6-r2-placement-contract.json), [native instance ledger](../hardware/ecad/generated/H2-R2-native-instance-ledger.json), [assembly coordinates](../hardware/product-design/assembly-coordinate-model.json), [display contract](../hardware/product-design/display-mount.json).
- Derived audits: [current routing](../hardware/layout/generated/H6-R2-current-routing-audit.json), [pad parity](../hardware/layout/generated/H6-R2-footprint-pad-parity.json), [native user labels](../hardware/layout/generated/H6-R2-user-silkscreen-audit.json). Check their recorded source hashes: a reproducible stale snapshot is not evidence for the two hashes above. Fresh production DRC receipts and the scoped silk audit have been verified against both final hashes.
- Current component images: the [view manifest](../hardware/layout/generated/H6-R2-component-views.json) matches both final PCB hashes and all five published SVG hashes: four faces plus overview. These are native component views, not an assembled-body or H1-to-PCB parity approval.
- Electrical proof: [bounded analog transfer](../hardware/verification/generated/H3-R2-analog-corners.json), [NC6 removal and connected-tuple baseline](../hardware/verification/h3-r2-input-freeze-contract.json), [typed electrical review](../hardware/verification/generated/H6-R2-electrical-semantics.json).
- Open mechanics: [Cap](../hardware/layout/h6-r2-cap-mating-review.json), [holder/encoder](../hardware/layout/h6-r2-holder-encoder-geometry-evidence.json), [B3S datum](../hardware/layout/h6-r2-b3s-actuator-datum-review.json), [audio placement](../hardware/layout/h6-r2-audio-placement-proposal.json). Source-review/candidate snapshots retain their original status; source-selection tags such as `native_integration_open` describe that original selection snapshot, not the subsequent native status recorded on this page.
- Historical discovery snapshots: [mechanical review, 2026-09-07 16:21:55 UTC](../hardware/layout/h6-r2-interface-review-findings.json), [74-row inventory, 16:24:49 UTC](../hardware/layout/h6-r2-connector-review-findings.json), [interface datums](../hardware/layout/h6-r2-interface-datum-review.json), [old mid-mount audio corrections](../hardware/layout/h6-r2-audio-datum-review.json). Their old defects must not be presented as current placements, nor their old DRC as fresh acceptance.

Next: close the exact holder/encoder, Cap, SMA and assembled display/acoustic/access boundaries and
continue routing. H6.0.7 assembled-body verification and the overall H6 phase
remain open. No purchase, manufacturing release or full functional sign-off is implied.
