# IMP-0019 — ESP32-S3 как единственный baseline-владелец native BLE

- Статус: **⚠️ Предложение — требуется решение владельца**
- Связано: `FND-0002`, `FND-0026`, `FND-0027`, `IMP-0017`, draft `REQ-BLE-0001`
- Цена hardware: без нового BOM
- Дата: 2026-08-16

## Контекст решения

Оба MCU имеют настоящий BLE controller, но baseline-функции не требуют двух BLE identity/stacks. ESP32-S3 уже поддерживает 1M/2M/Coded PHY, advertising extensions, multiple advertising sets, simultaneous advertising+scanning и concurrent central/peripheral roles. C5 добавляет более новые Link-Layer функции, которых нет в принятом legacy scope, и одновременно уже владеет Wi-Fi 5 GHz, IEEE 802.15.4, 3×nRF24 и IR.

BLE на C5 делит один 2.4 GHz RF path с Thread/Zigbee и Wi-Fi 2.4. BLE на S3 делит radio с S3 Wi-Fi 2.4, но остаётся физически независимым от C5 802.15.4 и не требует IPC для UI, phone keyboard, companion link или HID.

## Варианты

### A — S3 единственный baseline BLE owner (рекомендация)

- native scan/advertise/GATT/HID/phone companion выполняет S3;
- C5 BLE controller выключен в обычном build/profile;
- C5-only advanced BLE feature может вернуться только отдельным proposal с доказанной пользовательской задачей;
- nRF24 остаётся лишь conditional limited legacy-1M advertising compatibility по `IMP-0017`, не вторым BLE controller;
- один canonical device identity/bond vault/allowlist и отсутствие BLE IPC уменьшают firmware, power и HIL surface;
- accepted legacy capability не теряется и hardware BOM не меняется.

### B — C5 единственный BLE owner

Даёт прямой доступ к более новым C5 Link-Layer features, но они сейчас не требуются. Любой HID/phone/UI flow проходит S3↔C5 transport, BLE конкурирует с Thread/Zigbee на одном C5 radio, а C5 workload и recovery surface растут. Hardware BOM тот же, общей экономии нет.

### C — роли разделены между S3 и C5

Позволяет два BLE radio и потенциально parallel scan/connection, но создаёт две identities, два bond/key vault, cross-radio deduplication, больше self-interference/power и комбинаторный HIL. Ни один принятый сценарий пока не оправдывает сложность; вариант не считается бесплатным только потому, что оба MCU уже стоят на плате.

## Связанные границы

- native ESP controller не становится passive connection-follow sniffer; это отдельный `IMP-0004`;
- Bluetooth Classic не поддерживается S3/C5 и не появляется выбором владельца;
- host stack (NimBLE/Bluedroid) выбирается profile matrix на firmware-этапе: предпочтение меньшему NimBLE не отменяет доказательство HID/security/extended feature;
- S3 Wi-Fi/BLE coexistence, а также cross-MCU 2.4 GHz arbitration всё равно требуют HIL.

## Рекомендация

Выбрать A. Это сохраняет весь запрошенный BLE scope без нового BOM, освобождает C5 radio-time для принятого Thread/Zigbee и убирает ненужный IPC. C5-only advanced BLE не запрещается навсегда, но не входит в baseline без отдельного требования.

## Вопрос владельцу

Принимаем вариант A — S3 как единственный baseline native-BLE owner, C5 BLE выключен по умолчанию, nRF24 сохраняет только ограниченный compatibility/research path?

## Первичные источники

- [ESP32-S3 Bluetooth LE PHY/Link Controller](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-C5 Bluetooth LE feature set](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [ESP32-S3 coexistence](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/coexist.html)
- [ESP32-C5 coexistence](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/coexist.html)

