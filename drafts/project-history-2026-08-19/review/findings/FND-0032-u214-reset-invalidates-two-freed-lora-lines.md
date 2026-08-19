# FND-0032 — U214 RESET invalidates the claimed two freed LoRa controls

- Статус: **Layout-кандидат исправлен; открыто до решения matrix/U14 и recovery proof**
- Дата: 2026-08-16
- Серьёзность: pin/resource mismatch
- Затрагивает: `FND-0006`, `DEC-0009`, `IMP-0010`, `DM-EXT-02`, all three layouts

## Несоответствие

Старые `FND-0006/IMP-0010` считали свободными обе линии onboard E22: `U12.P04=LoRa_NRESET` и `U12.P12=LoRa_TR`. После `DEC-0008` onboard E22 действительно удалён, но принятый внешний U214 всё равно требует host-controlled `LoRa_RST`. `DM-EXT-02` фиксирует этот signal. Поэтому `U12.P04` не свободна; без коррекции прежний план matrix+audio теряет одну control line.

## Исправленный candidate map

| Resource | Target use |
|---|---|
| `U13.P10..P15` | six row/column lines of diode-isolated 3×3 ordinary-key matrix |
| `U13.P16/P17` | speaker and TX-audio default-to-analog selectors |
| `U12.P12` | ES8311 enable/reset; this is the one genuinely freed E22 T/R control |
| `U12.P04` | retained `EXT_RF_RST` for U214 |
| `U13.P06` | safe-default voice H/L; freed by making C5 BOOT a physical recovery control |
| `GPIO48` IRQ sum | expanders plus touch through a verified open-drain output or an explicit open-drain buffer |
| physical STOP | independent `DEC-0024` path, never in matrix |

This map requires proof that C5 native USB + physical BOOT/RESET provides independent recovery, and that the exact touch interrupt is safely wire-OR/open-drain or is converted by a buffer. If either proof fails, retain `U14`; nRF ownership maps remain pin-compatible.

## Closure

Close only after owner chooses matrix/U14, exact expander map is netlisted without duplication, C5 empty-flash recovery passes, and touch IRQ electrical behavior is qualified.

