# Память контроллеров и граница восстановления

[На главную](../README.ru.md) · [English](memory.md) · [Распиновка](pinout.ru.md) ·
[Карта памяти прошивки](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/memory.ru.md)

В Leshy2 R2 шесть независимо восстанавливаемых firmware-доменов. Ни один
контроллер не загружается из flash другого, а общая шина не заменяет локальный
last-known-good image.

## Физический состав памяти

| Домен | Точное устройство | Локальное хранилище кода | Оперативная память | Локальный rollback | Физическое восстановление |
|---|---|---:|---:|---|---|
| S3 | `ESP32-S3-WROOM-1U-N16R8` | 16 МиБ flash модуля | 8 МиБ octal PSRAM с ECC | два OTA slot по 7 МиБ | product USB, UART0, RESET и BOOT |
| C5 | `ESP32-C5-WROOM-1U-N8R8` | 8 МиБ flash модуля | 8 МиБ PSRAM модуля | два OTA slot по 3,5 МиБ | независимый data-only USB, UART0, RESET и BOOT |
| RF RP | `SC1512-A4` (`RP2354B`) | 2 МиБ stacked flash | 520 КиБ on-chip SRAM | нативная A/B-пара по 896 КиБ | независимый data-only USB, SWD, RUN и USB_BOOT |
| Hub RP | второй `SC1512-A4` (`RP2354B`) | собственные 2 МиБ stacked flash | 520 КиБ on-chip SRAM | отдельная нативная A/B-пара по 896 КиБ | независимый data-only USB, SWD, RUN и USB_BOOT |
| Pack | `MSPM0C1106SDGS20R` | 64 КиБ on-chip flash | 8 КиБ on-chip SRAM | независимая разметка boot/A/B/state 16/22/22/4 КиБ | NRST, SWDIO, SWCLK, UART1 и изолированное fixture-питание |
| Safety | второй `MSPM0C1106SDGS20R` | собственные 64 КиБ on-chip flash | 8 КиБ on-chip SRAM | отдельная разметка 16/22/22/4 КиБ | NRST, SWDIO, SWCLK, UART1 и изолированное fixture-питание |

Два RP2354B и два MSPM0 имеют общую только геометрию разделов. Их target ID,
identities images, boot state и физическое хранилище раздельны. Firmware
F0-R2.2 проверяет этот one-to-one ownership в
[машинном контракте](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/f0_r2_memory_rollback_contract.json).
Firmware F0-R2.3 теперь фиксирует S3-last update transaction шести образов;
реальный timing окна RP TBYB 16,7 с остаётся последующим firmware/physical gate.

## Аппаратные правила, сохраняющие boot и recovery

- GPIO35/36/37 модуля S3 являются внутренними сигналами octal PSRAM и никогда
  не считаются ресурсом PCB. Production firmware сохраняет
  `CONFIG_SPIRAM_ECC_ENABLE=y` и до обычной работы UI/radio доказывает не менее
  7,5 МиБ (`0x780000` bytes) usable PSRAM.
- Strap-sensitive GPIO0 S3 сейчас является входом `VIDEO_D0`; decoder обязан
  оставаться high-impedance до завершения ROM sampling. GPIO46 —
  `LCD_QSPI_D0`; его внешний bias сохраняет принятый strap до перехода в
  push-pull.
- Product USB S3 — единственный USB, которому разрешено питать устройство.
  Service USB C5 и обоих RP являются data-only и не могут back-power ни один
  rail.
- GPIO13/14 C5 намеренно мультиплексируются между native SDIO D3/D2 и service
  USB. Service mode останавливает и сбрасывает runtime link до переключения
  analog switch.
- Recovery Pack и Safety может заменить firmware, но не может синтезировать
  `RUN`, обслужить независимый watchdog или снять аппаратную защёлку
  `FAULT_KILL`. Пустая или неисправная прошивка остаётся fail-closed.

Это требования функциональной архитектуры, а не разрешение PCB routing. H2-R2
должен реализовать точные symbols, strap networks, switches и service headers;
H3/H6 проверяют power, timing и no-back-power; H7 доказывает programming и
rollback всех шести физических контроллеров.

## Детальная разметка принадлежит прошивке

Точные offsets, image limits, manifests и rollback state генерируются и
тестируются на [странице памяти firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/memory.ru.md).
Hardware-контракт фиксирует установленные ёмкости и recovery wiring; firmware
не может незаметно занять inactive slot или переосмыслить service port.
