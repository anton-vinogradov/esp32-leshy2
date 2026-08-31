# H0-R2 · Functional architecture

H0-R2 is the new functional baseline: UI and display remain local to S3, high-throughput peripheral work is offloaded through the Hub RP, the onboard video path is removed, and 118–137 MHz Airband AM is now mandatory.

> The exact current marker is **H3-R2.5**. The H1-R2.37 physical projection with two independent RP2354B domains, exact GPIO0..47 maps, M1 and 226 bodies was accepted and reviewed on 2026-08-30. Native R2 H2 materializes 1,185 instances and 823 nets in three KiCad projects with zero ERC findings. H3-R2.0 freezes inputs, provenance and methods; H3-R2.1 through R2.4 are reviewed. H3-R2.4 proves levels, timing, USB/service ownership, M1 and direct i8080-8 at an exact 20 MHz. H3-R2.5 verifies RF feeds, coexistence, quiet states and concurrent service of three nRF24 paths.

![H0-R2 functional architecture](images/h0-r2-functional-architecture.svg)

## Accepted result

- One user port is labelled `FM / SW / AIR RX`; no new external connector is added.
- Airband is a `BROADCAST_RX` submode, so its RF domain cannot run together with a TX group.
- Buttons stay on the S3-local TCA9539PWR path while encoder and USB remain direct; direct i8080-8 provides 20 MB/s at an exact 20 MHz from the standard ESP-IDF divider.
- The front RP owns three nRF24 paths and microSD; the rear RP owns Si4732/Airband, CC1101, voice, audio, M5 and exactly one U214/U219 profile.
- M1 carries control/status, safety, USB and power; contact 35 carries latched FAULT_KILL to the front indicator and contact 36 is the independent S3 fault-UI reset.

## Airband RX

`shared FM/SW/AIR SMA protection and mode split` → `118-137-MHz image-rejection band-pass network` → `PGA-103+ low-noise gain stage` → `LT5560EDD#TRPBF down-converting mixer` → `112-MHz LO from SI5351A-B-GTR` → `6-25-MHz IF cleanup network` → `paired HMC544AETR input/output isolation selectors` → `existing Si4732-A10-GSR FMI and audio path`

The fixed 112 MHz low-side LO maps 118–137 MHz to 6–25 MHz. The image band is 87–106 MHz, so the input band-pass network is a mandatory functional safety/performance element rather than an optional cleanup filter.

## GPIO and ownership

| GPIO | Function | Reset behavior |
|---|---|---|
| Rear RP GP35 | `AIR_RX_EN` | pulled low; LNA/mixer/LO domain off |
| Rear RP GP36 | `AIR_RX_MODE` | direct FM/SW path selected |

Front RP budget: **47 used / 1 free**. Rear RP budget: **43 used / 5 free**. SI5351 control stays on the rear-local I²C bus at `0x60`; no Airband control traffic uses the S3 UI bus.

## Working principle pin design

This is the complete H0-R2 working principle budget, not authorization to begin KiCad. H1 may change a contact only together with this source, its checks and this public table.

| S3 GPIO | Net | Peripheral | Direction |
|---:|---|---|---|
| `0` | `S3_BOOT_N` | `BOOT_STRAP` | `in` |
| `1` | `SYS_UI_I2C_SDA` | `I2C0` | `io` |
| `2` | `SYS_UI_I2C_SCL` | `I2C0` | `out` |
| `3` | `UI_HUB_ALERT_N` | `GPIO_IRQ` | `in` |
| `4` | `LCD_DB0` | `LCD_CAM_TX` | `out` |
| `5` | `LCD_RST_N` | `GPIO` | `out` |
| `6` | `TOUCH_RST_N` | `GPIO` | `out` |
| `7` | `S3_UART_SERVICE_TX` | `UART1_TX` | `out` |
| `8` | `S3_UART_SERVICE_RX` | `UART1_RX` | `in` |
| `9` | `LCD_DB1` | `LCD_CAM_TX` | `out` |
| `10` | `S3_RESERVE_10` | `GPIO` | `reserve` |
| `11` | `S3_RESERVE_11` | `GPIO` | `reserve` |
| `12` | `S3_RESERVE_12` | `GPIO` | `reserve` |
| `13` | `S3_RESERVE_13` | `GPIO` | `reserve` |
| `14` | `S3_HUB_D1` | `SPI3` | `io` |
| `15` | `S3_RESERVE_15` | `GPIO` | `reserve` |
| `16` | `S3_RESERVE_16` | `GPIO` | `reserve` |
| `17` | `LCD_WR_N` | `LCD_CAM_TX` | `out` |
| `18` | `LCD_DB2` | `LCD_CAM_TX` | `out` |
| `19` | `S3_USB_DM_LOCAL` | `USB_SERIAL_JTAG` | `io` |
| `20` | `S3_USB_DP_LOCAL` | `USB_SERIAL_JTAG` | `io` |
| `21` | `S3_HUB_D0` | `SPI3` | `io` |
| `38` | `LCD_DB3` | `LCD_CAM_TX` | `out` |
| `39` | `ENCODER_A` | `PCNT0` | `in` |
| `40` | `LCD_DB4` | `LCD_CAM_TX` | `out` |
| `41` | `LCD_DB5` | `LCD_CAM_TX` | `out` |
| `42` | `LCD_DB6` | `LCD_CAM_TX` | `out` |
| `43` | `S3_HUB_D2` | `SPI3` | `io` |
| `44` | `S3_HUB_D3` | `SPI3` | `io` |
| `45` | `LCD_DC` | `LCD_CAM_TX` | `out` |
| `46` | `LCD_DB7` | `LCD_CAM_TX` | `out` |
| `47` | `ENCODER_B` | `PCNT0` | `in` |
| `48` | `S3_HUB_SCK` | `SPI3` | `out` |

| Front RP GPIO | Assignment |
|---|---|
| `0, 1, 2, 3, 4, 5` | exclusive point-to-point S3 quad-SPI D0..D3/SCK plus wired-OR UI_HUB_ALERT_N; no redundant chip-select wire |
| `7, 8, 9, 10, 11, 12` | C5 native 4-bit SDIO CLK/CMD/D0..D3 |
| `13, 14, 15, 16, 17` | dedicated SPI plus ALERT to RF RP |
| `18, 19, 20, 21, 22, 23` | nRF24 #0 dedicated SPI SCK/MOSI/MISO/CS plus CE and IRQ |
| `24, 25, 26, 27, 28, 29` | nRF24 #1 dedicated SPI SCK/MOSI/MISO/CS plus CE and IRQ |
| `30, 31, 32, 33, 34, 35` | nRF24 #2 dedicated SPI SCK/MOSI/MISO/CS plus CE and IRQ |
| `36` | FAULT_KILL-qualified common nRF24 switched-rail request |
| `37, 38, 39, 40, 41, 44` | dedicated microSD SPI SCK/MOSI/MISO/CS plus power and detect |
| `42, 43` | dedicated fail-closed I2C1 controller bus to Pack and Safety MSPM0 mailboxes |
| `45` | LCD_TE direct front-local edge capture; Hub timestamps/alerts S3 without consuming another S3 GPIO |
| `46` | LCD_BL_PWM front-local backlight gate drive with the existing hardware reset-off pull-down |
| `6` | AON Pack/PD mailbox alert through M1.59 |
| `47` | uncommitted electrical reserve |

| Rear RP GPIO | Assignment |
|---|---|
| `0, 1, 2, 3, 6` | full-duplex codec/audio BCLK/WS/DOUT/DIN/ARM |
| `4, 5` | rear-local hardware I2C0 for codec, Si4732, headset and slow controls |
| `7, 8` | rear-local isolated M5 Unit PIO-I2C/PIO-UART/GPIO profile |
| `9, 10, 11, 23, 39, 42, 43` | CC1101 CS/GDO0/GDO2/power plus dedicated PIO SPI |
| `12, 13, 14, 30, 31, 40, 41, 44, 45, 46, 47` | exactly one U214/U219 profile: busy/IRQ/reset-or-power, hardware I2C1, GNSS-or-RF controls and dedicated SPI |
| `16, 17, 18, 20, 21, 22` | voice UART/PTT/audio-on, direct PTT input and ANY_TX diagnostic |
| `19, 24, 25, 26, 27` | dedicated SPI plus ALERT to front RP |
| `28, 29` | power-coherent private PIO I2C for Si5351; pull-ups disappear with 3V3_AIR_SWITCHED |
| `35` | AIR_RX_EN fail-low switched-domain and LT5560 enable control |
| `36` | AIR_RX_MODE direct-FM/SW versus converted-Airband selector; reset default direct |
| `15` | Schmitt-conditioned rear-local slow-I/O interrupt |
| `32, 33, 34, 37, 38` | uncommitted electrical reserve |

## Power

The old R1 2.5 A limit is no longer current. Airband reserves 150 mA / 0.5 W; the new H1 gate is at least 3.8 A continuous and 4.2 A step, with buck/eFuse/inductor/copper/thermal requalification.

## Factory BOM delta

| MPN | JLCPCB | Role | Route | Stock | Price, $ |
|---|---|---|---|---:|---:|
| `LT5560EDD#TRPBF` | `C462645` | active down-converting mixer | JLCPCB Standard-PCBA SMT | 165 | 14.5398 |
| `PGA-103+` | `C3008207` | 118-137-MHz low-noise gain | JLCPCB Standard-PCBA SMT | 1441 | 2.6063 |
| `SI5351A-B-GTR` | `C504891` | 112-MHz local oscillator | JLCPCB Standard-PCBA SMT | 36999 | 1.2180 |
| `HMC544AETR` | `C579555` | paired low-loss input/output isolation selectors | JLCPCB Standard-PCBA SMT | 2004 | 3.1529 |
| `SI4732-A10-GSR` | `C2155558` | existing FM/AM/SW/LW receiver reused for 6-25-MHz IF | existing R1 line; no incremental quantity | 547 | 2.8621 |

Incremental active-component cost: **`$24.6699`** before passives, PCB and assembly. The existing Si4732 line is reused and is not counted in that delta.

`BPF-A127+` has no exact JLCPCB catalogue match. It is the published response-mask reference; production uses a serial LC ladder made from factory passives, not a custom part. Its exact MPNs close after H1 RF synthesis and layout extraction.

## Honest capability boundary

Included:

- AM voice reception
- 25-kHz and 8.33-kHz channel plans
- scan and banks
- recording
- channel-activity history
- ACARS 2400-bps demodulation after the receiver

Excluded:

- Airband transmit
- simultaneous 19-MHz-wide spectrum capture
- VDL Mode 2
- certified VOR/ILS navigation

## What H1-R2 must close

- complete the canonical coordinate register for the existing Cap-Bus ESD, series, supervisor, bypass and evidence-aggregate bodies
- complete exact U219 support-passive values/MPNs and prove their courtyards inside the bounded placement islands
- obtain controlled U219 field-structure geometry or measure a received unit before locating the printed NFC pickup loop and DNP C0G bank
- measure the installed U219 RP-SMA antenna swept volume against the rear connector bank, enclosure and user hand access
