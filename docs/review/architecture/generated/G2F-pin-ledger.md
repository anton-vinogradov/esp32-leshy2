# G2F — generated exact-device pin ledger

- Статус: **машинные проверки проведены; кандидаты не приняты и не являются target architecture**
- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/*.json`
- Regenerate: `python3 hardware/architecture/generate.py --write`
- Verify: `python3 hardware/architecture/generate.py --check`

> Файл сгенерирован. Ручные изменения будут отвергнуты `--check`.

## Candidate snapshot

| Candidate | Programmable domains | Exact exposed-GPIO budget | Decisive open risk |
|---|---:|---|---|
| `G2F-2R` | 2 | `s3 32U/4R/0F`, `c5 17U/4R/0F` | zero free safe GPIO on both domains; C5 worst-case native-radio/IR/3x-nRF/CC latency needs HIL |
| `G2F-3D` | 3 | `s3 33U/3R/0F`, `c5 11U/5R/5F`, `rp 30U/0R/0F` | third image/power/clock/service burden; S3 and RP have zero free GPIO |
| `G2F-3I` | 5 | `s3 32U/3R/1F`, `c5 14U/6R/1F`, `rp 48U/0R/0F`, `pd_controller 5U/5R/0F`, `pack_admission 12U/3R/3F` | DEC-0045 limits runtime to one active signal group, but SG-N24 requires every simultaneous three-radio PTX/PRX mix including 3PTX; exact mixed-RF sensitivity/current/thermal envelope, quiet-state power parts and conducted/OTA HIL remain open |

## Exact-device provenance used by these drafts

| Device id | Exact MPN / boundary | Qualification | Lifecycle | Primary source | Lifecycle evidence |
|---|---|---|---|---|---|
| `adi_ltc5507_es6_trmpbf` | `LTC5507ES6#TRMPBF` | `verified_candidate` | `production` | [LTC5507 100kHz to 1GHz RF Power Detector datasheet 5507f](https://www.analog.com/media/en/technical-documentation/data-sheets/5507f.pdf) | same primary source |
| `adi_ltc5532_es6_trmpbf` | `LTC5532ES6#TRMPBF` | `verified_candidate` | `production` | [LTC5532 Precision 300MHz to 7GHz RF Detector datasheet 5532f](https://www.analog.com/media/en/technical-documentation/data-sheets/5532f.pdf) | same primary source |
| `adi_max17320_g20_t` | `Analog Devices MAX17320G20+T` | `verified_candidate` | `recommended_for_new_designs` | [MAX17320 2S-4S ModelGauge m5 gauge/protector datasheet Rev. 12, July 2025](https://www.analog.com/media/en/technical-documentation/data-sheets/max17320.pdf) | same primary source |
| `cc1101rgpr` | `CC1101RGPR` | `verified_candidate` | `active` | [CC1101 Low-Power Sub-1 GHz RF Transceiver datasheet SWRS061I](https://www.ti.com/lit/ds/symlink/cc1101.pdf) | [TI CC1101RGPR order page](https://www.ti.com/product/CC1101/part-details/CC1101RGPR) |
| `diodes_2n7002dw_7_f` | `Diodes Incorporated 2N7002DW-7-F` | `verified_candidate` | `active` | [2N7002DW dual N-channel MOSFET datasheet DS30120 Rev. 22-2, October 2021](https://www.diodes.com/datasheet/download/2N7002DW.pdf) | same primary source |
| `diodes_bat54_7_f` | `Diodes Incorporated BAT54-7-F` | `verified_candidate` | `active` | [BAT54 surface-mount Schottky barrier diode datasheet DS11005 Rev. 34-2, November 2023](https://www.diodes.com/datasheet/download/BAT54.pdf) | same primary source |
| `diodes_mmbt3904_7_f` | `Diodes Incorporated MMBT3904-7-F` | `verified_candidate` | `active` | [MMBT3904 40-V NPN small-signal transistor datasheet current product data checked 2026-08-18](https://www.diodes.com/datasheet/download/MMBT3904.pdf) | same primary source |
| `diodes_pam8302a_ascr` | `Diodes Incorporated PAM8302AASCR` | `verified_reference` | `active` | [PAM8302A 2.5-W mono filterless Class-D audio amplifier datasheet DS41333 Rev. 6-2, May 2021](https://www.diodes.com/datasheet/download/PAM8302A.pdf) | same primary source |
| `ebyte_e01_ml01ipx` | `Ebyte E01-ML01IPX` | `verified_reference` | `nrf24_family_not_recommended_for_new_designs` | [E01-ML01IPX product specification 2025-01-16](https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf) | [Nordic nRF24 Series lifecycle page](https://www.nordicsemi.com/Products/nRF24-series) |
| `esp32_c5_wroom_1u_n8r8` | `ESP32-C5-WROOM-1U-N8R8` | `verified_candidate` | `active_candidate_revision_floor_v1_2` | [ESP32-C5-WROOM-1/WROOM-1U Datasheet v1.2](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf) | same primary source |
| `esp32_s3_wroom_1u_n16r2` | `ESP32-S3-WROOM-1U-N16R2` | `verified_candidate` | `active` | [ESP32-S3-WROOM-1/WROOM-1U Datasheet v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | same primary source |
| `everest_es8311_qfn20` | `Everest Semiconductor ES8311` | `verified_candidate` | `current manufacturer product brief revision 17.0 dated 2026-02; production sourcing and lot qualification remain open` | [ES8311 Low Power Mono Audio CODEC Product Brief Revision 17.0, February 2026](https://www.everest-semi.com/pdf/ES8311%20PB.pdf) | same primary source |
| `hirose_dm3at_sf_pejm5` | `Hirose DM3AT-SF-PEJM5` | `verified_candidate` | `current_manufacturer_page` | [DM3 Series microSD Card Connectors catalog 2025-12-01](https://www.hirose.com/product/p/CL0609-0031-0-00) | same primary source |
| `liteon_ltst_c190kfkt` | `LTST-C190KFKT` | `verified_candidate` | `active` | [LTST-C190KFKT SMD LED datasheet BNS-OD-C131/A4](https://optoelectronics.liteon.com/upload/download/DS-22-99-0186/LTST-C190KFKT.PDF) | same primary source |
| `liteon_ltst_c190krkt` | `LTST-C190KRKT` | `verified_candidate` | `active` | [LTST-C190KRKT SMD LED datasheet BNS-OD-C131/A4](https://optoelectronics.liteon.com/upload/download/DS-22-99-0151/LTST-C190KRKT.PDF) | same primary source |
| `littelfuse_0451005_mrl` | `Littelfuse 0451005.MRL` | `verified_candidate` | `active` | [451/453 Nano2 surface-mount fuse datasheet current product data checked 2026-08-18](https://www.littelfuse.com/assetdocs/littelfuse-fuse-451-453-datasheet?assetguid=3dce64db-5f0f-4b52-bbf2-f879dd216803) | same primary source |
| `m5_u214` | `M5Stack U214 Cap LoRa-1262` | `verified_candidate` | `active` | [M5Stack Cap LoRa-1262 product documentation live product page](https://docs.m5stack.com/en/cap/Cap_LoRa-1262) | same primary source |
| `murata_grm155r71h472ka01d` | `Murata GRM155R71H472KA01D` | `verified_candidate` | `active` | [Murata GRM155R71H472KA01 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM155R71H472KA01D) | same primary source |
| `murata_grm188r71e224ka88d` | `Murata GRM188R71E224KA88D` | `verified_candidate` | `active` | [Murata GRM188R71E224KA88 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM188R71E224KA88D) | same primary source |
| `murata_grm21br71e225ke11l` | `Murata GRM21BR71E225KE11L` | `verified_candidate` | `active` | [Murata GRM21BR71E225KE11 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM21BR71E225KE11L) | same primary source |
| `nexperia_74lvc1g32gv_125` | `74LVC1G32GV,125` | `verified_candidate` | `production` | [74LVC1G32 Single 2-input OR gate datasheet 2024-09-03](https://assets.nexperia.com/documents/data-sheet/74LVC1G32.pdf) | same primary source |
| `nexperia_74lvc2g14gw_125` | `74LVC2G14GW,125` | `verified_candidate` | `production` | [74LVC2G14 Dual inverting Schmitt trigger datasheet 2023-08-18](https://assets.nexperia.com/documents/data-sheet/74LVC2G14.pdf) | same primary source |
| `nicerf_sa518_v11` | `NiceRF SA518` | `verified_candidate` | `current_product` | [SA518 UV Dual Frequency Walkie-talkie Module Product Specification 1.1 / 2026-05](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf) | same primary source |
| `onsemi_bat54alt1g` | `BAT54ALT1G` | `verified_candidate` | `active` | [BAT54ALT1 Schottky Barrier Diodes datasheet Rev. 16](https://www.onsemi.com/download/data-sheet/pdf/bat54alt1-d.pdf) | same primary source |
| `onsemi_bav70lt1g` | `onsemi BAV70LT1G` | `verified_candidate` | `active` | [BAV70L dual common-cathode switching diode datasheet Rev. 12](https://www.onsemi.com/pdf/datasheet/bav70lt1-d.pdf) | same primary source |
| `onsemi_cat24c512wi_gt3` | `onsemi CAT24C512WI-GT3` | `verified_candidate` | `active` | [CAT24C512 512-kb I2C serial EEPROM datasheet Rev. 9](https://www.onsemi.com/pdf/datasheet/cat24c512-d.pdf) | same primary source |
| `qdtech_hmx035ctft_001` | `HMX035CTFT-001 (QDtech schematic assembly marking)` | `verified_candidate` | `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified` | [QDtech ES3C35P ESP32-S3 schematic official published schematic](https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf) | same primary source |
| `rp2354a_a4` | `RP2354A A4 (exact order code required before BOM freeze)` | `verified_candidate` | `active` | [RP2350 Datasheet; RP2354A uses the same A-package pinout and stacked 2 MB flash build-date 2025-02-20](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) | same primary source |
| `rp2354b_a4` | `RP2354B A4 (exact A4 order/lot identity required before BOM freeze)` | `verified_candidate` | `active` | [RP2350 Datasheet; RP2354B uses the same B-package pinout and stacked 2 MB flash build-date 2025-02-20](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) | same primary source |
| `skyworks_si4732_a10_gs` | `Si4732-A10-GS` | `verified_candidate` | `manufacturer_documented` | [Si4732-A10 Broadcast AM/FM/SW/LW/RDS Radio Receiver data short 2021-09-13](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf) | same primary source |
| `sn74hc595pwr` | `SN74HC595PWR` | `verified_candidate` | `active` | [SNx4HC595 8-Bit Shift Registers datasheet SCLS041J](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf) | same primary source |
| `sunlord_mwsa0503s_3r3mt` | `Sunlord MWSA0503S-3R3MT` | `verified_candidate` | `active` | [Sunlord MWSA-S molded SMD power-inductor datasheet current table checked 2026-08-18](https://www.sunlordinc.com/uploads/files/20230303/MWSA-S%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf) | same primary source |
| `sunlord_mwsa0503s_4r7mt` | `Sunlord MWSA0503S-4R7MT` | `verified_candidate` | `active` | [Sunlord MWSA-S molded SMD power-inductor datasheet current table checked 2026-08-18](https://www.sunlordinc.com/uploads/files/20230303/MWSA-S%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf) | same primary source |
| `sunlord_wpn201612h2r2mt` | `Sunlord WPN201612H2R2MT` | `verified_candidate` | `active` | [Sunlord WPN series wire-wound SMD power-inductor datasheet current table checked 2026-08-18](https://www.sunlordinc.com/uploads/files/20221122/WPN%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf) | same primary source |
| `tca4307dgkr` | `TCA4307DGKR` | `reference_only` | `active` | [TCA4307 Hot-Swappable I2C/SMBus Buffer With Stuck-Bus Recovery datasheet SCPS270B](https://www.ti.com/lit/ds/symlink/tca4307.pdf) | same primary source |
| `tca6424argjr` | `TCA6424ARGJR` | `reference_only` | `active` | [TCA6424A Low-Voltage 24-Bit I2C/SMBus I/O Expander datasheet SCPS193D](https://www.ti.com/lit/ds/symlink/tca6424a.pdf) | same primary source |
| `tca9535pwr` | `TCA9535PWR` | `verified_candidate` | `active` | [TCA9535 Remote 16-Bit I2C/SMBus I/O Expander datasheet SCPS201E](https://www.ti.com/lit/ds/symlink/tca9535.pdf) | same primary source |
| `tdk_b57332v5103f360` | `TDK B57332V5103F360` | `verified_candidate` | `active` | [B57 V5 automotive SMD NTC datasheet and exact product page PPD ML PD 2025-10-30](https://product.tdk.com/en/search/sensor/ntc/chip-ntc-thermistor/info?part_no=B57332V5103F360) | same primary source |
| `ti_bq25798_rqmr` | `Texas Instruments BQ25798RQMR` | `verified_candidate` | `active` | [BQ25798 1-to-4-cell 5-A buck-boost charger datasheet SLUSDV2C, May 2020, revised June 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf) | same primary source |
| `ti_csd87313dmst` | `Texas Instruments CSD87313DMST` | `verified_candidate` | `active` | [CSD87313DMS 30-V dual common-drain N-channel NexFET datasheet SLPS659, April 2017; package addendum updated 2025-10-17](https://www.ti.com/lit/ds/symlink/csd87313dms.pdf) | same primary source |
| `ti_mspm0c1104_sdgs20r` | `Texas Instruments MSPM0C1104SDGS20R` | `verified_candidate` | `active` | [MSPM0C110x mixed-signal microcontroller datasheet SLASF90D, revised January 2026](https://www.ti.com/lit/ds/symlink/mspm0c1104.pdf) | same primary source |
| `ti_sn74lvc08a_pwr` | `SN74LVC08APWR` | `verified_candidate` | `active` | [SNx4LVC08A Quadruple 2-Input Positive-AND Gates datasheet Rev. W](https://www.ti.com/lit/ds/symlink/sn74lvc08a.pdf) | same primary source |
| `ti_sn74lvc1g3157_dbvr` | `Texas Instruments SN74LVC1G3157DBVR` | `verified_reference` | `active` | [SN74LVC1G3157 single-pole, double-throw analog switch datasheet SCES424O, January 2003, revised June 2025](https://www.ti.com/lit/ds/symlink/sn74lvc1g3157.pdf) | same primary source |
| `ti_sn74lvc1g74_dcur` | `SN74LVC1G74DCUR` | `verified_candidate` | `active` | [SN74LVC1G74 Single D-Type Flip-Flop With Clear and Preset datasheet Rev. G](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf) | same primary source |
| `ti_sn74lvc2g08_dcur` | `Texas Instruments SN74LVC2G08DCUR` | `reference_only` | `active` | [SN74LVC2G08 dual 2-input positive-AND gate datasheet SCES198N, April 1999, revised December 2015](https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf) | same primary source |
| `ti_sn74lvc3g34_dcur` | `SN74LVC3G34DCUR` | `verified_candidate` | `active` | [SN74LVC3G34 Triple Buffer Gate datasheet Rev. L](https://www.ti.com/lit/ds/symlink/sn74lvc3g34.pdf) | same primary source |
| `ti_tca9534a_pwr` | `TCA9534APWR` | `verified_candidate` | `active` | [TCA9534A Low-Voltage 8-Bit I2C/SMBus I/O Expander datasheet Rev. C](https://www.ti.com/lit/ds/symlink/tca9534a.pdf) | same primary source |
| `ti_tlv1824_pwr` | `TLV1824PWR` | `verified_candidate` | `active` | [TLV181x and TLV182x 40V Rail-to-Rail Comparator datasheet Rev. E](https://www.ti.com/lit/ds/symlink/tlv1824.pdf) | same primary source |
| `ti_tlv9061_idbvr` | `Texas Instruments TLV9061IDBVR` | `reference_only` | `active` | [TLV906x 10-MHz rail-to-rail input/output operational amplifiers datasheet SBOS839N, March 2017, revised July 2026](https://www.ti.com/lit/ds/symlink/tlv9061.pdf) | same primary source |
| `ti_tmux1136_dgsr` | `Texas Instruments TMUX1136DGSR` | `reference_only` | `active` | [TMUX1136 5-V, low-leakage-current, 2:1, 2-channel precision switch datasheet SCDS402B, June 2019, revised February 2024](https://www.ti.com/lit/ds/symlink/tmux1136.pdf) | same primary source |
| `ti_tps22919_dckr` | `Texas Instruments TPS22919DCKR` | `verified_candidate` | `active` | [TPS22919 5.5-V, 1.5-A self-protected load-switch datasheet SLVSEN5B, October 2018, revised May 2019](https://www.ti.com/lit/ds/symlink/tps22919.pdf) | same primary source |
| `ti_tps25751d_refr` | `Texas Instruments TPS25751DREFR` | `verified_candidate` | `active` | [TPS25751 USB Type-C and USB PD Controller datasheet SLVSH93A, October 2023, revised March 2024](https://www.ti.com/lit/ds/symlink/tps25751.pdf) | same primary source |
| `ti_tps259470l_rpwr` | `Texas Instruments TPS259470LRPWR` | `verified_candidate` | `active` | [TPS25947xx true-reverse-current-blocking eFuse datasheet SLVSFC9C, October 2020, revised May 2026](https://www.ti.com/lit/ds/symlink/tps25947.pdf) | same primary source |
| `ti_tps3808g33_dbvr` | `TPS3808G33DBVR` | `verified_candidate` | `active` | [TPS3808 Low-Quiescent-Current Programmable-Delay Supervisory Circuit datasheet Rev. M](https://www.ti.com/lit/ds/symlink/tps3808.pdf) | same primary source |
| `ti_tps564252_drlr` | `Texas Instruments TPS564252DRLR` | `verified_candidate` | `active` | [TPS56425x 3-V to 17-V input, 4-A synchronous buck converter datasheet SLUSEQ6A, December 2022, revised May 2023](https://www.ti.com/lit/ds/symlink/tps564252.pdf) | same primary source |
| `ti_tps629203_drlr` | `Texas Instruments TPS629203DRLR` | `verified_candidate` | `active` | [TPS629203 300-mA, 3-V to 17-V low-IQ buck converter datasheet SLVSGE2, March 2022](https://www.ti.com/lit/ds/symlink/tps629203.pdf) | same primary source |
| `ti_ts5a63157_dckr` | `Texas Instruments TS5A63157DCKR` | `reference_only` | `active` | [TS5A63157 12-ohm SPDT analog switch datasheet SCDS203B, December 2005, revised March 2019](https://www.ti.com/lit/ds/symlink/ts5a63157.pdf) | same primary source |
| `ti_tvs2200_drvr` | `Texas Instruments TVS2200DRVR` | `verified_candidate` | `active` | [TVS2200 22-V flat-clamp surge-protection datasheet SLVSED5C, December 2017, revised August 2023; orderable addendum 2025-11-09](https://www.ti.com/lit/ds/symlink/tvs2200.pdf) | same primary source |
| `vishay_vemd1060x01` | `VEMD1060X01` | `verified_candidate` | `active` | [VEMD1060X01 Silicon PIN Photodiode datasheet Rev. 1.1](https://www.vishay.com/docs/84295/vemd1060x01.pdf) | same primary source |
| `vishay_wsl25125l000fea` | `Vishay WSL25125L000FEA` | `verified_candidate` | `active` | [WSL power metal strip resistor datasheet current product data checked 2026-08-18](https://www.vishay.com/docs/30108/wsl.pdf) | same primary source |
| `yageo_rc0402fr_07169kl` | `Yageo RC0402FR-07169KL` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0402fr_072k21l` | `Yageo RC0402FR-072K21L` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0402fr_0747kl` | `Yageo RC0402FR-0747KL` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0603fr_071kl` | `Yageo RC0603FR-071KL` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |

## G2F-2R — Two compute domains: C5 owns IR and compatibility radios

- Candidate status: `draft_machine_checked_not_architecture_decision`
- Validation scope: exposed-contact identity, unique allocation, strap proof, complete GPIO accounting, controller declaration, reciprocal programmable links and service-contact coverage.

### Antenna policy

Decisions `DEC-0048`/`DEC-0049`: onboard endpoint `external_sma`; `9` total SMA paths (`S3-2G4`, `C5-2G4/5`, `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`); three nRF paths use `ipex_to_short_pigtail` to `3` dedicated SMA; integrated-PCB baseline `false`. Si4732 topology `dedicated_fmi_and_ami` with shared switch `false` and AMI profile `direct_plug_in_loop_or_qualified_buffered_pod`. Connector decision `DEC-0050` assigns device-side RP-SMA jack/pin to `S3-2G4`, `C5-2G4/5` and standard SMA jack/socket to `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`. Each antenna group requires at least `2` orderable qualified MPNs; native Wi-Fi fallback is `standard_sma_if_no_gain_cost_availability_advantage`. External accessories own their antennas.
Kit decision `DEC-0055` defines `12` loose antenna items with at most `9` connected at once. Native Wi-Fi uses one shared exact MPN in quantity 2, nRF24 one shared exact MPN in quantity 3, CC-SUB uses 315/433/combined-868+915 profiles, VOICE uses separate VHF/UHF profiles, and the receiver uses FM/SW whip plus AM/LW loop or buffered pod. Availability is checked at `exact_mpn_selection`; base/extended packaging remains `deferred_to_costed_product_variants`.

### `s3` — `ESP32-S3-WROOM-1U-N16R2`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `u214.SDA`, `slow_io.SDA`, `abstract:touch/codec/receiver I2C` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `u214.SCL`, `slow_io.SCL`, `abstract:touch/codec/receiver I2C` | — |
| `GPIO4` | 4 | `SD_CLK` | `o` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO5` | 5 | `SD_CMD` | `io` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO6` | 6 | `SD_D0` | `io` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO7` | 7 | `UNIT_SIG0` | `io` | `I2C1_OR_UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO8` | 12 | `UNIT_SIG1` | `io` | `I2C1_OR_UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO9` | 17 | `PTT_BUTTON_N` | `i` | `GPIO` | `abstract:physical PTT switch` | — |
| `GPIO10` | 18 | `S3_C5_SDIO_CLK` | `o` | `SDMMC_SLOT1_1BIT` | `c5.GPIO9` | — |
| `GPIO11` | 19 | `S3_C5_SDIO_CMD` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO10` | — |
| `GPIO12` | 20 | `S3_C5_SDIO_D0` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO8` | — |
| `GPIO13` | 21 | `S3_C5_SDIO_D1_IRQ` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO7` | — |
| `GPIO14` | 22 | `VOICE_PTT_N` | `o` | `GPIO` | `abstract:exact SA518/SA868 voice module` | — |
| `GPIO15` | 8 | `I2S_BCLK` | `o` | `I2S0` | `abstract:exact ES8311 codec` | — |
| `GPIO16` | 9 | `I2S_WS` | `o` | `I2S0` | `abstract:exact ES8311 codec` | — |
| `GPIO17` | 10 | `I2S_DOUT` | `o` | `I2S0` | `abstract:exact ES8311 codec` | — |
| `GPIO18` | 11 | `I2S_DIN` | `i` | `I2S0` | `abstract:exact ES8311 codec` | — |
| `GPIO19` | 13 | `S3_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO20` | 14 | `S3_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO21` | 23 | `VOICE_UART_RX` | `i` | `UART1` | `abstract:exact SA518/SA868 voice module` | — |
| `GPIO35` | 28 | `EXT_SPI_SCK` | `o` | `SPI2` | `u214.SCK`, `abstract:exact display controller` | — |
| `GPIO36` | 29 | `EXT_SPI_MOSI` | `o` | `SPI2` | `u214.MOSI`, `abstract:exact display controller` | — |
| `GPIO37` | 30 | `EXT_SPI_MISO` | `i` | `SPI2` | `u214.MISO` | — |
| `GPIO38` | 31 | `LCD_CS_N` | `o` | `SPI2` | `abstract:exact display controller` | — |
| `GPIO39` | 32 | `LCD_DC` | `o` | `GPIO` | `abstract:exact display controller` | — |
| `GPIO40` | 33 | `LCD_BL_PWM` | `o` | `LEDC` | `abstract:exact display/backlight driver` | — |
| `GPIO41` | 34 | `U214_NSS_N` | `o` | `SPI2` | `u214.NSS` | — |
| `GPIO42` | 35 | `U214_BUSY` | `i` | `GPIO` | `u214.LORA_BUSY` | — |
| `GPIO43` | 37 | `U214_IRQ` | `i` | `GPIO` | `u214.LORA_IRQ` | — |
| `GPIO44` | 36 | `U214_GPS_RX` | `i` | `UART2` | `u214.GPS_TX` | — |
| `GPIO47` | 24 | `U214_GPS_TX` | `o` | `UART2` | `u214.GPS_RX` | — |
| `GPIO48` | 25 | `VOICE_UART_TX` | `o` | `UART1` | `abstract:exact SA518/SA868 voice module` | — |

Budget: **32 used + 4 reserved + 0 free = 36 exposed GPIO**.
Reserved: `GPIO0`, `GPIO3`, `GPIO45`, `GPIO46`. Free: none.

### `c5` — `ESP32-C5-WROOM-1U-N8R8`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 6 | `IR_RX_DEMOD` | `i` | `RMT_RX0` | `abstract:exact robust-demod IR receiver` | — |
| `GPIO1` | 7 | `IR_RX_CARRIER` | `i` | `RMT_RX1` | `abstract:exact carrier-learning IR receiver` | — |
| `GPIO2` | 4 | `RF_SPI_MISO` | `i` | `SPI2` | `nrf0.MISO`, `nrf1.MISO`, `nrf2.MISO`, `cc.SO_GDO1` | JTAG/ROM-sensitive contact is sampled with all radio sources high-Z; exact reset pulls remain a schematic gate |
| `GPIO3` | 5 | `RF_CTRL_SRCLK` | `o` | `GPIO` | `rf_ctrl.SRCLK` | external pull-up fixes the accepted SDIO falling-sample/rising-drive profile; latch clock input does not override the pull during reset |
| `GPIO4` | 17 | `RF_SPI_SCK` | `o` | `SPI2` | `nrf0.SCK`, `nrf1.SCK`, `nrf2.SCK`, `cc.SCLK` | — |
| `GPIO5` | 16 | `RF_SPI_MOSI_LDATA` | `o` | `SPI2_OR_GPIO` | `nrf0.MOSI`, `nrf1.MOSI`, `nrf2.MOSI`, `cc.SI`, `rf_ctrl.SER` | — |
| `GPIO6` | 8 | `IR_TX_CARRIER` | `o` | `RMT_TX0` | `abstract:fail-safe IR LED driver` | — |
| `GPIO7` | 9 | `S3_C5_SDIO_D1_IRQ` | `io` | `SDIO_SLAVE` | `s3.GPIO13` | external pull-up and documented SDIO edge profile are verified before runtime ownership |
| `GPIO8` | 10 | `S3_C5_SDIO_D0` | `io` | `SDIO_SLAVE` | `s3.GPIO12` | — |
| `GPIO9` | 11 | `S3_C5_SDIO_CLK` | `i` | `SDIO_SLAVE` | `s3.GPIO10` | — |
| `GPIO10` | 12 | `S3_C5_SDIO_CMD` | `io` | `SDIO_SLAVE` | `s3.GPIO11` | — |
| `GPIO11` | 25 | `RF_CTRL_RCLK` | `o` | `GPIO` | `rf_ctrl.RCLK` | — |
| `GPIO12` | 24 | `NRF_IRQ_AGG_N` | `i` | `GPIO_IRQ` | `abstract:three-source protected nRF IRQ aggregator` | — |
| `GPIO13` | 13 | `C5_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB fixture` | — |
| `GPIO14` | 14 | `C5_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB fixture` | — |
| `GPIO23` | 21 | `CC_GDO0` | `i` | `GPIO_IRQ` | `cc.GDO0` | — |
| `GPIO24` | 23 | `CC_GDO2` | `i` | `GPIO_IRQ` | `cc.GDO2` | — |

Budget: **17 used + 4 reserved + 0 free = 21 exposed GPIO**.
Reserved: `GPIO25`, `GPIO26`, `GPIO27`, `GPIO28`. Free: none.

### Fixed-function/control routes

| Net | From | To | Reset/safety rule |
|---|---|---|---|
| `NRF0_CSN_N` | `rf_ctrl.QA` | `nrf0.CSN` | external pull-up; OE high until armed |
| `NRF0_CE` | `rf_ctrl.QB` | `nrf0.CE` | external pull-down; OE high until armed |
| `NRF1_CSN_N` | `rf_ctrl.QC` | `nrf1.CSN` | external pull-up; OE high until armed |
| `NRF1_CE` | `rf_ctrl.QD` | `nrf1.CE` | external pull-down; OE high until armed |
| `NRF2_CSN_N` | `rf_ctrl.QE` | `nrf2.CSN` | external pull-up; OE high until armed |
| `NRF2_CE` | `rf_ctrl.QF` | `nrf2.CE` | external pull-down; OE high until armed |
| `CC_CSN_N` | `rf_ctrl.QG` | `cc.CSN` | external pull-up; OE high until armed |
| `RF_CTRL_SPARE` | `rf_ctrl.QH` | `abstract:spare-safe-radio-control` | external STOP-dominant safe pull |
| `RF_CTRL_OE_N` | `abstract:latched-hard-stop` | `rf_ctrl.OE` | non-programmable STOP dominance |
| `RF_CTRL_CLR_N` | `abstract:reset-supervisor` | `rf_ctrl.SRCLR` | forces known shift state before arming |
| `U214_RST_N` | `slow_io.P00` | `u214.LORA_RST` | external reset-safe pull; slow path only |
| `LCD_RST_N` | `slow_io.P01` | `abstract:display-reset` | external reset-safe pull |
| `VOICE_PD_N` | `slow_io.P02` | `abstract:voice-power-down` | external RX/off-safe pull |
| `VOICE_HL` | `slow_io.P03` | `abstract:voice-power-select` | external conservative-power pull |
| `CODEC_EN` | `slow_io.P04` | `abstract:codec-enable` | external off-safe pull |

### Programming, recovery and diagnostics

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20` — native USB Serial/JTAG plus physical EN/BOOT; UART0 fallback is not yet isolated or routed.
- `c5`: `EN`, `GPIO28`, `GPIO27`, `GPIO13`, `GPIO14` — native USB Serial/JTAG plus physical CHIP_PU/BOOT and normal-boot/log strap; removable SDIO isolation.

### Open qualification gaps

- `nrf0` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf0` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf1` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf1` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf2` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf2` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- E01-ML01S is a geometry/interface reference, not the accepted three-module RF/power/antenna production choice
- nRF24 is not recommended for new designs; CC1101RGPR is ACTIVE, but authorised sourcing, qualified alternates and protocol HIL remain unresolved
- CC1101 crystal, balun/matching network, antenna switch/connector and regional RF proof are not represented by the bare IC pinout
- task-based display performance is accepted by DEC-0043 and exact display/touch and microSD references exist, but target MPN/interface/optics and shared-bus HIL, socket/width, codec, voice module, IR frontends, Unit protection/mux and safe IRQ aggregation are not frozen
- single-core C5 worst-case service latency for three simultaneous nRF PRX FIFOs plus CC1101, IR and native-radio work needs executable HIL
- TCA9535 powers up as inputs; every safety-relevant output requires the stated external safe pull and cannot implement STOP
- S3 microSD and C5-link logical slots share one SD/MMC host; required scheduling/concurrency and measured throughput are not yet proven
- U214 requires I2C initialization of its onboard PI4IOE5V6408 antenna-switch control; pin exposure alone does not prove an operational LoRa path
- ordinary UI, display/touch/receiver/audio resets and selectors, card detect, STOP/accessory/power senses and external-I2C fault isolation are not allocated across every TCA9535 port; the current validator proves MCU accounting only
- S3 native USB plus EN/BOOT satisfies baseline recovery, but a UART0 fallback is not isolated from current GPIO43/44 U214 use and must not be claimed without a later fixture/path proof

## G2F-3D — Three compute domains: RP2354A owns compatibility radios and voice deadlines

- Candidate status: `draft_machine_checked_not_architecture_decision`
- Validation scope: exposed-contact identity, unique allocation, strap proof, complete GPIO accounting, controller declaration, reciprocal programmable links and service-contact coverage.

### Antenna policy

Decisions `DEC-0048`/`DEC-0049`: onboard endpoint `external_sma`; `9` total SMA paths (`S3-2G4`, `C5-2G4/5`, `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`); three nRF paths use `ipex_to_short_pigtail` to `3` dedicated SMA; integrated-PCB baseline `false`. Si4732 topology `dedicated_fmi_and_ami` with shared switch `false` and AMI profile `direct_plug_in_loop_or_qualified_buffered_pod`. Connector decision `DEC-0050` assigns device-side RP-SMA jack/pin to `S3-2G4`, `C5-2G4/5` and standard SMA jack/socket to `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`. Each antenna group requires at least `2` orderable qualified MPNs; native Wi-Fi fallback is `standard_sma_if_no_gain_cost_availability_advantage`. External accessories own their antennas.
Kit decision `DEC-0055` defines `12` loose antenna items with at most `9` connected at once. Native Wi-Fi uses one shared exact MPN in quantity 2, nRF24 one shared exact MPN in quantity 3, CC-SUB uses 315/433/combined-868+915 profiles, VOICE uses separate VHF/UHF profiles, and the receiver uses FM/SW whip plus AM/LW loop or buffered pod. Availability is checked at `exact_mpn_selection`; base/extended packaging remains `deferred_to_costed_product_variants`.

### `s3` — `ESP32-S3-WROOM-1U-N16R2`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `u214.SDA`, `slow_io.SDA`, `abstract:touch/codec/receiver I2C` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `u214.SCL`, `slow_io.SCL`, `abstract:touch/codec/receiver I2C` | — |
| `GPIO3` | 15 | `RP_ALERT_N` | `i` | `GPIO_IRQ` | `rp.GPIO28` | RP is held in reset/high-Z through S3 strap sampling; external pull fixes the accepted S3 boot state |
| `GPIO4` | 4 | `SD_CLK` | `o` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO5` | 5 | `SD_CMD` | `io` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO6` | 6 | `SD_D0` | `io` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO7` | 7 | `UNIT_SIG0` | `io` | `I2C1_OR_UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO8` | 12 | `UNIT_SIG1` | `io` | `I2C1_OR_UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO9` | 17 | `S3_RP_IPC_CS_N` | `o` | `SPI3` | `rp.GPIO25` | — |
| `GPIO10` | 18 | `S3_C5_SDIO_CLK` | `o` | `SDMMC_SLOT1_1BIT` | `c5.GPIO9` | — |
| `GPIO11` | 19 | `S3_C5_SDIO_CMD` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO10` | — |
| `GPIO12` | 20 | `S3_C5_SDIO_D0` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO8` | — |
| `GPIO13` | 21 | `S3_C5_SDIO_D1_IRQ` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO7` | — |
| `GPIO14` | 22 | `S3_RP_IPC_MISO` | `i` | `SPI3` | `rp.GPIO27` | — |
| `GPIO15` | 8 | `I2S_BCLK` | `o` | `I2S0` | `abstract:exact ES8311 codec` | — |
| `GPIO16` | 9 | `I2S_WS` | `o` | `I2S0` | `abstract:exact ES8311 codec` | — |
| `GPIO17` | 10 | `I2S_DOUT` | `o` | `I2S0` | `abstract:exact ES8311 codec` | — |
| `GPIO18` | 11 | `I2S_DIN` | `i` | `I2S0` | `abstract:exact ES8311 codec` | — |
| `GPIO19` | 13 | `S3_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO20` | 14 | `S3_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO21` | 23 | `S3_RP_IPC_MOSI` | `o` | `SPI3` | `rp.GPIO24` | — |
| `GPIO35` | 28 | `EXT_SPI_SCK` | `o` | `SPI2` | `u214.SCK`, `abstract:exact display controller` | — |
| `GPIO36` | 29 | `EXT_SPI_MOSI` | `o` | `SPI2` | `u214.MOSI`, `abstract:exact display controller` | — |
| `GPIO37` | 30 | `EXT_SPI_MISO` | `i` | `SPI2` | `u214.MISO` | — |
| `GPIO38` | 31 | `LCD_CS_N` | `o` | `SPI2` | `abstract:exact display controller` | — |
| `GPIO39` | 32 | `LCD_DC` | `o` | `GPIO` | `abstract:exact display controller` | — |
| `GPIO40` | 33 | `LCD_BL_PWM` | `o` | `LEDC` | `abstract:exact display/backlight driver` | — |
| `GPIO41` | 34 | `U214_NSS_N` | `o` | `SPI2` | `u214.NSS` | — |
| `GPIO42` | 35 | `U214_BUSY` | `i` | `GPIO` | `u214.LORA_BUSY` | — |
| `GPIO43` | 37 | `U214_IRQ` | `i` | `GPIO` | `u214.LORA_IRQ` | — |
| `GPIO44` | 36 | `U214_GPS_RX` | `i` | `UART2` | `u214.GPS_TX` | — |
| `GPIO47` | 24 | `U214_GPS_TX` | `o` | `UART2` | `u214.GPS_RX` | — |
| `GPIO48` | 25 | `S3_RP_IPC_SCK` | `o` | `SPI3` | `rp.GPIO26` | — |

Budget: **33 used + 3 reserved + 0 free = 36 exposed GPIO**.
Reserved: `GPIO0`, `GPIO45`, `GPIO46`. Free: none.

### `c5` — `ESP32-C5-WROOM-1U-N8R8`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 6 | `IR_RX_DEMOD` | `i` | `RMT_RX0` | `abstract:exact robust-demod IR receiver` | — |
| `GPIO1` | 7 | `IR_RX_CARRIER` | `i` | `RMT_RX1` | `abstract:exact carrier-learning IR receiver` | — |
| `GPIO6` | 8 | `IR_TX_CARRIER` | `o` | `RMT_TX0` | `abstract:fail-safe IR LED driver` | — |
| `GPIO7` | 9 | `S3_C5_SDIO_D1_IRQ` | `io` | `SDIO_SLAVE` | `s3.GPIO13` | external pull-up and documented SDIO edge profile are verified before runtime ownership |
| `GPIO8` | 10 | `S3_C5_SDIO_D0` | `io` | `SDIO_SLAVE` | `s3.GPIO12` | — |
| `GPIO9` | 11 | `S3_C5_SDIO_CLK` | `i` | `SDIO_SLAVE` | `s3.GPIO10` | — |
| `GPIO10` | 12 | `S3_C5_SDIO_CMD` | `io` | `SDIO_SLAVE` | `s3.GPIO11` | — |
| `GPIO11` | 25 | `C5_UART_SERVICE_TX` | `o` | `UART0` | `abstract:service fixture` | — |
| `GPIO12` | 24 | `C5_UART_SERVICE_RX` | `i` | `UART0` | `abstract:service fixture` | — |
| `GPIO13` | 13 | `C5_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB fixture` | — |
| `GPIO14` | 14 | `C5_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB fixture` | — |

Budget: **11 used + 5 reserved + 5 free = 21 exposed GPIO**.
Reserved: `GPIO3`, `GPIO25`, `GPIO26`, `GPIO27`, `GPIO28`. Free: `GPIO2`, `GPIO4`, `GPIO5`, `GPIO23`, `GPIO24`.

### `rp` — `RP2354A A4 (exact order code required before BOM freeze)`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 2 | `RF_SPI_MISO` | `i` | `PIO_RF_SPI` | `nrf0.MISO`, `nrf1.MISO`, `nrf2.MISO`, `cc.SO_GDO1` | — |
| `GPIO1` | 3 | `NRF0_CSN_N` | `o` | `PIO_RF_SPI` | `nrf0.CSN` | — |
| `GPIO2` | 4 | `RF_SPI_SCK` | `o` | `PIO_RF_SPI` | `nrf0.SCK`, `nrf1.SCK`, `nrf2.SCK`, `cc.SCLK` | — |
| `GPIO3` | 5 | `RF_SPI_MOSI` | `o` | `PIO_RF_SPI` | `nrf0.MOSI`, `nrf1.MOSI`, `nrf2.MOSI`, `cc.SI` | — |
| `GPIO4` | 7 | `NRF0_CE` | `o` | `PIO_RF_SPI` | `nrf0.CE` | — |
| `GPIO5` | 8 | `NRF0_IRQ_N` | `i` | `GPIO_IRQ` | `nrf0.IRQ` | — |
| `GPIO6` | 9 | `NRF1_CSN_N` | `o` | `PIO_RF_SPI` | `nrf1.CSN` | — |
| `GPIO7` | 10 | `NRF1_CE` | `o` | `PIO_RF_SPI` | `nrf1.CE` | — |
| `GPIO8` | 12 | `NRF1_IRQ_N` | `i` | `GPIO_IRQ` | `nrf1.IRQ` | — |
| `GPIO9` | 13 | `NRF2_CSN_N` | `o` | `PIO_RF_SPI` | `nrf2.CSN` | — |
| `GPIO10` | 14 | `NRF2_CE` | `o` | `PIO_RF_SPI` | `nrf2.CE` | — |
| `GPIO11` | 15 | `NRF2_IRQ_N` | `i` | `GPIO_IRQ` | `nrf2.IRQ` | — |
| `GPIO12` | 16 | `CC_CSN_N` | `o` | `PIO_RF_SPI` | `cc.CSN` | — |
| `GPIO13` | 17 | `CC_GDO0` | `i` | `GPIO_IRQ` | `cc.GDO0` | — |
| `GPIO14` | 18 | `CC_GDO2` | `i` | `GPIO_IRQ` | `cc.GDO2` | — |
| `GPIO15` | 19 | `STOP_LATCH_SENSE_N` | `i` | `GPIO_IRQ` | `abstract:non-programmable latched hard-stop` | — |
| `GPIO16` | 27 | `VOICE_UART_TX` | `o` | `UART0` | `abstract:exact SA518/SA868 voice module` | — |
| `GPIO17` | 28 | `VOICE_UART_RX` | `i` | `UART0` | `abstract:exact SA518/SA868 voice module` | — |
| `GPIO18` | 29 | `VOICE_PTT_N` | `o` | `GPIO` | `abstract:exact SA518/SA868 voice module` | — |
| `GPIO19` | 31 | `VOICE_PD_N` | `o` | `GPIO` | `abstract:exact SA518/SA868 voice module` | — |
| `GPIO20` | 32 | `VOICE_HL` | `o` | `GPIO` | `abstract:exact SA518/SA868 voice module` | — |
| `GPIO21` | 33 | `VOICE_ACTIVITY` | `i` | `GPIO_IRQ` | `abstract:exact voice-module qualified activity/status output; SA518 has no dedicated SQ pin` | — |
| `GPIO22` | 34 | `PTT_BUTTON_N` | `i` | `GPIO_IRQ` | `abstract:physical PTT switch` | — |
| `GPIO23` | 35 | `VOICE_TX_EVIDENCE` | `i` | `GPIO_IRQ` | `abstract:independent actual-TX detector` | — |
| `GPIO24` | 36 | `S3_RP_IPC_MOSI` | `i` | `SPI1_IPC` | `s3.GPIO21` | — |
| `GPIO25` | 37 | `S3_RP_IPC_CS_N` | `i` | `SPI1_IPC` | `s3.GPIO9` | — |
| `GPIO26` | 40 | `S3_RP_IPC_SCK` | `i` | `SPI1_IPC` | `s3.GPIO48` | — |
| `GPIO27` | 41 | `S3_RP_IPC_MISO` | `o` | `SPI1_IPC` | `s3.GPIO14` | — |
| `GPIO28` | 42 | `RP_ALERT_N` | `od` | `GPIO_IRQ` | `s3.GPIO3` | — |
| `GPIO29` | 43 | `RP_BOOT_HEALTH` | `o` | `GPIO` | `abstract:hardware supervisor/status capture` | — |

Budget: **30 used + 0 reserved + 0 free = 30 exposed GPIO**.
Reserved: none. Free: none.

### Fixed-function/control routes

| Net | From | To | Reset/safety rule |
|---|---|---|---|
| `U214_RST_N` | `slow_io.P00` | `u214.LORA_RST` | external reset-safe pull; slow path only |
| `LCD_RST_N` | `slow_io.P01` | `abstract:display-reset` | external reset-safe pull |
| `CODEC_EN` | `slow_io.P02` | `abstract:codec-enable` | external off-safe pull |
| `HARD_STOP_N` | `abstract:latched-hard-stop` | `abstract:all-TX-enables-and-rails` | non-programmable dominance over C5, RP and radio/voice TX |

### Programming, recovery and diagnostics

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20` — native USB Serial/JTAG plus physical EN/BOOT; UART0 fallback is not yet isolated or routed.
- `c5`: `EN`, `GPIO28`, `GPIO27`, `GPIO13`, `GPIO14` — native USB Serial/JTAG plus physical CHIP_PU/BOOT and normal-boot/log strap.
- `rp`: `RUN`, `SWCLK`, `SWDIO`, `USB_DM`, `USB_DP`, `QSPI_SS_USB_BOOT` — independent SWD, RUN, USB and BOOTSEL fixture access.

### Open qualification gaps

- `nrf0` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf0` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf1` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf1` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf2` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf2` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- E01-ML01S is a geometry/interface reference, not the accepted three-module RF/power/antenna production choice
- nRF24 is not recommended for new designs; CC1101RGPR is ACTIVE, but authorised sourcing, qualified alternates and protocol HIL remain unresolved
- CC1101 crystal, balun/matching network, antenna switch/connector and regional RF proof are not represented by the bare IC pinout
- task-based display performance is accepted by DEC-0043 and exact display/touch and microSD references exist, but target MPN/interface/optics and shared-bus HIL, socket/width, codec, voice module, IR frontends, Unit protection/mux and hard-stop implementation are not frozen
- RP2354A is a bare-QFN candidate: power, clock, stacked-flash order identity, land pattern and prototype SWD/USB recovery remain implementation gates
- all 30 RP GPIO and all 36 S3 GPIO are accounted with zero general-purpose reserve; physical packaging or one new direct endpoint forces remap/consolidation
- TCA9535 powers up as inputs; every safety-relevant output requires an external safe pull and cannot implement STOP
- S3 microSD and C5-link logical slots share one SD/MMC host; required scheduling/concurrency and measured throughput are not yet proven
- U214 requires I2C initialization of its onboard PI4IOE5V6408 antenna-switch control; pin exposure alone does not prove an operational LoRa path
- ordinary UI, display/touch/receiver/audio resets and selectors, card detect, STOP/accessory/power senses and external-I2C fault isolation are not allocated across every TCA9535 port; the current validator proves MCU accounting only
- S3 native USB plus EN/BOOT satisfies baseline recovery, but a UART0 fallback is not isolated from current GPIO43/44 U214 use and must not be claimed without a later fixture/path proof

## G2F-3I — Three domains with independent radio IPC and only bounded display/storage sharing

- Candidate status: `draft_non_interference_candidate`
- Validation scope: exposed-contact identity, unique allocation, strap proof, complete GPIO accounting, controller declaration, reciprocal programmable links and service-contact coverage.

### Antenna policy

Decisions `DEC-0048`/`DEC-0049`: onboard endpoint `external_sma`; `9` total SMA paths (`S3-2G4`, `C5-2G4/5`, `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`); three nRF paths use `ipex_to_short_pigtail` to `3` dedicated SMA; integrated-PCB baseline `false`. Si4732 topology `dedicated_fmi_and_ami` with shared switch `false` and AMI profile `direct_plug_in_loop_or_qualified_buffered_pod`. Connector decision `DEC-0050` assigns device-side RP-SMA jack/pin to `S3-2G4`, `C5-2G4/5` and standard SMA jack/socket to `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`. Each antenna group requires at least `2` orderable qualified MPNs; native Wi-Fi fallback is `standard_sma_if_no_gain_cost_availability_advantage`. External accessories own their antennas.
Kit decision `DEC-0055` defines `12` loose antenna items with at most `9` connected at once. Native Wi-Fi uses one shared exact MPN in quantity 2, nRF24 one shared exact MPN in quantity 3, CC-SUB uses 315/433/combined-868+915 profiles, VOICE uses separate VHF/UHF profiles, and the receiver uses FM/SW whip plus AM/LW loop or buffered pod. Availability is checked at `exact_mpn_selection`; base/extended packaging remains `deferred_to_costed_product_variants`.

### Signal-group policy

Decision `DEC-0045`; default `NONE`; exclusive groups: `true`.

| Group | Members | Runtime mode | Required role mixes | RF acceptance |
|---|---|---|---|---|
| `SG-N24` | `nrf0`, `nrf1`, `nrf2` | all three active; each independently PTX or PRX in every simultaneous mix; no peer standby or hidden RX gap | `3PRX`, `1PTX+2PRX`, `2PTX+1PRX`, `3PTX` | `DEC-0047` / `qualified_internal_full_mix`; observer `N24H-0001`; `L0 DIV↔DIV` pre-HIL → `T1_TARGET`; HIL required |
| `SG-S3-24` | `s3 Wi-Fi`, `s3 BLE`, `ESP-NOW` | one native RF chain with visible vendor TDM | — | — |
| `SG-C5-NATIVE` | `c5 Wi-Fi 2.4/5`, `c5 IEEE 802.15.4` | one 1T1R native RF chain with visible vendor TDM | — | — |
| `SG-CC` | `cc` | RX or one controlled TX phase | — | — |
| `SG-VOICE` | `voice` | half-duplex RX or TX phase | — | — |
| `SG-BROADCAST` | `receiver`, `audio support` | receive-only | — | — |
| `SG-U214` | `u214 LoRa`, `declared u214 GNSS support` | one exact accessory manifest; joint HIL required | — | — |
| `SG-IR` | `c5 IR` | learn/RX or TX phase | — | — |
| `SG-EXT-*` | `one exact accessory profile` | manifest-declared members only | — | — |

### Unused-interface quiet-state policy

Decision `DEC-0046`; default `QUIET`.

| Contract | Interfaces | Inactive state | Control | Proof gate |
|---|---|---|---|---|
| `N24_QUIET` | `nrf0`, `nrf1`, `nrf2` | pre-off CE low and CSN deasserted; then common rail off, all signal paths isolated/high-Z and PIO/DMA stopped | RP.GPIO15 NRF_GROUP_PWR_EN with off-safe pull plus exact switched-domain I/O isolation | rail discharge/current, no I/O back-power, no carrier and active-receiver desense HIL |
| `CC_QUIET` | `cc` | pre-off IDLE/power-down and CSN deasserted; then rail off, SPI/GDO isolated/high-Z and PIO/DMA stopped | RP.GPIO23 CC_PWR_EN with off-safe pull plus exact switched-domain I/O isolation | rail discharge/current, no SPI/GDO back-power and active-receiver desense HIL |
| `U214_EXT_QUIET` | `u214`, `external accessories` | external 5 V off; I2C isolated; SPI/UART static | slow_io.P17 EXT_5V_EN plus protected power and TCA4307 isolation | rail discharge, isolation, hot-plug and no-back-power HIL |
| `VOICE_QUIET` | `voice` | PTT hardware-off; module power-down; qualified 4 V rail off | VOICE_PTT_N, VOICE_DOMAIN_EN and HARD_STOP_N-dominant power/TX gates | actual-TX-off, rail/current and stuck-control fault-injection HIL |
| `RECEIVER_AUDIO_QUIET` | `receiver`, `codec`, `I2S` | AUDIO_ARM low forces speaker bypass and electret TX-audio default; receiver rail/reset off and isolated when unused; codec muted/off; I2S clock/DMA stopped | direct S3.GPIO6 AUDIO_ARM with pull-down plus RX_DOMAIN_EN, CODEC_PWR_EN and S3 peripheral clock gates | stale P11/P12 reset/watchdog/brownout override, bypass delta, I2C no-back-power, clock spectrum, current and active-receiver desense HIL |
| `IR_QUIET` | `IR RX`, `IR TX` | frontend rail off; RMT stopped and pins parked; TX remains HARD_STOP_N-dominated | C5.GPIO4 IR_FRONTEND_PWR_EN plus independent HARD_STOP_N TX gate | dark/current/no-optical-output and active-radio desense HIL |
| `S3_RF_QUIET` | `S3 Wi-Fi`, `S3 BLE`, `ESP-NOW` | protocols/scans/advertising stopped and native RF block off while S3 CPU/UI remains alive | native RF power state plus S3_RF_TX_EVIDENCE | no background frame/carrier and active-receiver desense HIL |
| `C5_RF_QUIET` | `C5 Wi-Fi`, `C5 IEEE 802.15.4` | protocols stopped and native RF block off while C5 may remain alive for IR/recovery | native RF power state plus C5_RF_TX_EVIDENCE | no background frame/carrier and active-receiver desense HIL |
| `STORAGE_QUIET` | `microSD` | bounded flush then controller static and rail off when no storage session | slow_io.P20 SD_PWR_EN | no corruption/back-power and active-receiver desense HIL |
| `SERVICE_IPC_QUIET` | `USB/UART service`, `S3-RP SPI`, `S3-C5 SDIO`, `display SPI` | detached/suspended or static idle; clocks run only for bounded required transactions | per-controller clock/DMA gates; physical recovery contacts remain available | no periodic logs, measured clock spectrum, recovery and active-receiver desense HIL |

### `s3` — `ESP32-S3-WROOM-1U-N16R2`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `slow_io.SDA`, `receiver.SDIO`, `display.TP_I2C_SDA`, `codec.CDATA`, `pd_controller.I2Ct_SDA`, `pack_admission.PA0` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `slow_io.SCL`, `receiver.SCLK`, `display.TP_I2C_SCL`, `codec.CCLK`, `pd_controller.I2Ct_SCL`, `pack_admission.PA11` | — |
| `GPIO3` | 15 | `RP_ALERT_N` | `i` | `GPIO_IRQ` | `rp.GPIO19` | RP is held reset/high-Z through S3 strap sampling; an external pull fixes the accepted S3 boot state |
| `GPIO4` | 4 | `DISPLAY_SD_SPI_D1` | `io` | `SPI2` | `sd.DAT0`, `display.QSPI_D1` | — |
| `GPIO5` | 5 | `SD_SPI_CS_N` | `o` | `SPI2` | `sd.CD_DAT3` | — |
| `GPIO6` | 6 | `AUDIO_ARM` | `o` | `GPIO` | `audio_safe_gate.1B`, `audio_safe_gate.2B` | — |
| `GPIO7` | 7 | `UNIT_SIG0` | `io` | `I2C1_OR_UART1_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO8` | 12 | `UNIT_SIG1` | `io` | `I2C1_OR_UART1_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO9` | 17 | `S3_RP_IPC_CS_N` | `o` | `SPI3` | `rp.GPIO25` | — |
| `GPIO10` | 18 | `S3_C5_SDIO_CLK` | `o` | `SDMMC_SLOT1_1BIT` | `c5.GPIO9` | — |
| `GPIO11` | 19 | `S3_C5_SDIO_CMD` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO10` | — |
| `GPIO12` | 20 | `S3_C5_SDIO_D0` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO8` | — |
| `GPIO13` | 21 | `S3_C5_SDIO_D1_IRQ` | `io` | `SDMMC_SLOT1_1BIT` | `c5.GPIO7` | — |
| `GPIO14` | 22 | `S3_RP_IPC_MISO` | `i` | `SPI3` | `rp.GPIO27` | — |
| `GPIO15` | 8 | `I2S_BCLK` | `o` | `I2S0` | `codec.SCLK` | — |
| `GPIO16` | 9 | `I2S_WS` | `o` | `I2S0` | `codec.LRCK` | — |
| `GPIO17` | 10 | `I2S_DOUT` | `o` | `I2S0` | `codec.DSDIN` | — |
| `GPIO18` | 11 | `I2S_DIN` | `i` | `I2S0` | `codec.ASDOUT` | — |
| `GPIO19` | 13 | `S3_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO20` | 14 | `S3_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO21` | 23 | `S3_RP_IPC_MOSI` | `o` | `SPI3` | `rp.GPIO24` | — |
| `GPIO35` | 28 | `DISPLAY_SD_SPI_SCK` | `o` | `SPI2` | `sd.CLK`, `display.QSPI_CLK` | — |
| `GPIO36` | 29 | `DISPLAY_SD_SPI_D0` | `o` | `SPI2` | `sd.CMD`, `display.QSPI_D0` | — |
| `GPIO37` | 30 | `SYS_INT_N` | `i` | `GPIO_IRQ` | `slow_io.INT`, `pd_controller.I2Ct_IRQ`, `abstract:pack-admission reset-safe open-drain IRQ circuit` | — |
| `GPIO38` | 31 | `LCD_CS_N` | `o` | `SPI2` | `display.QSPI_CS` | — |
| `GPIO39` | 32 | `LCD_TOUCH_INT` | `i` | `GPIO_IRQ` | `display.TP_INT` | — |
| `GPIO40` | 33 | `LCD_BL_PWM` | `o` | `LEDC` | `abstract:exact display/backlight driver` | — |
| `GPIO41` | 34 | `LCD_QSPI_D2` | `o` | `SPI2` | `display.QSPI_D2` | — |
| `GPIO42` | 35 | `LCD_QSPI_D3` | `o` | `SPI2` | `display.QSPI_D3` | — |
| `GPIO43` | 37 | `S3_UART_SERVICE_TX` | `o` | `UART0` | `abstract:service fixture` | — |
| `GPIO44` | 36 | `S3_UART_SERVICE_RX` | `i` | `UART0` | `abstract:service fixture` | — |
| `GPIO48` | 25 | `S3_RP_IPC_SCK` | `o` | `SPI3` | `rp.GPIO26` | — |

Budget: **32 used + 3 reserved + 1 free = 36 exposed GPIO**.
Reserved: `GPIO0`, `GPIO45`, `GPIO46`. Free: `GPIO47`.

### `c5` — `ESP32-C5-WROOM-1U-N8R8`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 6 | `IR_RX_DEMOD` | `i` | `RMT_RX0` | `abstract:exact robust-demod IR receiver` | — |
| `GPIO1` | 7 | `IR_RX_CARRIER` | `i` | `RMT_RX1` | `abstract:exact carrier-learning IR receiver` | — |
| `GPIO4` | 17 | `IR_FRONTEND_PWR_EN` | `o` | `GPIO` | `abstract:off-safe IR frontend load switch` | — |
| `GPIO6` | 8 | `IR_TX_CARRIER` | `o` | `RMT_TX0` | `safe_gate_b.3A` | — |
| `GPIO7` | 9 | `S3_C5_SDIO_D1_IRQ` | `io` | `SDIO_SLAVE` | `s3.GPIO13` | external pull-up and documented SDIO edge profile are verified before runtime ownership |
| `GPIO8` | 10 | `S3_C5_SDIO_D0` | `io` | `SDIO_SLAVE` | `s3.GPIO12` | — |
| `GPIO9` | 11 | `S3_C5_SDIO_CLK` | `i` | `SDIO_SLAVE` | `s3.GPIO10` | — |
| `GPIO10` | 12 | `S3_C5_SDIO_CMD` | `io` | `SDIO_SLAVE` | `s3.GPIO11` | — |
| `GPIO11` | 25 | `C5_UART_SERVICE_TX` | `o` | `UART0` | `abstract:service fixture` | — |
| `GPIO12` | 24 | `C5_UART_SERVICE_RX` | `i` | `UART0` | `abstract:service fixture` | — |
| `GPIO13` | 13 | `C5_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO14` | 14 | `C5_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO23` | 21 | `C5_RF_TX_EVIDENCE_N` | `i` | `GPIO_IRQ` | `evidence_cmp_a.OUT2` | — |
| `GPIO24` | 23 | `IR_TX_EVIDENCE_N` | `i` | `GPIO_IRQ` | `evidence_cmp_b.OUT4` | — |

Budget: **14 used + 6 reserved + 1 free = 21 exposed GPIO**.
Reserved: `GPIO2`, `GPIO3`, `GPIO25`, `GPIO26`, `GPIO27`, `GPIO28`. Free: `GPIO5`.

### `rp` — `RP2354B A4 (exact A4 order/lot identity required before BOM freeze)`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 77 | `NRF0_CSN_N` | `o` | `GPIO` | `nrf0.CSN` | — |
| `GPIO1` | 78 | `NRF0_CE_REQ` | `o` | `GPIO` | `safe_gate_a.1A` | — |
| `GPIO2` | 79 | `NRF0_IRQ_N` | `i` | `GPIO_IRQ` | `nrf0.IRQ` | — |
| `GPIO3` | 80 | `NRF1_CSN_N` | `o` | `GPIO` | `nrf1.CSN` | — |
| `GPIO4` | 1 | `NRF1_CE_REQ` | `o` | `GPIO` | `safe_gate_a.2A` | — |
| `GPIO5` | 2 | `NRF1_IRQ_N` | `i` | `GPIO_IRQ` | `nrf1.IRQ` | — |
| `GPIO6` | 3 | `NRF2_CSN_N` | `o` | `GPIO` | `nrf2.CSN` | — |
| `GPIO7` | 4 | `NRF2_CE_REQ` | `o` | `GPIO` | `safe_gate_a.3A` | — |
| `GPIO8` | 6 | `NRF2_IRQ_N` | `i` | `GPIO_IRQ` | `nrf2.IRQ` | — |
| `GPIO9` | 7 | `CC_CSN_N` | `o` | `GPIO` | `cc.CSN` | — |
| `GPIO10` | 8 | `CC_GDO0` | `i` | `GPIO_IRQ` | `cc.GDO0` | — |
| `GPIO11` | 9 | `CC_GDO2` | `i` | `GPIO_IRQ` | `cc.GDO2` | — |
| `GPIO12` | 11 | `U214_BUSY` | `i` | `GPIO_IRQ` | `u214.LORA_BUSY` | — |
| `GPIO13` | 12 | `U214_IRQ` | `i` | `GPIO_IRQ` | `u214.LORA_IRQ` | — |
| `GPIO14` | 13 | `U214_RST_N` | `o` | `GPIO` | `u214.LORA_RST` | — |
| `GPIO15` | 14 | `NRF_GROUP_PWR_EN` | `o` | `GPIO` | `safe_gate_a.4A` | — |
| `GPIO16` | 16 | `VOICE_UART_TX` | `o` | `UART0` | `voice.UART_RX` | — |
| `GPIO17` | 17 | `VOICE_UART_RX` | `i` | `UART0` | `voice.UART_TX` | — |
| `GPIO18` | 18 | `VOICE_PTT_REQ_N` | `o` | `GPIO` | `safe_ptt_or.1A` | — |
| `GPIO19` | 19 | `RP_ALERT_N` | `od` | `GPIO_IRQ` | `s3.GPIO3` | — |
| `GPIO20` | 20 | `VOICE_ACTIVITY` | `i` | `GPIO_IRQ` | `voice.AUDIO_ON` | — |
| `GPIO21` | 21 | `PTT_BUTTON_N` | `i` | `GPIO_IRQ` | `abstract:physical PTT switch` | — |
| `GPIO22` | 22 | `RP_ANY_TX_N` | `i` | `GPIO_IRQ` | `evidence_or_0.A_COMMON`, `evidence_or_1.A_COMMON`, `evidence_or_2.A_COMMON`, `evidence_or_3.A_COMMON`, `any_tx_led.K` | — |
| `GPIO23` | 23 | `CC_PWR_EN` | `o` | `GPIO` | `safe_gate_b.1A` | — |
| `GPIO24` | 25 | `S3_RP_IPC_MOSI` | `i` | `SPI1_IPC` | `s3.GPIO21` | — |
| `GPIO25` | 26 | `S3_RP_IPC_CS_N` | `i` | `SPI1_IPC` | `s3.GPIO9` | — |
| `GPIO26` | 27 | `S3_RP_IPC_SCK` | `i` | `SPI1_IPC` | `s3.GPIO48` | — |
| `GPIO27` | 28 | `S3_RP_IPC_MISO` | `o` | `SPI1_IPC` | `s3.GPIO14` | — |
| `GPIO28` | 36 | `U214_I2C_SDA_IN` | `io` | `I2C0_EXT` | `u214_i2c_iso.SDAIN`, `evidence_mask.SDA` | — |
| `GPIO29` | 37 | `U214_I2C_SCL_IN` | `o` | `I2C0_EXT` | `u214_i2c_iso.SCLIN`, `evidence_mask.SCL` | — |
| `GPIO30` | 38 | `NRF0_MISO` | `i` | `PIO0_SM0_RF_SPI` | `nrf0.MISO` | — |
| `GPIO31` | 39 | `NRF0_SCK` | `o` | `PIO0_SM0_RF_SPI` | `nrf0.SCK` | — |
| `GPIO32` | 40 | `NRF0_MOSI` | `o` | `PIO0_SM0_RF_SPI` | `nrf0.MOSI` | — |
| `GPIO33` | 42 | `NRF1_MISO` | `i` | `PIO0_SM1_RF_SPI` | `nrf1.MISO` | — |
| `GPIO34` | 43 | `NRF1_SCK` | `o` | `PIO0_SM1_RF_SPI` | `nrf1.SCK` | — |
| `GPIO35` | 44 | `NRF1_MOSI` | `o` | `PIO0_SM1_RF_SPI` | `nrf1.MOSI` | — |
| `GPIO36` | 45 | `NRF2_MISO` | `i` | `PIO0_SM2_RF_SPI` | `nrf2.MISO` | — |
| `GPIO37` | 46 | `NRF2_SCK` | `o` | `PIO0_SM2_RF_SPI` | `nrf2.SCK` | — |
| `GPIO38` | 47 | `NRF2_MOSI` | `o` | `PIO0_SM2_RF_SPI` | `nrf2.MOSI` | — |
| `GPIO39` | 48 | `CC_MISO` | `i` | `PIO0_SM3_RF_SPI` | `cc.SO_GDO1` | — |
| `GPIO40` | 49 | `U214_GPS_TX` | `o` | `UART1` | `u214.GPS_RX` | — |
| `GPIO41` | 52 | `U214_GPS_RX` | `i` | `UART1` | `u214.GPS_TX` | — |
| `GPIO42` | 53 | `CC_SCK` | `o` | `PIO0_SM3_RF_SPI` | `cc.SCLK` | — |
| `GPIO43` | 54 | `CC_MOSI` | `o` | `PIO0_SM3_RF_SPI` | `cc.SI` | — |
| `GPIO44` | 55 | `U214_MISO` | `i` | `PIO1_SM0_EXT_SPI` | `u214.MISO` | — |
| `GPIO45` | 56 | `U214_SCK` | `o` | `PIO1_SM0_EXT_SPI` | `u214.SCK` | — |
| `GPIO46` | 57 | `U214_MOSI` | `o` | `PIO1_SM0_EXT_SPI` | `u214.MOSI` | — |
| `GPIO47` | 58 | `U214_NSS_N` | `o` | `GPIO` | `u214.NSS` | — |

Budget: **48 used + 0 reserved + 0 free = 48 exposed GPIO**.
Reserved: none. Free: none.

### `pd_controller` — `Texas Instruments TPS25751DREFR`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 5 | `PD_EEPROM_WP` | `o` | `GPIO` | `pd_config_eeprom.WP` | — |
| `GPIO1` | 6 | `CHARGE_EN_N` | `o` | `GPIO` | `nvdc_charger.CE` | — |
| `I2Ct_IRQ` | 10 (I2C target IRQ / GPIO10) | `SYS_INT_N` | `od` | `I2C_TARGET` | `s3.GPIO37` | — |
| `I2Ct_SCL` | 9 (fixed I2C target clock) | `SYS_I2C_SCL` | `i` | `I2C_TARGET` | `s3.GPIO2` | — |
| `I2Ct_SDA` | 8 (fixed I2C target data) | `SYS_I2C_SDA` | `io` | `I2C_TARGET` | `s3.GPIO1` | — |

Budget: **5 used + 5 reserved + 0 free = 10 exposed GPIO**.
Reserved: `GPIO2`, `GPIO3`, `GPIO6`, `GPIO7`, `GPIO11`. Free: none.

### `pack_admission` — `Texas Instruments MSPM0C1104SDGS20R`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `PA0` | 4 | `SYS_I2C_SDA` | `io` | `I2C_TARGET` | `s3.GPIO1` | — |
| `PA2` | 8 | `PACK_GAUGE_I2C_SCL` | `io` | `BITBANG_I2C` | `pack_gauge.SCL_OD` | — |
| `PA4` | 9 | `PACK_GAUGE_I2C_SDA` | `io` | `BITBANG_I2C` | `pack_gauge.SDA_DQ` | — |
| `PA6` | 10 | `PACK_FET_HOLD_RELEASE` | `o` | `GPIO` | `pack_hold.G2` | — |
| `PA11` | 11 | `SYS_I2C_SCL` | `i` | `I2C_TARGET` | `s3.GPIO2` | — |
| `PA17` | 13 | `PACK_SERVICE_UART_TX` | `o` | `UART0` | `abstract:pack service fixture` | — |
| `PA23` | 18 | `PACK_SYS_INT_REQ_N` | `o` | `GPIO` | `abstract:pack-admission reset-safe open-drain IRQ circuit` | — |
| `PA16_A8` | 12 | `PACK_PFAIL_N` | `i` | `GPIO_IRQ` | `pack_gauge.PFAIL` | — |
| `PA18_A7` | 14 | `PACK_SERVICE_UART_RX` | `i` | `UART0` | `abstract:pack service fixture` | — |
| `PA22_A4` | 17 | `PACK_DIAG_LOAD_EN` | `o` | `GPIO` | `abstract:bounded diagnostic load switch` | — |
| `PA24_A3` | 19 | `PACK_CELL0_ADC` | `i` | `ADC` | `abstract:protected 2S midpoint divider` | — |
| `PA25_A2` | 20 | `PACK_STACK_ADC` | `i` | `ADC` | `abstract:protected full-stack divider` | — |

Budget: **12 used + 3 reserved + 3 free = 18 exposed GPIO**.
Reserved: `PA19_SWDIO`, `PA1_NRST`, `PA20_A6_SWCLK`. Free: `PA26_A1`, `PA27_A0`, `PA28_A5`.

### Fixed-function/control routes

| Net | From | To | Reset/safety rule |
|---|---|---|---|
| `USB_C_VBUS_RAW` | `abstract:product-usb-c-vbus` | `pd_controller.VBUS_IN` | only the product S3 USB-C receptacle may power the board; current remains default-limited until a valid sink contract exists |
| `USB_C_VBUS_RAW` | `abstract:product-usb-c-vbus` | `pd_vbus_tvs.IN` | TVS2200DRVR is a shunt clamp physically adjacent to the receptacle, not a series element |
| `USB_C_VBUS_TVS_RETURN` | `pd_vbus_tvs.GND` | `abstract:power-ground` | short low-inductance surge return; exact placement and return geometry remain I4/layout gates |
| `USB_C_CC1` | `abstract:product-usb-c-cc1` | `pd_controller.CC1` | sink-only Type-C/PD detection; source and power-bank roles are disabled |
| `USB_C_CC2` | `abstract:product-usb-c-cc2` | `pd_controller.CC2` | sink-only Type-C/PD detection; source and power-bank roles are disabled |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `nvdc_charger.VBUS` | accepted profiles stop at 15 V/2 A; the integrated protected path remains off above the negotiated envelope |
| `PD_LOCAL_I2C_SDA` | `pd_controller.I2Cc_SDA` | `pd_config_eeprom.SDA` | dedicated address-0x50 boot image; one EEPROM per controller |
| `PD_LOCAL_I2C_SCL` | `pd_controller.I2Cc_SCL` | `pd_config_eeprom.SCL` | controller loads patch/config autonomously before S3 availability is assumed |
| `PD_LOCAL_I2C_SDA` | `pd_controller.I2Cc_SDA` | `nvdc_charger.SDA` | charger is controlled through the officially supported TPS25751D local-controller topology |
| `PD_LOCAL_I2C_SCL` | `pd_controller.I2Cc_SCL` | `nvdc_charger.SCL` | charger transactions never occupy an RF, display or storage bus |
| `PACK_AOLDO` | `pack_gauge.AOLDO` | `pack_supply_or.A1` | AOLDO supplies only measured low-clock admission below the MAX17320 2-mA source budget; BAV70LT1G blocks fixture/system backfeed |
| `PACK_FIXTURE_3V3` | `abstract:isolated-pack-fixture-3v3` | `pack_supply_or.A2` | fixture supply is isolated from USB/system power and is used for blank-device programming and recovery |
| `PACK_ADMISSION_VDD` | `pack_supply_or.K_COMMON` | `pack_admission.VDD` | common cathode passively ORs AOLDO and fixture sources without firmware control |
| `PACK_SYSTEM_3V3` | `abstract:admitted-system-3v3` | `pack_system_diode.A` | system source exists only after complete pair admission and uses the lower-drop branch |
| `PACK_ADMISSION_VDD` | `pack_system_diode.K` | `pack_admission.VDD` | BAT54-7-F blocks admission VDD from back-powering the admitted system rail |
| `PACK_LOCAL_GND` | `pack_admission.VSS` | `pack_gauge.GND` | local controller, gauge and fixture share one bounded pack-side reference; USB/system isolation and touch-safe access remain exact circuit gates |
| `PACK_HOLD_PULLUP_SOURCE` | `pack_gauge.AOLDO` | `abstract:exact-value-hold-gate-pullup` | exact-value resistor pulls Q1 gate high without exceeding the AOLDO budget |
| `PACK_HOLD_GATE` | `abstract:exact-value-hold-gate-pullup` | `pack_hold.G1` | reset or unpowered admission MCU turns Q1 on and asserts the hold |
| `PACK_FET_OVERRIDE_N` | `pack_hold.D1` | `pack_gauge.ALRT` | Q1 asserts ALRT low before MCU code; release follows protected gauge image/readback and complete pair admission only |
| `PACK_LOCAL_GND` | `pack_hold.S1` | `pack_gauge.GND` | Q1 has a local pack-side return |
| `PACK_HOLD_GATE` | `pack_hold.D2` | `pack_hold.G1` | Q2 can pull the Q1 gate low only after PA6 explicitly requests release |
| `PACK_LOCAL_GND` | `pack_hold.S2` | `pack_gauge.GND` | Q2 has a local pack-side return; its gate has an exact-value reset pulldown still to be frozen |
| `SYS_INT_N` | `abstract:pack-admission reset-safe open-drain IRQ circuit` | `s3.GPIO37` | reset, unpowered admission MCU and push-pull faults cannot drive the shared IRQ high or back-power the system bus |
| `PACK_CHG_GATE` | `pack_gauge.CHG` | `pack_power_fet.G1` | CSD87313DMST FET1 source is the cell-stack side required by MAX17320 CHG referenced to IN; exact 0.1-uF gate-source capacitor remains a schematic value |
| `PACK_DIS_GATE` | `pack_gauge.DIS` | `pack_power_fet.G2` | CSD87313DMST FET2 source is the pack side required by MAX17320 DIS referenced to PCKP |
| `PACK_ZVC_UNUSED` | `pack_gauge.ZVC` | `abstract:no-connect` | DEC-0067 forbids in-device zero-volt recovery; the datasheet requires ZVC open when unused |
| `BATTERY_STACK_POSITIVE` | `abstract:qualified-2s-positive` | `pack_power_fet.S1` | battery-side source enters a common-drain back-to-back pair; zero-volt and prequal recovery remain disabled |
| `PROTECTED_PACK_POSITIVE` | `pack_power_fet.S2` | `nvdc_charger.BAT` | pack-side source reaches the charger only after complete admission and MAX17320 protection permission |
| `PACK_SHUNT_CSP` | `pack_gauge.CSP` | `pack_shunt.END_1` | Kelvin pickup follows the ADI Figure-24 current-sense orientation |
| `PACK_SHUNT_CSN` | `pack_shunt.END_2` | `pack_gauge.CSN` | 5-mOhm shunt yields the accepted measurement range; force/kelvin copper geometry remains an I4 gate |
| `PACK_CELL0_TEMP` | `pack_gauge.TH1` | `pack_ntc0.END_1` | one exact 10-kOhm NTC is mechanically coupled to cell 0; coupling remains an I8/HIL gate |
| `PACK_LOCAL_GND` | `pack_ntc0.END_2` | `pack_gauge.GND` | TH1 uses the MAX17320 internal pullup and protected 10-kOhm mode |
| `PACK_CELL1_TEMP` | `pack_gauge.TH2` | `pack_ntc1.END_1` | one exact 10-kOhm NTC is mechanically coupled to cell 1; coupling remains an I8/HIL gate |
| `PACK_LOCAL_GND` | `pack_ntc1.END_2` | `pack_gauge.GND` | TH2 uses the MAX17320 internal pullup and protected 10-kOhm mode |
| `PACK_SLOT0_POSITIVE_RAW` | `abstract:qualified-slot0-positive` | `pack_fuse0.END_1` | each replaceable slot has its own adjacent 5-A fast fuse |
| `PACK_2S_MIDPOINT` | `pack_fuse0.END_2` | `abstract:protected-2s-midpoint` | slot-0 fuse opens independently; holder polarity and reverse-insertion blocking remain mechanical/electrical gates |
| `PACK_SLOT1_POSITIVE_RAW` | `abstract:qualified-slot1-positive` | `pack_fuse1.END_1` | each replaceable slot has its own adjacent 5-A fast fuse |
| `BATTERY_STACK_POSITIVE` | `pack_fuse1.END_2` | `abstract:qualified-2s-positive` | slot-1 fuse opens independently; holder polarity and reverse-insertion blocking remain mechanical/electrical gates |
| `CHARGER_INT_N` | `nvdc_charger.INT` | `pd_controller.I2Cc_IRQ` | active-low charger status/fault returns to the PD controller without a new MCU contact |
| `PD_EEPROM_WP` | `pd_controller.GPIO0` | `pd_config_eeprom.WP` | external pull-up protects the image at reset; TPS may drive low only inside an S3-authorized signed update window |
| `CHARGE_EN_N` | `pd_controller.GPIO1` | `nvdc_charger.CE` | external pull-up disables charge while TPS configuration is absent/invalid; valid policy explicitly drives the active-low enable |
| `PD_EEPROM_A0_LOW` | `abstract:power-ground` | `pd_config_eeprom.A0` | fixed 7-bit address 0x50 |
| `PD_EEPROM_A1_LOW` | `abstract:power-ground` | `pd_config_eeprom.A1` | fixed 7-bit address 0x50 |
| `PD_EEPROM_A2_LOW` | `abstract:power-ground` | `pd_config_eeprom.A2` | fixed 7-bit address 0x50 |
| `PD_USB_P_UNUSED_LOW` | `pd_controller.GPIO4_USB_P_LD1` | `abstract:power-ground` | BC1.2/liquid detection is disabled here so product D+ remains direct to S3; datasheet requires unused contact low |
| `PD_USB_N_UNUSED_LOW` | `pd_controller.GPIO5_USB_N_LD2` | `abstract:power-ground` | BC1.2/liquid detection is disabled here so product D- remains direct to S3; datasheet requires unused contact low |
| `CHARGER_DP_NC` | `nvdc_charger.D_PLUS` | `abstract:no-connect` | BQ DPDM detection is disabled and isolated from the direct S3 USB2 data pair |
| `CHARGER_DM_NC` | `nvdc_charger.D_MINUS` | `abstract:no-connect` | BQ DPDM detection is disabled and isolated from the direct S3 USB2 data pair |
| `NVDC_SYS` | `nvdc_charger.SYS` | `aon_buck.VIN` | the AON source is independent of every application rail and remains available on admitted battery or valid USB system power |
| `AON_BUCK_EN` | `abstract:nvdc-sys-via-aon-enable-pullup` | `aon_buck.EN` | hardware pull-up enables AON without application firmware; converter UVLO and supervisor still force a safe result on collapse |
| `AON_BUCK_SW` | `aon_buck.SW` | `aon_inductor.END_1` | 2.2-uH shielded inductor is the manufacturer-nominal 2.5-MHz first target |
| `AON_SAFE_3V3` | `aon_inductor.END_2` | `abstract:AON_SAFE_3V3` | rated for at least 5-mA continuous and 8-mA transient safety load; exact capacitor hold-up closes in the next passive-value gate |
| `AON_SAFE_3V3_SENSE` | `abstract:AON_SAFE_3V3` | `aon_buck.VOS` | remote sense is taken at the local AON output capacitor rather than the switching node |
| `AON_VSET_3V3` | `abstract:aon-3v3-vset-config` | `aon_buck.FB_VSET` | fixed 3.3-V hardware configuration; no runtime-programmable rail voltage |
| `AON_PG_N` | `aon_buck.PG` | `abstract:aon-power-good-sequence` | open-drain evidence must be valid before the hard-STOP supervisor and downstream sequencing are released |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_buck.VIN` | independent fixed converter prevents compute transients from changing voice or accessory voltage |
| `MAIN_3V3_EN` | `abstract:main-rail-enable-after-source-admission` | `main_buck.EN` | reset-low hardware sequencer permits main power only after an admitted battery pair or valid USB service source |
| `MAIN_BUCK_SW` | `main_buck.SW` | `main_inductor.END_1` | 3.3-uH exact first target keeps the 3-A load-step peak below its minimum saturation current |
| `3V3_MAIN` | `main_inductor.END_2` | `abstract:3V3_MAIN` | fixed 3.3-V rail is sized for 2.5-A continuous and 3.0-A load-step demand |
| `MAIN_3V3_FB` | `abstract:main-3v3-feedback-divider` | `main_buck.FB` | fixed divider; passive tolerance and feed-forward choice close before schematic authorization |
| `MAIN_3V3_PG_N` | `main_buck.PG` | `abstract:power-current-thermal-fault` | open-drain loss/fault evidence joins the diagnostic aggregate without replacing hardware protection |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_buck.VIN` | voice has a physically independent fixed-voltage converter rather than a shared 4/5-V selector |
| `VOICE_BUCK_SW` | `voice_buck.SW` | `voice_inductor.END_1` | 3.3-uH exact first target has margin over the qualified 1.5-A transient peak current |
| `VVOICE_4V` | `voice_inductor.END_2` | `voice.VCC` | fixed 4.0-V rail can never be switched to the 5-V accessory setting |
| `VOICE_4V_FB` | `abstract:voice-4v-feedback-divider` | `voice_buck.FB` | fixed divider; no MCU, mux or digital potentiometer can overvolt SA518 |
| `VOICE_4V_PG_N` | `voice_buck.PG` | `abstract:voice-power-reset-domain` | PD remains asserted until the exact fixed 4-V rail is valid |
| `VOICE_4V_PG_N` | `voice_buck.PG` | `voice_pg_qualifier.E` | the open-drain PG emitter input is qualified by the same STOP-dominant enable request; PG is pulled up only inside the powered 3V3_MAIN diagnostic domain |
| `VOICE_4V_FAULT_QUAL_N` | `voice_pg_qualifier.C` | `abstract:power-current-thermal-fault` | open collector sinks only for EN=1 and PG=0; a normally disabled voice rail releases POWER_FAULT_N |
| `NVDC_SYS` | `nvdc_charger.SYS` | `ext_buck.VIN` | external 5 V has a dedicated converter and cannot disturb fixed voice voltage |
| `EXT_BUCK_SW` | `ext_buck.SW` | `ext_inductor.END_1` | 4.7-uH exact first target limits ripple while preserving the 2-A transient envelope |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_efuse.IN` | the eFuse is the final series element before the externally accessible connector |
| `EXT_5V_FB` | `abstract:ext-5v-feedback-divider` | `ext_buck.FB` | fixed 5.0-V divider; no shared voice/accessory selector exists |
| `EXT_5V_PG_N` | `ext_buck.PG` | `ext_pg_qualifier.E` | the open-drain PG emitter input is qualified by the same STOP-dominant enable request; PG is pulled up only inside the powered 3V3_MAIN diagnostic domain |
| `EXT_5V_FAULT_QUAL_N` | `ext_pg_qualifier.C` | `abstract:power-current-thermal-fault` | open collector sinks only for EN=1 and PG=0; a normally disabled accessory converter releases POWER_FAULT_N |
| `5V_EXT_PROTECTED` | `ext_efuse.OUT` | `u214.5V_IN` | true reverse-current blocking, bounded inrush and active current limit sit between the connector and converter |
| `U214_5V_OUT_NC` | `u214.5V_OUT` | `abstract:no-connect` | the base is the only source in this profile; the cap output contact is not paralleled back into the protected rail |
| `EXT_EFUSE_FAULT_N` | `ext_efuse.FLT` | `abstract:power-current-thermal-fault` | active-low open-drain current/thermal/voltage fault joins POWER_FAULT_N |
| `EXT_5V_CURRENT_MONITOR` | `ext_efuse.ILM` | `abstract:TP_EXT_5V_ILM` | analog current evidence is accessible at a protected test point without consuming another MCU GPIO |
| `EXT_EFUSE_ILM_SET` | `ext_efuse.ILM` | `ext_rilm.END_1` | 2.21-kOhm 1% resistor sets a nominal 1.509-A current limit that is active during startup and steady operation |
| `POWER_GROUND` | `ext_rilm.END_2` | `abstract:power-ground` | short quiet return preserves the current-limit accuracy |
| `EXT_EFUSE_DVDT` | `ext_efuse.DVDT` | `ext_dvdt_cap.END_1` | 4.7-nF 10% capacitor controls the startup slew instead of relying on ITIMER |
| `POWER_GROUND` | `ext_dvdt_cap.END_2` | `abstract:power-ground` | local return completes the controlled-slew network |
| `EXT_EFUSE_ITIMER` | `ext_efuse.ITIMER` | `ext_itimer_cap.END_1` | 220-nF 10% capacitor bounds only post-start operation between ILIM and 2xILIM; it does not defer startup limiting |
| `POWER_GROUND` | `ext_itimer_cap.END_2` | `abstract:power-ground` | local return completes the post-start transient timer |
| `5V_EXT_PREPROTECT` | `ext_efuse.IN` | `ext_ovlo_top.END_1` | 169-kOhm 1% top element begins the fixed OVLO divider |
| `EXT_EFUSE_OVLO_SENSE` | `ext_ovlo_top.END_2` | `ext_efuse.OVLO` | divider sets about 5.515-V nominal input overvoltage cutoff |
| `EXT_EFUSE_OVLO_SENSE` | `ext_efuse.OVLO` | `ext_ovlo_bottom.END_1` | 47-kOhm 1% bottom element completes the fixed OVLO divider |
| `POWER_GROUND` | `ext_ovlo_bottom.END_2` | `abstract:power-ground` | fixed OVLO return has no firmware-controlled overvoltage setting |
| `5V_EXT_PREPROTECT` | `ext_efuse.IN` | `ext_input_cap.END_1` | local 2.2-uF 25-V X7R capacitor exceeds the eFuse input bypass minimum and retains voltage-rating margin |
| `POWER_GROUND` | `ext_input_cap.END_2` | `abstract:power-ground` | input bypass return stays local to the eFuse high-current path |
| `5V_EXT_PROTECTED` | `ext_efuse.OUT` | `ext_output_cap.END_1` | local 2.2-uF 25-V X7R capacitor provides the required close output capacitance |
| `POWER_GROUND` | `ext_output_cap.END_2` | `abstract:power-ground` | output bypass return stays local to the eFuse high-current path |
| `5V_EXT_PROTECTED` | `ext_efuse.OUT` | `ext_bleeder.END_1` | 1-kOhm 1% bleeder discharges the unplugged connector without creating an external backfeed sink path |
| `POWER_GROUND` | `ext_bleeder.END_2` | `abstract:power-ground` | 5-mA nominal passive discharge remains active whenever protected 5 V is present |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `nrf_power_switch.IN` | one 1.5-A protected branch serves all three simultaneously active nRF modules |
| `3V3_NRF_GROUP` | `nrf_power_switch.VOUT` | `nrf0.VCC` | all three modules share one commanded quiet-state domain but retain independent data, CE and IRQ |
| `3V3_NRF_GROUP` | `nrf_power_switch.VOUT` | `nrf1.VCC` | full three-radio PTX/PRX mix remains an accepted simultaneous load |
| `3V3_NRF_GROUP` | `nrf_power_switch.VOUT` | `nrf2.VCC` | full three-radio PTX/PRX mix remains an accepted simultaneous load |
| `NRF_QOD` | `nrf_power_switch.QOD` | `nrf_power_switch.VOUT` | internal 24-Ohm discharge removes the unused radio rail; capacitance and fall time remain HIL gates |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `cc_power_switch.IN` | compatibility radio receives an independent reset-off branch |
| `3V3_CC_SWITCHED` | `cc_power_switch.VOUT` | `abstract:cc-filtered-3v3` | exact RF decoupling/matching follows the switch and remains an I6 circuit gate |
| `CC_QOD` | `cc_power_switch.QOD` | `cc_power_switch.VOUT` | internal discharge produces a measured quiet state |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_power_switch.IN` | storage inrush and faults are isolated from the shared compute rail |
| `3V3_SD_SWITCHED` | `sd_power_switch.VOUT` | `sd.VDD` | card rail is enabled only for a bounded mounted storage session |
| `SD_QOD` | `sd_power_switch.QOD` | `sd_power_switch.VOUT` | rail discharges after a qualified flush/unmount sequence |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `codec_power_switch.IN` | codec branch is independently reset-off and cannot back-power the common I2C/I2S buses |
| `3V3_CODEC_SWITCHED` | `codec_power_switch.VOUT` | `abstract:qualified-codec-3v3-digital` | digital and analog filtering split only after the exact protected load switch |
| `3V3_CODEC_SWITCHED` | `codec_power_switch.VOUT` | `abstract:qualified-codec-3v3-analog` | analog filtering and return-current geometry remain a schematic/HIL gate |
| `CODEC_QOD` | `codec_power_switch.QOD` | `codec_power_switch.VOUT` | powered-off codec rail is actively discharged before interface isolation is relaxed |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `receiver_power_switch.IN` | receive-only radio has its own reset-off branch for desense control |
| `3V3_RECEIVER_SWITCHED` | `receiver_power_switch.VOUT` | `receiver.VDD` | local filtering and RST sequencing follow the exact switch |
| `RECEIVER_QOD` | `receiver_power_switch.QOD` | `receiver_power_switch.VOUT` | powered-off receiver rail is discharged and verified quiet |
| `NRF_SWITCH_NC` | `nrf_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `CC_SWITCH_NC` | `cc_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `SD_SWITCH_NC` | `sd_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `CODEC_SWITCH_NC` | `codec_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `RECEIVER_SWITCH_NC` | `receiver_power_switch.NC` | `abstract:no-connect` | SC70 pin 4 is left floating as required |
| `PD_LOCAL_I2C_SDA` | `pd_config_eeprom.SDA` | `abstract:pd-eeprom-factory-sda-pad` | blank-device programming and recovery remain possible without booted product firmware |
| `PD_LOCAL_I2C_SCL` | `pd_config_eeprom.SCL` | `abstract:pd-eeprom-factory-scl-pad` | blank-device programming and recovery remain possible without booted product firmware |
| `PD_EEPROM_WP` | `pd_config_eeprom.WP` | `abstract:pd-eeprom-factory-wp-pad` | fixture can verify protected and writable states; normal reset state remains protected |
| `U214_I2C_SDA_OUT` | `u214_i2c_iso.SDAOUT` | `u214.SDA` | hot-swap isolation and stuck-low recovery keep the external branch off the controller-side domain |
| `U214_I2C_SCL_OUT` | `u214_i2c_iso.SCLOUT` | `u214.SCL` | hot-swap isolation and stuck-low recovery keep the external branch off the controller-side domain |
| `U214_I2C_ISO_EN` | `abstract:protected-accessory-power-good` | `u214_i2c_iso.EN` | off until protected accessory power is stable |
| `U214_I2C_READY` | `u214_i2c_iso.READY` | `slow_io.P16` | read-only status; no safety function depends on firmware polling |
| `UI_ROW0` | `slow_io.P00` | `abstract:UI_ROW0` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_ROW1` | `slow_io.P01` | `abstract:UI_ROW1` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_ROW2` | `slow_io.P02` | `abstract:UI_ROW2` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_COL0` | `slow_io.P03` | `abstract:UI_COL0` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_COL1` | `slow_io.P04` | `abstract:UI_COL1` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `UI_COL2` | `slow_io.P05` | `abstract:UI_COL2` | diode-isolated 3x3 ordinary-key matrix; reset input-safe |
| `LCD_RST_N` | `slow_io.P06` | `display.RESET` | external reset-safe pull; release only after qualified display rails are stable |
| `TOUCH_RST_N` | `slow_io.P07` | `display.TP_RESET` | external reset-safe pull; exact TP_RESXP polarity and timing require specimen HIL |
| `LCD_VDDI_3V3` | `abstract:qualified-display-3v3` | `display.VDDI` | local decoupling and sequencing remain electrical gates |
| `LCD_VDD_3V3` | `abstract:qualified-display-3v3` | `display.VDD` | local decoupling, inrush and sequencing remain electrical gates |
| `LCD_IM1_HIGH` | `abstract:qualified-display-3v3` | `display.IM1` | fixed QSPI interface strap, matching the reviewed QDtech reference |
| `LCD_IM0_LOW` | `display.IM0` | `abstract:display-ground` | fixed QSPI interface strap, matching the reviewed QDtech reference |
| `LCD_IM2_LOW` | `display.IM2` | `abstract:display-ground` | fixed QSPI interface strap, matching the reviewed QDtech reference |
| `LCD_DB2_LOW` | `display.DB2_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB3_LOW` | `display.DB3_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB4_LOW` | `display.DB4_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB5_LOW` | `display.DB5_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB6_LOW` | `display.DB6_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_DB7_LOW` | `display.DB7_STRAP` | `abstract:display-ground` | unused parallel-data contact tied low, matching the reviewed QDtech reference |
| `LCD_LEDA` | `abstract:qualified-backlight-supply` | `display.LEDA` | production backlight source remains an exact current/thermal/EMI gate |
| `LCD_LEDK` | `display.LEDK_1` | `abstract:qualified-backlight-sink` | all three cathodes terminate on one qualified dimmable sink |
| `LCD_LEDK` | `display.LEDK_2` | `abstract:qualified-backlight-sink` | all three cathodes terminate on one qualified dimmable sink |
| `LCD_LEDK` | `display.LEDK_3` | `abstract:qualified-backlight-sink` | all three cathodes terminate on one qualified dimmable sink |
| `CODEC_PWR_EN` | `slow_io.P10` | `codec_power_switch.ON` | external off-safe pull; ES8311 has no hardware enable/reset pin and CE is only the I2C address strap |
| `CODEC_PVDD` | `abstract:qualified-codec-3v3-digital` | `codec.PVDD` | switched quiet rail with local decoupling; no back-power through I2C/I2S when off |
| `CODEC_DVDD` | `abstract:qualified-codec-3v3-digital` | `codec.DVDD` | switched quiet rail with local decoupling and manufacturer-valid sequencing |
| `CODEC_AVDD` | `abstract:qualified-codec-3v3-analog` | `codec.AVDD` | filtered switched analog rail; return-current and RF-noise layout remain gates |
| `CODEC_DGND` | `codec.DGND` | `abstract:codec-digital-ground` | joined to audio ground at the reviewed single-point/plane boundary |
| `CODEC_AGND` | `codec.AGND` | `abstract:codec-audio-ground` | quiet analog return |
| `CODEC_EPAD_AGND` | `codec.EPAD` | `abstract:codec-audio-ground` | manufacturer user guide requires the exposed thermal pad on audio ground |
| `CODEC_DACVREF` | `abstract:codec-dacvref-decoupling` | `codec.DACVREF` | exact capacitor/value/layout follow current product brief and HIL |
| `CODEC_ADCVREF` | `abstract:codec-adcvref-decoupling` | `codec.ADCVREF` | exact capacitor/value/layout follow current product brief and HIL |
| `CODEC_VMID` | `abstract:codec-vmid-decoupling` | `codec.VMID` | quiet local reference; not a general-purpose rail |
| `CODEC_I2C_ADDR_0X19` | `abstract:codec-address-high-3v3` | `codec.CE` | 10 kOhm reference strap selects documented 7-bit address 0x19; complete bus address scan remains HIL |
| `CODEC_MCLK_NC` | `codec.MCLK` | `abstract:no-connect` | current four-wire I2S contract selects BCLK/SCLK as internal master-clock source; no hidden S3 GPIO |
| `RX_AUDIO_L` | `receiver.LOUT_DFS` | `abstract:si4732-10k-left-mono-sum` | 10-kOhm-class summing branch; exact source level, capacitor and impedance remain schematic/HIL gates |
| `RX_AUDIO_R` | `receiver.ROUT_DOUT` | `abstract:si4732-10k-right-mono-sum` | 10-kOhm-class summing branch; exact source level, capacitor and impedance remain schematic/HIL gates |
| `RX_SI4732_MONO` | `abstract:si4732-passive-mono-sum-output` | `audio_rx_mux.B1` | logic-low/default receive source; component values and low-band response remain schematic/HIL gates |
| `RX_SA518_AFOUT` | `voice.AFOUT` | `audio_rx_mux.B2` | voice receive source; muted and isolated before voice rail transitions |
| `RX_AUDIO_SOURCE_SEL` | `slow_io.P27` | `audio_rx_mux.S` | ordinary non-TX source selection; external pull-down selects Si4732 B1 at reset |
| `AUDIO_RX_MUX_VCC` | `abstract:always-available-quiet-audio-rail` | `audio_rx_mux.VCC` | selector remains available independently of codec power |
| `AUDIO_RX_MUX_GND` | `audio_rx_mux.GND` | `abstract:audio-ground` | quiet analog return |
| `RX_AUDIO_SELECTED` | `audio_rx_mux.A_COM` | `abstract:rx-audio-bypass-and-capture-node` | one selected RX source feeds independent bypass and high-impedance capture branches |
| `SPK_BYPASS_P` | `abstract:rx-audio-bypass-and-capture-node` | `audio_speaker_selector.S1B` | logic-low/default path; qualified AC coupling and PAM input network remain schematic gates |
| `SPK_BYPASS_M` | `abstract:matched-bypass-ac-reference` | `audio_speaker_selector.S2B` | matched AC reference for PAM differential input in ordinary bypass mode |
| `CODEC_CAPTURE_TAP` | `abstract:rx-audio-bypass-and-capture-node` | `abstract:high-z-ac-coupled-capture-network` | 100-kOhm-class source-loading target; exact bias, capacitor and RF filter remain schematic/HIL gates |
| `CODEC_CAPTURE_BUFFER_IN` | `abstract:high-z-ac-coupled-capture-network` | `audio_capture_buffer.IN_PLUS` | biased inside TLV9061 valid common-mode range; no source back-power when codec branch is off |
| `CODEC_CAPTURE_BUFFER_FB` | `audio_capture_buffer.OUT` | `audio_capture_buffer.IN_MINUS` | unity-gain baseline; qualified gain may change only with repeated analog review |
| `CODEC_CAPTURE_BUFFER_VCC` | `abstract:qualified-codec-3v3-analog` | `audio_capture_buffer.V_PLUS` | switched with codec analog domain; input series network prevents powered-off loading/back-power |
| `CODEC_CAPTURE_BUFFER_GND` | `audio_capture_buffer.V_MINUS` | `abstract:codec-audio-ground` | quiet analog return |
| `CODEC_CAPTURE_BUFFER_OUT` | `audio_capture_buffer.OUT` | `abstract:qualified-es8311-mic-range-differential-input-network` | buffer output is AC-coupled, biased and attenuated into a manufacturer-valid ES8311 microphone-range interface |
| `CODEC_ADC_IN_P` | `abstract:qualified-es8311-mic-range-differential-input-network` | `codec.MIC1P` | exact gain, common mode, AC coupling and anti-RF values remain schematic/HIL gates |
| `CODEC_ADC_IN_N` | `abstract:qualified-es8311-mic-range-differential-input-network` | `codec.MIC1N` | matched reference and conditioning remain an exact schematic/HIL gate |
| `CODEC_DAC_OUT_P` | `codec.OUTP` | `audio_speaker_selector.S1A` | full differential DAC positive leg; never grounded or silently discarded |
| `CODEC_DAC_OUT_N` | `codec.OUTN` | `audio_speaker_selector.S2A` | full differential DAC negative leg |
| `PAM_AUDIO_IN_P` | `audio_speaker_selector.D1` | `speaker_amp.IN_PLUS` | paired selector poles always change together under one safe control |
| `PAM_AUDIO_IN_M` | `audio_speaker_selector.D2` | `speaker_amp.IN_MINUS` | paired selector poles always change together under one safe control |
| `AUDIO_SPK_SEL_VCC` | `abstract:always-available-quiet-audio-rail` | `audio_speaker_selector.VDD` | selector remains powered while codec rail is off so analog bypass survives |
| `AUDIO_SPK_SEL_GND` | `audio_speaker_selector.GND` | `abstract:audio-ground` | quiet analog return |
| `PAM_VDD` | `abstract:qualified-speaker-amp-supply` | `speaker_amp.VDD` | exact rail, decoupling, current and EMI remain schematic/HIL gates |
| `PAM_GND` | `speaker_amp.GND` | `abstract:audio-ground` | short quiet return; class-D output currents stay out of codec input return |
| `PAM_SD` | `abstract:qualified-speaker-enable-default-on` | `speaker_amp.SD` | ordinary bypass remains available after reset; startup pop and fault behavior remain HIL gates |
| `PAM_NC` | `speaker_amp.NC` | `abstract:no-connect` | physical MSOP-8 pin 2 is no-connect |
| `SPEAKER_P` | `speaker_amp.VO_PLUS` | `abstract:speaker-positive` | BTL/class-D output; never tie to ground |
| `SPEAKER_M` | `speaker_amp.VO_MINUS` | `abstract:speaker-negative` | BTL/class-D output; never tie to ground |
| `CODEC_TX_DAC_TAP` | `codec.OUTP` | `abstract:codec-dac-to-sa518-35-45db-attenuator` | separate high-impedance AC-coupled low-pass branch; exact attenuation is set by measured SA518 deviation |
| `VOICE_CODEC_INJECT` | `abstract:codec-dac-to-sa518-35-45db-attenuator` | `audio_tx_selector.NO` | codec injection is the non-default selected input |
| `VOICE_ELECTRET_DEFAULT` | `abstract:electret-microphone-bias-and-ac-coupling` | `audio_tx_selector.NC` | logic-low/default path preserves ordinary microphone operation |
| `VOICE_MIC_IN` | `audio_tx_selector.COM` | `voice.MIC_IN` | audio selection cannot assert PTT; input level and deviation remain measured gates |
| `AUDIO_TX_SEL_VCC` | `abstract:always-available-quiet-audio-rail` | `audio_tx_selector.VCC` | selector remains powered independently of codec rail |
| `AUDIO_TX_SEL_GND` | `audio_tx_selector.GND` | `abstract:audio-ground` | quiet analog return |
| `AUDIO_SPK_CODEC_REQ` | `slow_io.P11` | `audio_safe_gate.1A` | external pull-down requests ordinary analog bypass while expander is input or high-Z |
| `AUDIO_TX_CODEC_REQ` | `slow_io.P12` | `audio_safe_gate.2A` | external pull-down requests electret default while expander is input or high-Z |
| `AUDIO_SPK_SEL_SAFE` | `audio_safe_gate.1Y` | `audio_speaker_selector.SEL1` | low selects bypass S1B; external pull-down holds default if gate rail is absent |
| `AUDIO_SPK_SEL_SAFE` | `audio_safe_gate.1Y` | `audio_speaker_selector.SEL2` | both differential poles share the same reset-safe control |
| `AUDIO_TX_SEL_SAFE` | `audio_safe_gate.2Y` | `audio_tx_selector.IN` | low selects normally-closed electret path; external pull-down holds default if gate rail is absent |
| `AUDIO_SAFE_GATE_VCC` | `abstract:always-available-quiet-audio-rail` | `audio_safe_gate.VCC` | gate and selectors share a sequenced always-available rail |
| `AUDIO_SAFE_GATE_GND` | `audio_safe_gate.GND` | `abstract:audio-ground` | quiet logic return |
| `VOICE_DOMAIN_REQ` | `slow_io.P13` | `safe_gate_b.2A` | request only; RUN_PERMIT and a 10-kOhm output pull-down make the downstream rail enable STOP-dominant |
| `VOICE_PD_N` | `abstract:voice-power-reset-domain` | `voice.PD` | off-safe sequencer keeps the exact module in power-down until the qualified 4 V rail is valid |
| `VOICE_HL` | `slow_io.P14` | `voice.HL` | external conservative-power pull |
| `VOICE_UPDATE` | `voice.UPDATE` | `abstract:voice-update-fixture` | fixture-only; no runtime drive until the rev-1.1 direction/description conflict is resolved by specimen proof |
| `RX_DOMAIN_EN` | `slow_io.P15` | `receiver_power_switch.ON` | off-safe pull; exact switch removes receiver power while the following reset/isolation circuit prevents I2C back-power |
| `RX_DOMAIN_POWER_VALID` | `receiver_power_switch.VOUT` | `abstract:receiver-power-reset-isolation` | reset remains asserted until switched power and I2C isolation are valid |
| `RX_RST_N` | `abstract:receiver-power-reset-isolation` | `receiver.RST` | reset remains asserted until the qualified receiver rail and I2C isolation are valid |
| `RX_STATUS_N` | `receiver.GPO2_INTB` | `slow_io.P24` | exact interrupt source; bounded latency and pulse width remain HIL gates |
| `RX_SENB_I2C` | `abstract:i2c-mode-strap` | `receiver.SENB` | fixed reset strap selects the reviewed two-wire control mode |
| `RX_RCLK` | `abstract:qualified-32k-clock` | `receiver.RCLK` | clock source and startup remain exact electrical gates |
| `RX_FMI_RF` | `receiver.FMI` | `abstract:RX-FM-SW-SMA-front-end` | dedicated external-SMA whip path; matching/ESD stays close to FMI |
| `RX_AMI_RF` | `receiver.AMI` | `abstract:RX-AM-LW-loop-pod` | dedicated short loop/pod path; generic long coax is not qualified |
| `EXT_5V_REQ` | `slow_io.P17` | `safe_gate_b.4A` | request only; RUN_PERMIT gates the reverse-safe/current-limited accessory power stage selected in I3/I7 |
| `SD_PWR_EN` | `slow_io.P20` | `sd_power_switch.ON` | external off-safe pull; the exact switch controls inrush and short faults |
| `SD_CARD_DETECT_N` | `sd.DETECT_A` | `slow_io.P21` | read-only debounced input; socket switch return is tied to the qualified reference domain |
| `STOP_LATCH_SENSE` | `safe_latch.Q` | `slow_io.P22` | diagnostic mirror only; non-programmable hard-stop dominance never depends on the expander |
| `S3_RF_TX_EVIDENCE_N` | `evidence_cmp_a.OUT1` | `slow_io.P23` | direct read-only mirror of the exact S3 evidence comparator |
| `POWER_FAULT_N` | `abstract:power-current-thermal-fault` | `slow_io.P25` | hardware protection acts independently; this is diagnostic evidence |
| `ACCESSORY_PRESENT_N` | `abstract:accessory-present` | `slow_io.P26` | read-only, protected and debounced |
| `AON_SAFE_3V3` | `abstract:AON_SAFE_3V3` | `safe_supervisor.VDD` | always-on source and hold-up are selected and budgeted in I3 |
| `AON_SAFE_SENSE` | `abstract:AON_SAFE_3V3` | `safe_supervisor.SENSE` | factory G33 threshold supervises the actual safety rail |
| `AON_MR_N` | `abstract:AON_SAFE_3V3-via-10k` | `safe_supervisor.MR_N` | no firmware-controlled manual reset path |
| `POR_N` | `abstract:AON_SAFE_3V3-via-10k` | `safe_supervisor.RESET_N` | open-drain supervisor output is pulled up only to AON_SAFE_3V3 |
| `POR_N` | `safe_supervisor.RESET_N` | `safe_por_or.1A` | power-good clear input; STOP remains dominant through the second OR input |
| `STOP_LOOP_SENSE` | `abstract:NC-stop-loop-10k-pullup-10nF` | `safe_conditioner.1A` | healthy closed contact is low; press, disconnect or open wire is high |
| `STOP_LOOP_SENSE` | `abstract:NC-stop-loop-10k-pullup-10nF` | `safe_por_or.1B` | high forces CLR_N inactive so preset and clear cannot be asserted together |
| `STOP_ASSERT_N` | `safe_conditioner.1Y` | `safe_latch.PRE_N` | active-low asynchronous preset; software and clocks are outside the path |
| `REARM_RAW` | `abstract:NO-rearm-loop-47k-pullup-100nF` | `safe_conditioner.2A` | fresh press pulls raw input low and produces one or more harmless rising edges at the Schmitt output |
| `REARM_CLK` | `safe_conditioner.2Y` | `safe_latch.CLK` | only a fresh physical edge can clock fixed D=0 |
| `STOP_DOMINANT_CLR_N` | `safe_por_or.1Y` | `safe_latch.CLR_N` | CLR_N = POR_N OR STOP_LOOP_SENSE |
| `SAFE_D_LOW` | `abstract:safety-ground-via-10k` | `safe_latch.D` | fixed logic low; no MCU, expander or connector endpoint |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_reset_buffer.1A` | one non-programmable permit fans out through an Ioff buffer |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_reset_buffer.2A` | one non-programmable permit fans out through an Ioff buffer |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_reset_buffer.3A` | one non-programmable permit fans out through an Ioff buffer |
| `S3_RUN_SAFE` | `safe_reset_buffer.1Y` | `s3.EN` | 47-Ohm series plus 1-kOhm target pull-down; AON loss holds CHIP_PU low |
| `C5_RUN_SAFE` | `safe_reset_buffer.2Y` | `c5.EN` | 47-Ohm series plus 1-kOhm target pull-down; AON loss holds CHIP_PU low |
| `RP_RUN_SAFE` | `safe_reset_buffer.3Y` | `rp.RUN` | 47-Ohm series plus 1-kOhm target pull-down; AON loss holds RUN low |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_a.1B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_a.2B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_a.3B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_a.4B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_b.1B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_b.2B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_b.3B` | STOP-dominant active-high gate permit |
| `RUN_PERMIT` | `safe_latch.Q_N` | `safe_gate_b.4B` | STOP-dominant active-high gate permit |
| `NRF0_CE_SAFE` | `safe_gate_a.1Y` | `nrf0.CE` | 10-kOhm module-side pull-down; STOP and AON loss force CE low |
| `NRF1_CE_SAFE` | `safe_gate_a.2Y` | `nrf1.CE` | 10-kOhm module-side pull-down; STOP and AON loss force CE low |
| `NRF2_CE_SAFE` | `safe_gate_a.3Y` | `nrf2.CE` | 10-kOhm module-side pull-down; STOP and AON loss force CE low |
| `NRF_GROUP_PWR_EN_SAFE` | `safe_gate_a.4Y` | `nrf_power_switch.ON` | 10-kOhm pull-down; STOP and AON loss disable the exact protected load switch |
| `CC_PWR_EN_SAFE` | `safe_gate_b.1Y` | `cc_power_switch.ON` | 10-kOhm pull-down; STOP and AON loss disable the exact protected load switch |
| `VOICE_DOMAIN_EN_SAFE` | `safe_gate_b.2Y` | `voice_buck.EN` | 10-kOhm pull-down; STOP and AON loss disable the independent fixed 4-V converter |
| `VOICE_DOMAIN_EN_SAFE` | `safe_gate_b.2Y` | `voice_pg_qualifier.B` | 68-kOhm 1% series base resistor qualifies voice PG without adding a GPIO |
| `IR_TX_CARRIER_SAFE` | `safe_gate_b.3Y` | `abstract:fail-safe-IR-LED-driver` | carrier waveform is physically blocked whenever RUN_PERMIT is low |
| `EXT_5V_EN_SAFE` | `safe_gate_b.4Y` | `ext_buck.EN` | 10-kOhm pull-down; STOP and AON loss disable the dedicated 5-V converter |
| `EXT_5V_EN_SAFE` | `safe_gate_b.4Y` | `ext_pg_qualifier.B` | 68-kOhm 1% series base resistor qualifies accessory PG without adding a GPIO |
| `EXT_5V_EN_SAFE` | `safe_gate_b.4Y` | `ext_efuse.EN_UVLO` | the same STOP-dominant request also disables the connector-side true-reverse-blocking eFuse |
| `TX_KILL` | `safe_latch.Q` | `safe_ptt_or.1B` | active-high kill forces active-low PTT high/RX |
| `VOICE_PTT_SAFE_N` | `safe_ptt_or.1Y` | `voice.PTT` | 10-kOhm module-side pull-up keeps RX when the AON gate is unpowered |
| `STOP_LED_DRIVE` | `safe_latch.Q` | `abstract:stop-led-series-2k2` | non-programmable visible latched-stop state |
| `STOP_LED_A` | `abstract:stop-led-series-2k2` | `stop_led.A` | 2.2-kOhm first-target current limit |
| `STOP_LED_K` | `stop_led.K` | `abstract:safety-ground` | indicator stays outside UI and firmware |
| `S3_RF_SAMPLE` | `abstract:S3-qualified-RF-tap` | `det_s3.RFIN` | tap/attenuation is selected and measured in I6 |
| `C5_RF_SAMPLE` | `abstract:C5-qualified-RF-tap` | `det_c5.RFIN` | tap covers the qualified 2.4/5-GHz path; I6 sets attenuation |
| `NRF0_RF_SAMPLE` | `abstract:NRF0-qualified-RF-tap` | `det_nrf0.RFIN` | one source-specific tap; never shared with nRF1/2 |
| `NRF1_RF_SAMPLE` | `abstract:NRF1-qualified-RF-tap` | `det_nrf1.RFIN` | one source-specific tap; never shared with nRF0/2 |
| `NRF2_RF_SAMPLE` | `abstract:NRF2-qualified-RF-tap` | `det_nrf2.RFIN` | one source-specific tap; never shared with nRF0/1 |
| `CC_RF_SAMPLE` | `abstract:CC-qualified-RF-tap` | `det_cc.RFIN` | sub-GHz tap and coupling capacitor are selected in I6 |
| `VOICE_RF_SAMPLE` | `abstract:VOICE-qualified-RF-tap` | `det_voice.RFIN` | VHF/UHF tap and coupling capacitor are selected in I6 |
| `CC_DETECT_ENABLE` | `abstract:AON_SAFE_3V3` | `det_cc.SHDN` | evidence detector remains enabled independently of the CC application rail |
| `VOICE_DETECT_ENABLE` | `abstract:AON_SAFE_3V3` | `det_voice.SHDN` | evidence detector remains enabled independently of the voice application rail |
| `IR_OPTICAL_SAMPLE` | `det_ir.ANODE` | `abstract:shielded-ir-evidence-front-end` | physical optical pickup rather than drive-current inference; exact bias/front end is I6 |
| `S3_DETECT_V` | `det_s3.VOUT` | `evidence_cmp_a.IN1_N` | RF above the qualified threshold makes active-low comparator output assert |
| `C5_DETECT_V` | `det_c5.VOUT` | `evidence_cmp_a.IN2_N` | RF above the qualified threshold makes active-low comparator output assert |
| `NRF0_DETECT_V` | `det_nrf0.VOUT` | `evidence_cmp_a.IN3_N` | RF above the qualified threshold makes active-low comparator output assert |
| `NRF1_DETECT_V` | `det_nrf1.VOUT` | `evidence_cmp_a.IN4_N` | RF above the qualified threshold makes active-low comparator output assert |
| `NRF2_DETECT_V` | `det_nrf2.VOUT` | `evidence_cmp_b.IN1_N` | RF above the qualified threshold makes active-low comparator output assert |
| `CC_DETECT_V` | `det_cc.VOUT` | `evidence_cmp_b.IN2_N` | RF above the qualified threshold makes active-low comparator output assert |
| `VOICE_DETECT_V` | `det_voice.VOUT` | `evidence_cmp_b.IN3_N` | RF above the qualified threshold makes active-low comparator output assert |
| `IR_DETECT_V` | `abstract:shielded-ir-evidence-front-end` | `evidence_cmp_b.IN4_N` | optical energy above the qualified threshold makes active-low comparator output assert |
| `EV_THRESH_0` | `abstract:qualified-evidence-threshold-0` | `evidence_cmp_a.IN1_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_1` | `abstract:qualified-evidence-threshold-1` | `evidence_cmp_a.IN2_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_2` | `abstract:qualified-evidence-threshold-2` | `evidence_cmp_a.IN3_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_3` | `abstract:qualified-evidence-threshold-3` | `evidence_cmp_a.IN4_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_4` | `abstract:qualified-evidence-threshold-4` | `evidence_cmp_b.IN1_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_5` | `abstract:qualified-evidence-threshold-5` | `evidence_cmp_b.IN2_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_6` | `abstract:qualified-evidence-threshold-6` | `evidence_cmp_b.IN3_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_THRESH_7` | `abstract:qualified-evidence-threshold-7` | `evidence_cmp_b.IN4_P` | divider/hysteresis values are I6 calibration outputs |
| `EV_N0_S3` | `evidence_cmp_a.OUT1` | `evidence_mask.P0` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N1_C5` | `evidence_cmp_a.OUT2` | `evidence_mask.P1` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N2_NRF0` | `evidence_cmp_a.OUT3` | `evidence_mask.P2` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N3_NRF1` | `evidence_cmp_a.OUT4` | `evidence_mask.P3` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N4_NRF2` | `evidence_cmp_b.OUT1` | `evidence_mask.P4` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N5_CC` | `evidence_cmp_b.OUT2` | `evidence_mask.P5` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N6_VOICE` | `evidence_cmp_b.OUT3` | `evidence_mask.P6` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N7_IR` | `evidence_cmp_b.OUT4` | `evidence_mask.P7` | 10-kOhm AON pull-up; individually readable active-low evidence |
| `EV_N0_S3` | `evidence_cmp_a.OUT1` | `evidence_or_0.K1` | diode-isolated hardware aggregate |
| `EV_N1_C5` | `evidence_cmp_a.OUT2` | `evidence_or_0.K2` | diode-isolated hardware aggregate |
| `EV_N2_NRF0` | `evidence_cmp_a.OUT3` | `evidence_or_1.K1` | diode-isolated hardware aggregate |
| `EV_N3_NRF1` | `evidence_cmp_a.OUT4` | `evidence_or_1.K2` | diode-isolated hardware aggregate |
| `EV_N4_NRF2` | `evidence_cmp_b.OUT1` | `evidence_or_2.K1` | diode-isolated hardware aggregate |
| `EV_N5_CC` | `evidence_cmp_b.OUT2` | `evidence_or_2.K2` | diode-isolated hardware aggregate |
| `EV_N6_VOICE` | `evidence_cmp_b.OUT3` | `evidence_or_3.K1` | diode-isolated hardware aggregate |
| `EV_N7_IR` | `evidence_cmp_b.OUT4` | `evidence_or_3.K2` | diode-isolated hardware aggregate |
| `RP_ANY_TX_N` | `evidence_or_0.A_COMMON` | `evidence_or_1.A_COMMON` | common anodes form the active-low aggregate without merging source lines |
| `RP_ANY_TX_N` | `evidence_or_1.A_COMMON` | `evidence_or_2.A_COMMON` | common anodes form the active-low aggregate without merging source lines |
| `RP_ANY_TX_N` | `evidence_or_2.A_COMMON` | `evidence_or_3.A_COMMON` | common anodes form the active-low aggregate without merging source lines |
| `ANY_TX_LED_A` | `abstract:AON_SAFE_3V3-via-2k2` | `any_tx_led.A` | red physical indicator current is sunk by the asserting comparator through one Schottky diode |
| `EVIDENCE_MASK_INT_N_TP` | `evidence_mask.INT_N` | `abstract:TP_EVIDENCE_MASK_INT_N` | test point only; no safety claim depends on expander interrupt behavior |
| `EVIDENCE_ADDR_A0_LOW` | `abstract:safety-ground` | `evidence_mask.A0` | fixed 7-bit address 0x20 |
| `EVIDENCE_ADDR_A1_LOW` | `abstract:safety-ground` | `evidence_mask.A1` | fixed 7-bit address 0x20 |
| `EVIDENCE_ADDR_A2_LOW` | `abstract:safety-ground` | `evidence_mask.A2` | fixed 7-bit address 0x20 |

### Programming, recovery and diagnostics

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20`, `GPIO43`, `GPIO44` — native USB Serial/JTAG, permanent default UART0 RF-test/diagnostic route and physical EN/BOOT.
- `c5`: `EN`, `GPIO28`, `GPIO27`, `GPIO11`, `GPIO12`, `GPIO13`, `GPIO14` — native USB Serial/JTAG, permanent UART0, physical CHIP_PU/BOOT and normal-boot/log strap; 1-bit SDIO leaves USB contacts independent.
- `rp`: `RUN`, `SWCLK`, `SWDIO`, `USB_DM`, `USB_DP`, `QSPI_SS_USB_BOOT` — independent SWD, RUN, USB and BOOTSEL fixture access.
- `pd_controller`: `I2Ct_SDA`, `I2Ct_SCL`, `I2Ct_IRQ` — S3 shared SYS_I2C0 host control plus shared wired-low IRQ; same bus is exposed on protected service pads for controller status/recovery.
- `pd_config_eeprom`: `SDA`, `SCL`, `WP` — direct factory pads permit first-image programming and recovery independent of S3/TPS application state; GND and qualified 3.3 V accompany the fixture.
- `pack_gauge`: `ALRT`, `SCL_OD`, `SDA_DQ`, `PFAIL` — direct protected I2C/NVM and hold/fault pads with fixture ground and qualified stack-sense supply; protected image checksum and OvrdEn readback are mandatory before energized cell installation.
- `pack_admission`: `PA1_NRST`, `PA17`, `PA18_A7`, `PA19_SWDIO`, `PA20_A6_SWCLK`, `VDD`, `VSS` — permanent NRST/SWD/UART plus isolated fixture VDD/VSS; fixture or admitted system rail powers flash programming because MAX17320 AOLDO is not sized for it.
- `voice`: `UPDATE`, `UART_TX`, `UART_RX`, `PD` — permanent fixture breakout for vendor update/recovery plus UART and hardware power-down; UPDATE drive remains inhibited until exact rev-1.1 direction/timing proof.

### Non-MCU contact accounting

| Instance | Used | Reserved | Free |
|---|---:|---:|---:|
| `slow_io` | 24 | 0 | 0 |

### Interface non-interference contracts

| Resource | Owner | Clients | Sharing | Deadline / bound | Proof gate |
|---|---|---|---|---|---|
| `NRF0_SPI` | `rp` | `nrf0` | dedicated | IRQ serviced before nRF FIFO/transaction deadline under simultaneous peers | PIO0 SM0 plus dedicated DMA/IRQ stress HIL |
| `NRF1_SPI` | `rp` | `nrf1` | dedicated | IRQ serviced before nRF FIFO/transaction deadline under simultaneous peers | PIO0 SM1 plus dedicated DMA/IRQ stress HIL |
| `NRF2_SPI` | `rp` | `nrf2` | dedicated | IRQ serviced before nRF FIFO/transaction deadline under simultaneous peers | PIO0 SM2 plus dedicated DMA/IRQ stress HIL |
| `CC_SPI` | `rp` | `cc` | dedicated | GDO/FIFO service completes without waiting for any nRF or U214 transfer | PIO0 SM3 plus dedicated DMA/IRQ stress HIL |
| `U214_SPI` | `rp` | `u214` | dedicated | LoRa BUSY/IRQ transaction never waits for display or compatibility-radio bus ownership | PIO1 SM0 plus dedicated DMA/IRQ stress HIL |
| `U214_UART` | `rp` | `u214` | dedicated | GNSS receive has continuous hardware UART buffering independent of SPI activity | UART1 DMA/ring overflow stress HIL |
| `U214_I2C` | `rp` | `u214`, `u214_i2c_iso` | dedicated | external stuck-low or hot-plug cannot stall internal UI/audio/receiver I2C | TCA4307 stuck-bus and hot-plug fault-injection HIL |
| `DISPLAY_SD_SPI` | `s3` | `display`, `sd` | scheduled; separate CS and per-device modes/clocks; display non-preemptible SPI2 occupancy <=1 ms with byte quantum derived from measured datasheet-valid payload rate; QSPI only while SD CS is high; bounded SD command/data chunks; critical UI priority | critical/menu first visible response <=100 ms and qualified storage >=4.0 MB/s while all radios capture; no radio FIFO or IPC deadline is placed here | HMX035CTFT-001 direct-QSPI dirty/tiled display, CS-high high-Z/contention proof, 1.5 MB/s record and 250 ms card-stall HIL |
| `S3_RP_IPC` | `s3` | `rp` | dedicated | 20 MHz SPI raw 2.5 MB/s and qualified framed payload >=1.5 MB/s; no display/storage or C5 controller ownership | SPI3 load, alert-to-read <=250 us and aggregate-radio stress HIL |
| `S3_C5_IPC` | `s3` | `c5` | dedicated | 1-bit SDIO at 20 MHz raw 2.5 MB/s with qualified framed payload >=1.5 MB/s, admitted occupancy <=70% and control RTT <=2 ms; no microSD, RP or display controller ownership | single-slot 1-bit SDMMC/SDIO throughput, control-priority, reset recovery and simultaneous Wi-Fi/802.15.4 load HIL; 4-bit fallback only if this gate fails |
| `S3_INTERNAL_I2C` | `s3` | `slow_io`, `display touch`, `codec`, `receiver`, `pd_controller`, `pack_admission` | scheduled; bounded transactions; expander, PD, pack and touch interrupts only wake the service loop; GPIO47 remains free | ordinary UI/control first visible response <=100 ms; PD/pack/fault status is read after shared IRQ, and no radio FIFO or PTT deadline is placed here | ES8311 address/readback and power-off no-backfeed, touch IRQ/reset, PD and pack target-interface recovery, wired-low IRQ source identification, shortest-pulse, matrix and fault-latency HIL |
| `PD_LOCAL_I2C` | `pd_controller` | `pd_config_eeprom`, `nvdc_charger` | scheduled; TPS25751D owns the local bus; EEPROM address 0x50 and exact charger address are collision-checked; factory access is permitted only while the product controller is held inactive | boot image completes before high-voltage negotiation or charge enable; charger faults propagate without depending on display/storage/radio buses | blank/valid/corrupt dual-region EEPROM boots, charger-IRQ latency and signed-update rollback HIL |
| `PACK_LOCAL_I2C` | `pack_admission` | `pack_gauge` | dedicated | gauge identity, protected-NVM checksum, cell/temperature/protection state and diagnostic-pulse samples complete locally before any FET-hold release; S3 availability is irrelevant | bit-banged I2C electrical timing, both MAX17320 address paths, blank/wrong NVM, stuck bus, watchdog/reset and fixture-handover HIL |
| `S3_UNIT_PORT` | `s3` | `abstract:M5 Unit` | dedicated | one selected I2C/UART/GPIO Unit profile cannot be blocked by internal or U214 I2C | profile-switch and external-fault HIL |
| `S3_I2S` | `s3` | `codec` | dedicated | continuous DMA audio without storage/display service gaps | ES8311 BCLK-derived master-clock and simultaneous full-duplex display, SD, C5 and radio event stress HIL |

### Controller GPIO-window selections

| Instance | Controllers | Selected window | Device constraint / reason |
|---|---|---|---|
| `rp` | `PIO0_SM0_RF_SPI`, `PIO0_SM1_RF_SPI`, `PIO0_SM2_RF_SPI`, `PIO0_SM3_RF_SPI` | `GPIO16..GPIO47` | RP2354B PIO0 is fixed to the shared GPIO-base 16 window, so every PIO0 data pin must remain in GPIO16..GPIO47 |
| `rp` | `PIO1_SM0_EXT_SPI` | `GPIO16..GPIO47` | RP2354B PIO1 uses GPIO-base 16 for the U214 data bus |

### Controller/DMA capacity accounting

| Capacity | Instance | Claims | Reserve / available | Basis |
|---|---|---|---:|---|
| `RP_PIO_STATE_MACHINES` | `rp` | nrf0=1, nrf1=1, nrf2=1, cc=1, u214=1 | 7 / 12 | RP2350 provides three PIO blocks with four state machines each; PIO0 consumes four and PIO1 consumes one |
| `RP_DMA_CHANNELS` | `rp` | nrf0 full-duplex PIO SPI=2, nrf1 full-duplex PIO SPI=2, nrf2 full-duplex PIO SPI=2, cc full-duplex PIO SPI=2, u214 full-duplex PIO SPI=2, S3-RP full-duplex SPI1=2, U214 GNSS continuous UART1 RX=1 | 3 / 16 | worst-case persistent allocation leaves three channels for qualified transient/service use; slow UART TX and I2C do not require permanent DMA ownership |
| `S3_GDMA_TX_CHANNELS` | `s3` | display/microSD scheduled SPI2=1, S3-RP SPI3=1, audio I2S0=1 | 2 / 5 | ESP32-S3 has five independent GDMA transmit channels; SD/MMC is not in this GDMA peripheral list |
| `S3_GDMA_RX_CHANNELS` | `s3` | display/microSD scheduled SPI2=1, S3-RP SPI3=1, audio I2S0=1 | 2 / 5 | ESP32-S3 has five independent GDMA receive channels; C5 uses the separate SD/MMC host path |

### Exact fixed-mux contracts

| Contract | Instance/controller | Exact contacts | Datasheet/device proof |
|---|---|---|---|
| `S3_NATIVE_USB` | `s3.USB_SERIAL_JTAG` | `GPIO19`, `GPIO20` | ESP32-S3 native USB D-/D+ fixed contacts on the exact WROOM-1U module |
| `S3_UART0_SERVICE` | `s3.UART0` | `GPIO43`, `GPIO44` | ESP32-S3 default U0TXD/U0RXD contacts are GPIO43/GPIO44 and remain permanently routed for RF-test and diagnostics |
| `C5_FIXED_SDIO` | `c5.SDIO_SLAVE` | `GPIO7`, `GPIO8`, `GPIO9`, `GPIO10` | ESP32-C5 1-bit SDIO slave uses fixed DAT1/IRQ, DAT0, CLK and CMD contacts; GPIO13/14 remain independent native USB |
| `C5_NATIVE_USB` | `c5.USB_SERIAL_JTAG` | `GPIO13`, `GPIO14` | ESP32-C5 native USB D-/D+ fixed contacts are restored by the 1-bit SDIO selection |
| `RP_SPI1_IPC` | `rp.SPI1_IPC` | `GPIO24`, `GPIO25`, `GPIO26`, `GPIO27` | RP2354B bank-0 mux group is SPI1 RX/CSn/SCK/TX |
| `RP_UART0_VOICE` | `rp.UART0` | `GPIO16`, `GPIO17` | RP2354B bank-0 mux pair is UART0 TX/RX |
| `RP_UART1_GNSS` | `rp.UART1` | `GPIO40`, `GPIO41` | RP2354B bank-0 mux pair is UART1 TX/RX |
| `RP_I2C0_U214` | `rp.I2C0_EXT` | `GPIO28`, `GPIO29` | RP2354B bank-0 mux pair is I2C0 SDA/SCL |
| `PACK_SYSTEM_I2C` | `pack_admission.I2C_TARGET` | `PA0`, `PA11` | DGS20 exposes I2C0 SDA on PA0 pin 4 and alternate SCL on PA11 pin 11, preserving PA1/NRST pin 5 |
| `PACK_UART0_SERVICE` | `pack_admission.UART0` | `PA17`, `PA18_A7` | DGS20 exposes UART0 TX/RX on PA17 pin 13 and PA18 pin 14 independently of SWD and reset |

### Open qualification gaps

- `u214_i2c_iso` uses `TCA4307DGKR` as `reference_only`, not an accepted production choice.
- `nrf0` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf0` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf1` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf1` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf2` uses `Ebyte E01-ML01IPX` as `verified_reference`, not an accepted production choice.
- `nrf2` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `voice` lifecycle: `current_product`.
- `receiver` lifecycle: `manufacturer_documented`.
- `slow_io` uses `TCA6424ARGJR` as `reference_only`, not an accepted production choice.
- `sd` lifecycle: `current_manufacturer_page`.
- `display` lifecycle: `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified`.
- `codec` lifecycle: `current manufacturer product brief revision 17.0 dated 2026-02; production sourcing and lot qualification remain open`.
- `audio_rx_mux` uses `Texas Instruments SN74LVC1G3157DBVR` as `verified_reference`, not an accepted production choice.
- `audio_capture_buffer` uses `Texas Instruments TLV9061IDBVR` as `reference_only`, not an accepted production choice.
- `audio_speaker_selector` uses `Texas Instruments TMUX1136DGSR` as `reference_only`, not an accepted production choice.
- `audio_tx_selector` uses `Texas Instruments TS5A63157DCKR` as `reference_only`, not an accepted production choice.
- `audio_safe_gate` uses `Texas Instruments SN74LVC2G08DCUR` as `reference_only`, not an accepted production choice.
- `speaker_amp` uses `Diodes Incorporated PAM8302AASCR` as `verified_reference`, not an accepted production choice.
- `pack_gauge` lifecycle: `recommended_for_new_designs`.
- `safe_conditioner` lifecycle: `production`.
- `safe_por_or` lifecycle: `production`.
- `safe_ptt_or` lifecycle: `production`.
- `det_s3` lifecycle: `production`.
- `det_c5` lifecycle: `production`.
- `det_nrf0` lifecycle: `production`.
- `det_nrf1` lifecycle: `production`.
- `det_nrf2` lifecycle: `production`.
- `det_cc` lifecycle: `production`.
- `det_voice` lifecycle: `production`.
- RP2354B A4 exact lot identity, power/clock/land pattern and prototype assembly remain implementation gates; the verified QFN80 contact map is not a BOM freeze
- E01-ML01S is a geometry/interface reference, not an accepted three-module RF/power/antenna production choice; nRF24 family lifecycle remains not-recommended-for-new-designs
- CC1101 matching, oscillator, antenna path and regional proof are not represented by the bare-IC contact ledger
- TCA6424ARGJR and TCA4307DGKR are real-contact planning references; voltage domains, pulls, address, reset, shortest pulses and exact endpoint MPNs remain electrical/HIL gates
- HMX035CTFT-001 is the exact assembly marking disclosed by the QDtech reference schematic and is instantiated as a paper candidate, not a production-qualified orderable part; exact drawing/FPC mechanics, lifecycle, connector, backlight/protection and specimen HIL remain open
- After DEC-0059 restores full S3/C5 service, S3 retains only GPIO47 free, C5 one and RP none. Slow_io P27 carries RX_AUDIO_SOURCE_SEL, so the 24-line slow plane has no reserve. GPIO47 remains unassigned; any new direct RP endpoint requires an explicit remap and repeated review
- C5 1-bit SDIO has exclusive ownership of the S3 SD/MMC host and leaves C5 native USB GPIO13/14 independent. S3 and C5 each retain both native USB and permanent default UART service; 1-bit framed throughput, control priority and reset recovery remain HIL gates, with 4-bit plus explicit service isolation only as fallback
- display and microSD are the only scheduled high-rate pair on one SPI2 controller; separate CS/per-device clocks and bounded transactions remove radio impact, but >=4.0 MB/s storage plus <=100 ms visible UI under card stalls remains a mandatory HIL gate
- PIO instruction memory, DMA arbitration latency and SRAM-bank contention remain executable firmware/HIL gates even though the state-machine/channel capacity arithmetic closes with explicit reserve
- DEC-0045 prohibits cross-group simultaneous signal operation but requires all three SG-N24 radios concurrently active in every independent PTX/PRX mix; DEC-0047 selects a qualified internal envelope; N24H-0001 L0 DIV-DIV is pre-HIL only and T1 TARGET must prove exact channel/power/sensitivity points
- SG-N24 3PTX is a real accepted load case, so the exact module choice and packet-rail design must prove simultaneous TX peak/average current, droop, thermal, coupling and STOP at the qualified power profile; a former RX-only hunt budget is insufficient
- DEC-0046 consumes RP GPIO15/GPIO23 and C5 GPIO4 for group-level power gates; exact load-switch/isolator MPNs, discharge, no-back-power sequencing and quiet-state EMI HIL remain open, leaving no free direct RP GPIO
- DEC-0054 instantiates ES8311, SN74LVC1G3157DBVR, TLV9061IDBVR, TMUX1136DGSR, TS5A63157DCKR, SN74LVC2G08DCUR and PAM8302AASCR as the prototype audio topology and assigns GPIO6 AUDIO_ARM; exact passive values, powered-off loading, codec power, common-mode/gain, pop/click, RF immunity and HIL remain open before schematic/BOM freeze
- DEC-0063 instantiates TPS25751DREFR, BQ25798RQMR, CAT24C512WI-GT3 and TVS2200DRVR as the sink-only 30-W USB-PD frontend; DEC-0066 adds MAX17320G20+T and MSPM0C1104SDGS20R as the fail-closed 2S manager pair; DEC-0067 disables in-device deep-cell recovery and instantiates the exact switching path. DEC-0068 adds independent fixed TPS629203/TPS564252 AON/3.3/4.0/5.0-V converters, exact Sunlord inductors and five TPS22919 quiet-state switches; DEC-0069 corrects the connector eFuse to latch-off TPS259470LRPWR; DEC-0070 adds two exact MMBT3904-7-F PG qualifiers; DEC-0071 adds eight exact eFuse passives, an immediately active 1.509-A limit, controlled startup and a bounded post-start 2-A transient. Exact USB-C/USB2 protection, charger/application-converter passives, diagnostic load/dividers, mechanical reverse-insertion/thermal coupling, hot/fault calculations and HIL remain open before schematic/BOM freeze
- HMX035CTFT-001 exact contacts are instantiated, but display production qualification remains open; the I2 hard-stop/evidence active circuit is paper-reviewed while its AON source/hold-up is I3 and detector taps/thresholds are I6; exact IR frontends, power tree and antenna placement remain open; SA518/Si4732 contact maps are instantiated, while SA518 UPDATE electrical direction/timing and both modules' surrounding power/audio/RF circuits remain specimen/electrical/HIL gates before target-architecture acceptance

## Machine-check result and review boundary

All source candidates pass structural validation. This proves that their listed programmable GPIO exist on the exact compute packages/modules and are fully accounted without collisions. Where declared, non-MCU contacts, interface resource contracts, controller GPIO-window selections, fixed-mux contact contracts, capacity arithmetic, signal-group declarations and quiet-state contract coverage are also complete. It does **not** close electrical feasibility: abstract peers, reference-only modules, RF networks, quiet-state circuitry, timing/EMI HIL, power and physical integration remain open. Therefore no candidate receives «Проведено ревью» as a complete target architecture in this generated artifact.
