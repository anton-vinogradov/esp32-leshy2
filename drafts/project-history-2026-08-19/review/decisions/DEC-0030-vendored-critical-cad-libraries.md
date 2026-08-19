# DEC-0030 — repository-vendored critical CAD libraries

- Статус: **Superseded as active work by `DEC-0032`; snapshot archived**
- Дата: 2026-08-16
- Основание: владелец выбрал вариант A в IMP-0025
- Этап: 4 — компоненты и BOM
- Затрагивает: C-001…005, LIB-0001, FND-0036, future KiCad schematic/PCB releases

> The library snapshot was reproducible, but it was created before required
> product-design, optimality, conceptual-placement and architecture gates. It
> is preserved under `drafts/premature-compute-cad-2026-08-16/`; no active
> canonical C-001…005 library exists.

## Решение

1. Exact symbols and footprints for C-001…005 live in the hardware repository
   under hardware/kicad/lib and are resolved only through project-local library
   tables.
2. Every imported asset has a pinned upstream commit/file hash, attribution,
   source-drawing identity and an exact derived hash in the provenance manifest.
3. Automated validation locks complete pin number/name/electrical-type
   signatures, pad numbers/multiplicity/geometry, MPN Value, datasheet and local
   footprint binding. CI runs the same dependency-free gate.
4. Manufacturer or upstream changes never replace the snapshot automatically.
   They arrive as a reviewed diff with refreshed provenance and all affected
   qualification.
5. ESP32-C5-WROOM-1U-N8R8 pin 19 is no-connect because in-package PSRAM consumes
   SPICS1. The generic no-PSRAM GPIO15 presentation is forbidden for this exact
   target.
6. RP2350A in the library is an inheritance-only symbol body required by the
   exact RP2354A-A4 alias; it is not an accepted BOM alternate.
7. ABM8-272-T3 uses the pinned KiCad ABM8G-compatible land geometry after
   comparison with Abracon drawing 456603 Rev B. Because that drawing provides
   terminal dimensions but no separate recommended land pattern, 1:1 print,
   stencil and assembly-yield proof remain fabrication-release gates.
8. Optional 3D models are outside this decision. Their remaining upstream paths
   do not qualify STEP/MCAD or enclosure fit.

## Why this stays open

The decision vendors open CAD data under CC BY-SA 4.0 with the KiCad library
exception and preserves attribution. It does not restrict design, firmware,
owner keys or downstream generated boards, and it does not create a closed
toolchain.

## Boundary

This closes the reproducible library-production method and FND-0036. It does
not grant component Q, create the final schematic, prove ERC/DRC, qualify an
antenna/thermal placement, or close BOM-0002. Those remain later exact
electrical, recovery, assembly and HIL gates.

## Verification

REV-0004E records the five passing rows, KiCad 10.0.5 parser checks, provenance,
licence review and the corrections applied during import.
