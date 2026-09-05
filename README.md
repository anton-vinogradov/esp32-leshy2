<div align="center">

# Leshy2 ⭐

### Open autonomous hardware for radio, communications and authorized research

**2.4/5-GHz Wi-Fi · BLE · 802.15.4 · 3× nRF24 · Sub-GHz · VHF/UHF · FM/AM/SW/LW/Airband · IR · LoRa expansion**

[Capabilities](docs/hardware.md) · [How it is built](docs/h0-r2-functional-architecture.md) · [Schematics](docs/schematics.md) · [Roadmap](docs/roadmap.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware) · [Русский](README.ru.md)

</div>

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
| Interface | 3.5-inch 320×480 touch IPS `ER-TFT035IPS-6` + `ER-TPC035-6` over direct exact-20-MHz i8080-8, S3-local buttons through `TCA9539PWR`, waterfall, microSD and audio |
| Expansion | One protected rear Cap slot for U214 LoRa or U219 CC1101+NFC, plus a protected M5 Unit interface |
| Recovery | Four independent USB paths, recessed per-controller controls and DBG10 fallbacks |
| Unattended safety | TX evidence, watchdog, thermal supervision, hard power-off and retained fault reason |

Transmission and intrusive laboratory functions are separated from ordinary
use by the [three-level safety model](docs/safety.md). Installation requires the
user to accept the non-aggression/authorized-use terms.

> **Current hardware marker: `H6.0.3-R1`.** The complete two-PCB `H1-R2.39`
> placement was accepted and reviewed on 30 August 2026: exact dual-RP GPIO/M1 map and C5 SDIO/service-mux,
> the series-produced `ER-TFT035IPS-6` + `ER-TPC035-6` display and its direct
> 50-contact UI-PCB ZIF, all 18 U219 support bodies, NFC pickup loop and the external volume
> of the supplied 108-mm antenna are registered fail-closed. No H1 geometry
> blocker remains. The exact `FSUSB42MUX/C11355` factory route is reviewed;
> the exact service-VBUS path and `TCA9803DGKR/C2687966` Pack/Safety boundary
> are reviewed. The native R2 inventory is reviewed at `H2-R2.1.1`: two
> projects, 22 sheets, six domains, 251 exact component groups and 1,218 product
> positions. The exact symbol/contact/footprint ledger is reviewed at
> `H2-R2.1.2`: 245 board groups, six explicit non-PCBA groups and 1,617 logical
> contacts. Native symbol/footprint materialization accounts for all 1,558
> board contacts against 1,555 real selected-footprint contacts or three
> explicit on-module RF interfaces, with zero unclaimed named pads. The controlled
> library of 245 R2 symbols and 1,571 symbol pins passes KiCad 10; all
> 1,208 fitted instances are allocated without importing R1 designators. Their
> 4,302 ledger endpoints resolve to 4,064 connected endpoints, 238 explicit
> no-connects and 789 global canonical / 823 board-local nets with zero unresolved endpoints. The two
> [native KiCad projects](docs/h2-r2-native-kicad.md) now contain all 1,208
> symbols and 4,306 physical pins; KiCad ERC reports zero errors and zero
> warnings. H2 cross-sheet and hardware/firmware reconciliation covers six
> domains, 173 controller pins, 34 cross-project nets and 228 cross-sheet nets;
> [H2-R2.1.5 is reviewed](docs/h2-acceptance.md). [H3-R2.0.1](docs/h3-r2-input-freeze.md)
> freezes 14 stable inputs and all 22 sheets. [H3-R2.0.2](docs/parameter-model-register.md)
> reviews exact provenance for all 251 R2 groups and 1,208 fitted positions.
> [H3-R2.0.3](docs/verification-methods.md) freezes nine methods and twelve
> pass/fail rules. [H3-R2.1.1](docs/power-state-register.md) reviewed all 2,266 legal R2 states;
> [H3-R2.1.2](docs/power-load-binding.md) binds every load without a hidden aggregate. [H3-R2.1.3](docs/power-rail-margins.md) reviews 224 passing rail profiles. [H3-R2.1.4](docs/power-source-margins.md) owns all 75 source/pack lines and safely admits all 2,266 legal states: maximum pack current is 3.516 A against the 8-A boundary; 9-V/3-A and 15-V/2-A run every profile, while 14 oversized 5-V/3-A USB-only states are explicitly refused. The [H3-R2.1 cross-check](docs/power-dc-source-result.md) is reviewed. The complete [H3-R2.2 power-transition result](docs/power-transition-result.md) is also reviewed: 14 startup/reset/recovery scenarios, 7,316 USB/pack/DPM/brownout/source-loss cases, five protected-rail starts, four load-step envelopes and ten watchdog/fault-display cases pass without automatic restart. [H3-R2.3 analog verification](docs/analog-electrical-verification.md), [H3-R2.4 digital verification](docs/digital-electrical-verification.md), [H3-R2.5 RF verification](docs/rf-electrical-verification.md) and [H3-R2.6 thermal/fault verification](docs/thermal-fault-electrical-verification.md) are reviewed. The [global H3-R2 result](docs/h3-r2-acceptance.md) cross-checks 20 current evidence artifacts and all recorded source hashes with zero mismatch or open analytical finding; 51 physical-only rows remain explicitly owned by H5/H6/H8. [H4-R2.0.1](docs/h4-r2-input-freeze.md) froze 24 exact joined inputs. The [H4 diagnostic](docs/h4-r2-contract-reconciliation.md) found one owned 38-row BSP-generation gap; the [H4-R2.2 correction](docs/h4-r2-correction-closure.md) restored 173/173 controller rows and requalified all 12 target builds. The [global H4-R2 result](docs/h4-r2-acceptance.md) is reviewed with zero cross-domain contradiction. The historical [H5-R1 result](docs/h5-r1-acceptance.md) is now joined by the [current H5-R2 route revalidation](docs/h5-r2-current-route.md): all 249 purchasable groups / 1,216 articles have controlled routes, while `WBC16-1TLC` has one explicit order-time sourcing gate after its JLCPCB stock fell to zero. H6.0.1-R1 is complete: exact placement, the enclosure/fastener stack and all five relaxed microcoax corridors pass. `H6.0.3-R1` rebaselines both boards to 80 × 150 mm, preserves the external controls and five-plus-five antenna banks, and inserts a real 5-mm inner-face routing corridor. All 1,208 positions remain frozen without hard conflicts; routing requalification is current. The real PCBA price still follows Gerber/BOM/CPL. Ordering remains blocked.

> **H6 placement evidence:** the [current exact-footprint result](docs/h6-r2-exact-placement.md)
> now materializes both native six-layer boards and places all 1,208/1,208 fitted
> instances with zero hard courtyard conflict or unplaced body. Routing started
> only after the [mechanical stack](docs/h6-r2-mechanical-stack.md) and
> [five microcoax service corridors](docs/h6-r2-microcoax-service.md) passed.
> The [H6.0.2 routing policy](docs/h6-r2-routing-policy.md) classifies all
> 823 board-local net instances / 789 global canonical nets; only ordinary low-rate
> controls are eligible for automatic route proposals. The standard
> `JLC06161H-3313` calculator geometry is now enforced in KiCad: outer RF is
> 50-ohm CPWG at 5.31/6 mil and all 12 USB segments are native `_P/_N` pairs at
> 90 ohm, 5.31/6 mil. `H6.0.3-R1` widens both physical boards to 80 mm and
> dedicates x=35…40 mm to useful routing area. The [live H6.0.3 routing
> checkpoint](docs/h6-r2-current-routing.md) binds 5,412 checked track/via
> items to the current board hashes; native connectivity has 722 resolved and
> 2,543 remaining physical connections. The UI `ANALOG_AUDIO_SENSE` class is
> complete; RF/power has only 13 connections left in that class after 114 new
> DRC-clean connections. The formerly blocked
> `VOICE_EFUSE_BACKUP_EN_N` route now crosses the new corridor with ordinary
> 0.15-mm tracks and 0.4/0.2-mm vias. Fresh KiCad DRC matches the unrouted
> 80-mm baseline: zero UI violations and only the two already owned battery-holder
> exceptions on RF/power. Re-routing the chains released by the geometry change
> remains current; the former H6.0.2 accepted-slice totals are historical evidence.

## Current PCB routing

The images below are generated directly from the checked-in KiCad boards. They
show the live `H6.0.3-R1` rebaseline routing state, not an illustrative mock-up;
click either board for the full-size SVG and exact net labels.

<table>
  <tr>
    <td width="50%"><a href="docs/images/h6-r2-routing-ui.svg?rev=h6.0.3-r1"><img src="docs/images/h6-r2-routing-ui.svg?rev=h6.0.3-r1" alt="Current UI PCB routing" width="100%"></a></td>
    <td width="50%"><a href="docs/images/h6-r2-routing-rf.svg?rev=h6.0.3-r1-rf110"><img src="docs/images/h6-r2-routing-rf.svg?rev=h6.0.3-r1-rf110" alt="Current RF and power PCB routing" width="100%"></a></td>
  </tr>
  <tr>
    <td align="center">UI PCB · live 80-mm rebaseline</td>
    <td align="center">RF / power PCB · live 80-mm rebaseline</td>
  </tr>
</table>

[Open the detailed H6 stage result](docs/stage-results.md#h6).

> **R2 authority gate:** current H0/H1 has six compute domains and two `SC1512-A4`
> controllers: a front Hub RP and a rear RF RP. The checked-in G2F/H2/KiCad
> material is preserved historical single-RP R1 evidence, not current R2 authority.
> It cannot authorize firmware, R2 KiCad, fabrication or ordering. The exact
> dual-RP/C5 electrical authority is the reviewed H1 machine contract; the new
> native R2 schematics are reviewed logical H2 output, not PCB or fabrication authority.

## Physical mock-up

![Reviewed four-face Leshy2 mock-up](docs/images/h1-r2-four-faces.svg?rev=h1-r2.39-80mm-1)

[Open the legend for all 226 numbered references](docs/images/h1-r2-component-legend.svg?rev=h1-r2.39-80mm-1) ·
[detailed exterior](docs/images/h1-r2-external-layout.svg?rev=h1-r2.39-80mm-1) ·
[front inner face](docs/images/h1-r2-inner-ui.svg) ·
[rear inner face](docs/images/h1-r2-inner-rf.svg)

![Display PSA, folded FPC, relaxed service loop and direct ZIF](docs/images/display-mount.svg?rev=h1-r2.39-80mm-1)

![True side sections through the two-board sandwich](docs/images/h1-r2-inner-sections.svg?rev=h1-r2.39-80mm-1)

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
assigned: 31 live signals, 14 main-power contacts, 2 AON contacts, 24 defined returns and 9 true NC
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
| H1 · Physical product design | ✅ Reviewed · `H1-R2.39` | [Bilingual phase result](docs/h1-r2-acceptance.md) · [placement](docs/h1-r2-physical-layout.md) |
| H2 · Production ECAD schematic | ✅ Reviewed · `H2-R2.1.5` | [Bilingual phase result](docs/h2-acceptance.md) · [native KiCad result](docs/h2-r2-native-kicad.md) |
| H3 · Virtual electrical verification | ✅ Reviewed · `H3-R2.7` | [Bilingual phase result](docs/h3-r2-acceptance.md) · [physical evidence register](docs/physical-evidence-register-r2.md) · [stage page](docs/stage-results.md#h3) |
| H4 · Joined hardware/firmware pre-layout gate | ✅ Reviewed · `H4-R2.3` | [global result](docs/h4-r2-acceptance.md) · [BSP correction](docs/h4-r2-correction-closure.md) · [stage page](docs/stage-results.md#h4) |
| H5 · Component and factory evidence | ✅ Reviewed current R2 routes · `H5-R2.1` | [Current R2 result](docs/h5-r2-current-route.md) · [historical H5-R1](docs/h5-r1-acceptance.md) · [stage page](docs/stage-results.md#h5) |
| **H6 · KiCad placement, routing and release candidate** | **▶ Current · `H6.0.3-R1`** | [Exact placement](docs/h6-r2-exact-placement.md) · [routing policy](docs/h6-r2-routing-policy.md) · [live routing checkpoint](docs/h6-r2-current-routing.md) · [mechanical stack](docs/h6-r2-mechanical-stack.md) · [microcoax closure](docs/h6-r2-microcoax-service.md) · [stage page](docs/stage-results.md#h6) · [machine checklist](hardware/verification/h6-layout-release-plan.json) |
| F-PO · First-spin admission | 🔒 Waiting for final H2/H6 and firmware R2 | [Stage page](docs/stage-results.md#f-po) |
| H7 · Prototype fabrication and bring-up | 🔒 Waiting for H6, F-PO, immutable release and exact-one quote approval | [Stage page](docs/stage-results.md#h7) |
| H8 · Physical qualification | 🔒 Waiting for H7 | [Stage page](docs/stage-results.md#h8) |
| H9 · Manufacturing release | 🔒 Waiting for H8 and firmware F11 | [Stage page](docs/stage-results.md#h9) |

### Reviewed H1–H5 results and current H6 entry

- ✅ Exact front/rear RP GPIO0..47 maps, five Hub↔RF M1 signals and C5 SDIO/service-mux electrical join are machine-checked; budgets are `47/48` (1 free) and `43/48` (5 free: GP32/33/34/37/38). RF GPIO28/29 now form a power-coherent private Si5351 PIO-I²C bus. S3 retains 6 uncommitted GPIO after reset/service closure.
- ✅ Ten main antenna ports repartitioned `5 + 5`; no main RF trace crosses M1.
- ✅ Series-produced `ER-TFT035IPS-6` + `ER-TPC035-6` is fixed with its exact 50-contact FPC, `ILI9488`, `FT6236` and direct `FH34SRJ-50S-0.5SH(50)` on the UI PCB. The traceable ready-made 3M (TC) `4910SQ-2(5)` 50.8-mm PSA candidate retains the panel independently of the ZIF without any cutting; its official ±10% thickness tolerance makes a measured ≤0.714-mm folded-FPC stack and ≥0.20-mm actual clearance mandatory before release. The shortened slot/ZIF route preserves a machine-checked ≥5-mm relaxed reserve with one no-twist fold and explicit 1-to-1 / 50-to-50 orientation. Direct i8080-8 runs at an exact divider-safe 20 MHz (20 MB/s, 15.36 ms per full frame), with ordinary 4-wire serial retained through opened-device solder-jumper recovery.
- ✅ M1 has a complete 80-contact map and no structural role: the exact H6 stack uses four 11-mm `Ettinger 007.02.611` stops, 20-mm `Essentra 50M025045P020` nylon screws, captive `04M025045HN` nuts, four shell pilots and independent PCB capture. The full tolerance corner retains 2.18 mm of nut thread and buries the screw tip.
- ✅ Antenna silkscreen passes generated body/cable/accessory/fastener no-overlap checks.
- ✅ The onboard analog-video receiver, decoder, MMCX, antenna and physical reserves are removed; no active part requires owner soldering after PCBA.
- ✅ C5 DBG10 remains beside S3 DBG10; the structural audit of all currently registered bodies, including corrected maximum U219 package envelopes, reports zero same-face collisions and 2.59 mm minimum opposing clearance against 0.70 mm required.
- ✅ Public exterior, separate readable inner faces, service surface and real section views regenerated.
- ✅ The current 249-group purchasable R2 set is cost-ranked for exactly one prototype: 1,216 articles, `$311.38` known electronics, `$138.32` known external antennas and `$449.70` known combined before five unpriced component groups, two unpriced antenna groups, boards and assembly. Every current top-20 group has a critical market verdict: 19 are retained, while zero-stock `WBC16-1TLC` has a cheaper `H3-TC16-161T+ / C22383426` qualification candidate that is not yet an accepted substitution. The two identical `ANT-433-CW-QW-SMA` units remain permanently assigned to separate SUB-GHz and UHF VOICE ports so a menu error cannot key either transmitter into a missing or wrong-band load. The former five-board BOM Tool run remains historical evidence only. Procurement targets exactly one factory-assembled prototype without batteries. The HMX donor route is rejected; the selected EastRising panel is a customer-supplied final-assembly part.
- ✅ U219 is accepted as the second mutually exclusive Cap profile: CC1101 is hard RX-only, NFC is poll/read-only, pin 10 is fail-disconnected and NFC field evidence joins `ANY_TX_AON_N`. Pin 7 power identity remains a received-unit gate, not an H2 claim.
- ✅ The two DCK boundaries, two BAT54S bridges and LMV331 comparator use official maximum full-package envelopes and source-backed courtyards; all five fit their bounded islands without overlap.
- ✅ All 18 exact U219 support parts and the existing Cap/evidence register now have one source-backed coordinate and conservative courtyard; the NFC pickup loop, DNP tuning bank and external swept volume of the supplied antenna are covered by the same fail-closed audit.
- ✅ H1 was accepted and reviewed on 2026-08-30; its [bilingual result report](docs/h1-r2-acceptance.md) preserves the reviewed product boundary and evidence.
- ✅ `H2-R2.0.1`: live Standard-PCBA route for onsemi `FSUSB42MUX` / JLCPCB `C11355` reviewed with stock 66,698, available 66,045, MOQ 1 and USD 0.3179 quantity-one price.
- ✅ `H2-R2.0.2`: exact `DMN2056U-7` detector, `SN74LVC1G74DCUR` ownership latch and `74HC20PW,118` release qualifier reviewed with live Standard-PCBA routes, a fail-closed truth table and USD 0.5857 exact-one component cost.
- ✅ `H2-R2.0.3`: exact `TCA9803DGKR/C2687966` Pack/Safety powered-off boundary reviewed with correct rail-local termination and USD 0.3953 exact-one component cost.
- ✅ `H2-R2.1.1`: native R2 inventory reviewed — 2 projects, 22 sheets, 6 domain owners, 251 exact component groups and 1,218 product positions.
- ✅ `H2-R2.1.2`: exact ledger reviewed — 245 board groups, 6 explicit non-PCBA groups, 1,617 logical contacts and zero unresolved groups.
- ✅ `H2-R2.1.3`: 1,208 fitted positions expose 4,302 ledger endpoints: 4,064 connected and 238 explicit no-connects across 789 global canonical / 823 board-local nets; the two native projects materialize 4,306 physical pins with zero KiCad ERC errors or warnings.
- ✅ The Airband chain is complete and double-isolated: paired `HMC544AETR`, exact official transformers, private power-coherent LO I²C and a stock-backed nominal H2 filter state are present in the schematic. Filter retuning remains an explicit H3 gate.
- ✅ `H2-R2.1.4`: six domains, 173 controller-pin rows, 34 cross-project nets
  and 228 cross-sheet nets reconcile with zero unresolved boundary.
- ✅ `H2-R2.1.5`: the [bilingual H2 result](docs/h2-acceptance.md) is reviewed
  and the synchronized firmware H2 gate is open.
- ✅ `H3-R2.0.1`: [14 exact inputs and all 22 native sheets are hash-frozen](docs/h3-r2-input-freeze.md) across seven workstreams and all six domains.
- ✅ `H3-R2.0.2`: [all 251 R2 groups and 1,208 fitted positions have exact parameter/model provenance](docs/parameter-model-register.md), one H3 owner and no silent value assumption.
- ✅ `H3-R2.0.3`: [nine reproducible methods and twelve pass/fail rules](docs/verification-methods.md) cover all seven workstreams and all 251 groups.
- ✅ `H3-R2.1.1`: [all 2,266 legal R2 source, charge, fault and operating states are enumerated](docs/power-state-register.md), including U214/U219, Airband and all three-nRF mixes.
- ✅ `H3-R2.1.2`: [611 fitted powered instances—595 direct and 16 indirect—plus six external loads are bound explicitly](docs/power-load-binding.md); all 17 reviewed H2 power nets are covered, with no duplicate, unbound or miscellaneous line.
- ✅ `H3-R2.1.3`: [224 rail profiles across four rails pass voltage, protection and steady-thermal review](docs/power-rail-margins.md); all 617 fitted/external loads have one current owner or explicit source/pack deferral, minimum current reserve is 30.560% and minimum junction-temperature reserve is 24.706 °C.
- ✅ `H3-R2.1.4`: [all 75 source/pack lines and 2,266 legal states pass safe source/charge admission](docs/power-source-margins.md); maximum pack current is 3.516 A, sustained admission 1.549 A, and charge yields before system load.
- ✅ `H3-R2.1.5`: [all 15 ownership, state, rail, source and authorization cross-checks pass](docs/power-dc-source-result.md); the complete H3-R2.1 workstream is reviewed.
- ✅ `H3-R2.2.1`: [all 14 startup, shutdown, reset and recovery scenarios pass](docs/power-transition-sequences.md); every restart requires a fresh qualified physical KILL→RUN edge, while S3 retains the fault UI independently of direct C5/RF-RP reset.
- ✅ `H3-R2.2.2`: [all 7,316 USB/pack/DPM/brownout/source-loss transition cases pass](docs/power-handover.md); charging yields before system load, pack supplement remains inside 8 A, and OTG/backup stay disabled.
- ✅ `H3-R2.2.3/.4`: [five protected-rail starts, four load-step envelopes and ten watchdog/fault-display scenarios pass](docs/power-transition-result.md); M1-35 carries latched `FAULT_KILL` to the independent front indicator and nine true NC reserves remain.
- ✅ `H3-R2.3`: [all calculable display, audio, IR, battery and Airband analog corners pass](docs/analog-electrical-verification.md); the EastRising panel has a bounded 2.7-ohm backlight path, the exact Airband filter keeps 0.187 dB minimum margin and remaining work is physical-only H6/H8 measurement.
- ✅ `H3-R2.4`: [all calculable digital/interface checks pass](docs/digital-electrical-verification.md); five 3.3-V boundary classes retain positive DC margin, i8080-8 is exact 20 MHz with 15.36-ms full-frame wire time, M1 has 80/80 parity and nine true NC, and C5 service USB cannot contend with SDIO D2/D3.
- ✅ `H3-R2.5`: [all 71 RF/coexistence checks pass](docs/rf-electrical-verification.md); all ten permanent antenna feeds and five removable microcoaxes are explicit, the cable mix is 2×30 mm + 3×60 mm with 9.388 mm minimum conservative slack, and all four three-nRF24 role mixes remain admitted.
- ✅ `H3-R2.6`: [all 25 thermal/fault checks pass](docs/thermal-fault-electrical-verification.md); 56 current-R2 profiles, 30 single-fault cases and the local-only extended-operation policy close analytically, with seven physical residuals owned by H6/H8.
- ✅ `H3-R2.7`: the [bilingual global H3 report](docs/h3-r2-acceptance.md) cross-checks 20 current artifacts and their source hashes with no mismatch or open analytical finding; the [physical register](docs/physical-evidence-register-r2.md) keeps all 51 remaining rows open and owned.
- ✅ `H4-R2.0.1`: [24 exact current mechanics, ECAD, H3 and firmware-R2 inputs are hash-frozen](docs/h4-r2-input-freeze.md); all three cross-repository H3 import hashes match.
- ✅ `H4-R2.0.2` / `H4-R2.1`: [the preserved diagnostic](docs/h4-r2-contract-reconciliation.md) reconciles all six H2 domains, 80 M1 contacts and current H3 imports and owns the 38 missing generated rows.
- ✅ `H4-R2.2`: [complete C5, Pack and Safety BSP maps](docs/h4-r2-correction-closure.md) restore 173/173 rows; all 12 target configurations, 60 artifacts, 16 maps and 16 size gates requalify without warnings.
- ✅ `H4-R2.3`: the [bilingual global H4 result](docs/h4-r2-acceptance.md) closes the joined pre-layout gate with zero contradiction and transfers all 51 physical residuals to H5/H6/H8.
- ✅ `H5-R2.1`: the [current bilingual H5 result](docs/h5-r2-current-route.md) revalidates 249 purchasable groups / 1,216 articles with zero unmapped routes; the historical [H5-R1 evidence](docs/h5-r1-acceptance.md) remains available, and `WBC16-1TLC` is an explicit order-time sourcing gate.
- ✅ **`H6.0.1-R1` complete:** [native placement](docs/h6-r2-exact-placement.md) is reproducible at 1,208/1,208 positions with zero hard conflict; the [exact mechanical stack](docs/h6-r2-mechanical-stack.md) closes enclosure capture plus M2.5 retention; the [microcoax closure](docs/h6-r2-microcoax-service.md) proves five relaxed corridors, five clear saddles and ten antenna solder windows.
- ▶ **Exact current point `H6.0.3-R1`:** both boards are now 80 × 150 mm with a real x=35…40-mm routing corridor; 1,208/1,208 positions, mechanics and all five microcoax paths pass. The [current hash-bound routing snapshot](docs/h6-r2-current-routing.md) contains 5,412 DRC-clean copper items, resolves 722 physical connections and leaves 2,543 to route or explicitly no-connect; UI analogue/audio/sense is complete and RF/power has 13 connections remaining in that class.
- 🔒 Prototype purchase and fabrication remain unauthorized.

Every closed top-level `H*` phase publishes a bilingual readable report linked
from the table. Internal substeps update this exact marker and both repositories,
but do not pretend that a whole phase has been reviewed.

<!-- current-substep: H6.0.3-R1 -->

## Repository

Hardware documentation and generators live here. Firmware lives in
[`esp32-leshy2-firmware`](https://github.com/anton-vinogradov/esp32-leshy2-firmware).
Both repositories are open; signed releases protect update authenticity without
preventing owners from building and signing their own firmware.
