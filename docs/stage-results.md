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

**Status:** ✅ reviewed at **`H1-R2.37`** on 2026-08-30.

- [Reviewed H1 phase result](h1-r2-acceptance.md)
- [Current physical design](h1-r2-physical-layout.md)
- [Outer faces](images/h1-r2-external-layout.svg?rev=h1-r2.37-reviewed-1)
- [Front inner face](images/h1-r2-inner-ui.svg)
- [Rear inner face](images/h1-r2-inner-rf.svg)
- [External service access](images/h1-r2-service-access.svg?rev=h1-r2.37-reviewed-1)
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
removed. Eleven S3 GPIOs, eight rear-RP GPIOs and M1 contacts 35–36 remain
reserves; no hidden active module requires owner soldering after PCBA.

H1 has no physical blocker. The complete mock-up was explicitly accepted on
2026-08-30. This review does not authorize KiCad or ordering.

<a id="h2"></a>
## H2 · Production schematic

**Status:** ▶️ current at **`H2-R2.0.2`**.

The former reviewed G2F/H2/KiCad result is preserved as historical single-RP
R1 evidence and is explicitly superseded as current authority. The new R2 H2
has opened, but native schematic export/KiCad has not started.

Exact current checklist:

1. ✅ `H2-R2.0.1`: exact onsemi `FSUSB42MUX` / JLCPCB `C11355` live
   Standard-PCBA route reviewed: stock 66,698; available 66,045; MOQ 1;
   USD 0.3179 at quantity 1;
2. ▶ `H2-R2.0.2`: select and prove the exact factory-placeable always-on
   service-VBUS detector/latch;
3. ⏳ `H2-R2.0.3`: close the powered-off-Ioff Pack/Safety I²C boundary with separate
   `3V3_MAIN`/AON pull-ups on Hub GPIO42/43.

[Live prerequisite results](h2-r2-electrical-prerequisites.md).

Expected result: native KiCad schematics regenerated from the R2 architecture,
with pin reconciliation, ERC, NC review and a synchronized HW↔FW contract.
The [schematics page](schematics.md) keeps the principle diagrams visible and
clearly labels retained R1 ECAD as non-current evidence.

<a id="h3"></a>
## H3 · Virtual electrical verification

**Status:** 🔒 waits for reviewed H2.

Expected result: complete power, digital, RF, audio, timing, thermal and fault
simulation. Every legal state and transition must pass before fabrication.

<a id="h4"></a>
## H4 · Joined pre-layout gate

**Status:** 🔒 waits for reviewed H3 and current firmware R2 evidence.

Expected result: one current mechanics/ECAD/electrical/firmware review with no
virtual blocker and an owned downstream test for every physical residual.

<a id="h5"></a>
## H5 · Component and factory evidence

**Status:** 🔒 waits for reviewed H4.

Expected result: every exact MPN rechecked on the current JLCPCB surface,
non-PCBA accessories listed, consigned/private/global sourcing qualified and
received-part measurements assigned to their controlled downstream gates.

<a id="h6"></a>
## H6 · KiCad placement, routing and release candidate

**Status:** 🔒 waits for reviewed H5.

Expected result: two routed boards, the replaceable display adapter and one
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
