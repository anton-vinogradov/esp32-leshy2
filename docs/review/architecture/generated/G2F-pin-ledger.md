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
| `G2F-3I` | 3 | `s3 29U/3R/4F`, `c5 14U/6R/1F`, `rp 48U/0R/0F` | DEC-0045 limits runtime to one active signal group, but SG-N24 requires every simultaneous three-radio PTX/PRX mix including 3PTX; exact mixed-RF sensitivity/current/thermal envelope, quiet-state power parts and conducted/OTA HIL remain open |

## Exact-device provenance used by these drafts

| Device id | Exact MPN / boundary | Qualification | Lifecycle | Primary source | Lifecycle evidence |
|---|---|---|---|---|---|
| `cc1101rgpr` | `CC1101RGPR` | `verified_candidate` | `active` | [CC1101 Low-Power Sub-1 GHz RF Transceiver datasheet SWRS061I](https://www.ti.com/lit/ds/symlink/cc1101.pdf) | [TI CC1101RGPR order page](https://www.ti.com/product/CC1101/part-details/CC1101RGPR) |
| `ebyte_e01_ml01ipx` | `Ebyte E01-ML01IPX` | `verified_reference` | `nrf24_family_not_recommended_for_new_designs` | [E01-ML01IPX product specification 2025-01-16](https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf) | [Nordic nRF24 Series lifecycle page](https://www.nordicsemi.com/Products/nRF24-series) |
| `esp32_c5_wroom_1u_n8r8` | `ESP32-C5-WROOM-1U-N8R8` | `verified_candidate` | `active_candidate_revision_floor_v1_2` | [ESP32-C5-WROOM-1/WROOM-1U Datasheet v1.2](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf) | same primary source |
| `esp32_s3_wroom_1u_n16r2` | `ESP32-S3-WROOM-1U-N16R2` | `verified_candidate` | `active` | [ESP32-S3-WROOM-1/WROOM-1U Datasheet v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | same primary source |
| `hirose_dm3at_sf_pejm5` | `Hirose DM3AT-SF-PEJM5` | `verified_candidate` | `current_manufacturer_page` | [DM3 Series microSD Card Connectors catalog 2025-12-01](https://www.hirose.com/product/p/CL0609-0031-0-00) | same primary source |
| `m5_u214` | `M5Stack U214 Cap LoRa-1262` | `verified_candidate` | `active` | [M5Stack Cap LoRa-1262 product documentation live product page](https://docs.m5stack.com/en/cap/Cap_LoRa-1262) | same primary source |
| `nicerf_sa518_v11` | `NiceRF SA518` | `verified_candidate` | `current_product` | [SA518 UV Dual Frequency Walkie-talkie Module Product Specification 1.1 / 2026-05](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf) | same primary source |
| `rp2354a_a4` | `RP2354A A4 (exact order code required before BOM freeze)` | `verified_candidate` | `active` | [RP2350 Datasheet; RP2354A uses the same A-package pinout and stacked 2 MB flash build-date 2025-02-20](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) | same primary source |
| `rp2354b_a4` | `RP2354B A4 (exact A4 order/lot identity required before BOM freeze)` | `verified_candidate` | `active` | [RP2350 Datasheet; RP2354B uses the same B-package pinout and stacked 2 MB flash build-date 2025-02-20](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) | same primary source |
| `skyworks_si4732_a10_gs` | `Si4732-A10-GS` | `verified_candidate` | `manufacturer_documented` | [Si4732-A10 Broadcast AM/FM/SW/LW/RDS Radio Receiver data short 2021-09-13](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf) | same primary source |
| `sn74hc595pwr` | `SN74HC595PWR` | `verified_candidate` | `active` | [SNx4HC595 8-Bit Shift Registers datasheet SCLS041J](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf) | same primary source |
| `tca4307dgkr` | `TCA4307DGKR` | `reference_only` | `active` | [TCA4307 Hot-Swappable I2C/SMBus Buffer With Stuck-Bus Recovery datasheet SCPS270B](https://www.ti.com/lit/ds/symlink/tca4307.pdf) | same primary source |
| `tca6424argjr` | `TCA6424ARGJR` | `reference_only` | `active` | [TCA6424A Low-Voltage 24-Bit I2C/SMBus I/O Expander datasheet SCPS193D](https://www.ti.com/lit/ds/symlink/tca6424a.pdf) | same primary source |
| `tca9535pwr` | `TCA9535PWR` | `verified_candidate` | `active` | [TCA9535 Remote 16-Bit I2C/SMBus I/O Expander datasheet SCPS201E](https://www.ti.com/lit/ds/symlink/tca9535.pdf) | same primary source |

## G2F-2R — Two compute domains: C5 owns IR and compatibility radios

- Candidate status: `draft_machine_checked_not_architecture_decision`
- Validation scope: exposed-contact identity, unique allocation, strap proof, complete GPIO accounting, controller declaration, reciprocal programmable links and service-contact coverage.

### Antenna policy

Decisions `DEC-0048`/`DEC-0049`: onboard endpoint `external_sma`; `9` total SMA paths (`S3-2G4`, `C5-2G4/5`, `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`); three nRF paths use `ipex_to_short_pigtail` to `3` dedicated SMA; integrated-PCB baseline `false`. Si4732 topology `dedicated_fmi_and_ami` with shared switch `false` and AMI profile `direct_plug_in_loop_or_qualified_buffered_pod`. Connector decision `DEC-0050` assigns device-side RP-SMA jack/pin to `S3-2G4`, `C5-2G4/5` and standard SMA jack/socket to `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`, `RX-AM/LW`. Each antenna group requires at least `2` orderable qualified MPNs; native Wi-Fi fallback is `standard_sma_if_no_gain_cost_availability_advantage`. External accessories own their antennas.

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
| `RECEIVER_AUDIO_QUIET` | `receiver`, `codec`, `I2S` | receiver rail/reset off and isolated; codec muted/off; I2S clock/DMA stopped | RX_DOMAIN_EN, CODEC_EN and S3 peripheral clock gates | I2C no-back-power, clock spectrum, current and active-receiver desense HIL |
| `IR_QUIET` | `IR RX`, `IR TX` | frontend rail off; RMT stopped and pins parked; TX remains HARD_STOP_N-dominated | C5.GPIO4 IR_FRONTEND_PWR_EN plus independent HARD_STOP_N TX gate | dark/current/no-optical-output and active-radio desense HIL |
| `S3_RF_QUIET` | `S3 Wi-Fi`, `S3 BLE`, `ESP-NOW` | protocols/scans/advertising stopped and native RF block off while S3 CPU/UI remains alive | native RF power state plus S3_RF_TX_EVIDENCE | no background frame/carrier and active-receiver desense HIL |
| `C5_RF_QUIET` | `C5 Wi-Fi`, `C5 IEEE 802.15.4` | protocols stopped and native RF block off while C5 may remain alive for IR/recovery | native RF power state plus C5_RF_TX_EVIDENCE | no background frame/carrier and active-receiver desense HIL |
| `STORAGE_QUIET` | `microSD` | bounded flush then controller static and rail off when no storage session | slow_io.P20 SD_PWR_EN | no corruption/back-power and active-receiver desense HIL |
| `SERVICE_IPC_QUIET` | `USB/UART service`, `S3-RP SPI`, `S3-C5 SDIO`, `display SPI` | detached/suspended or static idle; clocks run only for bounded required transactions | per-controller clock/DMA gates; physical recovery contacts remain available | no periodic logs, measured clock spectrum, recovery and active-receiver desense HIL |

### `s3` — `ESP32-S3-WROOM-1U-N16R2`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO1` | 39 | `SYS_I2C_SDA` | `io` | `I2C0` | `slow_io.SDA`, `receiver.SDIO`, `abstract:touch/codec internal I2C` | — |
| `GPIO2` | 38 | `SYS_I2C_SCL` | `o` | `I2C0` | `slow_io.SCL`, `receiver.SCLK`, `abstract:touch/codec internal I2C` | — |
| `GPIO3` | 15 | `RP_ALERT_N` | `i` | `GPIO_IRQ` | `rp.GPIO19` | RP is held reset/high-Z through S3 strap sampling; an external pull fixes the accepted S3 boot state |
| `GPIO4` | 4 | `SD_SPI_MISO` | `i` | `SPI2` | `sd.DAT0` | — |
| `GPIO5` | 5 | `SD_SPI_CS_N` | `o` | `SPI2` | `sd.CD_DAT3` | — |
| `GPIO7` | 7 | `UNIT_SIG0` | `io` | `I2C1_OR_UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO8` | 12 | `UNIT_SIG1` | `io` | `I2C1_OR_UART0_OR_GPIO` | `abstract:protected configurable M5 Unit contact` | — |
| `GPIO9` | 17 | `S3_RP_IPC_CS_N` | `o` | `SPI3` | `rp.GPIO25` | — |
| `GPIO10` | 18 | `S3_C5_SDIO_CLK` | `o` | `SDMMC_SLOT1_4BIT` | `c5.GPIO9` | — |
| `GPIO11` | 19 | `S3_C5_SDIO_CMD` | `io` | `SDMMC_SLOT1_4BIT` | `c5.GPIO10` | — |
| `GPIO12` | 20 | `S3_C5_SDIO_D0` | `io` | `SDMMC_SLOT1_4BIT` | `c5.GPIO8` | — |
| `GPIO13` | 21 | `S3_C5_SDIO_D1` | `io` | `SDMMC_SLOT1_4BIT` | `c5.GPIO7` | — |
| `GPIO14` | 22 | `S3_RP_IPC_MISO` | `i` | `SPI3` | `rp.GPIO27` | — |
| `GPIO15` | 8 | `I2S_BCLK` | `o` | `I2S0` | `abstract:exact mono codec` | — |
| `GPIO16` | 9 | `I2S_WS` | `o` | `I2S0` | `abstract:exact mono codec` | — |
| `GPIO17` | 10 | `I2S_DOUT` | `o` | `I2S0` | `abstract:exact mono codec` | — |
| `GPIO18` | 11 | `I2S_DIN` | `i` | `I2S0` | `abstract:exact mono codec` | — |
| `GPIO19` | 13 | `S3_USB_DM` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO20` | 14 | `S3_USB_DP` | `io` | `USB_SERIAL_JTAG` | `abstract:service USB connector` | — |
| `GPIO21` | 23 | `S3_RP_IPC_MOSI` | `o` | `SPI3` | `rp.GPIO24` | — |
| `GPIO35` | 28 | `DISPLAY_SD_SPI_SCK` | `o` | `SPI2` | `sd.CLK`, `abstract:exact display controller` | — |
| `GPIO36` | 29 | `DISPLAY_SD_SPI_MOSI` | `o` | `SPI2` | `sd.CMD`, `abstract:exact display controller` | — |
| `GPIO37` | 30 | `SLOW_IO_INT_N` | `i` | `GPIO_IRQ` | `slow_io.INT` | — |
| `GPIO38` | 31 | `LCD_CS_N` | `o` | `SPI2` | `abstract:exact display controller` | — |
| `GPIO39` | 32 | `LCD_DC` | `o` | `GPIO` | `abstract:exact display controller` | — |
| `GPIO40` | 33 | `LCD_BL_PWM` | `o` | `LEDC` | `abstract:exact display/backlight driver` | — |
| `GPIO44` | 36 | `S3_C5_SDIO_D2` | `io` | `SDMMC_SLOT1_4BIT` | `c5.GPIO14` | — |
| `GPIO47` | 24 | `S3_C5_SDIO_D3` | `io` | `SDMMC_SLOT1_4BIT` | `c5.GPIO13` | — |
| `GPIO48` | 25 | `S3_RP_IPC_SCK` | `o` | `SPI3` | `rp.GPIO26` | — |

Budget: **29 used + 3 reserved + 4 free = 36 exposed GPIO**.
Reserved: `GPIO0`, `GPIO45`, `GPIO46`. Free: `GPIO6`, `GPIO41`, `GPIO42`, `GPIO43`.

### `c5` — `ESP32-C5-WROOM-1U-N8R8`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 6 | `IR_RX_DEMOD` | `i` | `RMT_RX0` | `abstract:exact robust-demod IR receiver` | — |
| `GPIO1` | 7 | `IR_RX_CARRIER` | `i` | `RMT_RX1` | `abstract:exact carrier-learning IR receiver` | — |
| `GPIO4` | 17 | `IR_FRONTEND_PWR_EN` | `o` | `GPIO` | `abstract:off-safe IR frontend load switch` | — |
| `GPIO6` | 8 | `IR_TX_CARRIER` | `o` | `RMT_TX0` | `abstract:fail-safe IR LED driver` | — |
| `GPIO7` | 9 | `S3_C5_SDIO_D1` | `io` | `SDIO_SLAVE_4BIT` | `s3.GPIO13` | external pull-up and documented SDIO edge profile are verified before runtime ownership |
| `GPIO8` | 10 | `S3_C5_SDIO_D0` | `io` | `SDIO_SLAVE_4BIT` | `s3.GPIO12` | — |
| `GPIO9` | 11 | `S3_C5_SDIO_CLK` | `i` | `SDIO_SLAVE_4BIT` | `s3.GPIO10` | — |
| `GPIO10` | 12 | `S3_C5_SDIO_CMD` | `io` | `SDIO_SLAVE_4BIT` | `s3.GPIO11` | — |
| `GPIO11` | 25 | `C5_UART_SERVICE_TX` | `o` | `UART0` | `abstract:service fixture` | — |
| `GPIO12` | 24 | `C5_UART_SERVICE_RX` | `i` | `UART0` | `abstract:service fixture` | — |
| `GPIO13` | 13 | `S3_C5_SDIO_D3` | `io` | `SDIO_SLAVE_4BIT` | `s3.GPIO47` | — |
| `GPIO14` | 14 | `S3_C5_SDIO_D2` | `io` | `SDIO_SLAVE_4BIT` | `s3.GPIO44` | — |
| `GPIO23` | 21 | `C5_RF_TX_EVIDENCE` | `i` | `GPIO_IRQ` | `abstract:independent C5 actual-TX detector` | — |
| `GPIO24` | 23 | `IR_TX_EVIDENCE` | `i` | `GPIO_IRQ` | `abstract:independent IR optical-current detector` | — |

Budget: **14 used + 6 reserved + 1 free = 21 exposed GPIO**.
Reserved: `GPIO2`, `GPIO3`, `GPIO25`, `GPIO26`, `GPIO27`, `GPIO28`. Free: `GPIO5`.

### `rp` — `RP2354B A4 (exact A4 order/lot identity required before BOM freeze)`

| Contact | Physical pad | Net | Dir | Controller | Exact/abstract peers | Strap/reset proof |
|---|---:|---|---|---|---|---|
| `GPIO0` | 77 | `NRF0_CSN_N` | `o` | `GPIO` | `nrf0.CSN` | — |
| `GPIO1` | 78 | `NRF0_CE` | `o` | `GPIO` | `nrf0.CE` | — |
| `GPIO2` | 79 | `NRF0_IRQ_N` | `i` | `GPIO_IRQ` | `nrf0.IRQ` | — |
| `GPIO3` | 80 | `NRF1_CSN_N` | `o` | `GPIO` | `nrf1.CSN` | — |
| `GPIO4` | 1 | `NRF1_CE` | `o` | `GPIO` | `nrf1.CE` | — |
| `GPIO5` | 2 | `NRF1_IRQ_N` | `i` | `GPIO_IRQ` | `nrf1.IRQ` | — |
| `GPIO6` | 3 | `NRF2_CSN_N` | `o` | `GPIO` | `nrf2.CSN` | — |
| `GPIO7` | 4 | `NRF2_CE` | `o` | `GPIO` | `nrf2.CE` | — |
| `GPIO8` | 6 | `NRF2_IRQ_N` | `i` | `GPIO_IRQ` | `nrf2.IRQ` | — |
| `GPIO9` | 7 | `CC_CSN_N` | `o` | `GPIO` | `cc.CSN` | — |
| `GPIO10` | 8 | `CC_GDO0` | `i` | `GPIO_IRQ` | `cc.GDO0` | — |
| `GPIO11` | 9 | `CC_GDO2` | `i` | `GPIO_IRQ` | `cc.GDO2` | — |
| `GPIO12` | 11 | `U214_BUSY` | `i` | `GPIO_IRQ` | `u214.LORA_BUSY` | — |
| `GPIO13` | 12 | `U214_IRQ` | `i` | `GPIO_IRQ` | `u214.LORA_IRQ` | — |
| `GPIO14` | 13 | `U214_RST_N` | `o` | `GPIO` | `u214.LORA_RST` | — |
| `GPIO15` | 14 | `NRF_GROUP_PWR_EN` | `o` | `GPIO` | `abstract:off-safe common nRF load switch` | — |
| `GPIO16` | 16 | `VOICE_UART_TX` | `o` | `UART0` | `voice.UART_RX` | — |
| `GPIO17` | 17 | `VOICE_UART_RX` | `i` | `UART0` | `voice.UART_TX` | — |
| `GPIO18` | 18 | `VOICE_PTT_N` | `o` | `GPIO` | `voice.PTT` | — |
| `GPIO19` | 19 | `RP_ALERT_N` | `od` | `GPIO_IRQ` | `s3.GPIO3` | — |
| `GPIO20` | 20 | `VOICE_ACTIVITY` | `i` | `GPIO_IRQ` | `voice.AUDIO_ON` | — |
| `GPIO21` | 21 | `PTT_BUTTON_N` | `i` | `GPIO_IRQ` | `abstract:physical PTT switch` | — |
| `GPIO22` | 22 | `VOICE_TX_EVIDENCE` | `i` | `GPIO_IRQ` | `abstract:independent actual-TX detector` | — |
| `GPIO23` | 23 | `CC_PWR_EN` | `o` | `GPIO` | `abstract:off-safe CC1101 load switch` | — |
| `GPIO24` | 25 | `S3_RP_IPC_MOSI` | `i` | `SPI1_IPC` | `s3.GPIO21` | — |
| `GPIO25` | 26 | `S3_RP_IPC_CS_N` | `i` | `SPI1_IPC` | `s3.GPIO9` | — |
| `GPIO26` | 27 | `S3_RP_IPC_SCK` | `i` | `SPI1_IPC` | `s3.GPIO48` | — |
| `GPIO27` | 28 | `S3_RP_IPC_MISO` | `o` | `SPI1_IPC` | `s3.GPIO14` | — |
| `GPIO28` | 36 | `U214_I2C_SDA_IN` | `io` | `I2C0_EXT` | `u214_i2c_iso.SDAIN` | — |
| `GPIO29` | 37 | `U214_I2C_SCL_IN` | `o` | `I2C0_EXT` | `u214_i2c_iso.SCLIN` | — |
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

### Fixed-function/control routes

| Net | From | To | Reset/safety rule |
|---|---|---|---|
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
| `LCD_RST_N` | `slow_io.P06` | `abstract:display-reset` | external reset-safe pull |
| `TOUCH_RST_N` | `slow_io.P07` | `abstract:touch-reset` | external reset-safe pull |
| `CODEC_EN` | `slow_io.P10` | `abstract:codec-enable` | external off-safe pull |
| `AUDIO_SEL0` | `slow_io.P11` | `abstract:audio-selector-0` | external muted-safe pull |
| `AUDIO_SEL1` | `slow_io.P12` | `abstract:audio-selector-1` | external muted-safe pull |
| `VOICE_DOMAIN_EN` | `slow_io.P13` | `abstract:voice-power-reset-domain` | off-safe pull; exact circuit gates the qualified 4 V rail and holds the module TX-safe during sequencing |
| `VOICE_PD_N` | `abstract:voice-power-reset-domain` | `voice.PD` | off-safe sequencer keeps the exact module in power-down until the qualified 4 V rail is valid |
| `VOICE_HL` | `slow_io.P14` | `voice.HL` | external conservative-power pull |
| `VOICE_UPDATE` | `voice.UPDATE` | `abstract:voice-update-fixture` | fixture-only; no runtime drive until the rev-1.1 direction/description conflict is resolved by specimen proof |
| `VOICE_MIC_IN` | `abstract:codec-voice-audio-out` | `voice.MIC_IN` | AC-coupled and limited by the exact codec/selector circuit |
| `VOICE_AF_OUT` | `voice.AFOUT` | `abstract:codec-voice-audio-in` | muted/isolated before voice rail transitions |
| `RX_DOMAIN_EN` | `slow_io.P15` | `abstract:receiver-power-reset-isolation` | off-safe pull; exact circuit removes receiver power, prevents I2C back-power and supplies reset sequencing |
| `RX_RST_N` | `abstract:receiver-power-reset-isolation` | `receiver.RST` | reset remains asserted until the qualified receiver rail and I2C isolation are valid |
| `RX_STATUS_N` | `receiver.GPO2_INTB` | `slow_io.P24` | exact interrupt source; bounded latency and pulse width remain HIL gates |
| `RX_SENB_I2C` | `abstract:i2c-mode-strap` | `receiver.SENB` | fixed reset strap selects the reviewed two-wire control mode |
| `RX_RCLK` | `abstract:qualified-32k-clock` | `receiver.RCLK` | clock source and startup remain exact electrical gates |
| `RX_AUDIO_L` | `receiver.LOUT_DFS` | `abstract:codec-receiver-left` | muted/AC-coupled by the exact audio selector |
| `RX_AUDIO_R` | `receiver.ROUT_DOUT` | `abstract:codec-receiver-right` | muted/AC-coupled by the exact audio selector |
| `RX_FMI_RF` | `receiver.FMI` | `abstract:RX-FM-SW-SMA-front-end` | dedicated external-SMA whip path; matching/ESD stays close to FMI |
| `RX_AMI_RF` | `receiver.AMI` | `abstract:RX-AM-LW-loop-pod` | dedicated short loop/pod path; generic long coax is not qualified |
| `EXT_5V_EN` | `slow_io.P17` | `abstract:protected-external-5v-enable` | external off-safe pull and current limit |
| `SD_PWR_EN` | `slow_io.P20` | `abstract:microsd-load-switch` | external off-safe pull |
| `SD_CARD_DETECT_N` | `sd.DETECT_A` | `slow_io.P21` | read-only debounced input; socket switch return is tied to the qualified reference domain |
| `STOP_LATCH_SENSE_N` | `abstract:latched-hard-stop-sense` | `slow_io.P22` | sense only; non-programmable hard-stop dominance never depends on this path |
| `S3_RF_TX_EVIDENCE` | `abstract:S3-actual-RF-TX-detector` | `slow_io.P23` | read-only evidence; hard-stop remains non-programmable |
| `POWER_FAULT_N` | `abstract:power-current-thermal-fault` | `slow_io.P25` | hardware protection acts independently; this is diagnostic evidence |
| `ACCESSORY_PRESENT_N` | `abstract:accessory-present` | `slow_io.P26` | read-only, protected and debounced |
| `HARD_STOP_N` | `abstract:latched-hard-stop` | `abstract:all-TX-enables-and-rails` | non-programmable dominance over every MCU and radio/voice/IR TX path |

### Programming, recovery and diagnostics

- `s3`: `EN`, `GPIO0`, `GPIO19`, `GPIO20` — native USB Serial/JTAG plus physical EN/BOOT.
- `c5`: `EN`, `GPIO28`, `GPIO27`, `GPIO11`, `GPIO12` — permanent UART0 plus physical CHIP_PU, BOOT and normal-boot/log strap; native USB pins are intentionally consumed by 4-bit SDIO.
- `rp`: `RUN`, `SWCLK`, `SWDIO`, `USB_DM`, `USB_DP`, `QSPI_SS_USB_BOOT` — independent SWD, RUN, USB and BOOTSEL fixture access.
- `voice`: `UPDATE`, `UART_TX`, `UART_RX`, `PD` — permanent fixture breakout for vendor update/recovery plus UART and hardware power-down; UPDATE drive remains inhibited until exact rev-1.1 direction/timing proof.

### Non-MCU contact accounting

| Instance | Used | Reserved | Free |
|---|---:|---:|---:|
| `slow_io` | 23 | 1 | 0 |

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
| `DISPLAY_SD_SPI` | `s3` | `abstract:display`, `sd` | scheduled; separate CS and per-device clocks; display transaction <=256 B; bounded SD command/data chunks; critical UI priority | critical/menu first visible response <=100 ms and qualified storage >=4.0 MB/s while all radios capture; no radio FIFO or IPC deadline is placed here | dirty/tiled display plus 1.5 MB/s record and 250 ms card-stall HIL |
| `S3_RP_IPC` | `s3` | `rp` | dedicated | 20 MHz SPI raw 2.5 MB/s and qualified framed payload >=1.5 MB/s; no display/storage or C5 controller ownership | SPI3 load, alert-to-read <=250 us and aggregate-radio stress HIL |
| `S3_C5_IPC` | `s3` | `c5` | dedicated | 4-bit SDIO at up to 40 MHz with qualified framed payload >=1.5 MB/s and control RTT <=2 ms; no microSD, RP or display controller ownership | single-slot SDMMC/SDIO throughput, control-priority and simultaneous Wi-Fi/802.15.4 load HIL |
| `S3_INTERNAL_I2C` | `s3` | `slow_io`, `abstract:touch`, `abstract:codec`, `receiver` | scheduled; bounded transactions; expander INT only wakes the service loop | ordinary UI/control first visible response <=100 ms; no radio FIFO or PTT deadline is placed here | shortest-pulse, matrix and fault-latency HIL |
| `S3_UNIT_PORT` | `s3` | `abstract:M5 Unit` | dedicated | one selected I2C/UART/GPIO Unit profile cannot be blocked by internal or U214 I2C | profile-switch and external-fault HIL |
| `S3_I2S` | `s3` | `abstract:codec` | dedicated | continuous DMA audio without storage/display service gaps | simultaneous display, SD, C5 and radio event stress HIL |

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
| `C5_FIXED_SDIO` | `c5.SDIO_SLAVE_4BIT` | `GPIO7`, `GPIO8`, `GPIO9`, `GPIO10`, `GPIO13`, `GPIO14` | ESP32-C5 SDIO slave fixed DAT1/DAT0/CLK/CMD/DAT3/DAT2 mapping; GPIO13/14 therefore cannot be runtime USB |
| `RP_SPI1_IPC` | `rp.SPI1_IPC` | `GPIO24`, `GPIO25`, `GPIO26`, `GPIO27` | RP2354B bank-0 mux group is SPI1 RX/CSn/SCK/TX |
| `RP_UART0_VOICE` | `rp.UART0` | `GPIO16`, `GPIO17` | RP2354B bank-0 mux pair is UART0 TX/RX |
| `RP_UART1_GNSS` | `rp.UART1` | `GPIO40`, `GPIO41` | RP2354B bank-0 mux pair is UART1 TX/RX |
| `RP_I2C0_U214` | `rp.I2C0_EXT` | `GPIO28`, `GPIO29` | RP2354B bank-0 mux pair is I2C0 SDA/SCL |

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
- RP2354B A4 exact lot identity, power/clock/land pattern and prototype assembly remain implementation gates; the verified QFN80 contact map is not a BOM freeze
- E01-ML01S is a geometry/interface reference, not an accepted three-module RF/power/antenna production choice; nRF24 family lifecycle remains not-recommended-for-new-designs
- CC1101 matching, oscillator, antenna path and regional proof are not represented by the bare-IC contact ledger
- TCA6424ARGJR and TCA4307DGKR are real-contact planning references; voltage domains, pulls, address, reset, shortest pulses and exact endpoint MPNs remain electrical/HIL gates
- After DEC-0046 quiet-state controls, S3 retains four free GPIO, C5 one and RP none; slow_io retains P27. Any new direct RP endpoint requires an explicit remap and repeated review
- C5 4-bit SDIO has exclusive ownership of the S3 SD/MMC host; C5 native USB is unavailable at runtime, so permanent UART0 plus EN/BOOT/strap contacts is the independent recovery path
- display and microSD are the only scheduled high-rate pair on one SPI2 controller; separate CS/per-device clocks and bounded transactions remove radio impact, but >=4.0 MB/s storage plus <=100 ms visible UI under card stalls remains a mandatory HIL gate
- PIO instruction memory, DMA arbitration latency and SRAM-bank contention remain executable firmware/HIL gates even though the state-machine/channel capacity arithmetic closes with explicit reserve
- DEC-0045 prohibits cross-group simultaneous signal operation but requires all three SG-N24 radios concurrently active in every independent PTX/PRX mix; DEC-0047 selects a qualified internal envelope; N24H-0001 L0 DIV-DIV is pre-HIL only and T1 TARGET must prove exact channel/power/sensitivity points
- SG-N24 3PTX is a real accepted load case, so the exact module choice and packet-rail design must prove simultaneous TX peak/average current, droop, thermal, coupling and STOP at the qualified power profile; a former RX-only hunt budget is insufficient
- DEC-0046 consumes RP GPIO15/GPIO23 and C5 GPIO4 for group-level power gates; exact load-switch/isolator MPNs, discharge, no-back-power sequencing and quiet-state EMI HIL remain open, leaving no free direct RP GPIO
- exact display/touch and codec, IR frontends, power tree, antenna placement and hard-stop circuitry remain open; SA518/Si4732 contact maps are instantiated, while SA518 UPDATE electrical direction/timing and both modules' surrounding power/audio/RF circuits remain specimen/electrical/HIL gates before target-architecture acceptance

## Machine-check result and review boundary

All source candidates pass structural validation. This proves that their listed programmable GPIO exist on the exact compute packages/modules and are fully accounted without collisions. Where declared, non-MCU contacts, interface resource contracts, controller GPIO-window selections, fixed-mux contact contracts, capacity arithmetic, signal-group declarations and quiet-state contract coverage are also complete. It does **not** close electrical feasibility: abstract peers, reference-only modules, RF networks, quiet-state circuitry, timing/EMI HIL, power and physical integration remain open. Therefore no candidate receives «Проведено ревью» as a complete target architecture in this generated artifact.
