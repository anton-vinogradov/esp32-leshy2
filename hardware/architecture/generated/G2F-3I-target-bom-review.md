# G2F-3I — generated target BOM coverage review

- Статус: **I8 paper procurement-feasibility scope reviewed; downstream G3/G8 qualification gated**
- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/G2F-3I.json`
- Regenerate: `python3 hardware/architecture/generate.py --write`

> Файл сгенерирован. Он показывает полноту входа в I8, а не выдаёт незакрытые строки за factory quote.

## Что уже посчитано

- **1053** architecture instances include **1** explicit assembly-internal evidence node.
- After excluding those non-purchase nodes, **1052** supplied/costed placements collapse to **210** used exact-device/MPN lines.
- Current orderability evidence exists for **210/210** used lines; **0** need a current source check.
- Machine-readable quantity-100 cost evidence exists for **201/210** lines.
- Of the remaining **9** unpriced lines, **9** have an explicit RFQ/retail comparability gate instead of a fabricated numeric value.
- Those priced lines cover **1038/1052** supplied placements; their partial subtotals are `base_product` — USD 252.3390. These are coverage diagnostics, not product COGS.
- Machine-readable alternate/no-substitution evidence exists for **210/210** lines.
- Cost basis: USD quantity 100 component material only; PCB, assembly, test, enclosure, tax, freight, yield and tooling stay separate until factory RFQ.

Scopes: `base_product` — 1049 placements; `optional_external_accessory` — 1 placements; `regional_replaceable_cell_kit` — 2 placements.

The complete per-line manifest is the adjacent `G2F-3I-target-bom.csv`; unused comparison-device definitions are deliberately excluded.

## Substitution/no-silent-replacement policy

Every purchase line below belongs to exactly one validated class. A class is a disposition and requalification envelope, not a claim that a second MPN is already qualified.

<details><summary><code>SUB-RF</code> — RF, clock and frequency-selective parts — 29 line(s)</summary>

- Disposition: no drop-in substitution; exact part remains first target until full RF/clock requalification.
- Equivalence envelope:
  - same footprint/contact map and temperature range.
  - frequency, tolerance, Q, SRF, insertion/return loss, coupling/directivity and parasitics no worse over every used band.
  - ESD capacitance/clamp and crystal ESR/load/drive limits no worse.
- Required requalification:
  - schematic and vendor model review.
  - VNA or clock-startup/margin measurements as applicable.
  - conducted/OTA sensitivity, power, harmonics, detector threshold and coexistence HIL for every affected signal group.
- Current lines:
  - `abracon_abm8_26mhz_10_d_1_g_t` — `Abracon ABM8-26.000MHZ-10-D-1-G-T`.
  - `abracon_abm8_272_t3` — `Abracon ABM8-272-T3`.
  - `epson_q13fc13500005` — `Seiko Epson Q13FC13500005`.
  - `kyocera_avx_cp0603q5425entr` — `KYOCERA AVX CP0603Q5425ENTR`.
  - `littelfuse_sesd0402x1un_0020_090` — `Littelfuse SESD0402X1UN-0020-090`.
  - `murata_gjm1555c1h100jb01d` — `Murata GJM1555C1H100JB01D`.
  - `murata_gjm1555c1h101jb01d` — `Murata GJM1555C1H101JB01D`.
  - `murata_gjm1555c1h150jb01d` — `Murata GJM1555C1H150JB01D`.
  - `murata_gjm1555c1h1r2bb01d` — `Murata GJM1555C1H1R2BB01D`.
  - `murata_gjm1555c1h6r2db01d` — `Murata GJM1555C1H6R2DB01D`.
  - `murata_gjm1555c1h8r0db01d` — `Murata GJM1555C1H8R0DB01D`.
  - `murata_gjm1555c1hr47bb01d` — `Murata GJM1555C1HR47BB01D`.
  - `murata_gjm1555c1hr60bb01d` — `Murata GJM1555C1HR60BB01D`.
  - `murata_grm1555c1h102ja01d` — `Murata GRM1555C1H102JA01D`.
  - `murata_grm1555c1h220ja01d` — `Murata GRM1555C1H220JA01D`.
  - `murata_grm1555c1h390ja01d` — `Murata GRM1555C1H390JA01D`.
  - `murata_lqg15hs10nj02d` — `Murata LQG15HS10NJ02D`.
  - `murata_lqg15hs15nj02d` — `Murata LQG15HS15NJ02D`.
  - `murata_lqg15hs2n2s02d` — `Murata LQG15HS2N2S02D`.
  - `murata_lqg15hs3n3s02d` — `Murata LQG15HS3N3S02D`.
  - `murata_lqg15hs3n6s02d` — `Murata LQG15HS3N6S02D`.
  - `murata_lqg15hs6n8j02d` — `Murata LQG15HS6N8J02D`.
  - `murata_lqw15an56ng00d` — `Murata LQW15AN56NG00D`.
  - `nexperia_pesd24vy1bsf` — `Nexperia PESD24VY1BSF`.
  - `ttm_b0310j50100ahf` — `TTM Technologies B0310J50100AHF`.
  - `ttm_dc2337j5010ahf` — `TTM Technologies DC2337J5010AHF`.
  - `yageo_rc0402fr_0749r9l` — `Yageo RC0402FR-0749R9L`.
  - `yageo_rc0402fr_0752r3l` — `Yageo RC0402FR-0752R3L`.
  - `yageo_rc0402fr_0756kl` — `Yageo RC0402FR-0756KL`.

</details>

<details><summary><code>SUB-PWR-PASSIVE</code> — Power conversion, decoupling and energy-storage passives — 18 line(s)</summary>

- Disposition: controlled alternate only after converter/rail stability, loss and thermal requalification.
- Equivalence envelope:
  - same land pattern and height envelope.
  - capacitance after DC bias, voltage, dielectric, ESR, ripple and temperature no worse.
  - inductance, saturation/current, DCR, shielding, core loss and impedance curve no worse.
- Required requalification:
  - loop/stability and transient calculation.
  - startup/load-step/short/brownout/ripple/thermal HIL on every affected rail.
  - EMI and RF-noise regression with the active signal group.
- Current lines:
  - `abracon_aota_b201610s3r3_101_t` — `Abracon AOTA-B201610S3R3-101-T`.
  - `murata_blm18pg181sn1d` — `Murata BLM18PG181SN1D`.
  - `murata_grm188r60j106me47d` — `Murata GRM188R60J106ME47D`.
  - `murata_grm188r71e474ka12d` — `Murata GRM188R71E474KA12D`.
  - `murata_grm188z71a475me15d` — `Murata GRM188Z71A475ME15D`.
  - `murata_grm21br60j226me39l` — `Murata GRM21BR60J226ME39L`.
  - `murata_grm21br71e225ke11l` — `Murata GRM21BR71E225KE11L`.
  - `murata_grm31cr71a226ke15l` — `Murata GRM31CR71A226KE15L`.
  - `murata_grm31cr71e106ma12l` — `Murata GRM31CR71E106MA12L`.
  - `murata_grm32er71e226ke15l` — `Murata GRM32ER71E226KE15L`.
  - `sunlord_mwsa0503s_2r2mt` — `Sunlord MWSA0503S-2R2MT`.
  - `sunlord_mwsa0503s_3r3mt` — `Sunlord MWSA0503S-3R3MT`.
  - `sunlord_mwsa0503s_4r7mt` — `Sunlord MWSA0503S-4R7MT`.
  - `sunlord_wpn201612h2r2mt` — `Sunlord WPN201612H2R2MT`.
  - `tdk_c1005x5r0j475k050bc` — `TDK C1005X5R0J475K050BC`.
  - `tdk_cga5l1x7r1e475k160ac` — `TDK CGA5L1X7R1E475K160AC`.
  - `yageo_cc0402krx7r9bb104` — `Yageo CC0402KRX7R9BB104`.
  - `yageo_cc0603krx7r0bb104` — `Yageo CC0603KRX7R0BB104`.

</details>

<details><summary><code>SUB-CTRL-PASSIVE</code> — Control, timing, precision, protection-current and sensing passives — 60 line(s)</summary>

- Disposition: controlled parametric substitution; no value-family or tolerance relaxation without owning-subblock review.
- Equivalence envelope:
  - same nominal value and footprint unless the owning calculation is redone.
  - tolerance, tempco, voltage, power, pulse/surge, dielectric, leakage and temperature no worse for every placement sharing the line.
  - fuse curve, shunt Kelvin behavior and NTC beta/thermal coupling remain equivalent where applicable.
- Required requalification:
  - recompute every threshold, timer, gain, divider, current and dissipation using the worst placement.
  - fault/startup/thermal/timing HIL for safety or power roles.
  - USB/audio/IR/signal-integrity check for series, coupling and filter roles.
- Current lines:
  - `bourns_crm2512_fx_20r0elf` — `Bourns CRM2512-FX-20R0ELF`.
  - `fh_rs_06k47r0ft` — `FH RS-06K47R0FT`.
  - `kemet_c0402c102k5ractu` — `KEMET C0402C102K5RACTU`.
  - `kemet_c0402c330j5gactu` — `KEMET C0402C330J5GACTU`.
  - `littelfuse_0451005_mrl` — `Littelfuse 0451005.MRL`.
  - `murata_grm1555c1h121ja01d` — `Murata GRM1555C1H121JA01D`.
  - `murata_grm1555c1h221ja01d` — `Murata GRM1555C1H221JA01D`.
  - `murata_grm155r71a474ke01d` — `Murata GRM155R71A474KE01D`.
  - `murata_grm155r71e473ka88d` — `Murata GRM155R71E473KA88D`.
  - `murata_grm155r71h103ka88d` — `Murata GRM155R71H103KA88D`.
  - `murata_grm155r71h472ka01d` — `Murata GRM155R71H472KA01D`.
  - `murata_grm188r71e224ka88d` — `Murata GRM188R71E224KA88D`.
  - `murata_grm31c5c1h224je02l` — `Murata GRM31C5C1H224JE02L`.
  - `panasonic_erj_2rkf22r0x` — `Panasonic ERJ-2RKF22R0X`.
  - `panasonic_erj_2rkf27r0x` — `Panasonic ERJ-2RKF27R0X`.
  - `panasonic_erj_p08f10r0v` — `Panasonic ERJ-P08F10R0V`.
  - `panasonic_erj_p08f49r9v` — `Panasonic ERJ-P08F49R9V`.
  - `tdk_b57332v5103f360` — `TDK B57332V5103F360`.
  - `tdk_c1608x7r1c105k080ac` — `TDK C1608X7R1C105K080AC`.
  - `uniroyal_0402wgf1333tce` — `UNI-ROYAL 0402WGF1333TCE`.
  - `uniroyal_0402wgf1603tce` — `UNI-ROYAL 0402WGF1603TCE`.
  - `uniroyal_0402wgf1651tce` — `UNI-ROYAL 0402WGF1651TCE`.
  - `uniroyal_0402wgf2201tce` — `UNI-ROYAL 0402WGF2201TCE`.
  - `uniroyal_0402wgf2703tce` — `UNI-ROYAL 0402WGF2703TCE`.
  - `uniroyal_0402wgf5231tce` — `UNI-ROYAL 0402WGF5231TCE`.
  - `uniroyal_0402wgf8201tce` — `UNI-ROYAL 0402WGF8201TCE`.
  - `vishay_tnpw040210k0beed` — `Vishay TNPW040210K0BEED`.
  - `vishay_tnpw040243k7beed` — `Vishay TNPW040243K7BEED`.
  - `vishay_wsl25125l000fea` — `Vishay WSL25125L000FEA`.
  - `yageo_rc0402fr_07100kl` — `Yageo RC0402FR-07100KL`.
  - `yageo_rc0402fr_07100rl` — `Yageo RC0402FR-07100RL`.
  - `yageo_rc0402fr_0710kl` — `Yageo RC0402FR-0710KL`.
  - `yageo_rc0402fr_07110kl` — `Yageo RC0402FR-07110KL`.
  - `yageo_rc0402fr_0712kl` — `Yageo RC0402FR-0712KL`.
  - `yageo_rc0402fr_07169kl` — `Yageo RC0402FR-07169KL`.
  - `yageo_rc0402fr_07196kl` — `Yageo RC0402FR-07196KL`.
  - `yageo_rc0402fr_071k82l` — `Yageo RC0402FR-071K82L`.
  - `yageo_rc0402fr_071kl` — `Yageo RC0402FR-071KL`.
  - `yageo_rc0402fr_071ml` — `Yageo RC0402FR-071ML`.
  - `yageo_rc0402fr_07220kl` — `Yageo RC0402FR-07220KL`.
  - `yageo_rc0402fr_07220rl` — `Yageo RC0402FR-07220RL`.
  - `yageo_rc0402fr_07240kl` — `Yageo RC0402FR-07240KL`.
  - `yageo_rc0402fr_0730k1l` — `Yageo RC0402FR-0730K1L`.
  - `yageo_rc0402fr_0730kl` — `Yageo RC0402FR-0730KL`.
  - `yageo_rc0402fr_0733kl` — `Yageo RC0402FR-0733KL`.
  - `yageo_rc0402fr_0733rl` — `Yageo RC0402FR-0733RL`.
  - `yageo_rc0402fr_073k32l` — `Yageo RC0402FR-073K32L`.
  - `yageo_rc0402fr_0742k2l` — `Yageo RC0402FR-0742K2L`.
  - `yageo_rc0402fr_0744k2l` — `Yageo RC0402FR-0744K2L`.
  - `yageo_rc0402fr_0745k3l` — `Yageo RC0402FR-0745K3L`.
  - `yageo_rc0402fr_07470rl` — `Yageo RC0402FR-07470RL`.
  - `yageo_rc0402fr_0747kl` — `Yageo RC0402FR-0747KL`.
  - `yageo_rc0402fr_074k7l` — `Yageo RC0402FR-074K7L`.
  - `yageo_rc0402fr_075k1l` — `Yageo RC0402FR-075K1L`.
  - `yageo_rc0402fr_07620kl` — `Yageo RC0402FR-07620KL`.
  - `yageo_rc0402fr_0768kl` — `Yageo RC0402FR-0768KL`.
  - `yageo_rc0402jr_070rl` — `Yageo RC0402JR-070RL`.
  - `yageo_rc0603fr_071kl` — `Yageo RC0603FR-071KL`.
  - `yageo_rt0402brd07100kl` — `Yageo RT0402BRD07100KL`.
  - `yageo_rt0402brd07191kl` — `Yageo RT0402BRD07191KL`.

</details>

<details><summary><code>SUB-DISCRETE-PROT</code> — Discrete switching, indication and signal-protection semiconductors — 12 line(s)</summary>

- Disposition: no automatic drop-in; a proposed alternate must pass pin/polarity, off-state and fault-boundary review.
- Equivalence envelope:
  - same package, pinout, polarity and assembly orientation.
  - voltage/current/power, leakage, capacitance, clamp, Vf, Rds(on), gain, thresholds and Ioff behavior no worse at real rails/temperature.
  - indicator wavelength/intensity and safety visibility remain equivalent.
- Required requalification:
  - reset/off/back-power and injected-fault HIL.
  - USB/ESD/signal-integrity or switching-loss/thermal HIL according to role.
  - visual status acceptance for LED substitutions.
- Current lines:
  - `diodes_2n7002dw_7_f` — `Diodes Incorporated 2N7002DW-7-F`.
  - `diodes_bat54_7_f` — `Diodes Incorporated BAT54-7-F`.
  - `diodes_dmn2056u_7` — `Diodes Incorporated DMN2056U-7`.
  - `diodes_mmbt3904_7_f` — `Diodes Incorporated MMBT3904-7-F`.
  - `liteon_ltst_c190kfkt` — `LTST-C190KFKT`.
  - `liteon_ltst_c190krkt` — `LTST-C190KRKT`.
  - `onsemi_bat54alt1g` — `BAT54ALT1G`.
  - `onsemi_bav70lt1g` — `onsemi BAV70LT1G`.
  - `ti_tpd2eusb30a_drtr` — `Texas Instruments TPD2EUSB30ADRTR`.
  - `ti_tpd4e05u06_dqar` — `Texas Instruments TPD4E05U06DQAR`.
  - `ti_tpd4s201_rukr` — `Texas Instruments TPD4S201RUKR`.
  - `ti_tpd8e003_dqdr` — `Texas Instruments TPD8E003DQDR`.

</details>

<details><summary><code>SUB-LOGIC-ANALOG</code> — Logic, interface, audio and analog signal ICs — 31 line(s)</summary>

- Disposition: no drop-in by family name; exact pin/function/electrical equivalent requires owning-interface requalification.
- Equivalence envelope:
  - same package/contact map, truth table, enable/reset defaults and active polarity.
  - rail range, thresholds, drive, leakage, Ioff/power-off protection, bandwidth, Ron, distortion, noise and timing no worse.
  - address, bus semantics, clocking and fault behavior remain compatible.
- Required requalification:
  - datasheet/errata and pin-by-pin review.
  - power-sequence/back-power/reset/bus-contention HIL.
  - audio, analog threshold or latency/no-stall HIL for every affected path.
- Current lines:
  - `diodes_pam8302a_aycr` — `Diodes Incorporated PAM8302AAYCR`.
  - `everest_es8311_qfn20` — `Everest Semiconductor ES8311`.
  - `nexperia_74lvc126apw_118` — `Nexperia 74LVC126APW,118`.
  - `nexperia_74lvc1g32gv_125` — `74LVC1G32GV,125`.
  - `nexperia_74lvc2g126dp_125` — `Nexperia 74LVC2G126DP,125`.
  - `nexperia_74lvc2g14gv_125` — `74LVC2G14GV,125`.
  - `onsemi_fsusb42_mux` — `onsemi FSUSB42MUX`.
  - `tca4307dgkr` — `TCA4307DGKR`.
  - `tca6424argjr` — `TCA6424ARGJR`.
  - `ti_sn74lvc08a_pwr` — `SN74LVC08APWR`.
  - `ti_sn74lvc1g06_dckr` — `Texas Instruments SN74LVC1G06DCKR`.
  - `ti_sn74lvc1g07_dckr` — `SN74LVC1G07DCKR`.
  - `ti_sn74lvc1g08_dckr` — `SN74LVC1G08DCKR`.
  - `ti_sn74lvc1g125_dckr` — `Texas Instruments SN74LVC1G125DCKR`.
  - `ti_sn74lvc1g126_dckr` — `Texas Instruments SN74LVC1G126DCKR`.
  - `ti_sn74lvc1g17_dckr` — `SN74LVC1G17DCKR`.
  - `ti_sn74lvc1g3157_dbvr` — `Texas Instruments SN74LVC1G3157DBVR`.
  - `ti_sn74lvc1g74_dcur` — `SN74LVC1G74DCUR`.
  - `ti_sn74lvc2g08_dcur` — `Texas Instruments SN74LVC2G08DCUR`.
  - `ti_sn74lvc2g66_dcur` — `Texas Instruments SN74LVC2G66DCUR`.
  - `ti_sn74lvc3g07_dcur` — `SN74LVC3G07DCUR`.
  - `ti_sn74lvc3g34_dcur` — `SN74LVC3G34DCUR`.
  - `ti_tca9534a_pwr` — `TCA9534APWR`.
  - `ti_tca9535_pwr` — `TCA9535PWR`.
  - `ti_tca9539_pwr` — `TCA9539PWR`.
  - `ti_tlv1821_dckr` — `TLV1821DCKR`.
  - `ti_tlv1824_pwr` — `TLV1824PWR`.
  - `ti_tlv9061_idbvr` — `TLV9061IDBVR`.
  - `ti_tmux1136_dgsr` — `Texas Instruments TMUX1136DGSR`.
  - `ti_ts5a63157_dckr` — `Texas Instruments TS5A63157DCKR`.
  - `ti_txs0102_dcur` — `Texas Instruments TXS0102DCUR`.

</details>

<details><summary><code>SUB-PWR-SAFETY</code> — Power, charging, admission and safety-control ICs — 18 line(s)</summary>

- Disposition: architecture-locked first target; substitute only by reopening and requalifying the complete safety/power subblock.
- Equivalence envelope:
  - same package/contact map and autonomous reset/fail-safe state.
  - limits, accuracy, protection coverage, gate drive, current/thermal capability, quiescent current, telemetry and fault latching no worse.
  - configuration memory/firmware image and independent recovery remain supported.
- Required requalification:
  - complete source-backed paper safety analysis and worst-case power calculations.
  - startup/source-transition/load-step/short/thermal/brownout/recovery HIL on the one prototype inside exact MPN limits.
  - safe single-fault injection through emulator, current-limited electrical/cell simulator and NTC fixtures; irreversible locks, real-cell abuse and hardware damage are forbidden.
- Current lines:
  - `adi_max17320_g20_t` — `Analog Devices MAX17320G20+T`.
  - `onsemi_cat24c512wi_gt3` — `onsemi CAT24C512WI-GT3`.
  - `ti_bq25798_rqmr` — `Texas Instruments BQ25798RQMR`.
  - `ti_csd87313dms` — `Texas Instruments CSD87313DMS`.
  - `ti_mspm0c1106_sdgs20r` — `Texas Instruments MSPM0C1106SDGS20R`.
  - `ti_tps22919_dckr` — `Texas Instruments TPS22919DCKR`.
  - `ti_tps2553drvr_1` — `Texas Instruments TPS2553DRVR-1`.
  - `ti_tps25751d_refr` — `Texas Instruments TPS25751DREFR`.
  - `ti_tps259470l_rpwr` — `Texas Instruments TPS259470LRPWR`.
  - `ti_tps25961_drvr` — `Texas Instruments TPS25961DRVR`.
  - `ti_tps25974l_rpwr` — `Texas Instruments TPS25974LRPWR`.
  - `ti_tps3435cakagddfr` — `Texas Instruments TPS3435CAKAGDDFR`.
  - `ti_tps3808g33_dbvr` — `TPS3808G33DBVR`.
  - `ti_tps3839k33_dbzr` — `Texas Instruments TPS3839K33DBZR`.
  - `ti_tps564252_drlr` — `Texas Instruments TPS564252DRLR`.
  - `ti_tps629203_drlr` — `Texas Instruments TPS629203DRLR`.
  - `ti_tpul2g223_bqbr` — `Texas Instruments TPUL2G223BQBR`.
  - `ti_tvs2200_drvr` — `Texas Instruments TVS2200DRVR`.

</details>

<details><summary><code>SUB-COMPUTE-RF</code> — Compute, radio modules and active RF/IR endpoints — 16 line(s)</summary>

- Disposition: architecture-locked first target; no drop-in substitution without full owner, pin, firmware, RF and recovery requalification.
- Equivalence envelope:
  - same exposed real-device contacts, package/mechanics, memory/resources and independent programming/recovery.
  - all accepted bands, modes, full nRF concurrency, timing, sensitivity, power, evidence and quiet-state controls preserved.
  - regulatory/profile and toolchain support no worse.
- Required requalification:
  - zero-based pin/resource/owner and firmware contract review.
  - programming/recovery/diagnostic and inter-domain IPC HIL.
  - conducted/OTA/optical/audio/coexistence/no-stall qualification for every affected group.
- Current lines:
  - `adi_ad8314acpz_rl7` — `Analog Devices AD8314ACPZ-RL7`.
  - `adi_ltc5532_es6_trmpbf` — `LTC5532ES6#TRMPBF`.
  - `cc1101rgpr` — `CC1101RGPR`.
  - `ebyte_e01_ml01sp4` — `Ebyte E01-ML01SP4`.
  - `esp32_c5_wroom_1u_n8r8` — `ESP32-C5-WROOM-1U-N8R8`.
  - `esp32_s3_wroom_1u_n16r8` — `ESP32-S3-WROOM-1U-N16R8`.
  - `infineon_bgs13sn8e6327xtsa1` — `Infineon BGS13SN8E6327XTSA1`.
  - `m5_u214` — `M5Stack U214 Cap LoRa-1262`.
  - `nicerf_sa818s_u_v18` — `G-NiceRF SA818S-U`.
  - `nicerf_sa818s_v_v18` — `G-NiceRF SA818S-V`.
  - `rp2354b_a4` — `SC1512-A4`.
  - `skyworks_si4732_a10_gsr` — `Si4732-A10-GSR`.
  - `vishay_tsmp95000tt` — `Vishay TSMP95000TT`.
  - `vishay_tsop75238tr` — `Vishay TSOP75238TR`.
  - `vishay_vemd1060x01` — `VEMD1060X01`.
  - `vishay_vsmy14940` — `Vishay VSMY14940`.

</details>

<details><summary><code>SUB-MECH-OPTICAL</code> — Display, cells, connectors, controls and electro-acoustic/mechanical parts — 26 line(s)</summary>

- Disposition: no drop-in by nominal description; exact mate, outline, human factors and source-backed mechanical/environmental analysis required.
- Equivalence envelope:
  - same mating standard/contact map/polarity plus compatible footprint, keepout, insertion, retention and service access.
  - display optics/touch/backlight, cell protection/chemistry, switch force/travel/current and transducer acoustic response no worse.
  - sealing, strain, temperature, life and manufacturing process remain compatible.
- Required requalification:
  - source-backed dimensional/fit analysis, geometry/DRC and deterministic assembly instructions before order.
  - ordinary assembly/disassembly, continuity and visual inspection on the one prototype after arrival; unsourced loads remain design-analysis inputs and no artificial ageing is required.
  - display, battery, UI and acoustic functional checks on the one prototype without drop, shaker/vibration or prescribed-cycle qualification.
- Current lines:
  - `alps_ec11e18244au` — `Alps Alpine EC11E18244AU`.
  - `alps_skrtlae010` — `Alps Alpine SKRTLAE010`.
  - `ck_js102011scqn` — `C&K JS102011SCQN`.
  - `davies_1227_j` — `Davies Molding 1227-J`.
  - `eastrising_er_tft035ips_6_ctp` — `EastRising ER-TFT035IPS-6 + ER-TPC035-6`.
  - `gct_rfpc_sma31_fn_175_a` — `GCT RFPC-SMA31-FN-175-A`.
  - `gct_rfpc_sma32_fn_175_a` — `GCT RFPC-SMA32-FN-175-A`.
  - `gct_usb4105_gf_a` — `GCT USB4105-GF-A`.
  - `hirose_df40c_2_0_40ds_0_4v_51` — `Hirose DF40C(2.0)-40DS-0.4V(51)`.
  - `hirose_df40c_40dp_0_4v_51` — `Hirose DF40C-40DP-0.4V(51)`.
  - `hirose_dm3at_sf_pejm5` — `Hirose DM3AT-SF-PEJM5`.
  - `hirose_fh34srj_50s_0_5sh_50` — `Hirose FH34SRJ-50S-0.5SH(50)`.
  - `hirose_fx8c_80p_sv1_92` — `Hirose FX8C-80P-SV1(92)`.
  - `hirose_fx8c_80s_sv5_92` — `Hirose FX8C-80S-SV5(92)`.
  - `hirose_ufl_r_smt_1_10` — `Hirose U.FL-R-SMT-1(80)`.
  - `jae_dx07s016ja1r1500` — `JAE DX07S016JA1R1500`.
  - `keystone_1048p` — `Keystone Electronics 1048P`.
  - `omron_b3s_1100p` — `OMRON B3S-1100P`.
  - `pui_as02404po` — `PUI Audio AS02404PO`.
  - `same_sky_cmej_0413_42_smt_tr` — `Same Sky CMEJ-0413-42-SMT-TR`.
  - `same_sky_sj_43504_smt_tr` — `Same Sky SJ-43504-SMT-TR`.
  - `samtec_ftsh_105_01_l_dv_k_p_tr` — `Samtec FTSH-105-01-L-DV-K-P-TR`.
  - `samtec_hle_107_02_g_dv_pe_lc` — `Samtec HLE-107-02-G-DV-PE-LC`.
  - `seeed_1125r_smt_4p` — `1125R-SMT-4P`.
  - `te_2118651_2` — `TE Connectivity 2118651-2`.
  - `xtar_18650_4000mah_protected` — `XTAR 18650 4000mAh`.

</details>

## Quantity-100 cost evidence

Only exact-MPN published USD prices that apply to a 100-piece purchase are listed. Taxes, tariffs, freight, PCB, assembly, test, enclosure, yield and tooling are excluded. The sum below is intentionally partial while any purchase line remains unpriced.

<details><summary><code>Abracon ABM8-26.000MHZ-10-D-1-G-T</code> — 1 × USD 0.3257 = USD 0.3257</summary>

- Device id: `abracon_abm8_26mhz_10_d_1_g_t`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/abracon-llc/ABM8-26-000MHZ-10-D-1-G-T/9997912).

</details>

<details><summary><code>Abracon ABM8-272-T3</code> — 1 × USD 0.4085 = USD 0.4085</summary>

- Device id: `abracon_abm8_272_t3`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.digikey.com/en/products/detail/abracon-llc/ABM8-272-T3/22472366).

</details>

<details><summary><code>Abracon AOTA-B201610S3R3-101-T</code> — 1 × USD 0.1512 = USD 0.1512</summary>

- Device id: `abracon_aota_b201610s3r3_101_t`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.digikey.com/en/products/detail/abracon-llc/AOTA-B201610S3R3-101-T/25621527).

</details>

<details><summary><code>Analog Devices AD8314ACPZ-RL7</code> — 6 × USD 2.8570 = USD 17.1420</summary>

- Device id: `adi_ad8314acpz_rl7`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/analog-devices-inc/AD8314ACPZ-RL7/671084).

</details>

<details><summary><code>LTC5532ES6#TRMPBF</code> — 2 × USD 3.8877 = USD 7.7754</summary>

- Device id: `adi_ltc5532_es6_trmpbf`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/analog-devices-inc/LTC5532ES6-TRMPBF/1115993).

</details>

<details><summary><code>Analog Devices MAX17320G20+T</code> — 1 × USD 4.0019 = USD 4.0019</summary>

- Device id: `adi_max17320_g20_t`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX17320G20-T/16675120).

</details>

<details><summary><code>Alps Alpine EC11E18244AU</code> — 1 × USD 3.2880 = USD 3.2880</summary>

- Device id: `alps_ec11e18244au`.
- Scope: `base_product`.
- Comparable basis: DigiKey tray quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/alps-alpine/EC11E18244AU/19529126).

</details>

<details><summary><code>Alps Alpine SKRTLAE010</code> — 6 × USD 0.2433 = USD 1.4598</summary>

- Device id: `alps_skrtlae010`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.digikey.com/en/products/detail/alps-alpine/SKRTLAE010/19529044).

</details>

<details><summary><code>Bourns CRM2512-FX-20R0ELF</code> — 2 × USD 0.1840 = USD 0.3680</summary>

- Device id: `bourns_crm2512_fx_20r0elf`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/bourns-inc/CRM2512-FX-20R0ELF/4698376).

</details>

<details><summary><code>CC1101RGPR</code> — 1 × USD 3.0358 = USD 3.0358</summary>

- Device id: `cc1101rgpr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/CC1101RGPR/3947323).

</details>

<details><summary><code>C&K JS102011SCQN</code> — 1 × USD 0.7823 = USD 0.7823</summary>

- Device id: `ck_js102011scqn`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/c-k/JS102011SCQN/7355835).

</details>

<details><summary><code>Davies Molding 1227-J</code> — 1 × USD 0.9720 = USD 0.9720</summary>

- Device id: `davies_1227_j`.
- Scope: `base_product`.
- Comparable basis: Mouser quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/en/ProductDetail/Davies-Molding/1227-J?qs=AaRlLUpeMszUlt7gcGM9fQ%3D%3D).

</details>

<details><summary><code>Diodes Incorporated 2N7002DW-7-F</code> — 4 × USD 0.1277 = USD 0.5108</summary>

- Device id: `diodes_2n7002dw_7_f`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/diodes-incorporated/2N7002DW-7-F/749948).

</details>

<details><summary><code>Diodes Incorporated BAT54-7-F</code> — 5 × USD 0.0698 = USD 0.3490</summary>

- Device id: `diodes_bat54_7_f`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/diodes-incorporated/BAT54-7-F/717699).

</details>

<details><summary><code>Diodes Incorporated DMN2056U-7</code> — 3 × USD 0.1490 = USD 0.4470</summary>

- Device id: `diodes_dmn2056u_7`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/diodes-incorporated/DMN2056U-7/7352909).

</details>

<details><summary><code>Diodes Incorporated MMBT3904-7-F</code> — 2 × USD 0.0597 = USD 0.1194</summary>

- Device id: `diodes_mmbt3904_7_f`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/diodes-incorporated/MMBT3904-7-F/815727).

</details>

<details><summary><code>Diodes Incorporated PAM8302AAYCR</code> — 1 × USD 0.3510 = USD 0.3510</summary>

- Device id: `diodes_pam8302a_aycr`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.mouser.com/en/ProductDetail/Diodes-Incorporated/PAM8302AAYCR?qs=pYVYkI7xuRX9VhIMiIHWEw%3D%3D).

</details>

<details><summary><code>EastRising ER-TFT035IPS-6 + ER-TPC035-6</code> — 1 × USD 14.9100 = USD 14.9100</summary>

- Device id: `eastrising_er_tft035ips_6_ctp`.
- Scope: `base_product`.
- Comparable basis: conservative quantity-1 base USD 9.34 plus exact capacitive-touch-controller option USD 5.57; quantity-10 configured material USD 14.67 each; target quantity `100`.
- Checked: `2026-08-29`; [published source](https://www.buydisplay.com/3-5-inch-ips-320x480-tft-lcd-display-capacitive-touch-screen).

</details>

<details><summary><code>Ebyte E01-ML01SP4</code> — 3 × USD 2.9633 = USD 8.8899</summary>

- Device id: `ebyte_e01_ml01sp4`.
- Scope: `base_product`.
- Comparable basis: JLCPCB public in-stock quantity-100 tier; target quantity `100`.
- Checked: `2026-08-29`; [published source](https://jlcpcb.com/partdetail/E01-ML01SP4/C97340).

</details>

<details><summary><code>Seiko Epson Q13FC13500005</code> — 1 × USD 0.2154 = USD 0.2154</summary>

- Device id: `epson_q13fc13500005`.
- Scope: `base_product`.
- Comparable basis: LCSC quantity-50 tier applicable to a 100-piece purchase; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.lcsc.com/product-detail/crystals_seiko-epson-q13fc13500005_C841881.html).

</details>

<details><summary><code>ESP32-C5-WROOM-1U-N8R8</code> — 1 × USD 4.1338 = USD 4.1338</summary>

- Device id: `esp32_c5_wroom_1u_n8r8`.
- Scope: `base_product`.
- Comparable basis: JLCPCB C54951858 quantity-100 tier; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/C54951858).

</details>

<details><summary><code>ESP32-S3-WROOM-1U-N16R8</code> — 1 × USD 5.1080 = USD 5.1080</summary>

- Device id: `esp32_s3_wroom_1u_n16r8`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-20`; [published source](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-WROOM-1U-N16R8/16162641).

</details>

<details><summary><code>Everest Semiconductor ES8311</code> — 1 × USD 0.3024 = USD 0.3024</summary>

- Device id: `everest_es8311_qfn20`.
- Scope: `base_product`.
- Comparable basis: JLCPCB assembly-parts quantity-100 tier; captive PCBA inventory; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://jlcpcb.com/partdetail/1044199-ES8311/C962342).

</details>

<details><summary><code>FH RS-06K47R0FT</code> — 1 × USD 0.0062 = USD 0.0062</summary>

- Device id: `fh_rs_06k47r0ft`.
- Scope: `base_product`.
- Comparable basis: conservative JLCPCB one-piece tier; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/151340-RS06K47R0FT/C140014).

</details>

<details><summary><code>GCT RFPC-SMA31-FN-175-A</code> — 8 × USD 2.4646 = USD 19.7165</summary>

- Device id: `gct_rfpc_sma31_fn_175_a`.
- Scope: `base_product`.
- Comparable basis: DigiKey tray 90-179 quantity tier applied at target quantity 100; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/gct/RFPC-SMA31-FN-175-A/25576371).

</details>

<details><summary><code>GCT RFPC-SMA32-FN-175-A</code> — 2 × USD 2.4646 = USD 4.9291</summary>

- Device id: `gct_rfpc_sma32_fn_175_a`.
- Scope: `base_product`.
- Comparable basis: DigiKey tray 90-179 quantity tier applied at target quantity 100; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/gct/RFPC-SMA32-FN-175-A/25576372).

</details>

<details><summary><code>GCT USB4105-GF-A</code> — 2 × USD 0.5745 = USD 1.1490</summary>

- Device id: `gct_usb4105_gf_a`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/gct/USB4105-GF-A/11198510).

</details>

<details><summary><code>Hirose DF40C(2.0)-40DS-0.4V(51)</code> — 1 × USD 0.3428 = USD 0.3428</summary>

- Device id: `hirose_df40c_2_0_40ds_0_4v_51`.
- Scope: `base_product`.
- Comparable basis: JLCPCB quantity-100 tier; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/x/C597934).

</details>

<details><summary><code>Hirose DF40C-40DP-0.4V(51)</code> — 1 × USD 0.7260 = USD 0.7260</summary>

- Device id: `hirose_df40c_40dp_0_4v_51`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.mouser.com/ProductDetail/Hirose-Connector/DF40C-40DP-0.4V51?qs=eDUdFcBPps3ody6AX5VRNA%3D%3D).

</details>

<details><summary><code>Hirose DM3AT-SF-PEJM5</code> — 1 × USD 2.5656 = USD 2.5656</summary>

- Device id: `hirose_dm3at_sf_pejm5`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DM3AT-SF-PEJM5/2533565).

</details>

<details><summary><code>Hirose FH34SRJ-50S-0.5SH(50)</code> — 1 × USD 0.5832 = USD 0.5832</summary>

- Device id: `hirose_fh34srj_50s_0_5sh_50`.
- Scope: `base_product`.
- Comparable basis: conservative JLCPCB exact C3169104 quantity-1 tier; quantity-10 tier USD 0.4711; target quantity `100`.
- Checked: `2026-08-29`; [published source](https://jlcpcb.com/partdetail/HRS_Hirose-FH34SRJ_50S_0_5SH_50/C3169104).

</details>

<details><summary><code>Hirose FX8C-80P-SV1(92)</code> — 1 × USD 3.1759 = USD 3.1759</summary>

- Device id: `hirose_fx8c_80p_sv1_92`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/FX8C-80P-SV1-92/4284726).

</details>

<details><summary><code>Hirose FX8C-80S-SV5(92)</code> — 1 × USD 3.9133 = USD 3.9133</summary>

- Device id: `hirose_fx8c_80s_sv5_92`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/FX8C-80S-SV5-92/4284737).

</details>

<details><summary><code>Hirose U.FL-R-SMT-1(80)</code> — 5 × USD 0.0823 = USD 0.4115</summary>

- Device id: `hirose_ufl_r_smt_1_10`.
- Scope: `base_product`.
- Comparable basis: JLCPCB in-stock quantity-50 tier applied to quantity 100; target quantity `100`.
- Checked: `2026-08-29`; [published source](https://jlcpcb.com/partdetail/U.FL-R-SMT-1%2880%29/C88374).

</details>

<details><summary><code>Infineon BGS13SN8E6327XTSA1</code> — 2 × USD 0.2126 = USD 0.4252</summary>

- Device id: `infineon_bgs13sn8e6327xtsa1`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/infineon-technologies/BGS13SN8E6327XTSA1/6559893).

</details>

<details><summary><code>JAE DX07S016JA1R1500</code> — 1 × USD 1.2272 = USD 1.2272</summary>

- Device id: `jae_dx07s016ja1r1500`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/jae-electronics/DX07S016JA1R1500/11585731).

</details>

<details><summary><code>KEMET C0402C102K5RACTU</code> — 2 × USD 0.0150 = USD 0.0300</summary>

- Device id: `kemet_c0402c102k5ractu`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/kemet/C0402C102K5RACTU/411034).

</details>

<details><summary><code>KEMET C0402C330J5GACTU</code> — 5 × USD 0.0213 = USD 0.1065</summary>

- Device id: `kemet_c0402c330j5gactu`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/kemet/C0402C330J5GACTU/411019).

</details>

<details><summary><code>Keystone Electronics 1048P</code> — 1 × USD 8.5700 = USD 8.5700</summary>

- Device id: `keystone_1048p`.
- Scope: `base_product`.
- Comparable basis: Mouser tray quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/ProductDetail/Keystone-Electronics/1048P?qs=9%252Bwcgl%2FJqd1h8Vx3IFpTxA%3D%3D).

</details>

<details><summary><code>KYOCERA AVX CP0603Q5425ENTR</code> — 2 × USD 0.4271 = USD 0.8542</summary>

- Device id: `kyocera_avx_cp0603q5425entr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/kyocera-avx/CP0603Q5425ENTR/4805840).

</details>

<details><summary><code>LTST-C190KFKT</code> — 1 × USD 0.0637 = USD 0.0637</summary>

- Device id: `liteon_ltst_c190kfkt`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/liteon/LTST-C190KFKT/386813).

</details>

<details><summary><code>LTST-C190KRKT</code> — 9 × USD 0.0675 = USD 0.6075</summary>

- Device id: `liteon_ltst_c190krkt`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/liteon/LTST-C190KRKT/386817).

</details>

<details><summary><code>Littelfuse 0451005.MRL</code> — 2 × USD 1.4488 = USD 2.8976</summary>

- Device id: `littelfuse_0451005_mrl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/littelfuse-inc/0451005-MRL/700828).

</details>

<details><summary><code>Littelfuse SESD0402X1UN-0020-090</code> — 3 × USD 0.3794 = USD 1.1382</summary>

- Device id: `littelfuse_sesd0402x1un_0020_090`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/littelfuse-inc/SESD0402X1UN-0020-090/5233545).

</details>

<details><summary><code>Murata BLM18PG181SN1D</code> — 4 × USD 0.0431 = USD 0.1724</summary>

- Device id: `murata_blm18pg181sn1d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/BLM18PG181SN1D/1634634).

</details>

<details><summary><code>Murata GJM1555C1H100JB01D</code> — 1 × USD 0.0417 = USD 0.0417</summary>

- Device id: `murata_gjm1555c1h100jb01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GJM1555C1H100JB01D/702306).

</details>

<details><summary><code>Murata GJM1555C1H150JB01D</code> — 4 × USD 0.0392 = USD 0.1568</summary>

- Device id: `murata_gjm1555c1h150jb01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GJM1555C1H150JB01D/702310).

</details>

<details><summary><code>Murata GJM1555C1H1R2BB01D</code> — 1 × USD 0.0310 = USD 0.0310</summary>

- Device id: `murata_gjm1555c1h1r2bb01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GJM1555C1H1R2BB01D/2592874).

</details>

<details><summary><code>Murata GJM1555C1H6R2DB01D</code> — 1 × USD 0.0210 = USD 0.0210</summary>

- Device id: `murata_gjm1555c1h6r2db01d`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/c/passive-components/capacitors/ceramic-capacitors/mlccs-multilayer-ceramic-capacitors/multilayer-ceramic-capacitors-mlcc-smd-smt/?capacitance=6.2+pF&case+code+-+in=0402).

</details>

<details><summary><code>Murata GJM1555C1H8R0DB01D</code> — 1 × USD 0.0207 = USD 0.0207</summary>

- Device id: `murata_gjm1555c1h8r0db01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GJM1555C1H8R0DB01D/2593153).

</details>

<details><summary><code>Murata GJM1555C1HR47BB01D</code> — 1 × USD 0.0346 = USD 0.0346</summary>

- Device id: `murata_gjm1555c1hr47bb01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GJM1555C1HR47BB01D/7362927).

</details>

<details><summary><code>Murata GJM1555C1HR60BB01D</code> — 1 × USD 0.0310 = USD 0.0310</summary>

- Device id: `murata_gjm1555c1hr60bb01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GJM1555C1HR60BB01D/2593254).

</details>

<details><summary><code>Murata GRM1555C1H102JA01D</code> — 1 × USD 0.0181 = USD 0.0181</summary>

- Device id: `murata_grm1555c1h102ja01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM1555C1H102JA01D/702509).

</details>

<details><summary><code>Murata GRM1555C1H121JA01D</code> — 8 × USD 0.0197 = USD 0.1576</summary>

- Device id: `murata_grm1555c1h121ja01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM1555C1H121JA01D/587178).

</details>

<details><summary><code>Murata GRM1555C1H220JA01D</code> — 2 × USD 0.0025 = USD 0.0050</summary>

- Device id: `murata_grm1555c1h220ja01d`.
- Scope: `base_product`.
- Comparable basis: LCSC quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.lcsc.com/product-detail/C76960.html).

</details>

<details><summary><code>Murata GRM1555C1H221JA01D</code> — 4 × USD 0.0177 = USD 0.0708</summary>

- Device id: `murata_grm1555c1h221ja01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM1555C1H221JA01D/587204).

</details>

<details><summary><code>Murata GRM1555C1H390JA01D</code> — 2 × USD 0.0140 = USD 0.0280</summary>

- Device id: `murata_grm1555c1h390ja01d`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/ProductDetail/Murata-Electronics/GRM1555C1H390JA01D?qs=4k9rjS6ZRl5FP2mUYTju2g%3D%3D).

</details>

<details><summary><code>Murata GRM155R71A474KE01D</code> — 1 × USD 0.1771 = USD 0.1771</summary>

- Device id: `murata_grm155r71a474ke01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM155R71A474KE01D/6605995).

</details>

<details><summary><code>Murata GRM155R71E473KA88D</code> — 2 × USD 0.0126 = USD 0.0252</summary>

- Device id: `murata_grm155r71e473ka88d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM155R71E473KA88D/702519).

</details>

<details><summary><code>Murata GRM155R71H103KA88D</code> — 8 × USD 0.0097 = USD 0.0776</summary>

- Device id: `murata_grm155r71h103ka88d`.
- Scope: `base_product`.
- Comparable basis: conservative JLCPCB one-piece tier; displayed stock 675,981; target quantity `100`.
- Checked: `2026-08-29`; [published source](https://jlcpcb.com/partdetail/MurataElectronics-GRM155R71H103KA88D/C77019).

</details>

<details><summary><code>Murata GRM155R71H472KA01D</code> — 4 × USD 0.0098 = USD 0.0392</summary>

- Device id: `murata_grm155r71h472ka01d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM155R71H472KA01D/587946).

</details>

<details><summary><code>Murata GRM188R60J106ME47D</code> — 19 × USD 0.0377 = USD 0.7163</summary>

- Device id: `murata_grm188r60j106me47d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM188R60J106ME47D/965910).

</details>

<details><summary><code>Murata GRM188R71E224KA88D</code> — 2 × USD 0.0306 = USD 0.0612</summary>

- Device id: `murata_grm188r71e224ka88d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM188R71E224KA88D/702554).

</details>

<details><summary><code>Murata GRM188R71E474KA12D</code> — 4 × USD 0.0496 = USD 0.1984</summary>

- Device id: `murata_grm188r71e474ka12d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM188R71E474KA12D/702555).

</details>

<details><summary><code>Murata GRM188Z71A475ME15D</code> — 2 × USD 0.0899 = USD 0.1798</summary>

- Device id: `murata_grm188z71a475me15d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM188Z71A475ME15D/13904814).

</details>

<details><summary><code>Murata GRM21BR60J226ME39L</code> — 6 × USD 0.1341 = USD 0.8046</summary>

- Device id: `murata_grm21br60j226me39l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM21BR60J226ME39L/587424).

</details>

<details><summary><code>Murata GRM21BR71E225KE11L</code> — 5 × USD 0.0612 = USD 0.3060</summary>

- Device id: `murata_grm21br71e225ke11l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM21BR71E225KE11L/6606096).

</details>

<details><summary><code>Murata GRM31C5C1H224JE02L</code> — 1 × USD 0.3198 = USD 0.3198</summary>

- Device id: `murata_grm31c5c1h224je02l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM31C5C1H224JE02L/10691338).

</details>

<details><summary><code>Murata GRM31CR71A226KE15L</code> — 1 × USD 0.1884 = USD 0.1884</summary>

- Device id: `murata_grm31cr71a226ke15l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM31CR71A226KE15L/2039036).

</details>

<details><summary><code>Murata GRM31CR71E106MA12L</code> — 12 × USD 0.1224 = USD 1.4688</summary>

- Device id: `murata_grm31cr71e106ma12l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM31CR71E106MA12L/2548205).

</details>

<details><summary><code>Murata GRM32ER71E226KE15L</code> — 13 × USD 0.3303 = USD 4.2939</summary>

- Device id: `murata_grm32er71e226ke15l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/GRM32ER71E226KE15L/2039092).

</details>

<details><summary><code>Murata LQG15HS10NJ02D</code> — 3 × USD 0.0310 = USD 0.0930</summary>

- Device id: `murata_lqg15hs10nj02d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/LQG15HS10NJ02D/662903).

</details>

<details><summary><code>Murata LQG15HS15NJ02D</code> — 1 × USD 0.0310 = USD 0.0310</summary>

- Device id: `murata_lqg15hs15nj02d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/LQG15HS15NJ02D/662874).

</details>

<details><summary><code>Murata LQG15HS2N2S02D</code> — 1 × USD 0.0310 = USD 0.0310</summary>

- Device id: `murata_lqg15hs2n2s02d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/LQG15HS2N2S02D/662863).

</details>

<details><summary><code>Murata LQG15HS3N3S02D</code> — 1 × USD 0.0310 = USD 0.0310</summary>

- Device id: `murata_lqg15hs3n3s02d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/LQG15HS3N3S02D/662896).

</details>

<details><summary><code>Murata LQG15HS3N6S02D</code> — 1 × USD 0.0310 = USD 0.0310</summary>

- Device id: `murata_lqg15hs3n6s02d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/LQG15HS3N6S02D/2594221).

</details>

<details><summary><code>Murata LQG15HS6N8J02D</code> — 1 × USD 0.0310 = USD 0.0310</summary>

- Device id: `murata_lqg15hs6n8j02d`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/murata-electronics/LQG15HS6N8J02D/662870).

</details>

<details><summary><code>Murata LQW15AN56NG00D</code> — 1 × USD 0.0447 = USD 0.0447</summary>

- Device id: `murata_lqw15an56ng00d`.
- Scope: `base_product`.
- Comparable basis: JLCPCB one-to-199-piece tier; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/x/C167482).

</details>

<details><summary><code>Nexperia 74LVC126APW,118</code> — 8 × USD 0.1341 = USD 1.0728</summary>

- Device id: `nexperia_74lvc126apw_118`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/nexperia-usa-inc/74LVC126APW-118/2753809).

</details>

<details><summary><code>74LVC1G32GV,125</code> — 2 × USD 0.0523 = USD 0.1046</summary>

- Device id: `nexperia_74lvc1g32gv_125`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/nexperia-usa-inc/74LVC1G32GV-125/946687).

</details>

<details><summary><code>Nexperia 74LVC2G126DP,125</code> — 5 × USD 0.3753 = USD 1.8765</summary>

- Device id: `nexperia_74lvc2g126dp_125`.
- Scope: `base_product`.
- Comparable basis: JLCPCB quantity-100 tier; live stock 155, MOQ 1; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/Nexperia-74LVC2G126DP125/C503392).

</details>

<details><summary><code>74LVC2G14GV,125</code> — 2 × USD 0.1600 = USD 0.3200</summary>

- Device id: `nexperia_74lvc2g14gv_125`.
- Scope: `base_product`.
- Comparable basis: JLCPCB 50-piece tier; current stock 153, available order quantity 35, MOQ 1; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/Nexperia-74LVC2G14GV125/C426708).

</details>

<details><summary><code>OMRON B3S-1100P</code> — 16 × USD 0.6405 = USD 10.2480</summary>

- Device id: `omron_b3s_1100p`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/B3S-1100P/368393).

</details>

<details><summary><code>BAT54ALT1G</code> — 5 × USD 0.0577 = USD 0.2885</summary>

- Device id: `onsemi_bat54alt1g`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/onsemi/BAT54ALT1G/917808).

</details>

<details><summary><code>onsemi BAV70LT1G</code> — 1 × USD 0.0460 = USD 0.0460</summary>

- Device id: `onsemi_bav70lt1g`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/onsemi/BAV70LT1G/918324).

</details>

<details><summary><code>onsemi CAT24C512WI-GT3</code> — 1 × USD 0.7133 = USD 0.7133</summary>

- Device id: `onsemi_cat24c512wi_gt3`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/onsemi/CAT24C512WI-GT3/2683757).

</details>

<details><summary><code>onsemi FSUSB42MUX</code> — 2 × USD 0.4663 = USD 0.9326</summary>

- Device id: `onsemi_fsusb42_mux`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/onsemi/FSUSB42MUX/2036916).

</details>

<details><summary><code>Panasonic ERJ-2RKF22R0X</code> — 45 × USD 0.0155 = USD 0.6975</summary>

- Device id: `panasonic_erj_2rkf22r0x`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/panasonic-industry/ERJ-2RKF22R0X/1746157).

</details>

<details><summary><code>Panasonic ERJ-2RKF27R0X</code> — 2 × USD 0.0155 = USD 0.0310</summary>

- Device id: `panasonic_erj_2rkf27r0x`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/panasonic-electronic-components/ERJ-2RKF27R0X/1746179).

</details>

<details><summary><code>Panasonic ERJ-P08F10R0V</code> — 1 × USD 0.0689 = USD 0.0689</summary>

- Device id: `panasonic_erj_p08f10r0v`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/panasonic-industry/ERJ-P08F10R0V/5722446).

</details>

<details><summary><code>PUI Audio AS02404PO</code> — 1 × USD 2.5294 = USD 2.5294</summary>

- Device id: `pui_as02404po`.
- Scope: `base_product`.
- Comparable basis: DigiKey bulk 50-plus tier applicable to an order of 100 pieces; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/pui-audio-inc/AS02404PO/24385608).

</details>

<details><summary><code>SC1512-A4</code> — 1 × USD 1.4927 = USD 1.4927</summary>

- Device id: `rp2354b_a4`.
- Scope: `base_product`.
- Comparable basis: JLCPCB/LCSC C39843328 public quantity-10 tier used conservatively until the quantity-100 tier is rechecked at freeze; quantity-1 is USD 1.5658; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/RaspberryPi-RP2354B/C39843328).

</details>

<details><summary><code>Same Sky CMEJ-0413-42-SMT-TR</code> — 1 × USD 0.3909 = USD 0.3909</summary>

- Device id: `same_sky_cmej_0413_42_smt_tr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CMEJ-0413-42-SMT-TR/10253447).

</details>

<details><summary><code>Same Sky SJ-43504-SMT-TR</code> — 1 × USD 0.9304 = USD 0.9304</summary>

- Device id: `same_sky_sj_43504_smt_tr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; 7,349 units shown in stock; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/SJ-43504-SMT-TR/2625173).

</details>

<details><summary><code>Samtec FTSH-105-01-L-DV-K-P-TR</code> — 3 × USD 1.6991 = USD 5.0973</summary>

- Device id: `samtec_ftsh_105_01_l_dv_k_p_tr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/samtec-inc/FTSH-105-01-L-DV-K-P-TR/5305483).

</details>

<details><summary><code>Samtec HLE-107-02-G-DV-PE-LC</code> — 1 × USD 2.5420 = USD 2.5420</summary>

- Device id: `samtec_hle_107_02_g_dv_pe_lc`.
- Scope: `base_product`.
- Comparable basis: Samtec OEM quantity-100 tier; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.samtec.com/products/hle-107-02-g-dv-pe-lc).

</details>

<details><summary><code>1125R-SMT-4P</code> — 1 × USD 0.0420 = USD 0.0420</summary>

- Device id: `seeed_1125r_smt_4p`.
- Scope: `base_product`.
- Comparable basis: Seeed Open Parts Library published per-placement price applied at target quantity 100; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.seeedstudio.com/blog/2022/11/18/seeed-grove-designers-guide-pcb-design-guidelines-and-more/).

</details>

<details><summary><code>Si4732-A10-GSR</code> — 1 × USD 1.6785 = USD 1.6785</summary>

- Device id: `skyworks_si4732_a10_gsr`.
- Scope: `base_product`.
- Comparable basis: JLCPCB PCBA-only in-stock-item quantity-100+ tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://jlcpcb.com/partdetail/SILICONLABS-SI4732_A10GSR/C2155558).

</details>

<details><summary><code>Sunlord MWSA0503S-2R2MT</code> — 1 × USD 0.5751 = USD 0.5751</summary>

- Device id: `sunlord_mwsa0503s_2r2mt`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/shenzhen-sunlord-electronics-co-ltd/MWSA0503S-2R2MT/14120103).

</details>

<details><summary><code>Sunlord MWSA0503S-4R7MT</code> — 1 × USD 0.5751 = USD 0.5751</summary>

- Device id: `sunlord_mwsa0503s_4r7mt`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/shenzhen-sunlord-electronics-co-ltd/MWSA0503S-4R7MT/14120288).

</details>

<details><summary><code>Sunlord WPN201612H2R2MT</code> — 1 × USD 0.0426 = USD 0.0426</summary>

- Device id: `sunlord_wpn201612h2r2mt`.
- Scope: `base_product`.
- Comparable basis: JLCPCB assembly-parts quantity-100 tier; captive PCBA inventory; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://jlcpcb.com/partdetail/Sunlord-WPN201612H2R2MT/C97025).

</details>

<details><summary><code>TCA4307DGKR</code> — 1 × USD 2.0137 = USD 2.0137</summary>

- Device id: `tca4307dgkr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TCA4307DGKR/13169411).

</details>

<details><summary><code>TCA6424ARGJR</code> — 1 × USD 1.7001 = USD 1.7001</summary>

- Device id: `tca6424argjr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TCA6424ARGJR/2411683).

</details>

<details><summary><code>TDK B57332V5103F360</code> — 6 × USD 0.1157 = USD 0.6942</summary>

- Device id: `tdk_b57332v5103f360`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/epcos-tdk-electronics/B57332V5103F360/4945421).

</details>

<details><summary><code>TDK C1005X5R0J475K050BC</code> — 4 × USD 0.0903 = USD 0.3612</summary>

- Device id: `tdk_c1005x5r0j475k050bc`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.digikey.com/en/products/detail/tdk-corporation/C1005X5R0J475K050BC/2443425).

</details>

<details><summary><code>TDK C1608X7R1C105K080AC</code> — 37 × USD 0.0392 = USD 1.4504</summary>

- Device id: `tdk_c1608x7r1c105k080ac`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/tdk-corporation/C1608X7R1C105K080AC/634395).

</details>

<details><summary><code>TDK CGA5L1X7R1E475K160AC</code> — 3 × USD 0.1419 = USD 0.4257</summary>

- Device id: `tdk_cga5l1x7r1e475k160ac`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/tdk/CGA5L1X7R1E475K160AC/2443184).

</details>

<details><summary><code>TE Connectivity 2118651-2</code> — 5 × USD 1.8211 = USD 9.1055</summary>

- Device id: `te_2118651_2`.
- Scope: `base_product`.
- Comparable basis: DigiKey bag quantity-100 tier; target quantity `100`.
- Checked: `2026-08-20`; [published source](https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/2118651-2/16538824).

</details>

<details><summary><code>Texas Instruments BQ25798RQMR</code> — 1 × USD 3.5140 = USD 3.5140</summary>

- Device id: `ti_bq25798_rqmr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/BQ25798RQMR/15666783).

</details>

<details><summary><code>Texas Instruments CSD87313DMS</code> — 1 × USD 0.7651 = USD 0.7651</summary>

- Device id: `ti_csd87313dms`.
- Scope: `base_product`.
- Comparable basis: JLCPCB quantity-100 tier; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/x/C2863848).

</details>

<details><summary><code>Texas Instruments MSPM0C1106SDGS20R</code> — 2 × USD 0.8384 = USD 1.6768</summary>

- Device id: `ti_mspm0c1106_sdgs20r`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-20`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/MSPM0C1106SDGS20R/28264017).

</details>

<details><summary><code>SN74LVC08APWR</code> — 2 × USD 0.2127 = USD 0.4254</summary>

- Device id: `ti_sn74lvc08a_pwr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC08APWR/276489).

</details>

<details><summary><code>Texas Instruments SN74LVC1G06DCKR</code> — 2 × USD 0.0749 = USD 0.1498</summary>

- Device id: `ti_sn74lvc1g06_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G06DCKR/377452).

</details>

<details><summary><code>SN74LVC1G07DCKR</code> — 10 × USD 0.0509 = USD 0.5090</summary>

- Device id: `ti_sn74lvc1g07_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G07DCKR/377457).

</details>

<details><summary><code>SN74LVC1G08DCKR</code> — 4 × USD 0.0490 = USD 0.1960</summary>

- Device id: `ti_sn74lvc1g08_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G08DCKR/385741).

</details>

<details><summary><code>Texas Instruments SN74LVC1G125DCKR</code> — 1 × USD 0.0583 = USD 0.0583</summary>

- Device id: `ti_sn74lvc1g125_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G125DCKR/385743).

</details>

<details><summary><code>Texas Instruments SN74LVC1G126DCKR</code> — 4 × USD 0.0546 = USD 0.2184</summary>

- Device id: `ti_sn74lvc1g126_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G126DCKR/385723).

</details>

<details><summary><code>SN74LVC1G17DCKR</code> — 1 × USD 0.1434 = USD 0.1434</summary>

- Device id: `ti_sn74lvc1g17_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-24`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G17DCKR/389053).

</details>

<details><summary><code>Texas Instruments SN74LVC1G3157DBVR</code> — 1 × USD 0.1301 = USD 0.1301</summary>

- Device id: `ti_sn74lvc1g3157_dbvr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G3157DBVR/562896).

</details>

<details><summary><code>SN74LVC1G74DCUR</code> — 1 × USD 0.3300 = USD 0.3300</summary>

- Device id: `ti_sn74lvc1g74_dcur`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/en/ProductDetail/Texas-Instruments/SN74LVC1G74DCUR?qs=DS7Z8uEdLNyRBKrHxqRXjA%3D%3D).

</details>

<details><summary><code>Texas Instruments SN74LVC2G08DCUR</code> — 3 × USD 0.2296 = USD 0.6888</summary>

- Device id: `ti_sn74lvc2g08_dcur`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC2G08DCUR/484830).

</details>

<details><summary><code>Texas Instruments SN74LVC2G66DCUR</code> — 2 × USD 0.3930 = USD 0.7860</summary>

- Device id: `ti_sn74lvc2g66_dcur`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/ProductDetail/Texas-Instruments/SN74LVC2G66DCUR?qs=N6WZOzgtpqWMpNL31DMvDQ%3D%3D).

</details>

<details><summary><code>SN74LVC3G07DCUR</code> — 2 × USD 0.4087 = USD 0.8174</summary>

- Device id: `ti_sn74lvc3g07_dcur`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC3G07DCUR/484588).

</details>

<details><summary><code>SN74LVC3G34DCUR</code> — 1 × USD 0.2616 = USD 0.2616</summary>

- Device id: `ti_sn74lvc3g34_dcur`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC3G34DCUR/484593).

</details>

<details><summary><code>TCA9534APWR</code> — 2 × USD 1.0212 = USD 2.0424</summary>

- Device id: `ti_tca9534a_pwr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TCA9534APWR/5004965).

</details>

<details><summary><code>TCA9535PWR</code> — 1 × USD 1.1915 = USD 1.1915</summary>

- Device id: `ti_tca9535_pwr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-20`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TCA9535PWR/2139128).

</details>

<details><summary><code>TCA9539PWR</code> — 1 × USD 1.0196 = USD 1.0196</summary>

- Device id: `ti_tca9539_pwr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TCA9539PWR/2139129).

</details>

<details><summary><code>TLV1821DCKR</code> — 2 × USD 0.7440 = USD 1.4880</summary>

- Device id: `ti_tlv1821_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TLV1821DCKR/22147288).

</details>

<details><summary><code>TLV1824PWR</code> — 2 × USD 1.0518 = USD 2.1036</summary>

- Device id: `ti_tlv1824_pwr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TLV1824PWR/23028806).

</details>

<details><summary><code>TLV9061IDBVR</code> — 2 × USD 0.3940 = USD 0.7880</summary>

- Device id: `ti_tlv9061_idbvr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TLV9061IDBVR/9771970).

</details>

<details><summary><code>Texas Instruments TMUX1136DGSR</code> — 4 × USD 2.0581 = USD 8.2324</summary>

- Device id: `ti_tmux1136_dgsr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TMUX1136DGSR/10273239).

</details>

<details><summary><code>Texas Instruments TPD2EUSB30ADRTR</code> — 2 × USD 0.4219 = USD 0.8438</summary>

- Device id: `ti_tpd2eusb30a_drtr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPD2EUSB30ADRTR/2520830).

</details>

<details><summary><code>Texas Instruments TPD4E05U06DQAR</code> — 13 × USD 0.3090 = USD 4.0170</summary>

- Device id: `ti_tpd4e05u06_dqar`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPD4E05U06DQAR/3996774).

</details>

<details><summary><code>Texas Instruments TPD4S201RUKR</code> — 1 × USD 0.7713 = USD 0.7713</summary>

- Device id: `ti_tpd4s201_rukr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPD4S201RUKR/27685826).

</details>

<details><summary><code>Texas Instruments TPD8E003DQDR</code> — 2 × USD 0.6445 = USD 1.2890</summary>

- Device id: `ti_tpd8e003_dqdr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPD8E003DQDR/2348535).

</details>

<details><summary><code>Texas Instruments TPS22919DCKR</code> — 7 × USD 0.1189 = USD 0.8323</summary>

- Device id: `ti_tps22919_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS22919DCKR/10435170).

</details>

<details><summary><code>Texas Instruments TPS2553DRVR-1</code> — 1 × USD 0.6093 = USD 0.6093</summary>

- Device id: `ti_tps2553drvr_1`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS2553DRVR-1/2047903).

</details>

<details><summary><code>Texas Instruments TPS25751DREFR</code> — 1 × USD 1.8384 = USD 1.8384</summary>

- Device id: `ti_tps25751d_refr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS25751DREFR/23028775).

</details>

<details><summary><code>Texas Instruments TPS259470LRPWR</code> — 2 × USD 1.0196 = USD 2.0392</summary>

- Device id: `ti_tps259470l_rpwr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS259470LRPWR/14124014).

</details>

<details><summary><code>Texas Instruments TPS25961DRVR</code> — 1 × USD 0.4513 = USD 0.4513</summary>

- Device id: `ti_tps25961_drvr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS25961DRVR/17394947).

</details>

<details><summary><code>Texas Instruments TPS25974LRPWR</code> — 2 × USD 0.7929 = USD 1.5858</summary>

- Device id: `ti_tps25974l_rpwr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS25974LRPWR/15965500).

</details>

<details><summary><code>Texas Instruments TPS3435CAKAGDDFR</code> — 1 × USD 1.4760 = USD 1.4760</summary>

- Device id: `ti_tps3435cakagddfr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-20`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS3435CAKAGDDFR/17748491).

</details>

<details><summary><code>TPS3808G33DBVR</code> — 4 × USD 1.0984 = USD 4.3936</summary>

- Device id: `ti_tps3808g33_dbvr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS3808G33DBVR/666727).

</details>

<details><summary><code>Texas Instruments TPS3839K33DBZR</code> — 2 × USD 0.3940 = USD 0.7880</summary>

- Device id: `ti_tps3839k33_dbzr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS3839K33DBZR/3748986).

</details>

<details><summary><code>Texas Instruments TPS564252DRLR</code> — 3 × USD 0.2953 = USD 0.8859</summary>

- Device id: `ti_tps564252_drlr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS564252DRLR/20415586).

</details>

<details><summary><code>Texas Instruments TPS629203DRLR</code> — 1 × USD 0.6192 = USD 0.6192</summary>

- Device id: `ti_tps629203_drlr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS629203DRLR/16516661).

</details>

<details><summary><code>Texas Instruments TS5A63157DCKR</code> — 3 × USD 0.2330 = USD 0.6990</summary>

- Device id: `ti_ts5a63157_dckr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; exact line was temporarily out of stock when checked; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TS5A63157DCKR/1216801).

</details>

<details><summary><code>Texas Instruments TVS2200DRVR</code> — 1 × USD 0.4493 = USD 0.4493</summary>

- Device id: `ti_tvs2200_drvr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TVS2200DRVR/8567233).

</details>

<details><summary><code>Texas Instruments TXS0102DCUR</code> — 1 × USD 0.3480 = USD 0.3480</summary>

- Device id: `ti_txs0102_dcur`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/ProductDetail/Texas-Instruments/TXS0102DCUR).

</details>

<details><summary><code>TTM Technologies B0310J50100AHF</code> — 1 × USD 0.9929 = USD 0.9929</summary>

- Device id: `ttm_b0310j50100ahf`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/ttm-technologies-inc/B0310J50100AHF/3069172).

</details>

<details><summary><code>TTM Technologies DC2337J5010AHF</code> — 3 × USD 1.0291 = USD 3.0873</summary>

- Device id: `ttm_dc2337j5010ahf`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/ttm-technologies-inc/DC2337J5010AHF/3069211).

</details>

<details><summary><code>UNI-ROYAL 0402WGF1333TCE</code> — 1 × USD 0.0015 = USD 0.0015</summary>

- Device id: `uniroyal_0402wgf1333tce`.
- Scope: `base_product`.
- Comparable basis: JLCPCB one-piece tier; live stock 6692, MOQ 1; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/26496-0402WGF1333TCE/C25753).

</details>

<details><summary><code>UNI-ROYAL 0402WGF1603TCE</code> — 1 × USD 0.0026 = USD 0.0026</summary>

- Device id: `uniroyal_0402wgf1603tce`.
- Scope: `base_product`.
- Comparable basis: conservative JLCPCB one-piece tier; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/26500-0402WGF1603TCE/C25757).

</details>

<details><summary><code>UNI-ROYAL 0402WGF1651TCE</code> — 1 × USD 0.0008 = USD 0.0008</summary>

- Device id: `uniroyal_0402wgf1651tce`.
- Scope: `base_product`.
- Comparable basis: JLCPCB one-piece tier; live stock 5616, MOQ 1; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/26612-0402WGF1651TCE/C25869).

</details>

<details><summary><code>UNI-ROYAL 0402WGF2201TCE</code> — 23 × USD 0.0039 = USD 0.0897</summary>

- Device id: `uniroyal_0402wgf2201tce`.
- Scope: `base_product`.
- Comparable basis: JLCPCB one-piece tier; live stock 2027222, MOQ 1; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/26622-0402WGF2201TCE/C25879).

</details>

<details><summary><code>UNI-ROYAL 0402WGF2703TCE</code> — 1 × USD 0.0057 = USD 0.0057</summary>

- Device id: `uniroyal_0402wgf2703tce`.
- Scope: `base_product`.
- Comparable basis: JLCPCB one-piece tier; live stock 156208, MOQ 1; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/26513-0402WGF2703TCE/C25770).

</details>

<details><summary><code>UNI-ROYAL 0402WGF5231TCE</code> — 1 × USD 0.0061 = USD 0.0061</summary>

- Device id: `uniroyal_0402wgf5231tce`.
- Scope: `base_product`.
- Comparable basis: JLCPCB one-piece tier; live stock 40861, MOQ 1; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/26650-0402WGF5231TCE/C25907).

</details>

<details><summary><code>UNI-ROYAL 0402WGF8201TCE</code> — 1 × USD 0.0048 = USD 0.0048</summary>

- Device id: `uniroyal_0402wgf8201tce`.
- Scope: `base_product`.
- Comparable basis: JLCPCB one-piece tier; live stock 234262, MOQ 1; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/26667-0402WGF8201TCE/C25924).

</details>

<details><summary><code>Vishay TNPW040210K0BEED</code> — 1 × USD 0.1812 = USD 0.1812</summary>

- Device id: `vishay_tnpw040210k0beed`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-24`; [published source](https://www.digikey.com/en/products/detail/vishay-dale/TNPW040210K0BEED/1857039).

</details>

<details><summary><code>Vishay TNPW040243K7BEED</code> — 1 × USD 0.3475 = USD 0.3475</summary>

- Device id: `vishay_tnpw040243k7beed`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-24`; [published source](https://www.digikey.com/en/products/detail/vishay-dale/TNPW040243K7BEED/9448503).

</details>

<details><summary><code>Vishay TSMP95000TT</code> — 1 × USD 1.0600 = USD 1.0600</summary>

- Device id: `vishay_tsmp95000tt`.
- Scope: `base_product`.
- Comparable basis: Mouser quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://br.mouser.com/ProductDetail/Vishay-Semiconductors/TSMP95000TT?qs=ulEaXIWI0c%252BKGdRJO7yKyQ%3D%3D).

</details>

<details><summary><code>Vishay TSOP75238TR</code> — 1 × USD 1.2231 = USD 1.2231</summary>

- Device id: `vishay_tsop75238tr`.
- Scope: `base_product`.
- Comparable basis: JLCPCB quantity-100 tier; public stock is below the 100-device requirement; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/x/C511498).

</details>

<details><summary><code>VEMD1060X01</code> — 1 × USD 0.5371 = USD 0.5371</summary>

- Device id: `vishay_vemd1060x01`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/vishay-semiconductor-opto-division/VEMD1060X01/5879087).

</details>

<details><summary><code>Vishay VSMY14940</code> — 1 × USD 0.5035 = USD 0.5035</summary>

- Device id: `vishay_vsmy14940`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/vishay-semiconductor-opto-division/VSMY14940/4494435).

</details>

<details><summary><code>Vishay WSL25125L000FEA</code> — 1 × USD 1.0600 = USD 1.0600</summary>

- Device id: `vishay_wsl25125l000fea`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/ProductDetail/Vishay-Dale/WSL25125L000FEA?qs=ViWNInbc%252BeWBpJ7mz8KqSA%3D%3D).

</details>

<details><summary><code>Yageo CC0402KRX7R9BB104</code> — 147 × USD 0.0107 = USD 1.5729</summary>

- Device id: `yageo_cc0402krx7r9bb104`.
- Scope: `base_product`.
- Comparable basis: JLCPCB one-piece tier; next displayed tier starts at 500 pieces; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/Yageo-CC0402KRX7R9BB104/C131394).

</details>

<details><summary><code>Yageo CC0603KRX7R0BB104</code> — 1 × USD 0.0260 = USD 0.0260</summary>

- Device id: `yageo_cc0603krx7r0bb104`.
- Scope: `base_product`.
- Comparable basis: conservative JLCPCB one-piece tier; target quantity `100`.
- Checked: `2026-08-28`; [published source](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R0BB104/C113803).

</details>

<details><summary><code>Yageo RC0402FR-07100KL</code> — 40 × USD 0.0097 = USD 0.3880</summary>

- Device id: `yageo_rc0402fr_07100kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-07100KL/726526).

</details>

<details><summary><code>Yageo RC0402FR-07100RL</code> — 7 × USD 0.0097 = USD 0.0679</summary>

- Device id: `yageo_rc0402fr_07100rl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-07100RL/729474).

</details>

<details><summary><code>Yageo RC0402FR-0710KL</code> — 203 × USD 0.0097 = USD 1.9691</summary>

- Device id: `yageo_rc0402fr_0710kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0710KL/726523).

</details>

<details><summary><code>Yageo RC0402FR-07110KL</code> — 2 × USD 0.0097 = USD 0.0194</summary>

- Device id: `yageo_rc0402fr_07110kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-07110KL/729478).

</details>

<details><summary><code>Yageo RC0402FR-0712KL</code> — 2 × USD 0.0097 = USD 0.0194</summary>

- Device id: `yageo_rc0402fr_0712kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0712KL/729479).

</details>

<details><summary><code>Yageo RC0402FR-07169KL</code> — 5 × USD 0.0097 = USD 0.0485</summary>

- Device id: `yageo_rc0402fr_07169kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-07169KL/5280860).

</details>

<details><summary><code>Yageo RC0402FR-07196KL</code> — 1 × USD 0.0097 = USD 0.0097</summary>

- Device id: `yageo_rc0402fr_07196kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-07196KL/5281889).

</details>

<details><summary><code>Yageo RC0402FR-071K82L</code> — 2 × USD 0.0097 = USD 0.0194</summary>

- Device id: `yageo_rc0402fr_071k82l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-24`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-071K82L/729468).

</details>

<details><summary><code>Yageo RC0402FR-071KL</code> — 12 × USD 0.0097 = USD 0.1164</summary>

- Device id: `yageo_rc0402fr_071kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-071KL/726513).

</details>

<details><summary><code>Yageo RC0402FR-071ML</code> — 12 × USD 0.0097 = USD 0.1164</summary>

- Device id: `yageo_rc0402fr_071ml`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-071ML/729462).

</details>

<details><summary><code>Yageo RC0402FR-07220KL</code> — 11 × USD 0.0097 = USD 0.1067</summary>

- Device id: `yageo_rc0402fr_07220kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-07220KL/726564).

</details>

<details><summary><code>Yageo RC0402FR-07220RL</code> — 2 × USD 0.0097 = USD 0.0194</summary>

- Device id: `yageo_rc0402fr_07220rl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-07220RL/729512).

</details>

<details><summary><code>Yageo RC0402FR-07240KL</code> — 1 × USD 0.0009 = USD 0.0009</summary>

- Device id: `yageo_rc0402fr_07240kl`.
- Scope: `base_product`.
- Comparable basis: LCSC quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.lcsc.com/product-detail/Chip-Resistor-Surface-Mount_YAGEO-RC0402FR-07240KL_C138029.html).

</details>

<details><summary><code>Yageo RC0402FR-0730K1L</code> — 1 × USD 0.0097 = USD 0.0097</summary>

- Device id: `yageo_rc0402fr_0730k1l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0730K1L/726587).

</details>

<details><summary><code>Yageo RC0402FR-0730KL</code> — 2 × USD 0.0097 = USD 0.0194</summary>

- Device id: `yageo_rc0402fr_0730kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0730KL/726586).

</details>

<details><summary><code>Yageo RC0402FR-0733KL</code> — 1 × USD 0.0097 = USD 0.0097</summary>

- Device id: `yageo_rc0402fr_0733kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0733KL/726592).

</details>

<details><summary><code>Yageo RC0402FR-0733RL</code> — 1 × USD 0.0103 = USD 0.0103</summary>

- Device id: `yageo_rc0402fr_0733rl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-23`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0733RL/726593).

</details>

<details><summary><code>Yageo RC0402FR-073K32L</code> — 14 × USD 0.0097 = USD 0.1358</summary>

- Device id: `yageo_rc0402fr_073k32l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-073K32L/2827627).

</details>

<details><summary><code>Yageo RC0402FR-0742K2L</code> — 1 × USD 0.0049 = USD 0.0049</summary>

- Device id: `yageo_rc0402fr_0742k2l`.
- Scope: `base_product`.
- Comparable basis: LCSC quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.lcsc.com/product-detail/Others_YAGEO-RC0402FR-0742K2L_C276270.html).

</details>

<details><summary><code>Yageo RC0402FR-0744K2L</code> — 1 × USD 0.0052 = USD 0.0052</summary>

- Device id: `yageo_rc0402fr_0744k2l`.
- Scope: `base_product`.
- Comparable basis: LCSC quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.lcsc.com/product-image/C354260.html).

</details>

<details><summary><code>Yageo RC0402FR-0745K3L</code> — 1 × USD 0.0097 = USD 0.0097</summary>

- Device id: `yageo_rc0402fr_0745k3l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0745K3L/726613).

</details>

<details><summary><code>Yageo RC0402FR-07470RL</code> — 6 × USD 0.0097 = USD 0.0582</summary>

- Device id: `yageo_rc0402fr_07470rl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-07470RL/729566).

</details>

<details><summary><code>Yageo RC0402FR-0747KL</code> — 10 × USD 0.0097 = USD 0.0970</summary>

- Device id: `yageo_rc0402fr_0747kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0747KL/726616).

</details>

<details><summary><code>Yageo RC0402FR-0749R9L</code> — 5 × USD 0.0097 = USD 0.0485</summary>

- Device id: `yageo_rc0402fr_0749r9l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0749R9L/726621).

</details>

<details><summary><code>Yageo RC0402FR-074K7L</code> — 1 × USD 0.0097 = USD 0.0097</summary>

- Device id: `yageo_rc0402fr_074k7l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-074K7L/2827563).

</details>

<details><summary><code>Yageo RC0402FR-0752R3L</code> — 5 × USD 0.0097 = USD 0.0485</summary>

- Device id: `yageo_rc0402fr_0752r3l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0752R3L/5281040).

</details>

<details><summary><code>Yageo RC0402FR-0756KL</code> — 1 × USD 0.0097 = USD 0.0097</summary>

- Device id: `yageo_rc0402fr_0756kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0756KL/726635).

</details>

<details><summary><code>Yageo RC0402FR-075K1L</code> — 6 × USD 0.0103 = USD 0.0618</summary>

- Device id: `yageo_rc0402fr_075k1l`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-075K1L/726624).

</details>

<details><summary><code>Yageo RC0402FR-07620KL</code> — 1 × USD 0.0009 = USD 0.0009</summary>

- Device id: `yageo_rc0402fr_07620kl`.
- Scope: `base_product`.
- Comparable basis: LCSC quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_yageo-rc0402fr-07620kl_C137952.html).

</details>

<details><summary><code>Yageo RC0402FR-0768KL</code> — 4 × USD 0.0097 = USD 0.0388</summary>

- Device id: `yageo_rc0402fr_0768kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402FR-0768KL/729598).

</details>

<details><summary><code>Yageo RC0402JR-070RL</code> — 4 × USD 0.0048 = USD 0.0192</summary>

- Device id: `yageo_rc0402jr_070rl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0402JR-070RL/729353).

</details>

<details><summary><code>Yageo RC0603FR-071KL</code> — 4 × USD 0.0122 = USD 0.0488</summary>

- Device id: `yageo_rc0603fr_071kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RC0603FR-071KL/729790).

</details>

<details><summary><code>Yageo RT0402BRD07100KL</code> — 1 × USD 0.0646 = USD 0.0646</summary>

- Device id: `yageo_rt0402brd07100kl`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/yageo/RT0402BRD07100KL/5138791).

</details>

<details><summary><code>Yageo RT0402BRD07191KL</code> — 1 × USD 0.0820 = USD 0.0820</summary>

- Device id: `yageo_rt0402brd07191kl`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://br.mouser.com/ProductDetail/YAGEO/RT0402BRD07191KL?qs=k2KEx2DUIRTNCS4INNWkNA%3D%3D).

</details>

## Unpriced lines with explicit cost gates

These entries are intentionally excluded from the partial subtotal until a comparable quantity-100 USD quote exists.

<details><summary><code>M5Stack U214 Cap LoRa-1262</code> — <code>retail_only_no_quantity_100_tier</code></summary>

- Device id: `m5_u214`.
- Scope: `optional_external_accessory`; quantity `1`.
- Reason: The exact U214 is sold as a retail package at USD 14.50 with no published quantity-100 tier; a comparable production quantity quote is required instead of multiplying the retail price.
- Checked: `2026-08-22`; [gate source](https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/U214/29291633).

</details>

<details><summary><code>Murata GJM1555C1H101JB01D</code> — <code>quantity_100_rfq_required</code></summary>

- Device id: `murata_gjm1555c1h101jb01d`.
- Scope: `base_product`; quantity `2`.
- Reason: Current exact-MPN sourcing exposes request-for-quote inventory but no published comparable quantity-100 USD tier; an RF-qualified replacement cannot be promoted only to obtain a price.
- Checked: `2026-08-19`; [gate source](https://www.1sourcecomponents.com/availability/MURATA--GJM1555C1H101JB01D.htm).

</details>

<details><summary><code>Nexperia PESD24VY1BSF</code> — <code>quantity_100_rfq_required</code></summary>

- Device id: `nexperia_pesd24vy1bsf`.
- Scope: `base_product`; quantity `2`.
- Reason: No published comparable exact-Nexperia quantity-100 USD tier was found; the same base marking sold by ElecSuper is a different manufacturer and cannot be priced as the accepted Nexperia device.
- Checked: `2026-08-19`; [gate source](https://www.nexperia.com/product/PESD24VY1BSF).

</details>

<details><summary><code>G-NiceRF SA818S-U</code> — <code>quantity_100_rfq_required</code></summary>

- Device id: `nicerf_sa818s_u_v18`.
- Scope: `base_product`; quantity `1`.
- Reason: JLCPCB exposes the exact G-NiceRF PCBA line, but a durable comparable quantity-100 quote is not yet captured.
- Checked: `2026-08-26`; [gate source](https://jlcpcb.com/partdetail/GNiceRF-SA818SU/C3001549).

</details>

<details><summary><code>G-NiceRF SA818S-V</code> — <code>quantity_100_rfq_required</code></summary>

- Device id: `nicerf_sa818s_v_v18`.
- Scope: `base_product`; quantity `1`.
- Reason: The exact G-NiceRF SA818S-V line exists at JLCPCB but is pre-order and lacks a durable comparable quantity-100 quote.
- Checked: `2026-08-26`; [gate source](https://jlcpcb.com/partdetail/GNiceRF-SA818SV/C51897911).

</details>

<details><summary><code>Panasonic ERJ-P08F49R9V</code> — <code>quantity_100_rfq_required</code></summary>

- Device id: `panasonic_erj_p08f49r9v`.
- Scope: `base_product`; quantity `2`.
- Reason: The authorized-distributor exact-MPN page offers only a 5,000-piece full reel, while accessible quantity-100 reference prices require a broker RFQ; no comparable published authorized USD quantity-100 tier is available.
- Checked: `2026-08-19`; [gate source](https://www.digikey.com/en/products/detail/panasonic-industry/ERJ-P08F49R9V/9813007).

</details>

<details><summary><code>Sunlord MWSA0503S-3R3MT</code> — <code>quantity_100_rfq_required</code></summary>

- Device id: `sunlord_mwsa0503s_3r3mt`.
- Scope: `base_product`; quantity `2`.
- Reason: The exact assembly listing publishes only CNY tax-inclusive tiers while the USD cost contract forbids an unstated FX conversion; a same-currency quantity-100 quote is required.
- Checked: `2026-08-19`; [gate source](https://www.jlc-smt.com/lcsc/detail/C408409.html).

</details>

<details><summary><code>Texas Instruments TPUL2G223BQBR</code> — <code>quantity_100_rfq_required</code></summary>

- Device id: `ti_tpul2g223_bqbr`.
- Scope: `base_product`; quantity `1`.
- Reason: TI marks the exact new part active/production but the current order page shows no inventory or published quantity-100 price; obtain a traceable distributor or factory quotation before freezing COGS.
- Checked: `2026-08-19`; [gate source](https://www.ti.com/product/TPUL2G223/part-details/TPUL2G223BQBR).

</details>

<details><summary><code>XTAR 18650 4000mAh</code> — <code>regional_retail_only_no_quantity_100_tier</code></summary>

- Device id: `xtar_18650_4000mah_protected`.
- Scope: `regional_replaceable_cell_kit`; quantity `2`.
- Reason: The official store exposes regional retail pricing but no exact quantity-100 tier or production quote for the protected no-USB cell.
- Checked: `2026-08-19`; [gate source](https://xtardirect.com/products/xtar-high-capacity-36v-18650-4000mah-10a-protected-lithium-ion-battery).

</details>

## Assembly-internal evidence nodes excluded from purchase BOM

- `display_touch_controller` / `Sitronix ST77922` is contained by `display`: Sitronix ST77922 is a COG internal to HMX035CTFT-001; it remains a separate architecture/diagram evidence node but is not a separately supplied or costed BOM placement.

## Physical purchase families with explicit resolution gates

### `external_antenna_kit` — 12 item(s)

- Scope: `costed_product_variant`.
- Role: two native, three nRF, three CC, dedicated VHF and UHF voice, and two receiver antennas/pods.
- Blocking evidence: exact first targets and paper alternates are selected for all 12 physical items; AM/LW source independence, alternate qualification, assembled-device HIL and package-variant costing remain open.
- Gate: `profile_variant_bom_and_hil_required`.
- Owner stage: G3 physical design plus product-variant qualification before antenna-kit freeze.
- Evidence chain: `DEC-0055`, `ANT-0002`, `FND-0058`.
- Prerequisites:
  - freeze final external connector plane, target ground/counterpoise environment and the twelve-item profiled-kit packaging manifest.
  - retain the exact L2-ANT-AM-LW-001 controlled passive-pod design, its L2-ANT-AM-LW-ALT01 geometry fallback and fail-closed TX profile selection from DEC-0055.
- Acceptance:
  - name exact current orderable first-target and qualified-alternate MPNs for every antenna profile, with twelve physical kit items and no missing AM/LW identity.
  - pass assembled VNA, receive sensitivity, TX EIRP/harmonic, coexistence, mechanical and environmental HIL for every affected path/profile.
  - attach current availability, variant quantities, factory kitting instructions, quantity-100 cost and substitution disposition.

## Used lines without current orderability evidence

This is deliberately rendered as vertical cards so the document remains usable on a narrow screen.

## Non-MPN physical features

- ground and via fields.
- no-connects and fixed copper straps.
- protected test pads.
- reserved DNP footprints.

These need exact library/geometry and manufacturing rules, but must not be padded into component cost as fictitious purchased parts.

## I8 exit

every installed or supplied physical item has a scope, exact first target or explicit measured/received-item gate, current lifecycle/orderability evidence, cost snapshot and no-silent-substitution policy.

Until those conditions pass, the BOM has **not** received «Проведено ревью», no total COGS is claimed and PCB placement/routing, fabrication and purchasing remain unauthorized.
