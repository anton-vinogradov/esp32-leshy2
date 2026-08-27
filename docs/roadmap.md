# Leshy2 hardware roadmap

[Home](../README.md) · [Русский](roadmap.ru.md) ·
[Firmware roadmap](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.md)

> **▶ Current hardware boundary: `H1-R2.19`.** H0 is reviewed. H1 is not.
> No R2 KiCad routing, quote, reservation or order is authorized.

Status reconciled: **27 August 2026**.

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
| Physical design | ▶ [H1-R2.19](h1-r2-physical-layout.md): complete functional islands, `5 + 5` main antenna banks, separate rear FPV MMCX and controlled SP331RX candidate-family geometry |
| Principle diagrams | Current component/bus map, external mock-up, separate readable inner faces, service map, FPV/MMCX proof and power/filter diagrams are published |
| Production ECAD | ⏳ R1 evidence retained; R2 schematic waits for H1 |
| Firmware prerequisite | ✅ firmware F1-R2 reviewed; F2-R2.0 is current on the separate [F0–F11 roadmap](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.md); emulator/dev-board execution must precede H7 fabrication |
| Ordering | 🔒 Prototype order only at H7 after H6 and explicit approval; production only at H9 |

## Current H1 · exact composition

<!-- current-substep: H1-R2.19 -->

**Exact marker: `H1-R2.19`.** This is one physical-design substep, not a closed
H1 report.

### 1. Functional-island placement

- ✅ Front UI/radio PCB: S3, C5, three complete nRF24 islands, front RP,
  microSD and UI-local TVP5150.
- ✅ Rear RF/power PCB: CC1101, VHF/UHF voice, FM/SW/AM/LW/Airband, audio,
  K331 FPV, M5, U214, rear RP, power and safety.
- ✅ Front RP GPIO: `46/48` with 2 free; rear RP GPIO: `45/48` with 3 free; K331 RSSI is officially NC.
- ✅ Display is direct 32-MHz i8080-8; all user keys, encoder, USB and camera RX remain direct S3 interfaces.

### 2. RF and antenna locality

- ✅ Ten main SMA connectors are split `5 + 5`; each terminates on the PCB that
  owns its radio island.
- ✅ Front order: `N24-0`, `S3-2G4`, `N24-1`, `C5-2G4/5`, `N24-2`.
- ✅ Rear order: `RX-FM/SW`, `RX-AM/LW`, `CC-SUB`, `VOICE-VHF`, `VOICE-UHF`.
- ✅ Separate Molex `73415-2063` (`C588480`) vertical SMT MMCX provides
  `FPV RX · 5.8G` below the evenly pitched five-SMA rear row and above U214.
- ✅ No main RF trace crosses M1; the MMCX has no through-board tail.

### 3. Interboard transport

- ✅ K331 remains rear-local and TVP5150 becomes UI-local.
- ✅ M1 carries one 75-ohm CVBS beside ground; the 8-bit data bus plus
  PCLK/VSYNC/HREF remain UI-local.
- ✅ M1 is fully counted: 25 live signals, 14 main-power, 2 AON, 25 defined
  returns and 14 NC reserves; the 4.25-A step is 0.3036 A per main contact.
- ✅ M1 carries no structural load: four 11.00-mm stops, at least two anti-shear
  datums and independent PCB capture cover the one-loose-screw case.
- ✅ Rear audio stays below 0.4 MB/s on the qualified 1.5 MB/s RP link; nRF
  payload is front-local.

### 4. Physical and service audit

- ✅ Same-face body collisions: `0`.
- ✅ Minimum opposing clearance: `1.44 mm`; required: `0.70 mm`.
- ✅ FPV MMCX body clearance to nearest SMA: `2.07 mm`.
- ✅ Controlled right-angle plug: `2.40 mm` to SMA, `4.80 mm` to U214 and no
  mounting-hole conflict; Ø12 remains a temporary H5 finger-access check.
- ✅ Four independent USB paths, eight recessed external recovery controls and
  four keyed DBG10 fallbacks remain available.
- ✅ Public diagrams use one board per inner image. The complete numbered
  163-body projection is retained only as machine-review evidence.
- ✅ The main public mock-up places the direct turned-over view of each PCB
  below its matching exterior; antenna silk passes body/cable/U214/display/fastener checks.

### 5. Exact current blocker

- ✅ Official Sinopine `SP331R-MANUAL-V1.0` controls `28.7 × 23.1 mm` nominal
  XY, `2.54 mm` contact pitch and `1.4 mm` edge offset for SP331RX.
- ▶ Obtain either an AKK-native K331 package or formal K331↔SP331RX production
  equivalence, plus maximum Z/tolerances, recommended land/paste and
  packaging/soldering/reflow data.
- This same evidence lets H5 submit the selected genuine-AKK/JLCPCB Consigned
  Parts route and H6 perform final Gerber/BOM/CPL DFM.
- AWM666V remains a controlled but materially degraded seven-channel fallback;
  it is not an automatic replacement.

## Complete hardware path

| Phase | Status | Result | Exit criterion |
|---|---|---|---|
| H0 · Requirements and functional architecture | ✅ [R2 reviewed](h0-r2-functional-architecture.md) | Product functions, owners, transports, safety and working pin budgets | Every function has one owner and all working budgets close |
| **H1 · Physical product design** | **▶ Current · `H1-R2.19`** | Exterior, separate inner faces, sections, exact bodies, RF locality, service access and power envelope | No body/fastener/silkscreen/antenna/accessory/cross-board collision; exact MPN or controlled reserve for every body; mock-up accepted |
| H2 · Production ECAD schematic | ⏳ Waiting for H1 | Exact R2 symbols, contacts, nets, values, protection and footprints | ERC-clean sheets and machine-readable HW↔FW contract |
| H3 · Virtual electrical verification | ⏳ Waiting for H2 | Complete power, digital, RF, audio, timing, thermal and fault simulation | Every legal state and transition passes before fabrication |
| H4 · Joined pre-layout gate | ⏳ Waiting for H3 and firmware R2 evidence | One current mechanics/ECAD/electrical/firmware review | No virtual blocker; each physical residual owns a test |
| H5 · Component and factory evidence | ⏳ Waiting for H4 | Exact current factory map and controlled external routes | Every BOM line has a current factory route without silent substitution |
| H6 · KiCad placement and routing | 🔒 Waiting for H5 | Two routed boards and accepted fabrication package | Placement review, DRC, impedance/return paths, RF isolation, thermal copper, test and DFM pass |
| H7 · Prototype fabrication and bring-up | 🔒 Waiting for H6, firmware execution and order approval | Small prototype lot and retained bring-up log | Rails, programming/recovery, UI, storage, audio, radios and expansion pass smoke tests |
| H8 · Physical qualification | 🔒 Waiting for H7 | HIL, RF, thermal, power, safety and endurance evidence | Concurrent nRF modes, quiet interfaces, coexistence, VNA, watchdog and single-fault tests pass |
| H9 · Manufacturing release | 🔒 Waiting for H8 and firmware F11 | Reproducible manufacturing/test package paired with released firmware | Zero blocker and matching hardware/firmware release tags |

## Advancement rules

1. Fix a mismatch in its source artifact and regenerate every downstream view.
2. Do not silently remove an unexpected feature; first check for a missing requirement.
3. Accept a low-cost improvement automatically only when product behaviour does not change.
4. Verify every exact production MPN on the current JLCPCB Standard PCBA surface at selection, architecture freeze and immediately before order.
5. RF transmission and dangerous tests run only on owned loads, with owner authorization or inside an isolated laboratory.
6. Emulation does not replace bring-up, but H7 fabrication cannot be the first execution of the firmware.

## Next action

Close the narrowed K331/SP331RX production-identity and assembly input, regenerate the same H1
views and ask the user to accept the complete mock-up. H2 can start only after
that H1 review. KiCad routing, quoting and every order remain blocked.
