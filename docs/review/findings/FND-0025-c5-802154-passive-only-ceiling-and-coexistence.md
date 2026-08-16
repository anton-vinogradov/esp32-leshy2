# FND-0025 — passive-only ceiling 802.15.4 ложен, но full-stack/coexistence не выбраны

- Статус: **Требуется решение владельца (`IMP-0018`)**
- Серьёзность: scope/openness/coexistence decision
- Затрагивает: `C-W5-09`, C5 firmware/storage/UI, 2.4 GHz arbitration и HIL
- Обнаружено: 2026-08-16

## Несоответствие

Legacy оставлял ESP32-C5 только passive 802.15.4 sniff/energy scan и исключал full-stack join. Актуальный supported target даёт без нового RF-железа:

- raw IEEE 802.15.4 promiscuous RX, energy detection, CCA, channel control и raw MAC TX;
- open-source OpenThread stack и ordinary Thread device roles;
- Zigbee 3.0 coordinator/router/end-device через официальный Espressif Zigbee SDK.

При этом это не три одновременно независимых радио:

- Wi-Fi 2.4 GHz, BLE и 802.15.4 делят один C5 RF path по времени;
- Wi-Fi/BLE могут вытеснять низкоприоритетный 802.15.4 RX, а некоторые SoftAP/sniffer+router combinations unstable/unsupported;
- Espressif рекомендует dual-SoC с отдельными антеннами для производительного Wi-Fi/Thread Border Router или Zigbee gateway; добавлять такой hardware без отдельного продуктового решения нельзя;
- OpenThread остаётся открытой baseline-зависимостью, а Zigbee SDK v2 содержит proprietary prebuilt core. Открытая wrapper repository/license не превращает core binary в open source.

## Следствие

Старый запрет снимается как технически неверный, но полный scope не выбирается автоматически. Требуется решить, входит ли обычный Thread/Zigbee join/control в Main и допустим ли optional proprietary Zigbee backend при сохранении открытого базового продукта.

## Критерий закрытия

Владелец выбирает `IMP-0018`; затем финальное `REQ-W5-0001` фиксирует protocol roles, open/proprietary dependency boundary, radio-time arbitration, memory/build profiles и HIL packet-loss/latency matrix. Raw active security/flood/interference functions получают отдельные Controlled-Zone gates и не смешиваются с ordinary networking.

## Первичные источники

- [ESP-IDF IEEE 802.15.4 CLI example for ESP32-C5](https://github.com/espressif/esp-idf/tree/master/examples/ieee802154/ieee802154_cli)
- [ESP-IDF OpenThread API](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-reference/network/esp_openthread.html)
- [Espressif Zigbee SDK for ESP32-C5](https://docs.espressif.com/projects/esp-zigbee-sdk/en/latest/esp32c5/introduction.html)
- [ESP32-C5 RF coexistence guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/coexist.html)

