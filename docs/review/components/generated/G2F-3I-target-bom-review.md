# G2F-3I — generated target BOM coverage review

- Статус: **I8 inventory complete; sourcing/cost/alternate review active**
- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/G2F-3I.json`
- Regenerate: `python3 hardware/architecture/generate.py --write`

> Файл сгенерирован. Он показывает полноту входа в I8, а не выдаёт незакрытые строки за factory quote.

## Что уже посчитано

- **858** architecture instances include **1** explicit assembly-internal evidence node.
- After excluding those non-purchase nodes, **857** supplied/costed placements collapse to **187** used exact-device/MPN lines.
- Current orderability evidence exists for **186/187** used lines; **1** need a current source check.
- Machine-readable quantity-100 cost evidence exists for **15/187** lines.
- Those priced lines cover **22/857** supplied placements; their partial subtotals are `base_product` — USD 57.2502. These are coverage diagnostics, not product COGS.
- Machine-readable alternate/no-substitution evidence exists for **187/187** lines.
- Cost basis: USD quantity 100 component material only; PCB, assembly, test, enclosure, tax, freight, yield and tooling stay separate until factory RFQ.

Scopes: `base_product` — 854 placements; `optional_external_accessory` — 1 placements; `regional_replaceable_cell_kit` — 2 placements.

The complete per-line manifest is the adjacent `G2F-3I-target-bom.csv`; unused comparison-device definitions are deliberately excluded.

## Substitution/no-silent-replacement policy

Every purchase line below belongs to exactly one validated class. A class is a disposition and requalification envelope, not a claim that a second MPN is already qualified.

<details><summary><code>SUB-RF</code> — RF, clock and frequency-selective parts — 28 line(s)</summary>

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
  - `murata_lqw15an56nj00d` — `Murata LQW15AN56NJ00D`.
  - `nexperia_pesd24vy1bsf` — `Nexperia PESD24VY1BSF`.
  - `ttm_b0310j50100ahf` — `TTM Technologies B0310J50100AHF`.
  - `ttm_dc2337j5010ahf` — `TTM Technologies DC2337J5010AHF`.
  - `yageo_rc0402fr_0749r9l` — `Yageo RC0402FR-0749R9L`.
  - `yageo_rc0402fr_0752r3l` — `Yageo RC0402FR-0752R3L`.
  - `yageo_rc0402fr_0756kl` — `Yageo RC0402FR-0756KL`.

</details>

<details><summary><code>SUB-PWR-PASSIVE</code> — Power conversion, decoupling and energy-storage passives — 16 line(s)</summary>

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
  - `tdk_c1005x7r1h104k050bb` — `TDK C1005X7R1H104K050BB`.
  - `tdk_c1608x7s2a104k080ab` — `TDK C1608X7S2A104K080AB`.
  - `tdk_cga5l1x7r1e475k160ac` — `TDK CGA5L1X7R1E475K160AC`.

</details>

<details><summary><code>SUB-CTRL-PASSIVE</code> — Control, timing, precision, protection-current and sensing passives — 56 line(s)</summary>

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
  - `vishay_wsl25125l000fea` — `Vishay WSL25125L000FEA`.
  - `yageo_rc0402fr_07100kl` — `Yageo RC0402FR-07100KL`.
  - `yageo_rc0402fr_07100rl` — `Yageo RC0402FR-07100RL`.
  - `yageo_rc0402fr_0710kl` — `Yageo RC0402FR-0710KL`.
  - `yageo_rc0402fr_07110kl` — `Yageo RC0402FR-07110KL`.
  - `yageo_rc0402fr_0712kl` — `Yageo RC0402FR-0712KL`.
  - `yageo_rc0402fr_07133kl` — `Yageo RC0402FR-07133KL`.
  - `yageo_rc0402fr_07169kl` — `Yageo RC0402FR-07169KL`.
  - `yageo_rc0402fr_07196kl` — `Yageo RC0402FR-07196KL`.
  - `yageo_rc0402fr_071k65l` — `Yageo RC0402FR-071K65L`.
  - `yageo_rc0402fr_071kl` — `Yageo RC0402FR-071KL`.
  - `yageo_rc0402fr_071ml` — `Yageo RC0402FR-071ML`.
  - `yageo_rc0402fr_07220kl` — `Yageo RC0402FR-07220KL`.
  - `yageo_rc0402fr_07220rl` — `Yageo RC0402FR-07220RL`.
  - `yageo_rc0402fr_07240kl` — `Yageo RC0402FR-07240KL`.
  - `yageo_rc0402fr_07270kl` — `Yageo RC0402FR-07270KL`.
  - `yageo_rc0402fr_072k21l` — `Yageo RC0402FR-072K21L`.
  - `yageo_rc0402fr_072k2l` — `Yageo RC0402FR-072K2L`.
  - `yageo_rc0402fr_0730k1l` — `Yageo RC0402FR-0730K1L`.
  - `yageo_rc0402fr_0730kl` — `Yageo RC0402FR-0730KL`.
  - `yageo_rc0402fr_0733kl` — `Yageo RC0402FR-0733KL`.
  - `yageo_rc0402fr_073k32l` — `Yageo RC0402FR-073K32L`.
  - `yageo_rc0402fr_0742k2l` — `Yageo RC0402FR-0742K2L`.
  - `yageo_rc0402fr_0744k2l` — `Yageo RC0402FR-0744K2L`.
  - `yageo_rc0402fr_0745k3l` — `Yageo RC0402FR-0745K3L`.
  - `yageo_rc0402fr_07470rl` — `Yageo RC0402FR-07470RL`.
  - `yageo_rc0402fr_0747kl` — `Yageo RC0402FR-0747KL`.
  - `yageo_rc0402fr_074k7l` — `Yageo RC0402FR-074K7L`.
  - `yageo_rc0402fr_075k1l` — `Yageo RC0402FR-075K1L`.
  - `yageo_rc0402fr_075k23l` — `Yageo RC0402FR-075K23L`.
  - `yageo_rc0402fr_07620kl` — `Yageo RC0402FR-07620KL`.
  - `yageo_rc0402fr_0768kl` — `Yageo RC0402FR-0768KL`.
  - `yageo_rc0402fr_078k2l` — `Yageo RC0402FR-078K2L`.
  - `yageo_rc0402jr_070rl` — `Yageo RC0402JR-070RL`.
  - `yageo_rc0603fr_071kl` — `Yageo RC0603FR-071KL`.
  - `yageo_rc1206fr_0733rl` — `Yageo RC1206FR-0733RL`.
  - `yageo_rt0402brd07100kl` — `Yageo RT0402BRD07100KL`.
  - `yageo_rt0402brd07191kl` — `Yageo RT0402BRD07191KL`.

</details>

<details><summary><code>SUB-DISCRETE-PROT</code> — Discrete switching, indication and signal-protection semiconductors — 13 line(s)</summary>

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
  - `onsemi_1n4148wt` — `onsemi 1N4148WT`.
  - `onsemi_bat54alt1g` — `BAT54ALT1G`.
  - `onsemi_bav70lt1g` — `onsemi BAV70LT1G`.
  - `ti_tpd2eusb30a_drtr` — `Texas Instruments TPD2EUSB30ADRTR`.
  - `ti_tpd4e05u06_dqar` — `Texas Instruments TPD4E05U06DQAR`.
  - `ti_tpd4s201_rukr` — `Texas Instruments TPD4S201RUKR`.
  - `ti_tpd8e003_dqdr` — `Texas Instruments TPD8E003DQDR`.

</details>

<details><summary><code>SUB-LOGIC-ANALOG</code> — Logic, interface, audio and analog signal ICs — 26 line(s)</summary>

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
  - `diodes_pam8302a_ascr` — `Diodes Incorporated PAM8302AASCR`.
  - `everest_es8311_qfn20` — `Everest Semiconductor ES8311`.
  - `nexperia_74lvc126apw_118` — `Nexperia 74LVC126APW,118`.
  - `nexperia_74lvc1g32gv_125` — `74LVC1G32GV,125`.
  - `nexperia_74lvc2g126dc_125` — `Nexperia 74LVC2G126DC,125`.
  - `nexperia_74lvc2g14gw_125` — `74LVC2G14GW,125`.
  - `onsemi_fsusb42_mux` — `onsemi FSUSB42MUX`.
  - `tca4307dgkr` — `TCA4307DGKR`.
  - `tca6424argjr` — `TCA6424ARGJR`.
  - `ti_sn74lvc08a_pwr` — `SN74LVC08APWR`.
  - `ti_sn74lvc1g06_dckr` — `Texas Instruments SN74LVC1G06DCKR`.
  - `ti_sn74lvc1g07_dckr` — `SN74LVC1G07DCKR`.
  - `ti_sn74lvc1g125_dckr` — `Texas Instruments SN74LVC1G125DCKR`.
  - `ti_sn74lvc1g126_dckr` — `Texas Instruments SN74LVC1G126DCKR`.
  - `ti_sn74lvc1g3157_dbvr` — `Texas Instruments SN74LVC1G3157DBVR`.
  - `ti_sn74lvc1g74_dcur` — `SN74LVC1G74DCUR`.
  - `ti_sn74lvc2g08_dcur` — `Texas Instruments SN74LVC2G08DCUR`.
  - `ti_sn74lvc2g66_dcur` — `Texas Instruments SN74LVC2G66DCUR`.
  - `ti_sn74lvc3g07_dcur` — `SN74LVC3G07DCUR`.
  - `ti_sn74lvc3g34_dcur` — `SN74LVC3G34DCUR`.
  - `ti_tca9534a_pwr` — `TCA9534APWR`.
  - `ti_tlv1824_pwr` — `TLV1824PWR`.
  - `ti_tlv9061_idbvr` — `Texas Instruments TLV9061IDBVR`.
  - `ti_tmux1136_dgsr` — `Texas Instruments TMUX1136DGSR`.
  - `ti_ts5a63157_dckr` — `Texas Instruments TS5A63157DCKR`.
  - `ti_txs0102_dcur` — `Texas Instruments TXS0102DCUR`.

</details>

<details><summary><code>SUB-PWR-SAFETY</code> — Power, charging, admission and safety-control ICs — 17 line(s)</summary>

- Disposition: architecture-locked first target; substitute only by reopening and requalifying the complete safety/power subblock.
- Equivalence envelope:
  - same package/contact map and autonomous reset/fail-safe state.
  - limits, accuracy, protection coverage, gate drive, current/thermal capability, quiescent current, telemetry and fault latching no worse.
  - configuration memory/firmware image and independent recovery remain supported.
- Required requalification:
  - complete paper safety analysis and worst-case power calculations.
  - startup/source-transition/load-step/short/thermal/brownout/recovery HIL.
  - controlled destructive single-fault verification where the owning contract requires it.
- Current lines:
  - `adi_max17320_g20_t` — `Analog Devices MAX17320G20+T`.
  - `onsemi_cat24c512wi_gt3` — `onsemi CAT24C512WI-GT3`.
  - `ti_bq25798_rqmr` — `Texas Instruments BQ25798RQMR`.
  - `ti_csd87313dmst` — `Texas Instruments CSD87313DMST`.
  - `ti_mspm0c1104_sdgs20r` — `Texas Instruments MSPM0C1104SDGS20R`.
  - `ti_tps22919_dckr` — `Texas Instruments TPS22919DCKR`.
  - `ti_tps2553drvr_1` — `Texas Instruments TPS2553DRVR-1`.
  - `ti_tps25751d_refr` — `Texas Instruments TPS25751DREFR`.
  - `ti_tps259470l_rpwr` — `Texas Instruments TPS259470LRPWR`.
  - `ti_tps25961_drvr` — `Texas Instruments TPS25961DRVR`.
  - `ti_tps25974l_rpwr` — `Texas Instruments TPS25974LRPWR`.
  - `ti_tps3808g33_dbvr` — `TPS3808G33DBVR`.
  - `ti_tps3839k33_dbzr` — `Texas Instruments TPS3839K33DBZR`.
  - `ti_tps564252_drlr` — `Texas Instruments TPS564252DRLR`.
  - `ti_tps629203_drlr` — `Texas Instruments TPS629203DRLR`.
  - `ti_tpul2g223_bqbr` — `Texas Instruments TPUL2G223BQBR`.
  - `ti_tvs2200_drvr` — `Texas Instruments TVS2200DRVR`.

</details>

<details><summary><code>SUB-COMPUTE-RF</code> — Compute, radio modules and active RF/IR endpoints — 15 line(s)</summary>

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
  - `ebyte_e01_ml01ipx` — `Ebyte E01-ML01IPX`.
  - `esp32_c5_wroom_1u_n8r8` — `ESP32-C5-WROOM-1U-N8R8`.
  - `esp32_s3_wroom_1u_n16r2` — `ESP32-S3-WROOM-1U-N16R2`.
  - `infineon_bgs13sn8e6327xtsa1` — `Infineon BGS13SN8E6327XTSA1`.
  - `m5_u214` — `M5Stack U214 Cap LoRa-1262`.
  - `nicerf_sa518_v11` — `NiceRF SA518`.
  - `rp2354b_a4` — `SC1512-A4`.
  - `skyworks_si4732_a10_gsr` — `Si4732-A10-GSR`.
  - `vishay_tsmp95000tt` — `Vishay TSMP95000TT`.
  - `vishay_tsop95238tt` — `Vishay TSOP95238TT`.
  - `vishay_vemd1060x01` — `VEMD1060X01`.
  - `vishay_vsmy14940` — `Vishay VSMY14940`.

</details>

<details><summary><code>SUB-MECH-OPTICAL</code> — Display, cells, connectors, controls and electro-acoustic/mechanical parts — 16 line(s)</summary>

- Disposition: no drop-in by nominal description; exact mate, outline, human factors and environmental qualification required.
- Equivalence envelope:
  - same mating standard/contact map/polarity plus compatible footprint, keepout, insertion, retention and service access.
  - display optics/touch/backlight, cell protection/chemistry, switch force/travel/current and transducer acoustic response no worse.
  - sealing, strain, temperature, life and manufacturing process remain compatible.
- Required requalification:
  - received-sample dimensional/fit and assembly coupon.
  - contact/current/ESD/wear/drop/vibration/environmental HIL as applicable.
  - display, battery, UI and acoustic acceptance tests for the owning product scenario.
- Current lines:
  - `alps_ec11e18244au` — `Alps Alpine EC11E18244AU`.
  - `alps_skqgade010` — `Alps Alpine SKQGADE010`.
  - `ck_y78b23214fp` — `C&K Y78B23214FP`.
  - `gct_usb4105_gf_a` — `GCT USB4105-GF-A`.
  - `hirose_dm3at_sf_pejm5` — `Hirose DM3AT-SF-PEJM5`.
  - `hirose_fh12_40s_0_5sh_55` — `Hirose FH12-40S-0.5SH(55)`.
  - `hirose_ufl_r_smt_1_10` — `Hirose U.FL-R-SMT-1(10)`.
  - `jae_dx07s016ja1r1500` — `JAE DX07S016JA1R1500`.
  - `keystone_1048p` — `Keystone Electronics 1048P`.
  - `panasonic_aeq10410` — `Panasonic AEQ10410`.
  - `pui_as02404po` — `PUI Audio AS02404PO`.
  - `qdtech_hmx035ctft_001` — `HMX035CTFT-001 (QDtech schematic assembly marking)`.
  - `same_sky_cmej_0413_42_smt_tr` — `Same Sky CMEJ-0413-42-SMT-TR`.
  - `same_sky_sj1_3515_smt_tr` — `Same Sky SJ1-3515-SMT-TR`.
  - `samtec_ftsh_105_01_l_dv_k_p_tr` — `Samtec FTSH-105-01-L-DV-K-P-TR`.
  - `xtar_18650_4000mah_protected` — `XTAR 18650 4000mAh`.

</details>

## Quantity-100 cost evidence

Only exact-MPN published USD prices that apply to a 100-piece purchase are listed. Taxes, tariffs, freight, PCB, assembly, test, enclosure, yield and tooling are excluded. The sum below is intentionally partial while any purchase line remains unpriced.

<details><summary><code>Analog Devices AD8314ACPZ-RL7</code> — 5 × USD 2.8570 = USD 14.2850</summary>

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

<details><summary><code>CC1101RGPR</code> — 1 × USD 3.0358 = USD 3.0358</summary>

- Device id: `cc1101rgpr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/CC1101RGPR/3947323).

</details>

<details><summary><code>ESP32-C5-WROOM-1U-N8R8</code> — 1 × USD 4.3700 = USD 4.3700</summary>

- Device id: `esp32_c5_wroom_1u_n8r8`.
- Scope: `base_product`.
- Comparable basis: Mouser cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/en/ProductDetail/Espressif-Systems/ESP32-C5-WROOM-1U-N8R8?qs=4dK74SdgGtxee18dMuslog%3D%3D).

</details>

<details><summary><code>ESP32-S3-WROOM-1U-N16R2</code> — 1 × USD 4.7741 = USD 4.7741</summary>

- Device id: `esp32_s3_wroom_1u_n16r2`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-S3-WROOM-1U-N16R2/16162650).

</details>

<details><summary><code>GCT USB4105-GF-A</code> — 2 × USD 0.5745 = USD 1.1490</summary>

- Device id: `gct_usb4105_gf_a`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/gct/USB4105-GF-A/11198510).

</details>

<details><summary><code>Hirose DM3AT-SF-PEJM5</code> — 1 × USD 2.5656 = USD 2.5656</summary>

- Device id: `hirose_dm3at_sf_pejm5`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DM3AT-SF-PEJM5/2533565).

</details>

<details><summary><code>Hirose FH12-40S-0.5SH(55)</code> — 1 × USD 2.2948 = USD 2.2948</summary>

- Device id: `hirose_fh12_40s_0_5sh_55`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/FH12-40S-0-5SH-55/1110328).

</details>

<details><summary><code>Hirose U.FL-R-SMT-1(10)</code> — 2 × USD 1.0655 = USD 2.1310</summary>

- Device id: `hirose_ufl_r_smt_1_10`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/U-FL-R-SMT-1-10/2391570).

</details>

<details><summary><code>JAE DX07S016JA1R1500</code> — 1 × USD 1.2272 = USD 1.2272</summary>

- Device id: `jae_dx07s016ja1r1500`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/jae-electronics/DX07S016JA1R1500/11585731).

</details>

<details><summary><code>SC1512-A4</code> — 1 × USD 1.0000 = USD 1.0000</summary>

- Device id: `rp2354b_a4`.
- Scope: `base_product`.
- Comparable basis: Mouser published 1+ cut-tape unit price applied to an order of 100 pieces; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.mouser.com/en/ProductDetail/Raspberry-Pi/SC1512-A4?qs=4dK74SdgGtwLCXnn6CRJZQ%3D%3D).

</details>

<details><summary><code>Texas Instruments BQ25798RQMR</code> — 1 × USD 3.5140 = USD 3.5140</summary>

- Device id: `ti_bq25798_rqmr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/BQ25798RQMR/15666783).

</details>

<details><summary><code>Texas Instruments TPS25751DREFR</code> — 1 × USD 1.8384 = USD 1.8384</summary>

- Device id: `ti_tps25751d_refr`.
- Scope: `base_product`.
- Comparable basis: DigiKey cut-tape quantity-100 tier; target quantity `100`.
- Checked: `2026-08-19`; [published source](https://www.digikey.com/en/products/detail/texas-instruments/TPS25751DREFR/23028775).

</details>

## Assembly-internal evidence nodes excluded from purchase BOM

- `display_touch_controller` / `Sitronix ST77922` is contained by `display`: Sitronix ST77922 is a COG internal to HMX035CTFT-001; it remains a separate architecture/diagram evidence node but is not a separately supplied or costed BOM placement.

## Physical items not yet instantiated

### `external_sma_bodies` — 9 item(s)

- Scope: `base_product`.
- Role: two RP-SMA and seven standard-SMA external RF connector bodies.
- Blocking evidence: exact attachment style and MPN depend on the physical connector plane; polarity and radio ownership are already fixed.

### `rf_cable_assemblies` — 5 item(s)

- Scope: `base_product`.
- Role: two native-radio double-ended microcoax jumpers and three nRF module-to-coupler pigtails.
- Blocking evidence: exact mating family, length and strain relief require received-module microscopy and internal placement.

### `m5_connector_bodies` — 2 item(s)

- Scope: `base_product`.
- Role: rear Cap-Bus receptacle and native HY2.0-4P Unit receptacle.
- Blocking evidence: manufacturer order codes are not published; received U214/cable mate and retention coupon are required.

### `external_antenna_kit` — 12 item(s)

- Scope: `costed_product_variant`.
- Role: two native, three nRF, three CC, two voice and two receiver antennas/pods.
- Blocking evidence: one first target exists for most profiles, but second-source, AM/LW pod and package-variant disposition remain open.

## Used lines without current orderability evidence

This is deliberately rendered as vertical cards so the document remains usable on a narrow screen.

<details><summary><code>HMX035CTFT-001 (QDtech schematic assembly marking)</code> — qty 1</summary>

- Device id: `qdtech_hmx035ctft_001`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified`
- Qualification: `verified_candidate`
- Placements: `display`

</details>

## Non-MPN physical features

- ground and via fields.
- no-connects and fixed copper straps.
- protected test pads.
- reserved DNP footprints.

These need exact library/geometry and manufacturing rules, but must not be padded into component cost as fictitious purchased parts.

## I8 exit

every installed or supplied physical item has a scope, exact first target or explicit measured/received-item gate, current lifecycle/orderability evidence, cost snapshot and no-silent-substitution policy.

Until those conditions pass, the BOM has **not** received «Проведено ревью», no total COGS is claimed and KiCad remains unauthorized.
