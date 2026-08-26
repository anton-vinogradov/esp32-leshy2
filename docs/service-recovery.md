# Leshy2 programming and recovery

[Русский](service-recovery.ru.md) · [Home](../README.md) · [Schematics](schematics.md)

A damaged image in one controller cannot permanently brick the product. No recovery path can bypass hardware transmit inhibits.

| Target | Primary path | Independent fallback | Location |
|---|---|---|---|
| ESP32-S3 | protected product USB-C (native USB Serial/JTAG) | internal keyed DBG10 UART0 + RESET/BOOT; two recessed side switches | LESHY2-UI + LESHY2-RF |
| ESP32-C5 | dedicated data-only USB-C through FSUSB42MUX | internal keyed DBG10 UART0 + RESET/BOOT; two recessed side switches | LESHY2-UI |
| RP2354B | dedicated data-only USB-C through FSUSB42MUX | internal keyed DBG10 SWD + RUN/USB_BOOT; two recessed side switches | LESHY2-RF |
| pack-admission MSPM0 | internal current-limited fixture VDD/GND + UART + SWD + NRST pads | none required; permanent SWD and UART are both present | LESHY2-RF |
| AON safety MSPM0 | internal AON-powered UART + SWD + NRST pads | recovery cannot release RUN_PERMIT or clear hardware FAULT_KILL | LESHY2-RF |
| TPS25751D + configuration EEPROM | SYS_I2C target pads plus direct local SDA/SCL/WP pads | pre-programmed loose EEPROM or current-limited raw-VBUS fixture | LESHY2-RF |
| MAX17320 pack gauge | internal protected local I2C and fault/hold observation | image checksum and override readback before energized cell installation | LESHY2-RF |
| SA818S-U and SA818S-V voice modules | permanent hardware-selected UART plus independent UHF/VHF PD controls | rail cycle, selection readback and replaceable serial module; neither part requires an undocumented firmware-update contact | LESHY2-RF |

## Hardware boundaries

- S3, C5 and RP2354B each retain independent USB plus an independent keyed DBG10 fallback
- all six RESET/BOOT controls are distinct recessed side switches and can only assert low
- both MSPM0 domains retain UART, SWD and reset even with S3/C5/RP firmware absent
- PD/EEPROM first programming no longer depends on an undocumented fixture contact
- service paths do not authorize RF re-arm, RUN_PERMIT release or FAULT_KILL clearing

## H2.5.2 result

✅ **Reviewed:** 61 reset/boot/service/recovery nets are verified in complete KiCad netlists. The PD/EEPROM access gap was corrected with six internal BOM-free copper pads and no enclosure change.

[Machine evidence](../hardware/ecad/generated/H2-REV52-recovery-paths.json).
