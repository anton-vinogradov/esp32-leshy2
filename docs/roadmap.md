# Leshy2 hardware roadmap

[Home](../README.md) · [Русский](roadmap.ru.md) ·
[Firmware roadmap](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.md)

> **▶ Current hardware boundary: `H3-R2.1.3`.** Inside H3-R2.1, H0, H1 and [H2-R2.1.5](h2-acceptance.md) are reviewed. [H3-R2.0.1](h3-r2-input-freeze.md) freezes 14 stable inputs, [H3-R2.0.2](parameter-model-register.md) binds all 242 R2 groups, [H3-R2.0.3](verification-methods.md) freezes nine methods and twelve rules, [H3-R2.1.1](power-state-register.md) reviews 2,266 legal states, and [H3-R2.1.2](power-load-binding.md) explicitly binds 596 fitted instances plus six external loads. Rail-margin evaluation is current.
> No R2 KiCad routing, quote, reservation or order is authorized.

Status reconciled: **31 August 2026**.

## Status rules

- ✅ **Reviewed** — the phase result and its evidence exist.
- ▶ **Current** — the first unfinished hardware phase.
- ⏳ **Waiting** — a prerequisite phase is unfinished.
- 🔒 **Blocked** — the downstream action is forbidden until its gate.

Hardware phases are sequential. A closed top-level `H*` phase publishes a
bilingual result report linked below. An internal substep only updates the exact
marker and current checklist; it is never presented as review of the whole phase.

## Current product boundary

| Area | Current result |
|---|---|
| Functional architecture | ✅ [H0-R2 reviewed](h0-r2-functional-architecture.md): front UI/radio and rear RF/power domains, explicit owners, transports, quiet states and safety crossings |
| Physical design | ✅ [H1-R2.37 reviewed](h1-r2-acceptance.md): the complete two-PCB model, ten permanent antenna assignments, exact EastRising display, U214/U219 slot and all TX-evidence islands are physically coherent; [all 208 base-BOM MPN groups are ranked](h1-r2-cost.md) |
| Principle diagrams | Current component/bus map, external mock-up, separate readable inner faces, service map and power/filter diagrams are published |
| Production ECAD | ✅ [H2-R2.1.5 reviewed](h2-acceptance.md): three native KiCad projects materialize 1,187 instances, 4,327 physical pins and 827 canonical nets with zero ERC findings; six-domain cross-sheet/HW↔FW reconciliation passes; retained G2F/H2/KiCad is historical R1 evidence only |
| Firmware prerequisite | ✅ firmware F1-R2 reviewed; F2-R2.4 qualified all 12 target builds, 60 artifacts, 16 maps and 16 size gates, while F2-R2.5 reproducibility is current on the separate [F0–F11 roadmap](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.md); a separate fail-closed `F-PO` requires diagnostics, emulation and recovery before ordering |
| Ordering | 🔒 Exactly one assembled `R2-EVT1` only after H6, `F-PO`, immutable release package and explicit exact-one quote approval; production only at H9 |

## Reviewed H1 · exact composition

<!-- current-substep: H3-R2.1.3 -->

**Reviewed marker: `H1-R2.37`.** The placement package was accepted on
2026-08-31. The current hardware marker is `H3-R2.1.3`.

### 1. Functional-island placement

- ✅ Front UI/radio PCB: S3, C5, three complete nRF24 islands, front RP and microSD.
- ✅ Rear RF/power PCB: CC1101, VHF/UHF voice, FM/SW/AM/LW/Airband, audio,
  M5, the exact-one U214/U219 Cap slot, rear RP, power and safety.
- ✅ Authority is fail-closed: H0/H1 owns six domains and two RP controllers;
  old G2F/H2/KiCad has five domains, one RP and the old M1, so it is historical
  R1 reference only. Exact GPIO0..47 maps for both RPs, the five Hub↔RF M1
  signals and the C5 SDIO/service-mux join are now machine-checked H1 authority.
- ✅ Front RP GPIO: `47/48` with 1 free; rear RP GPIO: `43/48` with 5 free (GP32/33/34/37/38).
- ✅ Exact `ER-TFT035IPS-6` + `ER-TPC035-6` is direct 24-MHz i8080-8 through passive `L2-DISP-ADP-001-B`; user keys stay on the S3-local `TCA9539PWR` path, while encoder and USB remain direct S3 interfaces. Six GPIO remain uncommitted after reset/service closure.

### 2. RF and antenna locality

- ✅ Ten main SMA connectors are split `5 + 5`; each terminates on the PCB that
  owns its radio island.
- ✅ Front order: `N24-0`, `S3-2G4`, `N24-1`, `C5-2G4/5`, `N24-2`.
- ✅ Rear order: `RX-FM/SW`, `RX-AM/LW`, `CC-SUB`, `VOICE-VHF`, `VOICE-UHF`.
- ✅ No main RF trace crosses M1; every one of the ten antenna ports terminates on its owning PCB.

### 3. Interboard transport

- ✅ M1 is fully counted: 29 live signals, 14 main-power, 2 AON, 24 defined
  returns and 11 true NC reserves; the 4.25-A step is 0.3036 A per main contact.
- ✅ M1 carries no structural load: four 11.00-mm stops, at least two anti-shear
  datums and independent PCB capture cover the one-loose-screw case.
- ✅ Rear audio stays below 0.4 MB/s on the qualified 1.5 MB/s RP link; nRF
  payload is front-local.

### 4. Physical and service audit

- ✅ Same-face body collisions: `0`.
- ✅ Minimum opposing clearance: `2.59 mm`; required: `0.70 mm`.
- ✅ Four independent USB paths, eight recessed external recovery controls and
  four keyed DBG10 fallbacks remain available.
- ✅ Public diagrams use one board per inner image. The complete numbered
  226-reference projection is retained as linked machine-review evidence.
- ✅ The main public mock-up places the direct turned-over view of each PCB
  below its matching exterior; antenna silk passes body/cable/U214/display/fastener checks.
- ✅ Exterior silk prints `UI PCB · R2-EVT1 · REV A` and
  `RF/PWR PCB · R2-EVT1 · REV A`; the changing H1-R2.xx work marker is never
  printed and PCB REV advances only with released manufacturing-file changes.
- ✅ The generated cost review ranks every BOM line by fitted-device burden
  and 100-device projection. The five-board BOM Tool capture is historical
  evidence only; procurement targets one fully assembled prototype without batteries.
- ✅ The R1→R2 undercount is corrected: the cost audit now adds the complete
  reference support for the second RP2354B, the fourth USB/recovery groups and
  counts 1,096 fitted parts. Checked cheaper controls, holders and Tag-Connect
  were rejected for ESD, mechanics or service-workflow regressions, so their
  former assumed savings are removed.
- ✅ Five pre-order `74LVC2G126DC,125` buffers are replaced by the stocked
  same-family `74LVC2G126DP,125` (`C503392`). Logic, pin order, Schmitt inputs,
  `Ioff` and timing remain unchanged; regenerated TSSOP bodies pass H2, H3 and
  physical collision checks. The observed five-device line falls from `$40.60`
  to `$12.1425`.
- ✅ The stocked no-nut connector search retained the independent GCT
  `RFPC-SMA31/32-FN-175-A` edge-launch pair without a shared antenna frame.
  HenryTech parts point normal to the PCB; DreamLNK `SMA-KWE901/902` are about
  10.2 mm high with through-hole tails. Neither is a no-worse mechanical swap.
- ✅ The exact GCT land pattern uses the selected dual-face retention principle:
  the SMA shell straddles the board edge and solders two ground wings to each
  PCB face. One-face edge soldering is machine-rejected;
  the exact A1 footprint uses a 1.75-mm body gap, x=±2.55-mm shell-land centres
  and a 1.87-mm RF land. H5 locks documents/plan, H7 inspects every populated
  connector on the one assembled prototype; H8 performs ordinary assembly/disassembly,
  continuity/inspection and path-specific RF checks without artificial ageing,
  drops or a vibration programme.
- ✅ C5 retains official MPN `ESP32-C5-WROOM-1U-N8R8`; the active Standard-PCBA
  route is Espressif `C54951858` with supplier code `...-V1.2`, stock 460,
  available 440 and MOQ 1. Production accepts only matching incoming MD/lot
  identity and eFuse revision >=v1.2; v1.0 is engineering-only, while
  `C51950748`, v0.1, unknown identity and any mismatch fail closed.

### 5. U219 Cap integration

- ✅ U214 and U219 are mutually exclusive profiles of the same protected Cap
  slot. U219 CC1101 is hard RX-only; NFC is poll/read-only and cannot enable a
  field without independent `EV_N9` evidence in `ANY_TX_AON_N`.
- ✅ Pin 8 fails low, pin 10 is disconnected until qualified, and the exact
  SCL/SDA contacts reuse the existing isolated rear-RF-RP I²C path.
- ⚠️ U219 pin 7 power identity remains a received-unit gate. The profile stays
  off if continuity, polarity and exact revision do not prove protected 5 V.
- ✅ The complete pin-10 and NFC evidence circuits use 18 exact production
  bodies with current JLC routes, official envelopes and source-backed
  courtyards; every body fits its bounded island.
- ✅ The full-slot NFC pickup loop, DNP tuning bank and external swept volume of
  the supplied 108-mm antenna are registered. Missing, duplicate or substituted
  bodies and unresolved physical features fail generation.

### 6. H1 review result

- ✅ The onboard analog-video receiver, decoder, MMCX, antenna and physical bay
  are removed. No hidden active module requires owner soldering after PCBA.
- ✅ Current exact reserve is six GPIO on S3, five on the rear RP and eleven
  true NC contacts on M1; contacts 35–36 remain NC.
- ✅ The complete exterior, both turned-over inner faces and the real sandwich
  sections were accepted on 2026-08-30. [Read the phase report](h1-r2-acceptance.md).

## Reviewed H2-R2.1.5 · native projects and reconciliation

**Reviewed marker: `H2-R2.1.5`.** All pre-ECAD electrical prerequisites and exact
ledgers are closed. The three native R2 KiCad projects now materialize 1,187
fitted instances, 4,327 physical pins and 827 canonical nets. All three roots
parse and export, and KiCad ERC reports zero errors and zero warnings. Cross-sheet
and machine-readable hardware/firmware reconciliation passes. Placement and
routing have not started.

- ✅ `H2-R2.0.1`: exact onsemi `FSUSB42MUX` / `C11355` Standard-PCBA route
  reviewed from the live surface: stock 66,698; available 66,045; MOQ 1;
  USD 0.3179 at quantity 1.
- ✅ `H2-R2.0.2`: exact `DMN2056U-7` / `C332302` insulated-gate detector,
  `SN74LVC1G74DCUR` / `C70285` asynchronous latch and `74HC20PW,118` /
  `C546719` four-condition release gate reviewed from live Standard-PCBA
  surfaces. The exact-one fitted component burden is USD 0.5857.
- ✅ `H2-R2.0.3`: exact TI `TCA9803DGKR` / `C2687966` powered-off boundary
  reviewed with two MAIN-local 2.2-kohm pull-ups, AON-local 3.3-mA current
  sources, four Basic decouplers and a USD 0.3953 exact-one component burden.
- ✅ `H2-R2.1.1`: reviewed 3 native projects, 23 sheets, 6 domain owners,
  242 exact MPN groups and 1,197 product positions.
- ✅ `H2-R2.1.2`: 237 board groups have one symbol and footprint identity; five
  non-PCBA groups are explicit; 1,662 logical contacts and all sheet affinities
  are hash-bound with zero unresolved groups.
- ✅ `H2-R2.1.3` contact checkpoint: 1,605 board contacts across all 237 groups
  map to real selected-footprint pads or three explicit on-module RF interfaces;
  every named footprint pad is accounted for. The exact 50-contact Hirose FH34
  footprint is materialized from the official drawing and passes KiCad parsing.
- ✅ `H2-R2.1.3` symbol checkpoint: the deterministic `Leshy2_R2` library contains
  237 exact-MPN symbols and 1,618 unique electrical-pad pins; KiCad 10 parses,
  resaves and exports representative symbols without errors.
- ✅ `H2-R2.1.3` instance checkpoint: all 1,187 fitted board positions are
  allocated across 237 groups and three native projects; the historical R1
  ledger contributes no net, reference designator or topology authority.
- ✅ `H2-R2.1.3` net checkpoint: all 4,323 fitted-instance contacts reconcile
  to 4,063 connected endpoints, 260 explicit board no-connects and 827
  canonical nets; unresolved endpoints: zero.
- ✅ `H2-R2.1.3` native KiCad checkpoint: 3 projects, 23 project-graph sheets,
  1,187 symbols and 4,327 physical pins pass parser/export and zero-finding ERC.
- ✅ `H2-R2.1.4`: six domains, 173 controller pins, 50 cross-project nets and
  233 cross-sheet nets reconcile with no unresolved boundary.
- ✅ `H2-R2.1.5`: the [bilingual phase report](h2-acceptance.md) is published;
  the synchronized firmware H2 gate is open.
- 🔒 PCB placement, routing, quote, purchase and fabrication remain unauthorized.

[Open the native KiCad result](h2-r2-native-kicad.md) ·
[net result](h2-r2-net-ledger.md) ·
[instance result](h2-r2-instance-ledger.md) ·
[live prerequisite ledger](h2-r2-electrical-prerequisites.md).

## Complete hardware path

| Phase | Status | Result | Exit criterion |
|---|---|---|---|
| H0 · Requirements and functional architecture | ✅ [R2 reviewed](h0-r2-functional-architecture.md) | Product functions, owners, transports, safety and working pin budgets | Every function has one owner and all working budgets close |
| H1 · Physical product design | ✅ [Reviewed · `H1-R2.37`](h1-r2-acceptance.md) | Exterior, separate inner faces, sections, exact bodies, RF locality, service access and power envelope | No body/fastener/silkscreen/antenna/accessory/cross-board collision; exact MPN or controlled reserve for every body; mock-up accepted |
| H2 · Production ECAD schematic | ✅ [Reviewed · `H2-R2.1.5`](h2-acceptance.md) | Exact R2 symbols, contacts, nets, values, protection and footprints | Native KiCad, zero-finding ERC and cross-sheet/HW↔FW reconciliation pass |
| **H3 · Virtual electrical verification** | **▶ Current · `H3-R2.1.3`** | Complete power, digital, RF, audio, timing, thermal and fault simulation | Every legal state and transition passes before fabrication |
| H4 · Joined pre-layout gate | ⏳ Waiting for H3 and firmware R2 evidence | One current mechanics/ECAD/electrical/firmware review | No virtual blocker; each physical residual owns a test |
| H5 · Component and factory evidence | ⏳ Waiting for H4 | Exact current factory map and controlled external routes | Every BOM line has a current factory route without silent substitution |
| H6 · KiCad placement, routing and release candidate | 🔒 Waiting for H5 | Two routed boards, routed re-analysis and hash-locked fabrication candidate | Placement; DRC/ERC parity; power/thermal; SI/returns/USB; RF/extracted parasitics; STEP/stack/cables; outputs and independent DFM/CPL review pass |
| `F-PO` · First-spin admission | 🔒 Waiting for H2/H6 and firmware R2 | Six diagnostic images, S3 QEMU, fake-HAL/dev-board evidence, flash/recovery and owner bring-up script | `FPO1`–`FPO7` are reviewed against the same H2/H6 candidate hashes; paid factory FCT is not required |
| H7 · Prototype fabrication and bring-up | 🔒 Waiting for H6, `F-PO`, immutable release and exact-one quote approval | Exactly one factory-assembled `R2-EVT1` and retained owner bring-up log | Released assembly package needs no factory engineering guesses; owner current-limited USB power-on proves rails, recovery, UI, storage, audio, radios and expansion |
| H8 · Physical qualification | 🔒 Waiting for H7 | HIL, RF, thermal, power, safety and endurance evidence | Concurrent nRF modes, quiet interfaces, coexistence, VNA, watchdog and single-fault tests pass |
| H9 · Manufacturing release | 🔒 Waiting for H8 and firmware F11 | Reproducible manufacturing/test package paired with released firmware | Zero blocker and matching hardware/firmware release tags |

## Advancement rules

1. Fix a mismatch in its source artifact and regenerate every downstream view.
2. Do not silently remove an unexpected feature; first check for a missing requirement.
3. Accept a low-cost improvement automatically only when product behaviour does not change.
4. Verify every exact production MPN on the current JLCPCB Standard PCBA surface at selection, architecture freeze and immediately before order.
5. RF transmission and dangerous tests run only on owned loads, with owner authorization or inside an isolated laboratory.
6. Emulation does not replace bring-up, but H7 cannot be the first firmware execution: [`F-PO`](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/first_spin_preorder_gate.json) is mandatory before ordering.

## Current H3 execution path

1. ✅ `H2-R2.1.1`: freeze native R2 sources, sheet map and exact component inventory.
2. ✅ `H2-R2.1.2`: build the exact symbols, contacts, values, protection and footprint ledger.
3. ✅ `H2-R2.1.3`: materialize 1,187 reviewed instances and 827 canonical nets in three native KiCad projects; pass zero-finding ERC.
4. ✅ `H2-R2.1.4`: pass cross-sheet and HW↔FW reconciliation.
5. ✅ `H2-R2.1.5`: publish the reviewed bilingual H2 report and open H3.
6. ✅ [`H3-R2.0.1`](h3-r2-input-freeze.md): freeze 14 reviewed H2 inputs and assign all 23 native sheets exactly once across seven workstreams.
7. ✅ [`H3-R2.0.2`](parameter-model-register.md): bind all 242 R2 groups and 1,187 fitted positions to exact provenance, parameter classes and H3 owners.
8. ✅ [`H3-R2.0.3`](verification-methods.md): freeze nine reproducible methods, twelve pass/fail rules and fail-closed assignments for all 242 groups.
9. ▶ `H3-R2.1`: verify worst-case DC, source, charge and power states.
   - ✅ [`H3-R2.1.1`](power-state-register.md): enumerate all 2,266 legal states.
   - ✅ [`H3-R2.1.2`](power-load-binding.md): bind all 596 fitted power-connected instances and six external loads without a hidden aggregate.
   - ▶ `H3-R2.1.3`: evaluate rail voltage/current, protection and steady thermal margins.

Worst-case power/DC verification is the next action. Placement, routing, quoting and
every order remain blocked.
