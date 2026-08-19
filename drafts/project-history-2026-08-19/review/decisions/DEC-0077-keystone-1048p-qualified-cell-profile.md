# DEC-0077 — Keystone 1048P and qualified protected-cell profile

- Статус: **Принято; проведено ревью бумажного mechanical/thermal contract**
- Дата: 2026-08-18
- Owner confirmation: accepted after explicit compatibility/cost comparison
- Analysis: [`PWR-0016`](../architecture/PWR-0016-keystone-1048p-holder-and-ntc-coupling.md)
- Corrected finding: [`FND-0081`](../findings/FND-0081-holder-contact-and-thermal-proof-gap.md)
- Propagation review: [`REV-0005AH`](../reviews/REV-0005AH-battery-holder-and-ntc-coupling.md)

## Decision

1. Accept exact `Keystone Electronics 1048P` as prototype holder and the
   production-reference geometry for two individually replaceable cells.
2. The base product supports only exact qualified protected button-top 18650
   MPNs. Raw flat-top cells are unsupported; electrical admission does not
   claim to authenticate an arbitrary cell.
3. The four holder contacts remain independent. The PCB alone creates the 2S
   midpoint and retains one slot fuse per positive contact.
4. Manufacturer functional polarity is accepted at paper level, but a real
   specimen must pass contact-isolation, polarity-orientation and insertion
   tests before footprint/schematic freeze because the drawing does not number
   the terminals.
5. `PACK_NTC0` and `PACK_NTC1` each contact their own cell through insulated
   compliant tongues. The single independent BQ25798 TS sensor has two indexed
   possible tongue sites and is populated only on the thermally worst slot
   established by placement analysis and confirmed by HIL.
6. Cells are normally sourced/shipped as a separate qualified regional kit,
   not bundled through ordinary PCBA/antenna factory logistics.
7. A custom molded compartment remains an I8 cost-down candidate only after it
   proves complete functional and safety equivalence. An ordinary
   non-polarized holder is not an allowed silent substitute.

## Consequence

Mechanical reverse insertion is now blocked by an exact reference device
before the supervised electrical path. The exact `39.8 × 86.0 mm` projection
fits the current `75 × 150 mm` board and leaves the accepted U214 dock a
`9.719 mm` plan gap and `5.59 mm` installed-depth reserve on paper. The holder
adds roughly `$8.57` at 100-piece visible distributor pricing; this cost is
accepted for the safe reference design and remains a later equivalent-only
cost-down target.

This is not final cell, enclosure, thermal-stack or KiCad authorization.
