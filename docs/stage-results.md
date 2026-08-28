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
RP, and CC1101, voice, broadcast/Airband, audio, FPV, extensions and safety
remain local to the rear RP. M1 carries control/data transport, one CVBS signal,
safety evidence and power—not primary RF payloads.

<a id="h1"></a>
## H1 · Physical product design

**Status:** ▶️ current at **`H1-R2.22`**.

- [Current physical design](h1-r2-physical-layout.md)
- [Outer faces](images/h1-r2-external-layout.svg?rev=h1-r2.21-dual-fpv-7)
- [Front inner face](images/h1-r2-inner-ui.svg)
- [Rear inner face](images/h1-r2-inner-rf.svg)
- [External service access](images/h1-r2-service-access.svg?rev=h1-r2.21-dual-fpv-7)
- [Vertical FPV MMCX proof](images/h1-r2-mmcx-service.svg)
- [Machine placement audit](../hardware/product-design/generated/H1-R2-placement-audit.json)
- [Analog FPV path](h1-r2-fpv.md)
- [Airband receive path](h1-airband-filter.md)
- [Power and thermal architecture](h1-r2-power-thermal.md)

Current result: ten main SMA ports are split 5+5; FPV uses a separate vertical
Molex `73415-2063` (`C588480`) MMCX on the rear face. The generated two-board
placement has zero same-face collisions and 1.05 mm minimum opposing clearance.
The enlarged 30 × 24 × 8 mm bay carries mutually exclusive post-PCBA K331 and
AWM666V lands; exactly one receiver is installed and C5 DBG10 is relocated.
Actual-module and solder qualification move to H5/H7. No engineering blocker
remains; explicit acceptance of the complete mock-up is the final H1 action.

<a id="h2"></a>
## H2 · Production schematic

**Status:** ⏳ waits for H1.

Expected result: native KiCad schematics regenerated from the R2 architecture,
with pin reconciliation, ERC, NC review and a synchronized HW↔FW contract.
The [schematics page](schematics.md) keeps the principle diagrams visible and
clearly labels retained R1 ECAD as non-current evidence.

<a id="h3"></a>
## H3 · PCB placement and routing

**Status:** 🔒 waits for reviewed H2.

Expected result: routed UI/radio and RF/power PCBs, controlled-impedance RF and
CVBS paths, return-current review, antenna isolation and post-route electrical
checks.

<a id="h4"></a>
## H4 · Enclosure and mechanical package

**Status:** 🔒 waits for reviewed H3.

Expected result: production enclosure, verified openings and labels, installed
U214/antenna/USB/button access, thermal clearances and assembly drawings.

<a id="h5"></a>
## H5 · Procurement and incoming qualification

**Status:** 🔒 waits for reviewed H4.

Expected result: every exact MPN rechecked on the current JLCPCB surface,
non-PCBA accessories listed, consigned/private/global sourcing qualified and
received-part measurements closed.

<a id="h6"></a>
## H6 · Fabrication release package

**Status:** 🔒 waits for reviewed H5.

Expected result: Gerber, drill, BOM, CPL, drawings, impedance, DFM, fixture and
factory-test package verified together. This is the final pre-order gate.

<a id="h7"></a>
## H7 · Prototype build and bring-up

**Status:** 🔒 waits for reviewed H6 and explicit order approval.

The firmware is exercised on host tests and emulated hardware before this
stage. H7 is still necessary for the first real PCB: rail sequencing, recovery,
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
