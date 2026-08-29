# H1-R2.33 · working target-device placement

The complete verifiable physical model of the two 75 × 150 mm PCBs is ready for visual acceptance. Every body, Cap profile, external U219 antenna volume and copper reserve is registered with no open geometry gate; H1 remains open only until this mock-up is explicitly accepted. H1 acceptance does not itself authorize KiCad routing: the R2 H2 electrical prerequisites listed below must still close first.

## What the user sees

![Four matched PCB faces](images/h1-r2-four-faces.svg?rev=h1-r2.33-layout-ready-1)

## Component legend

![Numbered component legend](images/h1-r2-component-legend.svg?rev=h1-r2.33-layout-ready-1)

[Detailed exterior at full scale](images/h1-r2-external-layout.svg?rev=h1-r2.33-layout-ready-1)

![External service access](images/h1-r2-service-access.svg?rev=h1-r2.33-layout-ready-1)

## What is inside

[Front UI/radio PCB · full-scale inner view](images/h1-r2-inner-ui.svg)

[Rear RF/power PCB · full-scale inner view](images/h1-r2-inner-rf.svg)

- Ten main SMA ports are split symmetrically `5 + 5`; every radio path remains on the PCB that carries its connector.
- The selected GCT `RFPC-SMA31/32-FN-175-A` bodies are not retained by one PCB face: each shell straddles the 1.6-mm board edge, with one RF plus two ground lands on the component face and two more shell-ground lands on the opposite face. This is the same dual-face principle visible in [ESP32-DIV v2](https://github.com/cifertech/ESP32-DIV/tree/9d4d82fe7a12febf554b12e1eca6d434ebe79d39/PCB/v2); a one-face substitute is forbidden.
- On the front PCB, five short removable microcoax jumpers connect the radio-source IPEX/U.FL sockets to board U.FL sockets; controlled board-local PCB paths continue from there to SMA.
- The rear PCB has no U.FL or removable RF cable: voice and FM/SW use board-local RF paths, AM/LW uses a separate high-impedance AMI path, and Airband uses the powered conversion branch and selector.
- The separate vertical `FPV RX · 5.8 GHz` MMCX sits below the evenly pitched five-SMA rear row and above the shared Cap-Bus slot; its mating right-angle plug and cable run parallel to the PCB.
- Exactly one accessory occupies the common slot: U214 (84 × 24 × 15.287 mm) or optional U219 (84 × 24 × 19.7 mm). U219 is 4.413 mm taller, yet remains 1.0 mm below the battery holder and 1.3 mm below the selected rear maximum.
- All user-facing labels are readable silkscreen; neither inner PCB face carries silkscreen.
- Each outer face prints a stable board role/revision — `UI PCB · R2-EVT1 · REV A` and `RF/PWR PCB · R2-EVT1 · REV A`; the changing H1-R2.xx work marker is never printed on a PCB.
- All three nRF24 islands move to the front PCB with their buffers, safety gate and a dedicated second `TLV1824PWR`.
- A mutually exclusive post-PCBA `K331 / AWM666V` bay remains rear-local while `TVP5150AM1PBS` moves beside S3: M1 carries one 75-ohm CVBS signal, not the 11-line LCD_CAM bus.
- Primary K331 uses a tolerant 14-pad land; the exact seven-channel AWM666V land nests in the same bay. Exactly one module is installed, without an internal U.FL or RF cable.
- FM/SW/AM/LW/Airband, CC1101, both voice paths and audio are rear-local; S3 directly owns i8080-8, camera RX, encoder and USB, with buttons on its local TCA9539PWR path.
- The panel is physically turned with its flex toward the antenna edge, as on ESP32-DIV; the adapter occupies the upper inner zone and firmware rotates display output and touch by 180°. The tail stays out of the LED, D-pad and side-key zone.

![True inner sandwich sections](images/h1-r2-inner-sections.svg)

![Rear-face FPV connector proof](images/h1-r2-mmcx-service.svg)

## Generator-verified

- Same-face body collisions: `0`.
- Minimum opposing Z clearance: `2.59 mm` against `0.70 mm` required.
- The FPV reserve is enlarged to `30 × 24 × 8 mm`; C5 DBG10 is relocated beside S3 DBG10 and intersects neither the bay nor adjacent bodies.
- FPV MMCX: the jack body leaves `2.07 mm` to the nearest SMA; the controlled right-angle plug leaves `2.40 mm` to SMA and `4.80 mm` to the common Cap-Bus slot. Ø12 is only a temporary finger-approach zone and remains an H5 ergonomic check.
- GPIO: front RP `46/48` with `2` free; rear RP `44/48` with `4` free. K331 RSSI is officially marked NC.
- M1: all 80 contacts are assigned — 25 signals, 14 main-power, 2 AON, 25 returns and 14 NC reserves.
- M1 mechanics: four 11.00-mm compression stops, two anti-shear datums and independent PCB capture; the connector carries no impact or bending load.
- Antenna silkscreen: the generator proves no overlap with SMA/MMCX bodies, the installed FPV cable, the Cap-Bus slot, the display or mounting keep-outs.
- The exact ten-SMA land pattern follows the A1 drawings: one rectangular 1.87 × 3.30-mm RF land at x=0, four rectangular 1.60 × 3.30-mm shell lands at x=±2.55 mm and board edge y=0. H5 locks the dual-face soldering process, H7 inspects all five joints per connector on the one assembled prototype, and H8 performs ordinary assembly/disassembly, continuity/inspection and every path-specific RF check without artificial ageing, drops or a vibration programme.
- Cap-Bus: mutually exclusive U214/U219 profiles and all eight target clearances pass; all 18 exact U219 bodies, their source-backed courtyards, the NFC pickup loop and the external swept volume of the supplied 108-mm antenna are registered fail-closed. Open H1 geometry gates: `0`.
- The `ER-TFT035IPS-6` + `ER-TPC035-6` assembly, its 50-contact `FH34SRJ-50S-0.5SH(50)` connector and passive `L2-DISP-ADP-001-B` are fixed; the adapter has zero body collisions and 5.10 mm minimum opposing clearance, while the second nRF24 board U.FL retains 1.00 mm planar clearance.

## Exact factory parts

| Role | MPN | JLCPCB | Current availability/route |
|---|---|---|---|
| configured 3.5-inch production display and capacitive touch assembly | `EastRising ER-TFT035IPS-6 + ER-TPC035-6` | — | manufacturer page says In stock; configured quantity-1 price USD 14.91; at least ten-year continuity stated |
| 50-contact display-tail connector on the passive adapter | `FH34SRJ-50S-0.5SH(50)` | [`C3169104`](https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104) | 2,679 pieces shown, 2,614 orderable, MOQ 1, USD 0.5832 at quantity 1 |
| U219 1-kOhm NFC input limiter | `0402WGF1001TCE` | [`C11702`](https://jlcpcb.com/partdetail/12256-0402WGF1001TCE/C11702) | 10,911,212 orderable, MOQ 1, USD 0.0039 at quantity 1 |
| U219 10-kOhm command, threshold and evidence resistor | `0402WGF1002TCE` | [`C25744`](https://jlcpcb.com/partdetail/26487-UNI_ROYAL0402WGF1002TCE/C25744) | 27,943,335 orderable, MOQ 1, USD 0.0031 at quantity 1 |
| U219 100-kOhm envelope and threshold resistor | `0402WGF1003TCE` | [`C25741`](https://jlcpcb.com/partdetail/x/C25741) | 13,226,514 orderable, MOQ 1, USD 0.0028 at quantity 1 |
| U219 1-MOhm comparator hysteresis resistor | `0402WGF1004TCE` | [`C26083`](https://jlcpcb.com/partdetail/x/C26083) | 3,044,597 orderable, MOQ 1, USD 0.0026 at quantity 1 |
| U219 10-nF NFC envelope capacitor | `GRM155R71H103KA88D` | [`C77019`](https://jlcpcb.com/partdetail/MurataElectronics-GRM155R71H103KA88D/C77019) | 629,708 orderable, MOQ 1, USD 0.0097 at quantity 1 |
| Hub RP2354B factory assembly cross-reference | `SC1512-A4` | [`C39843328`](https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328) | LCSC/JLC supply surface showed canPresale 3,442 (authoritative assembly availability), displayed stock 3,605, MOQ 1, USD 1.5658 at quantity 1 and USD 1.4927 at quantity 10 |
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

- No additional physical-body geometry blockers remain.
- review and explicitly accept the generated complete R2 exterior, both true-view inner faces and four real section planes before closing H1

### Preconditions before R2 H2 / KiCad

- timestamp an exact live JLC stock-or-explicit-route, MOQ and price for onsemi FSUSB42MUX / C11355
- select and factory-validate the exact service-VBUS detector/latch MPN used by the closed C5 electrical ownership contract
- instantiate and prove the exact powered-off-Ioff isolation boundary and separate 3V3_MAIN/AON pull-up domains for Hub GPIO42/43 Pack/Safety I2C

> Exact current marker: **H1-R2.33**. H1 remains in progress.
