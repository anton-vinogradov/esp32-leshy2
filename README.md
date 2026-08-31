<div align="center">

# Leshy2 ⭐

### Open autonomous hardware for radio, communications and authorized research

**2.4/5-GHz Wi-Fi · BLE · 802.15.4 · 3× nRF24 · Sub-GHz · VHF/UHF · FM/AM/SW/LW/Airband · IR · LoRa expansion**

[Capabilities](docs/hardware.md) · [How it is built](docs/h0-r2-functional-architecture.md) · [Schematics](docs/schematics.md) · [Roadmap](docs/roadmap.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware) · [Русский](README.ru.md)

</div>

> **Current hardware marker: `H3-R2.2.3`.** The complete two-PCB `H1-R2.37`
> placement was accepted and reviewed on 30 August 2026: exact dual-RP GPIO/M1 map and C5 SDIO/service-mux,
> the series-produced `ER-TFT035IPS-6` + `ER-TPC035-6` display, passive 40-to-50-contact
> adapter, all 18 U219 support bodies, NFC pickup loop and the external volume
> of the supplied 108-mm antenna are registered fail-closed. No H1 geometry
> blocker remains. The exact `FSUSB42MUX/C11355` factory route is reviewed;
> the exact service-VBUS path and `TCA9803DGKR/C2687966` Pack/Safety boundary
> are reviewed. The native R2 inventory is reviewed at `H2-R2.1.1`: three
> projects, 23 sheets, six domains, 242 exact component groups and 1,197 product
> positions. The exact symbol/contact/footprint ledger is reviewed at
> `H2-R2.1.2`: 237 board groups, five explicit non-PCBA groups and 1,662 logical
> contacts. Native symbol/footprint materialization accounts for all 1,605
> board contacts are accounted for against real selected-footprint pads or three
> explicit on-module RF interfaces, with zero unclaimed named pads. The controlled
> library of 237 R2 symbols and 1,618 unique PCB-pad pins passes KiCad 10; all
> 1,187 fitted instances are allocated without importing R1 designators. Their
> 4,323 logical contacts resolve to 4,065 connected endpoints, 258 explicit
> no-connects and 826 canonical nets with zero unresolved endpoints. The three
> [native KiCad projects](docs/h2-r2-native-kicad.md) now contain all 1,187
> symbols and 4,327 physical pins; KiCad ERC reports zero errors and zero
> warnings. H2 cross-sheet and hardware/firmware reconciliation covers six
> domains, 173 controller pins, 51 cross-project nets and 236 cross-sheet nets;
> [H2-R2.1.5 is reviewed](docs/h2-acceptance.md). [H3-R2.0.1](docs/h3-r2-input-freeze.md)
> freezes 14 stable inputs and all 23 sheets. [H3-R2.0.2](docs/parameter-model-register.md)
> reviews exact provenance for all 242 R2 groups and 1,187 fitted positions.
> [H3-R2.0.3](docs/verification-methods.md) freezes nine methods and twelve
> pass/fail rules. [H3-R2.1.1](docs/power-state-register.md) reviewed all 2,266 legal R2 states;
> [H3-R2.1.2](docs/power-load-binding.md) binds every load without a hidden aggregate. [H3-R2.1.3](docs/power-rail-margins.md) reviews 224 passing rail profiles. [H3-R2.1.4](docs/power-source-margins.md) owns all 75 source/pack lines and safely admits all 2,266 legal states: maximum pack current is 3.516 A against the 8-A boundary; 9-V/3-A and 15-V/2-A run every profile, while 14 oversized 5-V/3-A USB-only states are explicitly refused. The [H3-R2.1 cross-check](docs/power-dc-source-result.md) is reviewed. [H3-R2.2.1](docs/power-transition-sequences.md) reviews 14 startup/reset/recovery scenarios without automatic restart, and [H3-R2.2.2](docs/power-handover.md) reviews all 7,316 USB/pack/DPM/brownout/source-loss cases. H3-R2.2.3 now verifies inrush, load steps, watchdog kill and retained fault display. Ordering remains blocked.

> **R2 authority gate:** current H0/H1 has six compute domains and two `SC1512-A4`
> controllers: a front Hub RP and a rear RF RP. The checked-in G2F/H2/KiCad
> material is preserved historical single-RP R1 evidence, not current R2 authority.
> It cannot authorize firmware, R2 KiCad, fabrication or ordering. The exact
> dual-RP/C5 electrical authority is the reviewed H1 machine contract; the new
> native R2 schematics are reviewed logical H2 output, not PCB or fabrication authority.

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

![Reviewed four-face Leshy2 mock-up](docs/images/h1-r2-four-faces.svg?rev=h1-r2.37-reviewed-1)

[Open the legend for all 226 numbered references](docs/images/h1-r2-component-legend.svg?rev=h1-r2.37-reviewed-1) ·
[detailed exterior](docs/images/h1-r2-external-layout.svg?rev=h1-r2.37-reviewed-1) ·
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
assigned: 30 live signals, 14 main-power contacts, 2 AON contacts, 24 defined returns and 10 true NC
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
| H1 · Physical product design | ✅ Reviewed · `H1-R2.37` | [Bilingual phase result](docs/h1-r2-acceptance.md) · [placement](docs/h1-r2-physical-layout.md) |
| H2 · Production ECAD schematic | ✅ Reviewed · `H2-R2.1.5` | [Bilingual phase result](docs/h2-acceptance.md) · [native KiCad result](docs/h2-r2-native-kicad.md) |
| **H3 · Virtual electrical verification** | **▶ Current · `H3-R2.2.3`** | [Input freeze](docs/h3-r2-input-freeze.md) · [parameter/model register](docs/parameter-model-register.md) · [verification methods](docs/verification-methods.md) · [power states](docs/power-state-register.md) · [load binding](docs/power-load-binding.md) · [rail margins](docs/power-rail-margins.md) · [source/charge margins](docs/power-source-margins.md) · [reviewed DC/source result](docs/power-dc-source-result.md) · [transition sequences](docs/power-transition-sequences.md) · [USB/pack handover](docs/power-handover.md) · [stage page](docs/stage-results.md#h3) |
| H4 · Joined hardware/firmware pre-layout gate | ⏳ Waiting for R2 H3 and firmware contract | [Stage page](docs/stage-results.md#h4) |
| H5 · Component and factory evidence | ⏳ Waiting for R2 H4 | [Stage page](docs/stage-results.md#h5) |
| H6 · KiCad placement, routing and release candidate | 🔒 Waiting for R2 H5 | [Stage page](docs/stage-results.md#h6) |
| F-PO · First-spin admission | 🔒 Waiting for final H2/H6 and firmware R2 | [Stage page](docs/stage-results.md#f-po) |
| H7 · Prototype fabrication and bring-up | 🔒 Waiting for H6, F-PO, immutable release and exact-one quote approval | [Stage page](docs/stage-results.md#h7) |
| H8 · Physical qualification | 🔒 Waiting for H7 | [Stage page](docs/stage-results.md#h8) |
| H9 · Manufacturing release | 🔒 Waiting for H8 and firmware F11 | [Stage page](docs/stage-results.md#h9) |

### Reviewed H1/H2 results and current H3 entry

- ✅ Exact front/rear RP GPIO0..47 maps, five Hub↔RF M1 signals and C5 SDIO/service-mux electrical join are machine-checked; budgets are `47/48` (1 free) and `43/48` (5 free: GP32/33/34/37/38). RF GPIO28/29 now form a power-coherent private Si5351 PIO-I²C bus. S3 retains 6 uncommitted GPIO after reset/service closure.
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
- ✅ H1 was accepted and reviewed on 2026-08-30; its [bilingual result report](docs/h1-r2-acceptance.md) preserves the reviewed product boundary and evidence.
- ✅ `H2-R2.0.1`: live Standard-PCBA route for onsemi `FSUSB42MUX` / JLCPCB `C11355` reviewed with stock 66,698, available 66,045, MOQ 1 and USD 0.3179 quantity-one price.
- ✅ `H2-R2.0.2`: exact `DMN2056U-7` detector, `SN74LVC1G74DCUR` ownership latch and `74HC20PW,118` release qualifier reviewed with live Standard-PCBA routes, a fail-closed truth table and USD 0.5857 exact-one component cost.
- ✅ `H2-R2.0.3`: exact `TCA9803DGKR/C2687966` Pack/Safety powered-off boundary reviewed with correct rail-local termination and USD 0.3953 exact-one component cost.
- ✅ `H2-R2.1.1`: native R2 inventory reviewed — 3 projects, 23 sheets, 6 domain owners, 242 exact MPN groups and 1,197 product positions.
- ✅ `H2-R2.1.2`: exact ledger reviewed — 237 board groups, 5 explicit non-PCBA groups, 1,662 logical contacts and zero unresolved groups.
- ✅ `H2-R2.1.3`: 1,187 fitted positions and 4,323 logical contacts resolve into 826 canonical nets; the three native projects materialize 4,327 physical pins with zero KiCad ERC errors or warnings.
- ✅ The Airband chain is complete and double-isolated: paired `HMC544AETR`, exact official transformers, private power-coherent LO I²C and a stock-backed nominal H2 filter state are present in the schematic. Filter retuning remains an explicit H3 gate.
- ✅ `H2-R2.1.4`: six domains, 173 controller-pin rows, 51 cross-project nets
  and 236 cross-sheet nets reconcile with zero unresolved boundary.
- ✅ `H2-R2.1.5`: the [bilingual H2 result](docs/h2-acceptance.md) is reviewed
  and the synchronized firmware H2 gate is open.
- ✅ `H3-R2.0.1`: [14 exact inputs and all 23 native sheets are hash-frozen](docs/h3-r2-input-freeze.md) across seven workstreams and all six domains.
- ✅ `H3-R2.0.2`: [all 242 R2 groups and 1,187 fitted positions have exact parameter/model provenance](docs/parameter-model-register.md), one H3 owner and no silent value assumption.
- ✅ `H3-R2.0.3`: [nine reproducible methods and twelve pass/fail rules](docs/verification-methods.md) cover all seven workstreams and all 242 groups.
- ✅ `H3-R2.1.1`: [all 2,266 legal R2 source, charge, fault and operating states are enumerated](docs/power-state-register.md), including U214/U219, Airband and all three-nRF mixes.
- ✅ `H3-R2.1.2`: [613 fitted powered instances—597 direct and 16 indirect—plus six external loads are bound explicitly](docs/power-load-binding.md); all 17 reviewed H2 power nets are covered, with no duplicate, unbound or miscellaneous line.
- ✅ `H3-R2.1.3`: [224 rail profiles across four rails pass voltage, protection and steady-thermal review](docs/power-rail-margins.md); all 619 fitted/external loads have one current owner or explicit source/pack deferral, minimum current reserve is 30.560% and minimum junction-temperature reserve is 24.706 °C.
- ✅ `H3-R2.1.4`: [all 75 source/pack lines and 2,266 legal states pass safe source/charge admission](docs/power-source-margins.md); maximum pack current is 3.516 A, sustained admission 1.549 A, and charge yields before system load.
- ✅ `H3-R2.1.5`: [all 15 ownership, state, rail, source and authorization cross-checks pass](docs/power-dc-source-result.md); the complete H3-R2.1 workstream is reviewed.
- ✅ `H3-R2.2.1`: [all 14 startup, shutdown, reset and recovery scenarios pass](docs/power-transition-sequences.md); every restart requires a fresh qualified physical KILL→RUN edge, while S3 retains the fault UI independently of direct C5/RF-RP reset.
- ✅ `H3-R2.2.2`: [all 7,316 USB/pack/DPM/brownout/source-loss transition cases pass](docs/power-handover.md); charging yields before system load, pack supplement remains inside 8 A, and OTG/backup stay disabled.
- ▶ **Exact current point `H3-R2.2.3`:** verify inrush, load steps, watchdog kill and retained fault display.
- 🔒 PCB placement, routing, prototype purchase and fabrication remain unauthorized.

Every closed top-level `H*` phase publishes a bilingual readable report linked
from the table. Internal substeps update this exact marker and both repositories,
but do not pretend that a whole phase has been reviewed.

<!-- current-substep: H3-R2.2.3 -->

## Repository

Hardware documentation and generators live here. Firmware lives in
[`esp32-leshy2-firmware`](https://github.com/anton-vinogradov/esp32-leshy2-firmware).
Both repositories are open; signed releases protect update authenticity without
preventing owners from building and signing their own firmware.
