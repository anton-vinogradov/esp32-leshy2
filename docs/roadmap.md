# Leshy2 hardware roadmap

[Home](../README.md) · [Русский](roadmap.ru.md) ·
[Firmware roadmap](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.md)

> **▶ Current hardware boundary: `H1-R2.21`.** H0 is reviewed. H1 is not.
> No R2 KiCad routing, quote, reservation or order is authorized.

Status reconciled: **28 August 2026**.

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
| Physical design | ▶ [H1-R2.21](h1-r2-physical-layout.md): complete functional islands, `5 + 5` main antenna banks, separate rear FPV MMCX, dual post-PCBA K331/AWM666V bay and stable per-board revision silk |
| Principle diagrams | Current component/bus map, external mock-up, separate readable inner faces, service map, FPV/MMCX proof and power/filter diagrams are published |
| Production ECAD | ⏳ R1 evidence retained; R2 schematic waits for H1 |
| Firmware prerequisite | ✅ firmware F1-R2 reviewed; F2-R2.0 is current on the separate [F0–F11 roadmap](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.md); emulator/dev-board execution must precede H7 fabrication |
| Ordering | 🔒 Prototype order only at H7 after H6 and explicit approval; production only at H9 |

## Current H1 · exact composition

<!-- current-substep: H1-R2.21 -->

**Exact marker: `H1-R2.21`.** This is one physical-design substep, not a closed
H1 report.

### 1. Functional-island placement

- ✅ Front UI/radio PCB: S3, C5, three complete nRF24 islands, front RP,
  microSD and UI-local TVP5150.
- ✅ Rear RF/power PCB: CC1101, VHF/UHF voice, FM/SW/AM/LW/Airband, audio,
  one-of-two K331/AWM666V FPV bay, M5, U214, rear RP, power and safety.
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

- ✅ The mutually exclusive K331/AWM666V receiver bay remains rear-local and TVP5150 becomes UI-local.
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
- ✅ The FPV reserve is enlarged to `30 × 24 × 8 mm`; C5 DBG10 moves beside S3 DBG10.
- ✅ Minimum opposing clearance: `1.05 mm`; required: `0.70 mm`.
- ✅ FPV MMCX body clearance to nearest SMA: `2.07 mm`.
- ✅ Controlled right-angle plug: `2.40 mm` to SMA, `4.80 mm` to U214 and no
  mounting-hole conflict; Ø12 remains a temporary H5 finger-access check.
- ✅ Four independent USB paths, eight recessed external recovery controls and
  four keyed DBG10 fallbacks remain available.
- ✅ Public diagrams use one board per inner image. The complete numbered
  163-body projection is retained only as machine-review evidence.
- ✅ The main public mock-up places the direct turned-over view of each PCB
  below its matching exterior; antenna silk passes body/cable/U214/display/fastener checks.
- ✅ Exterior silk prints `UI PCB · R2-EVT1 · REV A` and
  `RF/PWR PCB · R2-EVT1 · REV A`; the changing H1-R2.xx work marker is never
  printed and PCB REV advances only with released manufacturing-file changes.

### 5. Final H1 acceptance input

- ✅ Primary K331 uses a tolerant 14-pad direct-solder land whose axes come from
  the official SP331RX drawing; exact-drawing AWM666V nests in the same bay as a
  materially degraded seven-channel fallback. Exactly one module is populated.
- ✅ One population-specific 50-ohm branch is completed at the MMCX launch; the
  unused branch is isolated there, with no internal U.FL, cable or live stub.
- ✅ Neither receiver enters the normal PCBA BOM. Actual body, hand soldering,
  Z and durability move to H5/H7; a later manufacturer package can simplify the footprint.
- ▶ Review and explicitly accept the complete exterior, both true-view inner
  faces and the real sandwich sections. This is the only remaining H1 action.

## Complete hardware path

| Phase | Status | Result | Exit criterion |
|---|---|---|---|
| H0 · Requirements and functional architecture | ✅ [R2 reviewed](h0-r2-functional-architecture.md) | Product functions, owners, transports, safety and working pin budgets | Every function has one owner and all working budgets close |
| **H1 · Physical product design** | **▶ Current · `H1-R2.21`** | Exterior, separate inner faces, sections, exact bodies, RF locality, service access and power envelope | No body/fastener/silkscreen/antenna/accessory/cross-board collision; exact MPN or controlled reserve for every body; mock-up accepted |
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

Obtain explicit acceptance of the complete H1 mock-up. H2 can start only after
that H1 review. KiCad routing, quoting and every order remain blocked. If AKK or
Sinopine replies later, simplify only the K331 land without changing the interfaces.
