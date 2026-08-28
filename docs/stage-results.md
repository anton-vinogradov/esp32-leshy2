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

**Status:** ▶️ current at **`H1-R2.31`**.

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
- [U214/U219 machine policy](../hardware/architecture/generated/H1-R2-U219-cap-policy.json)

The exact dual-RP GPIO/M1 map and the C5 SDIO/service-mux electrical join are
closed as current H1 authority. The accepted U219 profile shares the protected
Cap slot with U214, keeps CC1101 RX-only and NFC poll/read-only, and adds
independent NFC-field evidence to the existing safety aggregate.

Current physical result: ten main SMA ports are split 5+5; FPV uses a separate vertical
Molex `73415-2063` (`C588480`) MMCX on the rear face. The generated two-board
placement has zero same-face collisions and 2.59 mm minimum opposing clearance,
including the corrected official maximum full-package U219 host envelopes.
The enlarged 30 × 24 × 8 mm bay carries mutually exclusive post-PCBA K331 and
AWM666V lands; exactly one receiver is installed and C5 DBG10 is relocated.
Actual-module and solder qualification move to H5/H7. The five active U219 host
packages and their source-backed courtyards now fit the two reserved islands;
the canonical coordinate register for existing Cap/evidence bodies,
support-passive footprints, NFC pickup geometry and installed-antenna swept
volume are the four blockers still preventing final mock-up acceptance.
The display is physically turned so its flex exits toward the antenna edge;
firmware rotates display memory and touch coordinates by 180 degrees. The first
safe pre-order removal replaces five `74LVC2G126DC,125` buffers with stocked
same-family `74LVC2G126DP,125` (`C503392`), cutting the observed trial line from
`$40.60` to `$12.1425` without changing the circuit function. Cheaper stocked
no-nut SMA/RP-SMA pairs were rejected where their orientation, height or
through-hole tails degraded the accepted geometry; the independent GCT pair is retained.
The C5 manufacturer identity remains `ESP32-C5-WROOM-1U-N8R8`, while the active
stocked Standard-PCBA route is `C54951858` / supplier code `...-V1.2`. Incoming
MD/lot identity and eFuse revision must both prove >=v1.2 for production; v1.0 is
engineering-only and the historical `C51950748` cannot be selected as active.
Those placement numbers now include the U219 host switch, AON gate, two field
bridges, comparator and an explicitly unlocated pickup-loop reserve. Completing
the canonical coordinate register, support-passive values/MPNs and courtyards,
pickup geometry and installed antenna swept volume is the current H1 work;
explicit acceptance of the regenerated
mock-up follows it. R2 H2/KiCad has not started.

<a id="h2"></a>
## H2 · Production schematic

**Status:** ⏳ waits for H1.

The former reviewed G2F/H2/KiCad result is preserved as historical single-RP
R1 evidence and is explicitly superseded as current authority. R2 H2 remains
reopened until it exports six domains, both RP controllers and the exact H0 M1.

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
## H6 · KiCad placement and routing

**Status:** 🔒 waits for reviewed H5.

Expected result: two routed boards and one accepted fabrication package;
placement review, DRC, impedance/return paths, RF isolation, thermal copper,
test access and DFM must pass together. This is the final pre-order gate.

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
