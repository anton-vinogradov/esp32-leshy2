# Controller memory and recovery boundary

[Home](../README.md) · [Русский](memory.ru.md) · [Pin assignment](pinout.md) ·
[Firmware memory map](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/memory.md)

Leshy2 R2 has six independently recoverable firmware domains. No controller
boots from another controller's flash, and no shared bus is a substitute for a
local last-known-good image.

## Physical memory inventory

| Domain | Exact device | Local executable storage | Volatile memory | Local rollback | Physical recovery |
|---|---|---:|---:|---|---|
| S3 | `ESP32-S3-WROOM-1U-N16R8` | 16 MiB module flash | 8 MiB octal PSRAM with ECC | two 7-MiB OTA slots | product USB, UART0, RESET and BOOT |
| C5 | `ESP32-C5-WROOM-1U-N8R8` | 8 MiB module flash | 8 MiB module PSRAM | two 3.5-MiB OTA slots | independent data-only USB, UART0, RESET and BOOT |
| RF RP | `SC1512-A4` (`RP2354B`) | 2 MiB stacked flash | 520 KiB on-chip SRAM | native 896-KiB A/B pair | independent data-only USB, SWD, RUN and USB_BOOT |
| Hub RP | second `SC1512-A4` (`RP2354B`) | its own 2 MiB stacked flash | 520 KiB on-chip SRAM | a separate native 896-KiB A/B pair | independent data-only USB, SWD, RUN and USB_BOOT |
| Pack | `MSPM0C1106SDGS20R` | 64 KiB on-chip flash | 8 KiB on-chip SRAM | independent 16/22/22/4-KiB boot/A/B/state map | NRST, SWDIO, SWCLK, UART1 and isolated fixture power |
| Safety | second `MSPM0C1106SDGS20R` | its own 64 KiB on-chip flash | 8 KiB on-chip SRAM | a separate 16/22/22/4-KiB map | NRST, SWDIO, SWCLK, UART1 and isolated fixture power |

The two RP2354B devices and the two MSPM0 devices share only partition
geometry. Their target IDs, image identities, boot state and physical storage
remain separate. Firmware F0-R2.2 checks this one-to-one ownership in its
[machine contract](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/f0_r2_memory_rollback_contract.json).
Firmware F0-R2.3 now fixes the S3-last six-image update transaction; its actual
16.7-second RP TBYB timing remains a later firmware/physical qualification gate.

## Hardware rules that preserve boot and recovery

- The S3 module's GPIO35/36/37 are internal octal-PSRAM signals and never PCB
  resources. Production firmware keeps `CONFIG_SPIRAM_ECC_ENABLE=y` and proves
  at least 7.5 MiB (`0x780000` bytes) of usable PSRAM before normal UI or radio
  work.
- S3 strap-sensitive GPIO0 is the current `VIDEO_D0` input and its decoder must
  remain high-impedance through ROM sampling. GPIO46 is `LCD_QSPI_D0`; its
  external bias must preserve the accepted strap before push-pull ownership.
- The S3 product USB is the only USB path allowed to power the device. C5 and
  both RP service USB ports are data-only and must not back-power any rail.
- C5 GPIO13/14 are deliberately multiplexed between native SDIO D3/D2 and its
  service USB path. Entering service mode stops and resets the runtime link
  before the analog switch changes ownership.
- Pack and Safety recovery can replace firmware, but cannot synthesize
  `RUN`, service the independent watchdog or clear the hardware `FAULT_KILL`
  latch. Blank or failed firmware therefore remains fail-closed.

These are functional architecture requirements, not authorization for PCB
routing. H2-R2 must instantiate exact symbols, strap networks, switches and
service headers; H3/H6 verify power, timing and no-back-power behavior; H7 proves
programming and rollback on all six physical controllers.

## Firmware-owned partition detail

Exact offsets, image limits, manifests and rollback state are generated and
tested in the [firmware memory page](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/memory.md).
The hardware contract fixes installed capacities and recovery wiring; firmware
cannot silently consume the inactive slot or reinterpret a service port.
