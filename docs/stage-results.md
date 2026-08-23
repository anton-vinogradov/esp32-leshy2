# ⭐ Leshy2 stage results

[Home](../README.md) · [Full roadmap](roadmap.md) · [Русский](stage-results.ru.md)

This page collects the current outputs of each stage, not design-history
discussion. A completed stage receives “reviewed” only after its exit criteria
are satisfied.

<a id="h0"></a>
## ⭐ H0 · Requirements and functional architecture

**Status:** ✅ reviewed.

- [Hardware architecture](hardware.md) — capabilities, owners and boundaries.
- [Exact pin assignment](pinout.md) — GPIO, peripherals, directions and nets.
- [M1 map](interconnect.md) — physical crossing between the two PCBs.
- [HW↔FW integration contract](../hardware/architecture/target-integration-contract.json).
- [Machine target BOM](../hardware/architecture/generated/G2F-3I-target-bom.csv).

<a id="h1"></a>
## ⭐ H1 · Physical product design

**Status:** ✅ reviewed.

- [Outer faces](images/current-clamshell.svg),
  [service access](images/service-access.svg) and
  [mirrored inner faces](images/internal-board-layout.svg).
- [True antenna-edge view](images/top-edge-view.svg) and
  [sandwich sections](images/sandwich-section.svg).
- [Series navigation](images/navigation-cluster.svg) and
  [replaceable display adapter](images/display-adapter.svg).
- [Physical source register](physical-source-register.md).
- [Machine acceptance package](../hardware/product-design/generated/H1-cross-view-acceptance.json).

<a id="h2"></a>
## ⭐ H2 · Production ECAD schematic

**Status:** ▶️ current, exact marker `H2.3.12`.

- [Public schematics](schematics.md) — principle diagrams and current native
  KiCad sheet links.
- [H2 execution plan](../hardware/ecad/h2-schematic-plan.json) — exact subtask
  content and status.
- [Complete instance ledger](../hardware/ecad/generated/H2-instance-ledger.json).
- [HW↔FW export](../hardware/ecad/generated/H2-hwfw-contract.json).
- The complete UI/control PCB and the first nine RF/power sheets are reviewed.
- [`RF_30_RP2354_CORE_SERVICE`](../hardware/ecad/kicad/LESHY2-RF/RF_30_RP2354_CORE_SERVICE.kicad_sch)
  contains 48 exact components, all 81 SC1512-A4 package contacts, the official
  core-regulator and 12-MHz clock circuits, native USB/recovery and 13 explicit
  no-connects; its [machine review](../hardware/ecad/generated/H2-RF30-rp2354-core-service.json)
  passes native KiCad.
- [`RF_31_NRF24_X3`](../hardware/ecad/kicad/LESHY2-RF/RF_31_NRF24_X3.kicad_sch)
  contains 105 exact ledger components plus three factory-IPEX boundaries, 311
  physical contacts, three independent PIO SPI and RF paths, and two explicit
  no-connects; its [machine review](../hardware/ecad/generated/H2-RF31-nrf24-x3.json)
  passes native KiCad.
- [`RF_32_SUBGHZ_VOICE`](../hardware/ecad/kicad/LESHY2-RF/RF_32_SUBGHZ_VOICE.kicad_sch)
  contains 116 components and 363 physical contacts: independent CC1101 data
  and SA518 voice power/control/RF paths, 30 interfaces and 11 explicit
  no-connects; its [machine review](../hardware/ecad/generated/H2-RF32-subghz-voice.json)
  passes native KiCad. The SA518 footprint remains an honest H5 land-fit gate.
- [`RF_34_U214_M5_EXT`](../hardware/ecad/kicad/LESHY2-RF/RF_34_U214_M5_EXT.kicad_sch)
  contains 53 symbols, 52 board-fitted components, 228 contacts and 27
  interfaces. Its [machine review](../hardware/ecad/generated/H2-RF34-u214-m5-ext.json)
  confirms separate protected U214 and native M5 Unit paths; U214 itself is an
  external mating product, not a fictitious board component.
- [`RF_35_REAR_CONTROLS`](../hardware/ecad/kicad/LESHY2-RF/RF_35_REAR_CONTROLS.kicad_sch)
  contains seven fitted components and 36 contacts. Its
  [machine review](../hardware/ecad/generated/H2-RF35-rear-controls.json)
  closes independent encoder A/B/push and PTT paths with local ESD; the knob
  remains an external mechanical mating item.
- [`RF_36_AUDIO_IO_AMP`](../hardware/ecad/kicad/LESHY2-RF/RF_36_AUDIO_IO_AMP.kicad_sch)
  contains 14 symbols and 34 contacts. Its
  [machine review](../hardware/ecad/generated/H2-RF36-audio-io-amp.json)
  closes the exact downward-facing microphone, corrected compact U-DFN
  amplifier, reset-low shutdown and two independent floating-BTL outputs.
- [`RF_40_INTERBOARD_M1`](../hardware/ecad/kicad/LESHY2-RF/RF_40_INTERBOARD_M1.kicad_sch)
  contains the exact 80-contact receptacle and 51 hierarchy interfaces. Its
  [machine review](../hardware/ecad/generated/H2-RF40-interboard-m1.json)
  proves row-for-row equality with UI-side M1, including all repeated rails
  and returns, with no reserve or NC.
- RF-side TX safety and physical evidence are now active work.

<a id="h3"></a>
## H3 · Virtual electrical verification

**Status:** ⏳ waiting for H2.

Outputs will include worst-case DC budget, startup/shutdown and handover
simulation, fault tree, thermal/power/transient evidence, digital timing/levels
and RF pre-layout constraints. Layout remains blocked while a virtually
testable blocker exists.

<a id="h4"></a>
## H4 · Joined pre-layout gate

**Status:** 🔒 waiting for H1–H3 and firmware F3.

One joined review of mechanics, production ECAD, virtual electrical evidence
and target-visible firmware contracts. F3 requires builds for all five domains,
size/rollback gates, S3 QEMU and portable/host models for targets without an
exact emulator.

<a id="h5"></a>
## H5 · Component evidence samples

**Status:** 🔒 waiting for H4 and separate cost approval.

A minimal purchase closes only uncertainties that documents cannot resolve:
received-part identity, mating, stack-up and physical dimensions. It is not a
production basket.

<a id="h6"></a>
## H6 · PCB placement and routing

**Status:** 🔒 waiting for H5.

Outputs are two real PCBs with closed DRC, impedance, return-current, RF
isolation, antenna-feed, thermal, assembly and manufacturability reviews.

<a id="h7"></a>
## H7 · Prototype fabrication and bring-up

**Status:** 🔒 waiting for H6, firmware F3 already inherited through H4 and
explicit order approval.

Yes: partial target firmware must already build and run through available
emulators/host models before this stage. H7 creates the first small PCB lot and
runs rail, boot, recovery and interface smoke tests. Emulation does not replace
bring-up, but fabrication must not be the first execution of the code.

<a id="h8"></a>
## H8 · Physical qualification

**Status:** 🔒 waiting for H7.

HIL, RF, antenna/VNA, coexistence, thermal, power, safety, endurance and full
three-nRF24 `3R/1T2R/2T1R/3T` evidence.

<a id="h9"></a>
## H9 · Manufacturing release

**Status:** 🔒 waiting for H8 and firmware F11.

A reproducible BOM/fab/assembly/fixture/calibration/test package, zero blockers
and explicitly bound hardware and firmware release tags.
