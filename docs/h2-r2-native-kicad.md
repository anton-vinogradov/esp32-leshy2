# H2-R2.1.3 · native R2 KiCad schematics

**Passed on 31 August 2026.** The current R2 architecture now exists as two
native KiCad 10 schematic projects generated from the exact component, contact,
instance and net authorities. The retained single-RP R1 projects are not read by
the generator.

| Result | Value |
|---|---:|
| Native projects / project-graph sheets | 2 / 22 |
| Populated logical sheets | 18 |
| Fitted symbol instances | 1,183 |
| Controlled physical symbol pins | 4,243 |
| Connected / explicit no-connect pins | 4,006 / 237 |
| Canonical nets | 816 |
| KiCad ERC errors / warnings | 0 / 0 |
| PCB, placement or routing files | 0 |

The projects are:

- [`LESHY2-UI-R2`](../hardware/ecad/kicad/LESHY2-UI-R2/) — S3 UI/display,
  C5, Hub RP, three complete nRF24 islands, storage and front safety;
- [`LESHY2-RF-R2`](../hardware/ecad/kicad/LESHY2-RF-R2/) — RF RP, power,
  CC1101, VHF/UHF, broadcast/Airband, audio, expansion and TX evidence.

The exact 50-contact display tail terminates directly in
`FH34SRJ-50S-0.5SH(50)` on `LESHY2-UI-R2`; there is no adapter-PCB project.

## Airband closure carried into the schematic

The receive-only 118–137 MHz path is no longer a block-diagram placeholder.
It contains the exact stock-backed H2 nominal parts, the complete LC tuning
network, `PGA-103+`, `LT5560EDD#TRPBF`, official `WBC1-1TLC` / `WBC16-1TLC`
transformers and `SI5351A-B-GTR`. Paired `HMC544AETR` switches isolate both
ends of the converted path so the inactive chain cannot load ordinary FM/SW.
The LO uses private RF-RP GPIO28/29 PIO-I²C pull-ups powered from
`3V3_AIR_SWITCHED`, eliminating an off-domain back-power path. Reset defaults
remain fail-off and fail-direct.

The exact LC values are the nominal H2 fitted state, not the production filter
freeze. The updated tolerance/Q sweep records 3.10 dB nominal worst-passband
loss but 4.67 dB stressed loss and insufficient stressed rejection at 155 and
180 MHz. H3 must retune and prove that network before H6 routed extraction.

## What this authorizes

This checkpoint authorizes native logical schematics only. It creates no PCB,
placement, routing, fabrication output or order. Cross-sheet reconciliation
passed in the [reviewed H2-R2.1.5 result](h2-acceptance.md); H3 now freezes the
same machine-readable hardware/firmware boundary.

[Generated project manifest](../hardware/ecad/generated/H2-R2-native-kicad-projects.json) ·
[native net ledger](h2-r2-net-ledger.md) ·
[roadmap](roadmap.md)
