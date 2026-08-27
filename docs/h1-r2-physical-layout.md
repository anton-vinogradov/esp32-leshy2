# H1-R2.6 · physical re-layout

This is the current verified H1 result, not a decision diary and not authorization to start KiCad.

The second Hub RP, Airband active bodies, an expanded 24 × 11 mm tuning cell for its filter, the FPV video decoder and a replaceable bay for the leading serial AKK K331 candidate are placed in the accepted 75 × 150 mm coordinate system. The reserve is not promoted to a fixed body before AKK-controlled dimensions exist.

![H1-R2 inner placement](images/h1-r2-inner-placement.svg)

![H1-R2 MMCX placement and service proof](images/h1-r2-mmcx-service.svg)

## Already verified

- Same-face body collisions: `0`.
- Intentional opposing XY projections: `26`; minimum Z clearance is `2.44 mm` against `0.70 mm` required.
- The K331 reserve fits without changing the PCB outline or battery/U214 exterior zones; functional pin fit is accepted while physical dimensions remain open.
- The exact linear TBS5G8MMCXA antenna mates with the distinct MMCX; K331 ANT IN reaches it over one direct 50-ohm PCB trace without U.FL.
- Corrected `DL-MMCX-KWE-90` geometry keeps 3.6 mm of body on the RF PCB and projects only the 3.0-mm barrel beyond the right edge; its pins enter the interboard gap by a nominal 1.2 mm and the tail keepout meets no opposing body.
- The side wall now has a 4.5-mm minimum free aperture and the plug a clear Ø12×20-mm exterior service corridor. H5 later verifies the received mating pair, final wall tolerance, retention and cable strain.
- Hub remains on the UI board beside storage/audio/broadcast; the FPV RF module and decoder remain together on the RF board.
- Airband now has a [nominally passing but stress-open synthesis](h1-airband-filter.md); the enlarged cell carries alternate/DNP pads, H3 checks bounded estimates, H6 routed extraction before order and H8 the final VNA state.

## Exact factory parts

| Role | Exact MPN | JLCPCB | Selection status | Current route |
|---|---|---|---|---|
| Hub RP2354B factory assembly cross-reference | `SC1512-A4` | [`C39843328`](https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328) | working selection; A4 marking remains an incoming gate | LCSC/JLC supply surface showed 3,682 pieces, MOQ 1, USD 1.6225 at quantity 1 |
| analog composite-video decoder | `TVP5150AM1PBS` | [`C3824301`](https://jlcpcb.com/partdetail/TexasInstruments-TVP5150AM1PBS/C3824301) | accepted for the working placement | 62 pieces, MOQ 1, USD 6.4081 at quantity 1 |
| 24-channel 5.8-GHz analog-FPV receiver module | `K331` | [`None`](https://www.akktek.com/products/vtx-modules/akk-k331.html) | accepted functional and pin-fit candidate; physical body and factory-placement route remain open | manufacturer store showed in stock at USD 29.99; exact JLCPCB searches for AKK K331, RX5808 and RTC6715 returned zero results |
| side-facing 5.8-GHz user connector | `DL-MMCX-KWE-90` | [`C2894793`](https://jlcpcb.com/partdetail/DreamLNK-DL_MMCX_KWE90/C2894793) | accepted physical definition, corrected edge placement and machine-proved solder-tail/side-service keepouts | 25,383 pieces, MOQ 1, USD 0.9077 at quantity 1 |
| FPV decoder 1.8-V rail | `TPS7A2018PDBVR` | [`C963430`](https://jlcpcb.com/partdetail/TexasInstruments-TPS7A2018PDBVR/C963430) | accepted for the working placement | 2,225 pieces, MOQ/multiple 5, USD 0.2413 at quantity 5; JLC identifies Economic and Standard SMT assembly |
| 3V3_MAIN 6-A synchronous buck with protected diagnostic PG | `TPS566231PRQFR` | [`C3190178`](https://jlcpcb.com/partdetail/TexasInstruments-TPS566231PRQFR/C3190178) | accepted H1-R2 working selection; dynamic and thermal closure remains H3 | 112 pieces, MOQ 1, USD 1.0478 at quantity 1 |
| 3V3_MAIN 2.2-uH high-current shielded inductor | `PSPMAA0605H-2R2M-ANP` | [`C2983088`](https://jlcpcb.com/partdetail/PRODTech-PSPMAA0605H2R2MANP/C2983088) | accepted H1-R2 working selection; 10-A RMS and 15-A saturation ratings | 627 pieces, MOQ 1, USD 0.1735 at quantity 1 |
| 3V3_MAIN eFuse threshold resistor | `RC0402FR-071K18L` | [`C273709`](https://jlcpcb.com/partdetail/YAGEO-RC0402FR071K18L/C273709) | accepted H1-R2 working selection; 4.870-A nominal and 4.340-A guaranteed-low threshold | 5,864 pieces, MOQ 1, USD 0.0025 at quantity 1 |
| TPS566231P VCC decoupling capacitor | `CL10B105KO8NNNC` | [`C59782`](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL10B105KO8NNNC/C59782) | accepted H1-R2 working selection | 631,719 pieces, MOQ 1, USD 0.0210 at quantity 1 |
| TPS566231P bootstrap and local high-frequency decoupling capacitor | `CL05B104KB5NNNC` | [`C960916`](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL05B104KB5NNNC/C960916) | accepted H1-R2 working selection | 754,861 pieces, MOQ 1, USD 0.0093 at quantity 1 |
| 3V3_MAIN input/output bulk capacitor | `GRM32ER71E226KE15L` | [`C21397`](https://jlcpcb.com/partdetail/MurataElectronics-GRM32ER71E226KE15L/C21397) | accepted physical body and working nominal; H3 proves effective capacitance after bias/temperature/tolerance | 116,360 pieces, MOQ 1, USD 0.6222 at quantity 1 |
| TPS566231P serial bootstrap tuning link | `RC0402JR-070RL` | [`C60485`](https://jlcpcb.com/partdetail/YAGEO-RC0402JR070RL/C60485) | accepted fitted 0-ohm default | 4,551,848 pieces, MOQ 1, USD 0.0034 at quantity 1 |

## What still blocks H1

- obtain AKK-controlled maximum dimensions, land pattern and packaging/reflow evidence before replacing the K331 reserve with a fixed body
- obtain a JLCPCB private/global-sourcing response for K331 or retain explicit post-PCBA hand installation
- qualify the supply-independent FXP831.09.0100C FPV fallback on the assembled enclosure and secure stock before relying on its current 16-week backorder route
- regenerate the complete exterior, inner faces and both sections only after the R2 bodies stop moving

> Exact current marker: **H1-R2.6**. H1 remains in progress.
