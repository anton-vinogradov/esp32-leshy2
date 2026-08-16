# LIB-0001 — compute CAD symbol/footprint audit

- Статус: **Проведено ревью; DEC-0030/A реализовано**
- Дата snapshot: 2026-08-16
- Tool snapshot: KiCad `10.0.5`; installed official KiCad 10 libraries
- Пререквизиты: `BOM-0002`, `DEC-0028/0029`, `PIN-0002`
- Finding: [`FND-0036`](../findings/FND-0036-current-cad-cannot-represent-target-compute.md)
- Decision: [`DEC-0030`](../decisions/DEC-0030-vendored-critical-cad-libraries.md)
- Reviews: [`REV-0004D`](../reviews/REV-0004D-compute-cad-library-audit.md),
  [`REV-0004E`](../reviews/REV-0004E-vendored-critical-cad-libraries.md)

## Stage boundary

Stage 4 must identify exact symbols, footprints, source drawings, metadata and validation rules. It must not pretend that a final product schematic already exists: electrical topology is specified in stage 6 and implemented/ERC-checked in stage 8. A library artifact can therefore close its identity/geometry contract now while schematic connectivity and PCB fabrication remain later gates.

## Installed-library audit

| Row | KiCad 10.0.5 evidence | Fit to exact target | Required correction |
|---|---|---|---|
| `C-001` S3 N16R2 | symbol `RF_Module:ESP32-S3-WROOM-1` exists and defaults to PCB-antenna footprint; exact `RF_Module:ESP32-S3-WROOM-1U` footprint exists | pin body is reusable, but default symbol identity/footprint is not exact `1U-N16R2` | exact project symbol/alias must bind the `1U` footprint and carry MPN/memory/datasheet fields; pad/EP/keep-out comparison remains required |
| `C-002` C5 N8R8 ≥v1.2 | no `ESP32-C5-WROOM-1U` symbol or footprint found in installed official symbol/footprint trees | fail | repository-local symbol and footprint derived from current Espressif module datasheet are mandatory; metadata must require v1.2/`MD`, not encode revision in the generic MPN |
| `C-003` RP2354A A4 | exact `MCU_RaspberryPi:RP2354A` exists and binds `Package_DFN_QFN:QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm` | geometric identity available; symbol value alone does not enforce A4/order code | project metadata must enforce `SC1511-A4`/packaging-equivalent A4 and record exposed-pad/paste/assembly validation |
| `C-004` TCA9535PWR | exact `Interface_Expansion:TCA9535PWR` binds `Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm` | exact package identity available | project snapshot still needs MPN/datasheet/provenance and pin-number test |
| `C-005` ABM8-272-T3 | generic crystal symbols and `Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm` footprint exist | not accepted: footprint is named/sourced for `ABM8G`, while target is exact `ABM8-272-T3` | derive/verify exact land pattern from Abracon drawing 456603; carry pins 2/4 ground, 12 MHz, CL/ESR and exact circuit metadata |

Primary sources remain the [S3 module datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), [C5 module datasheet](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html), [RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf), [TCA9535 datasheet](https://www.ti.com/lit/ds/symlink/tca9535.pdf) and exact [ABM8-272-T3 control drawing](https://abracon.com/datasheets/ABM8-272-T3.pdf). CAD-library presence never overrides them.

## Current source audit

The checked-in `hardware/tscircuit` source is explicitly legacy/noncanonical and cannot close the new contract:

| Current artifact | Mismatch |
|---|---|
| `jlcpcb:C3013944` | identifies S3 `N8R2`, not accepted `N16R2`; a shared mechanical footprint does not fix BOM identity |
| `jlcpcb:C51950748` | gives a mutable parts-engine C5 identity but no repository-owned geometry/provenance or v1.2 lot identity |
| no RP2354A component/domain | cannot represent accepted third compute target or its clock/recovery |
| legacy buses/owners/expanders | conflict with `PKG-0001/PIN-0002`; must not be patched into canonical target |
| no checked-in `.kicad_sch` or project library | no self-contained ERC input or reproducible critical-footprint source |

The existing generated PCBs/SVGs remain historical evidence only. Stage 8 will generate the target schematic from the reviewed contracts rather than silently mutate these files.

## Required validation for any library strategy

Each critical symbol/footprint must provide:

- exact manufacturer MPN/variant/stepping fields and primary datasheet URL/revision;
- source type and immutable provenance reference/hash;
- pin-number/name/electrical-type table test against datasheet;
- body, pad, exposed-pad, paste/mask, courtyard and pin-1 checks;
- antenna connector/body/keep-out geometry for both Espressif modules;
- 1:1 print or calibrated overlay review before fabrication;
- KiCad parser/DRC/library checks in the pinned toolchain;
- explicit requalification when manufacturer or CAD-library revision changes.

## Implemented strategy

The owner selected `IMP-0025/A`. The repository now carries exact project
symbols and footprints for all five rows, project-local library tables, pinned
source/drawing hashes, licence attribution, a dependency-free structural/hash
validator and a path-filtered CI job.

Import review also corrected C5 N8R8 pin 19 from generic GPIO15 to no-connect,
the upstream C5→C6 footprint-filter typo, and the S3 1U antenna description.
The ABM8 land geometry is explicitly library-derived and terminal-compatible,
not misrepresented as a manufacturer-published recommended land pattern.

This closes `FND-0036` at CAD-representation level. It does not grant
component `Q`, imply schematic connectivity, or replace the remaining
electrical, 1:1, assembly, ERC/DRC, antenna/thermal and HIL gates.
