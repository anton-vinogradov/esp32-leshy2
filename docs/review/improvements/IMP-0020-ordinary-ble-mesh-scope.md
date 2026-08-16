# IMP-0020 — ordinary Bluetooth Mesh как найденная, но не запрошенная функция

- Статус: **⚠️ Предложение отложено до решения BLE owner**
- Связано: `FND-0002`, `IMP-0019`, draft `REQ-BLE-0001`
- Зона: Main ordinary owner network; Lab/Controlled Zone security cases separate
- Дата: 2026-08-16

## Почему это отмечено как «лишнее»

ESP-IDF официально поддерживает ESP-BLE-MESH provisioning/node control, Proxy, Relay, Low Power и Friend на ESP32-S3/C5. Legacy capability tree этого не просил. Поэтому функция технически возможна без нового radio BOM, но не включается молча: она добавляет provisioned key lifecycle, flash/RAM, routing/coexistence, interoperability и большой test matrix.

## Будущий выбор

- A: включить ordinary owner-administered Bluetooth Mesh node/provisioner roles как conditional Main profile;
- B: не включать Mesh и сохранить только point-to-point/broadcast BLE baseline;
- security provisioning/key tests при любом варианте проектируются отдельно по трём уровням.

Вопрос будет задан после выбора BLE owner, потому что ownership/coexistence — обязательный prerequisite. До отдельного согласия target README и `REQ-BLE-0001` Mesh не обещают.

## Первичный источник

- [ESP32-S3 Bluetooth LE stack and ESP-BLE-MESH support](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/ble/overview.html)
