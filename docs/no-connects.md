# Leshy2 intentional no-connect register

[Русский](no-connects.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

This is the complete H2.6.2 physical NC register. Every row is checked against its symbol, exact contact and KiCad NC marker; no generic reserve rationale is accepted.

| Sheet | Contact | Physical pin | Rationale |
|---|---|---:|---|
| `ADP_00_DISPLAY_ADAPTER` | `display_panel_connector.FITTING_1` | `MP1` | mechanical hold-down contact has no electrical function |
| `ADP_00_DISPLAY_ADAPTER` | `display_panel_connector.FITTING_2` | `MP2` | mechanical hold-down contact has no electrical function |
| `CAP_00_ROOT` | `cap_header.PIN_1` | `1` | stock U214 GNSS UART contact is deliberately unused by the radio-only Leshy Cap |
| `CAP_00_ROOT` | `cap_header.PIN_2` | `2` | stock U214 GNSS UART contact is deliberately unused by the radio-only Leshy Cap |
| `CAP_10_RADIO_CONTROL` | `rf_detector.FLTR` | `4` | optional detector filter pin is left open for the selected fast envelope response |
| `CAP_10_RADIO_CONTROL` | `rf_detector.V_DN` | `7` | optional detector output-divider pin is unused for the selected full-scale output |
| `CAP_10_RADIO_CONTROL` | `variant_module.DIO3_TCXO` | `11` | the selected module owns TCXO control internally; the host leaves DIO3 open |
| `CAP_10_RADIO_CONTROL` | `variant_module.NC_12` | `12` | manufacturer NC module pad remains open |
| `CAP_10_RADIO_CONTROL` | `variant_module.NC_14` | `14` | manufacturer NC module pad remains open |
| `CAP_10_RADIO_CONTROL` | `variant_module.NC_7` | `7` | manufacturer NC module pad remains open |
| `CAP_20_POWER_BUS` | `identity.NC` | `5` | manufacturer NC package pad remains open |
| `CAP_20_POWER_BUS` | `local_regulator.NC` | `4` | manufacturer NC package pad remains open |
| `CAP_30_TX_EVIDENCE` | `evidence_driver.NC` | `1` | manufacturer NC pad of the open-drain evidence driver remains open |
| `RF_01_USB_PD_CHARGE` | `nvdc_charger.D_MINUS` | `7` | BQ DPDM detection is disabled and isolated from the protected native S3 USB2 data pair |
| `RF_01_USB_PD_CHARGE` | `nvdc_charger.D_PLUS` | `6` | BQ DPDM detection is disabled and isolated from the protected native S3 USB2 data pair |
| `RF_01_USB_PD_CHARGE` | `nvdc_charger.QON` | `12` | QON uses its specified internal pull-up; no external system-reset or ship-FET function is claimed |
| `RF_01_USB_PD_CHARGE` | `nvdc_charger.STAT` | `1` | unused open-drain STAT is disabled in the charger image; status and faults use INT/I2C |
| `RF_01_USB_PD_CHARGE` | `product_usb_connector.A8_SBU1` | `A8` | the base product implements no Type-C Alt Mode or SBU accessory path |
| `RF_01_USB_PD_CHARGE` | `product_usb_connector.B8_SBU2` | `B8` | the base product implements no Type-C Alt Mode or SBU accessory path |
| `RF_01_USB_PD_CHARGE` | `product_usb_protector.NC_16` | `16` | datasheet NC remains physically unconnected |
| `RF_01_USB_PD_CHARGE` | `product_usb_protector.NC_17` | `17` | datasheet NC remains physically unconnected |
| `RF_01_USB_PD_CHARGE` | `product_usb_protector.NC_19` | `19` | datasheet NC remains physically unconnected |
| `RF_01_USB_PD_CHARGE` | `product_usb_protector.NC_20` | `20` | datasheet NC remains physically unconnected |
| `RF_02_PACK_SAFETY_AON` | `pack_admission.PA27` | `2` | unused physical DGS20 pin 2 is intentionally open and remains recorded as free GPIO |
| `RF_02_PACK_SAFETY_AON` | `pack_admission.PA30` | `3` | unused physical DGS20 pin 3 is intentionally open and remains recorded as free GPIO |
| `RF_02_PACK_SAFETY_AON` | `pack_diag_timer.CH1_Q_N` | `4` | unused push-pull complementary channel-1 output is left open as required |
| `RF_02_PACK_SAFETY_AON` | `pack_diag_timer.CH2_Q` | `5` | unused push-pull active-high channel-2 output is left open as required |
| `RF_02_PACK_SAFETY_AON` | `pack_gauge.ZVC` | `5` | The product does not implement in-device zero-volt recovery; the datasheet requires ZVC open when unused |
| `RF_02_PACK_SAFETY_AON` | `pack_system_diode.NC` | `2` | the BAT54 SOT-23 center pin is physically not connected and remains explicitly open |
| `RF_03_MAIN_RAILS_DOMAIN_GATES` | `aon_buck.FB_VSET` | `1` | FB/VSET is deliberately left open; the datasheet decodes open or at least 249 kOhm as fixed 3.3 V |
| `RF_03_MAIN_RAILS_DOMAIN_GATES` | `ext_efuse.AUXOFF` | `3` | unused TPS259470 open-drain auxiliary-output contact is left open; it must never be shorted to ground |
| `RF_03_MAIN_RAILS_DOMAIN_GATES` | `ext_evidence_buffer.NC` | `1` | datasheet no-connect remains open |
| `RF_30_RP2354_CORE_SERVICE` | `rp.QSPI_SCLK` | `71` | stacked-flash clock remains package-visible but no secondary external flash is populated |
| `RF_30_RP2354_CORE_SERVICE` | `rp.QSPI_SD0` | `72` | stacked-flash bus remains package-visible but no secondary external flash is populated |
| `RF_30_RP2354_CORE_SERVICE` | `rp.QSPI_SD1` | `74` | stacked-flash bus remains package-visible but no secondary external flash is populated |
| `RF_30_RP2354_CORE_SERVICE` | `rp.QSPI_SD2` | `73` | stacked-flash bus remains package-visible but no secondary external flash is populated |
| `RF_30_RP2354_CORE_SERVICE` | `rp.QSPI_SD3` | `70` | stacked-flash bus remains package-visible but no secondary external flash is populated |
| `RF_30_RP2354_CORE_SERVICE` | `rp_dbg_esd.NC_10` | `10` | manufacturer NC remains open |
| `RF_30_RP2354_CORE_SERVICE` | `rp_dbg_esd.NC_6` | `6` | manufacturer NC remains open |
| `RF_30_RP2354_CORE_SERVICE` | `rp_dbg_esd.NC_7` | `7` | manufacturer NC remains open |
| `RF_30_RP2354_CORE_SERVICE` | `rp_dbg_esd.NC_9` | `9` | manufacturer NC remains open |
| `RF_30_RP2354_CORE_SERVICE` | `rp_service_usb_connector.A8_SBU1` | `A8` | service port implements no Alt Mode |
| `RF_30_RP2354_CORE_SERVICE` | `rp_service_usb_connector.B8_SBU2` | `B8` | service port implements no Alt Mode |
| `RF_30_RP2354_CORE_SERVICE` | `rp_service_usb_switch.HSD2_MINUS` | `8` | no hidden second data destination |
| `RF_30_RP2354_CORE_SERVICE` | `rp_service_usb_switch.HSD2_PLUS` | `9` | no hidden second data destination |
| `RF_31_NRF24_X3` | `nrf_evidence_hold_diode.NC` | `2` | manufacturer no-connect remains open |
| `RF_31_NRF24_X3` | `nrf_power_switch.NC` | `4` | SC70 pin 4 is left floating as required |
| `RF_32_SUBGHZ_VOICE` | `cc_balun.DNC_5` | `5` | datasheet do-not-connect contact remains isolated |
| `RF_32_SUBGHZ_VOICE` | `cc_balun.DNC_6` | `6` | datasheet do-not-connect contact remains isolated |
| `RF_32_SUBGHZ_VOICE` | `cc_host_buffer.4Y` | `11` | disabled spare output is unconnected |
| `RF_32_SUBGHZ_VOICE` | `cc_power_switch.NC` | `4` | SC70 pin 4 is left floating as required |
| `RF_32_SUBGHZ_VOICE` | `cc_return_buffer.4Y` | `11` | disabled spare output is unconnected |
| `RF_32_SUBGHZ_VOICE` | `voice.NC_11` | `11` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice.NC_13` | `13` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice.NC_14` | `14` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice.NC_15` | `15` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice.NC_2` | `2` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice.NC_4` | `4` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_band_inverter.2Y` | `4` | unused inverter output remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_hl_driver.NC` | `1` | SC70 no-connect remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_io_power_switch.NC` | `4` | TPS22919 physical pin 4 remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_v.NC_11` | `11` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_v.NC_13` | `13` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_v.NC_14` | `14` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_v.NC_15` | `15` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_v.NC_2` | `2` | manufacturer reserved contact remains open |
| `RF_32_SUBGHZ_VOICE` | `voice_v.NC_4` | `4` | manufacturer reserved contact remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_a.NC_10` | `10` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_a.NC_6` | `6` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_a.NC_7` | `7` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_a.NC_9` | `9` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_b.NC_10` | `10` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_b.NC_6` | `6` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_b.NC_7` | `7` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_b.NC_9` | `9` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_c.NC_10` | `10` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_c.NC_6` | `6` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_c.NC_7` | `7` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_esd_c.NC_9` | `9` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `u214_host_buffer_b.2Y` | `6` | disabled output unconnected |
| `RF_34_U214_M5_EXT` | `u214_host_buffer_b.3Y` | `8` | disabled output unconnected |
| `RF_34_U214_M5_EXT` | `u214_host_buffer_b.4Y` | `11` | disabled output unconnected |
| `RF_34_U214_M5_EXT` | `unit_efuse.AUXOFF` | `3` | unused TPS259470 open-drain auxiliary-output contact is left open; it must never be shorted to ground |
| `RF_34_U214_M5_EXT` | `unit_esd.D2_MINUS` | `5` | unused ESD channel is not tied to a connector contact |
| `RF_34_U214_M5_EXT` | `unit_esd.D2_PLUS` | `4` | unused ESD channel is not tied to a connector contact |
| `RF_34_U214_M5_EXT` | `unit_esd.NC_10` | `10` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `unit_esd.NC_6` | `6` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `unit_esd.NC_7` | `7` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_34_U214_M5_EXT` | `unit_esd.NC_9` | `9` | manufacturer NC pad of the fitted ESD protector remains open |
| `RF_35_REAR_CONTROLS` | `encoder_ptt_esd.D2_MINUS` | `5` | fourth ESD signal channel is intentionally unused |
| `RF_35_REAR_CONTROLS` | `encoder_ptt_esd.NC_10` | `10` | manufacturer no-connect remains open |
| `RF_35_REAR_CONTROLS` | `encoder_ptt_esd.NC_6` | `6` | manufacturer no-connect remains open |
| `RF_35_REAR_CONTROLS` | `encoder_ptt_esd.NC_7` | `7` | manufacturer no-connect remains open |
| `RF_35_REAR_CONTROLS` | `encoder_ptt_esd.NC_9` | `9` | manufacturer no-connect remains open |
| `RF_35_REAR_CONTROLS` | `rear_control_esd.D1_MINUS` | `2` | second rear-control ESD channel is intentionally unused |
| `RF_35_REAR_CONTROLS` | `rear_control_esd.D2_MINUS` | `5` | fourth rear-control ESD channel is intentionally unused |
| `RF_35_REAR_CONTROLS` | `rear_control_esd.D2_PLUS` | `4` | third rear-control ESD channel is intentionally unused |
| `RF_35_REAR_CONTROLS` | `rear_control_esd.NC_10` | `10` | manufacturer no-connect remains open |
| `RF_35_REAR_CONTROLS` | `rear_control_esd.NC_6` | `6` | manufacturer no-connect remains open |
| `RF_35_REAR_CONTROLS` | `rear_control_esd.NC_7` | `7` | manufacturer no-connect remains open |
| `RF_35_REAR_CONTROLS` | `rear_control_esd.NC_9` | `9` | manufacturer no-connect remains open |
| `RF_36_AUDIO_IO_AMP` | `speaker_amp.NC` | `2` | U-DFN physical pin 2 remains open; the unnumbered central thermal pad remains electrically unassigned per the manufacturer drawing |
| `RF_50_TX_SAFETY_EVIDENCE` | `cc_evidence_hold_diode.NC` | `2` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `det_cc.V_DN` | `7` | unused controller output remains unconnected |
| `RF_50_TX_SAFETY_EVIDENCE` | `det_nrf0.V_DN` | `7` | controller-mode falling output is intentionally unused |
| `RF_50_TX_SAFETY_EVIDENCE` | `det_nrf1.V_DN` | `7` | controller-mode falling output is intentionally unused |
| `RF_50_TX_SAFETY_EVIDENCE` | `det_nrf2.V_DN` | `7` | controller-mode falling output is intentionally unused |
| `RF_50_TX_SAFETY_EVIDENCE` | `det_voice.V_DN` | `7` | unused controller output remains unconnected |
| `RF_50_TX_SAFETY_EVIDENCE` | `det_voice_v.V_DN` | `7` | unused VHF detector controller output remains unconnected |
| `RF_50_TX_SAFETY_EVIDENCE` | `evidence_or_4.K2` | `2` | unused second cathode remains open and cannot create a false source |
| `RF_50_TX_SAFETY_EVIDENCE` | `safe_rearm_buffer.NC` | `2` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safe_reset_buffer.NC` | `1` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safe_reset_sink_b.D2` | `1` | unused fourth FET drain remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safe_run_fault_iso.NC` | `1` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safe_supervisor.CT` | `4` | open CT selects the documented fixed reset delay; the open contact is explicit rather than omitted |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_control_esd.D1_MINUS` | `2` | unused safety-domain ESD channel remains unconnected |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_control_esd.D2_MINUS` | `5` | unused safety-domain ESD channel remains unconnected |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_control_esd.D2_PLUS` | `4` | unused safety-domain ESD channel remains unconnected |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_control_esd.NC_10` | `10` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_control_esd.NC_6` | `6` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_control_esd.NC_7` | `7` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_control_esd.NC_9` | `9` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_fault_request_iso.NC` | `1` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `safety_s3_reset_iso.NC` | `1` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `voice_evidence_hold_diode.NC` | `2` | manufacturer no-connect remains open |
| `RF_50_TX_SAFETY_EVIDENCE` | `voice_v_evidence_hold_diode.NC` | `2` | manufacturer no-connect remains open |
| `UI_10_S3_CORE_MEMORY_BOOT` | `s3.NC_PSRAM_GPIO35` | `28` | N16R8 octal PSRAM consumes this package-visible carrier pad internally |
| `UI_10_S3_CORE_MEMORY_BOOT` | `s3.NC_PSRAM_GPIO36` | `29` | N16R8 octal PSRAM consumes this package-visible carrier pad internally |
| `UI_10_S3_CORE_MEMORY_BOOT` | `s3.NC_PSRAM_GPIO37` | `30` | N16R8 octal PSRAM consumes this package-visible carrier pad internally |
| `UI_10_S3_CORE_MEMORY_BOOT` | `s3_dbg_esd.NC_10` | `10` | manufacturer NC remains open |
| `UI_10_S3_CORE_MEMORY_BOOT` | `s3_dbg_esd.NC_6` | `6` | manufacturer NC remains open |
| `UI_10_S3_CORE_MEMORY_BOOT` | `s3_dbg_esd.NC_7` | `7` | manufacturer NC remains open |
| `UI_10_S3_CORE_MEMORY_BOOT` | `s3_dbg_esd.NC_9` | `9` | manufacturer NC remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_14` | `14` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_25` | `25` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_26` | `26` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_27` | `27` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_28` | `28` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_29` | `29` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_30` | `30` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_31` | `31` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.NC_32` | `32` | display assembly identifies this physical tail contact as no-connect |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.RD_UNUSED` | `12` | the selected direct-QSPI display path is write-only and needs no parallel read strobe |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display.TE` | `8` | tearing-effect output is not required by the bounded direct-QSPI update contract |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_12` | `12` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_14` | `14` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_25` | `25` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_26` | `26` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_27` | `27` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_28` | `28` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_29` | `29` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_30` | `30` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_31` | `31` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_32` | `32` | board-side contact deliberately open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_connector.PIN_8` | `8` | board-side contact deliberately open; S3 GPIO43 remains service UART TX |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `display_touch_controller.TE` | `TE` | tearing-effect output is not required by the bounded direct-QSPI update contract |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_esd_a.NC_10` | `10` | manufacturer no-connect remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_esd_a.NC_6` | `6` | manufacturer no-connect remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_esd_a.NC_7` | `7` | manufacturer no-connect remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_esd_a.NC_9` | `9` | manufacturer no-connect remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_esd_b.NC_10` | `10` | manufacturer no-connect remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_esd_b.NC_6` | `6` | manufacturer no-connect remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_esd_b.NC_7` | `7` | manufacturer no-connect remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_esd_b.NC_9` | `9` | manufacturer no-connect remains open |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `sd_power_switch.NC` | `4` | SC70 pin 4 is left floating as required |
| `UI_11_DISPLAY_TOUCH_STORAGE` | `touch_irq_buffer.NC` | `1` | SC70 pin 1 is intentionally unconnected |
| `UI_12_CONTROLS_INDICATORS` | `front_function_esd.IO8` | `8` | eighth function-key ESD channel is intentionally unused |
| `UI_12_CONTROLS_INDICATORS` | `slow_io_fault_sense_iso.NC` | `1` | manufacturer NC pad of the selected isolation device remains open |
| `UI_12_CONTROLS_INDICATORS` | `slow_io_s3_evidence_iso.NC` | `1` | manufacturer NC pad of the selected isolation device remains open |
| `UI_13_AUDIO_CODEC_HEADSET` | `codec.MCLK` | `2` | reviewed BCLK-derived-clock mode consumes no hidden S3 contact |
| `UI_13_AUDIO_CODEC_HEADSET` | `codec_power_switch.NC` | `4` | SC70 pin 4 is left floating as required |
| `UI_13_AUDIO_CODEC_HEADSET` | `headphone_esd.D2_MINUS` | `5` | the fourth independent ESD channel remains an intentional no-connect |
| `UI_13_AUDIO_CODEC_HEADSET` | `headphone_esd.NC_10` | `10` | manufacturer no-connect remains open |
| `UI_13_AUDIO_CODEC_HEADSET` | `headphone_esd.NC_6` | `6` | manufacturer no-connect remains open |
| `UI_13_AUDIO_CODEC_HEADSET` | `headphone_esd.NC_7` | `7` | manufacturer no-connect remains open |
| `UI_13_AUDIO_CODEC_HEADSET` | `headphone_esd.NC_9` | `9` | manufacturer no-connect remains open |
| `UI_13_AUDIO_CODEC_HEADSET` | `headphone_jack.RING1_SWITCH` | `6` | unused second internal switch remains open |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.ANT2` | `31` | secondary RF pad remains default-disabled and is not a second baseline antenna |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.GPIO2` | `4` | unallocated physical C5 GPIO remains open and has no hidden product role |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.GPIO25` | `26` | unallocated physical C5 GPIO remains open and has no hidden product role |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.GPIO26` | `27` | unallocated physical C5 GPIO remains open and has no hidden product role |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.GPIO3` | `5` | unallocated physical C5 GPIO remains open and has no hidden product role |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.GPIO5` | `16` | unallocated physical C5 GPIO remains open and has no hidden product role |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.NC_20` | `20` | module/package contract marks this physical C5 contact unavailable or no-connect |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.NC_22` | `22` | module/package contract marks this physical C5 contact unavailable or no-connect |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5.NC_PSRAM_GPIO15` | `19` | module/package contract marks this physical C5 contact unavailable or no-connect |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5_dbg_esd.NC_10` | `10` | manufacturer NC remains open |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5_dbg_esd.NC_6` | `6` | manufacturer NC remains open |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5_dbg_esd.NC_7` | `7` | manufacturer NC remains open |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5_dbg_esd.NC_9` | `9` | manufacturer NC remains open |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5_service_usb_connector.A8_SBU1` | `A8_SBU1` | service port implements no Alt Mode |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5_service_usb_connector.B8_SBU2` | `B8_SBU2` | service port implements no Alt Mode |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5_service_usb_switch.HSD2_MINUS` | `8` | no hidden second data destination |
| `UI_20_C5_RADIO_IR_SERVICE` | `c5_service_usb_switch.HSD2_PLUS` | `9` | no hidden second data destination |
| `UI_20_C5_RADIO_IR_SERVICE` | `ir_power_switch.NC` | `4` | manufacturer NC pad of the IR load switch remains open |
| `UI_21_FM_AM_RECEIVER` | `receiver.GPO1` | `4` | unused multifunction output remains open |
| `UI_21_FM_AM_RECEIVER` | `receiver.NC` | `5` | SOIC physical pin 5 remains open |
| `UI_21_FM_AM_RECEIVER` | `receiver_irq_iso.NC` | `1` | SC70 no-connect remains open |
| `UI_21_FM_AM_RECEIVER` | `receiver_power_switch.NC` | `4` | SC70 pin 4 is left floating as required |
| `UI_50_TX_SAFETY_EVIDENCE` | `evidence_cmp_a.OUT4` | `13` | unused UI comparator open-drain output remains unconnected |
| `UI_50_TX_SAFETY_EVIDENCE` | `safe_c5_fault_reset_buffer.NC` | `1` | manufacturer no-connect remains open |
| `UI_50_TX_SAFETY_EVIDENCE` | `safe_c5_reset_buffer.NC` | `1` | manufacturer no-connect remains open |

✅ **Reviewed:** 202 NC / 22 sheets; no contact, marker or rationale is missing.

[Machine evidence](../hardware/ecad/generated/H2-REV62-no-connects.json).
