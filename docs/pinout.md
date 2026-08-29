# Current Leshy2 R2 pin assignment

[Home](../README.md) · [Русский](pinout.ru.md) · [Hardware](hardware.md)

This is the exact H1-R2.31 working GPIO map for the two independent RP2354B domains and their five M1 signals. The exact C5 module-pad/IO-mux electrical contract is joined. It still does not authorize KiCad: the live FSUSB42MUX/C11355 production route and an exact service-VBUS detector/latch MPN remain fail-closed before a new R2 H2 export.

> Machine source: `hardware/architecture/h1-r2-dual-rp-pinout.json`. Pin-map artifact marker: **`H1-R2.31`**; current physical-design marker: **`H1-R2.37`**.

## Front Hub RP

Front S3/C5/rear-RP fan-out, three independent nRF24 buses, microSD, Pack/Safety mailbox, LCD TE and backlight; no audio or broadcast ownership.

**GPIO:** `46/48` used, `2` reserve. **PIO:** `8/12` used. **DMA:** `14/16` used.

| GPIO | Net | Direction | Controller | Physical endpoint | Reset / pull |
|---:|---|---|---|---|---|
| `0` | `S3_HUB_D0` | `io` | `PIO1_SM0_S3_QUAD` | S3 GPIO21 | input/high-Z; external pull-down |
| `1` | `S3_HUB_D1` | `io` | `PIO1_SM0_S3_QUAD` | S3 GPIO14 | input/high-Z; external pull-down |
| `2` | `S3_HUB_D2` | `io` | `PIO1_SM0_S3_QUAD` | S3 GPIO43 through ROM-UART isolation | input/high-Z; Hub-side external pull-down; isolation open |
| `3` | `S3_HUB_D3` | `io` | `PIO1_SM0_S3_QUAD` | S3 GPIO44 through ROM-UART isolation | input/high-Z; Hub-side external pull-down; isolation open |
| `4` | `S3_HUB_SCK` | `in` | `PIO1_SM0_S3_QUAD` | S3 GPIO48 | input; external pull-down |
| `5` | `UI_HUB_ALERT_N` | `od` | `GPIO_IRQ` | S3 GPIO3 wired-OR | released/high-Z; external pull-up |
| `6` | `HUB_RESERVE_6` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `7` | `C5_SDIO_CLK` | `out` | `PIO1_SM1_2_C5_SDIO` | direct series footprint -> C5 GPIO9 / module pad 11 | input/high-Z; no fitted pull; C5 and Hub held reset until ownership is established |
| `8` | `C5_SDIO_CMD` | `io` | `PIO1_SM1_2_C5_SDIO` | direct pull-up/series branch -> C5 GPIO10 / module pad 12 | input/high-Z; branch-local 10-kohm pull-up; C5 and Hub held reset |
| `9` | `C5_SDIO_D0` | `io` | `PIO1_SM1_2_C5_SDIO` | direct pull-up/series branch -> C5 GPIO8 / module pad 10 | input/high-Z; branch-local 10-kohm pull-up; C5 and Hub held reset |
| `10` | `C5_SDIO_D1` | `io` | `PIO1_SM1_2_C5_SDIO` | direct pull-up/series branch -> C5 GPIO7 / module pad 9 | input/high-Z; branch-local 10-kohm pull-up also fixes the JTAG-source strap; C5 and Hub held reset |
| `11` | `C5_SDIO_D2` | `io` | `PIO1_SM1_2_C5_SDIO` | FSUSB42 HSD2+ -> D+ common -> C5 GPIO14 / module pad 14 | input/high-Z; 10-kohm HSD2 branch pull-up disconnected from C5 in service mode |
| `12` | `C5_SDIO_D3` | `io` | `PIO1_SM1_2_C5_SDIO` | FSUSB42 HSD2- -> D- common -> C5 GPIO13 / module pad 13 | input/high-Z; 10-kohm HSD2 branch pull-up disconnected from C5 in service mode |
| `13` | `HUB_RF_SCK` | `out` | `PIO2_SM0_RF_SPI` | M1.24 -> RF RP GPIO26 | input/high-Z; external pull-down |
| `14` | `HUB_RF_MOSI` | `out` | `PIO2_SM0_RF_SPI` | M1.26 -> RF RP GPIO24 | input/high-Z; external pull-down |
| `15` | `HUB_RF_MISO` | `in` | `PIO2_SM0_RF_SPI` | M1.27 <- RF RP GPIO27 | input; external pull-down |
| `16` | `HUB_RF_CS_N` | `out` | `GPIO` | M1.23 -> RF RP GPIO25 | input/high-Z; external pull-up |
| `17` | `HUB_RF_ALERT_N` | `in` | `GPIO_IRQ` | M1.22 <- RF RP GPIO19 | input; external pull-up |
| `18` | `NRF0_SCK` | `out` | `PIO0_SM0_NRF0_SPI` | nRF24 #0 command buffer | input/high-Z; external pull-down |
| `19` | `NRF0_MOSI` | `out` | `PIO0_SM0_NRF0_SPI` | nRF24 #0 command buffer | input/high-Z; external pull-down |
| `20` | `NRF0_MISO` | `in` | `PIO0_SM0_NRF0_SPI` | nRF24 #0 return buffer | input; external pull-down |
| `21` | `NRF0_CSN_N` | `out` | `GPIO` | nRF24 #0 command buffer | input/high-Z; external pull-up |
| `22` | `NRF0_CE_REQ` | `out` | `GPIO` | nRF24 #0 safety gate | input/high-Z; external pull-down |
| `23` | `NRF0_IRQ_N` | `in` | `GPIO_IRQ` | nRF24 #0 return buffer | input; external pull-up |
| `24` | `NRF1_SCK` | `out` | `PIO0_SM1_NRF1_SPI` | nRF24 #1 command buffer | input/high-Z; external pull-down |
| `25` | `NRF1_MOSI` | `out` | `PIO0_SM1_NRF1_SPI` | nRF24 #1 command buffer | input/high-Z; external pull-down |
| `26` | `NRF1_MISO` | `in` | `PIO0_SM1_NRF1_SPI` | nRF24 #1 return buffer | input; external pull-down |
| `27` | `NRF1_CSN_N` | `out` | `GPIO` | nRF24 #1 command buffer | input/high-Z; external pull-up |
| `28` | `NRF1_CE_REQ` | `out` | `GPIO` | nRF24 #1 safety gate | input/high-Z; external pull-down |
| `29` | `NRF1_IRQ_N` | `in` | `GPIO_IRQ` | nRF24 #1 return buffer | input; external pull-up |
| `30` | `NRF2_SCK` | `out` | `PIO0_SM2_NRF2_SPI` | nRF24 #2 command buffer | input/high-Z; external pull-down |
| `31` | `NRF2_MOSI` | `out` | `PIO0_SM2_NRF2_SPI` | nRF24 #2 command buffer | input/high-Z; external pull-down |
| `32` | `NRF2_MISO` | `in` | `PIO0_SM2_NRF2_SPI` | nRF24 #2 return buffer | input; external pull-down |
| `33` | `NRF2_CSN_N` | `out` | `GPIO` | nRF24 #2 command buffer | input/high-Z; external pull-up |
| `34` | `NRF2_CE_REQ` | `out` | `GPIO` | nRF24 #2 safety gate | input/high-Z; external pull-down |
| `35` | `NRF2_IRQ_N` | `in` | `GPIO_IRQ` | nRF24 #2 return buffer | input; external pull-up |
| `36` | `NRF_GROUP_PWR_EN` | `out` | `GPIO` | FAULT_KILL-dominant nRF rail switch | input/high-Z; external pull-down |
| `37` | `SD_SCK` | `out` | `PIO0_SM3_SD_SPI` | microSD command buffer | input/high-Z; external pull-down |
| `38` | `SD_MOSI` | `out` | `PIO0_SM3_SD_SPI` | microSD command buffer | input/high-Z; external pull-down |
| `39` | `SD_MISO` | `in` | `PIO0_SM3_SD_SPI` | microSD return buffer | input; external pull-up |
| `40` | `SD_CS_N` | `out` | `GPIO` | microSD command buffer | input/high-Z; external pull-up |
| `41` | `SD_PWR_EN` | `out` | `GPIO` | microSD load switch | input/high-Z; external pull-down |
| `42` | `HUB_SAFE_I2C_SDA` | `io` | `I2C1` | M1.32 -> Pack/Safety mailboxes | input/open-drain released; external pull-up to AON-safe compatible domain |
| `43` | `HUB_SAFE_I2C_SCL` | `od` | `I2C1` | M1.33 -> Pack/Safety mailboxes | input/open-drain released; external pull-up to AON-safe compatible domain |
| `44` | `SD_DETECT_N` | `in` | `GPIO_IRQ` | microSD socket detect | input; external pull-up |
| `45` | `LCD_TE` | `in` | `GPIO_IRQ` | HMX035CTFT-001 TE | input; external pull-down while panel reset is asserted |
| `46` | `LCD_BL_PWM` | `out` | `PWM` | backlight hardware gate | input/high-Z; external pull-down keeps backlight off |
| `47` | `HUB_RESERVE_47` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |

### Resources

| Kind | Allocation |
|---|---|
| PIO | `PIO0_SM0` → nRF24 #0 full-duplex SPI; `PIO0_SM1` → nRF24 #1 full-duplex SPI; `PIO0_SM2` → nRF24 #2 full-duplex SPI; `PIO0_SM3` → microSD full-duplex SPI; `PIO1_SM0` → S3 four-data-line half-duplex link; `PIO1_SM1` → C5 4-bit SDIO command/clock; `PIO1_SM2` → C5 4-bit SDIO data; `PIO2_SM0` → rear RF RP full-duplex SPI |
| DMA | nRF24 #0 full-duplex SPI = `2`; nRF24 #1 full-duplex SPI = `2`; nRF24 #2 full-duplex SPI = `2`; microSD full-duplex SPI = `2`; S3 four-data-line half-duplex link = `2`; C5 4-bit SDIO = `2`; rear RF RP full-duplex SPI = `2` |

## Rear RF RP

Rear CC1101, voice, FM/AM/SW/LW/Airband RX, audio, M5 Unit and exactly one signed U214/U219 Cap profile owner; no nRF24 or microSD ownership.

**GPIO:** `40/48` used, `8` reserve. **PIO:** `6/12` used. **DMA:** `12/16` used.

| GPIO | Net | Direction | Controller | Physical endpoint | Reset / pull |
|---:|---|---|---|---|---|
| `0` | `AUDIO_BCLK` | `out` | `PIO1_SM0_I2S_TX` | SN74LVC1G126DCKR Ioff isolation -> ES8311 BCLK | input/high-Z; external pull-down; codec-side isolation OE low |
| `1` | `AUDIO_WS` | `out` | `PIO1_SM0_I2S_TX` | SN74LVC1G126DCKR Ioff isolation -> ES8311 LRCK | input/high-Z; external pull-down; codec-side isolation OE low |
| `2` | `AUDIO_DOUT` | `out` | `PIO1_SM0_I2S_TX` | SN74LVC1G126DCKR Ioff isolation -> ES8311 SDIN | input/high-Z; external pull-down; codec-side isolation OE low |
| `3` | `AUDIO_DIN` | `in` | `PIO1_SM1_I2S_RX` | ES8311 SDOUT -> SN74LVC1G126DCKR Ioff isolation | input; external pull-down; host-side isolation OE low |
| `4` | `REAR_I2C_SDA` | `io` | `I2C0` | codec/Si4732/Airband/headset slow-control bus | input/open-drain released; external pull-up |
| `5` | `REAR_I2C_SCL` | `od` | `I2C0` | codec/Si4732/Airband/headset slow-control bus | input/open-drain released; external pull-up |
| `6` | `AUDIO_ARM` | `out` | `GPIO` | audio reset-safe selector gate | input/high-Z; external pull-down |
| `7` | `M5_UNIT_SIG0` | `io` | `PIO2_SM0_1_M5_PROFILE` | isolated M5 Unit PIO-I2C/PIO-UART/GPIO profile | input/high-Z; branch isolation disabled; accessory-side profile pull |
| `8` | `M5_UNIT_SIG1` | `io` | `PIO2_SM0_1_M5_PROFILE` | isolated M5 Unit PIO-I2C/PIO-UART/GPIO profile | input/high-Z; branch isolation disabled; accessory-side profile pull |
| `9` | `CC_CSN_N` | `out` | `GPIO` | CC1101 command buffer | input/high-Z; external pull-up |
| `10` | `CC_GDO0` | `in` | `GPIO_IRQ` | CC1101 return buffer | input; external pull-down |
| `11` | `CC_GDO2` | `in` | `GPIO_IRQ` | CC1101 return buffer | input; external pull-down |
| `12` | `CAP_PIN10_BUSY_OR_NFC_CS_N` | `io` | `GPIO_IRQ_OR_OUTPUT_PROFILE` | SN74CBTLV1G125: U214 BUSY input or U219 NFC_CS_N output | input/high-Z; AON /OE pull-up disconnects pin 10; U219 profile drives inactive high before POWER_EN |
| `13` | `CAP_IRQ` | `in` | `GPIO_IRQ` | exact-one profile return buffer: U214 DIO1 or U219 NFC_IRQ; polarity interpreted only by the signed profile | input; external pull-down; accessory branch remains off |
| `14` | `CAP_RESET_N_OR_POWER_EN` | `out` | `GPIO` | exact-one profile command buffer: U214 RESET_N or U219 POWER_EN | input/high-Z; external pull-down holds U214 reset and U219 power disabled |
| `15` | `RF_RESERVE_15` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `16` | `VOICE_UART_TX` | `out` | `UART0` | SA818S-U/V selected command path | input/high-Z; external pull-up keeps UART idle |
| `17` | `VOICE_UART_RX` | `in` | `UART0` | SA818S-U/V selected response path | input; external pull-up |
| `18` | `VOICE_PTT_REQ_N` | `out` | `GPIO` | FAULT_KILL-dominant voice PTT gate | input/high-Z; external pull-up inhibits TX |
| `19` | `HUB_RF_ALERT_N` | `od` | `GPIO_IRQ` | M1.22 -> Hub RP GPIO17 | released/high-Z; external pull-up |
| `20` | `VOICE_AUDIO_ON_N` | `in` | `GPIO_IRQ` | voice audio activity selector | input; external pull-up |
| `21` | `PTT_BUTTON_N` | `in` | `GPIO_IRQ` | direct user PTT | input; external pull-up |
| `22` | `RF_ANY_TX_N` | `in` | `GPIO_IRQ` | wired actual-TX evidence | input; external pull-up |
| `23` | `CC_PWR_EN` | `out` | `GPIO` | CC1101 rail switch | input/high-Z; external pull-down |
| `24` | `HUB_RF_MOSI` | `in` | `SPI1` | M1.26 <- Hub RP GPIO14 | input; external pull-down |
| `25` | `HUB_RF_CS_N` | `in` | `SPI1` | M1.23 <- Hub RP GPIO16 | input; external pull-up |
| `26` | `HUB_RF_SCK` | `in` | `SPI1` | M1.24 <- Hub RP GPIO13 | input; external pull-down |
| `27` | `HUB_RF_MISO` | `out` | `SPI1` | M1.27 -> Hub RP GPIO15 | input/high-Z; external pull-down |
| `28` | `RF_RESERVE_28` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `29` | `RF_RESERVE_29` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `30` | `CAP_I2C_SDA` | `io` | `I2C1` | TCA4307DGKR hot-plug/stuck-bus isolator to exact-one U214/U219 contact 4 SDA | input/open-drain released; external pull-up; isolator disabled |
| `31` | `CAP_I2C_SCL` | `od` | `I2C1` | TCA4307DGKR hot-plug/stuck-bus isolator to exact-one U214/U219 contact 3 SCL | input/open-drain released; external pull-up; isolator disabled |
| `32` | `RF_RESERVE_32` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `33` | `RF_RESERVE_33` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `34` | `RF_RESERVE_34` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `35` | `AIR_RX_EN` | `out` | `GPIO` | Airband switched rail and LT5560 enable | input/high-Z; external pull-down disables converted path |
| `36` | `AIR_RX_MODE` | `out` | `GPIO` | direct FM/SW versus converted-Airband selector | input/high-Z; external pull-down selects direct FM/SW |
| `37` | `RF_RESERVE_37` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `38` | `RF_RESERVE_38` | `reserve` | `GPIO` | test pad only | input/high-Z; external pull-down; DNP |
| `39` | `CC_MISO` | `in` | `PIO0_SM0_CC_SPI` | CC1101 return buffer | input; external pull-down |
| `40` | `CAP_GNSS_TX_OR_RF_SW0` | `out` | `UART1_OR_GPIO_PROFILE` | exact-one profile: U214 GNSS RX or U219 RF_SW0 | input/high-Z; external pull-down until signed profile admission |
| `41` | `CAP_GNSS_RX_OR_CC_GDO0` | `in` | `UART1_OR_GPIO_IRQ_PROFILE` | exact-one profile return: U214 GNSS TX or U219 CC1101 GDO0 | input; external pull-down; accessory branch remains off |
| `42` | `CC_SCK` | `out` | `PIO0_SM0_CC_SPI` | CC1101 command buffer | input/high-Z; external pull-down |
| `43` | `CC_MOSI` | `out` | `PIO0_SM0_CC_SPI` | CC1101 command buffer | input/high-Z; external pull-down |
| `44` | `CAP_SPI_MISO` | `in` | `PIO0_SM1_CAP_SPI` | exact-one profile return: U214 MISO or U219 shared MISO | input; external pull-down; accessory branch remains off |
| `45` | `CAP_SPI_SCK` | `out` | `PIO0_SM1_CAP_SPI` | exact-one profile command: U214 SCK or U219 shared SCLK | input/high-Z; external pull-down |
| `46` | `CAP_SPI_MOSI` | `out` | `PIO0_SM1_CAP_SPI` | exact-one profile command: U214 MOSI or U219 shared MOSI | input/high-Z; external pull-down |
| `47` | `CAP_SPI_PRIMARY_CS_N` | `out` | `GPIO` | exact-one profile command: U214 NSS_N or U219 CC1101_CS_N | input/high-Z; external pull-up keeps either profile deselected |

### Resources

| Kind | Allocation |
|---|---|
| PIO | `PIO0_SM0` → CC1101 full-duplex SPI; `PIO0_SM1` → exact-one U214/U219 Cap full-duplex SPI; `PIO1_SM0` → codec I2S transmit clocks/data; `PIO1_SM1` → codec I2S receive data; `PIO2_SM0` → isolated M5 Unit PIO-I2C or UART transmit profile; `PIO2_SM1` → isolated M5 Unit UART receive profile; idle in I2C/GPIO profiles |
| DMA | CC1101 full-duplex SPI = `2`; exact-one U214/U219 Cap full-duplex SPI = `2`; codec full-duplex I2S = `2`; Hub-RF hardware SPI1 = `2`; voice UART continuous RX = `1`; U214 GNSS UART continuous RX = `1`; M5 Unit profile full-duplex worst case = `2` |

## Hub RP ↔ RF RP through M1

| Net | M1 | Hub GPIO | RF GPIO | Driver |
|---|---:|---:|---:|---|
| `HUB_RF_ALERT_N` | `22` | `17` | `19` | rf_rp open-drain |
| `HUB_RF_CS_N` | `23` | `16` | `25` | hub_rp |
| `HUB_RF_SCK` | `24` | `13` | `26` | hub_rp |
| `HUB_RF_MOSI` | `26` | `14` | `24` | hub_rp |
| `HUB_RF_MISO` | `27` | `15` | `27` | rf_rp |

## S3 ROM-UART isolation

Both lines cross an Ioff-capable bidirectional isolation boundary whose OE is held disabled by a physical pull throughout S3 reset, strap sampling, ROM download and UART0 recovery.

S3 firmware may enable the two data channels only after normal application boot, Hub RUN release and a successful idle/ready handshake; entering ROM download, either-controller reset or fault shutdown opens the boundary again.

## Still unproven

- PIO instruction fit and Hub/RF 14/12-channel DMA allocation must compile in the six-domain firmware build matrix; exact channel IDs, DREQ routing and peak simultaneous profile remain executable proof gates.
- Simultaneous three-nRF RX/TX/mix, microSD, S3-Hub, Hub-C5 and Hub-RF traffic must pass emulator/dev-board timing before fabrication and HIL after assembly.
- Reset-state voltage and no-back-power behavior must be measured for every switched/isolated branch.
- Hub GPIO42/43 Pack/Safety I2C requires an exact powered-off-Ioff boundary and separate 3V3_MAIN/AON pull-up domains before schematic authorization.
- The C5 electrical pad/mux contract is joined; exact live production route for FSUSB42MUX/C11355 and an exact service-VBUS detector/latch MPN remain fail-closed before R2 H2.
- The exact-one signed U214/U219 profile must pass received-unit pin continuity, protected-power, RF-switch, VNA and RX/NFC HIL before the U219 branch can be enabled.

## Exact dual-NMOS pin map

`Diodes Incorporated 2N7002DW-7-F` / JLC `C83571` keeps the exact physical SOT-363 top-view mapping.

| Physical pin | Terminal |
|---:|---|
| `1` | `S2` |
| `2` | `G2` |
| `3` | `D1` |
| `4` | `S1` |
| `5` | `G1` |
| `6` | `D2` |

| Instance | Channel | Gate | Source | Drain |
|---|---|---|---|---|
| `pack_hold` | `channel_1` | `PACK_HOLD_GATE` | `PACK_LOCAL_GND` | `PACK_FET_OVERRIDE_N` |
| `pack_hold` | `channel_2` | `PACK_FET_HOLD_RELEASE` | `PACK_LOCAL_GND` | `PACK_HOLD_GATE` |
| `pack_status_buffer` | `channel_1` | `PACK_PFAIL_RAW` | `PACK_LOCAL_GND` | `PACK_PFAIL_N` |
| `pack_status_buffer` | `channel_2` | `PACK_SYS_INT_REQ` | `PACK_LOCAL_GND` | `SYS_INT_N` |
| `safe_reset_sink_a` | `channel_1` | `S3_RESET_KILL_GATE` | `SAFETY_GROUND` | `S3_RESET_N` |
| `safe_reset_sink_a` | `channel_2` | `C5_RESET_KILL_GATE` | `SAFETY_GROUND` | `C5_RESET_N` |
| `safe_reset_sink_b` | `channel_1` | `RF_RESET_KILL_GATE` | `SAFETY_GROUND` | `RP_RESET_N` |
| `safe_reset_sink_b` | `channel_2` | `SAFETY_GROUND` | `SAFETY_GROUND` | `NO_CONNECT` |
