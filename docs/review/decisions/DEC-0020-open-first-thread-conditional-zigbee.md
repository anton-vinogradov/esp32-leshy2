# DEC-0020 — open-first Thread и условный изолированный Zigbee backend

- Статус: **Принято владельцем**
- Источник: `IMP-0018`, вариант A
- Дата: 2026-08-16

## Решение

Встроенный IEEE 802.15.4 radio ESP32-C5 используется шире legacy passive-only режима без добавления нового RF hardware:

- OpenThread является открытым baseline для ordinary Thread roles, прошедших memory/coexistence/HIL;
- ordinary Zigbee coordinator/router/end-device допускается как optional conditional adapter официального SDK;
- proprietary Zigbee core изолируется отдельным build profile и не требуется для core product, raw IEEE 802.15.4, OpenThread, сборки, обновления или восстановления открытого baseline;
- binary adapter получает exact version/provenance/redistribution/SBOM/hash/signature/update/rollback gates;
- Wi-Fi 2.4 GHz, BLE и IEEE 802.15.4 считаются одним shared C5 RF path: одновременная производительность не обещается, scheduler/preemption/loss доступны измерению.

## Трёхуровневая граница

- Main: ordinary commissioning/join/control/diagnostics только собственных или администрируемых Thread/Zigbee networks;
- Lab: passive raw IEEE 802.15.4 sniff, ED/CCA и privacy-bounded PCAP;
- Controlled Zone `AUTHORIZED_TARGET`: bounded raw injection/replay/commissioning-security test exact authorized fixture;
- Controlled Zone `BOTH`: flood/interference/resilience test только conducted/RF-shielded с no-leakage proof, hard timeout и STOP.

## Стоимость и открытость

В baseline не добавляется второй 802.15.4 SoC, RF path или antenna. Это сохраняет base BOM и использует уже принятое C5 silicon. Если HIL докажет неприемлемую потерю пакетов в принятом пользовательском сценарии, dual-SoC может появиться только как отдельное предложение с измеримой причиной и полной BOM/RF/power оценкой.

Optional proprietary Zigbee adapter не делает устройство закрытым: открытый core product остаётся полностью собираемым и восстанавливаемым без него, а владелец контролирует подключение и обновление adapter.

## Последствия для артефактов

- `REQ-W5-0001` получает статус **«Проведено ревью»**;
- `FND-0025` закрывается на уровне требований; coexistence/build/HIL остаются implementation proof;
- `FND-0022`–`FND-0024`, `FND-0001` и `FND-0007` остаются открытыми implementation findings; `FND-0002` позднее закрыт решением `DEC-0021`;
- `IMP-0003` и private patched Wi-Fi backend не принимаются этим решением и сохраняют собственные gates;
- target/current-state EN/RU обоих репозиториев получают одинаковую open/proprietary boundary.
