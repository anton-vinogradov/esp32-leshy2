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

## Exact-device provenance used by these drafts

| Device id | Exact MPN / boundary | Qualification | Lifecycle | Primary source | Lifecycle evidence |
|---|---|---|---|---|---|
| `cc1101rgpr` | `CC1101RGPR` | `verified_candidate` | `active` | [CC1101 Low-Power Sub-1 GHz RF Transceiver datasheet SWRS061I](https://www.ti.com/lit/ds/symlink/cc1101.pdf) | [TI CC1101RGPR order page](https://www.ti.com/product/CC1101/part-details/CC1101RGPR) |
| `ebyte_e01_ml01s` | `Ebyte E01-ML01S` | `reference_only` | `nrf24_family_not_recommended_for_new_designs` | [E01-ML01S product page/manual live product page](https://www.ebyte.com/product/45.html) | [Nordic nRF24 Series lifecycle page](https://www.nordicsemi.com/Products/nRF24-series) |
| `esp32_c5_wroom_1u_n8r8` | `ESP32-C5-WROOM-1U-N8R8` | `verified_candidate` | `active_candidate_revision_floor_v1_2` | [ESP32-C5-WROOM-1/WROOM-1U Datasheet v1.2](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf) | same primary source |
| `esp32_s3_wroom_1u_n16r2` | `ESP32-S3-WROOM-1U-N16R2` | `verified_candidate` | `active` | [ESP32-S3-WROOM-1/WROOM-1U Datasheet v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | same primary source |
| `m5_u214` | `M5Stack U214 Cap LoRa-1262` | `verified_candidate` | `active` | [M5Stack Cap LoRa-1262 product documentation live product page](https://docs.m5stack.com/en/cap/Cap_LoRa-1262) | same primary source |
| `rp2354a_a4` | `RP2354A A4 (exact order code required before BOM freeze)` | `verified_candidate` | `active` | [RP2350 Datasheet; RP2354A uses the same A-package pinout and stacked 2 MB flash build-date 2025-02-20](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) | same primary source |
| `sn74hc595pwr` | `SN74HC595PWR` | `verified_candidate` | `active` | [SNx4HC595 8-Bit Shift Registers datasheet SCLS041J](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf) | same primary source |
| `tca9535pwr` | `TCA9535PWR` | `verified_candidate` | `active` | [TCA9535 Remote 16-Bit I2C/SMBus I/O Expander datasheet SCPS201E](https://www.ti.com/lit/ds/symlink/tca9535.pdf) | same primary source |

## G2F-2R — Two compute domains: C5 owns IR and compatibility radios

- Candidate status: `draft_machine_checked_not_architecture_decision`
- Validation scope: exposed-contact identity, unique allocation, strap proof, complete GPIO accounting, controller declaration, reciprocal programmable links and service-contact coverage.

### `s3` — `ESP32-S3-WROOM-1U-N16R2`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `u214.SDA`, `slow_io.SDA`, `abstract:touch/codec/receiver I2C` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `u214.SCL`, `slow_io.SCL`, `abstract:touch/codec/receiver I2C` | — |
| `GPIO4` | 4 | `SD_CLK` | `o` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO5` | 5 | `SD_CMD` | `io` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO6` | 6 | `SD_D0` | `io` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO7` | 7 | `UNIT_SIG0` | `io` | `UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO8` | 12 | `UNIT_SIG1` | `io` | `UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
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

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20` — native USB Serial/JTAG plus physical EN/BOOT and UART0 fixture fallback.
- `c5`: `EN`, `GPIO28`, `GPIO13`, `GPIO14` — native USB Serial/JTAG plus physical CHIP_PU/BOOT; removable SDIO isolation.

### Open qualification gaps

- `nrf0` uses `Ebyte E01-ML01S` as `reference_only`, not an accepted production choice.
- `nrf0` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf1` uses `Ebyte E01-ML01S` as `reference_only`, not an accepted production choice.
- `nrf1` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf2` uses `Ebyte E01-ML01S` as `reference_only`, not an accepted production choice.
- `nrf2` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- E01-ML01S is a geometry/interface reference, not the accepted three-module RF/power/antenna production choice
- nRF24 is not recommended for new designs; CC1101RGPR is ACTIVE, but authorised sourcing, qualified alternates and protocol HIL remain unresolved
- CC1101 crystal, balun/matching network, antenna switch/connector and regional RF proof are not represented by the bare IC pinout
- exact display/touch, microSD socket, codec, voice module, IR frontends, Unit protection/mux and safe IRQ aggregation are not frozen
- single-core C5 worst-case service latency for three simultaneous nRF PRX FIFOs plus CC1101, IR and native-radio work needs executable HIL
- TCA9535 powers up as inputs; every safety-relevant output requires the stated external safe pull and cannot implement STOP
- S3 microSD and C5-link logical slots share one SD/MMC host; required scheduling/concurrency and measured throughput are not yet proven
- U214 requires I2C initialization of its onboard PI4IOE5V6408 antenna-switch control; pin exposure alone does not prove an operational LoRa path

## G2F-3D — Three compute domains: RP2354A owns compatibility radios and voice deadlines

- Candidate status: `draft_machine_checked_not_architecture_decision`
- Validation scope: exposed-contact identity, unique allocation, strap proof, complete GPIO accounting, controller declaration, reciprocal programmable links and service-contact coverage.

### `s3` — `ESP32-S3-WROOM-1U-N16R2`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `u214.SDA`, `slow_io.SDA`, `abstract:touch/codec/receiver I2C` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `u214.SCL`, `slow_io.SCL`, `abstract:touch/codec/receiver I2C` | — |
| `GPIO3` | 15 | `RP_ALERT_N` | `i` | `GPIO_IRQ` | `rp.GPIO28` | RP is held in reset/high-Z through S3 strap sampling; external pull fixes the accepted S3 boot state |
| `GPIO4` | 4 | `SD_CLK` | `o` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO5` | 5 | `SD_CMD` | `io` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO6` | 6 | `SD_D0` | `io` | `SDMMC_SLOT0_1BIT` | `abstract:exact microSD socket` | — |
| `GPIO7` | 7 | `UNIT_SIG0` | `io` | `UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO8` | 12 | `UNIT_SIG1` | `io` | `UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
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
| `GPIO21` | 33 | `VOICE_SQ` | `i` | `GPIO_IRQ` | `abstract:exact SA518/SA868 voice module` | — |
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

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20` — native USB Serial/JTAG plus physical EN/BOOT and UART0 fixture fallback.
- `c5`: `EN`, `GPIO28`, `GPIO13`, `GPIO14` — native USB Serial/JTAG plus permanent UART0 and physical CHIP_PU/BOOT.
- `rp`: `RUN`, `SWCLK`, `SWDIO`, `USB_DM`, `USB_DP`, `QSPI_SS_USB_BOOT` — independent SWD, RUN, USB and BOOTSEL fixture access.

### Open qualification gaps

- `nrf0` uses `Ebyte E01-ML01S` as `reference_only`, not an accepted production choice.
- `nrf0` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf1` uses `Ebyte E01-ML01S` as `reference_only`, not an accepted production choice.
- `nrf1` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- `nrf2` uses `Ebyte E01-ML01S` as `reference_only`, not an accepted production choice.
- `nrf2` lifecycle: `nrf24_family_not_recommended_for_new_designs`.
- E01-ML01S is a geometry/interface reference, not the accepted three-module RF/power/antenna production choice
- nRF24 is not recommended for new designs; CC1101RGPR is ACTIVE, but authorised sourcing, qualified alternates and protocol HIL remain unresolved
- CC1101 crystal, balun/matching network, antenna switch/connector and regional RF proof are not represented by the bare IC pinout
- exact display/touch, microSD socket, codec, voice module, IR frontends, Unit protection/mux and hard-stop implementation are not frozen
- RP2354A is a bare-QFN candidate: power, clock, stacked-flash order identity, land pattern and prototype SWD/USB recovery remain implementation gates
- all 30 RP GPIO and all 36 S3 GPIO are accounted with zero general-purpose reserve; physical packaging or one new direct endpoint forces remap/consolidation
- TCA9535 powers up as inputs; every safety-relevant output requires an external safe pull and cannot implement STOP
- S3 microSD and C5-link logical slots share one SD/MMC host; required scheduling/concurrency and measured throughput are not yet proven
- U214 requires I2C initialization of its onboard PI4IOE5V6408 antenna-switch control; pin exposure alone does not prove an operational LoRa path

## Machine-check result and review boundary

Both source candidates pass structural validation. This proves that their listed programmable GPIO exist on the exact compute packages/modules and are fully accounted without collisions. It does **not** close electrical feasibility: abstract peers, reference-only nRF modules, RF networks, timing HIL, power and physical integration remain open. Therefore neither candidate receives «Проведено ревью» as a complete owner/pin architecture in this artifact.
