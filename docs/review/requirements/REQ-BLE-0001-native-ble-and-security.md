# REQ-BLE-0001 — native Bluetooth LE connectivity, observation and controlled-test contract

- Статус набора: **Проведено ревью**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-BLE-01`–`C-BLE-12`, `C-X-03`, `C-X-06`, `C-X-09`, `C-UX-01`, `C-UX-02`, `OUT-03`, `OUT-04`
- Обязательные решения: `DEC-0002`, `DEC-0003`, `DEC-0004`, `DEC-0005`, `DEC-0010`, `DEC-0013`, `DEC-0019`, `DEC-0020`, `DEC-0021`
- Находки: `FND-0002`, `FND-0007`, `FND-0021`, `FND-0026`, `FND-0027`
- Принятые предложения: `IMP-0017`, `IMP-0019`
- Disposition extras: `IMP-0004`/`W-EXTRA-02` и `IMP-0020`/`W-EXTRA-03` сохранены `DEC-0023` как optional `defer-release`

## Граница документа

Native BLE controller предоставляет standard scanning, advertising, central/peripheral connections, GATT, SMP и HID profiles. Он не является promiscuous connection-follow sniffer, дальномером, универсальным tracker identifier или доказательством vendor-protocol emulation. Ordinary connectivity, passive observation, active authorized enumeration, identity imitation и disruptive load никогда не скрываются под одной кнопкой.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-BLE-01` | все | `include`, `DEC-0021` | Сквозной ownership | S3 единолично владеет baseline native BLE controller, identity, bond/key vault и scheduler; C5 BLE default-off и не создаёт параллельный product identity без отдельного requirement. Это не меняет физического владельца nRF24 и не сокращает их native feature set. |
| `REQ-BLE-02` | `C-BLE-01` | `conditional` | Сквозной feature matrix | Exact owner/profile доказывает 1M/2M/Coded PHY, legacy/extended advertising, multiple sets, simultaneous scan+advertise и central/peripheral roles до включения UI. Controller support, host support и tested peer support — разные states. |
| `REQ-BLE-03` | все | `conditional` | Сквозной stack | NimBLE/Bluedroid и ESP-IDF version выбираются воспроизводимой profile matrix по flash/heap, GAP/GATT/SMP/HID/ext-adv/Coded needs. Preferred lightweight stack не подменяет feature/security HIL; release содержит SBOM/config/version. |
| `REQ-BLE-04` | `C-BLE-01` | `include` | Основной | Ordinary scan показывает address+type, PHY, advertising type/set, payload length, RSSI, timestamp/age, duplicate/filter policy и scan coverage/loss. Active scan response запрашивается только в ordinary/authorized session; no-background default. |
| `REQ-BLE-05` | `C-BLE-01` | `conditional` | Основной | Extended/Coded scan/advertise показывает actual primary/secondary PHY, periodic/auxiliary status и truncation. Coded PHY не default: airtime/coexistence impact и peer support измеряются, unsupported остаётся `unknown`. |
| `REQ-BLE-06` | `C-BLE-02` | `conditional` | Основной | Offline company/service/device DB использует versioned licensed snapshots. Public/static/RPA/NRPA, company ID, service UUID и signature evidence разделены; OUI/company/signature не объявляют stable identity/model/owner. |
| `REQ-BLE-07` | `C-BLE-02` | `conditional` | Основной measurement | Proximity хранит raw RSSI/statistics, PHY, TX-power field provenance, sample window, orientation/calibration state и age. UI допускает calibrated `stronger/comparable/unknown`, но не метры, точную дальность или положение без отдельного ranging hardware/protocol. |
| `REQ-BLE-08` | `C-BLE-03` | `conditional` | Основной safety | Unwanted-tracker detector использует versioned proven signatures и temporal/co-presence evidence, показывает `potential compatible tracker`, confidence и unknown. Он не устанавливает owner/malicious intent и не обещает безопасность по отсутствию alert; identifiers/location minimized and redacted. |
| `REQ-BLE-09` | `C-BLE-04` | `conditional` | Лаборатория | Continuity/Flipper/vendor-type passive classification имеет source/licence/version/hash/fixture matrix и объяснимые matched fields. Непроверенный payload остаётся generic advertisement; proprietary name не означает compatibility или vulnerability. |
| `REQ-BLE-10` | `C-BLE-05`, `C-UX-01` | `conditional` | Лаборатория | BLE wardrive/geo-log/advertising PCAP — explicit foreground session с external GNSS provenance, coverage/loss, privacy minimization, encrypted vault и export/delete/retention. Rotating addresses не склеиваются без authorized IRK/evidence. |
| `REQ-BLE-11` | `OUT-03` | `defer`, `IMP-0004` | Лаборатория | Native controller не обещает passive Link-Layer connection follow. Такая запись появляется только после отдельного dedicated-sniffer decision и автономного PHY/channel/encryption/loss/timestamp/transport/licence/HIL proof; отсутствие дешифрования показывается явно. |
| `REQ-BLE-12` | `C-BLE-06` | `conditional` | Смешанный | Ordinary paired owner-service use может быть Main. Security GATT enumeration exact owned/authorized peer выполняется только в Controlled Zone `AUTHORIZED_TARGET`, с service/characteristic/property/security/read/write preview, bounded operations и no-write default. |
| `REQ-BLE-13` | `C-BLE-07`, `C-X-09` | `conditional` | Основной | BLE HID host/phone keyboard/companion input использует explicit pairing, allowlist, visible active peer, LE Secure Connections where supported, local disconnect/revoke и on-device input fallback. Remote input не подтверждает destructive/security actions без local confirmation. |
| `REQ-BLE-14` | `C-BLE-07`, `C-UX-02` | `conditional` | Смешанный | Ordinary interactive BLE HID device use is Main. Scripted BadBLE/Ducky injection — Controlled Zone `AUTHORIZED_TARGET`: exact host identity, script preview, bounded keys/time, hold-to-run, local STOP; imported scripts inert and share parser tests with USB without sharing authorization. |
| `REQ-BLE-15` | `C-BLE-08` | `conditional` | Смешанный | Custom/open beacon TX in owned namespace is Main with visible identity/rate/power. iBeacon/Eddystone/vendor profile names require exact specification/licence/rights and peer HIL; third-party identity imitation is Controlled Zone `AUTHORIZED_TARGET`, with no certification/trademark claim. |
| `REQ-BLE-16` | `C-BLE-11` | `defer` | Контролируемая зона, `BOTH` | Find My/AirTag-like emulation requires protocol/rights/corpus proof, authorized receiver/account fixture and conducted/RF-shielded containment preventing third-party network participation. Generic rotating advertisement is not Find My compatibility. |
| `REQ-BLE-17` | `C-BLE-09`, `C-BLE-10`, `C-BLE-12` | `conditional` | Контролируемая зона, `BOTH` | Pairing/notification/crash/connection/GATT flood and resilience tests run only conducted/RF-shielded on authorized fixtures with exact packet corpus/version, conservative power, rate/count/time ceiling, countdown, dead-man, STOP and no-leakage validation. Open-air nuisance/DoS mode absent. |
| `REQ-BLE-18` | `OUT-03` | `exclude baseline` | Контролируемая зона, `BOTH` | Native BLE does not promise jamming. Any interference-resilience source uses separately qualified hardware and the same conducted/RF-shielded `BOTH` contract; protocol failure is not evidence of intentional interference. |
| `REQ-BLE-19` | connections | `conditional` | Сквозной security | Ordinary bonds prefer LE Secure Connections, authenticated method when available, RPA/privacy and least-privilege GATT. `Just Works` is labelled without MITM proof. Bond/IRK/LTK/passkey/credential data encrypted, access-controlled, explicitly revocable/exportable only by policy and erased on factory reset. |
| `REQ-BLE-20` | all radio | `conditional` | Сквозной coexistence | S3 Wi-Fi/BLE TDM and cross-MCU C5/802.15.4/IR/nRF24 activity are scheduled with active owner, preemption/loss/latency visibility; если nRF24 также принадлежат S3, их local scheduler входит в тот же proof. Coded/high-duty advertising и scan не подавляют принятый Thread/Zigbee; unsafe simultaneous TX запрещён до antenna/self-desense HIL. |
| `REQ-BLE-21` | all records | `conditional` | Сквозной storage | Advertising/GATT/HID/session formats are versioned, bounded and fuzzed; identifiers/payload/location/keys have typed sensitivity, minimization/redaction, encrypted storage, explicit export/delete/retention and inert import. Parser/signature update follows owner-controlled signed lifecycle. |
| `REQ-BLE-22` | all | `acceptance` | Сквозной HIL | Exact module/antenna/owner fixture tests 1M/2M/Coded, legacy/extended scan/adv, RPA rotation/resolution, RSSI variance, tracker/signature false positives, GATT/SMP/HID peers, privacy, Wi-Fi/C5/nRF coexistence, crash/reset/update/link loss, STOP and shielded active tests. Unknown never becomes success/safe. |

## Явно не обещается

- Bluetooth Classic/BR/EDR на S3 или C5;
- passive follow/decryption чужого BLE connection штатным controller;
- stable identity из rotating address или generic advertisement;
- distance in metres, direction/AoA or precise location from RSSI alone;
- universal AirTag/Find My/Continuity/Flipper emulation or Apple certification;
- arbitrary GATT/HID action without target/preview/security gates;
- open-air pairing/crash/connection flood или BLE jammer;
- Bluetooth Mesh в baseline release; он сохранён как optional later profile по `DEC-0023`.

Полноценный BLE через nRF24 также не обещается: возможен только доказанный experimental legacy-1M advertising subset. Эта BLE-граница не ограничивает native nRF24L01+ PTX/PRX, Enhanced ShockBurst, rate/channel, ACK, pipe, FIFO, IRQ или RPD функции.

## Финальное ревью

Распространение `DEC-0021` проведено в `REV-0002Y`: owner/native/nRF24 boundary синхронизирована в обоих репозиториях. `DEC-0023` закрыл functional decision по extras: dedicated nRF52 connection sniffer и Bluetooth Mesh сохранены как optional `defer-release`, Bluetooth Classic — только как возможный внешний controller. Они не блокируют native BLE baseline и не входят в base BOM/core release.

## Первичные источники

- [ESP32-S3 datasheet](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-C5 datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [ESP32-S3 Bluetooth LE stack](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/ble/overview.html)
- [ESP32-S3 Wi-Fi/BLE coexistence](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/coexist.html)
- [ESP32-C5 RF coexistence](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/coexist.html)
- [Nordic nRF Sniffer](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-ble-sniffer/guides/running_sniffer.html)
- [Bluetooth SIG Security and Privacy Best Practices](https://www.bluetooth.com/download/bluetooth-security-and-privacy-best-practices-guide/)
- [Apple unwanted-tracker guidance](https://support.apple.com/en-us/119874)
