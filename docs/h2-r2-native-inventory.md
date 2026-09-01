# H2-R2 native ECAD inventory

[Русский](h2-r2-native-inventory.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

**`H2-R2.1.1` reviewed on 2026-08-30.** This is the clean input boundary for
the new R2 production schematic. It describes the finished device, not the
history of earlier design decisions.

## Result

| Inventory | Reviewed result |
|---|---|
| Native projects | `LESHY2-UI-R2`, `LESHY2-RF-R2` |
| Functional sheets | 22 unique sheets with one owner for every responsibility |
| Compute domains | 6: S3, C5, front Hub RP, rear RF RP, Pack and Safety |
| Exact component groups | 238 MPN groups, 1,193 positions per finished product |
| External antenna kit | 8 exact groups, 12 separately identified antennas/pods |
| Open pre-ECAD prerequisite | 0 |
| Native symbols/nets created | 0 / 0 |

The front project owns S3, C5, Hub RP, display/touch, microSD, controls and all
three complete nRF24 islands. The rear project owns RF RP, power, Pack/Safety,
CC1101, VHF/UHF voice, broadcast/Airband, audio and the U214/U219/M5 host
interfaces. M1 appears only as two named endpoints of the exact 80-contact
contract.

The historical custom `LESHY2-LORA-CAP-01` board is not a native R2 project.
The product supports series-produced U214/U219 Caps through its rear host
receptacle; it does not manufacture a separate LoRa-Cap PCB.

## Exact delta after the H1 cost inventory

The accepted H1 inventory has 210 grouped BOM lines and 1,094 fitted base
placements. The reviewed Pack/Safety boundary, exact Airband conversion branch
and direct display ZIF bring the electrical inventory to 238 exact groups and
1,193 positions. Display, optional U214,
removable cells and encoder knob retain explicit non-PCBA/final-assembly
dispositions.

## Machine evidence

- [Source/sheet contract](../hardware/ecad/h2-r2-native-inventory-contract.json)
- [Generated component inventory](../hardware/ecad/generated/H2-R2-native-inventory.json)
- [Electrical prerequisites](h2-r2-electrical-prerequisites.md)
- [Reviewed H1 physical result](h1-r2-acceptance.md)

Every source is hash-bound. Historical stock evidence is not presented as live
stock: every selected MPN is rechecked on the JLCPCB Standard-PCBA surface at
architecture freeze and immediately before the exact-one order.

## Current boundary

The exact ledger for these 238 groups passed review at
[`H2-R2.1.2`](h2-r2-symbol-footprint-ledger.md), and the downstream
[4,239-endpoint net reconciliation](h2-r2-net-ledger.md) and
[native KiCad generation](h2-r2-native-kicad.md) have passed. Cross-sheet and
HW↔FW reconciliation also passed in [H2-R2.1.5](h2-acceptance.md). H3 now
freezes those inputs; PCB placement, routing, fabrication and ordering remain blocked.
