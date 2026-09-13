# Leshy2 programming and recovery

[Русский](service-recovery.ru.md) · [Home](../README.md) · [Schematics](schematics.md)

The design goal is to recover one damaged controller image without reflashing every healthy controller. This is not yet an end-to-end qualified procedure. Recovery does not authorize a generic bypass of KILL, watchdog or hardware faults.

## Current R2 recovery boundary · 2026-09-14

These are native connection paths, not proof that power, reset and boot sequencing are already correct. A direct connection must not require the broken target's application, the S3 menu or a working Hub application.

| Target | Direct path | Current limitation / fallback | Location |
|---|---|---|---|
| ESP32-S3 | product USB RF J1 through M1 to native USB, manual BOOT/RESET | **UART fallback open:** UI J2 reaches GPIO7/8, not ROM UART0 GPIO43/44; the latter currently carry Hub D2/D3 without the required isolation | UI + RF |
| ESP32-C5 | UI J9 service USB through FSUSB42; UI J6 UART0 GPIO11/12; manual BOOT/RESET | GPIO28 net membership corrected; copper/strap timing, USB SEL/OE and reset-under-KILL remain open. UART avoids the data mux, not the reset sinks | UI |
| RF RP2354B | RF J4 service USB/BOOTSEL; RF J3 SWD/RUN | MAIN and release of both hardware reset paths are required; KILL still holds RUN low | RF |
| Hub RP2354B | UI J11 service USB/BOOTSEL; UI J10 SWD/RUN | MAIN and reset release are required; KILL and C5 service ownership can hold Hub in reset | UI |
| Pack MSPM0C1106 | RF J2 SWD + NRST; separate PACK_FIXTURE_3V3 input | Fixture ground is **cell-side**, not ordinary system POWER_GROUND. UART bootloading requires its flash-resident component; SWD is the blank-device recovery path | RF |
| Safety MSPM0C1106 | RF J13 SWD + NRST, without S3/Hub application | Use working board AON power; J13.2 is directly AON_SAFE_3V3, not an isolated programmer supply input. Treat it as VTref, not an additional power source | RF |
| TPS25751D + configuration EEPROM | SYS_I2C target pads plus direct local SDA/SCL/WP pads | pre-programmed loose EEPROM or current-limited raw-VBUS fixture | LESHY2-RF |
| MAX17320 pack gauge | internal protected local I2C and fault/hold observation | image checksum and override readback before energized cell installation | LESHY2-RF |
| SA818S-U and SA818S-V voice modules | permanent hardware-selected UART plus independent UHF/VHF PD controls | rail cycle, selection readback and replaceable serial module; neither part requires an undocumented firmware-update contact | LESHY2-RF |

## Recovery, updates and debugging are different workflows

- Bad image or erased application: address that target through ROM USB/UART or SWD, verify the written image, then check compatibility before returning to operation. The entry must not depend on the broken application.
- Bad Pack/Safety firmware: restore the affected supervisory controller by SWD with physical KILL first; restore normal power/reset behavior before servicing application controllers. A physically shorted device or failed supply is a repair case, not a firmware recovery case.
- Interrupted programming: re-enter the direct loader and repeat verified programming. The planned multi-controller rollback transaction is not yet implemented or power-cut qualified; a RAM-only model is not a persistent journal.
- Recommended design direction: explicit service RUN with working Safety for ESP/RP recovery, without requiring normal IPC replies from the target being repaired. Preserve physical KILL and electrical/thermal faults. **This is not an implemented policy change:** the current KILL/update conflict and service sequencing still require correction. Software TX inhibit or ROM entry is not an unconditional hardware guarantee of no RF transmission.
- Breakpoint debugging: an independent watchdog may correctly reset a halted processor. Do not silently disable it or infer a safe debug mode from working flash recovery; a separate controlled bench procedure is required.
- Preserve physical debug/recovery access. Do not irreversibly disable it through ESP eFuses, RP OTP or MSPM0 NONMAIN policy. For MSPM0C1106 the bootloader has a flash-resident component; it is not an independent, complete ROM UART loader for an erased device.

[Current interface review](h6-r2-interface-review.md) · [C5 mux defect](h6-r2-c5-mux-control-review.md) · [KILL/update conflict](safety.md#update-and-recovery).

Primary loader references: [Espressif S3](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html), [Espressif C5](https://docs.espressif.com/projects/esptool/en/latest/esp32c5/advanced-topics/boot-mode-selection.html), [Raspberry Pi BOOTSEL](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#resetting-flash-memory), [TI MSPM0 bootloader guide, sections2/6](https://www.ti.com/lit/ug/slau887a/slau887a.pdf). The Pack/Safety `boot_main.c` files are currently idle placeholders, not implemented recovery/A-B managers.

## Retained H2.5.2 history

The [61-net H2.5.2 review](../hardware/ecad/generated/H2-REV52-recovery-paths.json) belongs to the earlier single-RP design. It records the six-pad PD/EEPROM access correction; it does not qualify current R2 recovery or close the gaps above.
