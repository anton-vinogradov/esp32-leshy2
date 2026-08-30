# H2-R2.1.5 · Production schematic result

[Русский](h2-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Schematics](schematics.md)

**Status:** ✅ reviewed on 31 August 2026. H2 now supplies the complete logical
R2 production schematic and a synchronized hardware/firmware boundary. It does
not authorize PCB placement, routing, purchasing or fabrication.

## Result

| Evidence | Reviewed result |
|---|---:|
| Native projects / sheet graph | 3 / 23 |
| Compute domains | 6 |
| Exact MPN groups / product positions | 242 / 1,197 |
| Board groups / explicit non-PCBA groups | 237 / 5 |
| Fitted positions / physical pins | 1,187 / 4,327 |
| Canonical nets | 827 |
| Connected logical endpoints / explicit NCs | 4,063 / 260 |
| Controller-pin rows | 173 |
| Cross-project / cross-sheet nets | 50 / 233 |
| KiCad ERC | 0 errors / 0 warnings in all 3 projects |

The three native roots are `LESHY2-UI-R2`, `LESHY2-RF-R2` and
`L2-DISP-ADP-001-B`. Every fitted board position has an exact symbol and
footprint identity. Every logical contact resolves to a canonical net or an
explicit no-connect. Every cross-project signal crosses a registered connector
boundary; no accidental RF or private local bus crosses M1.

## Hardware/firmware boundary

The machine reconciliation covers all six compute domains, the exact 173-row
controller map, 50 cross-project nets and 233 cross-sheet nets. Fourteen named
aliases are deliberate conditioned or multiplexed boundaries, not silent name
mismatches. Firmware imports the current H2 contract fail-closed and its R2 H2
sync gate is open.

## What H2 does not prove

- PCB placement, copper routing, return paths, controlled impedance or final DRC;
- real-part, connector and factory evidence assigned to H5;
- routed thermal, RF, SI, mechanical and enclosure behavior assigned to H6;
- physical bring-up and HIL evidence assigned to H7/H8.

These are downstream gates, not omissions from the production schematic.
Exactly one assembled prototype remains blocked until H3, H4, H5, H6 and the
firmware first-spin gate pass against one immutable candidate.

## Evidence

- [Native KiCad result](h2-r2-native-kicad.md)
- [Exact instance ledger](h2-r2-instance-ledger.md)
- [Net reconciliation](h2-r2-net-ledger.md)
- [Current schematics and interfaces](schematics.md)
- [`H2-R2-native-kicad-projects.json`](../hardware/ecad/generated/H2-R2-native-kicad-projects.json)
- [`H2-R2-hwfw-contract.json`](../hardware/ecad/generated/H2-R2-hwfw-contract.json)
- [`H2-R2-interboard-m1.json`](../hardware/ecad/generated/H2-R2-interboard-m1.json)

## Historical boundary

The former four-project, single-RP R1 H2 package remains reproducible historical
evidence. It is superseded by this result and is forbidden as R2 build authority.
