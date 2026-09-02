# H1-R2.38 · working target-device placement

The complete verifiable physical model of the two 75 × 150 mm PCBs was accepted on 2026-08-30; H1 is reviewed. Every body, Cap profile, external U219 antenna volume and copper reserve is registered with no open geometry gate. This does not authorize KiCad routing: the R2 H2 electrical prerequisites listed below must close first.

## What the user sees

![Four matched PCB faces](images/h1-r2-four-faces.svg?rev=h1-r2.38-4910sq-1)

## Component legend

![Numbered component legend](images/h1-r2-component-legend.svg?rev=h1-r2.38-4910sq-1)

[Detailed exterior at full scale](images/h1-r2-external-layout.svg?rev=h1-r2.38-4910sq-1)

![External service access](images/h1-r2-service-access.svg?rev=h1-r2.38-4910sq-1)

## What is inside

![Direct display ZIF and mechanical retention](images/display-mount.svg?rev=h1-r2.38-4910sq-1)

[Front UI/radio PCB · full-scale inner view](images/h1-r2-inner-ui.svg)

[Rear RF/power PCB · full-scale inner view](images/h1-r2-inner-rf.svg)

- Ten main SMA ports are split symmetrically `5 + 5`; every radio path remains on the PCB that carries its connector.
- The selected GCT `RFPC-SMA31/32-FN-175-A` bodies are not retained by one PCB face: each shell straddles the 1.6-mm board edge, with one RF plus two ground lands on the component face and two more shell-ground lands on the opposite face. This is the same dual-face principle visible in [ESP32-DIV v2](https://github.com/cifertech/ESP32-DIV/tree/9d4d82fe7a12febf554b12e1eca6d434ebe79d39/PCB/v2); a one-face substitute is forbidden.
- On the front PCB, two exact 30-mm S3/C5 and three exact 60-mm nRF removable microcoax jumpers connect the radio-source IPEX/U.FL sockets to board U.FL sockets; controlled board-local PCB paths continue from there to SMA.
- The rear PCB has no U.FL or removable RF cable: voice and FM/SW use board-local RF paths, AM/LW uses a separate high-impedance AMI path, and Airband uses the powered conversion branch and selector.
- Exactly one accessory occupies the common slot: U214 (84 × 24 × 15.287 mm) or optional U219 (84 × 24 × 19.7 mm). U219 is 4.413 mm taller, yet remains 1.0 mm below the battery holder and 1.3 mm below the selected rear maximum.
- All user-facing labels are readable silkscreen; neither inner PCB face carries silkscreen.
- Each outer face prints a stable board role/revision — `UI PCB · R2-EVT1 · REV A` and `RF/PWR PCB · R2-EVT1 · REV A`; the changing H1-R2.xx work marker is never printed on a PCB.
- All three nRF24 islands move to the front PCB with their buffers, safety gate and a dedicated second `TLV1824PWR`.
- The onboard video receiver, decoder, MMCX and physical reserves are removed: no hidden post-PCBA module remains behind the display or between the antennas.
- FM/SW/AM/LW/Airband, CC1101, both voice paths and audio are rear-local; S3 directly owns i8080-8, encoder and USB, with buttons on its local TCA9539PWR path. Six GPIO remain uncommitted electrical reserve after reset and service closure.
- The panel is physically turned with its flex toward the antenna edge / board -Y; the tail enters one direct 50-contact ZIF on the UI PCB and firmware rotates display output and touch by 180°. A tail toward +Y is a stop-work factory error. All display and touch lines remain S3-local; C5 has no panel connection.
- The panel bonds through one ready-stock 3M (TC) 4910SQ-2(5) square measuring 50.80×50.80×1.016 mm, first located on the PCB by its own silkscreen frame at [12.10, 44.46]. It supports 2580.64 mm², or about 53.7% of the stiff panel plan; cutting, a custom die-cut, side shoulders, upper tape strip and separate clamp are unnecessary. After the tongue crosses the slot and the upper liner is removed, a second DISPLAY 56.54×84.96-mm frame with an FPC-UP mark locates the panel. The upper FPC zone remains adhesive-free; only its 25.50±0.15-mm tongue crosses one rounded 27.00×1.20-mm PCB slot into the inner ZIF at [24.0, 25.0]. The 3M ±10% tolerance makes the minimum thickness 0.914 mm, so the current-lot folded FPC must be no higher than 0.714 mm and the actual dry fit must preserve at least 0.20 mm clearance. All five U.FL bodies end at y=17.1 mm and the slot begins at y=23.0 mm, leaving 5.9 mm between them. Neither the FPC nor ZIF carries panel load. A custom contour is allowed only if the PCBA factory itself confirms manufacture and installation inside the order; no external converter is required.
- ESP32-DIV v2 seats its raw 2.8-inch display directly on the main PCB while its 18-contact FPC is soldered to long SMD lands without a ZIF. Four 1.2-mm holes around the display zone remain empty on the assembled device and do not retain the panel. The public Gerbers, PcbDoc, BOM, 3D model and photograph do not disclose the actual retention method; hidden PSA or double-sided tape is plausible but unproven. Leshy2 therefore does not copy DIV's unknown mechanics and defines its own positive load path with a serviceable non-load-bearing ZIF.

![True inner sandwich sections](images/h1-r2-inner-sections.svg)

## Generator-verified

- Same-face body collisions: `0`.
- Minimum opposing Z clearance: `2.59 mm` against `0.70 mm` required.
- Complete TX evidence: `8` exact detectors, `5` couplers and `8` bounded local islands pass fail-closed audit; all six AD8314 positions use the accepted `AD8314ARMZ-REEL` / `C652687`.
- Microcoax reach: two 30-mm native-radio and three 60-mm nRF paths have at least `9.39 mm` paper slack, with each nRF checked against the farthest corner of the complete SP4 envelope rather than a guessed IPEX axis.
- C5 DBG10 is relocated beside S3 DBG10 and intersects no adjacent body.
- GPIO: front RP `46/48` with `2` free; rear RP `43/48` with `5` free; S3 uses 27 of 33 GPIO.
- M1: all 80 contacts are assigned — 31 signals, 14 main-power, 2 AON, 24 returns and 9 true NC reserves.
- M1 mechanics: four 11.00-mm compression stops, two anti-shear datums and independent PCB capture; the connector carries no impact or bending load.
- Antenna silkscreen: the generator proves no overlap with SMA bodies, the Cap-Bus slot, the display or mounting keep-outs.
- The exact ten-SMA land pattern follows the A1 drawings: one rectangular 1.87 × 3.30-mm RF land at x=0, four rectangular 1.60 × 3.30-mm shell lands at x=±2.55 mm and board edge y=0. H5 locks the dual-face soldering process, H7 inspects all five joints per connector on the one assembled prototype, and H8 performs ordinary assembly/disassembly, continuity/inspection and every path-specific RF check without artificial ageing, drops or a vibration programme.
- Cap-Bus: mutually exclusive U214/U219 profiles and all eight target clearances pass; all 18 exact U219 bodies, their source-backed courtyards, the NFC pickup loop and the external swept volume of the supplied 108-mm antenna are registered fail-closed. Open H1 geometry gates: `0`.
- The `ER-TFT035IPS-6` + `ER-TPC035-6` assembly and direct UI-board `FH34SRJ-50S-0.5SH(50)` are fixed; the 1.00-mm ZIF leaves 10.00 mm to the opposing PCB plane, both DF40 parts and the adapter PCB are removed, and the connector carries no panel load.

## Exact factory parts

| Role | MPN | JLCPCB | Current availability/route |
|---|---|---|---|
| six logarithmic RF detectors for complete real-TX evidence | `AD8314ARMZ-REEL` | [`C652687`](https://jlcpcb.com/partdetail/AnalogDevices-AD8314ARMZREEL/C652687) | local stock 0; 2,978 overseas and 2,977 explicitly pre-orderable, MOQ 4; the one device needs 6; USD 2.9826 at quantity 1-9 and USD 1.9398 at quantity 100 |
| configured 3.5-inch production display and capacitive touch assembly | `EastRising ER-TFT035IPS-6 + ER-TPC035-6` | — | manufacturer page says In stock; configured quantity-1 price USD 14.91; at least ten-year continuity stated |
| direct 50-contact display-tail ZIF on the UI PCB | `FH34SRJ-50S-0.5SH(50)` | [`C3169104`](https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104) | 2,679 pieces shown, 2,614 orderable, MOQ 1, USD 0.5832 at quantity 1 |
| U219 1-kOhm NFC input limiter | `0402WGF1001TCE` | [`C11702`](https://jlcpcb.com/partdetail/12256-0402WGF1001TCE/C11702) | 10,911,212 orderable, MOQ 1, USD 0.0039 at quantity 1 |
| U219 10-kOhm command, threshold and evidence resistor | `0402WGF1002TCE` | [`C25744`](https://jlcpcb.com/partdetail/26487-UNI_ROYAL0402WGF1002TCE/C25744) | 27,943,335 orderable, MOQ 1, USD 0.0031 at quantity 1 |
| U219 100-kOhm envelope and threshold resistor | `0402WGF1003TCE` | [`C25741`](https://jlcpcb.com/partdetail/x/C25741) | 13,226,514 orderable, MOQ 1, USD 0.0028 at quantity 1 |
| U219 1-MOhm comparator hysteresis resistor | `0402WGF1004TCE` | [`C26083`](https://jlcpcb.com/partdetail/x/C26083) | 3,044,597 orderable, MOQ 1, USD 0.0026 at quantity 1 |
| U219 10-nF NFC envelope capacitor | `GRM155R71H103KA88D` | [`C77019`](https://jlcpcb.com/partdetail/MurataElectronics-GRM155R71H103KA88D/C77019) | 629,708 orderable, MOQ 1, USD 0.0097 at quantity 1 |
| Hub RP2354B factory assembly cross-reference | `SC1512-A4` | [`C39843328`](https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328) | LCSC/JLC supply surface showed canPresale 3,442 (authoritative assembly availability), displayed stock 3,605, MOQ 1, USD 1.5658 at quantity 1 and USD 1.4927 at quantity 10 |
| Hub RP independent data-only service USB-C | `USB4105-GF-A` | [`C3020560`](https://jlcpcb.com/partdetail/GlobalConnectorTechnology-USB4105_GF_A/C3020560) | 3,712 pieces, MOQ 1, USD 1.0605 at quantity 1 |
| Hub RP recessed RESET/USB_BOOT side switch | `SKRTLAE010` | [`C110293`](https://jlcpcb.com/partdetail/ALPSALPINE-SKRTLAE010/C110293) | 49,305 pieces, MOQ 1, USD 0.1443 at quantity 1 |
| Hub RP keyed internal DBG10 recovery header | `FTSH-105-01-L-DV-K-P-TR` | [`C2932107`](https://jlcpcb.com/partdetail/Samtec-FTSH_105_01_L_DV_K_PTR/C2932107) | 11,433 pieces, MOQ 1, USD 1.2797 at quantity 1 |
| 3V3_MAIN 6-A synchronous buck with protected diagnostic PG | `TPS566231PRQFR` | [`C3190178`](https://jlcpcb.com/partdetail/TexasInstruments-TPS566231PRQFR/C3190178) | 112 pieces, MOQ 1, USD 1.0478 at quantity 1 |
| 3V3_MAIN 2.2-uH high-current shielded inductor | `PSPMAA0605H-2R2M-ANP` | [`C2983088`](https://jlcpcb.com/partdetail/PRODTech-PSPMAA0605H2R2MANP/C2983088) | 627 pieces, MOQ 1, USD 0.1735 at quantity 1 |
| 3V3_MAIN eFuse threshold resistor | `RC0402FR-071K18L` | [`C273709`](https://jlcpcb.com/partdetail/YAGEO-RC0402FR071K18L/C273709) | 5,864 pieces, MOQ 1, USD 0.0025 at quantity 1 |
| TPS566231P VCC decoupling capacitor | `CL10B105KO8NNNC` | [`C59782`](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL10B105KO8NNNC/C59782) | 631,719 pieces, MOQ 1, USD 0.0210 at quantity 1 |
| TPS566231P bootstrap and local high-frequency decoupling capacitor | `CL05B104KB5NNNC` | [`C960916`](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL05B104KB5NNNC/C960916) | 754,861 pieces, MOQ 1, USD 0.0093 at quantity 1 |
| 3V3_MAIN input/output bulk capacitor | `GRM32ER71E226KE15L` | [`C21397`](https://jlcpcb.com/partdetail/MurataElectronics-GRM32ER71E226KE15L/C21397) | 116,360 pieces, MOQ 1, USD 0.6222 at quantity 1 |
| TPS566231P serial bootstrap tuning link | `RC0402JR-070RL` | [`C60485`](https://jlcpcb.com/partdetail/YAGEO-RC0402JR070RL/C60485) | 4,551,848 pieces, MOQ 1, USD 0.0034 at quantity 1 |

## H1 result

- No additional physical-body geometry blockers remain.

### Preconditions before R2 H2 / KiCad


> Final result marker: **H1-R2.38**. H1 was reviewed on 2026-08-30.
