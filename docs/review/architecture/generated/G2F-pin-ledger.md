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
| `G2F-3I` | 5 | `s3 33U/3R/0F`, `c5 14U/6R/1F`, `rp 48U/0R/0F`, `pd_controller 5U/5R/0F`, `pack_admission 12U/3R/3F` | DEC-0045 limits runtime to one active signal group, but SG-N24 requires every simultaneous three-radio PTX/PRX mix including 3PTX; exact mixed-RF sensitivity/current/thermal envelope, quiet-state power parts and conducted/OTA HIL remain open |

## Exact-device provenance used by these drafts

| Device id | Exact MPN / boundary | Qualification | Lifecycle | Primary source | Lifecycle evidence |
|---|---|---|---|---|---|
| `adi_ltc5507_es6_trmpbf` | `LTC5507ES6#TRMPBF` | `verified_candidate` | `production` | [LTC5507 100kHz to 1GHz RF Power Detector datasheet 5507f](https://www.analog.com/media/en/technical-documentation/data-sheets/5507f.pdf) | same primary source |
| `adi_ltc5532_es6_trmpbf` | `LTC5532ES6#TRMPBF` | `verified_candidate` | `production` | [LTC5532 Precision 300MHz to 7GHz RF Detector datasheet 5532f](https://www.analog.com/media/en/technical-documentation/data-sheets/5532f.pdf) | same primary source |
| `adi_max17320_g20_t` | `Analog Devices MAX17320G20+T` | `verified_candidate` | `recommended_for_new_designs` | [MAX17320 2S-4S ModelGauge m5 gauge/protector datasheet Rev. 12, July 2025](https://www.analog.com/media/en/technical-documentation/data-sheets/max17320.pdf) | same primary source |
| `alps_ec11e18244au` | `Alps Alpine EC11E18244AU` | `verified_first_target_mechanical_fit_hil_open` | `active_standard` | [EC11E Series Incremental Encoder catalog and product specification catalog update 2510](https://tech.alpsalpine.com/cms.media/product_catalog_ec_01_ec11e_en_611f078659.pdf) | same primary source |
| `bourns_crm2512_fx_20r0elf` | `Bourns CRM2512-FX-20R0ELF` | `verified_candidate` | `active` | [Bourns CRM2512 high-power resistor datasheet with pulse-load curve Rev. 08/21; current product data checked 2026-08-18](https://www.bourns.com/docs/product-datasheets/CRM.pdf) | same primary source |
| `cc1101rgpr` | `CC1101RGPR` | `verified_candidate` | `active` | [CC1101 Low-Power Sub-1 GHz RF Transceiver datasheet SWRS061I](https://www.ti.com/lit/ds/symlink/cc1101.pdf) | [TI CC1101RGPR order page](https://www.ti.com/product/CC1101/part-details/CC1101RGPR) |
| `diodes_2n7002dw_7_f` | `Diodes Incorporated 2N7002DW-7-F` | `verified_candidate` | `active` | [2N7002DW dual N-channel MOSFET datasheet DS30120 Rev. 22-2, October 2021](https://www.diodes.com/datasheet/download/2N7002DW.pdf) | same primary source |
| `diodes_bat54_7_f` | `Diodes Incorporated BAT54-7-F` | `verified_candidate` | `active` | [BAT54 surface-mount Schottky barrier diode datasheet DS11005 Rev. 34-2, November 2023](https://www.diodes.com/datasheet/download/BAT54.pdf) | same primary source |
| `diodes_dmn2056u_7` | `Diodes Incorporated DMN2056U-7` | `verified_candidate` | `active` | [DMN2056U 20-V N-channel enhancement-mode MOSFET datasheet DS38480 Rev. 2-2, July 2021; product status checked 2026-08-18](https://www.diodes.com/datasheet/download/DMN2056U.pdf) | same primary source |
| `diodes_mmbt3904_7_f` | `Diodes Incorporated MMBT3904-7-F` | `verified_candidate` | `active` | [MMBT3904 40-V NPN small-signal transistor datasheet current product data checked 2026-08-18](https://www.diodes.com/datasheet/download/MMBT3904.pdf) | same primary source |
| `diodes_pam8302a_ascr` | `Diodes Incorporated PAM8302AASCR` | `verified_reference` | `active` | [PAM8302A 2.5-W mono filterless Class-D audio amplifier datasheet DS41333 Rev. 6-2, May 2021](https://www.diodes.com/datasheet/download/PAM8302A.pdf) | same primary source |
| `ebyte_e01_ml01ipx` | `Ebyte E01-ML01IPX` | `verified_reference` | `nrf24_family_not_recommended_for_new_designs` | [E01-ML01IPX product specification 2025-01-16](https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf) | [Nordic nRF24 Series lifecycle page](https://www.nordicsemi.com/Products/nRF24-series) |
| `esp32_c5_wroom_1u_n8r8` | `ESP32-C5-WROOM-1U-N8R8` | `verified_candidate` | `active_candidate_revision_floor_v1_2` | [ESP32-C5-WROOM-1/WROOM-1U Datasheet v1.2](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf) | same primary source |
| `esp32_s3_wroom_1u_n16r2` | `ESP32-S3-WROOM-1U-N16R2` | `verified_candidate` | `active` | [ESP32-S3-WROOM-1/WROOM-1U Datasheet v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | same primary source |
| `everest_es8311_qfn20` | `Everest Semiconductor ES8311` | `verified_candidate` | `current manufacturer product brief revision 17.0 dated 2026-02; production sourcing and lot qualification remain open` | [ES8311 Low Power Mono Audio CODEC Product Brief Revision 17.0, February 2026](https://www.everest-semi.com/pdf/ES8311%20PB.pdf) | same primary source |
| `hirose_dm3at_sf_pejm5` | `Hirose DM3AT-SF-PEJM5` | `verified_candidate` | `active` | [DM3 Series microSD Card Connectors catalog 2026-05-01 current catalog and exact product page](https://www.hirose.com/product/p/CL0609-0031-0-00) | same primary source |
| `hirose_fh12_40s_0_5sh_55` | `Hirose FH12-40S-0.5SH(55)` | `verified_first_fit_candidate` | `active; exact HMX035CTFT-001 tail thickness, exposed-contact side, stiffener and insertion fit remain specimen HIL` | [Hirose FH12-40S-0.5SH(55) product page and 2D drawing CL0586-0527-7-55; drawing updated 2026-07-01](https://www.hirose.com/product/p/CL0586-0527-7-55?lang=en) | same primary source |
| `jae_dx07s016ja1r1500` | `JAE DX07S016JA1R1500` | `verified_candidate` | `active` | [JAE DX07 16-position receptacle product brochure MB-0350E, August 2025](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8440/MB-0350E_DX07_16-POS_RECEPTACLE.pdf) | same primary source |
| `kemet_c0402c102k5ractu` | `KEMET C0402C102K5RACTU` | `verified_candidate` | `active` | [KEMET C0402C102K5RACTU product specification and TI reference BOM current product data checked 2026-08-18](https://search.kemet.com/download/specsheet/C0402C102K5RACTU) | same primary source |
| `kemet_c0402c330j5gactu` | `KEMET C0402C330J5GACTU` | `verified_candidate` | `active` | [KEMET C0402C330J5GACTU product specification current product data checked 2026-08-18](https://search.kemet.com/download/specsheet/C0402C330J5GACTU) | same primary source |
| `keystone_1048p` | `Keystone Electronics 1048P` | `verified_mechanical_reference` | `active` | [Keystone 1048P exact product page and 18650 holder drawing current product page and catalog M65 p27 checked 2026-08-18](https://www.keyelco.com/product.cfm/product_id/13959) | same primary source |
| `liteon_ltst_c190kfkt` | `LTST-C190KFKT` | `verified_candidate` | `active` | [LTST-C190KFKT SMD LED datasheet BNS-OD-C131/A4](https://optoelectronics.liteon.com/upload/download/DS-22-99-0186/LTST-C190KFKT.PDF) | same primary source |
| `liteon_ltst_c190krkt` | `LTST-C190KRKT` | `verified_candidate` | `active` | [LTST-C190KRKT SMD LED datasheet BNS-OD-C131/A4](https://optoelectronics.liteon.com/upload/download/DS-22-99-0151/LTST-C190KRKT.PDF) | same primary source |
| `littelfuse_0451005_mrl` | `Littelfuse 0451005.MRL` | `verified_candidate` | `active` | [451/453 Nano2 surface-mount fuse datasheet current product data checked 2026-08-18](https://www.littelfuse.com/assetdocs/littelfuse-fuse-451-453-datasheet?assetguid=3dce64db-5f0f-4b52-bbf2-f879dd216803) | same primary source |
| `m5_u214` | `M5Stack U214 Cap LoRa-1262` | `verified_candidate` | `active` | [M5Stack Cap LoRa-1262 product documentation live product page](https://docs.m5stack.com/en/cap/Cap_LoRa-1262) | same primary source |
| `murata_grm1555c1h121ja01d` | `Murata GRM1555C1H121JA01D` | `verified_candidate` | `active` | [Murata GRM1555C1H121JA01 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM1555C1H121JA01D) | same primary source |
| `murata_grm1555c1h221ja01d` | `Murata GRM1555C1H221JA01D` | `verified_candidate` | `active` | [Murata GRM1555C1H221JA01 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM1555C1H221JA01D) | same primary source |
| `murata_grm155r71e473ka88d` | `Murata GRM155R71E473KA88D` | `verified_candidate` | `active` | [Murata GRM155R71E473KA88 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM155R71E473KA88D) | same primary source |
| `murata_grm155r71h103ka88d` | `Murata GRM155R71H103KA88D` | `verified_candidate` | `active` | [Murata GRM155R71H103KA88 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM155R71H103KA88D) | same primary source |
| `murata_grm155r71h472ka01d` | `Murata GRM155R71H472KA01D` | `verified_candidate` | `active` | [Murata GRM155R71H472KA01 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM155R71H472KA01D) | same primary source |
| `murata_grm188r60j106me47d` | `Murata GRM188R60J106ME47D` | `verified_candidate` | `active` | [Murata GRM188R60J106ME47 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM188R60J106ME47D) | same primary source |
| `murata_grm188r71e224ka88d` | `Murata GRM188R71E224KA88D` | `verified_candidate` | `active` | [Murata GRM188R71E224KA88 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM188R71E224KA88D) | same primary source |
| `murata_grm21br60j226me39l` | `Murata GRM21BR60J226ME39L` | `verified_candidate` | `active` | [Murata GRM21BR60J226ME39 product data and current part list current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM21BR60J226ME39L) | same primary source |
| `murata_grm21br71e225ke11l` | `Murata GRM21BR71E225KE11L` | `verified_candidate` | `active` | [Murata GRM21BR71E225KE11 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM21BR71E225KE11L) | same primary source |
| `murata_grm31c5c1h224je02l` | `Murata GRM31C5C1H224JE02L` | `verified_candidate` | `active` | [Murata GRM31C5C1H224JE02 product detail current product data checked 2026-08-18](https://www.murata.com/en-us/products/productdetail?partno=GRM31C5C1H224JE02%23) | same primary source |
| `murata_grm31cr71a226ke15l` | `Murata GRM31CR71A226KE15L` | `verified_candidate` | `active` | [Murata GRM31CR71A226KE15 product data current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM31CR71A226KE15L) | same primary source |
| `murata_grm31cr71e106ma12l` | `Murata GRM31CR71E106MA12L` | `verified_candidate` | `active` | [Murata GRM31CR71E106MA12 product data current product data checked 2026-08-18](https://www.murata.com/en-us/products/productdetail?partno=GRM31CR71E106MA12L) | same primary source |
| `murata_grm32er71e226ke15l` | `Murata GRM32ER71E226KE15L` | `verified_candidate` | `active` | [Murata GRM32ER71E226KE15 product data and TI reference-BOM use current product data checked 2026-08-18](https://www.murata.com/en-global/products/productdetail?partno=GRM32ER71E226KE15L) | same primary source |
| `nexperia_74lvc1g32gv_125` | `74LVC1G32GV,125` | `verified_candidate` | `production` | [74LVC1G32 Single 2-input OR gate datasheet 2024-09-03](https://assets.nexperia.com/documents/data-sheet/74LVC1G32.pdf) | same primary source |
| `nexperia_74lvc2g14gw_125` | `74LVC2G14GW,125` | `verified_candidate` | `production` | [74LVC2G14 Dual inverting Schmitt trigger datasheet 2023-08-18](https://assets.nexperia.com/documents/data-sheet/74LVC2G14.pdf) | same primary source |
| `nicerf_sa518_v11` | `NiceRF SA518` | `verified_candidate` | `current_product` | [SA518 UV Dual Frequency Walkie-talkie Module Product Specification 1.1 / 2026-05](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf) | same primary source |
| `onsemi_1n4148wt` | `onsemi 1N4148WT` | `verified_candidate` | `active` | [1N4148WT Small Signal Diode datasheet Rev. 11](https://www.onsemi.com/pdf/datasheet/1n4148wt-d.pdf) | same primary source |
| `onsemi_bat54alt1g` | `BAT54ALT1G` | `verified_candidate` | `active` | [BAT54ALT1 Schottky Barrier Diodes datasheet Rev. 16](https://www.onsemi.com/download/data-sheet/pdf/bat54alt1-d.pdf) | same primary source |
| `onsemi_bav70lt1g` | `onsemi BAV70LT1G` | `verified_candidate` | `active` | [BAV70L dual common-cathode switching diode datasheet Rev. 12](https://www.onsemi.com/pdf/datasheet/bav70lt1-d.pdf) | same primary source |
| `onsemi_cat24c512wi_gt3` | `onsemi CAT24C512WI-GT3` | `verified_candidate` | `active` | [CAT24C512 512-kb I2C serial EEPROM datasheet Rev. 9](https://www.onsemi.com/pdf/datasheet/cat24c512-d.pdf) | same primary source |
| `panasonic_erj_2rkf22r0x` | `Panasonic ERJ-2RKF22R0X` | `verified_candidate` | `active` | [Panasonic ERJ precision thick-film chip resistor datasheet current family datasheet checked 2026-08-18](https://api.pim.na.industrial.panasonic.com/file_stream/main/fileversion/1263) | same primary source |
| `panasonic_erj_p08f10r0v` | `Panasonic ERJ-P08F10R0V` | `verified_candidate` | `active` | [Panasonic ERJ-P08F10R0V high-power anti-surge resistor product page current product data checked 2026-08-18](https://na.industrial.panasonic.com/products/resistors/smd-chip-resistors/high-power-anti-surge-high-voltage/series/36033/model/39214) | same primary source |
| `qdtech_hmx035ctft_001` | `HMX035CTFT-001 (QDtech schematic assembly marking)` | `verified_candidate` | `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified` | [QDtech ES3C35P ESP32-S3 schematic official published schematic](https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf) | same primary source |
| `rp2354a_a4` | `RP2354A A4 (exact order code required before BOM freeze)` | `verified_candidate` | `active` | [RP2350 Datasheet; RP2354A uses the same A-package pinout and stacked 2 MB flash build-date 2025-02-20](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) | same primary source |
| `rp2354b_a4` | `RP2354B A4 (exact A4 order/lot identity required before BOM freeze)` | `verified_candidate` | `active` | [RP2350 Datasheet; RP2354B uses the same B-package pinout and stacked 2 MB flash build-date 2025-02-20](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) | same primary source |
| `skyworks_si4732_a10_gs` | `Si4732-A10-GS` | `verified_candidate` | `manufacturer_documented` | [Si4732-A10 Broadcast AM/FM/SW/LW/RDS Radio Receiver data short 2021-09-13](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf) | same primary source |
| `sn74hc595pwr` | `SN74HC595PWR` | `verified_candidate` | `active` | [SNx4HC595 8-Bit Shift Registers datasheet SCLS041J](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf) | same primary source |
| `sunlord_mwsa0503s_2r2mt` | `Sunlord MWSA0503S-2R2MT` | `verified_candidate` | `active` | [Sunlord MWSA-S molded SMD power-inductor datasheet current table checked 2026-08-18](https://www.sunlordinc.com/uploads/files/20230303/MWSA-S%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf) | same primary source |
| `sunlord_mwsa0503s_3r3mt` | `Sunlord MWSA0503S-3R3MT` | `verified_candidate` | `active` | [Sunlord MWSA-S molded SMD power-inductor datasheet current table checked 2026-08-18](https://www.sunlordinc.com/uploads/files/20230303/MWSA-S%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf) | same primary source |
| `sunlord_mwsa0503s_4r7mt` | `Sunlord MWSA0503S-4R7MT` | `verified_candidate` | `active` | [Sunlord MWSA-S molded SMD power-inductor datasheet current table checked 2026-08-18](https://www.sunlordinc.com/uploads/files/20230303/MWSA-S%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf) | same primary source |
| `sunlord_wpn201612h2r2mt` | `Sunlord WPN201612H2R2MT` | `verified_candidate` | `active` | [Sunlord WPN series wire-wound SMD power-inductor datasheet current table checked 2026-08-18](https://www.sunlordinc.com/uploads/files/20221122/WPN%C2%A0series%C2%A0of%C2%A0SMD%C2%A0Power%C2%A0Inductor.pdf) | same primary source |
| `tca4307dgkr` | `TCA4307DGKR` | `reference_only` | `active` | [TCA4307 Hot-Swappable I2C/SMBus Buffer With Stuck-Bus Recovery datasheet SCPS270B](https://www.ti.com/lit/ds/symlink/tca4307.pdf) | same primary source |
| `tca6424argjr` | `TCA6424ARGJR` | `reference_only` | `active` | [TCA6424A Low-Voltage 24-Bit I2C/SMBus I/O Expander datasheet SCPS193D](https://www.ti.com/lit/ds/symlink/tca6424a.pdf) | same primary source |
| `tca9535pwr` | `TCA9535PWR` | `verified_candidate` | `active` | [TCA9535 Remote 16-Bit I2C/SMBus I/O Expander datasheet SCPS201E](https://www.ti.com/lit/ds/symlink/tca9535.pdf) | same primary source |
| `tdk_b57332v5103f360` | `TDK B57332V5103F360` | `verified_candidate` | `active` | [B57 V5 automotive SMD NTC datasheet and exact product page PPD ML PD 2025-10-30](https://product.tdk.com/en/search/sensor/ntc/chip-ntc-thermistor/info?part_no=B57332V5103F360) | same primary source |
| `tdk_c1005x7r1h104k050bb` | `TDK C1005X7R1H104K050BB` | `verified_candidate` | `active` | [TDK C1005X7R1H104K050BB product data and characteristic models production status checked 2026-08-18](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1005X7R1H104K050BB) | same primary source |
| `tdk_c1608x7r1c105k080ac` | `TDK C1608X7R1C105K080AC` | `verified_candidate` | `active_production` | [TDK C1608X7R1C105K080AC product and characterization data production status and DC-bias/temperature curves checked 2026-08-18](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1C105K080AC) | same primary source |
| `tdk_c1608x7s2a104k080ab` | `TDK C1608X7S2A104K080AB` | `verified_candidate` | `active` | [TDK commercial mid-voltage MLCC datasheet current catalog checked 2026-08-18](https://product.tdk.com/info/en/catalog/datasheets/mlcc_commercial_midvoltage_en.pdf) | same primary source |
| `tdk_cga5l1x7r1e475k160ac` | `TDK CGA5L1X7R1E475K160AC` | `verified_candidate` | `active` | [TDK CGA5L1X7R1E475K160AC product data and characteristic models production status checked 2026-08-18](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA5L1X7R1E475K160AC) | same primary source |
| `ti_bq25798_rqmr` | `Texas Instruments BQ25798RQMR` | `verified_candidate` | `active` | [BQ25798 1-to-4-cell 5-A buck-boost charger datasheet SLUSDV2C, May 2020, revised June 2026](https://www.ti.com/lit/ds/symlink/bq25798.pdf) | same primary source |
| `ti_csd87313dmst` | `Texas Instruments CSD87313DMST` | `verified_candidate` | `active` | [CSD87313DMS 30-V dual common-drain N-channel NexFET datasheet SLPS659, April 2017; package addendum updated 2025-10-17](https://www.ti.com/lit/ds/symlink/csd87313dms.pdf) | same primary source |
| `ti_mspm0c1104_sdgs20r` | `Texas Instruments MSPM0C1104SDGS20R` | `verified_candidate` | `active` | [MSPM0C110x mixed-signal microcontroller datasheet SLASF90D, revised January 2026](https://www.ti.com/lit/ds/symlink/mspm0c1104.pdf) | same primary source |
| `ti_sn74lvc08a_pwr` | `SN74LVC08APWR` | `verified_candidate` | `active` | [SNx4LVC08A Quadruple 2-Input Positive-AND Gates datasheet Rev. W](https://www.ti.com/lit/ds/symlink/sn74lvc08a.pdf) | same primary source |
| `ti_sn74lvc1g07_dckr` | `SN74LVC1G07DCKR` | `verified_first_target_touch_polarity_hil_open` | `active` | [SN74LVC1G07 Single Buffer/Driver With Open-Drain Output datasheet Rev. V](https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf) | same primary source |
| `ti_sn74lvc1g125_dckr` | `Texas Instruments SN74LVC1G125DCKR` | `verified_candidate` | `active` | [SN74LVC1G125 single-bus buffer with 3-state output datasheet SCES223T and current exact-part page checked 2026-08-18](https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf) | same primary source |
| `ti_sn74lvc1g3157_dbvr` | `Texas Instruments SN74LVC1G3157DBVR` | `verified_reference` | `active` | [SN74LVC1G3157 single-pole, double-throw analog switch datasheet SCES424O, January 2003, revised June 2025](https://www.ti.com/lit/ds/symlink/sn74lvc1g3157.pdf) | same primary source |
| `ti_sn74lvc1g74_dcur` | `SN74LVC1G74DCUR` | `verified_candidate` | `active` | [SN74LVC1G74 Single D-Type Flip-Flop With Clear and Preset datasheet Rev. G](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf) | same primary source |
| `ti_sn74lvc2g08_dcur` | `Texas Instruments SN74LVC2G08DCUR` | `reference_only` | `active` | [SN74LVC2G08 dual 2-input positive-AND gate datasheet SCES198N, April 1999, revised December 2015](https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf) | same primary source |
| `ti_sn74lvc3g34_dcur` | `SN74LVC3G34DCUR` | `verified_candidate` | `active` | [SN74LVC3G34 Triple Buffer Gate datasheet Rev. L](https://www.ti.com/lit/ds/symlink/sn74lvc3g34.pdf) | same primary source |
| `ti_tca9534a_pwr` | `TCA9534APWR` | `verified_candidate` | `active` | [TCA9534A Low-Voltage 8-Bit I2C/SMBus I/O Expander datasheet Rev. C](https://www.ti.com/lit/ds/symlink/tca9534a.pdf) | same primary source |
| `ti_tlv1824_pwr` | `TLV1824PWR` | `verified_candidate` | `active` | [TLV181x and TLV182x 40V Rail-to-Rail Comparator datasheet Rev. E](https://www.ti.com/lit/ds/symlink/tlv1824.pdf) | same primary source |
| `ti_tlv9061_idbvr` | `Texas Instruments TLV9061IDBVR` | `reference_only` | `active` | [TLV906x 10-MHz rail-to-rail input/output operational amplifiers datasheet SBOS839N, March 2017, revised July 2026](https://www.ti.com/lit/ds/symlink/tlv9061.pdf) | same primary source |
| `ti_tmux1136_dgsr` | `Texas Instruments TMUX1136DGSR` | `reference_only` | `active` | [TMUX1136 5-V, low-leakage-current, 2:1, 2-channel precision switch datasheet SCDS402B, June 2019, revised February 2024](https://www.ti.com/lit/ds/symlink/tmux1136.pdf) | same primary source |
| `ti_tpd4e05u06_dqar` | `Texas Instruments TPD4E05U06DQAR` | `verified_candidate` | `active` | [TPDxE05U06 1/4/6-channel ESD protection datasheet SLVSBO7O, revised 2024-08; exact order code checked 2026-08-18](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf) | same primary source |
| `ti_tpd4s201_rukr` | `Texas Instruments TPD4S201RUKR` | `verified_candidate` | `active` | [TPD4S201 USB Type-C port-protection datasheet SLVSIF2, July 2025](https://www.ti.com/lit/gpn/TPD4S201) | same primary source |
| `ti_tps22919_dckr` | `Texas Instruments TPS22919DCKR` | `verified_candidate` | `active` | [TPS22919 5.5-V, 1.5-A self-protected load-switch datasheet SLVSEN5B, October 2018, revised May 2019](https://www.ti.com/lit/ds/symlink/tps22919.pdf) | same primary source |
| `ti_tps2553drvr_1` | `Texas Instruments TPS2553DRVR-1` | `verified_candidate` | `active` | [TPS2552/TPS2553 precision adjustable current-limited power-distribution switch datasheet SLVS841F and current exact-part page checked 2026-08-18](https://www.ti.com/lit/gpn/TPS2553-1) | same primary source |
| `ti_tps25751d_refr` | `Texas Instruments TPS25751DREFR` | `verified_candidate` | `active` | [TPS25751 USB Type-C and USB PD Controller datasheet SLVSH93A, October 2023, revised March 2024](https://www.ti.com/lit/ds/symlink/tps25751.pdf) | same primary source |
| `ti_tps259470l_rpwr` | `Texas Instruments TPS259470LRPWR` | `verified_candidate` | `active` | [TPS25947xx true-reverse-current-blocking eFuse datasheet SLVSFC9C, October 2020, revised May 2026](https://www.ti.com/lit/ds/symlink/tps25947.pdf) | same primary source |
| `ti_tps25961_drvr` | `Texas Instruments TPS25961DRVR` | `verified_candidate` | `active` | [TPS25961 2.7-V to 19-V, 106-mOhm eFuse datasheet SLVSGT8, December 2022](https://www.ti.com/lit/ds/symlink/tps25961.pdf) | same primary source |
| `ti_tps25974l_rpwr` | `Texas Instruments TPS25974LRPWR` | `verified_candidate` | `active` | [TPS2597xx 2.7-V to 23-V, 7-A, 9.8-mOhm eFuse datasheet SLVSGG5D, November 2021, revised May 2025](https://www.ti.com/lit/ds/symlink/tps2597.pdf) | same primary source |
| `ti_tps3808g33_dbvr` | `TPS3808G33DBVR` | `verified_candidate` | `active` | [TPS3808 Low-Quiescent-Current Programmable-Delay Supervisory Circuit datasheet Rev. M](https://www.ti.com/lit/ds/symlink/tps3808.pdf) | same primary source |
| `ti_tps564252_drlr` | `Texas Instruments TPS564252DRLR` | `verified_candidate` | `active` | [TPS56425x 3-V to 17-V input, 4-A synchronous buck converter datasheet SLUSEQ6A, December 2022, revised May 2023](https://www.ti.com/lit/ds/symlink/tps564252.pdf) | same primary source |
| `ti_tps629203_drlr` | `Texas Instruments TPS629203DRLR` | `verified_candidate` | `active` | [TPS629203 300-mA, 3-V to 17-V low-IQ buck converter datasheet SLVSGE2, March 2022](https://www.ti.com/lit/ds/symlink/tps629203.pdf) | same primary source |
| `ti_tpul2g223_bqbr` | `Texas Instruments TPUL2G223BQBR` | `verified_candidate` | `active_production` | [TPUL2G223 dual RC-timed non-retriggerable monostable multivibrators datasheet SLVSL08, January 2026](https://www.ti.com/lit/ds/symlink/tpul2g223.pdf) | same primary source |
| `ti_ts5a63157_dckr` | `Texas Instruments TS5A63157DCKR` | `reference_only` | `active` | [TS5A63157 12-ohm SPDT analog switch datasheet SCDS203B, December 2005, revised March 2019](https://www.ti.com/lit/ds/symlink/ts5a63157.pdf) | same primary source |
| `ti_tvs2200_drvr` | `Texas Instruments TVS2200DRVR` | `verified_candidate` | `active` | [TVS2200 22-V flat-clamp surge-protection datasheet SLVSED5C, December 2017, revised August 2023; orderable addendum 2025-11-09](https://www.ti.com/lit/ds/symlink/tvs2200.pdf) | same primary source |
| `vishay_vemd1060x01` | `VEMD1060X01` | `verified_candidate` | `active` | [VEMD1060X01 Silicon PIN Photodiode datasheet Rev. 1.1](https://www.vishay.com/docs/84295/vemd1060x01.pdf) | same primary source |
| `vishay_wsl25125l000fea` | `Vishay WSL25125L000FEA` | `verified_candidate` | `active` | [WSL power metal strip resistor datasheet current product data checked 2026-08-18](https://www.vishay.com/docs/30108/wsl.pdf) | same primary source |
| `xtar_18650_4000mah_protected` | `XTAR 18650 4000mAh` | `selected_qualification_target` | `current_catalog` | [XTAR 18650 4000mAh official two-page battery datasheet official download page last updated 2026-07-06; exact PDF content rechecked 2026-08-18](https://www.xtar.cc/download/18650-4000mah-data-sheet) | same primary source |
| `yageo_rc0402fr_07100kl` | `Yageo RC0402FR-07100KL` | `verified_candidate` | `active` | [Yageo RC0402FR-07100KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07100KL) | same primary source |
| `yageo_rc0402fr_07100rl` | `Yageo RC0402FR-07100RL` | `verified_candidate` | `active` | [Yageo RC0402FR-07100RL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07100RL) | same primary source |
| `yageo_rc0402fr_0710kl` | `Yageo RC0402FR-0710KL` | `verified_candidate` | `active` | [Yageo RC0402FR-0710KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0710KL) | same primary source |
| `yageo_rc0402fr_0712kl` | `Yageo RC0402FR-0712KL` | `verified_candidate` | `active` | [Yageo RC0402FR-0712KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0712KL) | same primary source |
| `yageo_rc0402fr_07133kl` | `Yageo RC0402FR-07133KL` | `verified_candidate` | `active` | [Yageo RC0402FR-07133KL product specification current product data checked 2026-08-18](https://www.yageogroup.com/component-documentation/download/specsheet/RC0402FR-07133KL) | same primary source |
| `yageo_rc0402fr_07169kl` | `Yageo RC0402FR-07169KL` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0402fr_07196kl` | `Yageo RC0402FR-07196KL` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0402fr_071k65l` | `Yageo RC0402FR-071K65L` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0402fr_07220kl` | `Yageo RC0402FR-07220KL` | `verified_candidate` | `active` | [Yageo RC0402FR-07220KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07220KL) | same primary source |
| `yageo_rc0402fr_07240kl` | `Yageo RC0402FR-07240KL` | `verified_candidate` | `active` | [Yageo RC0402FR-07240KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07240KL) | same primary source |
| `yageo_rc0402fr_07270kl` | `Yageo RC0402FR-07270KL` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0402fr_072k21l` | `Yageo RC0402FR-072K21L` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0402fr_072k2l` | `Yageo RC0402FR-072K2L` | `verified_candidate` | `active` | [Yageo RC0402 thick-film resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_16.pdf) | same primary source |
| `yageo_rc0402fr_0730k1l` | `Yageo RC0402FR-0730K1L` | `verified_candidate` | `active` | [Yageo RC0402FR-0730K1L product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0730K1L) | same primary source |
| `yageo_rc0402fr_0730kl` | `Yageo RC0402FR-0730KL` | `verified_candidate` | `active` | [Yageo RC0402FR-0730KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0730KL) | same primary source |
| `yageo_rc0402fr_0733kl` | `Yageo RC0402FR-0733KL` | `verified_candidate` | `active` | [Yageo RC0402FR-0733KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0733KL) | same primary source |
| `yageo_rc0402fr_073k32l` | `Yageo RC0402FR-073K32L` | `verified_candidate` | `active` | [Yageo RC0402FR-073K32L product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-073K32L) | same primary source |
| `yageo_rc0402fr_0742k2l` | `Yageo RC0402FR-0742K2L` | `verified_candidate` | `active` | [Yageo RC0402FR-0742K2L product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0742K2L) | same primary source |
| `yageo_rc0402fr_0744k2l` | `Yageo RC0402FR-0744K2L` | `verified_candidate` | `active` | [Yageo RC0402FR-0744K2L product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0744K2L) | same primary source |
| `yageo_rc0402fr_0745k3l` | `Yageo RC0402FR-0745K3L` | `verified_candidate` | `active` | [Yageo RC0402FR-0745K3L product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0745K3L) | same primary source |
| `yageo_rc0402fr_0747kl` | `Yageo RC0402FR-0747KL` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rc0402fr_075k23l` | `Yageo RC0402FR-075K23L` | `verified_candidate` | `active` | [Yageo RC0402FR-075K23L product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-075K23L) | same primary source |
| `yageo_rc0402fr_07620kl` | `Yageo RC0402FR-07620KL` | `verified_candidate` | `active` | [Yageo RC0402FR-07620KL exact product specification generated 2026-05-21; checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-07620KL) | same primary source |
| `yageo_rc0402fr_0768kl` | `Yageo RC0402FR-0768KL` | `verified_candidate` | `active` | [Yageo RC0402FR-0768KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-0768KL) | same primary source |
| `yageo_rc0402fr_078k2l` | `Yageo RC0402FR-078K2L` | `verified_candidate` | `active` | [Yageo RC0402FR-078K2L product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RC0402FR-078K2L) | same primary source |
| `yageo_rc0603fr_071kl` | `Yageo RC0603FR-071KL` | `verified_candidate` | `active` | [Yageo RC general-purpose thick-film chip resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_14.pdf) | same primary source |
| `yageo_rt0402brd07100kl` | `Yageo RT0402BRD07100KL` | `verified_candidate` | `active` | [Yageo RT0402BRD07100KL product specification current product data checked 2026-08-18](https://yageogroup.com/component-documentation/download/specsheet/RT0402BRD07100KL) | same primary source |
| `yageo_rt0402brd07191kl` | `Yageo RT0402BRD07191KL` | `verified_candidate` | `active` | [Yageo RT high-precision thin-film resistor series datasheet current product data checked 2026-08-18](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RT_1-to-0_01.pdf) | same primary source |

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
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `slow_io.SDA`, `ui_matrix_io.SDA`, `receiver.SDIO`, `display_connector.PIN_2`, `codec.CDATA`, `pd_controller.I2Ct_SDA`, `pack_admission.PA0` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `slow_io.SCL`, `ui_matrix_io.SCL`, `receiver.SCLK`, `display_connector.PIN_1`, `codec.CCLK`, `pd_controller.I2Ct_SCL`, `pack_admission.PA11` | — |
| `GPIO3` | 15 | `RP_ALERT_N` | `i` | `GPIO_IRQ` | `rp.GPIO19` | RP is held reset/high-Z through S3 strap sampling; an external pull fixes the accepted S3 boot state |
| `GPIO4` | 4 | `DISPLAY_SD_SPI_D1` | `io` | `SPI2` | `sd_miso_series.END_2`, `sd_host_d1_pullup.END_1`, `display_connector.PIN_10` | — |
| `GPIO5` | 5 | `SD_SPI_CS_N` | `o` | `SPI2` | `sd_host_buffer.3A`, `sd_miso_buffer.OE_N`, `sd_host_cs_pullup.END_1` | — |
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
| `GPIO19` | 13 | `S3_USB_DM` | `io` | `USB_SERIAL_JTAG` | `product_usb_dm_series.END_2` | — |
| `GPIO20` | 14 | `S3_USB_DP` | `io` | `USB_SERIAL_JTAG` | `product_usb_dp_series.END_2` | — |
| `GPIO21` | 23 | `S3_RP_IPC_MOSI` | `o` | `SPI3` | `rp.GPIO24` | — |
| `GPIO35` | 28 | `DISPLAY_SD_SPI_SCK` | `o` | `SPI2` | `sd_host_buffer.1A`, `sd_host_sck_pulldown.END_1`, `display_connector.PIN_11` | — |
| `GPIO36` | 29 | `DISPLAY_SD_SPI_D0` | `o` | `SPI2` | `sd_host_buffer.2A`, `sd_host_d0_pullup.END_1`, `display_connector.PIN_13` | — |
| `GPIO37` | 30 | `SYS_INT_N` | `i` | `GPIO_IRQ` | `slow_io.INT`, `ui_matrix_io.INT_N`, `pd_controller.I2Ct_IRQ`, `touch_irq_buffer.Y`, `abstract:pack-admission reset-safe open-drain IRQ circuit` | — |
| `GPIO38` | 31 | `LCD_CS_N` | `o` | `SPI2` | `display_connector.PIN_9`, `lcd_host_cs_pullup.END_1` | — |
| `GPIO39` | 32 | `ENCODER_A` | `i` | `PCNT0` | `encoder.A`, `encoder_a_pullup.END_1` | — |
| `GPIO40` | 33 | `LCD_BL_PWM` | `o` | `LEDC` | `backlight_gate_series.END_1` | — |
| `GPIO41` | 34 | `LCD_QSPI_D2` | `o` | `SPI2` | `display_connector.PIN_17` | — |
| `GPIO42` | 35 | `LCD_QSPI_D3` | `o` | `SPI2` | `display_connector.PIN_18` | — |
| `GPIO43` | 37 | `S3_UART_SERVICE_TX` | `o` | `UART0` | `abstract:service fixture` | — |
| `GPIO44` | 36 | `S3_UART_SERVICE_RX` | `i` | `UART0` | `abstract:service fixture` | — |
| `GPIO47` | 24 | `ENCODER_B` | `i` | `PCNT0` | `encoder.B`, `encoder_b_pullup.END_1` | — |
| `GPIO48` | 25 | `S3_RP_IPC_SCK` | `o` | `SPI3` | `rp.GPIO26` | — |

Budget: **33 used + 3 reserved + 0 free = 36 exposed GPIO**.
Reserved: `GPIO0`, `GPIO45`, `GPIO46`. Free: none.

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
| `GPIO0` | 5 | `PD_EEPROM_WP` | `od` | `GPIO` | `pd_config_eeprom.WP` | — |
| `GPIO1` | 6 | `CHARGE_EN_N` | `od` | `GPIO` | `nvdc_charger.CE` | — |
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
| `PA22_A4` | 17 | `PACK_DIAG_TRIGGER` | `o` | `GPIO` | `pack_diag_timer.CH1_T`, `pack_diag_trigger_pulldown.END_1` | — |
| `PA25_A2` | 20 | `PACK_CELL0_ADC` | `i` | `ADC` | `pack_mid_adc_top1.END_2`, `pack_mid_adc_bottom.END_1`, `pack_mid_adc_filter.END_1` | — |
| `PA26_A1` | 1 | `PACK_STACK_ADC` | `i` | `ADC` | `pack_stack_adc_top4.END_2`, `pack_stack_adc_bottom.END_1`, `pack_stack_adc_filter.END_1` | — |

Budget: **12 used + 3 reserved + 3 free = 18 exposed GPIO**.
Reserved: `PA19_SWDIO`, `PA1_NRST`, `PA20_A6_SWCLK`. Free: `PA24_A3`, `PA27_A0`, `PA28_A5`.

### Fixed-function/control routes

| Net | From | To | Reset/safety rule |
|---|---|---|---|
| `USB_C_VBUS_RAW` | `product_usb_connector.A4_VBUS` | `product_usb_connector.A9_VBUS` | both A-side VBUS contacts join one short wide connector-side copper region |
| `USB_C_VBUS_RAW` | `product_usb_connector.A9_VBUS` | `product_usb_connector.B4_VBUS` | all four exact receptacle VBUS contacts share the raw input plane |
| `USB_C_VBUS_RAW` | `product_usb_connector.B4_VBUS` | `product_usb_connector.B9_VBUS` | all four exact receptacle VBUS contacts are electrically present and independently soldered |
| `USB_C_VBUS_RAW` | `product_usb_connector.B9_VBUS` | `pd_controller.VBUS` | the separate controller VBUS pins power dead-battery attach detection, safe discharge and the internal startup LDO before any application rail exists |
| `USB_C_VBUS_RAW` | `product_usb_connector.B9_VBUS` | `pd_controller.VBUS_IN` | the separate VBUS_IN pins feed only the protected PPHV input path; SafeMode keeps that path off until a valid configuration is loaded |
| `USB_C_VBUS_RAW` | `product_usb_connector.B9_VBUS` | `pd_vbus_tvs.IN` | TVS2200DRVR is a shunt clamp physically adjacent to the receptacle, not a series element |
| `USB_C_VBUS_TVS_RETURN` | `pd_vbus_tvs.GND` | `abstract:power-ground` | short low-inductance surge return; exact placement and return geometry remain I4/layout gates |
| `POWER_GROUND` | `product_usb_connector.A1_GND` | `product_usb_connector.A12_GND` | both A-side ground contacts reach the local connector return plane |
| `POWER_GROUND` | `product_usb_connector.A12_GND` | `product_usb_connector.B1_GND` | all four signal/power ground contacts share the low-impedance local return |
| `POWER_GROUND` | `product_usb_connector.B1_GND` | `product_usb_connector.B12_GND` | all four exact ground contacts remain independently soldered |
| `POWER_GROUND` | `product_usb_connector.B12_GND` | `abstract:power-ground` | connector ground reaches the product power-ground plane through a short low-inductance region |
| `USB_C_SHIELD` | `product_usb_connector.SHIELD` | `abstract:chassis-ground-at-product-usb-entry` | four shell locks terminate at the entry-zone chassis/ESD structure; the final chassis-to-power-ground network remains a placement/HIL item |
| `USB_C_CC1_CONNECTOR` | `product_usb_connector.A5_CC1` | `product_usb_protector.C_CC1` | connector-side CC1 reaches only the 28-V short-to-VBUS and IEC-ESD protector input |
| `USB_C_CC2_CONNECTOR` | `product_usb_connector.B5_CC2` | `product_usb_protector.C_CC2` | connector-side CC2 reaches only the 28-V short-to-VBUS and IEC-ESD protector input |
| `USB_C_CC1_PROTECTED` | `product_usb_protector.CC1` | `pd_controller.CC1` | protected sink-only Type-C/PD detection; source, VCONN and power-bank roles are disabled |
| `USB_C_CC2_PROTECTED` | `product_usb_protector.CC2` | `pd_controller.CC2` | protected sink-only Type-C/PD detection; source, VCONN and power-bank roles are disabled |
| `USB_C_CC1_CONNECTOR` | `product_usb_protector.RPD_G1` | `product_usb_protector.C_CC1` | TI dead-battery ground-loop contact stays on connector-side CC1 exactly as required |
| `USB_C_CC2_CONNECTOR` | `product_usb_protector.RPD_G2` | `product_usb_protector.C_CC2` | TI dead-battery ground-loop contact stays on connector-side CC2 exactly as required |
| `USB2_DP_CONNECTOR` | `product_usb_connector.A6_DP` | `product_usb_connector.B6_DP` | both orientation-dependent D+ contacts join at the receptacle before protection |
| `USB2_DP_CONNECTOR` | `product_usb_connector.B6_DP` | `product_usb_protector.C_SBU1` | the first explicitly USB2-capable protector channel carries D+; it is not an Alt-Mode SBU route |
| `USB2_DP_PROTECTED` | `product_usb_protector.SBU1` | `product_usb_dp_series.END_1` | protected USB2 D+ reaches the exact 22-Ohm first-target source-termination position |
| `S3_USB_DP` | `product_usb_dp_series.END_2` | `s3.GPIO20` | series termination stays close to the S3 module; a 0402 shunt-capacitor position is reserved DNP pending Full-Speed signal-integrity HIL |
| `USB2_DM_CONNECTOR` | `product_usb_connector.A7_DM` | `product_usb_connector.B7_DM` | both orientation-dependent D- contacts join at the receptacle before protection |
| `USB2_DM_CONNECTOR` | `product_usb_connector.B7_DM` | `product_usb_protector.C_SBU2` | the second explicitly USB2-capable protector channel carries D-; it is not an Alt-Mode SBU route |
| `USB2_DM_PROTECTED` | `product_usb_protector.SBU2` | `product_usb_dm_series.END_1` | protected USB2 D- reaches the exact 22-Ohm first-target source-termination position |
| `S3_USB_DM` | `product_usb_dm_series.END_2` | `s3.GPIO19` | series termination stays close to the S3 module; a 0402 shunt-capacitor position is reserved DNP pending Full-Speed signal-integrity HIL |
| `NO_CONNECT` | `product_usb_connector.A8_SBU1` | `abstract:no-connect` | the base product implements no Type-C Alt Mode or SBU accessory path |
| `NO_CONNECT` | `product_usb_connector.B8_SBU2` | `abstract:no-connect` | the base product implements no Type-C Alt Mode or SBU accessory path |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `product_usb_protector.VPWR` | the port protector is powered from the autonomous TPS local rail during dead-battery attach |
| `PD_LOCAL_3V3` | `product_usb_protector.VPWR` | `product_usb_vpwr_cap.END_1` | exact 1-uF 16-V X7R bypass follows the protector VPWR requirement |
| `POWER_GROUND` | `product_usb_vpwr_cap.END_2` | `abstract:power-ground` | VPWR bypass return is short and local |
| `USB_PROTECTOR_VBIAS` | `product_usb_protector.VBIAS` | `product_usb_vbias_cap.END_1` | exact 100-nF 100-V X7S capacitor provides the required high-voltage bias reservoir |
| `POWER_GROUND` | `product_usb_vbias_cap.END_2` | `abstract:power-ground` | VBIAS reservoir return is short and local |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `product_usb_fault_pullup.END_1` | fault evidence is pulled only to the protector supply and cannot back-power a disabled main rail |
| `USB_PROTECTOR_FAULT_N` | `product_usb_fault_pullup.END_2` | `product_usb_protector.FLT` | exact 10-kOhm pull-up exposes the open-drain fault without consuming a scarce MCU GPIO |
| `USB_PROTECTOR_FAULT_N` | `product_usb_protector.FLT` | `abstract:TP_USB_PROTECTOR_FAULT_N` | protected fixture test point provides automated electrical evidence; runtime detach and PD status remain the product-visible fault path |
| `POWER_GROUND` | `product_usb_protector.GND_8` | `abstract:power-ground` | first protector ground contact reaches the local entry-zone plane |
| `POWER_GROUND` | `product_usb_protector.GND_13` | `abstract:power-ground` | second protector ground contact reaches the local entry-zone plane |
| `POWER_GROUND` | `product_usb_protector.GND_18` | `abstract:power-ground` | third protector ground contact reaches the local entry-zone plane |
| `POWER_GROUND` | `product_usb_protector.GND_PAD` | `abstract:power-ground` | exposed pad uses the datasheet thermal/ESD via structure |
| `NO_CONNECT` | `product_usb_protector.NC_16` | `abstract:no-connect` | datasheet NC remains physically unconnected |
| `NO_CONNECT` | `product_usb_protector.NC_17` | `abstract:no-connect` | datasheet NC remains physically unconnected |
| `NO_CONNECT` | `product_usb_protector.NC_19` | `abstract:no-connect` | datasheet NC remains physically unconnected |
| `NO_CONNECT` | `product_usb_protector.NC_20` | `abstract:no-connect` | datasheet NC remains physically unconnected |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `nvdc_charger.VBUS` | accepted profiles stop at 15 V/2 A; the integrated protected path remains off above the negotiated envelope |
| `AON_SAFE_3V3` | `abstract:AON_SAFE_3V3` | `pd_controller.VIN_3V3` | after autonomous dead-battery startup the PD controller runs from the admitted always-on rail; maximum active load is included in the 15-mA continuous budget |
| `PD_VIN_3V3` | `pd_controller.VIN_3V3` | `pd_vin_cap.END_1` | one exact 10-uF 6.3-V X5R capacitor is placed at VIN_3V3 |
| `POWER_GROUND` | `pd_vin_cap.END_2` | `abstract:power-ground` | VIN capacitor return is short and local |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_ldo3v3_cap.END_1` | one exact 10-uF capacitor stays inside the allowed 5-25-uF LDO_3V3 range |
| `POWER_GROUND` | `pd_ldo3v3_cap.END_2` | `abstract:power-ground` | LDO_3V3 capacitor return is short and local |
| `PD_LOCAL_1V5` | `pd_controller.LDO_1V5` | `pd_ldo1v5_cap.END_1` | one exact 10-uF capacitor stays inside the allowed 4.5-12-uF LDO_1V5 range |
| `POWER_GROUND` | `pd_ldo1v5_cap.END_2` | `abstract:power-ground` | LDO_1V5 capacitor return is short and local |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `pd_pphv_cap0.END_1` | first exact 22-uF 25-V X7R output capacitor supports the protected path |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `pd_pphv_cap1.END_1` | second physical 22-uF output capacitor is independent |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `pd_pphv_cap2.END_1` | third physical 22-uF output capacitor is independent |
| `PD_NEGOTIATED_VBUS` | `pd_controller.PPHV` | `pd_pphv_cap3.END_1` | fourth physical 22-uF output capacitor brings nominal PPHV bulk to 88 uF inside the 47-100-uF requirement |
| `POWER_GROUND` | `pd_pphv_cap0.END_2` | `abstract:power-ground` | PPHV bulk return stays in the high-current local plane |
| `POWER_GROUND` | `pd_pphv_cap1.END_2` | `abstract:power-ground` | second PPHV capacitor has its own short return |
| `POWER_GROUND` | `pd_pphv_cap2.END_2` | `abstract:power-ground` | third PPHV capacitor has its own short return |
| `POWER_GROUND` | `pd_pphv_cap3.END_2` | `abstract:power-ground` | fourth PPHV capacitor has its own short return |
| `USB_C_VBUS_RAW` | `pd_controller.VBUS` | `pd_vbus_cap.END_1` | one exact 4.7-uF 25-V capacitor supports dead-battery attach and safe-discharge operation |
| `POWER_GROUND` | `pd_vbus_cap.END_2` | `abstract:power-ground` | VBUS capacitor is placed directly at the separate VBUS pins |
| `USB_C_CC1_PROTECTED` | `pd_controller.CC1` | `pd_cc1_cap.END_1` | 220-pF +/-5% C0G plus 120-pF TPS input and 40-120-pF protector totals 369-471 pF before route parasitics, leaving 129 pF to the USB-PD 600-pF ceiling |
| `POWER_GROUND` | `pd_cc1_cap.END_2` | `abstract:power-ground` | CC1 shunt stays adjacent and on the same layer as the controller contact |
| `USB_C_CC2_PROTECTED` | `pd_controller.CC2` | `pd_cc2_cap.END_1` | the identical 220-pF protected CC2 network preserves the same 369-471-pF paper range and route-parasitic margin |
| `POWER_GROUND` | `pd_cc2_cap.END_2` | `abstract:power-ground` | CC2 shunt stays adjacent and on the same layer as the controller contact |
| `PD_ADCIN1_SAFE_MODE_HIGH` | `pd_controller.LDO_3V3` | `pd_controller.ADCIN1` | decoded strap 7 selects the TI SafeMode boot row and target address index 1 |
| `PD_ADCIN2_SAFE_MODE_LOW` | `pd_controller.ADCIN2` | `abstract:power-ground` | decoded strap 0 completes the hardware SafeMode selection |
| `POWER_GROUND` | `pd_controller.PP5V` | `abstract:power-ground` | unused source/VCONN rail is grounded for the accepted sink-only application |
| `PD_DRAIN_COPPER` | `pd_controller.DRAIN_15` | `pd_controller.DRAIN_30` | both exposed drain contacts share the compact high-current thermal copper required by the integrated PPHV path |
| `PD_DRAIN_COPPER` | `pd_controller.DRAIN_30` | `pd_controller.DRAIN_PAD` | the exposed drain pad joins the same local drain copper and is not tied to ground |
| `POWER_GROUND` | `pd_controller.GND_11` | `abstract:power-ground` | every numbered controller ground contact reaches the local plane |
| `POWER_GROUND` | `pd_controller.GND_12` | `abstract:power-ground` | every numbered controller ground contact reaches the local plane |
| `POWER_GROUND` | `pd_controller.GND_14` | `abstract:power-ground` | every numbered controller ground contact reaches the local plane |
| `POWER_GROUND` | `pd_controller.GND_31` | `abstract:power-ground` | every numbered controller ground contact reaches the local plane |
| `POWER_GROUND` | `pd_controller.GND_PAD` | `abstract:power-ground` | the exposed ground pad receives the datasheet via array and thermal return |
| `POWER_GROUND` | `pd_controller.GPIO2` | `abstract:power-ground` | unused GPIO is never left floating |
| `POWER_GROUND` | `pd_controller.GPIO3` | `abstract:power-ground` | unused GPIO is never left floating |
| `POWER_GROUND` | `pd_controller.GPIO6` | `abstract:power-ground` | unused GPIO is never left floating |
| `POWER_GROUND` | `pd_controller.GPIO7` | `abstract:power-ground` | unused GPIO is never left floating |
| `POWER_GROUND` | `pd_controller.GPIO11` | `abstract:power-ground` | unused GPIO is never left floating |
| `CHARGER_VBUS_SENSE` | `nvdc_charger.VBUS` | `nvdc_charger.VAC1` | VAC1 is tied to VBUS exactly as required when the first external ACFET/RBFET pair is omitted |
| `CHARGER_VBUS_SENSE` | `nvdc_charger.VBUS` | `nvdc_charger.VAC2` | VAC2 is also tied to VBUS exactly as required when the second external ACFET/RBFET pair is omitted |
| `POWER_GROUND` | `nvdc_charger.ACDRV1` | `abstract:power-ground` | unused input-FET driver 1 is tied to ground per the exact pin requirement |
| `POWER_GROUND` | `nvdc_charger.ACDRV2` | `abstract:power-ground` | unused input-FET driver 2 is tied to ground per the exact pin requirement |
| `POWER_GROUND` | `nvdc_charger.GND` | `abstract:power-ground` | charger exposed ground return joins the compact converter ground plane |
| `CHARGER_VBUS` | `nvdc_charger.VBUS` | `charger_vbus_cap0.END_1` | first physical 10-uF 25-V X7R input capacitor supports the accepted 15-V source |
| `POWER_GROUND` | `charger_vbus_cap0.END_2` | `abstract:power-ground` | VBUS bulk return uses the short local charger power-ground path |
| `CHARGER_VBUS` | `nvdc_charger.VBUS` | `charger_vbus_cap1.END_1` | second independent 10-uF 25-V X7R input capacitor completes the required VBUS bank |
| `POWER_GROUND` | `charger_vbus_cap1.END_2` | `abstract:power-ground` | second VBUS bulk return stays local to the charger |
| `CHARGER_VBUS` | `nvdc_charger.VBUS` | `charger_vbus_hf_cap.END_1` | one exact 100-nF 50-V capacitor is placed directly at the VBUS pins |
| `POWER_GROUND` | `charger_vbus_hf_cap.END_2` | `abstract:power-ground` | VBUS HF return is direct and low inductance |
| `CHARGER_PMID` | `nvdc_charger.PMID` | `charger_pmid_cap0.END_1` | first physical 10-uF 25-V X7R PMID capacitor supports discontinuous buck current |
| `POWER_GROUND` | `charger_pmid_cap0.END_2` | `abstract:power-ground` | PMID bulk return stays inside the high-frequency converter loop |
| `CHARGER_PMID` | `nvdc_charger.PMID` | `charger_pmid_cap1.END_1` | second independent 10-uF 25-V X7R PMID capacitor is not collapsed into a quantity label |
| `POWER_GROUND` | `charger_pmid_cap1.END_2` | `abstract:power-ground` | second PMID bulk return stays local |
| `CHARGER_PMID` | `nvdc_charger.PMID` | `charger_pmid_cap2.END_1` | third independent 10-uF 25-V X7R PMID capacitor completes the required bank |
| `POWER_GROUND` | `charger_pmid_cap2.END_2` | `abstract:power-ground` | third PMID bulk return stays local |
| `CHARGER_PMID` | `nvdc_charger.PMID` | `charger_pmid_hf_cap.END_1` | one exact 100-nF 50-V capacitor sits directly at PMID and ground |
| `POWER_GROUND` | `charger_pmid_hf_cap.END_2` | `abstract:power-ground` | PMID HF return minimizes the switching-current loop |
| `CHARGER_SW1` | `nvdc_charger.SW1` | `charger_inductor.END_1` | the 750-kHz buck-side switching node reaches only the exact 2.2-uH power inductor |
| `CHARGER_SW2` | `charger_inductor.END_2` | `nvdc_charger.SW2` | 7-A saturation rating exceeds the calculated <=6.42-A device-limited peak before HIL margin |
| `CHARGER_BTST1` | `nvdc_charger.BTST1` | `charger_btst1_cap.END_1` | first exact 47-nF 25-V bootstrap capacitor follows the 750-kHz converter requirement |
| `CHARGER_SW1` | `charger_btst1_cap.END_2` | `nvdc_charger.SW1` | BTST1 capacitor returns directly to SW1 |
| `CHARGER_BTST2` | `nvdc_charger.BTST2` | `charger_btst2_cap.END_1` | second exact 47-nF 25-V bootstrap capacitor drives the SYS-side high switch |
| `CHARGER_SW2` | `charger_btst2_cap.END_2` | `nvdc_charger.SW2` | BTST2 capacitor returns directly to SW2 |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap0.END_1` | first physical 10-uF 25-V X7R SYS capacitor supports boost-output ripple |
| `POWER_GROUND` | `charger_sys_cap0.END_2` | `abstract:power-ground` | first SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap1.END_1` | second independent 10-uF SYS capacitor is physically instantiated |
| `POWER_GROUND` | `charger_sys_cap1.END_2` | `abstract:power-ground` | second SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap2.END_1` | third independent 10-uF SYS capacitor is physically instantiated |
| `POWER_GROUND` | `charger_sys_cap2.END_2` | `abstract:power-ground` | third SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap3.END_1` | fourth independent 10-uF SYS capacitor is physically instantiated |
| `POWER_GROUND` | `charger_sys_cap3.END_2` | `abstract:power-ground` | fourth SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_cap4.END_1` | fifth independent 10-uF SYS capacitor completes the required bank |
| `POWER_GROUND` | `charger_sys_cap4.END_2` | `abstract:power-ground` | fifth SYS bulk return stays local |
| `NVDC_SYS` | `nvdc_charger.SYS` | `charger_sys_hf_cap.END_1` | one exact 100-nF 50-V capacitor sits directly at SYS and ground |
| `POWER_GROUND` | `charger_sys_hf_cap.END_2` | `abstract:power-ground` | SYS HF return minimizes the boost switching loop |
| `PROTECTED_PACK_POSITIVE` | `nvdc_charger.BAT` | `charger_bat_cap0.END_1` | first physical 10-uF 25-V X7R BAT capacitor stabilizes the admitted 2S boundary |
| `POWER_GROUND` | `charger_bat_cap0.END_2` | `abstract:power-ground` | first BAT bulk return stays local |
| `PROTECTED_PACK_POSITIVE` | `nvdc_charger.BAT` | `charger_bat_cap1.END_1` | second independent 10-uF BAT capacitor completes the required bank |
| `POWER_GROUND` | `charger_bat_cap1.END_2` | `abstract:power-ground` | second BAT bulk return stays local |
| `CHARGER_REGN` | `nvdc_charger.REGN` | `charger_regn_cap.END_1` | one exact 4.7-uF 25-V X7R capacitor stabilizes the internal gate-driver and TS-bias regulator |
| `POWER_GROUND` | `charger_regn_cap.END_2` | `abstract:power-ground` | REGN return follows the dedicated short-via layout rule |
| `CHARGER_SDRV_UNUSED` | `nvdc_charger.SDRV` | `charger_sdrv_cap.END_1` | latest Rev-C requirement for no external ship FET is exactly 1 nF, 50 V, 0402 to ground |
| `POWER_GROUND` | `charger_sdrv_cap.END_2` | `abstract:power-ground` | SDRV has no resistor and no BAT connection in the accepted no-ship-FET path |
| `CHARGER_PROG_2S_750KHZ` | `nvdc_charger.PROG` | `charger_prog_res.END_1` | 8.2-kOhm 1% strap selects 2S and 750 kHz at every POR and register reset |
| `POWER_GROUND` | `charger_prog_res.END_2` | `abstract:power-ground` | PROG strap is a permanent physical default rather than firmware state |
| `PROTECTED_PACK_POSITIVE` | `pack_power_fet.S2` | `charger_batp_res.END_1` | BATP senses the admitted pack boundary rather than a raw holder contact |
| `CHARGER_BATP_SENSE` | `charger_batp_res.END_2` | `nvdc_charger.BATP` | exact 100-Ohm series resistor follows the BATP pin requirement |
| `CHARGER_REGN` | `nvdc_charger.REGN` | `charger_ts_top.END_1` | 5.23-kOhm 1% top resistor biases the direct charger thermistor gate |
| `CHARGER_TS` | `charger_ts_top.END_2` | `nvdc_charger.TS` | TS feedback remains enabled and independent of host firmware |
| `CHARGER_TS` | `nvdc_charger.TS` | `charger_ts_bottom.END_1` | 30.1-kOhm 1% bottom resistor completes the JEITA threshold network |
| `POWER_GROUND` | `charger_ts_bottom.END_2` | `abstract:power-ground` | fixed TS lower leg preserves open/short fault detection |
| `CHARGER_TS` | `nvdc_charger.TS` | `charger_ts_ntc.END_1` | third independent B57332V5103F360 gives BQ25798 a direct battery-temperature gate without loading either MAX17320 cell sensor |
| `POWER_GROUND` | `charger_ts_ntc.END_2` | `abstract:power-ground` | the third sensor is populated at one of two indexed compliant-contact locations on the thermally worst slot; open, short, lift and response-time behavior remain HIL gates |
| `CHARGER_REGN` | `nvdc_charger.REGN` | `charger_ilim_top.END_1` | 44.2-kOhm 1% upper leg begins the independent hardware input-current ceiling |
| `CHARGER_ILIM_HIZ` | `charger_ilim_top.END_2` | `nvdc_charger.ILIM_HIZ` | physical target spans about 2.71-3.29 A over REGN and resistor corners and never replaces negotiated IINDPM |
| `CHARGER_ILIM_HIZ` | `nvdc_charger.ILIM_HIZ` | `charger_ilim_bottom.END_1` | 100-kOhm 1% lower leg keeps the pin above HIZ and below the 3.3-A recommended input ceiling |
| `POWER_GROUND` | `charger_ilim_bottom.END_2` | `abstract:power-ground` | hardware ILIM reference is independent of controller software |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_local_scl_pullup.END_1` | local-bus pull-up remains inside TPS, EEPROM and BQ digital voltage ranges |
| `PD_LOCAL_I2C_SCL` | `pd_local_scl_pullup.END_2` | `nvdc_charger.SCL` | one exact 2.2-kOhm pull-up follows the complete TPS25751 plus EEPROM plus charger bus reference |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_local_sda_pullup.END_1` | local data pull-up uses the autonomous TPS switched 3.3-V rail |
| `PD_LOCAL_I2C_SDA` | `pd_local_sda_pullup.END_2` | `nvdc_charger.SDA` | one exact 2.2-kOhm pull-up bounds rise time on the complete local multi-device bus |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `charger_int_pullup.END_1` | charger interrupt pull-up stays valid while the TPS local controller is active |
| `CHARGER_INT_N` | `charger_int_pullup.END_2` | `nvdc_charger.INT` | one physical 10-kOhm pull-up preserves the 256-us active-low interrupt pulse |
| `CHARGER_REGN` | `nvdc_charger.REGN` | `charger_ce_pullup.END_1` | REGN rises before converter start and makes reset/default charge-disable independent of TPS firmware |
| `CHARGE_EN_N` | `charger_ce_pullup.END_2` | `nvdc_charger.CE` | 10-kOhm keeps CE high while TPS GPIO1 is Hi-Z; a valid image uses GPIO1 only as an open-drain active-low enable |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sys_i2c_scl_pullup.END_1` | the host I2C pull-up exists only with the S3 application domain and cannot back-power an off host |
| `SYS_I2C_SCL` | `sys_i2c_scl_pullup.END_2` | `s3.GPIO2` | one exact 2.2-kOhm pull-up serves the complete scheduled host-control bus |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sys_i2c_sda_pullup.END_1` | host data pull-up uses the common live logic domain |
| `SYS_I2C_SDA` | `sys_i2c_sda_pullup.END_2` | `s3.GPIO1` | one exact 2.2-kOhm pull-up serves the complete scheduled host-control bus |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sys_int_pullup.END_1` | the shared interrupt pull-up exists only with the host domain |
| `SYS_INT_N` | `sys_int_pullup.END_2` | `s3.GPIO37` | one exact 10-kOhm pull-up completes the wired-low interrupt tree without consuming another dedicated GPIO |
| `CHARGER_QON_NC` | `nvdc_charger.QON` | `abstract:no-connect` | QON uses its specified internal pull-up; no external system-reset or ship-FET function is claimed |
| `CHARGER_STAT_NC` | `nvdc_charger.STAT` | `abstract:no-connect` | unused open-drain STAT is disabled in the charger image; status and faults use INT/I2C |
| `PD_LOCAL_I2C_SDA` | `pd_controller.I2Cc_SDA` | `pd_config_eeprom.SDA` | dedicated address-0x50 boot image; one EEPROM per controller |
| `PD_LOCAL_I2C_SCL` | `pd_controller.I2Cc_SCL` | `pd_config_eeprom.SCL` | controller loads patch/config autonomously before S3 availability is assumed |
| `PD_LOCAL_I2C_SDA` | `pd_controller.I2Cc_SDA` | `nvdc_charger.SDA` | charger is controlled through the officially supported TPS25751D local-controller topology |
| `PD_LOCAL_I2C_SCL` | `pd_controller.I2Cc_SCL` | `nvdc_charger.SCL` | charger transactions never occupy an RF, display or storage bus |
| `PACK_AOLDO` | `pack_gauge.AOLDO` | `pack_supply_or.A1` | AOLDO supplies only measured low-clock admission below the MAX17320 2-mA source budget; BAV70LT1G blocks fixture/system backfeed |
| `PACK_FIXTURE_3V3` | `abstract:isolated-pack-fixture-3v3` | `pack_supply_or.A2` | fixture supply is isolated from USB/system power and is used for blank-device programming and recovery |
| `PACK_ADMISSION_VDD` | `pack_supply_or.K_COMMON` | `pack_admission.VDD` | common cathode passively ORs AOLDO and fixture sources without firmware control |
| `PACK_SYSTEM_3V3` | `abstract:admitted-system-3v3` | `pack_system_diode.A` | system source exists only after complete pair admission and uses the lower-drop branch |
| `PACK_ADMISSION_VDD` | `pack_system_diode.K` | `pack_admission.VDD` | BAT54-7-F blocks admission VDD from back-powering the admitted system rail |
| `PACK_ADMISSION_VDD` | `pack_supply_or.K_COMMON` | `pack_diag_timer.VCC` | the hardware pulse limiter is alive whenever the admission MCU can request a diagnostic; its ready-state current remains inside the AOLDO budget |
| `PACK_DIAG_TIMER_VCC` | `pack_diag_timer.VCC` | `pack_diag_timer_bypass.END_1` | one exact 100-nF local bypass capacitor supports one-shot switching without coupling the diagnostic edge into the admission ADC reference |
| `PACK_LOCAL_GND` | `pack_diag_timer_bypass.END_2` | `pack_gauge.GND` | timer bypass return stays local to the admission controller and gauge |
| `PACK_LOCAL_GND` | `pack_diag_timer.GND` | `pack_gauge.GND` | one-shot and admission MCU share the same pack-side logic reference |
| `PACK_DIAG_TRIGGER` | `pack_admission.PA22_A4` | `pack_diag_timer.CH1_T` | firmware emits a rising edge only; holding or repeatedly toggling the pin cannot extend an active non-retriggerable pulse |
| `PACK_DIAG_TRIGGER` | `pack_admission.PA22_A4` | `pack_diag_trigger_pulldown.END_1` | the exact 10-kOhm pull-down prevents a reset-default high-impedance contact from producing a diagnostic pulse |
| `PACK_LOCAL_GND` | `pack_diag_trigger_pulldown.END_2` | `pack_gauge.GND` | trigger default is low in reset, fixture handover and unpowered-MCU states |
| `PACK_DIAG_CH1_FALLING_TRIGGER_DISABLED` | `pack_diag_timer.CH1_T_N` | `pack_gauge.GND` | the unused falling-edge trigger is fixed low for rising-edge-only operation |
| `PACK_DIAG_REFRACTORY_CLEAR_N` | `pack_diag_timer.CH2_Q_N` | `pack_diag_timer.CH1_CLR_N` | complementary channel-2 output is high while ready and asynchronously holds channel 1 clear throughout every hardware refractory interval |
| `PACK_DIAG_TIMER_RC_SUPPLY` | `pack_diag_timer.VCC` | `pack_diag_timer_res.END_1` | 169-kOhm 1% timing resistance reuses an existing BOM line |
| `PACK_DIAG_TIMER_RC` | `pack_diag_timer_res.END_2` | `pack_diag_timer.CH1_RC` | the timing node follows the TPUL2G223 manufacturer connection |
| `PACK_DIAG_TIMER_RC` | `pack_diag_timer.CH1_RC` | `pack_diag_timer_cap.END_1` | 169-kOhm with 220-nF yields about 34.4 ms typical |
| `PACK_DIAG_TIMER_C` | `pack_diag_timer_cap.END_2` | `pack_diag_timer.CH1_C` | the exact C0G timing capacitor bounds both sides of the paper pulse window without X7R DC-bias or aging ambiguity |
| `PACK_LOCAL_GND` | `pack_diag_timer.CH1_C` | `pack_gauge.GND` | the optional external C-terminal ground is used to give the timing capacitor an explicit local return |
| `PACK_DIAG_GATE` | `pack_diag_timer.CH1_Q` | `pack_diag_switch.G` | only the hardware one-shot output, never a direct MCU level, can hold the diagnostic MOSFET on |
| `PACK_DIAG_GATE` | `pack_diag_switch.G` | `pack_diag_gate_pulldown.END_1` | the MOSFET gate remains low if the one-shot supply is absent or its output is high impedance |
| `PACK_LOCAL_GND` | `pack_diag_gate_pulldown.END_2` | `pack_gauge.GND` | 10-kOhm gate pull-down fails the diagnostic load off |
| `PACK_DIAG_CH1_Q_N_NC` | `pack_diag_timer.CH1_Q_N` | `abstract:no-connect` | unused push-pull complementary channel-1 output is left open as required |
| `PACK_DIAG_PULSE_ACTIVE` | `pack_diag_timer.CH1_Q` | `pack_diag_timer.CH2_T_N` | the falling edge at the natural end of channel 1 starts channel 2; the rising edge at pulse start cannot trigger the falling-edge input |
| `PACK_DIAG_CH2_RISING_GATE_HIGH` | `pack_diag_timer.VCC` | `pack_diag_timer.CH2_T` | the channel-2 rising-edge gate is fixed high so only the channel-1 Q falling edge is accepted |
| `PACK_DIAG_CH2_CLEAR_RELEASED` | `pack_diag_timer.VCC` | `pack_diag_timer.CH2_CLR_N` | channel 2 remains independently non-retriggerable and cannot be shortened by firmware |
| `PACK_DIAG_LOCKOUT_RC_SUPPLY` | `pack_diag_timer.VCC` | `pack_diag_lockout_res.END_1` | exact 620-kOhm 1% resistance begins the bounded hardware refractory timer |
| `PACK_DIAG_LOCKOUT_RC` | `pack_diag_lockout_res.END_2` | `pack_diag_timer.CH2_RC` | the channel-2 timing node follows the manufacturer connection |
| `PACK_DIAG_LOCKOUT_RC` | `pack_diag_timer.CH2_RC` | `pack_diag_lockout_cap.END_1` | 620-kOhm and 1-uF yield about 569 ms typical and remain inside the TPUL2G223 supported pulse-width range |
| `PACK_DIAG_LOCKOUT_C` | `pack_diag_lockout_cap.END_2` | `pack_diag_timer.CH2_C` | the exact TDK X7R part is screened with initial, temperature and 3.3-V DC-bias loss for at least 350 ms hardware lockout |
| `PACK_LOCAL_GND` | `pack_diag_timer.CH2_C` | `pack_gauge.GND` | the channel-2 timing capacitor has an explicit local return |
| `PACK_DIAG_CH2_Q_NC` | `pack_diag_timer.CH2_Q` | `abstract:no-connect` | unused push-pull active-high channel-2 output is left open as required |
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
| `PACK_CELL0_TEMP` | `pack_gauge.TH1` | `pack_ntc0.END_1` | one exact 10-kOhm NTC uses a dedicated insulated compliant contact through the open holder window to the middle third of cell 0; compression and response remain I8/HIL gates |
| `PACK_LOCAL_GND` | `pack_ntc0.END_2` | `pack_gauge.GND` | TH1 uses the MAX17320 internal pullup and protected 10-kOhm mode |
| `PACK_CELL1_TEMP` | `pack_gauge.TH2` | `pack_ntc1.END_1` | one exact 10-kOhm NTC uses a dedicated insulated compliant contact through the open holder window to the middle third of cell 1; compression and response remain I8/HIL gates |
| `PACK_LOCAL_GND` | `pack_ntc1.END_2` | `pack_gauge.GND` | TH2 uses the MAX17320 internal pullup and protected 10-kOhm mode |
| `PACK_SLOT0_POSITIVE_RAW` | `pack_cell0.POS` | `pack_holder.SLOT0_POS` | only the exact protected button-top qualification target is modeled; physical polarity and received-lot identity remain admission prerequisites |
| `PACK_LOCAL_GND` | `pack_cell0.NEG` | `pack_holder.SLOT0_NEG` | the exact cell negative end reaches local pack ground only through the mechanically polarized holder contact |
| `PACK_SLOT1_POSITIVE_RAW` | `pack_cell1.POS` | `pack_holder.SLOT1_POS` | the upper exact protected cell remains a separately replaceable physical device with its own holder contact and fuse path |
| `PACK_2S_MIDPOINT` | `pack_cell1.NEG` | `pack_holder.SLOT1_NEG` | the upper cell negative end forms the supervised midpoint only after correct physical insertion into the exact holder |
| `PACK_SLOT0_POSITIVE_RAW` | `pack_holder.SLOT0_POS` | `pack_fuse0.END_1` | the polarized holder exposes the lower-cell positive contact separately and the adjacent 5-A fuse remains slot-specific |
| `PACK_2S_MIDPOINT` | `pack_fuse0.END_2` | `abstract:protected-2s-midpoint` | slot-0 fuse opens independently; holder polarity and reverse-insertion blocking remain mechanical/electrical gates |
| `PACK_LOCAL_GND` | `pack_holder.SLOT0_NEG` | `pack_gauge.GND` | the lower-cell negative contact is independently exposed; reverse insertion remains open before this local reference is reached |
| `PACK_2S_MIDPOINT` | `pack_holder.SLOT1_NEG` | `abstract:protected-2s-midpoint` | the upper-cell negative contact is independently exposed and forms the supervised 2S midpoint only in the PCB routing |
| `PACK_SLOT1_POSITIVE_RAW` | `pack_holder.SLOT1_POS` | `pack_fuse1.END_1` | the polarized holder exposes the upper-cell positive contact separately and the adjacent 5-A fuse remains slot-specific |
| `BATTERY_STACK_POSITIVE` | `pack_fuse1.END_2` | `abstract:qualified-2s-positive` | slot-1 fuse opens independently; holder polarity and reverse-insertion blocking remain mechanical/electrical gates |
| `PACK_DIAG_LOAD_POSITIVE` | `abstract:qualified-2s-positive` | `pack_diag_res0.END_1` | the first 20-Ohm 2-W pulse-rated branch samples the fused full stack ahead of the normally-open CHG/DIS pair |
| `PACK_DIAG_LOAD_POSITIVE` | `abstract:qualified-2s-positive` | `pack_diag_res1.END_1` | the second equal branch provides exact 10-Ohm total resistance and shares both pulse and hostile-repetition heat |
| `PACK_DIAG_LOAD_DRAIN` | `pack_diag_res0.END_2` | `pack_diag_switch.D` | one-percent matched-value branches bound effective load resistance to 9.9-10.1 Ohm before MOSFET resistance |
| `PACK_DIAG_LOAD_DRAIN` | `pack_diag_res1.END_2` | `pack_diag_switch.D` | each resistor sees half the approximately 7.82-W worst-screen load and remains below the official 50-ms pulse curve |
| `PACK_LOCAL_GND` | `pack_diag_switch.S` | `pack_gauge.GND` | the 20-V low-gate-drive MOSFET closes only the bounded pre-admission diagnostic path |
| `PACK_MID_DIV_TOP` | `abstract:protected-2s-midpoint` | `pack_mid_adc_top0.END_1` | first 220-kOhm series element begins the protected midpoint divider |
| `PACK_MID_DIV_SERIES` | `pack_mid_adc_top0.END_2` | `pack_mid_adc_top1.END_1` | two physical top resistors limit fault and injection current rather than relying on one high-side element |
| `PACK_CELL0_ADC` | `pack_mid_adc_top1.END_2` | `pack_admission.PA25_A2` | 2x220-kOhm over 169-kOhm keeps the 4.3-V screen corner below 1.21 V with 1% resistor tolerance |
| `PACK_CELL0_ADC` | `pack_admission.PA25_A2` | `pack_mid_adc_bottom.END_1` | 169-kOhm bottom resistor reuses an active stocked BOM value |
| `PACK_LOCAL_GND` | `pack_mid_adc_bottom.END_2` | `pack_gauge.GND` | midpoint divider return shares the quiet admission ADC reference |
| `PACK_CELL0_ADC` | `pack_admission.PA25_A2` | `pack_mid_adc_filter.END_1` | 10-nF filter supports a bounded settled sample rather than sampling the load edge |
| `PACK_LOCAL_GND` | `pack_mid_adc_filter.END_2` | `pack_gauge.GND` | midpoint ADC filter return stays at the admission reference |
| `PACK_STACK_DIV_TOP` | `abstract:qualified-2s-positive` | `pack_stack_adc_top0.END_1` | first of five 220-kOhm series elements begins the fused full-stack divider |
| `PACK_STACK_DIV_SERIES_01` | `pack_stack_adc_top0.END_2` | `pack_stack_adc_top1.END_1` | series construction distributes voltage and bounds single-element stress |
| `PACK_STACK_DIV_SERIES_12` | `pack_stack_adc_top1.END_2` | `pack_stack_adc_top2.END_1` | series construction distributes voltage and bounds single-element stress |
| `PACK_STACK_DIV_SERIES_23` | `pack_stack_adc_top2.END_2` | `pack_stack_adc_top3.END_1` | series construction distributes voltage and bounds single-element stress |
| `PACK_STACK_DIV_SERIES_34` | `pack_stack_adc_top3.END_2` | `pack_stack_adc_top4.END_1` | series construction distributes voltage and bounds single-element stress |
| `PACK_STACK_ADC` | `pack_stack_adc_top4.END_2` | `pack_admission.PA26_A1` | 5x220-kOhm over 169-kOhm keeps the 8.6-V screen corner below 1.17 V with 1% resistor tolerance |
| `PACK_STACK_ADC` | `pack_admission.PA26_A1` | `pack_stack_adc_bottom.END_1` | 169-kOhm bottom resistor completes the full-stack divider |
| `PACK_LOCAL_GND` | `pack_stack_adc_bottom.END_2` | `pack_gauge.GND` | stack divider return shares the quiet admission ADC reference |
| `PACK_STACK_ADC` | `pack_admission.PA26_A1` | `pack_stack_adc_filter.END_1` | 10-nF filter supports a bounded settled sample and rejects the load-switch edge |
| `PACK_LOCAL_GND` | `pack_stack_adc_filter.END_2` | `pack_gauge.GND` | stack ADC filter return stays at the admission reference |
| `CHARGER_INT_N` | `nvdc_charger.INT` | `pd_controller.I2Cc_IRQ` | active-low charger status/fault returns to the PD controller without a new MCU contact |
| `PD_EEPROM_WP` | `pd_controller.GPIO0` | `pd_config_eeprom.WP` | external pull-up protects the image at reset; TPS may drive low only inside an S3-authorized signed update window |
| `CHARGE_EN_N` | `pd_controller.GPIO1` | `nvdc_charger.CE` | GPIO1 is open-drain only; exact REGN pull-up disables charge while TPS configuration is absent/invalid and valid policy sinks only after IINDPM is written |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_config_eeprom.VCC` | the boot EEPROM is powered by the controller LDO during raw-VBUS dead-battery startup |
| `PD_LOCAL_3V3` | `pd_config_eeprom.VCC` | `pd_eeprom_bypass.END_1` | one exact 100-nF 50-V X7R bypass is placed at the EEPROM supply |
| `POWER_GROUND` | `pd_eeprom_bypass.END_2` | `abstract:power-ground` | EEPROM bypass return is short and local |
| `POWER_GROUND` | `pd_config_eeprom.VSS` | `abstract:power-ground` | EEPROM ground is explicit for both product and recovery fixtures |
| `PD_LOCAL_3V3` | `pd_controller.LDO_3V3` | `pd_eeprom_wp_pullup.END_1` | WP defaults high whenever the EEPROM is powered |
| `PD_EEPROM_WP` | `pd_eeprom_wp_pullup.END_2` | `pd_config_eeprom.WP` | exact 10-kOhm pull-up dominates reset Hi-Z while allowing the controller open-drain output to authorize writes |
| `PD_EEPROM_A0_LOW` | `abstract:power-ground` | `pd_config_eeprom.A0` | fixed 7-bit address 0x50 |
| `PD_EEPROM_A1_LOW` | `abstract:power-ground` | `pd_config_eeprom.A1` | fixed 7-bit address 0x50 |
| `PD_EEPROM_A2_LOW` | `abstract:power-ground` | `pd_config_eeprom.A2` | fixed 7-bit address 0x50 |
| `PD_USB_P_UNUSED_LOW` | `pd_controller.GPIO4_USB_P_LD1` | `abstract:power-ground` | BC1.2/liquid detection is disabled here so product D+ remains direct to S3; datasheet requires unused contact low |
| `PD_USB_N_UNUSED_LOW` | `pd_controller.GPIO5_USB_N_LD2` | `abstract:power-ground` | BC1.2/liquid detection is disabled here so product D- remains direct to S3; datasheet requires unused contact low |
| `CHARGER_DP_NC` | `nvdc_charger.D_PLUS` | `abstract:no-connect` | BQ DPDM detection is disabled and isolated from the protected native S3 USB2 data pair |
| `CHARGER_DM_NC` | `nvdc_charger.D_MINUS` | `abstract:no-connect` | BQ DPDM detection is disabled and isolated from the protected native S3 USB2 data pair |
| `NVDC_SYS` | `nvdc_charger.SYS` | `aon_buck.VIN` | the AON source is independent of every application rail and remains available on admitted battery or valid USB system power |
| `NVDC_SYS` | `nvdc_charger.SYS` | `aon_input_cap.END_1` | one exact 4.7-uF 25-V X7R input capacitor is the TPS629203 nominal local input target |
| `POWER_GROUND` | `aon_input_cap.END_2` | `abstract:power-ground` | the AON input-capacitor loop must be placed directly at VIN and GND |
| `AON_BUCK_EN` | `nvdc_charger.SYS` | `aon_buck.EN` | direct hardware strap is manufacturer-valid, has no uncertain divider against the internal fail-low pull-down and enables AON without application firmware |
| `AON_BUCK_SW` | `aon_buck.SW` | `aon_inductor.END_1` | 2.2-uH shielded inductor is the manufacturer-nominal 2.5-MHz first target |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `abstract:AON_RAW_3V3` | regulated converter output is deliberately separated from the safety rail by an independent overvoltage/current boundary |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `aon_output_cap.END_1` | one exact 22-uF 10-V X7R capacitor provides the recommended nominal converter output capacitance before the protection boundary |
| `POWER_GROUND` | `aon_output_cap.END_2` | `abstract:power-ground` | VOS senses the capacitor positive terminal and its return remains local to the converter |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `aon_efuse.IN` | TPS25961 is an independent series cutoff for a shorted converter high-side switch, overload, short and thermal fault |
| `AON_EFUSE_EN` | `aon_inductor.END_2` | `aon_efuse.EN_UVLO` | direct raw-rail tie is manufacturer-valid below 5 V and gives firmware no bypass path |
| `POWER_GROUND` | `aon_efuse.GND` | `abstract:power-ground` | exposed pad and ground contact share the short local power return |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `aon_efuse_input_cap.END_1` | 100-nF 50-V X7R sits directly at the eFuse input in addition to the converter output bank |
| `POWER_GROUND` | `aon_efuse_input_cap.END_2` | `abstract:power-ground` | local high-frequency eFuse input return |
| `AON_EFUSE_ILIM` | `aon_efuse.ILIM` | `aon_efuse_rilim.END_1` | 240-kOhm sets about 0.208-A nominal limit, above protected AON startup and load demand but below converter capability |
| `POWER_GROUND` | `aon_efuse_rilim.END_2` | `abstract:power-ground` | one exact current-limit resistor; open moves TPS25961 toward its minimum limit rather than disabling protection |
| `AON_RAW_3V3` | `aon_inductor.END_2` | `aon_efuse_ovlo_top.END_1` | 196-kOhm 1% starts the independent AON overvoltage divider |
| `AON_EFUSE_OVLO` | `aon_efuse_ovlo_top.END_2` | `aon_efuse.OVLO` | 196/100-kOhm divider yields a 3.505-to-3.809-V full-corner cutoff window |
| `AON_EFUSE_OVLO` | `aon_efuse.OVLO` | `aon_efuse_ovlo_bottom.END_1` | OVLO is never left floating |
| `POWER_GROUND` | `aon_efuse_ovlo_bottom.END_2` | `abstract:power-ground` | 100-kOhm 1% completes the OVLO divider |
| `AON_SAFE_3V3` | `aon_efuse.OUT` | `abstract:AON_SAFE_3V3` | only the independently protected output powers the supervisor, hard-STOP logic and PD VIN_3V3 |
| `AON_SAFE_3V3` | `aon_efuse.OUT` | `aon_efuse_output_cap.END_1` | 10-uF 6.3-V X5R is the exact protected-side hold-up and local output capacitor |
| `POWER_GROUND` | `aon_efuse_output_cap.END_2` | `abstract:power-ground` | protected AON local return |
| `AON_SAFE_3V3` | `aon_efuse.OUT` | `aon_pg_pullup.END_1` | 47-kOhm pull-up exists only after the independent cutoff and limits the always-on PG load to about 70 uA |
| `AON_PG_N` | `aon_pg_pullup.END_2` | `aon_buck.PG` | open-drain AON evidence has a defined high only after its own output rail exists |
| `AON_RAW_3V3_SENSE` | `abstract:AON_RAW_3V3` | `aon_buck.VOS` | converter remote sense remains at its own pre-eFuse output capacitor; the supervisor independently validates the protected output |
| `AON_VSET_3V3_NC` | `abstract:no-connect-open-vset` | `aon_buck.FB_VSET` | FB/VSET is deliberately left open; the datasheet decodes open or at least 249 kOhm as fixed 3.3 V |
| `AON_MODE_SET` | `aon_buck.MODE_SCONF` | `aon_mode_res.END_1` | 42.2-kOhm 1% selects VSET, up-to-2.5-MHz auto-PFM/PWM AEE and disabled output discharge |
| `POWER_GROUND` | `aon_mode_res.END_2` | `abstract:power-ground` | fixed resistor strap is read at startup and cannot be changed by application firmware |
| `AON_PG_N` | `aon_buck.PG` | `safe_supervisor.MR_N` | the pulled-up converter PG directly holds the exact AON supervisor in manual reset until the converter reports valid output; there is no programmable source-sequencer dependency |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_buck.VIN` | independent fixed converter prevents compute transients from changing voice or accessory voltage |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_input_cap.END_1` | 22-uF 25-V X7R local bulk input capacitor exceeds the TPS564252 nominal input recommendation |
| `POWER_GROUND` | `main_input_cap.END_2` | `abstract:power-ground` | main bulk input return stays inside the high-current switching loop |
| `NVDC_SYS` | `nvdc_charger.SYS` | `main_hf_input_cap.END_1` | 100-nF 50-V X7R directly shunts high-frequency VIN current |
| `POWER_GROUND` | `main_hf_input_cap.END_2` | `abstract:power-ground` | main high-frequency input return is placed directly at converter ground |
| `POR_N` | `safe_supervisor.RESET_N` | `main_buck.EN` | the exact open-drain AON supervisor releases the main converter only after AON PG, the 3.07-V SENSE threshold and the CT delay all pass |
| `POR_N` | `main_buck.EN` | `main_en_pulldown.END_1` | external 100-kOhm reset-low default with the exact 10-kOhm POR pull-up releases to about 3.0V, above the converter's 1.25-V maximum rising threshold |
| `POWER_GROUND` | `main_en_pulldown.END_2` | `abstract:power-ground` | main converter stays disabled if the AON POR pull-up or AON source is absent |
| `MAIN_BUCK_SW` | `main_buck.SW` | `main_inductor.END_1` | 3.3-uH exact first target keeps the 3-A load-step peak below its minimum saturation current |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `abstract:MAIN_RAW_3V3` | regulated output is a raw converter rail until the independent latch-off protection accepts it |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_fb_top.END_1` | active 45.3-kOhm replacement for the obsolete 45.0-kOhm table value starts the fixed main feedback divider |
| `MAIN_3V3_FB` | `main_fb_top.END_2` | `main_buck.FB` | 45.3-kOhm over 10-kOhm sets nominal 3.318 V without a selector or firmware control |
| `MAIN_3V3_FB` | `main_buck.FB` | `main_fb_bottom.END_1` | 1% bottom resistor completes the fixed main feedback divider |
| `POWER_GROUND` | `main_fb_bottom.END_2` | `abstract:power-ground` | quiet Kelvin feedback return must not share the switching-current return |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_ff_cap.END_1` | 33-pF C0G feed-forward capacitor stays inside the datasheet 10-to-100-pF high-output range |
| `MAIN_3V3_FB` | `main_ff_cap.END_2` | `main_buck.FB` | feed-forward element is physically across the top divider resistor |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_output_cap0.END_1` | first physical 22-uF 25-V X7R pre-eFuse capacitor contributes to the recommended 44-uF nominal converter bank |
| `POWER_GROUND` | `main_output_cap0.END_2` | `abstract:power-ground` | first main output capacitor closes the local power loop |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_output_cap1.END_1` | second independent 22-uF 25-V X7R pre-eFuse capacitor preserves DC-bias and transient margin |
| `POWER_GROUND` | `main_output_cap1.END_2` | `abstract:power-ground` | second main output capacitor closes the local power loop |
| `MAIN_RAW_3V3_PG_N` | `main_buck.PG` | `abstract:main-raw-converter-pg-test` | raw converter PG is a fixture-pulled diagnostic point and cannot certify the protected load side |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_efuse.IN` | independent latch-off circuit breaker interrupts converter high-side short overvoltage and downstream overload faults |
| `MAIN_EFUSE_EN` | `main_inductor.END_2` | `main_efuse.EN_UVLO` | direct sub-5-V raw-rail tie is manufacturer-valid and cannot be bypassed by firmware |
| `POWER_GROUND` | `main_efuse.GND` | `abstract:power-ground` | short low-inductance protection return |
| `MAIN_EFUSE_ILM` | `main_efuse.ILM` | `main_efuse_rilm.END_1` | 1.65-kOhm sets a guaranteed 3.2-to-3.715-A circuit-breaker threshold above the accepted 3.0-A step |
| `POWER_GROUND` | `main_efuse_rilm.END_2` | `abstract:power-ground` | ILM open or short are both detected fail-safe single-point states by TPS25974 |
| `MAIN_EFUSE_DVDT` | `main_efuse.DVDT` | `main_efuse_dvdt_cap.END_1` | 4.7-nF controls protected-output rise to about 4.7 ms at 3.3 V |
| `POWER_GROUND` | `main_efuse_dvdt_cap.END_2` | `abstract:power-ground` | exact slew capacitor limits protected-side inrush |
| `MAIN_EFUSE_ITIMER` | `main_efuse.ITIMER` | `main_efuse_itimer_cap.END_1` | 120-pF C0G permits only about 0.09-ms nominal sub-fast-trip overload before latch-off |
| `POWER_GROUND` | `main_efuse_itimer_cap.END_2` | `abstract:power-ground` | bounded timer does not defeat the independent fast-trip path |
| `MAIN_RAW_3V3` | `main_inductor.END_2` | `main_efuse_ovlo_top.END_1` | 191-kOhm 0.1% thin-film top resistor begins the tight main-rail OVLO divider |
| `MAIN_EFUSE_OVLO` | `main_efuse_ovlo_top.END_2` | `main_efuse.OVLO` | precision divider keeps full-corner cutoff between 3.438 and 3.578 V |
| `MAIN_EFUSE_OVLO` | `main_efuse.OVLO` | `main_efuse_ovlo_bottom.END_1` | OVLO is never left floating |
| `POWER_GROUND` | `main_efuse_ovlo_bottom.END_2` | `abstract:power-ground` | 100-kOhm 0.1% thin-film bottom resistor completes the narrow safe window |
| `3V3_MAIN` | `main_efuse.OUT` | `abstract:3V3_MAIN` | only the protected output supplies compute, UI and quiet-state switches at 2.5-A continuous and 3.0-A step demand |
| `3V3_MAIN` | `main_efuse.OUT` | `main_efuse_output_cap.END_1` | 10-uF 6.3-V X5R is the exact local protected-side capacitor |
| `POWER_GROUND` | `main_efuse_output_cap.END_2` | `abstract:power-ground` | protected main local return |
| `3V3_MAIN` | `main_efuse.OUT` | `main_efuse_pg_top.END_1` | 45.3-kOhm 1% starts the protected-output power-good divider |
| `MAIN_EFUSE_PGTH` | `main_efuse_pg_top.END_2` | `main_efuse.PGTH` | 45.3/30-kOhm divider asserts only after the protected rail crosses approximately 3.0 V |
| `MAIN_EFUSE_PGTH` | `main_efuse.PGTH` | `main_efuse_pg_bottom.END_1` | PGTH directly measures protected output, not raw converter output |
| `POWER_GROUND` | `main_efuse_pg_bottom.END_2` | `abstract:power-ground` | 30-kOhm 1% completes the PG divider |
| `MAIN_3V3_PG_N` | `main_efuse.PG` | `abstract:power-current-thermal-fault` | protected-rail PG replaces raw converter PG as the diagnostic aggregate source |
| `3V3_MAIN` | `main_efuse.OUT` | `power_fault_pullup.END_1` | one exact pull-up serves the entire wired-low fault aggregate only while its protected diagnostic domain is powered |
| `POWER_FAULT_N` | `power_fault_pullup.END_2` | `abstract:power-current-thermal-fault` | 10-kOhm limits any asserting PG, FLT or qualifier sink to about 0.33 mA |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_buck.VIN` | voice has a physically independent fixed-voltage converter rather than a shared 4/5-V selector |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_input_cap.END_1` | 22-uF 25-V X7R local bulk input capacitor keeps the voice switching loop independent |
| `POWER_GROUND` | `voice_input_cap.END_2` | `abstract:power-ground` | voice bulk input return stays inside its own high-current switching loop |
| `NVDC_SYS` | `nvdc_charger.SYS` | `voice_hf_input_cap.END_1` | 100-nF 50-V X7R directly shunts high-frequency voice-converter VIN current |
| `POWER_GROUND` | `voice_hf_input_cap.END_2` | `abstract:power-ground` | voice high-frequency input return is placed directly at converter ground |
| `VOICE_BUCK_SW` | `voice_buck.SW` | `voice_inductor.END_1` | 3.3-uH exact first target has margin over the qualified 1.5-A transient peak current |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `abstract:VVOICE_RAW_4V` | fixed 4.0-V converter output is raw until the independent latch-off protection accepts it |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_fb_top.END_1` | 68-kOhm 1% top resistor starts the physically fixed voice feedback divider |
| `VOICE_4V_FB` | `voice_fb_top.END_2` | `voice_buck.FB` | 68-kOhm over 12-kOhm sets nominal 4.000 V without a selector |
| `VOICE_4V_FB` | `voice_buck.FB` | `voice_fb_bottom.END_1` | 12-kOhm 1% bottom resistor completes the fixed voice divider |
| `POWER_GROUND` | `voice_fb_bottom.END_2` | `abstract:power-ground` | quiet Kelvin return prevents load current from shifting the voice set point |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_ff_cap.END_1` | 33-pF C0G feed-forward capacitor follows the datasheet high-output recommendation |
| `VOICE_4V_FB` | `voice_ff_cap.END_2` | `voice_buck.FB` | feed-forward element is physically across the voice top divider resistor |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_output_cap0.END_1` | first physical 22-uF 25-V X7R pre-eFuse capacitor supports converter stability and startup |
| `POWER_GROUND` | `voice_output_cap0.END_2` | `abstract:power-ground` | first voice output capacitor closes its local power loop |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_output_cap1.END_1` | second independent 22-uF 25-V X7R pre-eFuse capacitor completes the 44-uF nominal converter bank |
| `POWER_GROUND` | `voice_output_cap1.END_2` | `abstract:power-ground` | second voice output capacitor closes its local power loop |
| `VOICE_RAW_4V_PG_N` | `voice_buck.PG` | `abstract:voice-raw-converter-pg-test` | raw converter PG is fixture-only and cannot certify the protected module supply |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_efuse.IN` | independent latch-off circuit breaker interrupts converter high-side short overvoltage and downstream overload faults |
| `VOICE_EFUSE_EN` | `voice_inductor.END_2` | `voice_efuse.EN_UVLO` | direct sub-5-V raw-rail tie is manufacturer-valid and cannot be bypassed by firmware |
| `POWER_GROUND` | `voice_efuse.GND` | `abstract:power-ground` | short low-inductance protection return |
| `VOICE_EFUSE_ILM` | `voice_efuse.ILM` | `voice_efuse_rilm.END_1` | 3.32-kOhm sets a guaranteed 1.55-to-1.905-A circuit-breaker threshold above the accepted 1.5-A transient |
| `POWER_GROUND` | `voice_efuse_rilm.END_2` | `abstract:power-ground` | ILM open or short are both detected fail-safe single-point states by TPS25974 |
| `VOICE_EFUSE_DVDT` | `voice_efuse.DVDT` | `voice_efuse_dvdt_cap.END_1` | 4.7-nF controls protected-output rise to about 5.7 ms at 4.0 V |
| `POWER_GROUND` | `voice_efuse_dvdt_cap.END_2` | `abstract:power-ground` | exact slew capacitor limits module-side inrush |
| `VOICE_EFUSE_ITIMER` | `voice_efuse.ITIMER` | `voice_efuse_itimer_cap.END_1` | 120-pF C0G permits only about 0.09-ms nominal sub-fast-trip overload before latch-off |
| `POWER_GROUND` | `voice_efuse_itimer_cap.END_2` | `abstract:power-ground` | bounded timer preserves fast-trip short protection |
| `VVOICE_RAW_4V` | `voice_inductor.END_2` | `voice_efuse_ovlo_top.END_1` | 270-kOhm 1% starts the independent voice-rail overvoltage divider |
| `VOICE_EFUSE_OVLO` | `voice_efuse_ovlo_top.END_2` | `voice_efuse.OVLO` | 270/100-kOhm divider yields a 4.314-to-4.610-V full-corner cutoff window |
| `VOICE_EFUSE_OVLO` | `voice_efuse.OVLO` | `voice_efuse_ovlo_bottom.END_1` | OVLO is never left floating |
| `POWER_GROUND` | `voice_efuse_ovlo_bottom.END_2` | `abstract:power-ground` | 100-kOhm 1% completes the OVLO divider |
| `VVOICE_4V` | `voice_efuse.OUT` | `voice.VCC` | only the protected fixed 4.0-V rail powers the SA518; it can never be switched to the 5-V accessory setting |
| `VVOICE_4V` | `voice_efuse.OUT` | `voice_efuse_output_cap.END_1` | 10-uF 6.3-V X5R is the exact local protected-side capacitor |
| `POWER_GROUND` | `voice_efuse_output_cap.END_2` | `abstract:power-ground` | protected voice local return |
| `VVOICE_4V` | `voice_efuse.OUT` | `voice_efuse_pg_top.END_1` | 68-kOhm 1% starts the protected-output power-good divider |
| `VOICE_EFUSE_PGTH` | `voice_efuse_pg_top.END_2` | `voice_efuse.PGTH` | 68/33-kOhm divider asserts only after the protected rail crosses approximately 3.67 V |
| `VOICE_EFUSE_PGTH` | `voice_efuse.PGTH` | `voice_efuse_pg_bottom.END_1` | PGTH directly measures protected output, not raw converter output |
| `POWER_GROUND` | `voice_efuse_pg_bottom.END_2` | `abstract:power-ground` | 33-kOhm 1% completes the PG divider |
| `VOICE_4V_PG_N` | `voice_efuse.PG` | `abstract:voice-power-reset-domain` | PD remains asserted until the protected 4-V rail and internal eFuse power path are valid |
| `3V3_MAIN` | `main_efuse.OUT` | `voice_pg_pullup.END_1` | voice protected-PG is referenced only to the powered diagnostic domain |
| `VOICE_4V_PG_N` | `voice_pg_pullup.END_2` | `voice_efuse.PG` | 10-kOhm draws at most about 0.33 mA when the open-drain protected PG is low |
| `VOICE_4V_PG_N` | `voice_efuse.PG` | `voice_pg_qualifier.E` | the protected-rail PG input is qualified by the same STOP-dominant enable request |
| `VOICE_4V_FAULT_QUAL_N` | `voice_pg_qualifier.C` | `abstract:power-current-thermal-fault` | open collector sinks only for EN=1 and PG=0; a normally disabled voice rail releases POWER_FAULT_N |
| `NVDC_SYS` | `nvdc_charger.SYS` | `ext_buck.VIN` | external 5 V has a dedicated converter and cannot disturb fixed voice voltage |
| `NVDC_SYS` | `nvdc_charger.SYS` | `ext_buck_input_cap.END_1` | 22-uF 25-V X7R local bulk input capacitor keeps accessory load steps out of the other converter loops |
| `POWER_GROUND` | `ext_buck_input_cap.END_2` | `abstract:power-ground` | accessory-buck bulk input return stays inside its own switching loop |
| `NVDC_SYS` | `nvdc_charger.SYS` | `ext_buck_hf_input_cap.END_1` | 100-nF 50-V X7R directly shunts high-frequency accessory-converter VIN current |
| `POWER_GROUND` | `ext_buck_hf_input_cap.END_2` | `abstract:power-ground` | accessory-buck high-frequency input return is placed directly at converter ground |
| `EXT_BUCK_SW` | `ext_buck.SW` | `ext_inductor.END_1` | 4.7-uH exact first target limits ripple while preserving the 2-A transient envelope |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_efuse.IN` | the eFuse is the final series element before the externally accessible connector |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_buck_fb_top.END_1` | 220-kOhm 1% top resistor starts the physically fixed accessory feedback divider |
| `EXT_5V_FB` | `ext_buck_fb_top.END_2` | `ext_buck.FB` | 220-kOhm over 30-kOhm sets nominal 5.000 V without a shared voice/accessory selector |
| `EXT_5V_FB` | `ext_buck.FB` | `ext_buck_fb_bottom.END_1` | 30-kOhm 1% bottom resistor completes the fixed accessory divider |
| `POWER_GROUND` | `ext_buck_fb_bottom.END_2` | `abstract:power-ground` | quiet Kelvin feedback return prevents connector current from shifting the set point |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_buck_ff_cap.END_1` | 33-pF C0G feed-forward capacitor follows the datasheet 5-V recommendation |
| `EXT_5V_FB` | `ext_buck_ff_cap.END_2` | `ext_buck.FB` | feed-forward element is physically across the accessory top divider resistor |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_buck_output_cap0.END_1` | first physical 22-uF 25-V X7R output capacitor supports eFuse startup and post-start load steps |
| `POWER_GROUND` | `ext_buck_output_cap0.END_2` | `abstract:power-ground` | first accessory-buck output capacitor closes its local power loop |
| `5V_EXT_PREPROTECT` | `ext_inductor.END_2` | `ext_buck_output_cap1.END_1` | second independent 22-uF 25-V X7R output capacitor completes the recommended 44-uF nominal bank |
| `POWER_GROUND` | `ext_buck_output_cap1.END_2` | `abstract:power-ground` | second accessory-buck output capacitor closes its local power loop |
| `3V3_MAIN` | `main_efuse.OUT` | `ext_pg_pullup.END_1` | accessory PG is referenced only to the protected powered diagnostic domain |
| `EXT_5V_PG_N` | `ext_pg_pullup.END_2` | `ext_buck.PG` | 10-kOhm draws at most about 0.33 mA when the open-drain PG is low, far below its 4-mA rating |
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
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_power_input_cap.END_1` | exact 1-uF local switch-input bypass follows the TPS22919 evaluation profile |
| `POWER_GROUND` | `sd_power_input_cap.END_2` | `abstract:power-ground` | short local input-capacitor return |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_power_switch.IN` | controlled-rise self-protected switch isolates card inrush and hard shorts from the shared compute rail |
| `POWER_GROUND` | `sd_power_switch.GND` | `abstract:power-ground` | short local switch return |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd.VDD` | card rail exists only during a bounded storage session |
| `SD_QOD` | `sd_power_switch.QOD` | `sd_power_switch.VOUT` | direct internal 24-Ohm QOD discharges card, buffer and local bulk after a qualified flush/unmount sequence |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_power_bulk_cap.END_1` | exact 22-uF 6.3-V X5R local bulk supports card write-current transients |
| `POWER_GROUND` | `sd_power_bulk_cap.END_2` | `abstract:power-ground` | bulk return stays beside the socket and signal isolators |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_power_hf_cap.END_1` | exact 100-nF high-frequency card-rail bypass |
| `POWER_GROUND` | `sd_power_hf_cap.END_2` | `abstract:power-ground` | high-frequency return stays local |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_host_buffer.VCC` | host-to-card buffer disappears electrically with the card rail and uses Ioff against live host signals |
| `POWER_GROUND` | `sd_host_buffer.GND` | `abstract:power-ground` | short logic return |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_host_buffer_bypass.END_1` | one exact local 100-nF bypass per physical buffer |
| `POWER_GROUND` | `sd_host_buffer_bypass.END_2` | `abstract:power-ground` | local triple-buffer bypass return |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_miso_buffer.VCC` | return buffer powers down with the card and exposes an Ioff high-Z host output |
| `POWER_GROUND` | `sd_miso_buffer.GND` | `abstract:power-ground` | short return-buffer ground |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_miso_buffer_bypass.END_1` | separate exact 100-nF return-buffer bypass |
| `POWER_GROUND` | `sd_miso_buffer_bypass.END_2` | `abstract:power-ground` | local return-buffer bypass return |
| `POWER_GROUND` | `sd_host_sck_pulldown.END_2` | `abstract:power-ground` | 10-kOhm host-side default keeps shared SPI2 clock low across reset |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_host_d0_pullup.END_2` | 10-kOhm host default prevents a powered card buffer from seeing floating MOSI across S3 reset |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_host_d1_pullup.END_2` | 10-kOhm host default prevents the shared QSPI D1/MISO node from floating |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_host_cs_pullup.END_2` | 10-kOhm host default deselects the card and disables its return buffer before firmware |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `lcd_host_cs_pullup.END_2` | 10-kOhm host default keeps the display deselected during card SPI-mode admission |
| `SD_CLK_BUFFERED` | `sd_host_buffer.1Y` | `sd_sck_series.END_1` | first Ioff channel drives only the powered card branch |
| `SD_CLK_PROTECTED` | `sd_sck_series.END_2` | `sd.CLK` | exact 22-Ohm source series limits clock ringing at the removable socket |
| `SD_CLK_PROTECTED` | `sd_sck_series.END_2` | `sd_esd_a.D1_PLUS` | first low-capacitance IEC channel clamps the exposed clock contact |
| `SD_CMD_BUFFERED` | `sd_host_buffer.2Y` | `sd_cmd_series.END_1` | second Ioff channel drives CMD/MOSI only while card power is present |
| `SD_CMD_PROTECTED` | `sd_cmd_series.END_2` | `sd.CMD` | exact 22-Ohm source series limits CMD edge energy |
| `SD_CMD_PROTECTED` | `sd_cmd_series.END_2` | `sd_esd_a.D1_MINUS` | second low-capacitance IEC channel clamps the exposed CMD contact |
| `SD_CS_BUFFERED_N` | `sd_host_buffer.3Y` | `sd_cs_series.END_1` | third Ioff channel carries the reset-high card select |
| `SD_DAT3_CS_PROTECTED_N` | `sd_cs_series.END_2` | `sd.CD_DAT3` | exact 22-Ohm source series terminates the card-select branch |
| `SD_DAT3_CS_PROTECTED_N` | `sd_cs_series.END_2` | `sd_esd_a.D2_PLUS` | third IEC channel clamps the exposed DAT3/CS contact |
| `SD_DAT0_MISO_PROTECTED` | `sd.DAT0` | `sd_miso_buffer.A` | only the card's selected DAT0 return reaches the explicit tri-state buffer |
| `SD_DAT0_MISO_PROTECTED` | `sd.DAT0` | `sd_esd_a.D2_MINUS` | fourth IEC channel clamps the exposed DAT0 contact |
| `SD_MISO_BUFFERED` | `sd_miso_buffer.Y` | `sd_miso_series.END_1` | buffer output is high-Z whenever SD_CS_N is high or the card rail is absent |
| `DISPLAY_SD_SPI_D1` | `sd_miso_series.END_2` | `abstract:S3-GPIO4-shared-D1` | exact 22-Ohm source series bounds the return edge before the shared display D1 node |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_cmd_pullup.END_1` | switched-rail pull cannot back-power an off card |
| `SD_CMD_PROTECTED` | `sd_card_cmd_pullup.END_2` | `sd.CMD` | exact 10-kOhm CMD pull-up required for ESP32-S3 SD SPI mode |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_dat0_pullup.END_1` | switched-rail DAT0 pull-up |
| `SD_DAT0_MISO_PROTECTED` | `sd_card_dat0_pullup.END_2` | `sd.DAT0` | exact 10-kOhm DAT0 pull-up required for ESP32-S3 SD SPI mode |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_dat1_pullup.END_1` | unused card data pins still receive required switched-rail pulls |
| `SD_DAT1_PROTECTED` | `sd_card_dat1_pullup.END_2` | `sd.DAT1` | exact 10-kOhm DAT1 pull-up prevents an invalid card state |
| `SD_DAT1_PROTECTED` | `sd.DAT1` | `sd_esd_b.D1_PLUS` | fifth card-signal IEC channel clamps DAT1 |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_dat2_pullup.END_1` | unused card data pins still receive required switched-rail pulls |
| `SD_DAT2_PROTECTED` | `sd_card_dat2_pullup.END_2` | `sd.DAT2` | exact 10-kOhm DAT2 pull-up prevents an invalid card state |
| `SD_DAT2_PROTECTED` | `sd.DAT2` | `sd_esd_b.D1_MINUS` | sixth card-signal IEC channel clamps DAT2 |
| `SD_CARD_3V3` | `sd_power_switch.VOUT` | `sd_card_dat3_pullup.END_1` | switched DAT3 pull follows the SD SPI requirement without leaking into an off rail |
| `SD_DAT3_CS_PROTECTED_N` | `sd_card_dat3_pullup.END_2` | `sd.CD_DAT3` | exact 10-kOhm DAT3/CS pull-up keeps the card deselected during rail rise |
| `SD_CARD_3V3` | `sd.VDD` | `sd_esd_b.D2_PLUS` | seventh required ESD channel protects the exposed 2.6-to-3.3-V card supply contact |
| `POWER_GROUND` | `sd.VSS` | `abstract:power-ground` | short card return beside the socket |
| `SD_SHIELD_GROUND` | `sd.SHIELD` | `abstract:power-ground-multivia` | four shield tabs use a short multi-via ESD return outside the protected signal path |
| `SD_ESD_GROUND_A` | `sd_esd_a.GND_3` | `abstract:power-ground-dedicated-via` | first independent shortest-path IEC return |
| `SD_ESD_GROUND_A` | `sd_esd_a.GND_8` | `abstract:power-ground-dedicated-via` | both array ground contacts receive local vias |
| `SD_ESD_GROUND_B` | `sd_esd_b.GND_3` | `abstract:power-ground-dedicated-via` | second independent shortest-path IEC return |
| `SD_ESD_GROUND_B` | `sd_esd_b.GND_8` | `abstract:power-ground-dedicated-via` | both array ground contacts receive local vias |
| `SD_ESD_A_NC6` | `sd_esd_a.NC_6` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_A_NC7` | `sd_esd_a.NC_7` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_A_NC9` | `sd_esd_a.NC_9` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_A_NC10` | `sd_esd_a.NC_10` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_B_NC6` | `sd_esd_b.NC_6` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_B_NC7` | `sd_esd_b.NC_7` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_B_NC9` | `sd_esd_b.NC_9` | `abstract:no-connect` | manufacturer no-connect remains open |
| `SD_ESD_B_NC10` | `sd_esd_b.NC_10` | `abstract:no-connect` | manufacturer no-connect remains open |
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
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_io.VCC` | dedicated ordinary-control expander shares the protected SYS-I2C logic domain |
| `POWER_GROUND` | `ui_matrix_io.GND` | `abstract:power-ground` | short local digital return |
| `SYS_I2C_SDA` | `s3.GPIO1` | `ui_matrix_io.SDA` | bounded ordinary-control transactions share the internal bus but no encoder or PTT edge depends on them |
| `SYS_I2C_SCL` | `s3.GPIO2` | `ui_matrix_io.SCL` | candidate 400-kHz service; physical bus timing remains HIL |
| `SYS_INT_N` | `ui_matrix_io.INT_N` | `abstract:SYS_INT_N_WIRED_LOW` | open-drain interrupt asserts on any column change while every row is held low in idle |
| `UI_MATRIX_ADDR_A0_HIGH` | `abstract:3V3_MAIN` | `ui_matrix_io.A0` | candidate 7-bit address 0x3F; physical collision scan remains HIL |
| `UI_MATRIX_ADDR_A1_HIGH` | `abstract:3V3_MAIN` | `ui_matrix_io.A1` | candidate 7-bit address 0x3F; physical collision scan remains HIL |
| `UI_MATRIX_ADDR_A2_HIGH` | `abstract:3V3_MAIN` | `ui_matrix_io.A2` | candidate 7-bit address 0x3F; physical collision scan remains HIL |
| `UI_ROW0_N` | `ui_matrix_io.P0` | `abstract:UI_MATRIX_ROW0_UP_DOWN_LEFT` | 1-kOhm reset pull-down makes the row low before firmware; bounded scan may drive it high when unselected |
| `UI_ROW1_N` | `ui_matrix_io.P1` | `abstract:UI_MATRIX_ROW1_RIGHT_OK_BACK` | 1-kOhm reset pull-down makes the row low before firmware; bounded scan may drive it high when unselected |
| `UI_ROW2_N` | `ui_matrix_io.P2` | `abstract:UI_MATRIX_ROW2_OPT_F1_F2` | 1-kOhm reset pull-down makes the row low before firmware; bounded scan may drive it high when unselected |
| `UI_ROW3_N` | `ui_matrix_io.P3` | `abstract:UI_MATRIX_ROW3_ENCODER_PUSH` | 1-kOhm reset pull-down makes the encoder-push row low before firmware |
| `UI_COL0` | `ui_matrix_io.P4` | `abstract:UI_MATRIX_COL0_WITH_SWITCHES_AND_DIODES` | 10-kOhm pull-up and one 1N4148WT per populated control; ordinary UI only |
| `UI_COL1` | `ui_matrix_io.P5` | `abstract:UI_MATRIX_COL1_WITH_SWITCHES_AND_DIODES` | 10-kOhm pull-up and one 1N4148WT per populated control; ordinary UI only |
| `UI_COL2` | `ui_matrix_io.P6` | `abstract:UI_MATRIX_COL2_WITH_SWITCHES_AND_DIODES` | 10-kOhm pull-up and one 1N4148WT per populated control; ordinary UI only |
| `UI_MATRIX_P7_RESERVE` | `ui_matrix_io.P7` | `abstract:reserved-local-control-expansion-pad` | single local growth contact is reserved until all physical-control wishes close |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_io_bypass.END_1` | 100-nF local expander bypass |
| `POWER_GROUND` | `ui_matrix_io_bypass.END_2` | `abstract:power-ground` | short local bypass return |
| `UI_ROW0_N` | `ui_matrix_io.P0` | `ui_matrix_row0_pulldown.END_1` | exact 1-kOhm reset pull-down |
| `POWER_GROUND` | `ui_matrix_row0_pulldown.END_2` | `abstract:power-ground` | row is low while TCA9534A powers up as an input |
| `UI_ROW1_N` | `ui_matrix_io.P1` | `ui_matrix_row1_pulldown.END_1` | exact 1-kOhm reset pull-down |
| `POWER_GROUND` | `ui_matrix_row1_pulldown.END_2` | `abstract:power-ground` | row is low while TCA9534A powers up as an input |
| `UI_ROW2_N` | `ui_matrix_io.P2` | `ui_matrix_row2_pulldown.END_1` | exact 1-kOhm reset pull-down |
| `POWER_GROUND` | `ui_matrix_row2_pulldown.END_2` | `abstract:power-ground` | row is low while TCA9534A powers up as an input |
| `UI_ROW3_N` | `ui_matrix_io.P3` | `ui_matrix_row3_pulldown.END_1` | exact 1-kOhm reset pull-down |
| `POWER_GROUND` | `ui_matrix_row3_pulldown.END_2` | `abstract:power-ground` | row is low while TCA9534A powers up as an input |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_col0_pullup.END_1` | ordinary matrix column pull-up source |
| `UI_COL0` | `ui_matrix_col0_pullup.END_2` | `ui_matrix_io.P4` | 10-kOhm column pull-up |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_col1_pullup.END_1` | ordinary matrix column pull-up source |
| `UI_COL1` | `ui_matrix_col1_pullup.END_2` | `ui_matrix_io.P5` | 10-kOhm column pull-up |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `ui_matrix_col2_pullup.END_1` | ordinary matrix column pull-up source |
| `UI_COL2` | `ui_matrix_col2_pullup.END_2` | `ui_matrix_io.P6` | 10-kOhm column pull-up |
| `UI_ROW0_N` | `abstract:UI_MATRIX_ROW0_UP_DOWN_LEFT` | `ui_matrix_diode_up.K` | one exact diode isolates D-pad UP from other rows |
| `UI_UP_ROW_SIDE` | `ui_matrix_diode_up.A` | `abstract:UI_SWITCH_UP_ROW_CONTACT` | ordinary normally-open D-pad UP mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL0` | `abstract:UI_SWITCH_UP_COL_CONTACT` | `ui_matrix_io.P4` | D-pad UP occupies row 0, column 0 |
| `UI_ROW0_N` | `abstract:UI_MATRIX_ROW0_UP_DOWN_LEFT` | `ui_matrix_diode_down.K` | one exact diode isolates D-pad DOWN from other rows |
| `UI_DOWN_ROW_SIDE` | `ui_matrix_diode_down.A` | `abstract:UI_SWITCH_DOWN_ROW_CONTACT` | ordinary normally-open D-pad DOWN mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL1` | `abstract:UI_SWITCH_DOWN_COL_CONTACT` | `ui_matrix_io.P5` | D-pad DOWN occupies row 0, column 1 |
| `UI_ROW0_N` | `abstract:UI_MATRIX_ROW0_UP_DOWN_LEFT` | `ui_matrix_diode_left.K` | one exact diode isolates D-pad LEFT from other rows |
| `UI_LEFT_ROW_SIDE` | `ui_matrix_diode_left.A` | `abstract:UI_SWITCH_LEFT_ROW_CONTACT` | ordinary normally-open D-pad LEFT mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL2` | `abstract:UI_SWITCH_LEFT_COL_CONTACT` | `ui_matrix_io.P6` | D-pad LEFT occupies row 0, column 2 |
| `UI_ROW1_N` | `abstract:UI_MATRIX_ROW1_RIGHT_OK_BACK` | `ui_matrix_diode_right.K` | one exact diode isolates D-pad RIGHT from other rows |
| `UI_RIGHT_ROW_SIDE` | `ui_matrix_diode_right.A` | `abstract:UI_SWITCH_RIGHT_ROW_CONTACT` | ordinary normally-open D-pad RIGHT mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL0` | `abstract:UI_SWITCH_RIGHT_COL_CONTACT` | `ui_matrix_io.P4` | D-pad RIGHT occupies row 1, column 0 |
| `UI_ROW1_N` | `abstract:UI_MATRIX_ROW1_RIGHT_OK_BACK` | `ui_matrix_diode_ok.K` | one exact diode isolates D-pad OK from other rows |
| `UI_OK_ROW_SIDE` | `ui_matrix_diode_ok.A` | `abstract:UI_SWITCH_OK_ROW_CONTACT` | ordinary normally-open D-pad OK mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL1` | `abstract:UI_SWITCH_OK_COL_CONTACT` | `ui_matrix_io.P5` | D-pad OK occupies row 1, column 1 |
| `UI_ROW1_N` | `abstract:UI_MATRIX_ROW1_RIGHT_OK_BACK` | `ui_matrix_diode_back.K` | one exact diode isolates BACK from other rows |
| `UI_BACK_ROW_SIDE` | `ui_matrix_diode_back.A` | `abstract:UI_SWITCH_BACK_ROW_CONTACT` | ordinary normally-open BACK mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL2` | `abstract:UI_SWITCH_BACK_COL_CONTACT` | `ui_matrix_io.P6` | BACK occupies row 1, column 2 |
| `UI_ROW2_N` | `abstract:UI_MATRIX_ROW2_OPT_F1_F2` | `ui_matrix_diode_opt.K` | one exact diode isolates OPT from other rows |
| `UI_OPT_ROW_SIDE` | `ui_matrix_diode_opt.A` | `abstract:UI_SWITCH_OPT_ROW_CONTACT` | ordinary normally-open OPT mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL0` | `abstract:UI_SWITCH_OPT_COL_CONTACT` | `ui_matrix_io.P4` | OPT occupies row 2, column 0 |
| `UI_ROW2_N` | `abstract:UI_MATRIX_ROW2_OPT_F1_F2` | `ui_matrix_diode_f1.K` | one exact diode isolates F1 from other rows |
| `UI_F1_ROW_SIDE` | `ui_matrix_diode_f1.A` | `abstract:UI_SWITCH_F1_ROW_CONTACT` | ordinary normally-open F1 mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL1` | `abstract:UI_SWITCH_F1_COL_CONTACT` | `ui_matrix_io.P5` | F1 occupies row 2, column 1 |
| `UI_ROW2_N` | `abstract:UI_MATRIX_ROW2_OPT_F1_F2` | `ui_matrix_diode_f2.K` | one exact diode isolates F2 from other rows |
| `UI_F2_ROW_SIDE` | `ui_matrix_diode_f2.A` | `abstract:UI_SWITCH_F2_ROW_CONTACT` | ordinary normally-open F2 mechanics remain an I4 MPN/ergonomics gate |
| `UI_COL2` | `abstract:UI_SWITCH_F2_COL_CONTACT` | `ui_matrix_io.P6` | F2 occupies row 2, column 2 |
| `UI_ROW3_N` | `abstract:UI_MATRIX_ROW3_ENCODER_PUSH` | `ui_matrix_diode_encoder.K` | one exact diode isolates encoder push from other rows |
| `UI_ENCODER_PUSH_ROW` | `ui_matrix_diode_encoder.A` | `encoder.SW1` | integrated push switch is the tenth ordinary matrix control |
| `POWER_GROUND` | `encoder.C` | `abstract:power-ground` | quadrature common is a short local digital return |
| `UI_COL0` | `encoder.SW2` | `abstract:UI_MATRIX_COL0_WITH_SWITCHES_AND_DIODES` | encoder push occupies row 3, column 0 |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `encoder_a_pullup.END_1` | external phase pull-up keeps the direct PCNT input deterministic |
| `ENCODER_A` | `encoder_a_pullup.END_2` | `encoder.A` | exact 3.32-kOhm pull-up targets approximately 1 mA closed-contact current at 3.3 V; chatter and EMI remain HIL |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `encoder_b_pullup.END_1` | external phase pull-up keeps the direct PCNT input deterministic |
| `ENCODER_B` | `encoder_b_pullup.END_2` | `encoder.B` | exact 3.32-kOhm pull-up targets approximately 1 mA closed-contact current at 3.3 V; chatter and EMI remain HIL |
| `SYS_I2C_SCL` | `display_connector.PIN_1` | `display.TP_I2C_SCL` | logical contact 1 maps one-to-one; physical tail orientation remains specimen HIL |
| `SYS_I2C_SDA` | `display_connector.PIN_2` | `display.TP_I2C_SDA` | one existing exact 2.2-kOhm host pull-up pair serves the complete bus; no duplicate panel pull-ups |
| `LCD_TOUCH_INT_RAW` | `display_connector.PIN_3` | `display.TP_INT` | panel contact is kept separate from SYS_INT_N until specimen polarity/type is handled by the population option |
| `LCD_TOUCH_INT_RAW` | `display_connector.PIN_3` | `touch_irq_buffer.A` | first target is non-inverting open drain for active-low TP_INT; pin-compatible inverter is populated if specimen HIL proves active-high |
| `SYS_INT_N` | `touch_irq_buffer.Y` | `abstract:SYS_INT_N_WIRED_LOW` | open-drain output joins the existing shared interrupt without consuming another GPIO |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `touch_irq_buffer.VCC` | Ioff-capable buffer is supplied from protected main logic |
| `POWER_GROUND` | `touch_irq_buffer.GND` | `abstract:power-ground` | short local digital return |
| `TOUCH_IRQ_BUFFER_NC` | `touch_irq_buffer.NC` | `abstract:no-connect` | SC70 pin 1 is intentionally unconnected |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `touch_irq_buffer_bypass.END_1` | 100-nF local buffer bypass |
| `POWER_GROUND` | `touch_irq_buffer_bypass.END_2` | `abstract:power-ground` | short local bypass return |
| `TOUCH_RST_N` | `slow_io.P07` | `display_connector.PIN_4` | TP_RESXP is held low by a physical pull-down and released only after display power is stable |
| `TOUCH_RST_N` | `display_connector.PIN_4` | `display.TP_RESET` | official ST77922 timing requires a reset pulse of at least 10 us and at least 100 ms after release before touch operation |
| `TOUCH_RST_N` | `display_connector.PIN_4` | `touch_reset_pulldown.END_1` | separate physical reset-default resistor remains effective while the slow-I/O output is high-impedance |
| `POWER_GROUND` | `touch_reset_pulldown.END_2` | `abstract:power-ground` | 10-kOhm exact pull-down makes touch reset assert by default |
| `POWER_GROUND` | `display_connector.PIN_5` | `display.GND_5` | first panel return contact |
| `POWER_GROUND` | `display_connector.PIN_5` | `abstract:power-ground` | short local return at the connector |
| `LCD_VDDI_3V3` | `abstract:3V3_MAIN` | `display_connector.PIN_6` | protected common main rail avoids back-power through live QSPI/I2C when a separate display switch would trip |
| `LCD_VDDI_3V3` | `display_connector.PIN_6` | `display.VDDI` | ST77922 VDDI accepts the protected 3.3-V rail |
| `LCD_VDD_3V3` | `abstract:3V3_MAIN` | `display_connector.PIN_7` | VDD and VDDI may be applied in either order; both are one protected source here |
| `LCD_VDD_3V3` | `display_connector.PIN_7` | `display.VDD` | ST77922 VDD accepts the protected 3.3-V rail |
| `LCD_LOGIC_3V3` | `abstract:3V3_MAIN` | `display_logic_bulk_cap.END_1` | exact 10-uF local bulk target at the connector |
| `POWER_GROUND` | `display_logic_bulk_cap.END_2` | `abstract:power-ground` | display logic bulk return stays local |
| `LCD_LOGIC_3V3` | `abstract:3V3_MAIN` | `display_logic_hf_cap.END_1` | exact 100-nF high-frequency bypass at the connector |
| `POWER_GROUND` | `display_logic_hf_cap.END_2` | `abstract:power-ground` | display logic high-frequency return stays local |
| `LCD_TE_NC` | `display_connector.PIN_8` | `display.TE` | tearing-effect output is not required by the bounded dirty-region renderer |
| `LCD_TE_NC` | `display_connector.PIN_8` | `abstract:no-connect` | board-side contact deliberately open; S3 GPIO43 remains service UART TX |
| `LCD_CS_N` | `display_connector.PIN_9` | `display.QSPI_CS` | dedicated panel chip select; CS-high high-Z remains shared-bus HIL |
| `DISPLAY_SD_SPI_D1` | `display_connector.PIN_10` | `display.QSPI_D1` | direct QSPI data lane; source-series/DNP tuning footprint is reserved but not populated before HIL |
| `DISPLAY_SD_SPI_SCK` | `display_connector.PIN_11` | `display.QSPI_CLK` | direct QSPI clock; source-series/DNP tuning footprint is reserved but not populated before HIL |
| `LCD_RD_NC` | `display_connector.PIN_12` | `display.RD_UNUSED` | RD is unused in the selected QSPI strap |
| `LCD_RD_NC` | `display_connector.PIN_12` | `abstract:no-connect` | board-side contact deliberately open |
| `DISPLAY_SD_SPI_D0` | `display_connector.PIN_13` | `display.QSPI_D0` | direct QSPI data lane; source-series/DNP tuning footprint is reserved but not populated before HIL |
| `LCD_NC_14` | `display_connector.PIN_14` | `display.NC_14` | manufacturer-declared no-connect remains open |
| `LCD_NC_14` | `display_connector.PIN_14` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_RST_N` | `slow_io.P06` | `display_connector.PIN_15` | RESX is held low by a physical pull-down and released only after the protected rail is stable |
| `LCD_RST_N` | `display_connector.PIN_15` | `display.RESET` | official ST77922 timing requires at least 10-us reset pulse and at least 120 ms before Sleep Out after release |
| `LCD_RST_N` | `display_connector.PIN_15` | `display_reset_pulldown.END_1` | separate physical reset-default resistor remains effective while the slow-I/O output is high-impedance |
| `POWER_GROUND` | `display_reset_pulldown.END_2` | `abstract:power-ground` | 10-kOhm exact pull-down makes display reset assert by default |
| `POWER_GROUND` | `display_connector.PIN_16` | `display.GND_16` | second panel return contact |
| `POWER_GROUND` | `display_connector.PIN_16` | `abstract:power-ground` | short local return at the connector |
| `LCD_QSPI_D2` | `display_connector.PIN_17` | `display.QSPI_D2` | direct fourth-lane QSPI contact |
| `LCD_QSPI_D3` | `display_connector.PIN_18` | `display.QSPI_D3` | direct fourth-lane QSPI contact |
| `LCD_DB2_LOW` | `display_connector.PIN_19` | `display.DB2_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB3_LOW` | `display_connector.PIN_20` | `display.DB3_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB4_LOW` | `display_connector.PIN_21` | `display.DB4_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB5_LOW` | `display_connector.PIN_22` | `display.DB5_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB6_LOW` | `display_connector.PIN_23` | `display.DB6_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB7_LOW` | `display_connector.PIN_24` | `display.DB7_STRAP` | unused parallel-data contact tied low for the selected QSPI interface |
| `LCD_DB2_LOW` | `display_connector.PIN_19` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB3_LOW` | `display_connector.PIN_20` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB4_LOW` | `display_connector.PIN_21` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB5_LOW` | `display_connector.PIN_22` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB6_LOW` | `display_connector.PIN_23` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_DB7_LOW` | `display_connector.PIN_24` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_NC_25` | `display_connector.PIN_25` | `display.NC_25` | manufacturer-declared no-connect remains open |
| `LCD_NC_26` | `display_connector.PIN_26` | `display.NC_26` | manufacturer-declared no-connect remains open |
| `LCD_NC_27` | `display_connector.PIN_27` | `display.NC_27` | manufacturer-declared no-connect remains open |
| `LCD_NC_28` | `display_connector.PIN_28` | `display.NC_28` | manufacturer-declared no-connect remains open |
| `LCD_NC_29` | `display_connector.PIN_29` | `display.NC_29` | manufacturer-declared no-connect remains open |
| `LCD_NC_30` | `display_connector.PIN_30` | `display.NC_30` | manufacturer-declared no-connect remains open |
| `LCD_NC_31` | `display_connector.PIN_31` | `display.NC_31` | manufacturer-declared no-connect remains open |
| `LCD_NC_32` | `display_connector.PIN_32` | `display.NC_32` | manufacturer-declared no-connect remains open |
| `LCD_NC_25` | `display_connector.PIN_25` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_26` | `display_connector.PIN_26` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_27` | `display_connector.PIN_27` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_28` | `display_connector.PIN_28` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_29` | `display_connector.PIN_29` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_30` | `display_connector.PIN_30` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_31` | `display_connector.PIN_31` | `abstract:no-connect` | board-side contact deliberately open |
| `LCD_NC_32` | `display_connector.PIN_32` | `abstract:no-connect` | board-side contact deliberately open |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `backlight_efuse.IN` | only the LEDA branch receives independent latch-off protection; panel logic remains on common protected power to prevent interface back-power |
| `LCD_BACKLIGHT_EFUSE_EN` | `abstract:3V3_MAIN` | `backlight_efuse.EN` | hardware-enabled whenever main power exists; firmware cannot auto-retry a latched LED fault |
| `POWER_GROUND` | `backlight_efuse.GND` | `abstract:power-ground` | short local WSON return |
| `POWER_GROUND` | `backlight_efuse.POWERPAD` | `abstract:power-ground` | PowerPAD is externally tied to ground as required |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `backlight_efuse_input_cap.END_1` | exact 100-nF local input bypass required by TI |
| `POWER_GROUND` | `backlight_efuse_input_cap.END_2` | `abstract:power-ground` | local high-frequency input return |
| `LCD_BACKLIGHT_ILIM` | `backlight_efuse.ILIM` | `backlight_efuse_ilim.END_1` | 133-kOhm exact resistor sets about 200-mA nominal latch threshold |
| `POWER_GROUND` | `backlight_efuse_ilim.END_2` | `abstract:power-ground` | TI table gives approximately 174-to-234-mA system threshold including 1% resistor corners |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `backlight_fault_pullup.END_1` | exact 10-kOhm pull-up makes the open-drain fault observable |
| `LCD_BACKLIGHT_FAULT_N` | `backlight_fault_pullup.END_2` | `backlight_efuse.FAULT_N` | fixture-visible only; no scarce S3 GPIO is consumed |
| `LCD_BACKLIGHT_FAULT_N` | `backlight_efuse.FAULT_N` | `abstract:TP_LCD_BACKLIGHT_FAULT_N` | latched-fault diagnostic test point |
| `LCD_LEDA_PROTECTED` | `backlight_efuse.OUT` | `display_connector.PIN_33` | reverse-blocking latch-off source protects the 120-mA reference backlight branch |
| `LCD_LEDA_PROTECTED` | `display_connector.PIN_33` | `display.LEDA` | exact panel anode contact |
| `LCD_LEDA_PROTECTED` | `backlight_efuse.OUT` | `backlight_efuse_output_bulk.END_1` | exact 10-uF local output bulk supports PWM current edges |
| `POWER_GROUND` | `backlight_efuse_output_bulk.END_2` | `abstract:power-ground` | backlight bulk return stays beside the connector and switch |
| `LCD_LEDA_PROTECTED` | `backlight_efuse.OUT` | `backlight_efuse_output_hf.END_1` | exact 100-nF high-frequency output bypass |
| `POWER_GROUND` | `backlight_efuse_output_hf.END_2` | `abstract:power-ground` | backlight high-frequency return stays local |
| `LCD_LEDK` | `display_connector.PIN_34` | `display.LEDK_1` | first cathode contact shares the qualified low-side sink |
| `LCD_LEDK` | `display_connector.PIN_35` | `display.LEDK_2` | second cathode contact shares the qualified low-side sink |
| `LCD_LEDK` | `display_connector.PIN_36` | `display.LEDK_3` | third cathode contact shares the qualified low-side sink |
| `LCD_LEDK` | `display_connector.PIN_34` | `backlight_series_resistor.END_1` | all three cathodes join before the exact reference-equivalent 10-Ohm pulse-rated resistor |
| `LCD_LEDK` | `display_connector.PIN_35` | `backlight_series_resistor.END_1` | all three cathodes join before the exact reference-equivalent 10-Ohm pulse-rated resistor |
| `LCD_LEDK` | `display_connector.PIN_36` | `backlight_series_resistor.END_1` | all three cathodes join before the exact reference-equivalent 10-Ohm pulse-rated resistor |
| `LCD_LEDK_LIMITED` | `backlight_series_resistor.END_2` | `backlight_mosfet.D` | 0.66-W anti-surge resistor has wide margin over the approximately 0.144-W 120-mA reference load |
| `POWER_GROUND` | `backlight_mosfet.S` | `abstract:power-ground` | short low-side PWM return |
| `LCD_BACKLIGHT_GATE` | `backlight_gate_series.END_2` | `backlight_mosfet.G` | exact 100-Ohm gate resistor limits edge current and ringing |
| `LCD_BACKLIGHT_GATE` | `backlight_mosfet.G` | `backlight_gate_pulldown.END_1` | gate is forced low before S3 configures GPIO40 |
| `POWER_GROUND` | `backlight_gate_pulldown.END_2` | `abstract:power-ground` | exact 10-kOhm reset-off default |
| `POWER_GROUND` | `display_connector.PIN_37` | `display.GND_37` | third panel return contact |
| `POWER_GROUND` | `display_connector.PIN_37` | `abstract:power-ground` | short local return at the connector |
| `LCD_IM0_LOW` | `display_connector.PIN_38` | `display.IM0` | fixed QSPI interface strap |
| `LCD_IM0_LOW` | `display_connector.PIN_38` | `abstract:power-ground` | short fixed board-side QSPI strap |
| `LCD_IM1_HIGH` | `abstract:3V3_MAIN` | `display_connector.PIN_39` | fixed QSPI interface strap |
| `LCD_IM1_HIGH` | `display_connector.PIN_39` | `display.IM1` | fixed QSPI interface strap |
| `LCD_IM2_LOW` | `display_connector.PIN_40` | `display.IM2` | fixed QSPI interface strap |
| `LCD_IM2_LOW` | `display_connector.PIN_40` | `abstract:power-ground` | short fixed board-side QSPI strap |
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
| `SD_PWR_EN` | `slow_io.P20` | `sd_power_switch.ON` | ordinary session request only; exact external fail-low and switch protection remain effective across firmware reset |
| `SD_PWR_EN` | `sd_power_switch.ON` | `sd_on_pulldown.END_1` | separate exact 10-kOhm reset-off default supplements the switch smart pull-down |
| `POWER_GROUND` | `sd_on_pulldown.END_2` | `abstract:power-ground` | card, buffers and pull-ups remain off until an explicit storage session |
| `POWER_GROUND` | `sd.DETECT_B` | `abstract:power-ground` | normally-open detect pair closes to ground only with a fully inserted card |
| `SD_CARD_DETECT_RAW_N` | `sd.DETECT_A` | `sd_esd_b.D2_MINUS` | eighth available low-capacitance IEC channel protects the mechanical detect conductor |
| `SD_CARD_DETECT_RAW_N` | `sd.DETECT_A` | `sd_detect_series.END_1` | exact 1-kOhm series resistor limits residual surge and contact current into the slow expander |
| `SD_CARD_DETECT_N` | `sd_detect_series.END_2` | `slow_io.P21` | read-only active-low presence remains available while card power is off |
| `3V3_MAIN` | `abstract:3V3_MAIN` | `sd_detect_pullup.END_1` | presence sensing does not require or back-power SD_CARD_3V3 |
| `SD_CARD_DETECT_N` | `sd_detect_pullup.END_2` | `slow_io.P21` | exact 10-kOhm pull-up reports absent/open wiring as high |
| `SD_CARD_DETECT_N` | `slow_io.P21` | `sd_detect_cap.END_1` | exact 100-nF hardware filter suppresses the shortest contact chatter before software debounce |
| `POWER_GROUND` | `sd_detect_cap.END_2` | `abstract:power-ground` | local detect-filter return |
| `STOP_LATCH_SENSE` | `safe_latch.Q` | `slow_io.P22` | diagnostic mirror only; non-programmable hard-stop dominance never depends on the expander |
| `S3_RF_TX_EVIDENCE_N` | `evidence_cmp_a.OUT1` | `slow_io.P23` | direct read-only mirror of the exact S3 evidence comparator |
| `POWER_FAULT_N` | `abstract:power-current-thermal-fault` | `slow_io.P25` | hardware protection acts independently; this is diagnostic evidence |
| `ACCESSORY_PRESENT_N` | `abstract:accessory-present` | `slow_io.P26` | read-only, protected and debounced |
| `AON_SAFE_3V3` | `abstract:AON_SAFE_3V3` | `safe_supervisor.VDD` | always-on source and hold-up are selected and budgeted in I3 |
| `AON_SAFE_SENSE` | `abstract:AON_SAFE_3V3` | `safe_supervisor.SENSE` | factory G33 threshold supervises the actual safety rail |
| `AON_SAFE_3V3` | `abstract:AON_SAFE_3V3` | `safe_por_pullup.END_1` | one exact 10-kOhm resistor is the sole external pull-up on the supervisor's open-drain POR output |
| `POR_N` | `safe_por_pullup.END_2` | `safe_supervisor.RESET_N` | POR_N is pulled only to AON_SAFE_3V3; a missing AON rail cannot produce a main-enable high |
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
| `VOICE_DOMAIN_EN_SAFE` | `safe_gate_b.2Y` | `voice_buck.EN` | STOP and AON loss disable the independent fixed 4-V converter |
| `VOICE_DOMAIN_EN_SAFE` | `voice_buck.EN` | `voice_en_pulldown.END_1` | one exact 10-kOhm pull-down defines voice off even if the safety-gate output is high-impedance |
| `POWER_GROUND` | `voice_en_pulldown.END_2` | `abstract:power-ground` | external fail-low default is independent of converter internal bias |
| `VOICE_DOMAIN_EN_SAFE` | `safe_gate_b.2Y` | `voice_pg_base_res.END_1` | the qualifier consumes the same STOP-dominant voice enable evidence |
| `VOICE_PG_QUAL_BASE` | `voice_pg_base_res.END_2` | `voice_pg_qualifier.B` | exact 68-kOhm 1% base resistor limits drive while preserving the reviewed forced-beta margin |
| `IR_TX_CARRIER_SAFE` | `safe_gate_b.3Y` | `abstract:fail-safe-IR-LED-driver` | carrier waveform is physically blocked whenever RUN_PERMIT is low |
| `EXT_5V_EN_SAFE` | `safe_gate_b.4Y` | `ext_buck.EN` | STOP and AON loss disable the dedicated 5-V converter |
| `EXT_5V_EN_SAFE` | `ext_buck.EN` | `ext_en_pulldown.END_1` | one exact 10-kOhm pull-down defines accessory off for both converter and eFuse if the safety-gate output is high-impedance |
| `POWER_GROUND` | `ext_en_pulldown.END_2` | `abstract:power-ground` | external fail-low default is independent of the converter's internal 2-MOhm pull-down |
| `EXT_5V_EN_SAFE` | `safe_gate_b.4Y` | `ext_pg_base_res.END_1` | the qualifier consumes the same STOP-dominant accessory enable evidence |
| `EXT_PG_QUAL_BASE` | `ext_pg_base_res.END_2` | `ext_pg_qualifier.B` | exact 68-kOhm 1% base resistor limits drive while preserving the reviewed forced-beta margin |
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
| `EVIDENCE_ADDR_A0_LOW` | `abstract:safety-ground` | `evidence_mask.A0` | fixed 7-bit address 0x38 |
| `EVIDENCE_ADDR_A1_LOW` | `abstract:safety-ground` | `evidence_mask.A1` | fixed 7-bit address 0x38 |
| `EVIDENCE_ADDR_A2_LOW` | `abstract:safety-ground` | `evidence_mask.A2` | fixed 7-bit address 0x38 |

### Programming, recovery and diagnostics

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20`, `GPIO43`, `GPIO44` — native USB Serial/JTAG, permanent default UART0 RF-test/diagnostic route and physical EN/BOOT.
- `c5`: `EN`, `GPIO28`, `GPIO27`, `GPIO11`, `GPIO12`, `GPIO13`, `GPIO14` — native USB Serial/JTAG, permanent UART0, physical CHIP_PU/BOOT and normal-boot/log strap; 1-bit SDIO leaves USB contacts independent.
- `rp`: `RUN`, `SWCLK`, `SWDIO`, `USB_DM`, `USB_DP`, `QSPI_SS_USB_BOOT` — independent SWD, RUN, USB and BOOTSEL fixture access.
- `pd_controller`: `I2Ct_SDA`, `I2Ct_SCL`, `I2Ct_IRQ` — S3 shared SYS_I2C0 host control plus shared wired-low IRQ; same bus is exposed on protected service pads for controller status/recovery.
- `pd_config_eeprom`: `SDA`, `SCL`, `WP` — first image uses a preprogrammed loose EEPROM or a current-limited raw-VBUS fixture. The fixture observes TPS ReadyForPatch on I2Ct and verifies I2Cc high-Z before direct SDA/SCL/WP programming; it never drives LDO_3V3 externally and does not depend on S3.
- `pack_gauge`: `ALRT`, `SCL_OD`, `SDA_DQ`, `PFAIL` — direct protected I2C/NVM and hold/fault pads with fixture ground and qualified stack-sense supply; protected image checksum and OvrdEn readback are mandatory before energized cell installation.
- `pack_admission`: `PA1_NRST`, `PA17`, `PA18_A7`, `PA19_SWDIO`, `PA20_A6_SWCLK`, `VDD`, `VSS` — permanent NRST/SWD/UART plus isolated fixture VDD/VSS; fixture or admitted system rail powers flash programming because MAX17320 AOLDO is not sized for it.
- `voice`: `UPDATE`, `UART_TX`, `UART_RX`, `PD` — permanent fixture breakout for vendor update/recovery plus UART and hardware power-down; UPDATE drive remains inhibited until exact rev-1.1 direction/timing proof.

### Non-MCU contact accounting

| Instance | Used | Reserved | Free |
|---|---:|---:|---:|
| `slow_io` | 18 | 0 | 6 |
| `ui_matrix_io` | 7 | 1 | 0 |

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
| `S3_INTERNAL_I2C` | `s3` | `slow_io`, `ui_matrix_io`, `display touch`, `codec`, `receiver`, `pd_controller`, `pack_admission` | scheduled; bounded transactions; both expanders, PD, pack and touch interrupts only wake the service loop; UI initialization writes low output latches before P0..P3 become outputs, then holds all rows low in idle, scans one low row against three high rows, and restores idle; direct PCNT captures encoder phases independently | ordinary UI/control first visible response <=100 ms; PD/pack/fault status is read after shared IRQ, and no radio FIFO, encoder-edge or PTT deadline is placed here | complete physical address scan including candidate UI address 0x3F, ES8311 address/readback and power-off no-backfeed, touch IRQ polarity/reset, TCA9534A idle-row interrupt behavior, PD and pack target-interface recovery, wired-low IRQ source identification, shortest-pulse, 4x3 matrix and fault-latency HIL |
| `S3_ENCODER_PCNT` | `s3` | `encoder` | dedicated; PCNT0 owns GPIO39=A and GPIO47=B as dedicated inputs; the I2C matrix carries only encoder push and never phase edges | no lost or invented detents while display dirty-region, storage and the active signal group run at their qualified worst case | phase polarity, valid Gray transitions, full-detent semantics, contact chatter, fastest manual rotation, temperature, EMI and concurrent-load HIL |
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
- `encoder` uses `Alps Alpine EC11E18244AU` as `verified_first_target_mechanical_fit_hil_open`, not an accepted production choice.
- `encoder` lifecycle: `active_standard`.
- `touch_irq_buffer` uses `SN74LVC1G07DCKR` as `verified_first_target_touch_polarity_hil_open`, not an accepted production choice.
- `display` lifecycle: `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified`.
- `display_connector` uses `Hirose FH12-40S-0.5SH(55)` as `verified_first_fit_candidate`, not an accepted production choice.
- `display_connector` lifecycle: `active; exact HMX035CTFT-001 tail thickness, exposed-contact side, stiffener and insertion fit remain specimen HIL`.
- `sd_power_input_cap` lifecycle: `active_production`.
- `codec` lifecycle: `current manufacturer product brief revision 17.0 dated 2026-02; production sourcing and lot qualification remain open`.
- `audio_rx_mux` uses `Texas Instruments SN74LVC1G3157DBVR` as `verified_reference`, not an accepted production choice.
- `audio_capture_buffer` uses `Texas Instruments TLV9061IDBVR` as `reference_only`, not an accepted production choice.
- `audio_speaker_selector` uses `Texas Instruments TMUX1136DGSR` as `reference_only`, not an accepted production choice.
- `audio_tx_selector` uses `Texas Instruments TS5A63157DCKR` as `reference_only`, not an accepted production choice.
- `audio_safe_gate` uses `Texas Instruments SN74LVC2G08DCUR` as `reference_only`, not an accepted production choice.
- `speaker_amp` uses `Diodes Incorporated PAM8302AASCR` as `verified_reference`, not an accepted production choice.
- `product_usb_vpwr_cap` lifecycle: `active_production`.
- `pack_gauge` lifecycle: `recommended_for_new_designs`.
- `pack_holder` uses `Keystone Electronics 1048P` as `verified_mechanical_reference`, not an accepted production choice.
- `pack_cell0` uses `XTAR 18650 4000mAh` as `selected_qualification_target`, not an accepted production choice.
- `pack_cell0` lifecycle: `current_catalog`.
- `pack_cell1` uses `XTAR 18650 4000mAh` as `selected_qualification_target`, not an accepted production choice.
- `pack_cell1` lifecycle: `current_catalog`.
- `pack_diag_timer` lifecycle: `active_production`.
- `pack_diag_lockout_cap` lifecycle: `active_production`.
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
- HMX035CTFT-001 is the exact assembly marking disclosed by the QDtech reference schematic and is instantiated as a paper candidate, not a production-qualified orderable part; DEC-0084 closes exact paper power/reset/backlight and the first connector candidate, while exact drawing/FPC mechanics, lifecycle, real-tail mate and specimen HIL remain open
- DEC-0086 consumes the former free S3 GPIO47 together with GPIO39 for direct PCNT0 encoder phases, so S3 and RP retain no free GPIO, C5 retains one, and the 24-line slow plane has no reserve. New direct endpoints require an explicit remap and repeated review; exact ordinary/PTT/STOP/RE-ARM switch mechanics, touch polarity and control HIL remain open
- C5 1-bit SDIO has exclusive ownership of the S3 SD/MMC host and leaves C5 native USB GPIO13/14 independent. S3 and C5 each retain both native USB and permanent default UART service; 1-bit framed throughput, control priority and reset recovery remain HIL gates, with 4-bit plus explicit service isolation only as fallback
- display and microSD are the only scheduled high-rate pair on one SPI2 controller; DEC-0085 closes the exact isolated microSD paper endpoint with card-side Ioff buffers, CS-gated MISO, switched mandatory pulls, complete contact ESD and always-readable detect, but >=4.0 MB/s storage plus <=100 ms visible UI under card stalls remains a mandatory HIL gate
- PIO instruction memory, DMA arbitration latency and SRAM-bank contention remain executable firmware/HIL gates even though the state-machine/channel capacity arithmetic closes with explicit reserve
- DEC-0045 prohibits cross-group simultaneous signal operation but requires all three SG-N24 radios concurrently active in every independent PTX/PRX mix; DEC-0047 selects a qualified internal envelope; N24H-0001 L0 DIV-DIV is pre-HIL only and T1 TARGET must prove exact channel/power/sensitivity points
- SG-N24 3PTX is a real accepted load case, so the exact module choice and packet-rail design must prove simultaneous TX peak/average current, droop, thermal, coupling and STOP at the qualified power profile; a former RX-only hunt budget is insufficient
- DEC-0046 consumes RP GPIO15/GPIO23 and C5 GPIO4 for group-level power gates; exact load-switch/isolator MPNs, discharge, no-back-power sequencing and quiet-state EMI HIL remain open, leaving no free direct RP GPIO
- DEC-0054 instantiates ES8311, SN74LVC1G3157DBVR, TLV9061IDBVR, TMUX1136DGSR, TS5A63157DCKR, SN74LVC2G08DCUR and PAM8302AASCR as the prototype audio topology and assigns GPIO6 AUDIO_ARM; exact passive values, powered-off loading, codec power, common-mode/gain, pop/click, RF immunity and HIL remain open before schematic/BOM freeze
- DEC-0063 instantiates TPS25751DREFR, BQ25798RQMR, CAT24C512WI-GT3 and TVS2200DRVR as the sink-only 30-W USB-PD frontend; DEC-0066 adds MAX17320G20+T and MSPM0C1104SDGS20R as the fail-closed 2S manager pair; DEC-0067 disables in-device deep-cell recovery and instantiates the exact switching path. DEC-0068 adds independent fixed TPS629203/TPS564252 AON/3.3/4.0/5.0-V converters, exact Sunlord inductors and five TPS22919 quiet-state switches; DEC-0069 corrects the connector eFuse to latch-off TPS259470LRPWR; DEC-0070 adds two exact MMBT3904-7-F PG qualifiers; DEC-0071 adds eight exact eFuse passives, an immediately active 1.509-A limit, controlled startup and a bounded post-start 2-A transient; DEC-0072 adds 24 exact converter energy/configuration/feedback passives and fixed tolerance-screened outputs; DEC-0073 originally adds nine exact converter EN/PG/fault resistors and a direct hardware AON enable strap; DEC-0080 amends this to ten physical positions and exact SYS-to-AON, AON-PG/MR, SENSE/CT/POR and main-EN wiring without a programmable sequencer; DEC-0081 adds independent TPS25961DRVR AON cutoff plus two TPS25974LRPWR latch-off protected-PG circuit breakers, exact thresholds, rise/timer networks and single-fault paper containment after every internal buck; DEC-0074 establishes the 10-Ohm pre-admission function, <=50-ms hardware cutoff and corrected PA25/PA26 frontends; DEC-0075 adds the exact BQ25798 750-kHz/2.2-uH energy, TS/ILIM, reset and special-pin profile; DEC-0076 adds the exact TPS25751/CAT24 support circuit, hardware SafeMode, separate raw-VBUS startup path and complete local/host bus pulls; DEC-0077 adds exact polarized Keystone 1048P contacts and three physical NTC roles; DEC-0078 corrects the TPUL WQFN contact map, adds a >=350-ms second-channel hardware refractory lockout and splits the 10-Ohm load across two exact 20-Ohm/2-W branches; DEC-0079 selects two XTAR 18650 4000mAh protected button-top cells as the exact first qualification target and freezes a 2-A charge ceiling. Exact-cell droop thresholds, certification-document/specimen fit, continuity/thermal/hot-copper/source-handover and full injected-fault HIL remain open in I3. DEC-0083 closes the first I4 paper endpoint with exact DX07S016JA1R1500, TPD4S201RUKR, protected USB2/CC routes, exact 22-Ohm S3 terminations, reserved DNP tuning footprints and recalculated 220-pF CC shunts. DEC-0084 closes the second I4 paper endpoint with exact first display ZIF candidate, protected-main logic decoupling, reset-low defaults and a latch-protected PWM backlight. DEC-0085 closes the third I4 paper endpoint with exact DM3AT-SF-PEJM5, switched TPS22919 rail, Ioff card-side isolation, CS-gated DAT0 return, mandatory switched pulls, complete contact/detect ESD and safe shared-bus sequencing; connector placement/mate, USB/display/storage signal integrity and destructive/thermal HIL remain explicit
- HMX035CTFT-001 exact contacts and its DEC-0084 power/reset/backlight/first-mate paper circuit plus DM3AT-SF-PEJM5 and its DEC-0085 isolated storage paper circuit are instantiated, but display/storage production qualification, physical integration and electrical HIL remain open; the I2 hard-stop/evidence active circuit is paper-reviewed while detector taps/thresholds are I6; exact IR frontends and antenna placement remain open; SA518/Si4732 contact maps are instantiated, while SA518 UPDATE electrical direction/timing and both modules' surrounding power/audio/RF circuits remain specimen/electrical/HIL gates before target-architecture acceptance

## Machine-check result and review boundary

All source candidates pass structural validation. This proves that their listed programmable GPIO exist on the exact compute packages/modules and are fully accounted without collisions. Where declared, non-MCU contacts, interface resource contracts, controller GPIO-window selections, fixed-mux contact contracts, capacity arithmetic, signal-group declarations and quiet-state contract coverage are also complete. It does **not** close electrical feasibility: abstract peers, reference-only modules, RF networks, quiet-state circuitry, timing/EMI HIL, power and physical integration remain open. Therefore no candidate receives «Проведено ревью» as a complete target architecture in this generated artifact.
