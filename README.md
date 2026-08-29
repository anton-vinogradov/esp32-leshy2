<div align="center">

# Leshy2 ⭐

### Open autonomous hardware for radio, communications and authorized research

**2.4/5-GHz Wi-Fi · BLE · 802.15.4 · 3× nRF24 · Sub-GHz · VHF/UHF · FM/AM/SW/LW/Airband · IR · LoRa expansion**

[Capabilities](docs/hardware.md) · [How it is built](docs/h0-r2-functional-architecture.md) · [Schematics](docs/schematics.md) · [Roadmap](docs/roadmap.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware) · [Русский](README.ru.md)

</div>

> **Current hardware marker: `H1-R2.37`.** The complete two-PCB placement is
> ready for visual acceptance: exact dual-RP GPIO/M1 map and C5 SDIO/service-mux,
> the series-produced `ER-TFT035IPS-6` + `ER-TPC035-6` display, passive 40-to-50-contact
> adapter, all 18 U219 support bodies, NFC pickup loop and the external volume
> of the supplied 108-mm antenna are registered fail-closed. No H1 geometry
> blocker remains; H1 stays open only until the complete mock-up is accepted.
> R2 H2/KiCad has not started, and ordering remains blocked.

> **R2 authority gate:** current H0/H1 has six compute domains and two `SC1512-A4`
> controllers: a front Hub RP and a rear RF RP. The checked-in G2F/H2/KiCad
> material is preserved historical single-RP R1 evidence, not current R2 authority.
> It cannot authorize firmware, R2 KiCad, fabrication or ordering. The exact
> dual-RP/C5 electrical authority is the current H1 machine contract; H2 will be
> a new R2 export only after physical H1 closes.

## What it is

Leshy2 is a portable, repairable instrument for radio observation,
communications, diagnostics and authorized security work. It keeps the user
interface responsive while active radio groups run on local buses and unused
interfaces enter a hardware-verifiable quiet state.

| Capability | Finished-device result |
|---|---|
| Three nRF24 radios | Concurrent full RX/TX/mixed modes: `3R`, `1T2R`, `2T1R`, `3T` |
| Native wireless | S3 Wi-Fi/BLE and C5 2.4/5-GHz Wi-Fi, 802.15.4 and IR |
| Dedicated RF | CC1101 Sub-GHz, independent VHF/UHF voice, FM/AM/SW/LW/Airband RX |
| Interface | 3.5-inch 320×480 touch IPS `ER-TFT035IPS-6` + `ER-TPC035-6` over direct 24-MHz i8080-8, S3-local buttons through `TCA9539PWR`, waterfall, microSD and audio |
| Expansion | One protected rear Cap slot for U214 LoRa or U219 CC1101+NFC, plus a protected M5 Unit interface |
| Recovery | Four independent USB paths, recessed per-controller controls and DBG10 fallbacks |
| Unattended safety | TX evidence, watchdog, thermal supervision, hard power-off and retained fault reason |

Transmission and intrusive laboratory functions are separated from ordinary
use by the [three-level safety model](docs/safety.md). Installation requires the
user to accept the non-aggression/authorized-use terms.

## Physical mock-up

![Current four-face Leshy2 mock-up](docs/images/h1-r2-four-faces.svg?rev=h1-r2.36-complete-tx-evidence-1)

[Open the legend for all 226 numbered references](docs/images/h1-r2-component-legend.svg?rev=h1-r2.36-complete-tx-evidence-1) ·
[detailed exterior](docs/images/h1-r2-external-layout.svg?rev=h1-r2.36-complete-tx-evidence-1) ·
[front inner face](docs/images/h1-r2-inner-ui.svg) ·
[rear inner face](docs/images/h1-r2-inner-rf.svg)

The exterior silkscreen identifies `UI PCB · R2-EVT1 · REV A` and
`RF/PWR PCB · R2-EVT1 · REV A`; `H1-R2.xx` remains documentation-only.

## How it is built

![Leshy2 functional architecture](docs/images/h0-r2-functional-architecture.svg)

The front UI/radio PCB owns S3, C5, all three complete nRF24 islands, the front
RP and microSD. The rear RF/power PCB owns CC1101,
VHF/UHF voice, broadcast/Airband, audio, M5 and the mutually exclusive U214/U219 Cap slot, the rear RP, power
and independent safety.

No video payload crosses the 80-contact M1 connector. The i8080-8 display TX
path remains local to S3; nRF payload remains local to the front RP. M1 is fully
assigned: 24 live signals, 14 main-power contacts, 2 AON contacts, 24 defined returns and 16 NC
reserves.

The drawings are generated from one machine-readable placement source. Inner
labels are drawing references, not silkscreen. The complete component legend is
linked beside the mock-up; individual inner views remain links without repeating
the same diagrams on the page.

[Open the readable physical result](docs/h1-r2-physical-layout.md) ·
[Grouped component cost ranking](docs/h1-r2-cost.md) ·
[Power and thermal result](docs/h1-r2-power-thermal.md) ·
[Airband filter feasibility](docs/h1-airband-filter.md)

## Schematics and interfaces

The public site keeps the principle schematics needed to understand the finished
device:

- [component and bus schematics](docs/schematics.md);
- [working principle pin design](docs/h0-r2-functional-architecture.md#working-principle-pin-design);
- [external programming and recovery](docs/h1-r2-physical-layout.md#what-the-user-sees);
- [safety and hard-off architecture](docs/safety.md).

## Roadmap and current position

The roadmap stays on this landing page until prototype fabrication is approved.
Firmware has its own [independent roadmap](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.md).

| Stage | Status | Published result |
|---|---|---|
| H0 · Requirements and functional architecture | ✅ Reviewed · R2 | [H0-R2 result](docs/h0-r2-functional-architecture.md) |
| **H1 · Physical product design** | **▶ Ready for acceptance · `H1-R2.37`** | [Current placement](docs/h1-r2-physical-layout.md) · [grouped cost ranking](docs/h1-r2-cost.md) |
| H2 · Production ECAD schematic | ⏳ Waiting for R2 H1 | [Stage page](docs/stage-results.md#h2) |
| H3 · Virtual electrical verification | ⏳ Waiting for R2 H2 | [Stage page](docs/stage-results.md#h3) |
| H4 · Joined hardware/firmware pre-layout gate | ⏳ Waiting for R2 H3 and firmware contract | [Stage page](docs/stage-results.md#h4) |
| H5 · Component and factory evidence | ⏳ Waiting for R2 H4 | [Stage page](docs/stage-results.md#h5) |
| H6 · KiCad placement, routing and release candidate | 🔒 Waiting for R2 H5 | [Stage page](docs/stage-results.md#h6) |
| F-PO · First-spin admission | 🔒 Waiting for final H2/H6 and firmware R2 | [Stage page](docs/stage-results.md#f-po) |
| H7 · Prototype fabrication and bring-up | 🔒 Waiting for H6, F-PO, immutable release and exact-one quote approval | [Stage page](docs/stage-results.md#h7) |
| H8 · Physical qualification | 🔒 Waiting for H7 | [Stage page](docs/stage-results.md#h8) |
| H9 · Manufacturing release | 🔒 Waiting for H8 and firmware F11 | [Stage page](docs/stage-results.md#h9) |

### Current H1 composition

- ✅ Exact front/rear RP GPIO0..47 maps, five Hub↔RF M1 signals and C5 SDIO/service-mux electrical join are machine-checked; budgets are `46/48` (2 free) and `40/48` (8 free: GP15/28/29/32/33/34/37/38). S3 has 11 newly released GPIO reserves.
- ✅ Ten main antenna ports repartitioned `5 + 5`; no main RF trace crosses M1.
- ✅ Series-produced `ER-TFT035IPS-6` + `ER-TPC035-6` is fixed with its exact 50-contact FPC, `ILI9488`, `FT6236` and passive `L2-DISP-ADP-001-B`; direct i8080-8 runs at a conservative 24 MHz (24 MB/s, 12.8 ms per full frame), with ordinary 4-wire serial retained as recovery mode.
- ✅ M1 has a complete 80-contact map and an enclosure load path: four 11-mm stops, anti-shear datums and independent PCB capture.
- ✅ Antenna silkscreen passes generated body/cable/accessory/fastener no-overlap checks.
- ✅ The onboard analog-video receiver, decoder, MMCX, antenna and physical reserves are removed; no active part requires owner soldering after PCBA.
- ✅ C5 DBG10 remains beside S3 DBG10; the structural audit of all currently registered bodies, including corrected maximum U219 package envelopes, reports zero same-face collisions and 2.59 mm minimum opposing clearance against 0.70 mm required.
- ✅ Public exterior, separate readable inner faces, service surface and real section views regenerated.
- ✅ The 208-line `H1-R2.37` base BOM is grouped by exact MPN and cost-ranked for one fitted prototype; R2 overrides count the second RP and its complete reference support, four DBG10 headers and 1,096 fitted parts. The accepted no-loss `AD8314ARMZ-REEL` and stocked `Hirose U.FL-R-SMT-1(80)` packaging routes save $10.42 in total; the current electronics planning floor is $273.42 before five unpriced lines, boards and assembly. All 20 most expensive groups now have a critical mass-market audit and are retained. Six cheaper antenna comparisons with $89.13 theoretical saving were explicitly rejected on 2026-08-30 and are neither active qualification routes nor BOM substitutions. The two identical `ANT-433-CW-QW-SMA` units remain permanently assigned to separate SUB-GHz and UHF VOICE ports so a menu error cannot key either transmitter into a missing or wrong-band load. A proven further $57.42–84.42 is needed to reach the $189–216 electronics band behind the $220–260 complete-device target. The former five-board BOM Tool run remains historical evidence only. Procurement targets exactly one factory-assembled prototype without batteries. The HMX donor route is rejected; the selected EastRising panel is a customer-supplied final-assembly part.
- ✅ U219 is accepted as the second mutually exclusive Cap profile: CC1101 is hard RX-only, NFC is poll/read-only, pin 10 is fail-disconnected and NFC field evidence joins `ANY_TX_AON_N`. Pin 7 power identity remains a received-unit gate, not an H2 claim.
- ✅ The two DCK boundaries, two BAT54S bridges and LMV331 comparator use official maximum full-package envelopes and source-backed courtyards; all five fit their bounded islands without overlap.
- ✅ All 18 exact U219 support parts and the existing Cap/evidence register now have one source-backed coordinate and conservative courtyard; the NFC pickup loop, DNP tuning bank and external swept volume of the supplied antenna are covered by the same fail-closed audit.
- ▶ **Exact current point:** review and explicitly accept the complete exterior, both inner faces after physically turning the PCBs over, and the real sandwich sections. After H1 acceptance, R2 H2 still requires the three electrical prerequisites listed in the roadmap; KiCad does not start automatically.
- 🔒 KiCad, prototype purchase and fabrication remain unauthorized.

Every closed top-level `H*` phase publishes a bilingual readable report linked
from the table. Internal substeps update this exact marker and both repositories,
but do not pretend that a whole phase has been reviewed.

<!-- current-substep: H1-R2.37 -->

## Repository

Hardware documentation and generators live here. Firmware lives in
[`esp32-leshy2-firmware`](https://github.com/anton-vinogradov/esp32-leshy2-firmware).
Both repositories are open; signed releases protect update authenticity without
preventing owners from building and signing their own firmware.
