# H1-R2.1 · physical re-layout

This is the current verified H1 result, not a decision diary and not authorization to start KiCad.

The second Hub RP, Airband active bodies, FPV video decoder and a replaceable bay for its still-unselected 5.8-GHz receiver are placed in the accepted 75 × 150 mm coordinate system.

![H1-R2 inner placement](images/h1-r2-inner-placement.svg)

## Already verified

- Same-face body collisions: `0`.
- Intentional opposing XY projections: `26`; minimum Z clearance is `2.44 mm` against `0.70 mm` required.
- The large FPV receiver bay fits without changing the PCB outline or battery/U214 exterior zones.
- Hub remains on the UI board beside storage/audio/broadcast; the FPV RF module and decoder remain together on the RF board.

## Exact factory parts

| Role | Exact MPN | JLCPCB | Selection status | Current route |
|---|---|---|---|---|
| Hub RP2354B factory assembly cross-reference | `SC1512-A4` | [`C39843328`](https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328) | working selection; A4 marking remains an incoming gate | LCSC/JLC supply surface showed 3,682 pieces, MOQ 1, USD 1.6225 at quantity 1 |
| analog composite-video decoder | `TVP5150AM1PBS` | [`C3824301`](https://jlcpcb.com/partdetail/TexasInstruments-TVP5150AM1PBS/C3824301) | accepted for the working placement | 62 pieces, MOQ 1, USD 6.4081 at quantity 1 |
| side-facing 5.8-GHz user connector | `DL-MMCX-KWE-90` | [`C2894793`](https://jlcpcb.com/partdetail/DreamLNK-DL_MMCX_KWE90/C2894793) | working selection; exact mechanical drawing remains open | 22,687 pieces, MOQ 1, USD 0.9032 at quantity 1 |
| FPV decoder 1.8-V rail | `TPS7A2018PDBVR` | [`C963430`](https://jlcpcb.com/partdetail/TexasInstruments-TPS7A2018PDBVR/C963430) | not accepted | JLC assembly card and LCSC stock exist; live JLC stock/MOQ/price recheck remains required before acceptance |

## What still blocks H1

- select an in-production exact serial 5.8-GHz analog receiver with a live purchase route; generic RX5808 and discontinued MM238R-MCU are not accepted
- close the exact MMCX drawing, hole pattern, hand-assembly accessibility and enclosure side opening
- live-check JLC stock, MOQ and price for the 1.8-V LDO before accepting it
- synthesize the Airband input and IF filters from factory-stock serial passives and prove the 87-106-MHz image rejection mask
- rebuild the complete six-domain rail and thermal matrix
- regenerate the complete exterior, inner faces and both sections only after the R2 bodies stop moving

> Exact current marker: **H1-R2.1**. H1 remains in progress.
