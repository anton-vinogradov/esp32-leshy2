# Third-party CAD attribution

The files under hardware/kicad/lib/ are a reviewed, modified collection of
CAD-library material. This collection is distributed under **CC BY-SA 4.0 with
the KiCad library exception** reproduced in
[KICAD-LIBRARY-LICENSE.md](KICAD-LIBRARY-LICENSE.md).

## Espressif Systems

- Upstream: <https://github.com/espressif/kicad-libraries>
- Pinned commit: dd76561812ab300351234ba6e0ec1295641796f0
- Imported material: ESP32-C5-WROOM-1U and ESP32-S3-WROOM-1U symbols and
  footprints.
- Local modifications: exact Leshy2 MPN/variant names and footprint bindings;
  S3 external-antenna description; C5 N8R8 pin 19 marked unavailable because
  in-package PSRAM consumes SPICS1; C5 filter typo corrected.

Copyright and attribution remain with Espressif Systems and the upstream
contributors.

## KiCad library project

- Symbols upstream: <https://gitlab.com/kicad/libraries/kicad-symbols>
- Pinned symbols commit: f0811ce7f108212a1305fce0dc1d164749cdf8c4
- Footprints upstream: <https://gitlab.com/kicad/libraries/kicad-footprints>
- Pinned footprints commit: c75e8f3ddc65439a5140e7c5b8c6e5b40be0f90e
- Imported material: RP2350A/RP2354A, TCA9535PWR and Crystal_GND24 symbols;
  RP2354A QFN60, TSSOP-24 and Abracon ABM8G-compatible footprint geometry.
- Local modifications: exact Leshy2 MPN names, repository-local bindings and
  descriptions. The ABM8 land pattern retains the upstream ABM8G pad geometry
  after comparison with the ABM8-272-T3 terminal envelope in Abracon drawing
  456603 Rev B.

Copyright and attribution remain with the KiCad library contributors.

The source file hashes, datasheet hashes and exact derived artifact hashes are
recorded in
[critical-compute-libraries.json](../provenance/critical-compute-libraries.json).
