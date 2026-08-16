# FND-0026 — native BLE scan не является connection sniffer, устойчивой identity или дальномером

- Статус: **Открыто; overclaims сняты в draft-требованиях**
- Серьёзность: measurement/privacy/security capability blocker
- Затрагивает: `C-BLE-01`–`C-BLE-06`, `OUT-03`, tracker/device DB/proximity/PCAP UI
- Обнаружено: 2026-08-16

## Несоответствие

Legacy смешивает четыре разные возможности:

1. standard BLE advertising scan собственного controller;
2. активное GATT-соединение как central;
3. passive Link-Layer connection follow стороннего соединения;
4. вывод identity/distance/intent из address, payload и RSSI.

S3/C5 официально поддерживают standard observer/central roles, но публичный ESP-IDF contract не документирует promiscuous перехват и следование за чужим BLE connection. Отдельный Nordic nRF Sniffer умеет follow connection/PHY и поэтому остаётся отдельным hardware proposal `IMP-0004`, а не скрытой функцией native controller.

BLE privacy дополнительно запрещает наивную identity-модель: resolvable/non-resolvable private addresses меняются, а без IRK сканер не имеет права объявлять новый address тем же устройством. Manufacturer/company ID, service UUID и advertising signature дают только evidence о формате/вендоре/классе с указанной confidence, не доказательство конкретной модели, владельца или намерения.

RSSI зависит от TX power, antenna/orientation, body/enclosure, multipath, PHY и калибровки. Он может быть rough proximity evidence, но не метрами и не гарантией «рядом/далеко». C5 direction-finding capability также не создаёт AoA/AoD без квалифицированной antenna array/switching/calibration architecture.

## Обязательное исправление

- scan records хранят address type, PHY, channel/report type, payload, RSSI, timestamp/age и parser/signature version;
- identity state разделяется на `observed address`, `resolved bonded identity`, `signature candidate` и `unknown`;
- proximity показывает raw RSSI/statistics и только calibrated `stronger/comparable/unknown`, без distance claim;
- unwanted-tracker функция показывает `potential compatible tracker observed` и временные evidence, но не объявляет злой умысел, владельца или безопасность по отсутствию alert;
- connection PCAP/follow отсутствует до отдельного `IMP-0004` decision и autonomous integration proof.

## Критерий закрытия

Parser/UI/storage/HIL fixture с public/static/RPA/NRPA, legacy/extended/Coded advertisements, calibrated attenuation/orientation и known connections подтверждает states/loss/false positives. Невозможные identity/distance/connection-follow поля отсутствуют, а не заполняются эвристикой.

## Первичные источники

- [ESP32-S3 Bluetooth LE feature set](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [Bluetooth SIG Security and Privacy Best Practices](https://www.bluetooth.com/download/bluetooth-security-and-privacy-best-practices-guide/)
- [Nordic nRF Sniffer: advertising and connection-follow modes](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-ble-sniffer/guides/running_sniffer.html)
- [Apple unwanted-tracker behavior and rotating identifiers](https://support.apple.com/en-us/119874)

