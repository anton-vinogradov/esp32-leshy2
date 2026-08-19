# FND-0102 — Si4732 SOIC-16 contact map was shifted

- Статус: **Исправлено; проведено ревью**
- Scope: exact-device registry and every generated Si4732 physical contact
- Review: [`REV-0005BB`](../reviews/REV-0005BB-si4732-soic16-pin-map-correction.md)

## Несоответствие

The machine-readable Si4732-A10 record had incorrectly assigned
the ordered contact names to physical contacts 1 through 16. It claimed
`FMI/RFGND/AMI = 1/2/3` and shifted the remaining functions even though the
official top-view SOIC-16 package drawing states:

| Physical contact | Exact function | Physical contact | Exact function |
|---:|---|---:|---|
| 1 | `LOUT/DFS` | 16 | `ROUT/DOUT` |
| 2 | `GPO3/DCLK` | 15 | `GND` |
| 3 | `GPO2/INTB` | 14 | `VDD` |
| 4 | `GPO1` | 13 | `RCLK` |
| 5 | `NC` | 12 | `SDIO` |
| 6 | `FMI` | 11 | `SCLK` |
| 7 | `RFGND` | 10 | `SENB` |
| 8 | `AMI` | 9 | `RST` |

This was a provenance/transcription failure, not a lack of exposed contacts.
The legacy tsCircuit audio source had already used the correct physical map,
but the newer architecture registry and documents contradicted it. No KiCad
work had been authorized, so no production schematic or PCB must be reworked.

## Исправление

- replaced the complete 16-contact map from the manufacturer package drawing;
- corrected FMI/AMI/RFGND physical labels in the machine route descriptions,
  principled diagram, receiver architecture, decision and firmware contract;
- kept the functional assignment `FM/SW → FMI` and `AM/LW → AMI`, which is
  separately explicit in the exact Si4732-A10 block diagram;
- added a regression assertion for all 16 contacts rather than only RF pins;
- amended earlier reviews that had incorrectly marked the shifted map as pass.

Symbolic route endpoints such as `receiver.FMI`, `receiver.SDIO` and
`receiver.ROUT_DOUT` did not change. The correction changes their physical-pad
resolution and prevents a later schematic from connecting those nets to the
wrong package contacts.

## Root cause and prevention

The PDF text-extraction order was mistaken for physical pin order. For
package-level decisions, the rendered package drawing or manufacturer pin table
must now be visually checked; extracted text is only a search aid. Regression
tests must lock the whole selected-package map when one device record fans out
to multiple architecture stages.

## Source

- [Skyworks Si4732-A10 data short, package drawing and functional block diagram](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
