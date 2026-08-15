# Leshy2 — controls & firmware conventions

*Read this in: **English** · [Русский](firmware-controls.ru.md)*

The physical control set is fixed; most of the usability lives in **firmware
conventions**. A control-coverage review (74 scenarios) found the hardware set
**sufficient** — no scenario lacks a physical path — but flagged **two safety
blockers** and a set of conventions without which most flows degrade. Those are
firmware requirements, captured here so the layout and the firmware stay in sync.

## Physical controls

| Control | Where | Role |
|---|---|---|
| **D-pad (5-way)** | front | Up / Down / Left / Right / Center(OK) — navigation |
| **BACK** | front | up a level / cancel / (in active TX) stop |
| **OPTIONS** | front | context menu of the current mode |
| **Encoder wheel** (rotate + push) | left edge | a value / scroll wheel, context-dependent |
| **F1 / F2** | left edge | context function keys |
| **PTT** | right edge | walkie transmit (SA868) |
| **STOP** | right edge | hardware panic key |
| **Master toggle** | bottom | the only true on/off (hard, cuts the pack) |
| **RESET / BOOT** | bottom | recessed, dev / flashing only |

All buttons except PTT (on PCA9555 #2) sit on a **third PCA9555 (0x22)**, read over
I²C via one shared INT. Consequence: fast navigation must be **encoder rotation**,
not D-pad hold, and long-press / combo timing must budget the expander read latency.
There is **no second hardware encoder** (A/B are timing-critical; GPIO is full).

## Safety blockers (must be in firmware)

1. **Orderly shutdown.** The master toggle cuts power instantly (no ship-mode), so an
   in-flight PCAP / log would corrupt. Provide **OPTIONS → Shut down** (and/or a
   long-BACK menu): flush SD, park all radios, orderly-stop S3 + C5, then a
   *"safe to flip the switch"* screen. Backstop: periodic flush + a brown-out flush.
2. **Panic-stop of transmit.** A stuck TX (deauth, beacon spam, nRF24 / CC1101 / LoRa
   jam, latched PTT) with a hung UI must be stoppable without pulling power. A **core
   long-BACK (or long encoder-press) = "stop all TX"** handler runs over any screen.
   The physical **STOP** key is the dedicated hardware path to the same handler.

## Conventions

1. **Encoder role is hard-contextual**, with a persistent on-screen chip (VOL / TUNE /
   STEP / ZOOM): list → scroll (×10 on hold), numeric field → value, spectrum /
   waterfall with no audio → zoom, audio mode (Si4732 / FM / SA868-RX) → volume. Never
   nail the default to "volume".
2. **Encoder press:** short = toggle coarse/fine or cycle target; long = mute. Never two
   unrelated functions on one press event.
3. **long-BACK / long-ENC = stop all TX**, over any screen, in any mode (see blocker 2).
4. **BACK:** single = up a level (in active TX the first press = stop-TX); long = home.
5. **Shut down** (blocker 1) is a first-class OPTIONS item + a long-press.
6. **OPTIONS + Left / Right = global prev / next mode**, always mirrored by an OPTIONS
   menu item — a combo is never the only path.
7. **OPTIONS → Band** is the canonical CC1101 315 / 433 / 868 / 915 band switch; a
   Left/Right shortcut only outside numeric-edit; the current band is always in the header.
8. **Arm / fire are separate.** TX / attacks sit behind a distinct gesture (long-press
   Center or an OPTIONS confirm) + an explicit *"armed"* indicator (red WS2812 + TX LED);
   a bare Center on a target list never fires.
9. **Numeric entry** = one digit-cursor widget (D-pad = digit, encoder = value, press =
   cycle step 1 / 10 / 100) + frequency / band presets and a CTCSS list in OPTIONS.
10. **Delete confirmation** modal defaults focus to "Cancel"; bulk delete via
    OPTIONS → Select multiple.
11. **Text entry:** canned messages / quick-replies + a one-button *"send GPS position"*
    as the first-class path; an encoder char-wheel as fallback; **a phone keyboard is the
    primary path for long text** (state it in the UI). Auto-name files / IR codes
    (timestamp + GPS + mode); manual rename optional.
12. Every **combo (OPTIONS + direction) is mirrored** by an OPTIONS item and/or a
    long-press — combos are accelerators only (one-handed / gloves).
13. **PTT is live only** when a radio mode is foregrounded and armed; inert elsewhere;
    debounce + a minimum hold-to-talk; edit channel / CTCSS only in RX.
14. A persistent **"TX active" banner** when leaving an attack screen (mirror the hardware
    TX LED on-screen); OPTIONS → "Stop all".

## Text keyboard from a phone (no new hardware)

Long text (Meshtastic messages, Wi-Fi passwords, SSIDs, file names) is typed on a paired
phone — the Apple-TV pattern — over radios the device already has:

- **BLE companion** (preferred): the device is a BLE peripheral with a text-input
  characteristic; the phone writes to it. Keeps Wi-Fi free during attacks. Needs a small
  companion app on iOS (Android can use Web Bluetooth in the browser).
- **Wi-Fi captive portal** (fallback): the device hosts an AP + a tiny web page with a
  text box; works on any phone with no app, but uses the Wi-Fi radio.

The D-pad char-wheel stays as the offline fallback for short entry.

## Hardware bring-up note

- **Backlight** has no PWM path yet (`LCD_BL_EN` is on/off via the slow expander).
  Brightness is a toggle until a boost / constant-current LED driver + a PWM pin are
  added (a bring-up decision — see the [power sheet](../hardware/power/power.md)).

*Part of [Leshy2](../README.md) · MIT.*
