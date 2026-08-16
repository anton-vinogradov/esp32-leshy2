# IMP-0017 — native BLE для обычных функций, nRF24 только для ограниченной compatibility

- Статус: **⚠️ Предложение; решение отложено до BLE-owner review**
- Связано: `C-N24-08`, `FND-0002`, `FND-0021`, `OUT-03`, `OUT-04`
- Зона: Main ordinary BLE; Lab compatibility RX; Controlled Zone identity/security TX
- Дата: 2026-08-16

## Контекст

S3 и C5 имеют настоящий BLE controller, тогда как nRF24 способен лишь software-совместимые фрагменты legacy 1 Mbit/s advertising. Использовать nRF24 как основной BLE backend означало бы потерять standard scanning, Link Layer semantics и connection support, одновременно дублируя уже оплаченное silicon.

## ⚠️ Предложение

После решения `FND-0002` обычные BLE scan/advertise/connection функции направить в нативный ESP32 BLE backend. nRF24-путь сохранить только как conditional compatibility/research mode:

- legacy advertising channels и ограниченный PDU/payload support;
- software whitening/CRC с explicit confidence и false-positive fixtures;
- отсутствие claim full BLE, connection follow, extended advertising или compliance;
- passive raw compatibility analysis — Lab;
- imitation чужой identity, notification/spam/flood и security test TX — Controlled Zone с соответствующим `AUTHORIZED_TARGET`/`BOTH`.

Это не добавляет hardware BOM, уменьшает риск ложной совместимости и сохраняет исследовательскую возможность nRF24. Exact BLE owner и coexistence policy принимаются в отдельном BLE-срезе, поэтому текущий документ не просит второго решения одновременно с `IMP-0016`.

## Первичные источники

- [ESP32-C5 DevKit hardware capabilities](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c5/esp32-c5-devkitc-1/user_guide.html)
- [pyRF24 fake-BLE limitations](https://nrf24.github.io/pyRF24/ble_api.html)

