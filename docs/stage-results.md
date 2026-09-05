# Leshy2 hardware stage results

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](stage-results.ru.md)

This page shows the present result of every top-level hardware stage. A stage
receives **reviewed** only after its own exit criteria pass. Work inherited from
the earlier R1 baseline is reference evidence, not acceptance of the new R2
device.

<a id="h0"></a>
## H0 · Requirements and functional architecture

**Status:** ✅ reviewed.

- [Current hardware architecture](hardware.md)
- [Functional two-PCB diagram](images/h0-r2-functional-architecture.svg)
- [Machine architecture model](../hardware/architecture/h0-r2-rebaseline.json)

Result: the product is split into a front UI/radio PCB and a rear RF/power PCB.
UI remains local to S3, all three complete nRF24 paths remain local to the front
RP, and CC1101, voice, broadcast/Airband, audio, extensions and safety remain
local to the rear RP. M1 carries control/data transport, safety evidence and
power—not primary RF payloads.

<a id="h1"></a>
## H1 · Physical product design

**Status:** ✅ reviewed at **`H1-R2.39`**; the 80-mm geometry rebaseline passed on 2026-09-05.

- [Reviewed H1 phase result](h1-r2-acceptance.md)
- [Current physical design](h1-r2-physical-layout.md)
- [Outer faces](images/h1-r2-external-layout.svg?rev=h1-r2.39-80mm-1)
- [Front inner face](images/h1-r2-inner-ui.svg)
- [Rear inner face](images/h1-r2-inner-rf.svg)
- [Display PSA, relaxed FPC route and direct ZIF](images/display-mount.svg?rev=h1-r2.39-80mm-1)
- [True sandwich sections](images/h1-r2-inner-sections.svg?rev=h1-r2.39-80mm-1)
- [External service access](images/h1-r2-service-access.svg?rev=h1-r2.39-80mm-1)
- [Machine placement audit](../hardware/product-design/generated/H1-R2-placement-audit.json)
- [Airband receive path](h1-airband-filter.md)
- [Power and thermal architecture](h1-r2-power-thermal.md)
- [U214/U219 machine policy](../hardware/architecture/generated/H1-R2-U219-cap-policy.json)

The exact dual-RP GPIO/M1 map and the C5 SDIO/service-mux electrical join are
closed as current H1 authority. The accepted U219 profile shares the protected
Cap slot with U214, keeps CC1101 RX-only and NFC poll/read-only, and adds
independent NFC-field evidence to the existing safety aggregate.

Current physical result: ten main SMA ports are split 5+5. The screen is exact
EastRising `ER-TFT035IPS-6 + ER-TPC035-6` option 5344 through exact Hirose
`FH34SRJ-50S-0.5SH(50)` (`C3169104`) and a replaceable i8080-8 adapter. The panel
is turned so the FPC exits toward the antenna edge; firmware rotates display and
touch coordinates by 180 degrees.

The single coordinate model now registers 226 bodies: all component packages,
all 18 U219 host bodies, the NFC pickup loop, the external antenna swept volume,
connectors, controls, through-board mechanics, all eight TX detectors and all
five required couplers. Eight bounded local evidence islands keep every active
TX path physically complete; the six AD8314 positions use the accepted
`AD8314ARMZ-REEL` / `C652687` route. Its generated four-face,
external, internal, antenna-edge and sandwich views report zero same-face
collisions and 2.59 mm minimum opposing-face clearance against the 0.70 mm rule.
The onboard video receiver, decoder, connector, antenna and physical bay are
removed. Six S3 GPIOs, five rear-RP GPIOs and nine M1 contacts remain
reserves; no hidden active module requires owner soldering after PCBA.

H1 has no physical blocker. The complete mock-up was explicitly accepted on
2026-08-30. This review does not authorize KiCad or ordering.

<a id="h2"></a>
## H2 · Production schematic

**Status:** ✅ reviewed at **`H2-R2.1.5`** on 2026-08-31.

The former G2F/H2/KiCad result is historical single-RP R1 evidence. All three
new R2 electrical prerequisites, the native source/sheet/component inventory,
the exact symbol/contact/footprint ledger and the 4,306-pin native project
reconciliation are reviewed. Two native KiCad projects now pass zero-finding
ERC; cross-sheet and HW↔FW reconciliation passes. At H2 closure,
placement/routing had not started; the current H6 status is recorded below.

Exact current checklist:

1. ✅ `H2-R2.0.1`: exact onsemi `FSUSB42MUX` / JLCPCB `C11355` live
   Standard-PCBA route reviewed: stock 66,698; available 66,045; MOQ 1;
   USD 0.3179 at quantity 1;
2. ✅ `H2-R2.0.2`: exact `DMN2056U-7` / `C332302` detector,
   `SN74LVC1G74DCUR` / `C70285` ownership latch and `74HC20PW,118` / `C546719`
   release qualifier reviewed with complete Standard-PCBA routes and fail-closed truth table;
3. ✅ `H2-R2.0.3`: exact TI `TCA9803DGKR` / `C2687966` Pack/Safety boundary
   reviewed with rail-local termination, four Basic decouplers and USD 0.3953 cost;
4. ✅ `H2-R2.1.1`: 2 projects, 22 sheets, 6 domain owners and 251 exact
   component groups reviewed;
5. ✅ `H2-R2.1.2`: 245 board groups, six explicit non-PCBA groups and 1,617
   logical contacts mapped with zero unresolved groups;
6. ✅ `H2-R2.1.3` definitions/instances: 245 controlled symbols, 1,571 symbol
   pins and all 1,208 fitted instances pass the current two-project allocation;
7. ✅ `H2-R2.1.3` nets: 4,302 fitted-instance contacts resolve to 789 global
   canonical / 823 board-local nets or 238 explicit board no-connects with zero unresolved endpoints;
8. ✅ `H2-R2.1.3`: two native KiCad projects materialize 4,306 physical pins
   and pass ERC with zero errors and zero warnings;
9. ✅ `H2-R2.1.4`: six domains, 173 controller pins, 34 cross-project nets and
   228 cross-sheet nets reconcile with zero unresolved boundary;
10. ✅ `H2-R2.1.5`: the bilingual result report is published and the synchronized
    firmware H2 gate is open.

[Reviewed H2 result](h2-acceptance.md) ·
[Native R2 inventory](h2-r2-native-inventory.md) ·
[exact symbols/footprints](h2-r2-symbol-footprint-ledger.md) ·
[native instance allocation](h2-r2-instance-ledger.md) ·
[native net reconciliation](h2-r2-net-ledger.md) ·
[native KiCad result](h2-r2-native-kicad.md).

Expected result: native KiCad schematics regenerated from the R2 architecture,
with pin reconciliation, ERC, NC review and a synchronized HW↔FW contract.
The [schematics page](schematics.md) keeps the principle diagrams visible and
clearly labels retained R1 ECAD as non-current evidence.

<a id="h3"></a>
## H3 · Virtual electrical verification

**Status:** ✅ reviewed at **`H3-R2.7`**. [Bilingual phase result](h3-r2-acceptance.md) · [physical evidence register](physical-evidence-register-r2.md).

[`H3-R2.0.1`](h3-r2-input-freeze.md) reviewed the hash-bound H2 input and complete R2
verification matrix. [`H3-R2.0.2`](parameter-model-register.md) reviewed exact
parameter/model provenance for 251 groups and 1,208 fitted positions. Current
methods are frozen by [`H3-R2.0.3`](verification-methods.md): nine methods and
twelve pass/fail rules cover all 251 groups. [`H3-R2.1.1`](power-state-register.md)
reviews all 2,266 legal source, charge, fault and operating states.
[`H3-R2.1.2`](power-load-binding.md) reviews explicit binding for 623 fitted powered
power-connected instances and six external loads. [`H3-R2.1.3`](power-rail-margins.md)
reviews 224 passing profiles across all four rails, with 30.560% minimum current
reserve and 24.706 °C minimum junction-temperature reserve. [`H3-R2.1.4`](power-source-margins.md)
reviews all 75 source/pack lines and 2,266 legal states: maximum pack current is
3.516 A, sustained admission is 1.549 A, and charging yields before system load.
The [H3-R2.1 cross-check](power-dc-source-result.md) reconciles all 617 fitted/external loads,
224 rail profiles and 2,266 states through 15 passing checks, so H3-R2.1 is
reviewed. [`H3-R2.2.1`](power-transition-sequences.md) reviews all 14 ordered
startup, shutdown, reset and recovery scenarios without automatic restart;
S3 retains the fault UI while C5/RF RP reset directly. [`H3-R2.2.2`](power-handover.md)
reviews all 7,316 USB/pack/DPM/brownout/source-loss cases with zero unsafe
admission or automatic restart. [`H3-R2.2.3/.4`](power-transition-result.md)
reviews five protected-rail starts, four load-step envelopes and ten
watchdog/fault-display cases with zero analytical failures or automatic restart.
[`H3-R2.3`](analog-electrical-verification.md) reviews all calculable display,
audio, IR, battery and Airband analog corners. [`H3-R2.4`](digital-electrical-verification.md)
reviews logic levels, timing, schematic loading, USB/service ownership, M1 and
the direct exact-20-MHz i8080-8 path. [`H3-R2.5`](rf-electrical-verification.md)
reviews 71 RF feed, topology, cable-slack, quiet-state and three-nRF24 concurrency
checks. [`H3-R2.6`](thermal-fault-electrical-verification.md) reviews all 56 thermal
profiles, 30 single-fault cases and the local-only extended-operation policy through
25 passing checks. [`H3-R2.7`](h3-r2-acceptance.md) cross-checks 20 current
evidence artifacts and all recorded source hashes with zero mismatch or open
analytical finding. Its 51-row [physical register](physical-evidence-register-r2.md)
keeps every non-paper result explicitly open and owned by H5/H6/H8.

<a id="h4"></a>
## H4 · Joined pre-layout gate

**Status:** ✅ reviewed at **`H4-R2.3`**. [`H4-R2.0.1`](h4-r2-input-freeze.md)
froze 24 exact inputs. The preserved [`H4-R2.0.2/H4-R2.1`](h4-r2-contract-reconciliation.md)
diagnostic found one owned 38-row firmware BSP-generation gap across C5, Pack
and Safety. [`H4-R2.2`](h4-r2-correction-closure.md) restored 173/173 rows and
requalified all 12 target builds. The [global bilingual H4 result](h4-r2-acceptance.md)
closes with zero contradiction and transfers all 51 physical residuals.

<a id="h5"></a>
## H5 · Component and factory evidence

**Status:** ✅ current R2 routes reviewed at **`H5-R2.1`**.

The [current bilingual H5-R2 result](h5-r2-current-route.md) revalidates all 249
purchasable groups / 1,216 articles with zero unmapped route. It preserves the
[historical H5-R1 evidence](h5-r1-acceptance.md), owner final assembly and exact
`Ettinger 007.02.611` 11-mm pass-through stops. One order-time gate remains:
zero-stock `WBC16-1TLC` must use an explicitly confirmed JLCPCB Global Sourcing
route or a separately qualified and adopted replacement; no silent substitution
is allowed. No commercial action was created.

H6 owns enclosure-dependent screw length and quoteable Gerber/BOM/CPL. Final
`SA818S-V` terms, `WBC16-1TLC` sourcing and the complete live stock/price
recheck remain immediate pre-order gates.

<a id="h6"></a>
## H6 · KiCad placement, routing and release candidate

**Status:** ▶️ current at **`H6.0.3-R1`**.

The [current exact-footprint placement result](h6-r2-exact-placement.md) now
contains two native six-layer KiCad boards. All 1,208/1,208 reviewed fitted
instances and all 789 global canonical / 823 board-local nets are materialized; the machine audit reports
zero hard courtyard conflicts, zero unplaced bodies and zero mapping errors.
Generation is byte-reproducible and KiCad 10 parses both boards. The [exact mechanical-stack result](h6-r2-mechanical-stack.md) locks
20-mm nylon M2.5 screws, captive nuts, 11-mm stops, wall bearings, four pilot
shoulders and independent edge capture; its full tolerance corner preserves
2.18 mm of nut thread and keeps the screw tip buried without using M1
structurally. The [microcoax service result](h6-r2-microcoax-service.md) adds five
relaxed corridors, five clear tape saddles and ten antenna solder windows with
7.69 mm minimum cable reserve. H6.0.1 is complete; H6.0.3 now rebaselines both
boards to 80 × 150 mm and dedicates x=35…40 mm to a real inner-face routing
corridor. All 1,208 positions remain exact, with no hard placement conflict.
The [live routing checkpoint](h6-r2-current-routing.md) binds 5,412 DRC-clean
track/via items to the current board hashes: 722 physical connections are
resolved and 2,543 remain. UI `ANALOG_AUDIO_SENSE` is complete; after 114 new
DRC-clean connections, RF/power has only 13 remaining in that class. The
checkpoint also includes a complete `VOICE_EFUSE_BACKUP_EN_N`
path through the added corridor using ordinary
0.15-mm tracks and 0.4/0.2-mm vias. Fresh KiCad DRC matches the clean 80-mm
baseline: zero UI findings and only the two already owned battery-holder
exceptions on RF/power. H6.0.2 routing totals remain historical evidence;
requalification and completion of routing are current.

### Live view of the 80-mm routing rebaseline

These are direct SVG exports from the saved `.kicad_pcb` files, not
illustrative mockups. Blue is front copper and red is back copper. Each file
embeds the source-board hash, so the H6 check rejects a stale image after any
PCB change. Open an image for its full-size view; layer details and the
reproducible export command are in the
[live H6.0.3 routing checkpoint](h6-r2-current-routing.md#live-images).

**Front UI board**

[![Current real routing of the front UI board](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)

**Rear RF/power board**

[![Current real routing of the rear RF/power board](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)

Expected result: two routed boards with the exact panel connected directly to the UI-board ZIF, and one
hash-locked fabrication package. H6 closes only after eight reviewable steps:

1. both-face placement for every board;
2. routed DRC/ERC and schematic-to-PCB net/footprint/courtyard/fitted-option parity;
3. routed-value power/PDN/current/thermal/startup/load-step re-analysis;
4. digital SI, return paths, USB and M1;
5. RF 50-ohm, ground/via fences, isolation and extracted Airband parasitics;
6. STEP/stack/cables/swept volumes/enclosure collision review;
7. Gerber/drill/BOM/CPL/STEP/schematic/assembly outputs and test access;
8. independent DFM and CPL-orientation review.

H6 alone does not authorize an order.

<a id="f-po"></a>
## F-PO · First-spin admission

**Status:** 🔒 waits for final H2/H6 and firmware R2.

Seven [machine-readable gates](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/first_spin_preorder_gate.json) must pass before payment: exact H2/H6 authority import; six reproducible diagnostic images; S3 QEMU; host/fake-HAL UI, controls and faults; available target dev-board runs; one flash/recovery bundle; and a current-limited owner bring-up script. Complete product F6–F8 is not required before ordering, but every installed device already has a diagnostic path. Factory Function Test is optional.

After `F-PO`, a separate immutable release binds Gerber, drill, BOM, CPL, STEP,
schematics, firmware and assembly instructions to the same hashes. Only then can
the quote for exactly one assembled `R2-EVT1` be approved.

<a id="h7"></a>
## H7 · Prototype build and bring-up

**Status:** 🔒 waits for reviewed H6 and `F-PO`, immutable release and explicit exact-one quote approval.

The firmware is exercised on host tests and emulated hardware before this
stage. The order target is exactly one factory-assembled prototype without
batteries. Its released package must leave no component, display-mating or
assembly choice to factory interpretation; paid factory Function Test is
optional, and the owner performs the first full USB power-on. H7 is still
necessary for the first real PCB: rail sequencing, recovery,
display/touch, controls, storage, radios, audio and safety are proven on the
assembled prototype.

<a id="h8"></a>
## H8 · RF, safety and endurance validation

**Status:** 🔒 waits for H7.

Expected result: conducted/radiated RF checks, coexistence, antenna identity,
thermal/watchdog shutdown, fault retention and 24–48 hour endurance evidence.

<a id="h9"></a>
## H9 · Production release

**Status:** 🔒 waits for reviewed H8.

Expected result: frozen manufacturing package, reproducible factory test,
versioned BOM/firmware, release notes and final product documentation.
