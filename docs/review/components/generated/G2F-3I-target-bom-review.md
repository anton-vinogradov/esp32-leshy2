# G2F-3I — generated target BOM coverage review

- Статус: **I8 inventory complete; sourcing/cost/alternate review active**
- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/G2F-3I.json`
- Regenerate: `python3 hardware/architecture/generate.py --write`

> Файл сгенерирован. Он показывает полноту входа в I8, а не выдаёт незакрытые строки за factory quote.

## Что уже посчитано

- **816** machine-instantiated physical placements collapse to **187** used exact-device/MPN lines.
- Current orderability evidence exists for **153/187** used lines; **34** need a current source check.
- Machine-readable quantity-100 cost evidence exists for **0/187** lines.
- Machine-readable alternate/no-substitution evidence exists for **0/187** lines.
- Cost basis: USD quantity 100 component material only; PCB, assembly, test, enclosure, tax, freight, yield and tooling stay separate until factory RFQ.

Scopes: `base_product` — 813 placements; `optional_external_accessory` — 1 placements; `regional_replaceable_cell_kit` — 2 placements.

The complete per-line manifest is the adjacent `G2F-3I-target-bom.csv`; unused comparison-device definitions are deliberately excluded.

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

### `actual_tx_threshold_networks` — 8 item(s)

- Scope: `base_product`.
- Role: separate divider and hysteresis population for eight actual-TX comparators.
- Blocking evidence: first values and exact resistor placements must be machine-instantiated; production values remain measured calibration outputs.

### `external_antenna_kit` — 12 item(s)

- Scope: `costed_product_variant`.
- Role: two native, three nRF, three CC, two voice and two receiver antennas/pods.
- Blocking evidence: one first target exists for most profiles, but second-source, AM/LW pod and package-variant disposition remain open.

## Used lines without current orderability evidence

This is deliberately rendered as vertical cards so the document remains usable on a narrow screen.

<details><summary><code>LTC5532ES6#TRMPBF</code> — qty 2</summary>

- Device id: `adi_ltc5532_es6_trmpbf`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `production`
- Qualification: `verified_candidate`
- Placements: `det_c5`, `det_s3`

</details>

<details><summary><code>Alps Alpine EC11E18244AU</code> — qty 1</summary>

- Device id: `alps_ec11e18244au`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active_standard`
- Qualification: `verified_first_target_mechanical_fit_hil_open`
- Placements: `encoder`

</details>

<details><summary><code>CC1101RGPR</code> — qty 1</summary>

- Device id: `cc1101rgpr`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `cc`

</details>

<details><summary><code>Diodes Incorporated 2N7002DW-7-F</code> — qty 4</summary>

- Device id: `diodes_2n7002dw_7_f`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `pack_hold`, `pack_status_buffer`, `safe_reset_sink_a`, `safe_reset_sink_b`

</details>

<details><summary><code>Diodes Incorporated BAT54-7-F</code> — qty 4</summary>

- Device id: `diodes_bat54_7_f`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `cc_evidence_hold_diode`, `nrf_evidence_hold_diode`, `pack_system_diode`, `voice_evidence_hold_diode`

</details>

<details><summary><code>Diodes Incorporated PAM8302AASCR</code> — qty 1</summary>

- Device id: `diodes_pam8302a_ascr`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_reference`
- Placements: `speaker_amp`

</details>

<details><summary><code>Ebyte E01-ML01IPX</code> — qty 3</summary>

- Device id: `ebyte_e01_ml01ipx`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `nrf24_family_not_recommended_for_new_designs`
- Qualification: `verified_reference`
- Placements: `nrf0`, `nrf1`, `nrf2`

</details>

<details><summary><code>Seiko Epson Q13FC13500005</code> — qty 1</summary>

- Device id: `epson_q13fc13500005`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active_orderable`
- Qualification: `verified_candidate`
- Placements: `receiver_clock`

</details>

<details><summary><code>ESP32-C5-WROOM-1U-N8R8</code> — qty 1</summary>

- Device id: `esp32_c5_wroom_1u_n8r8`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active_candidate_revision_floor_v1_2`
- Qualification: `verified_candidate`
- Placements: `c5`

</details>

<details><summary><code>ESP32-S3-WROOM-1U-N16R2</code> — qty 1</summary>

- Device id: `esp32_s3_wroom_1u_n16r2`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `s3`

</details>

<details><summary><code>Everest Semiconductor ES8311</code> — qty 1</summary>

- Device id: `everest_es8311_qfn20`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `current manufacturer product brief revision 17.0 dated 2026-02; production sourcing and lot qualification remain open`
- Qualification: `verified_candidate`
- Placements: `codec`

</details>

<details><summary><code>LTST-C190KFKT</code> — qty 1</summary>

- Device id: `liteon_ltst_c190kfkt`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `stop_led`

</details>

<details><summary><code>LTST-C190KRKT</code> — qty 1</summary>

- Device id: `liteon_ltst_c190krkt`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `any_tx_led`

</details>

<details><summary><code>Littelfuse 0451005.MRL</code> — qty 2</summary>

- Device id: `littelfuse_0451005_mrl`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `pack_fuse0`, `pack_fuse1`

</details>

<details><summary><code>M5Stack U214 Cap LoRa-1262</code> — qty 1</summary>

- Device id: `m5_u214`
- Scope: `optional_external_accessory`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `u214`

</details>

<details><summary><code>Murata GRM1555C1H220JA01D</code> — qty 2</summary>

- Device id: `murata_grm1555c1h220ja01d`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active_orderable`
- Qualification: `verified_candidate`
- Placements: `receiver_clock_cap_gpo3`, `receiver_clock_cap_rclk`

</details>

<details><summary><code>74LVC1G32GV,125</code> — qty 3</summary>

- Device id: `nexperia_74lvc1g32gv_125`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `production`
- Qualification: `verified_candidate`
- Placements: `ext_request_or`, `safe_por_or`, `safe_ptt_or`

</details>

<details><summary><code>74LVC2G14GW,125</code> — qty 1</summary>

- Device id: `nexperia_74lvc2g14gw_125`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `production`
- Qualification: `verified_candidate`
- Placements: `safe_conditioner`

</details>

<details><summary><code>NiceRF SA518</code> — qty 1</summary>

- Device id: `nicerf_sa518_v11`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `current_product`
- Qualification: `verified_candidate`
- Placements: `voice`

</details>

<details><summary><code>onsemi 1N4148WT</code> — qty 10</summary>

- Device id: `onsemi_1n4148wt`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `ui_matrix_diode_back`, `ui_matrix_diode_down`, `ui_matrix_diode_encoder`, `ui_matrix_diode_f1`, `ui_matrix_diode_f2`, `ui_matrix_diode_left`, `ui_matrix_diode_ok`, `ui_matrix_diode_opt`, `ui_matrix_diode_right`, `ui_matrix_diode_up`

</details>

<details><summary><code>BAT54ALT1G</code> — qty 4</summary>

- Device id: `onsemi_bat54alt1g`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `evidence_or_0`, `evidence_or_1`, `evidence_or_2`, `evidence_or_3`

</details>

<details><summary><code>onsemi BAV70LT1G</code> — qty 1</summary>

- Device id: `onsemi_bav70lt1g`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `pack_supply_or`

</details>

<details><summary><code>HMX035CTFT-001 (QDtech schematic assembly marking)</code> — qty 1</summary>

- Device id: `qdtech_hmx035ctft_001`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified`
- Qualification: `verified_candidate`
- Placements: `display`

</details>

<details><summary><code>RP2354B A4 (exact A4 order/lot identity required before BOM freeze)</code> — qty 1</summary>

- Device id: `rp2354b_a4`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `rp`

</details>

<details><summary><code>TDK B57332V5103F360</code> — qty 3</summary>

- Device id: `tdk_b57332v5103f360`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `charger_ts_ntc`, `pack_ntc0`, `pack_ntc1`

</details>

<details><summary><code>SN74LVC08APWR</code> — qty 2</summary>

- Device id: `ti_sn74lvc08a_pwr`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `safe_gate_a`, `safe_gate_b`

</details>

<details><summary><code>SN74LVC1G07DCKR</code> — qty 5</summary>

- Device id: `ti_sn74lvc1g07_dckr`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_exact_open_drain_partial_power_buffer`
- Placements: `receiver_irq_iso`, `slow_io_s3_evidence_iso`, `slow_io_stop_sense_iso`, `touch_irq_buffer`, `voice_hl_driver`

</details>

<details><summary><code>SN74LVC1G74DCUR</code> — qty 1</summary>

- Device id: `ti_sn74lvc1g74_dcur`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `safe_latch`

</details>

<details><summary><code>SN74LVC3G34DCUR</code> — qty 1</summary>

- Device id: `ti_sn74lvc3g34_dcur`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `sd_host_buffer`

</details>

<details><summary><code>TLV1824PWR</code> — qty 2</summary>

- Device id: `ti_tlv1824_pwr`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `evidence_cmp_a`, `evidence_cmp_b`

</details>

<details><summary><code>TPS3808G33DBVR</code> — qty 4</summary>

- Device id: `ti_tps3808g33_dbvr`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `safe_supervisor`, `u214_supervisor`, `unit_supervisor`, `voice_supervisor`

</details>

<details><summary><code>Vishay WSL25125L000FEA</code> — qty 1</summary>

- Device id: `vishay_wsl25125l000fea`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active`
- Qualification: `verified_candidate`
- Placements: `pack_shunt`

</details>

<details><summary><code>Yageo RC0402FR-07220RL</code> — qty 1</summary>

- Device id: `yageo_rc0402fr_07220rl`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active_orderable`
- Qualification: `verified_candidate`
- Placements: `microphone_bias_filter_res`

</details>

<details><summary><code>Yageo RC0402JR-070RL</code> — qty 1</summary>

- Device id: `yageo_rc0402jr_070rl`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `active_orderable`
- Qualification: `verified_candidate`
- Placements: `audio_ground_link`

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
