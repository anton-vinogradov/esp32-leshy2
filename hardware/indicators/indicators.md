# Leshy2 — Indicators & I/O sheet (Sheet 6)

*Read this in: **English** · [Русский](indicators.ru.md)*

The last sheet: the per-antenna **hardware TX-live LEDs** (RF envelope detectors, 0 GPIO), the **WS2812** status LED, the **buzzer**, **IR** transmit/receive, the **microSD** card, and the **rotary encoder** input. Pin numbers come from [Sheet 2](../c5-buses/c5-buses.md); slow lines are on the PCA9555.

> ⚠️ Design stage. Detector coupling, LED series values and the IR drive current are starting points to confirm on real hardware. Keep every indicator **dim** — this is a receiver, and bright LEDs both waste battery and leak light in the field.

## Blocks and parts

| Ref | Part | Role | Interface |
|-----|------|------|-----------|
| D50–D56 | 7× amber LED + envelope detector | **TX-live** — honest "on air" per transmit chain | **hardware, 0 GPIO** |
| Q50–Q56 | 7× NPN (or Schottky + comparator) | detector output → LED | analog |
| DS1 | **WS2812** RGB | general device / status LED | `WS2812` = GPIO27 (RMT), +5V |
| U51 | **74AHCT1G125** buffer | WS2812 DIN level shift 3V3→5V | 5 V, TTL input |
| LS2 | Active buzzer + Q57 | alerts / proximity "geiger" | `BUZZER` = PCA9555.P0.5, +5V |
| D57 + Q58 | IR LED + drive transistor | clone / replay remotes (TX) | `IR_TX` = GPIO7 (38 kHz carrier), +5V |
| U50 | **TSOP38238** IR receiver | read remotes (RX) | `IR_RX` = GPIO10 (RMT), +3V3 |
| J50 | microSD socket (SPI mode) | PCAP logs, profiles | SPI + CS = 138 **Y0** |
| SW10 | Rotary encoder + push | navigation (sole input) | `A`=GPIO4, `B`=GPIO5, `SW`=PCA9555.P0.0 |

## TX-live LED — the honest "on air" light (×7)

Each **transmit** chain gets an amber LED that lights from the **real RF emission**, not from firmware:

```
antenna feed ─┤├─ (light coupling cap / directional tap)
              └─►│─ Schottky env-detect ─┬─ small cap ─┬─ NPN base
                                          │             └─ → amber LED ─ Rdim ─ +3V3
                                          └─ bleed R to GND
```

- **0 GPIO.** Fully analog — it fires whenever that chain radiates, **even if the firmware hangs or crashes**. That is the whole point: a truthful transmit indicator.
- **TX chains only (7):** C5 Wi-Fi/BLE, 3× nRF24, CC1101, SA868, SX1262 (LoRa). The **Si4732 is receive-only → no LED**; a detector on a receive input would spoil its sensitivity.
- **Light coupling.** The tap must barely load the RF path (a small series cap or a short coupled line), so it costs almost no transmit power.
- **Dim by design.** A high series resistor keeps it a soft glow.

## WS2812 status LED

One addressable RGB (DS1) on `GPIO27` (RMT timing), powered from `+5V`, kept dim. **Its DIN needs a 3.3 V→5 V level shift:** at VDD 5 V the WS2812 logic-high threshold is ~3.5 V — above the C5's 3.3 V — so DIN goes through a **74AHCT1G125** (U51, 5 V rail, TTL input). Alternatives: a 3.3 V-native part (SK6812) or dropping the LED VDD to ~4.3 V with a series diode. It shows overall device state (mode, battery, alerts) — the display carries the detail, so one LED is enough. If more are ever wanted, chain `DOUT → DIN`.

## Buzzer

An **active** (self-oscillating) buzzer on `PCA9555.P0.5` through a transistor — on/off tones for alerts and the RSSI "geiger". A passive buzzer with melodies would need a PWM GPIO the budget can't spare; the active part trades tune flexibility for a free pin.

## IR

- **TX:** an IR LED driven by Q58 from `GPIO7` with a 38 kHz carrier (LEDC/RMT). The LED needs ~100 mA pulses, so it is transistor-driven, not straight off the GPIO.
- **RX:** a **TSOP38238** demodulating receiver into `GPIO10` (RMT capture), with a 100 nF close to its supply.

## microSD

Standard **SPI-mode** microSD (J50) on the shared bus, chip-select from the 74HC138 (**Y0**). 3.3 V native (no level shift on the C5). Add a 10 µF + 100 nF at the socket and, on longer traces, small series resistors on CLK/CMD/DAT. Being on the shared bus, logging interleaves with radio SPI under one-radio-at-a-time — **issue 8+ dummy clocks after deselecting the card** before addressing a radio, since some cards hold MISO for a few clocks after CS releases. The socket's optional **card-detect** switch goes on a spare PCA9555 port.

## Rotary encoder

The sole onboard input: quadrature `A`/`B` on `GPIO4`/`GPIO5` (pulled up, direct for clean stepping), push `SW` on the PCA9555. Long text is entered from the phone over BLE. Extra buttons, if wanted, also go on the PCA9555. The system controls — RESET and BOOT buttons (Sheet 2) and the POWER **master switch** (Sheet 1) — live on their own sheets, not here.

## Gotchas

- **TX-LED is not a software LED.** Do not try to drive it from a GPIO — its value is that it reports physics, not code. The only software indicator is the WS2812.
- **Keep it dim.** Field use and battery life both punish bright indicators; size every series resistor for a soft glow.
- **IR LED current.** Never drive the IR LED directly from a pin — use the transistor; peak pulses exceed GPIO limits.
- **microSD on the shared bus.** Do not access the card mid-transaction with a radio; the 74HC138 selects one device at a time, so the firmware must sequence SD vs radio access.

---

*This completes the sheet-by-sheet schematic. Previous: (5) [expansion](../expansion/expansion.md). Whole design: [Leshy2](../../README.md).*
*Part of [Leshy2](../../README.md) · MIT.*
