# S3 memory and boot wiring

[Home](../README.md) · [Русский](memory.ru.md) · [Pin assignment](pinout.md) · [Firmware memory map](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/memory.md)

The application controller is the exact external-antenna
`ESP32-S3-WROOM-1U-N16R8`: 16 MB quad flash and 8 MB 3.3-V octal PSRAM in the
same 18.0 × 19.2 × 3.2-mm module envelope. Production firmware enables PSRAM
ECC, retaining the −40…+85 °C module operating envelope and at least 7.5 MB of
usable external RAM.

ECC is a hardware/firmware interface requirement, not a recommendation:
production defaults must contain `CONFIG_SPIRAM_ECC_ENABLE=y`, and a startup
self-test must confirm at least `0x780000` bytes of usable PSRAM before UI or
radio startup. A build without that flag is laboratory diagnostic software for
operation up to +65 °C only and cannot be released as production firmware.

GPIO35, GPIO36 and GPIO37 are internal octal-PSRAM signals on this exact module
and are not routed on the PCB. The complete application pin budget still closes:

| S3 contact | Product signal | Boot-safe electrical state |
|---|---|---|
| `GPIO0` | codec `I2S_DIN` after boot | 10-kΩ normal-boot pull-up; the codec buffer is enabled only by `CODEC_READY AND AUDIO_ARM`, and `AUDIO_ARM` is physically low during reset |
| `GPIO18` | display/microSD `SPI2 SCK` | 10-kΩ reset-low default; ordinary non-strap GPIO |
| `GPIO45` | shared active-low `SYS_INT_N` | the N16R8 module fixes 3.3-V `VDD_SPI` by eFuse, so the 10-kΩ interrupt pull-up cannot change the memory supply |
| `GPIO46` | display/microSD `SPI2 D0` | 10-kΩ pull-down holds the required low strap state; firmware takes push-pull ownership only after ROM sampling |

Native USB, UART0, RESET and BOOT remain permanent recovery paths. A protected
1-kΩ service path can still pull GPIO0 low, while the reset-qualified codec gate
prevents an audio-domain fault from blocking ROM download.

The machine build defaults and exact flash layout live in the
[firmware repository](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/sdkconfig.defaults.esp32s3).

Production validation covers active and sleep current, temperature stress,
strap waveforms and recovery with the codec powered, unpowered and faulted.
The exact module is also present in the
[machine-readable BOM](../hardware/architecture/generated/G2F-3I-target-bom.csv).
