# Leshy2 power architecture

[Русский](power-architecture.ru.md) · [Home](../README.md) · [Schematics](schematics.md)

This is the final product power architecture. It is checked against the complete netlist exported by KiCad itself.

## Sources

- The sole external source is the main S3 USB-C port: sink only, up to 30 W (5 V fallback, 9 V × 3 A or 15 V × 2 A). C5 and RP2354B service USB ports cannot power the product.
- Portable power uses two removable protected 18650 cells in series, 6.0–8.4 V. Both cells are required for battery operation.

## Input, charging and pack

`USB-C` → **Texas Instruments TPS25751DREFR** → **Texas Instruments BQ25798RQMR** → `NVDC_SYS`.

`2× 18650` → two independent 5 A fuses → **Analog Devices MAX17320G20+T** + **Texas Instruments MSPM0C1106SDGS20R** → back-to-back power FET → charger/`NVDC_SYS`.

## Generated rails

| Output | Path | Purpose |
|---|---|---|
| `AON_SAFE_3V3` | `NVDC_SYS` → TPS629203 → TPS25961 | Always-on safety logic |
| `3V3_MAIN` | `NVDC_SYS` → TPS564252 → TPS25974 | Processors, UI and ordinary logic |
| `VVOICE_4V` | `NVDC_SYS` → TPS564252 → TPS25974 | Voice RF path only |
| `5V_U214_PROTECTED` | `NVDC_SYS` → TPS564252 → TPS259470 | Removable U214 LoRa Cap |
| `5V_UNIT_PROTECTED` | same buck → separate TPS259470 | M5 Unit; one branch cannot feed the other |

## H2.5.1 result

✅ **Reviewed:** 17 critical power nets are traced in the actual KiCad netlist. UI, RF and LoRa Cap contain 395, 690 and 27 uniquely annotated components; there are no reference collisions.

A fabrication blocker was corrected: child-sheet-local `R1/C1/U1` references now use deterministic sheet-number ranges.

[Machine review evidence](../hardware/ecad/generated/H2-REV51-power-paths.json).
