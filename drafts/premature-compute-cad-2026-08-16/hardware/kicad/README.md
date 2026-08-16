# Leshy2 project-local KiCad libraries

- Статус: **Проведено ревью library snapshot; не является готовой схемой**
- Решение: DEC-0030, вариант IMP-0025/A
- Scope: critical compute rows C-001…005
- Tool baseline: KiCad 10.0.5

This directory is the canonical project-local CAD-library root. It intentionally
contains no product schematic or PCB: topology is a later stage-6 contract and
the first canonical ERC input is created at stage 8.

## Exact target bindings

| Row | Symbol | Footprint | Important exactness |
|---|---|---|---|
| C-001 | ESP32-S3-WROOM-1U-N16R2 | same | 1U external antenna, 16 MB flash, 2 MB PSRAM |
| C-002 | ESP32-C5-WROOM-1U-N8R8 | same | v1.2+ production floor is procurement evidence; pin 19 is NC for N8R8 PSRAM |
| C-003 | RP2354A-A4 | RP2354A-A4-QFN60 | exact A4/SC1511-A4 target; inherited pin body is vendored as RP2350A |
| C-004 | TCA9535PWR | same | TI PWR/TSSOP-24 exact package |
| C-005 | ABM8-272-T3-12MHz | ABM8-272-T3 | 12 MHz, CL 10 pF, pins 2/4 ground |

RP2350A.kicad_sym is a support-only inheritance body for RP2354A-A4; it is
not an accepted alternate target.

## Use

Create the future KiCad project in this directory or copy/link the two library
tables into its project root. Both tables resolve assets through
${KIPRJMOD} and therefore do not depend on workstation-global symbol or
footprint paths.

Run the reproducibility gate from the hardware repository root:

    python3 hardware/kicad/tools/validate_compute_libraries.py

The validator parses KiCad s-expressions, checks exact symbol properties,
pin-number/name/type signatures, pad-number/geometry signatures, file hashes,
local bindings, C5 N8R8 pin 19 and ABM8 ground pins. Any intentional update
requires a reviewed source/provenance diff and refreshed manifest values.

## Qualification boundary

- The C5/S3 module geometry comes from the pinned Espressif library and is
  independently compared with the current manufacturer datasheet.
- RP/TCA geometry comes from pinned canonical KiCad libraries.
- Abracon drawing 456603 Rev B defines the exact terminal envelope but does not
  publish a separate recommended PCB land pattern. The local ABM8 footprint
  therefore uses the pinned KiCad ABM8G-compatible land pattern after package
  comparison; 1:1 print, stencil and assembly-yield evidence remain mandatory
  before fabrication release.
- Source footprints retain optional upstream 3D-model references. STEP/MCAD
  vendoring and enclosure collision proof are a later mechanical gate and are
  not silently counted as complete here.
- File and geometry checks do not replace 1:1 overlay, ERC, DRC, paste review,
  antenna/thermal placement or prototype assembly qualification.
