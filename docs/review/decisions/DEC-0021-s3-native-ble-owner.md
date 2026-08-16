# DEC-0021 — former ESP32-S3 baseline native-BLE ownership

- Статус: **Superseded as target ownership by `DEC-0032`; native-BLE capability retained**
- Дата: 2026-08-16
- Принимает: `IMP-0019/A`, уточнённый `IMP-0017`
- Закрывает: `FND-0002` на уровне требований
- Не решает: физического владельца 3×nRF24 (`IMP-0021`)

## Решение

> Пункты ниже сохраняют историю и доказанный S3 reference profile. В новой
> архитектуре native BLE, product identity/key-vault semantics и coexistence
> остаются обязательными, но owner/controller выбирается заново целиком.

1. ESP32-S3 — единственный baseline-владелец native Bluetooth LE: GAP/GATT/SMP/HID, ordinary scan/advertise/central/peripheral, product identity, bond/IRK/LTK vault и allowlist.
2. BLE controller ESP32-C5 выключен в обычном profile. C5-only advanced BLE функция может появиться только через новое требование с доказанной пользой, coexistence и HIL.
3. Выбор BLE owner ничего не отнимает у трёх nRF24. Они остаются полнофункциональными в собственном native GFSK/Enhanced ShockBurst scope; ограниченным является только их дополнительный experimental BLE-compatible legacy-1M advertising subset, потому что nRF24 физически не является BLE controller.
4. Точный владелец 3×nRF24 переоткрыт владельцем проекта и выбирается отдельно в `IMP-0021`. IR остаётся на C5 по `DEC-0001`/`DEC-0018`, пока отдельное решение его не изменит.
5. Native BLE S3, nRF24 и C5 802.15.4 используют раздельные RF frontends, но общий cross-MCU arbiter обязан учитывать self-desense, unsafe simultaneous TX и измеренные coexistence budgets.

## Последствия

- `REQ-BLE-0001` получает статус **«Проведено ревью»**;
- `FND-0002` закрыт на requirement-level;
- `IMP-0004` dedicated connection sniffer и `IMP-0020` ordinary Bluetooth Mesh остаются отдельными предложениями;
- target/current EN/RU обоих репозиториев получают одинаковую BLE ownership boundary;
- `FND-0026`, `FND-0027`, exact host stack, storage/privacy и HIL остаются implementation work.

## Первичные источники

- [ESP32-S3 Bluetooth LE feature set](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-S3 BLE hosts and profiles](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/ble/overview.html)
- [ESP32-C5 RF coexistence](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/coexist.html)
