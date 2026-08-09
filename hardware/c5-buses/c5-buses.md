# Leshy2 — C5 + buses sheet (Sheet 2)

*Read this in: **English** · [Русский](c5-buses.ru.md)*

The ESP32-C5 and how every bus fans out from it: the shared SPI bus with its **74HC138** chip-select decoder, I²C (with the **PCA9555** slow-signal expander), UART to the SA868, the display `DC`/`CS`/`RESX`, the rotary encoder, USB, and the reset/boot circuit. See [c5-buses-schematic.svg](c5-buses-schematic.svg) for the drawing, and [../../docs/pin-budget.md](../../docs/pin-budget.md) for the pin logic.

> ⚠️ Design stage. The **GPIO numbers below are a proposed map**, not yet confirmed against the ESP32-C5 datasheet. Before capture, confirm: strapping-pin boot levels (add the datasheet-recommended pulls), which pins reach the RMT/FSPI/I²C peripherals, and USB/UART-console reuse. Functions are fixed; exact pin numbers may shift.

## The MCU

**U10 — ESP32-C5-WROOM-1U-N8R4** (or -N16R8): single RISC-V core, native Wi-Fi 2.4 **and** 5 GHz + BLE + 802.15.4, **8/16 MB flash + 4/8 MB PSRAM in-package**. The PSRAM holds the 320×480×2 ≈ 300 KB display framebuffer and the firmware-port working set. In-package flash/PSRAM occupies GPIO16–22 (not brought out); native USB is on GPIO13/14.

**Antenna: the -1U variant brings the RF out on a u.FL connector** → an external dual-band SMA on top (this is the 8th onboard antenna). Keep a copper keep-out under the u.FL/coax, and tune 2.4 / 5 GHz on real hardware. A hardware TX-live LED taps this feed (Sheet 6).

## GPIO map (proposed)

~20 usable GPIO (GPIO0–28 minus flash/PSRAM 16–22 minus USB 13/14). **Direct signal pins = 19; GPIO28 = BOOT button, EN = RESET**; power on/off is the **master switch** (Sheet 1). That is the full 20 — no spare direct pin (LoRa `DIO1` is polled to stay within it).

| C5 GPIO | Net | Dir | Peripheral / note |
|:--:|------|:--:|-------|
| GPIO23 | `SPI_SCK` | out | FSPI (via GPIO matrix) |
| GPIO24 | `SPI_MOSI` | out | FSPI |
| GPIO6 | `SPI_MISO` | in | FSPI |
| GPIO0 | `I2C_SDA` | o-d | ext 4.7 kΩ pull-up; I²C idle-high = normal boot |
| GPIO1 | `I2C_SCL` | o-d | ext 4.7 kΩ pull-up |
| GPIO11 | `UART_TX` → SA868 | out | UART0 console repurposed (flash over USB) |
| GPIO15 | `UART_RX` ← SA868 | in | UART0 |
| GPIO2 | `HC138_A` | out | ⚠ strap: crystal-freq select — boot pull to match module xtal (40 MHz = low) |
| GPIO3 | `HC138_B` | out | ⚠ strapping — add pull |
| GPIO25 | `HC138_C` | out | ⚠ strapping — add pull |
| GPIO12 | `LCD_DC` | out | UART0-RX console repurposed |
| GPIO8 | `CC1101_GDO0` | i/o | RMT (raw OOK): RX capture and TX-replay drive |
| GPIO9 | `LoRa_BUSY` | in | polled before each SX1262 command |
| GPIO10 | `IR_RX` | in | RMT (demod capture) |
| GPIO4 | `ENC_A` | in | pull-up; quadrature |
| GPIO5 | `ENC_B` | in | pull-up; quadrature |
| GPIO26 | `nRF24_CE` | out | ⚠ strapping — add pull; 3 modules tied |
| GPIO7 | `IR_TX` | out | ⚠ strapping — add pull; RMT/LEDC carrier |
| GPIO27 | `WS2812` | out | ⚠ boot strap: **must be high** at reset → pull-up; RMT; **5 V level shifter** (Sheet 6) |
| GPIO13 | `USB_D−` | — | native USB (flashing + data) |
| GPIO14 | `USB_D+` | — | native USB |
| GPIO28 | `BOOT` button | in | boot strap: low → serial download; internal + external pull-up |

**Not on a direct pin:** `LoRa_DIO1` is **polled** over SPI (`GetIrqStatus`); `nRF24 IRQ` is polled over SPI too. All slow control lines are on the **PCA9555** (below), including the ones the review added — display `RESX`, backlight enable, LoRa T/R, audio mux, amp shutdown, and the 74HC138 enable.

## Blocks and parts

| Ref | Part | Role | Key notes |
|-----|------|------|-----------|
| U10 | **ESP32-C5-WROOM-1U** (PSRAM) | Brain + all radios' bus master | `+3V3`; EN + boot circuit; USB on 13/14; u.FL antenna |
| U11 | **74HC138** | 3→8 chip-select decoder | `A/B/C` = GPIO2/3/25; `G1`=+3V3, `G2B`=GND; **`G2A` = `HC138_EN`** from PCA9555 (pulled high = disabled at boot) |
| U12 | **PCA9555** | I²C GPIO expander for slow lines | I²C `0x20`; carries the 16 low-speed signals below |
| SW10 | Rotary encoder + push | Navigation | `A/B` = GPIO4/5 (direct); `SW` = PCA9555 |
| J10 | USB-C data tap | Flash + data + console | `D−/D+` = GPIO13/14; shares the J1 receptacle on the power sheet |
| — | Decoupling | C5 rails | 10 µF + 0.1 µF at each `+3V3` pin; 1 µF on EN |

### 74HC138 — chip-select map

| Output | Chip-select | On the SPI sheet |
|:--:|------|------|
| Y0 | `SD_CS` | microSD |
| Y1 | `CC1101_CS` | sub-GHz |
| Y2 | `nRF24_1_CSN` | 2.4 raw #1 |
| Y3 | `nRF24_2_CSN` | 2.4 raw #2 |
| Y4 | `nRF24_3_CSN` | 2.4 raw #3 |
| Y5 | `LoRa_NSS` | SX1262 |
| Y6 | `LCD_CS` | ST7796 display |
| Y7 | (none) | **idle / deselect-all address** |

Only one Y is low at a time, so only one device is ever selected. **`G2A` is gated by `HC138_EN`** (a PCA9555 output, pulled **high** at boot): the decoder stays fully disabled through the boot/strap window, and the firmware enables it only after the address lines are stable — this kills the spurious CS the always-enabled version would have asserted at reset. To talk to none (bus idle), the firmware parks `A/B/C` on **Y7**; a brief address-change transient is harmless because no SCK toggles during the switch.

### PCA9555 — slow-signal map (I²C, 0 host GPIO)

| Port | Signal | Dir | Goes to |
|:--:|------|:--:|------|
| P0.0 | `ENC_SW` | in | encoder push |
| P0.1 | `SA868_PTT` | out | walkie push-to-talk |
| P0.2 | `SA868_PD` | out | walkie power-down |
| P0.3 | `Si4732_RST` | out | HF receiver reset |
| P0.4 | `LoRa_NRESET` | out | SX1262 reset |
| P0.5 | `BUZZER` | out | active buzzer (on/off) |
| P0.6 | `LCD_RESX` | out | ST7796 reset |
| P0.7 | `MUX_SEL` | out | audio 2:1 source mux (Sheet 4) |
| P1.0 | `BQ_INT` | in | charger interrupt (Sheet 1) |
| P1.1 | `BQ_CD` | out | charger disable / pause (Sheet 1) |
| P1.2 | `LoRa_TR` | out | E22 T/R select → RXEN direct + TXEN via inverter (Sheet 3) |
| P1.3 | `PAM_SD` | out | speaker-amp shutdown (Sheet 4) |
| P1.4 | `LCD_BL_EN` | out | backlight driver enable (on/off) |
| P1.5 | `RFSW_CTL` | out | CC1101 band RF switch (Sheet 3) |
| P1.6 | `HC138_EN` | out | 74HC138 `G2A` gate (pulled high at boot) |
| P1.7 | — | — | spare (e.g. jack-detect) |

All 16 ports mapped, 1 spare. Timing-critical lines never go here — only resets, enables, PTT, buttons and mux selects. Battery gauge is read from the **BQ25887's own I²C ADC**, so no dedicated ADC pin is needed.

### Reset & boot buttons

Two physical buttons on the C5; the power on/off is the **master switch** (Sheet 1) — there is **no soft power button** (BQ25887 has no ship mode).

- **RESET (SW_RST)** — momentary across **EN**–GND. EN carries a power-on-reset RC (10 kΩ pull-up to `+3V3` + 1 µF to GND).
- **BOOT (SW_BOOT)** — momentary from **GPIO28** to GND. GPIO28 is the C5 download strap (low at reset → serial bootloader) with an internal pull-up; add an external pull-up too. Hold BOOT and tap RESET to force download. Normal flashing is over USB-JTAG, so this is the recovery path.

**Strap levels to honour at reset** (all sampled only at reset, then free): GPIO28 high = normal boot (pull-up). **GPIO27 must be high** for a valid download, so its WS2812 line gets a pull-up (`GPIO27=0` with `GPIO28=0` is invalid). GPIO2 selects the crystal frequency — set its boot pull to match the module (40 MHz = low). Confirm GPIO26's boot-config level. Drive all strap-shared signals only after reset.

## Key nets

```
SPI      : SCK(23) · MOSI(24) · MISO(6) → microSD, CC1101, 3× nRF24, SX1262, ST7796  (CS via U11)
LCD      : SPI + LCD_CS(U11.Y6) + LCD_DC(12) + LCD_RESX(PCA9555.P0.6) ; backlight driver EN = PCA9555.P1.4
I2C      : SDA(0) · SCL(1) → Si4732, u-blox GPS(0x42), PCA9555(0x20), BQ25887 ; Grove units (e.g. RFID2 0x28) plug in
UART     : TX(11) → SA868.RX ; RX(15) ← SA868.TX
138      : A(2) B(3) C(25) → U11 ; G1=+3V3, G2B=GND, G2A=HC138_EN(PCA9555.P1.6, boot=high/disabled)
ENC      : A(4) B(5) pulled-up ; SW → PCA9555.P0.0
IR       : RX(10, RMT) ; TX(7, RMT/LEDC)
WS2812   : DIN(27, RMT) → 5 V level shifter → DS1 ; kept dim
RESET    : EN → RC (10k pull-up + 1µF) + SW_RST to GND
BOOT     : GPIO28 (int + ext pull-up) → SW_BOOT to GND ; GPIO27 pull-up keeps download valid
USB      : D−(13) D+(14) → J1 CC-side data pair ; ESD array
```

## Gotchas

- **Strapping pins carry outputs on purpose.** GPIO2/3/7/25/26/27 are sampled only at reset, then are free. Each gets the datasheet-recommended pull so the board always powers up in normal boot mode; the driven load must not fight that pull at t=0.
- **74HC138 disabled through boot.** `G2A` is held high (disabled) by a pull-up until the firmware brings up the PCA9555 and drives `HC138_EN` low — no CS is asserted during the strap window.
- **Flashing is over USB** (GPIO13/14). That frees the UART0 console pins (GPIO11/12) for the SA868 UART and `LCD_DC`. Keep USB test pads; OTA is the field path.
- **PCA9555 is not for timing.** Anything edge-timed (`GDO0`, `BUSY`, IR, WS2812, encoder A/B) stays on a direct GPIO; the expander only carries resets, enables, PTT, mux and buttons. LoRa T/R is half-duplex and switches per-packet, so its I²C latency is fine.
- **I²C on GPIO0/1:** external pull-ups hold them high at boot (the normal-boot level); keep them modest (4.7 kΩ) and verify GPIO0 boot behaviour on the C5 before committing.

---

*Next sheets: (3) RF chains, (4) audio, (5) expansion, (6) indicators/IO. Previous: (1) [power](../power/power.md).*
*Part of [Leshy2](../../README.md) · MIT.*
