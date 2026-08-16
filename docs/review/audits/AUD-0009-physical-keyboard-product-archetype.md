# AUD-0009 — physical keyboard as a whole-product control archetype

- Статус: **Проведено ревью фактов; product-design disposition открыт**
- Дата snapshot: 2026-08-17
- Delta: `W-EXTRA-15`
- Предложение: [`IMP-0032`](../improvements/IMP-0032-keyboard-whole-product-comparison.md)
- Finding: [`FND-0046`](../findings/FND-0046-legacy-ui-layout-is-not-a-target-constraint.md)

## Уже принятый пользовательский результат

`REQ-SYS-0001` уже требует автономное локальное управление и доступный
on-device text input без телефона. Новый вопрос не в том, «можно ли напечатать
символ», а обязана ли permanent physical text keyboard определять корпус всего
устройства.

Input tasks materially different:

| Task class | Examples | Dominant control need |
|---|---|---|
| safety/immediate | STOP, PTT release, BACK/panic, re-arm ceremony | dedicated tactile physical controls independent of touch/keyboard focus |
| frequent field instrument | menu/list, scan start/stop, tune step, mark, zoom, threshold/power/channel adjustment | eyes-on-screen navigation with reliable one-hand repeat actions |
| sparse structured text | frequency/channel, SSID/password, callsign, filename/tag, FIDO PIN | local numeric/symbol/text editor; presets/history/scanning reduce typing but cannot remove it |
| sustained authoring/development | scripts, CLI commands, notes, long identifiers | physical keyboard is materially faster; USB console/external accessory is acceptable for nonessential long sessions if base text input remains complete |

A full keyboard does not replace STOP, PTT, BACK/cancel or positive
confirmation. Conversely, an on-screen editor satisfies autonomy but may be
slow for sustained authoring. These results must be scored separately.

## Current representative hardware

### Card-sized integrated keyboard

Current M5 Cardputer-Adv is 84×54×19.6 mm and 81 g with a 56-key 4×14 keyboard,
160 gf stated key actuation and a 1.14-inch 240×135 display. It demonstrates a
compact autonomous text terminal, but its front-face allocation also
demonstrates the trade: many keys coexist with a small visualization surface.
Leshy2 spectrum/waterfall/status/safety UI cannot assume that geometry is free.

### Landscape keyboard plus pointer

LILYGO T-Deck Plus is 100×68×11 mm with a 2.8-inch 320×240 display, physical
keyboard, trackball and 2000 mAh battery. It demonstrates that larger display
and keyboard can coexist by moving to a wider two-hand landscape class. Its
integrated GNSS consumes Grove pins, which is a useful warning that an attractive
form factor can silently consume general expansion.

### Compact field controls

Flipper Zero is autonomous at 100×40×25 mm/102 g with a sunlight-readable
1.4-inch 128×64 display, five-way D-pad and BACK. It proves that ordinary field
operation does not require a permanent text keyboard, though long text entry is
necessarily slower. T-Embed CC1101 shows another narrow instrument pattern:
97.5×39×31 mm, 1.9-inch 320×170 display and rotary encoder.

### External keyboard evidence

Current M5 Unit CardKB2 `U215` provides 42 keys on an 84.7×54.3×1.0 mm,
22.4 g board. It has M2 mounting holes, HY2.0 I²C/UART, USB recovery and its own
ESP32-C61 firmware; it also supports BLE HID/ESP-NOW and consumes 19.31 mA
standby from Grove. It is credible evidence for optional sustained text entry,
not a passive keypad and not proof that the base product needs no local editor.

If later qualified, a Leshy2 wired profile must explicitly select I²C/UART,
control accessory identity/version/update/recovery and not silently enable its
wireless modes. Its full 84.7×54.3 mm mechanical envelope is still a product
surface/mount decision.

## Whole-product consequences

| Dimension | Permanent integrated keyboard | Display-first field controls |
|---|---|---|
| text/CLI | fastest and always present | slower on-screen; optional external/USB for long sessions |
| frequent scan/tune/mark | needs separate nav/action controls or awkward layer chords | dedicated controls optimized for the task |
| safety | still needs independent STOP/PTT/BACK/confirmation | same mandatory dedicated controls |
| display | competes for front area unless body widens | can prioritize waterfall/status/readability |
| grip/use posture | tends toward two-thumb/card or landscape posture | can prioritize one-hand and gloved repeated actions |
| enclosure/repair | many openings, key matrix/FPC/controller and legends | fewer controls; touch/encoder/buttons still require sealing/lifetime proof |
| RF/expansion | wider face and hand position alter antenna/connector volume | more freedom, but exact display/control geometry still affects antennas |
| recurring cost/test | keys, matrix/controller, assembly and per-key test | touch/encoder/button/display costs; not automatically cheaper until full candidates are compared |

No single row decides the product. A keyboard candidate may win if real task
frequency justifies it, but selecting it now would skip G3/G4/G5 whole-product
comparison that the owner explicitly required.

## Corrected neutral boundary

- mandatory now: autonomous local navigation, all essential actions, local text
  input, dedicated STOP/PTT and unambiguous cancel/confirm;
- open for G3 comparison: permanent keyboard, touch, encoder, D-pad, action-key
  count, display size/aspect, one-/two-hand posture and optional U215 profile;
- forbidden shortcut: counting on phone/BLE/USB/external keyboard for an
  essential action or base configuration;
- forbidden inheritance: former 480×320 touch + encoder + named-button count is
  a historical candidate, not a target prerequisite.

## Sources

- [M5Stack Cardputer-Adv official documentation](https://docs.m5stack.com/en/core/Cardputer-Adv)
- [LILYGO T-Deck Plus official documentation](https://wiki.lilygo.cc/products/t-deck-series/t-deck-plus/)
- [Flipper Zero official product/specifications](https://flipper.net/)
- [LILYGO T-Embed CC1101 official documentation](https://wiki.lilygo.cc/products/t-embed-series/t-embed-cc1101/)
- [M5Stack Unit CardKB2 U215 official documentation](https://docs.m5stack.com/en/unit/Unit_CardKB2)

## Audit gate

- [x] accepted local autonomy/text result separated from physical implementation;
- [x] safety/frequent/sparse-text/sustained-text tasks separated;
- [x] current compact, landscape, field-control and external examples checked;
- [x] display/grip/RF/expansion/cost/repair/test consequences kept coupled;
- [x] active requirements and blocked historical BOM corrected for neutrality;
- [x] no keyboard/touch/encoder exact target selected before G3/G5;
- [ ] owner disposition through `IMP-0032`.
