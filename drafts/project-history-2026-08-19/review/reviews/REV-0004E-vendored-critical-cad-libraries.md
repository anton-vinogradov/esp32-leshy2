# REV-0004E — vendored critical CAD libraries

- Статус: **Historical snapshot review; superseded as active CAD by `REV-0004H`**
- Дата: 2026-08-16
- Решение: DEC-0030 / IMP-0025-A
- Артефакты: hardware/kicad, LIB-0001
- Finding: FND-0036 closed at CAD-representation level

> The checks remain factual for the archived files, but they no longer grant
> canonical product-library status or authorize schematic work.

## Source and licence checks

| Check | Result |
|---|---|
| Espressif CAD source pinned | commit dd76561812ab300351234ba6e0ec1295641796f0 |
| canonical KiCad symbols pinned | GitLab commit f0811ce7f108212a1305fce0dc1d164749cdf8c4 |
| canonical KiCad footprints pinned | GitLab commit c75e8f3ddc65439a5140e7c5b8c6e5b40be0f90e |
| manufacturer drawings pinned | C5 datasheet v1.2 and Abracon 456603 Rev B with SHA-256 |
| redistribution terms retained | CC BY-SA 4.0 plus KiCad library exception and NOTICE |
| obsolete GitHub KiCad mirror avoided | yes; its default branch was dated 2020 and was not imported |
| hardware EN/RU current-state propagated | yes |
| firmware ARC-0001 and EN/RU current-state propagated | yes; firmware consumes exact manifest identities and does not duplicate CAD |
| target README change required | no; exact accepted product identities were already correct and this decision changes artifact production, not product scope |

## Artifact checks

| Row | Exact binding | Pin set | Numbered pads | Structural/hash gate |
|---|---|---:|---:|---|
| C-001 | ESP32-S3-WROOM-1U-N16R2 → same footprint | 1…41 | 49 occurrences, 1…41 | pass |
| C-002 | ESP32-C5-WROOM-1U-N8R8 → same footprint | 1…32 | 40 occurrences, 1…32 | pass |
| C-003 | RP2354A-A4 → RP2354A-A4-QFN60 | inherited 1…61 | 61, 1…61 | pass |
| C-004 | TCA9535PWR → same footprint | 1…24 | 24, 1…24 | pass |
| C-005 | ABM8-272-T3-12MHz → ABM8-272-T3 | 1…4 | 4, 1…4 | pass |

The repository validator reported PASS for all five rows. KiCad 10.0.5
successfully parsed and force-resaved all six symbol files, including the
RP2350A inheritance body, and all five footprints into temporary output.

## Corrections made during import

| Source mismatch | Correction | Consequence |
|---|---|---|
| generic C5 symbol exposed pin 19 as GPIO15 | exact N8R8 symbol marks NC_PSRAM_SPICS1 as no-connect | prevents assignment to a pin consumed by in-package PSRAM |
| C5 symbol footprint filter named ESP32-C6 | corrected to the exact C5 project footprint | no wrong-family filter result |
| generic S3 description said onboard PCB antenna | exact 1U alias says external antenna connector | identity now matches 1U |
| generic CAD names did not carry memory/stepping target | exact project Value/bindings and manifest added | BOM identity cannot drift with shared geometry |
| ABM8G geometry was merely similar-name evidence | compared against ABM8-272 terminal envelope and renamed with explicit qualification boundary | no claim of a nonexistent manufacturer land-pattern recommendation |

These changes implement the accepted exact target; they do not add a product
function or remove an owner-approved capability.

## Remaining gates

- component electrical/reset/current/thermal and recovery contracts;
- exact passives and oscillator startup/temperature/EMI proof;
- 1:1 footprint overlays, stencil/paste and assembly-yield evidence;
- antenna placement, STEP/MCAD and enclosure collision proof;
- canonical stage-8 schematic, ERC, PCB, DRC and fabrication review.

Result: the project-local critical library snapshot receives **Проведено
ревью**. No C-001…005 component receives final Q from this substep alone.
