# PIN-0002 — zero-based exact pin/controller maps

- Статус: **Historical candidate/reference; internal map review сохранён, full-device exactness не доказана**
- Дата: 2026-08-16
- Этап: 3, шаг 5a
- Входы: reviewed `SYN-0001`, `SRC-0001`; accepted `DEC-0013/0018/0024/0026/0027`
- Scope: `SYN-2A`, `SYN-2B`, `SYN-3A`
- Не является: final component qualification, PCB routing proof или architecture decision

> `FND-0049/DEC-0041`: эти maps корректно считали module-exposed S3/C5 GPIO,
> но не имели exact device/carrier provenance для всей подключённой периферии.
> Они сохраняются как полезная арифметика и источник test gates, но не являются
> active prerequisite или доказательством реальной полной сборки.

## Mapping rules

1. Maps use module-exposed pins of `ESP32-S3-WROOM-1U-N16R2` and `ESP32-C5-WROOM-1U-N8R8`, not SoC maximum counts.
2. GPIO matrix routing is allowed where the manufacturer supports it; fixed USB and C5 SDIO pins remain fixed.
3. SD/MMC pull-ups never land on S3 boot straps.
4. A strap pin is usable only with explicit reset-state proof; `strap-reserved` is not free product I/O.
5. S3 native USB and physical `GPIO0/EN` recovery remain. C5 uses 1-bit SDIO, preserving GPIO13/14 USB and physical `GPIO28/CHIP_PU` recovery.
6. STOP/reset, power gates, radio-latch `OE`, actual-TX indicator and analog safety are non-programmable dominant nets, not ordinary MCU control pins.
7. Display/touch reset, ordinary UI inputs and slow controls may use local I²C I/O; PTT and radio deadline paths follow the direct/latch maps below.

## Common S3 map — all candidates

All three use the same 18 S3 pins.

| GPIO | Net / direction | Controller | Reset/electrical note |
|---:|---|---|---|
| 1 | `SYS_I2C_SDA` I/O | I²C | onboard slow controls; external branches switched/isolated |
| 2 | `SYS_I2C_SCL` I/O | I²C | no safety-critical sole path |
| 4 | `SD_CLK` O | SDMMC slot 0 | no strap; signal-integrity qualification |
| 5 | `SD_CMD` I/O | SDMMC slot 0 | required pull-up |
| 6 | `SD_D0` I/O | SDMMC slot 0 | required pull-up |
| 7 | `SD_D1` I/O | SDMMC slot 0 | required pull-up |
| 8 | `SD_D2` I/O | SDMMC slot 0 | required pull-up |
| 9 | `SD_D3` I/O | SDMMC slot 0 | required pull-up |
| 10 | `C5_SDIO_CLK` O | SDMMC slot 1 | C5 1-bit SDIO slave |
| 11 | `C5_SDIO_CMD` I/O | SDMMC slot 1 | pull-up, bounded host ownership |
| 12 | `C5_SDIO_D0` I/O | SDMMC slot 1 | control/event/bulk data |
| 13 | `C5_SDIO_D1_IRQ` I/O | SDMMC slot 1 | SDIO interrupt/data1 |
| 15 | `I2S_BCLK` O | I2S0 | ES8311 full-duplex mono |
| 16 | `I2S_WS` O | I2S0 | ES8311 word select |
| 17 | `I2S_DOUT` O | I2S0 TX | S3→ES8311 |
| 18 | `I2S_DIN` I | I2S0 RX | ES8311→S3 |
| 19 | `USB_D-` I/O | native USB | service/HID/CDC/MSC/update/recovery |
| 20 | `USB_D+` I/O | native USB | never repurposed |

`SYS_I2C` covers ES8311/Si4732 control, touch, a bounded local-input/slow-output controller, power/status sensors and switched U216/generic-I²C branches. External stuck-low cannot hold the onboard bus. The budget retains up to eight ordinary local-input states plus direct PTT; exact ergonomics/MPN remain stage-4 qualification, not hidden MCU GPIO.

## `SYN-2A` S3 delta

| GPIO | Net / direction | Controller / owner | Reset/electrical note |
|---:|---|---|---|
| 0 | `VOICE_UART_TX` O | UART1 | voice rail off during boot/recovery |
| 3 | `PTT_BUTTON_N` I | direct | pull-up; default eFuse ignores GPIO3 JTAG strap; inert until armed |
| 14 | `VOICE_PTT_N` O | direct/dead-man | pull-up forces RX; STOP dominates |
| 21 | `CC_GDO2` I | packet-radio service | direct event |
| 35 | `LCD_SCK` O | GP-SPI2 | readless baseline display |
| 36 | `LCD_MOSI` O | GP-SPI2 | chunked/preemptible bulk |
| 37 | `LCD_CS_N` O | GP-SPI2 | pull-up |
| 38 | `LCD_DC` O | GPIO | defined reset level |
| 39 | `LCD_BL_PWM` O | LEDC/PWM | default off |
| 40 | `RF_SPI_SCK` O | GP-SPI3 | nRF/CC shared; ≤10 MHz for nRF |
| 41 | `RF_SPI_MOSI_LDATA` O | GP-SPI3 + latch data | latch clock separate |
| 42 | `RF_SPI_MISO` I | GP-SPI3 | only selected powered device drives |
| 43 | `RF_LATCH_CLK` O | bounded GPIO | independent of radio SCK |
| 44 | `RF_LATCH_STB` O | GPIO | `OE` disabled until safe vector loaded |
| 46 | `VOICE_UART_RX` I | UART1 | voice rail off through strap sample |
| 47 | `NRF_IRQ_AGG_N` I | protected logic | read all three STATUS sources |
| 48 | `CC_GDO0` I | packet-radio service | direct FIFO/event input |
| 45 | `STRAP_RESERVED_VDD_SPI` | — | no functional load; 3.3 V memory strap |

Ledger: `35 used + 1 strap-reserved = 36`; no general-purpose spare. `GPIO0/EN` remain service recovery; the GPIO0-connected backend is unpowered while reset.

## `SYN-2B` S3 delta

| GPIO | Net / direction | Controller / owner | Reset/electrical note |
|---:|---|---|---|
| 0 | `BOOT_SERVICE` | ROM strap/test access | no runtime peripheral |
| 3 | `PTT_BUTTON_N` I | direct | pull-up; default eFuse ignores JTAG strap |
| 14 | `VOICE_PTT_N` O | direct/dead-man | pull-up RX default; STOP dominant |
| 21 | `VOICE_UART_RX` I | UART1 | voice rail off at reset |
| 35 | `EXT_SPI_SCK` O | GP-SPI2 | display + U214, per-device clock |
| 36 | `EXT_SPI_MOSI` O | GP-SPI2 | bounded arbitration |
| 37 | `EXT_SPI_MISO` I | GP-SPI2 | U214 response; display is write-only baseline |
| 38 | `LCD_CS_N` O | GP-SPI2 | pull-up |
| 39 | `LCD_DC` O | GPIO | defined reset level |
| 40 | `LCD_BL_PWM` O | LEDC/PWM | default off |
| 41 | `U214_NSS_N` O | GP-SPI2 software CS | pull-up; accessory off by default |
| 42 | `U214_BUSY` I | direct | powered-profile input |
| 43 | `U214_IRQ` I | direct | powered-profile input |
| 44 | `GNSS_MUX_UART_RX` I | UART2 | selected U214/Unit GPS only |
| 47 | `GNSS_MUX_UART_TX` O | UART2 | 2:1 switch + mutually exclusive rails |
| 48 | `VOICE_UART_TX` O | UART1 | module protocol |
| 45 | `STRAP_RESERVED_VDD_SPI` | — | no functional load |
| 46 | `STRAP_RESERVED_BOOT_LOG` | — | no functional load |

Ledger: `33 used + 3 strap/recovery-reserved = 36`; no general-purpose spare. `U214_RST`, display/touch reset, voice `PD/H-L`, GNSS mux select and slow status use reset-safe slow-control outputs; STOP/power gates remain independent.

## `SYN-3A` S3 delta

| GPIO | Net / direction | Controller / owner | Reset/electrical note |
|---:|---|---|---|
| 0 | `RP_IPC_CS_N` O | GP-SPI3 | pull-up preserves normal boot |
| 3 | `RP_ALERT_N` I | event | RP held reset/high-Z through strap sample |
| 14 | `RP_IPC_MISO` I | GP-SPI3 | RP→S3 |
| 21 | `RP_IPC_MOSI` O | GP-SPI3 | S3→RP |
| 35 | `EXT_SPI_SCK` O | GP-SPI2 | display + U214 |
| 36 | `EXT_SPI_MOSI` O | GP-SPI2 | bounded arbitration |
| 37 | `EXT_SPI_MISO` I | GP-SPI2 | U214 response |
| 38 | `LCD_CS_N` O | GP-SPI2 | pull-up |
| 39 | `LCD_DC` O | GPIO | defined reset level |
| 40 | `LCD_BL_PWM` O | LEDC/PWM | default off |
| 41 | `U214_NSS_N` O | GP-SPI2 software CS | pull-up |
| 42 | `U214_BUSY` I | direct | accessory off at reset |
| 43 | `U214_IRQ` I | direct | accessory off at reset |
| 44 | `GNSS_MUX_UART_RX` I | UART2 | selected backend only |
| 47 | `GNSS_MUX_UART_TX` O | UART2 | 2:1 switch + exclusive rails |
| 48 | `RP_IPC_SCK` O | GP-SPI3 | local board link |
| 45 | `STRAP_RESERVED_VDD_SPI` | — | no functional load |
| 46 | `STRAP_RESERVED_BOOT_LOG` | — | no functional load |

Ledger: `34 used + 2 strap-reserved = 36`; no general-purpose spare.

## Common C5 fixed map

| GPIO | Net / direction | Controller | Reset/strap note |
|---:|---|---|---|
| 0 | `IR_RX_DEMOD` I | RMT RX2 | robust 38 kHz path |
| 1 | `IR_RX_CARRIER` I | RMT RX3 | measured-carrier path |
| 6 | `IR_TX_CARRIER` O | RMT TX0 | driver inhibit/STOP default off |
| 7 | `SDIO_D1_IRQ` I/O | SDIO slave | required pull-up; production checks USB Serial/JTAG recovery |
| 8 | `SDIO_D0` I/O | SDIO slave | 1-bit data |
| 9 | `SDIO_CLK` I | SDIO slave | fixed IO-MUX |
| 10 | `SDIO_CMD` I/O | SDIO slave | fixed IO-MUX |
| 13 | `USB_D-` I/O | native USB | retained by 1-bit SDIO |
| 14 | `USB_D+` I/O | native USB | independent recovery |

All candidates require a C5 revision with working SDIO, not v0.0/v0.1. External straps select `GPIO25=0`, `GPIO3=1`, the documented falling-sample/rising-drive SDIO profile. No irreversible JTAG eFuse is required.

## `SYN-2A` C5 delta

| GPIO | Net / direction | Controller / owner | Reset/strap note |
|---:|---|---|---|
| 2 | `U214_MISO` I | GP-SPI2 | U214 rail off at boot |
| 3 | `U214_NSS_N` O | GP-SPI2 CS | pull-up also selects SDIO edge strap |
| 4 | `U214_MOSI` O | GP-SPI2 | Cap profile |
| 5 | `U214_SCK` O | GP-SPI2 | Cap profile |
| 11 | `U214_BUSY` I | direct | accessory off at reset |
| 12 | `U214_IRQ` I | direct | accessory off at reset |
| 23 | `U214_GNSS_UART_RX` I | UART0 | U214 GPS TX→C5 |
| 24 | `U214_GNSS_UART_TX` O | UART0 | C5→U214 GPS RX |
| 25 | `UNIT_GPS_UART_RX` I | UART1 | rail off; external pull-down fixes SDIO edge |
| 26 | `CAP_I2C_SDA` I/O | I²C | pull-up; GPIO26 is not the USB-capable download selector |
| 27 | `CAP_I2C_SCL` I/O | I²C | pull-up; ROM-log strap documented |
| 28 | `UNIT_GPS_UART_TX / BOOT_SERVICE` O/strap | UART1 + ROM recovery | pull-up normal boot; accessory rail off/high-Z while physical service control forces low for Joint Download Boot 0 |

Ledger: `21 used / 21`; no spare. `U214_RST`, profile power and Cap-I²C isolation use local safe slow-control outputs; STOP directly cuts/inhibits `VEXT_RF`. U214 and Unit GPS use separate UARTs, but exactly one GNSS backend is active.

## `SYN-2B` C5 delta

| GPIO | Net / direction | Controller / owner | Reset/strap note |
|---:|---|---|---|
| 2 | `RF_SPI_MISO` I | GP-SPI2 | RF rail/buffers off at reset |
| 3 | `RF_LATCH_CLK` O | bounded GPIO | pull-up fixes SDIO edge; not radio SCK |
| 4 | `RF_SPI_SCK` O | GP-SPI2 | ≤10 MHz nRF bus |
| 5 | `RF_SPI_MOSI_LDATA` O | GP-SPI2 + latch data | separate latch clock |
| 11 | `RF_LATCH_STB` O | bounded GPIO | `OE` STOP-disabled until safe vector loaded |
| 12 | `NRF_IRQ_AGG_N` I | protected logic | query all STATUS sources |
| 23 | `CC_GDO0` I | direct | FIFO/event |
| 24 | `CC_GDO2` I | direct | event |
| 25 | `STRAP_RESERVED_SDIO_EDGE` | — | external pull-down |
| 26 | `STRAP_RESERVED_BOOT_AUX` | — | no external runtime load; GPIO26 is any-value in SPI boot and Joint Download Boot 0 |
| 27 | `STRAP_RESERVED_ROM_LOG` | — | no functional load |
| 28 | `BOOT_SERVICE` | ROM recovery | pull-up normal boot; physical control low plus CHIP_PU toggle selects USB/UART Joint Download Boot 0 |

Ledger: `17 used + 4 strap/recovery-reserved = 21`; no general-purpose spare. GP-SPI2 is not double-booked because S3↔C5 uses SDIO.

## `SYN-3A` C5 delta

| GPIO | State | Reason |
|---:|---|---|
| 2 | free after boot | no external load |
| 3 | strap-reserved | pull-up fixes SDIO edge |
| 4 | free after boot | no assignment |
| 5 | free after boot | no assignment |
| 11 | `C5_UART0_TX_SERVICE` | permanent diagnostics/RF-test; DBG10 `DBG0` |
| 12 | `C5_UART0_RX_SERVICE` | permanent diagnostics/RF-test; DBG10 `DBG1` |
| 23 | free | no assignment |
| 24 | free | no assignment |
| 25 | strap-reserved | pull-down fixes SDIO edge |
| 26 | strap-reserved | no external runtime load; not tied to the physical BOOT control |
| 27 | strap-reserved | deterministic ROM-log state |
| 28 | boot/recovery-reserved | pull-up normal boot; physical low plus CHIP_PU toggle selects USB/UART Joint Download Boot 0 |

Ledger after `DEC-0031`: `9 product-used + 2 service-reserved + 5 strap/recovery-reserved + 5 general-purpose free = 21`. This is the only candidate with useful non-strap MCU GPIO reserve. The stage-3 map originally counted GPIO11/12 among seven generic free pins; permanent UART0 diagnostics correctly reclassifies them without creating a collision (`FND-0038`).

## `SYN-3A` RP2354A A4 map

All 30 GPIO are used; dedicated `USB_DP/DM`, `SWDIO/SWCLK` and `RUN` retain recovery/reset.

| GPIO | Net / direction | Function | Safe state |
|---:|---|---|---|
| 0 | `RF_SPI_MISO` I | SPI0 RX | radios off/high-Z |
| 1 | `NRF0_CSN_N` O | direct | pull-up |
| 2 | `RF_SPI_SCK` O | SPI0 SCK | idle |
| 3 | `RF_SPI_MOSI` O | SPI0 TX | defined idle |
| 4 | `NRF0_CE` O | direct | pull-down |
| 5 | `NRF0_IRQ_N` I | direct | qualified level |
| 6 | `NRF1_CSN_N` O | direct | pull-up |
| 7 | `NRF1_CE` O | direct | pull-down |
| 8 | `NRF1_IRQ_N` I | direct | qualified level |
| 9 | `NRF2_CSN_N` O | direct | pull-up |
| 10 | `NRF2_CE` O | direct | pull-down |
| 11 | `NRF2_IRQ_N` I | direct | qualified level |
| 12 | `CC_CSN_N` O | direct | pull-up |
| 13 | `CC_GDO0` I | direct event | qualified input |
| 14 | `CC_GDO2` I | direct event | qualified input |
| 15 | `STOP_LATCH_SENSE` I | observation | not the kill path |
| 16 | `VOICE_UART_TX` O | UART0 TX | voice rail off |
| 17 | `VOICE_UART_RX` I | UART0 RX | voice rail off |
| 18 | `VOICE_PTT_N` O | direct/dead-man | pull-up + STOP gate |
| 19 | `VOICE_PD` O | direct | pull-down/off |
| 20 | `VOICE_HL` O | direct | pull-down/low power |
| 21 | `VOICE_SQ` I | direct | qualified input |
| 22 | `PTT_BUTTON_N` I | direct | pull-up; lease-gated |
| 23 | `VOICE_TX_EVIDENCE` I | detector | command and evidence separate |
| 24 | `RP_IPC_MOSI` I | SPI1 RX | S3→RP |
| 25 | `RP_IPC_CS_N` I | SPI1 CSn | pull-up |
| 26 | `RP_IPC_SCK` I | SPI1 SCK | local link |
| 27 | `RP_IPC_MISO` O | SPI1 TX | high-Z unless selected |
| 28 | `RP_ALERT_N` O | open-drain/SIO | high-Z until valid boot |
| 29 | `RP_BOOT_HEALTH` O | SIO/watchdog | supervisor evidence |

STOP asynchronously drives RP `RUN`, radio/voice gates and CE/PTT safe states. Direct nRF IRQs preserve source identity.

## Controller-instance ledger

| Domain | `SYN-2A` | `SYN-2B` | `SYN-3A` |
|---|---|---|---|
| S3 SDMMC | slot0 microSD 4-bit; slot1 C5 1-bit | same | same |
| S3 GP-SPI2 | display | display + U214 | display + U214 |
| S3 GP-SPI3 | nRF/CC | free/reserved | RP IPC master |
| S3 I2S0 | ES8311 full-duplex | same | same |
| S3 UART | voice | voice + selected-GNSS mux | selected-GNSS mux |
| S3 I²C | onboard + isolated NFC/accessory | onboard + isolated external | same |
| C5 SDIO/USB/RMT | 1-bit / native / 2 RX+1 TX IR | same | same |
| C5 GP-SPI2 | U214 | nRF/CC | free |
| C5 UART | U214 GNSS + Unit GPS | unassigned | unassigned |
| C5 I²C | Cap-Bus + local slow control | free | free |
| RP2354A | absent | absent | SPI0 nRF/CC, UART0 voice, SPI1 IPC, direct dead-man |

No hardware controller is double-booked. Shared buses have one local owner and bounded arbitration.

## Radio-control latch contract for `SYN-2A/2B`

| Q | Function | Disabled/default |
|---:|---|---|
| 0 | `NRF0_CSN_N` | high |
| 1 | `NRF0_CE` | low |
| 2 | `NRF1_CSN_N` | high |
| 3 | `NRF1_CE` | low |
| 4 | `NRF2_CSN_N` | high |
| 5 | `NRF2_CE` | low |
| 6 | `CC_CSN_N` | high |
| 7 | reserved/test-safe | non-enabling |

`OE` is reset/STOP-dominant. Data may share MOSI, but latch clock/strobe are independent. Sequence: disable outputs → shift complete safe vector → strobe → verify → enable. STOP disables outputs asynchronously and separately cuts/inhibits TX-capable power.

## Strap/recovery proof

| Risk | Resolution |
|---|---|
| S3 Octal PSRAM steals GPIO35…37 | all maps fix `N16R2`; later memory budget must prove 2 MB sufficient |
| S3 GPIO0 | normal pull-up; service forces low only for intentional recovery |
| S3 GPIO3 | default eFuse ignores value; attached circuit remains reset-safe |
| S3 GPIO45/46 | GPIO45 retains 3.3 V-memory strap; GPIO46 is reserved or driven only by unpowered voice backend after sampling |
| C5 GPIO7 | SDIO pull-up explicit; production verifies USB Serial/JTAG; no JTAG-lock eFuse assumed |
| C5 GPIO3/25 | fixed `1/0` SDIO edge profile; HIL uses that exact state |
| C5 GPIO26/27/28 | GPIO27/28 pull-up; physical GPIO28-low plus CHIP_PU toggle selects USB/UART Joint Download Boot 0; GPIO26 is not tied to BOOT and profile rails are off during sampling |
| broken peer | S3/C5 native USB/EN/boot independent; RP has USB/SWD/RUN |

## Collision and reserve result

| Candidate | S3 | C5 | Extra controller | Conclusion |
|---|---|---|---|---|
| `SYN-2A` | 35 used, 1 strap-reserved | 21 used | none | collision-free; no general-purpose reserve |
| `SYN-2B` | 33 used, 3 strap/recovery-reserved | 17 used, 4 strap/recovery-reserved | none | collision-free; no safe generic reserve |
| `SYN-3A` | 34 used, 2 strap-reserved | 9 product-used, 2 service-reserved, 5 strap/recovery-reserved, 5 free | RP 30/30 + dedicated recovery | collision-free; five generic C5 GPIO remain plus dedicated UART0 diagnostics |

All three pass the exact collision gate. `SYN-2A` required the no-loss correction `FND-0034`; `SYN-2A/2B` have effectively zero expansion margin. `SYN-3A` pays another firmware target but is the only map with non-strap MCU GPIO headroom.

`PIN-0002` receives **«Проведено ревью»**. It proves signal/controller placement, not memory, traffic, power, RF, availability or total cost.
