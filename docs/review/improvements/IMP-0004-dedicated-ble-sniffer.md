# IMP-0004 — dedicated BLE connection sniffer

- Статус: **Предложено как аппаратное расширение**
- Связано: `OUT-03`, `FND-0002`
- Зона: `LAB-P`
- Обнаружено: 2026-08-15

## Legacy-ограничение

ESP32-S3 и ESP32-C5 поддерживают BLE, но legacy считал connection-follow sniff недоступным и исключал его на уровне продукта.

## Обход

Nordic официально поддерживает near-real-time BLE sniff и следование за выбранным соединением на nRF52840/nRF52833/nRF52 hardware. Рассмотреть отдельный компактный nRF52-class sniffer как встроенный сопроцессор или опциональный модуль.

## Что ещё не доказано

Официальный Nordic flow ориентирован на dongle/DK и host software. До включения в Leshy2 нужно доказать автономную интеграцию, формат потока, управление каналами, firmware licence/distribution, интерфейс к S3 и одновременную работу с остальными 2.4 ГГц радио.

## Цена и риски

Дополнительные BOM, антенна/RF coexistence, питание, прошивка третьего MCU и новый transport. Пассивный capture всё равно требует собственных/разрешённых устройств и privacy policy.

## Источники

- [Nordic nRF Sniffer for Bluetooth LE](https://www.nordicsemi.com/Products/Development-tools/nRF-Sniffer-for-Bluetooth-LE)
- [Nordic connection-follow modes](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-ble-sniffer/guides/sniffer_usage.html)
