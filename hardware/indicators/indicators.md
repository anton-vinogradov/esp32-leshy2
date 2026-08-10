# Leshy2 — Indicators & I/O sheet (Sheet 6)

*Read this in: **English** · [Русский](indicators.ru.md)*

The last sheet: the per-chain **hardware TX-live LEDs** (RF envelope detectors, 0 GPIO), the **WS2812** status LED, the **buzzer**, **IR** transmit/receive, the **microSD** card, the **rotary encoder**, and the physical **RESET / BOOT / PTT** buttons. Every net here is owned by the **ESP32-S3**; pin numbers come from [Sheet 2](../c5-buses/c5-buses.md), slow lines ride the PCA9555 expanders.

> ⚠️ Design stage. Detector coupling, LED series values and the IR drive current are starting points to confirm on real hardware. Keep every indicator **dim** — this is a receiver, and bright LEDs both waste battery and leak light in the field.

## Blocks and parts

| Ref | Part | Role | Interface |
|-----|------|------|-----------|
| D50–D56 | 7× amber LED + envelope detector | **TX-live** — honest "on air" per transmit chain | **hardware, 0 GPIO** |
| Q50–Q56 | 7× NPN (or Schottky + comparator) | detector output → LED | analog |
| DS1 | **WS2812** RGB | general device / status LED | `WS2812` = S3 GPIO1 (RMT), +5V |
| U51 | **74AHCT1G125** buffer | WS2812 DIN level shift 3V3→5V | +5V, TTL input |
| LS2 | Active buzzer + Q57 | alerts / proximity "geiger" | `BUZZER` = PCA9555 #1 P0.5, +5V |
| D57 + Q58 | IR LED + drive transistor | clone / replay remotes (TX) | `IR_TX` = S3 GPIO2 (38 kHz carrier), +5V |
| U50 | **TSOP38238** IR receiver | read remotes (RX) | `IR_RX` = S3 GPIO42 (RMT), +3V3 |
| J50 | microSD socket (SPI mode) | PCAP logs, profiles | SPI + CS = 74HC138 **Y0**; `SD_CD` = PCA9555 #1 P1.7 |
| SW10 | Rotary encoder + push | navigation (sole onboard input) | `ENC_A`=GPIO40, `ENC_B`=GPIO41, `ENC_SW`=PCA9555 #1 P0.0 |
| SW11–SW13 | RESET / BOOT / PTT buttons | system + push-to-talk | `RESET`=EN, `BOOT`=GPIO0, `PTT_BTN`=PCA9555 #2 P0.0 |

## TX-live LED — the honest "on air" light (×7)

Each **transmit** chain gets an amber LED that lights from the **real RF emission**, not from firmware:

```
antenna feed ─┤├─ (light coupling cap / directional tap)
              └─►│─ Schottky env-detect ─┬─ small cap ─┬─ NPN base
                                          │             └─ → amber LED ─ Rdim ─ +3V3
                                          └─ bleed R to GND
```

- **0 GPIO.** Fully analog — it fires whenever that chain radiates, **even if the firmware hangs or crashes**. That is the whole point: a truthful transmit indicator.
- **TX chains only (7):** C5 Wi-Fi/BLE, 3× nRF24, CC1101, SA868, SX1262 (LoRa). The **Si4732 is receive-only → no LED**; a detector on a receive input would spoil its sensitivity. The **S3's own 2.4 GHz** is the always-on phone/control link, so a TX light there would sit lit and mean nothing — it is left off deliberately.
- **Light coupling.** The tap must barely load the RF path (a small series cap or a short coupled line), so it costs almost no transmit power.
- **Dim by design.** A high series resistor keeps it a soft glow.
- **Cross-chip.** The C5's LED reads the C5's own antenna feed — the detector is pure analog and does not care which MCU drove the transmission.

## WS2812 status LED

One addressable RGB (DS1) on the S3's `GPIO1` (RMT timing), powered from `+5V`, kept dim. **Its DIN needs a 3.3 V→5 V level shift:** at VDD 5 V the WS2812 logic-high threshold is ~3.5 V — above the S3's 3.3 V — so DIN goes through a **74AHCT1G125** (U51, +5V rail, TTL input). Alternatives: a 3.3 V-native part (SK6812) or dropping the LED VDD to ~4.3 V with a series diode. It shows overall device state (mode, battery, alerts) — the display carries the detail, so one LED is enough. If more are ever wanted, chain `DOUT → DIN`.

> **Back-power rule:** the WS2812 and its buffer sit on `+5V`. Before gating `+5V` off (`RAIL_EN_5V` low), drive `GPIO1` **low** first — a high DIN output would back-power the dead rail through the 74AHCT1G125 input clamp. Same discipline as `IR_TX` on GPIO2.

## Buzzer

An **active** (self-oscillating) buzzer on `PCA9555 #1 P0.5` through a transistor (Q57) — on/off tones for alerts and the RSSI "geiger". A passive buzzer with melodies would need a PWM GPIO the budget can't spare; the active part trades tune flexibility for a free pin. Powered from `+5V`, so it is silent whenever the +5V rail is gated off.

## IR

- **TX:** an IR LED (D57) driven by Q58 from `GPIO2` with a 38 kHz carrier (LEDC/RMT), off the `+5V` rail. The LED needs ~100 mA pulses, so it is transistor-driven, not straight off the GPIO. GPIO2 is **not** a strapping pin on the S3. Same back-power rule as the WS2812: pull GPIO2 low before gating +5V off.
- **RX:** a **TSOP38238** demodulating receiver into `GPIO42` (RMT capture) on `+3V3`, with a 100 nF close to its supply.

## microSD

Standard **SPI-mode** microSD (J50) on the shared SPI2 bus, chip-select from the 74HC138 (**Y0**). 3.3 V native (no level shift on the S3). Add a 10 µF + 100 nF at the socket and, on longer traces, small series resistors on CLK/CMD/DAT. Being on the shared bus, logging interleaves with radio SPI under one-device-at-a-time — **issue 8+ dummy clocks after deselecting the card** before addressing a radio, since some cards hold MISO for a few clocks after CS releases. The socket's **card-detect** switch is `SD_CD` on `PCA9555 #1 P1.7`.

## Rotary encoder

The sole onboard navigation input: quadrature `ENC_A`/`ENC_B` on `GPIO40`/`GPIO41` (pulled up, direct for clean stepping), push `ENC_SW` on `PCA9555 #1 P0.0`. Long text is entered from the phone over BLE. Extra buttons, if ever wanted, also go on a PCA9555.

## Physical buttons

Three momentary buttons, all on the S3 (the C5 has none — the S3 drives its `EN`/`BOOT`):

- **RESET** (SW11) — across S3 **EN**–GND (10 kΩ pull-up + 1 µF RC).
- **BOOT** (SW12) — from S3 **GPIO0** to GND; hold BOOT and tap RESET to force USB download.
- **PTT** (SW13) — push-to-talk to GND on `PCA9555 #2 P0.0`; the expander INT wakes the S3, which keys the SA868 walkie.

Power on/off is the **master toggle switch** (Sheet 1) — there is no soft power button and no mode switch.

## Key nets

| Net | Owner pin | Notes |
|-----|-----------|-------|
| `WS2812` | S3 GPIO1 (RMT) | +5V, 74AHCT1G125 shift; **low before +5V gate-off** |
| `IR_TX` | S3 GPIO2 (LEDC/RMT) | +5V, transistor; **low before +5V gate-off** |
| `IR_RX` | S3 GPIO42 (RMT) | +3V3, TSOP38238 |
| `ENC_A` / `ENC_B` | S3 GPIO40 / GPIO41 | pull-up, direct quadrature |
| `ENC_SW` | PCA9555 #1 P0.0 | encoder push |
| `BUZZER` | PCA9555 #1 P0.5 | +5V, active buzzer via Q57 |
| `SD_CD` | PCA9555 #1 P1.7 | card-detect |
| `PTT_BTN` | PCA9555 #2 P0.0 | INT-wakes S3 → keys SA868 |
| `SD_CS` | 74HC138 Y0 | microSD on shared SPI2 |
| TX-live LEDs | none | 7× analog envelope detectors, 0 GPIO |

## Gotchas

- **TX-LED is not a software LED.** Do not try to drive it from a GPIO — its value is that it reports physics, not code. The only software indicator is the WS2812.
- **Keep it dim.** Field use and battery life both punish bright indicators; size every series resistor for a soft glow.
- **+5V back-power.** `WS2812` (GPIO1) and `IR_TX` (GPIO2) both sit on +5V through a buffer/driver. Drive both **low** before `RAIL_EN_5V` goes low, or a high output back-powers the dead rail through the input clamp.
- **IR LED current.** Never drive the IR LED directly from a pin — use Q58; peak pulses exceed GPIO limits.
- **microSD on the shared bus.** Do not access the card mid-transaction with a radio; the 74HC138 selects one device at a time, so the firmware must sequence SD vs radio access, and issue 8+ dummy clocks after SD deselect.
- **No RX LEDs.** Only transmit chains get a TX-live light; a detector on the Si4732 (or any listen path) would rob receive sensitivity.

---

*This completes the sheet-by-sheet schematic. Previous: (5) [expansion](../expansion/expansion.md). Whole design: [Leshy2](../../README.md).*
*Part of [Leshy2](../../README.md) · MIT.*
