# FND-0029 — memory, transport and recovery consume the same scarce pins

- Статус: **Открыто; обязательно для всех layouts этапа 3**
- Дата: 2026-08-16
- Артефакты: current `hardware/tscircuit/c5-buses.tsx`, `PIN-0001`, `DM-0001`

## Несоответствие

Legacy and preliminary improvements treated three choices too independently:

1. Current S3 N8R2 exposes `GPIO35..37` and uses them for `C5LINK`; an 8 MB Octal-PSRAM N*R8 module makes those pins unavailable.
2. C5 4-bit SDIO uses `GPIO13/14`, the same fixed pins as C5 USB Serial/JTAG, so wider SDIO silently removes the currently documented independent C5 USB recovery path.
3. C5 GP-SPI link consumes the only C5 general-purpose SPI controller and therefore cannot coexist with C5-owned native nRF24 bus.

Each choice is individually plausible, but combining their optimistic benefits produces a layout that cannot exist.

## Required correction

- every layout names exact S3/C5 module memory variant and unavailable pins;
- every transport lists exact mode and pins, not only protocol name;
- recovery is proven for both MCUs before a UART/USB path is deleted;
- S3-heavy, C5-heavy and balanced scorecards use the same traffic and memory demand;
- 1-bit C5 SDIO is measured before being accepted as the C5-heavy default;
- no price saving is credited for deleting a recovery path or selecting insufficient PSRAM.

## Closure evidence

The finding closes only when all scored layouts have exact pin/controller tables, boot-strap analysis, signed update/recovery paths, traffic/memory tests and zero duplicate allocation. A final ownership decision alone is not closure.

## Primary sources

- [ESP32-S3 module pin/PSRAM notes](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [ESP32-C5 module pin, USB and SDIO notes](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf)
