# H1-R2.28 · finished-device placement

Current physical model of the two 75 × 150 mm PCBs. This is a verifiable H1 result, not authorization to start KiCad: no engineering blocker remains, but the complete mock-up still needs explicit acceptance.

## What the user sees

![Four matched PCB faces](images/h1-r2-four-faces.svg?rev=h1-r2.22-display-flex-up-1)

## Component legend

![Numbered component legend](images/h1-r2-component-legend.svg?rev=h1-r2.22-display-flex-up-1)

[Detailed exterior at full scale](images/h1-r2-external-layout.svg?rev=h1-r2.22-display-flex-up-1)

![External service access](images/h1-r2-service-access.svg?rev=h1-r2.22-display-flex-up-1)

## What is inside

[Front UI/radio PCB · full-scale inner view](images/h1-r2-inner-ui.svg)

[Rear RF/power PCB · full-scale inner view](images/h1-r2-inner-rf.svg)

- Ten main SMA ports are split symmetrically `5 + 5`; every radio path remains on the PCB that carries its connector.
- On the front PCB, five short removable microcoax jumpers connect the radio-source IPEX/U.FL sockets to board U.FL sockets; controlled board-local PCB paths continue from there to SMA.
- The rear PCB has no U.FL or removable RF cable: voice and FM/SW use board-local RF paths, AM/LW uses a separate high-impedance AMI path, and Airband uses the powered conversion branch and selector.
- The separate vertical `FPV RX · 5.8 GHz` MMCX sits below the evenly pitched five-SMA rear row and above U214; its mating right-angle plug and cable run parallel to the PCB.
- All user-facing labels are readable silkscreen; neither inner PCB face carries silkscreen.
- Each outer face prints a stable board role/revision — `UI PCB · R2-EVT1 · REV A` and `RF/PWR PCB · R2-EVT1 · REV A`; the changing H1-R2.xx work marker is never printed on a PCB.
- All three nRF24 islands move to the front PCB with their buffers, safety gate and a dedicated second `TLV1824PWR`.
- A mutually exclusive post-PCBA `K331 / AWM666V` bay remains rear-local while `TVP5150AM1PBS` moves beside S3: M1 carries one 75-ohm CVBS signal, not the 11-line LCD_CAM bus.
- Primary K331 uses a tolerant 14-pad land; the exact seven-channel AWM666V land nests in the same bay. Exactly one module is installed, without an internal U.FL or RF cable.
- FM/SW/AM/LW/Airband, CC1101, both voice paths and audio are rear-local; S3 directly owns i8080-8, camera RX, buttons, encoder and USB.
- The panel is physically turned with its flex toward the antenna edge, as on ESP32-DIV; the adapter occupies the upper inner zone and firmware rotates display output and touch by 180°. The tail stays out of the LED, D-pad and side-key zone.

![True inner sandwich sections](images/h1-r2-inner-sections.svg)

![Rear-face FPV connector proof](images/h1-r2-mmcx-service.svg)

## Generator-verified

- Same-face body collisions: `0`.
- Minimum opposing Z clearance: `2.59 mm` against `0.70 mm` required.
- The FPV reserve is enlarged to `30 × 24 × 8 mm`; C5 DBG10 is relocated beside S3 DBG10 and intersects neither the bay nor adjacent bodies.
- FPV MMCX: the jack body leaves `2.07 mm` to the nearest SMA; the controlled right-angle plug leaves `2.40 mm` to SMA and `4.80 mm` to U214. Ø12 is only a temporary finger-approach zone and remains an H5 ergonomic check.
- GPIO: front RP `46/48` with `2` free; rear RP `45/48` with `3` free. K331 RSSI is officially marked NC.
- M1: all 80 contacts are assigned — 25 signals, 14 main-power, 2 AON, 25 returns and 14 NC reserves.
- M1 mechanics: four 11.00-mm compression stops, two anti-shear datums and independent PCB capture; the connector carries no impact or bending load.
- Antenna silkscreen: the generator proves no overlap with SMA/MMCX bodies, the installed FPV cable, U214, the display or mounting keep-outs.
- The upper display adapter has zero body collisions and 5.10 mm minimum opposing clearance; the second nRF24 board U.FL moves below it with 1.00 mm planar clearance.

## Exact factory parts

| Role | MPN | JLCPCB | Current availability/route |
|---|---|---|---|
| Hub RP2354B factory assembly cross-reference | `SC1512-A4` | [`C39843328`](https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328) | LCSC/JLC supply surface showed 3,682 pieces, MOQ 1, USD 1.6225 at quantity 1 |
| analog composite-video decoder | `TVP5150AM1PBS` | [`C3824301`](https://jlcpcb.com/partdetail/TexasInstruments-TVP5150AM1PBS/C3824301) | 62 pieces, MOQ 1, USD 6.4081 at quantity 1 |
| 24-channel 5.8-GHz analog-FPV receiver module | `K331` | — | manufacturer store showed in stock at USD 29.99; JLCPCB confirmed zero Parts Library/Global Sourcing route and no direct replacement, but accepts a Consigned Parts application before shipment |
| rear-face vertical 5.8-GHz user connector | `73415-2063` | [`C588480`](https://jlcpcb.com/partdetail/Molex-734152063/C588480) | 5,520 pieces (5,506 orderable), MOQ 1, USD 1.9893 at quantity 1; USD 1.7393 at quantity 10 |
| Hub RP independent data-only service USB-C | `USB4105-GF-A` | [`C3020560`](https://jlcpcb.com/partdetail/GlobalConnectorTechnology-USB4105_GF_A/C3020560) | 3,712 pieces, MOQ 1, USD 1.0605 at quantity 1 |
| Hub RP recessed RESET/USB_BOOT side switch | `SKRTLAE010` | [`C110293`](https://jlcpcb.com/partdetail/ALPSALPINE-SKRTLAE010/C110293) | 49,305 pieces, MOQ 1, USD 0.1443 at quantity 1 |
| Hub RP keyed internal DBG10 recovery header | `FTSH-105-01-L-DV-K-P-TR` | [`C2932107`](https://jlcpcb.com/partdetail/Samtec-FTSH_105_01_L_DV_K_PTR/C2932107) | 11,433 pieces, MOQ 1, USD 1.2797 at quantity 1 |
| FPV decoder 1.8-V rail | `TPS7A2018PDBVR` | [`C963430`](https://jlcpcb.com/partdetail/TexasInstruments-TPS7A2018PDBVR/C963430) | 2,225 pieces, MOQ/multiple 5, USD 0.2413 at quantity 5; JLC identifies Economic and Standard SMT assembly |
| 3V3_MAIN 6-A synchronous buck with protected diagnostic PG | `TPS566231PRQFR` | [`C3190178`](https://jlcpcb.com/partdetail/TexasInstruments-TPS566231PRQFR/C3190178) | 112 pieces, MOQ 1, USD 1.0478 at quantity 1 |
| 3V3_MAIN 2.2-uH high-current shielded inductor | `PSPMAA0605H-2R2M-ANP` | [`C2983088`](https://jlcpcb.com/partdetail/PRODTech-PSPMAA0605H2R2MANP/C2983088) | 627 pieces, MOQ 1, USD 0.1735 at quantity 1 |
| 3V3_MAIN eFuse threshold resistor | `RC0402FR-071K18L` | [`C273709`](https://jlcpcb.com/partdetail/YAGEO-RC0402FR071K18L/C273709) | 5,864 pieces, MOQ 1, USD 0.0025 at quantity 1 |
| TPS566231P VCC decoupling capacitor | `CL10B105KO8NNNC` | [`C59782`](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL10B105KO8NNNC/C59782) | 631,719 pieces, MOQ 1, USD 0.0210 at quantity 1 |
| TPS566231P bootstrap and local high-frequency decoupling capacitor | `CL05B104KB5NNNC` | [`C960916`](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL05B104KB5NNNC/C960916) | 754,861 pieces, MOQ 1, USD 0.0093 at quantity 1 |
| 3V3_MAIN input/output bulk capacitor | `GRM32ER71E226KE15L` | [`C21397`](https://jlcpcb.com/partdetail/MurataElectronics-GRM32ER71E226KE15L/C21397) | 116,360 pieces, MOQ 1, USD 0.6222 at quantity 1 |
| TPS566231P serial bootstrap tuning link | `RC0402JR-070RL` | [`C60485`](https://jlcpcb.com/partdetail/YAGEO-RC0402JR070RL/C60485) | 4,551,848 pieces, MOQ 1, USD 0.0034 at quantity 1 |

## Final H1 acceptance

- No engineering blockers remain.
- review and explicitly accept the generated complete R2 exterior, both true-view inner faces and four real section planes before closing H1

> Exact current marker: **H1-R2.28**. H1 remains in progress.
