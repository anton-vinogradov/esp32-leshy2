# Память S3 и загрузочные линии

[На главную](../README.ru.md) · [English](memory.md) · [Распиновка](pinout.ru.md) · [Карта памяти прошивки](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/memory.ru.md)

Контроллер приложения — точный модуль с внешней антенной
`ESP32-S3-WROOM-1U-N16R8`: 16 МБ quad flash и 8 МБ 3,3-В octal PSRAM в прежнем
габарите 18,0 × 19,2 × 3,2 мм. В production-прошивке включается ECC PSRAM:
сохраняется диапазон модуля −40…+85 °C и остаётся не менее 7,5 МБ доступной
внешней RAM.

ECC является частью интерфейса между железом и прошивкой, а не рекомендацией:
production defaults обязаны содержать `CONFIG_SPIRAM_ECC_ENABLE=y`, а startup
self-test — подтвердить не менее `0x780000` байт usable PSRAM до запуска UI или
радио. Сборка без этого признака относится только к лабораторной диагностике в
диапазоне до +65 °C и не может быть выпущена как production.

GPIO35, GPIO36 и GPIO37 у этого точного модуля заняты внутренней шиной octal
PSRAM и на PCB не используются. Полный бюджет выводов приложения при этом
сходится:

| Контакт S3 | Сигнал продукта | Безопасное состояние при загрузке |
|---|---|---|
| `GPIO0` | `I2S_DIN` кодека после загрузки | pull-up 10 кОм для normal boot; буфер кодека включается только по `CODEC_READY AND AUDIO_ARM`, а `AUDIO_ARM` аппаратно удерживается в нуле при reset |
| `GPIO18` | `SPI2 SCK` экрана/microSD | reset-low через 10 кОм; обычный не-strap GPIO |
| `GPIO45` | общий active-low `SYS_INT_N` | у N16R8 питание `VDD_SPI` 3,3 В зафиксировано eFuse, поэтому pull-up interrupt не меняет питание памяти |
| `GPIO46` | `SPI2 D0` экрана/microSD | pull-down 10 кОм удерживает требуемый нулевой strap; push-pull включается только после ROM sampling |

Native USB, UART0, RESET и BOOT остаются постоянными путями восстановления.
Защищённая цепь 1 кОм по-прежнему может притянуть GPIO0 к нулю, а
reset-квалифицированный gate кодека не позволяет аварии audio-домена закрыть
ROM download.

Машинные build defaults и точная разметка flash находятся в
[репозитории прошивки](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/sdkconfig.defaults.esp32s3).

Production validation проверяет active/sleep current, температурный stress,
strap-осциллограммы и recovery при включённом, выключенном и неисправном
кодеке. Точный модуль также присутствует в
[машинном BOM](../hardware/architecture/generated/G2F-3I-target-bom.csv).
