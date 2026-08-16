# FND-0002 — владелец BLE расходится между legacy-репозиториями

- Статус: **Требуется решение владельца (`IMP-0019`)**
- Серьёзность: архитектурное несоответствие
- Этап разрешения: 3 — системная архитектура и владение
- Обнаружено: 2026-08-15

## Наблюдение

Hardware legacy сообщает, что BLE имеется у обоих MCU, а в карте частот объединяет `802.15.4 / Zigbee + BLE` на ESP32-C5. Firmware legacy, напротив, строит весь BLE-раздел на ESP32-S3 и использует C5 только для 5 ГГц/802.15.4, nRF24 и IR.

`DEC-0001` назначает C5 только 3× nRF24 и IR; владельца BLE оно не определяет.

## Влияние

Набор пользовательских BLE-возможностей можно инвентаризировать независимо от MCU, но нельзя проектировать драйверы, IPC, coexistence и тесты до выбора одного из вариантов:

1. BLE только на S3;
2. BLE только на C5;
3. разделение BLE-ролей между обоими MCU с явным контрактом.

## Текущее действие

Prerequisite audit подтвердил:

- S3 покрывает весь legacy BLE baseline: 1M/2M/Coded PHY, advertising extensions, multiple advertising sets, simultaneous advertising+scanning и concurrent central/peripheral roles;
- C5 имеет дополнительные новые Link-Layer функции, не являющиеся принятыми требованиями, но его BLE делит один RF path с C5 Wi-Fi 2.4 и IEEE 802.15.4;
- S3 BLE делит RF только с S3 Wi-Fi 2.4, оставаясь физически отдельным от C5 Thread/Zigbee и устраняя IPC для UI/phone keyboard/HID;
- оба MCU уже входят в hardware BOM; выбор владельца меняет software/power/coexistence/HIL, а не цену radio IC.

`IMP-0019` предлагает назначить S3 единственным baseline BLE owner, оставить C5 BLE выключенным в обычном profile и не закрывать будущий отдельный C5-only feature adapter. До ответа `REQ-BLE-0001` остаётся на ревью.

## Первичные источники

- [ESP32-S3 datasheet: Bluetooth LE PHY and Link Controller](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-C5 datasheet: Bluetooth LE feature set](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [ESP32-S3 Wi-Fi/BLE coexistence](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/coexist.html)
- [ESP32-C5 Wi-Fi/BLE/802.15.4 coexistence](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/coexist.html)
