# Распиновка Leshy2

[На главную](../README.ru.md) · [English](pinout.md) · [Аппаратная архитектура](hardware.ru.md)

Текущий рабочий дизайн контактов R2 и полные бюджеты S3/Hub автоматически
публикуются в [отчёте H0-R2](h0-r2-functional-architecture.ru.md). H1-R2
сейчас сверяет эту принципиальную карту с физической компоновкой и межплатными
переходами; изменение контакта допустимо только вместе с machine-контрактом,
проверками и публичной таблицей.

> Текущий источник: `hardware/architecture/h0-r2-rebaseline.json`. Таблица ниже —
> сохранённая точная распиновка **R1**, а не разрешение на KiCad для R2.

<details>
<summary><strong>Сохранённая точная распиновка R1</strong></summary>

## S3 — приложение, UI, display, storage и audio

**MPN:** `ESP32-S3-WROOM-1U-N16R8`

| Контакт | Сеть | Направление | Периферия | Подключение |
|---|---|---|---|---|
| `GPIO0` | `I2S_DIN` | `i` | `I2S0` | codec_i2s_din_iso.Y<br>s3_boot_pullup.END_2<br>s3_dbg_boot_series.END_2 |
| `GPIO1` | `SYS_I2C_SDA` | `io` | `I2C0` | slow_io.SDA<br>ui_matrix_io.SDA<br>headset_control_io.SDA<br>voice_band_io.SDA<br>receiver_i2c_iso.1A<br>display_connector.PIN_2<br>codec_i2c_iso.1A<br>pd_controller.I2Ct_SDA<br>pack_admission.PA0<br>safety_controller.PA0 |
| `GPIO2` | `SYS_I2C_SCL` | `o` | `I2C0` | slow_io.SCL<br>ui_matrix_io.SCL<br>headset_control_io.SCL<br>voice_band_io.SCL<br>receiver_i2c_iso.2A<br>display_connector.PIN_1<br>codec_i2c_iso.2A<br>pd_controller.I2Ct_SCL<br>pack_admission.PA11<br>safety_controller.PA11 |
| `GPIO3` | `RP_ALERT_N` | `i` | `GPIO_IRQ` | rp.GPIO19 |
| `GPIO4` | `DISPLAY_SD_SPI_D1` | `io` | `SPI2` | sd_miso_series.END_2<br>sd_host_d1_pullup.END_1<br>display_connector.PIN_10 |
| `GPIO5` | `SD_SPI_CS_N` | `o` | `SPI2` | sd_host_buffer.3A<br>sd_miso_buffer.OE_N<br>sd_host_cs_pullup.END_1 |
| `GPIO6` | `AUDIO_ARM` | `o` | `GPIO` | audio_safe_gate.1B<br>audio_safe_gate.2B<br>codec_i2s_din_boot_gate.B |
| `GPIO7` | `UNIT_HOST_SIG0` | `io` | `I2C1_OR_UART1_OR_GPIO` | unit_signal_iso.A1 |
| `GPIO8` | `UNIT_HOST_SIG1` | `io` | `I2C1_OR_UART1_OR_GPIO` | unit_signal_iso.A2 |
| `GPIO9` | `S3_RP_IPC_CS_N` | `o` | `SPI3` | rp.GPIO25 |
| `GPIO10` | `S3_C5_SDIO_CLK` | `o` | `SDMMC_SLOT1_1BIT` | c5.GPIO9 |
| `GPIO11` | `S3_C5_SDIO_CMD` | `io` | `SDMMC_SLOT1_1BIT` | c5.GPIO10 |
| `GPIO12` | `S3_C5_SDIO_D0` | `io` | `SDMMC_SLOT1_1BIT` | c5.GPIO8 |
| `GPIO13` | `S3_C5_SDIO_D1_IRQ` | `io` | `SDMMC_SLOT1_1BIT` | c5.GPIO7 |
| `GPIO14` | `S3_RP_IPC_MISO` | `i` | `SPI3` | rp.GPIO27 |
| `GPIO15` | `I2S_BCLK` | `o` | `I2S0` | codec_i2s_bclk_iso.A |
| `GPIO16` | `I2S_WS` | `o` | `I2S0` | codec_i2s_ws_iso.A |
| `GPIO17` | `I2S_DOUT` | `o` | `I2S0` | codec_i2s_dout_iso.A |
| `GPIO18` | `DISPLAY_SD_SPI_SCK` | `o` | `SPI2` | sd_host_buffer.1A<br>sd_host_sck_pulldown.END_1<br>display_connector.PIN_11 |
| `GPIO19` | `S3_USB_DM_LOCAL` | `io` | `USB_SERIAL_JTAG` | product_usb_dm_series.END_2 |
| `GPIO20` | `S3_USB_DP_LOCAL` | `io` | `USB_SERIAL_JTAG` | product_usb_dp_series.END_2 |
| `GPIO21` | `S3_RP_IPC_MOSI` | `o` | `SPI3` | rp.GPIO24 |
| `GPIO38` | `LCD_CS_N` | `o` | `SPI2` | display_connector.PIN_9<br>lcd_host_cs_pullup.END_1 |
| `GPIO39` | `ENCODER_A` | `i` | `PCNT0` | encoder.A<br>encoder_a_pullup.END_2 |
| `GPIO40` | `LCD_BL_PWM` | `o` | `LEDC` | backlight_gate_series.END_1 |
| `GPIO41` | `LCD_QSPI_D2` | `o` | `SPI2` | display_connector.PIN_17 |
| `GPIO42` | `LCD_QSPI_D3` | `o` | `SPI2` | display_connector.PIN_18 |
| `GPIO43` | `S3_UART_SERVICE_TX` | `o` | `UART0` | s3_dbg0_series.END_2 |
| `GPIO44` | `S3_UART_SERVICE_RX` | `i` | `UART0` | s3_dbg1_series.END_2 |
| `GPIO45` | `SYS_INT_N` | `i` | `GPIO_IRQ` | slow_io.INT<br>ui_matrix_io.INT_N<br>headset_control_io.INT_N<br>pd_controller.I2Ct_IRQ<br>touch_irq_buffer.Y<br>pack_status_buffer.D2 |
| `GPIO46` | `DISPLAY_SD_SPI_D0` | `o` | `SPI2` | sd_host_buffer.2A<br>sd_host_d0_pulldown.END_1<br>display_connector.PIN_13 |
| `GPIO47` | `ENCODER_B` | `i` | `PCNT0` | encoder.B<br>encoder_b_pullup.END_2 |
| `GPIO48` | `S3_RP_IPC_SCK` | `o` | `SPI3` | rp.GPIO26 |

## C5 — native 2,4/5 ГГц, IEEE 802.15.4 и IR

**MPN:** `ESP32-C5-WROOM-1U-N8R8`

| Контакт | Сеть | Направление | Периферия | Подключение |
|---|---|---|---|---|
| `GPIO0` | `IR_RX_DEMOD` | `i` | `RMT_RX0` | ir_demod_series.END_2<br>ir_demod_host_pullup.END_1 |
| `GPIO1` | `IR_RX_CARRIER` | `i` | `RMT_RX1` | ir_carrier_series.END_2<br>ir_carrier_host_pullup.END_1 |
| `GPIO4` | `IR_FRONTEND_PWR_EN` | `o` | `GPIO` | ir_power_switch.ON<br>ir_power_on_pulldown.END_1 |
| `GPIO6` | `IR_TX_CARRIER` | `o` | `RMT_TX0` | ir_safe_gate.A |
| `GPIO7` | `S3_C5_SDIO_D1_IRQ` | `io` | `SDIO_SLAVE` | s3.GPIO13 |
| `GPIO8` | `S3_C5_SDIO_D0` | `io` | `SDIO_SLAVE` | s3.GPIO12 |
| `GPIO9` | `S3_C5_SDIO_CLK` | `i` | `SDIO_SLAVE` | s3.GPIO10 |
| `GPIO10` | `S3_C5_SDIO_CMD` | `io` | `SDIO_SLAVE` | s3.GPIO11 |
| `GPIO11` | `C5_UART_SERVICE_TX` | `o` | `UART0` | c5_dbg0_series.END_2 |
| `GPIO12` | `C5_UART_SERVICE_RX` | `i` | `UART0` | c5_dbg1_series.END_2 |
| `GPIO13` | `C5_USB_DM` | `io` | `USB_SERIAL_JTAG` | c5_service_usb_dm_series.END_2 |
| `GPIO14` | `C5_USB_DP` | `io` | `USB_SERIAL_JTAG` | c5_service_usb_dp_series.END_2 |
| `GPIO23` | `C5_RF_TX_EVIDENCE_N` | `i` | `GPIO_IRQ` | evidence_main_isolator.1Y<br>c5_evidence_main_pullup.END_2 |
| `GPIO24` | `IR_TX_EVIDENCE_N` | `i` | `GPIO_IRQ` | evidence_main_isolator.2Y<br>ir_evidence_main_pullup.END_2 |

## RP2354B — nRF24 ×3, Sub-GHz, voice и Cap Bus

**MPN:** `SC1512-A4`

| Контакт | Сеть | Направление | Периферия | Подключение |
|---|---|---|---|---|
| `GPIO0` | `NRF0_CSN_N` | `o` | `GPIO` | nrf0_host_buffer.2A<br>nrf0_host_csn_pullup.END_1 |
| `GPIO1` | `NRF0_CE_REQ` | `o` | `GPIO` | safe_gate_a.1A |
| `GPIO2` | `NRF0_IRQ_N` | `i` | `GPIO_IRQ` | nrf0_irq_series.END_2<br>nrf0_host_irq_pullup.END_1 |
| `GPIO3` | `NRF1_CSN_N` | `o` | `GPIO` | nrf1_host_buffer.2A<br>nrf1_host_csn_pullup.END_1 |
| `GPIO4` | `NRF1_CE_REQ` | `o` | `GPIO` | safe_gate_a.2A |
| `GPIO5` | `NRF1_IRQ_N` | `i` | `GPIO_IRQ` | nrf1_irq_series.END_2<br>nrf1_host_irq_pullup.END_1 |
| `GPIO6` | `NRF2_CSN_N` | `o` | `GPIO` | nrf2_host_buffer.2A<br>nrf2_host_csn_pullup.END_1 |
| `GPIO7` | `NRF2_CE_REQ` | `o` | `GPIO` | safe_gate_a.3A |
| `GPIO8` | `NRF2_IRQ_N` | `i` | `GPIO_IRQ` | nrf2_irq_series.END_2<br>nrf2_host_irq_pullup.END_1 |
| `GPIO9` | `CC_CSN_N` | `o` | `GPIO` | cc_host_buffer.3A<br>cc_host_csn_pullup.END_1 |
| `GPIO10` | `CC_GDO0` | `i` | `GPIO_IRQ` | cc_gdo0_series.END_2<br>cc_host_gdo0_pulldown.END_1 |
| `GPIO11` | `CC_GDO2` | `i` | `GPIO_IRQ` | cc_gdo2_series.END_2<br>cc_host_gdo2_pulldown.END_1 |
| `GPIO12` | `U214_HOST_BUSY` | `i` | `GPIO_IRQ` | u214_series_busy.END_2 |
| `GPIO13` | `U214_HOST_IRQ` | `i` | `GPIO_IRQ` | u214_series_irq.END_2 |
| `GPIO14` | `U214_HOST_RST_N` | `o` | `GPIO` | u214_host_buffer_a.1A |
| `GPIO15` | `NRF_GROUP_PWR_EN` | `o` | `GPIO` | safe_gate_a.4A |
| `GPIO16` | `VOICE_UART_TX` | `o` | `UART0` | voice_control_mux_a.D1 |
| `GPIO17` | `VOICE_UART_RX` | `i` | `UART0` | voice_control_mux_a.D2 |
| `GPIO18` | `VOICE_PTT_REQ_N` | `o` | `GPIO` | safe_ptt_or.1A |
| `GPIO19` | `RP_ALERT_N` | `od` | `GPIO_IRQ` | s3.GPIO3 |
| `GPIO20` | `VOICE_AUDIO_ON_N` | `i` | `GPIO_IRQ` | voice_control_mux_b.D2<br>voice_audio_on_pulldown.END_1 |
| `GPIO21` | `PTT_BUTTON_N` | `i` | `GPIO_IRQ` | ptt_series.END_2 |
| `GPIO22` | `RP_ANY_TX_N` | `i` | `GPIO_IRQ` | evidence_main_isolator.3Y<br>rp_any_tx_main_pullup.END_2 |
| `GPIO23` | `CC_PWR_EN` | `o` | `GPIO` | safe_gate_b.1A |
| `GPIO24` | `S3_RP_IPC_MOSI` | `i` | `SPI1_IPC` | s3.GPIO21 |
| `GPIO25` | `S3_RP_IPC_CS_N` | `i` | `SPI1_IPC` | s3.GPIO9 |
| `GPIO26` | `S3_RP_IPC_SCK` | `i` | `SPI1_IPC` | s3.GPIO48 |
| `GPIO27` | `S3_RP_IPC_MISO` | `o` | `SPI1_IPC` | s3.GPIO14 |
| `GPIO28` | `U214_I2C_SDA_IN` | `io` | `I2C0_EXT` | u214_i2c_iso.SDAIN |
| `GPIO29` | `U214_I2C_SCL_IN` | `o` | `I2C0_EXT` | u214_i2c_iso.SCLIN |
| `GPIO30` | `NRF0_MISO` | `i` | `PIO0_SM0_RF_SPI` | nrf0_miso_series.END_2<br>nrf0_host_miso_pulldown.END_1 |
| `GPIO31` | `NRF0_SCK` | `o` | `PIO0_SM0_RF_SPI` | nrf0_host_buffer.3A<br>nrf0_host_sck_pulldown.END_1 |
| `GPIO32` | `NRF0_MOSI` | `o` | `PIO0_SM0_RF_SPI` | nrf0_host_buffer.4A<br>nrf0_host_mosi_pulldown.END_1 |
| `GPIO33` | `NRF1_MISO` | `i` | `PIO0_SM1_RF_SPI` | nrf1_miso_series.END_2<br>nrf1_host_miso_pulldown.END_1 |
| `GPIO34` | `NRF1_SCK` | `o` | `PIO0_SM1_RF_SPI` | nrf1_host_buffer.3A<br>nrf1_host_sck_pulldown.END_1 |
| `GPIO35` | `NRF1_MOSI` | `o` | `PIO0_SM1_RF_SPI` | nrf1_host_buffer.4A<br>nrf1_host_mosi_pulldown.END_1 |
| `GPIO36` | `NRF2_MISO` | `i` | `PIO0_SM2_RF_SPI` | nrf2_miso_series.END_2<br>nrf2_host_miso_pulldown.END_1 |
| `GPIO37` | `NRF2_SCK` | `o` | `PIO0_SM2_RF_SPI` | nrf2_host_buffer.3A<br>nrf2_host_sck_pulldown.END_1 |
| `GPIO38` | `NRF2_MOSI` | `o` | `PIO0_SM2_RF_SPI` | nrf2_host_buffer.4A<br>nrf2_host_mosi_pulldown.END_1 |
| `GPIO39` | `CC_MISO` | `i` | `PIO0_SM3_RF_SPI` | cc_so_series.END_2<br>cc_host_so_pulldown.END_1 |
| `GPIO40` | `U214_HOST_GPS_TX` | `o` | `UART1` | u214_host_buffer_a.2A |
| `GPIO41` | `U214_HOST_GPS_RX` | `i` | `UART1` | u214_series_gps_tx.END_2 |
| `GPIO42` | `CC_SCK` | `o` | `PIO0_SM3_RF_SPI` | cc_host_buffer.1A<br>cc_host_sclk_pulldown.END_1 |
| `GPIO43` | `CC_MOSI` | `o` | `PIO0_SM3_RF_SPI` | cc_host_buffer.2A<br>cc_host_si_pulldown.END_1 |
| `GPIO44` | `U214_HOST_MISO` | `i` | `PIO1_SM0_EXT_SPI` | u214_series_miso.END_2 |
| `GPIO45` | `U214_HOST_SCK` | `o` | `PIO1_SM0_EXT_SPI` | u214_host_buffer_a.3A |
| `GPIO46` | `U214_HOST_MOSI` | `o` | `PIO1_SM0_EXT_SPI` | u214_host_buffer_a.4A |
| `GPIO47` | `U214_HOST_NSS_N` | `o` | `GPIO` | u214_host_buffer_b.1A |

## USB-PD controller

**MPN:** `Texas Instruments TPS25751DREFR`

| Контакт | Сеть | Направление | Периферия | Подключение |
|---|---|---|---|---|
| `GPIO0` | `PD_EEPROM_WP` | `od` | `GPIO` | pd_config_eeprom.WP |
| `GPIO1` | `CHARGE_EN_N` | `od` | `GPIO` | nvdc_charger.CE |
| `I2Ct_IRQ` | `SYS_INT_N` | `od` | `I2C_TARGET` | s3.GPIO45 |
| `I2Ct_SCL` | `SYS_I2C_SCL` | `i` | `I2C_TARGET` | s3.GPIO2 |
| `I2Ct_SDA` | `SYS_I2C_SDA` | `io` | `I2C_TARGET` | s3.GPIO1 |

## Контроллер допуска батарейного pack

**MPN:** `Texas Instruments MSPM0C1106SDGS20R`

| Контакт | Сеть | Направление | Периферия | Подключение |
|---|---|---|---|---|
| `PA0` | `SYS_I2C_SDA` | `io` | `I2C_TARGET` | s3.GPIO1 |
| `PA2` | `PACK_GAUGE_I2C_SCL` | `io` | `BITBANG_I2C` | pack_gauge.SCL_OD<br>pack_gauge_scl_pullup.END_2 |
| `PA4` | `PACK_GAUGE_I2C_SDA` | `io` | `BITBANG_I2C` | pack_gauge.SDA_DQ<br>pack_gauge_sda_pullup.END_2 |
| `PA6` | `PACK_FET_HOLD_RELEASE` | `o` | `GPIO` | pack_hold.G2<br>pack_hold_release_pulldown.END_1 |
| `PA11` | `SYS_I2C_SCL` | `i` | `I2C_TARGET` | s3.GPIO2 |
| `PA16` | `PACK_PFAIL_N` | `i` | `GPIO_IRQ` | pack_status_buffer.D1<br>pack_pfail_pullup.END_2 |
| `PA17` | `PACK_ADMISSION_UART_TX` | `o` | `UART1` | abstract:pack service fixture |
| `PA18` | `PACK_ADMISSION_UART_RX` | `i` | `UART1` | abstract:pack service fixture |
| `PA22` | `PACK_DIAG_TRIGGER` | `o` | `GPIO` | pack_diag_timer.CH1_T<br>pack_diag_trigger_pulldown.END_1 |
| `PA23` | `PACK_SYS_INT_REQ` | `o` | `GPIO` | pack_status_buffer.G2<br>pack_irq_gate_pulldown.END_1 |
| `PA24` | `POWER_COMMAND_OFF_N` | `i` | `GPIO_IRQ` | power_command_pullup.END_2<br>power_command_filter.END_1<br>power_command_switch.THROW_B |
| `PA25` | `PACK_CELL0_ADC` | `i` | `ADC` | pack_mid_adc_top1.END_2<br>pack_mid_adc_bottom.END_1<br>pack_mid_adc_filter.END_1 |
| `PA26` | `PACK_STACK_ADC` | `i` | `ADC` | pack_stack_adc_top4.END_2<br>pack_stack_adc_bottom.END_1<br>pack_stack_adc_filter.END_1 |

`i` — вход, `o` — выход, `io` — двунаправленный контакт. Сервисные, питание и fixed-function контакты учитываются в полной machine-карте, даже если не являются GPIO.

</details>
