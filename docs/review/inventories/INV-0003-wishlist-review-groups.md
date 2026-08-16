# INV-0003 — сгруппированный пакет хотелок для owner review

- Статус: **На ревью владельца — проверяется группировка, не принимаются функции оптом**
- Дата: 2026-08-16
- Основание: `DEC-0022`, `INV-0001`, `INV-0002`
- Полнота: **125 из 125 кандидатных строк распределены ровно по одной группе**

## Как проводить ревью

Эта группировка нужна, чтобы обсуждать продукт понятными блоками, не прыгая между GPIO и firmware. Подтверждение `INV-0003` означает только «группы полны и удобны». Оно не принимает все функции внутри группы и не замораживает wishlist.

Каждая группа затем проходит одинаково:

1. обычные Main-функции;
2. пассивные и защитные Lab-функции;
3. active/identity/injection Controlled-Zone функции;
4. disruptive/DoS/interference только с `ISOLATED_ONLY`, `AUTHORIZED_TARGET` или `BOTH`;
5. найденные extras;
6. zero-loss boundary и только класс resource demand без выбора MCU/GPIO/layout.

## Девять основных групп

| Порядок | Группа | Единственное размещение ID | Кол-во | Что пользователь получает | Состояние перед owner review |
|---:|---|---|---:|---|---|
| 1 | `WG-01` Платформа, UI, safety, storage и обслуживание | `C-SYS-01..11`, `C-X-01..04`, `C-X-07`, `C-X-09`, `C-X-11`, `C-HWX-01`, `C-HWX-03..04` | 21 | launcher/input, SD/USB/OTA, power/sleep, self-test, STOP/TX state, update/recovery, phone input, alerts и performance infrastructure | базовый `REQ-SYS-0001` reviewed; cross/performance хвост требует review |
| 2 | `WG-02` Навигация, журналирование и составные полевые сессии | `C-GPS-01..04`, `C-X-05..06`, `C-X-08`, `C-X-10`, `C-UX-01`, `C-UX-03` | 10 | position/time/track, GNSS integrity, geo-tagged captures, combined spectrum/wardrive, Remote-ID, быстрый replay собственных записей | GNSS reviewed; combined privacy/session/replay boundary pending |
| 3 | `WG-03` Broadcast receiver и analog voice | `C-RX-01..07`, `C-VHF-01..07` | 14 | FM/RDS/LW/MW/SW/SSB/CW, scan/log/record/decode, NFM voice, tones, modem/APRS/SSTV и bounded relay | reviewed contracts; отдельные deferred/extras не принимаются автоматически |
| 4 | `WG-04` Consumer IR | `C-IR-01..05` | 5 | обучение, decode, own remote/replay, universal DB и изолированные security sweeps | capability reviewed; layout позже |
| 5 | `WG-05` HF NFC/RFID | `C-NFC-01..10` | 10 | tag read/write/NDEF/library, credential analysis, emulation/recovery/clone с разными gates | capability reviewed; extra LF/relay отдельно |
| 6 | `WG-06` Wi-Fi и IP/local-network функции | `C-W24-01..12`, `C-W5-01..08` | 20 | AP/STA/ESP-NOW/SoftAP/OTA, scan/metrics/capture/detection и изолированные active security tests в 2.4/5 GHz | C5 slice reviewed; S3 2.4 slice и cross-owner dedup pending |
| 7 | `WG-07` Native BLE и IEEE 802.15.4 | `C-BLE-01..12`, `C-W5-09`, `C-UX-02` | 14 | ordinary BLE/GATT/HID/beacons, tracker safety, Thread/Zigbee/raw 802.15.4 и единый BadBLE/BadUSB script UX | baseline reviewed; extras Mesh/sniffer/Classic отдельно |
| 8 | `WG-08` Три полнофункциональных nRF24 | `C-N24-01..10` | 10 | independent PTX/PRX, RPD hunt, ESB discovery/analysis, authorized exploitation и contained RF tests | capability reviewed; owner/bus/GPIO/layout только после freeze |
| 9 | `WG-09` Sub-GHz CC1101 и внешний LoRa | `C-SUB-01..11`, `C-LORA-01..09`, `C-HWX-02` | 21 | receive/spectrum/decode/replay, P2P/mesh/APRS/LoRaWAN/file transfer, modulation tests и contained resilience tests | attachment direction accepted; capability contracts pending |
|  | **Итого** |  | **125** |  | каждая строка размещена один раз |

## Сквозные принятые условия

`W-OWN-01..15` не образуют десятую подсистему и не дублируют 125 функций. Они накладываются на все группы:

- all-in-one и три пользовательских уровня;
- install-time акт и per-tool technical gates;
- conservative TX default и независимый STOP;
- zero-loss cost review;
- открытая owner-controlled signed-update chain;
- внешние GNSS/LoRa paths;
- full-function 3×nRF24, S3 native BLE, C5 IR, OpenThread/conditional Zigbee;
- target README отдельно от current-state.

## Четыре пакета дополнительных хотелок

Ни один пакет не принимается подтверждением группировки. Каждая строка позднее получает отдельный ответ.

| Пакет | ⚠️ Extras | Влияние |
|---|---|---|
| `WE-01` Дополнительное наблюдение протоколов | `W-EXTRA-01` EAPOL/PMKID, `W-EXTRA-02` BLE connection sniffer, `W-EXTRA-04` Bluetooth Classic | privacy/storage; для BLE sniff/Classic появляется дополнительный radio/accessory |
| `WE-02` Дополнительные сети | `W-EXTRA-03` Bluetooth Mesh, `W-EXTRA-08` cellular | Mesh в основном software/resource scope; cellular добавляет modem/SIM/power/certification |
| `WE-03` Расширенный RF и compute | `W-EXTRA-05` дополнительные HF/VHF/DRM, `W-EXTRA-06` full-duplex/digital voice, `W-EXTRA-07` wideband SDR/Linux analytics | новый RF/compute class, возможно отдельный модуль или иная версия устройства |
| `WE-04` Расширенный RFID | `W-EXTRA-09` LF 125 kHz, `W-EXTRA-10` two-frontend relay/heavy recovery | отдельный LF frontend либо второй HF frontend/compute; не бесплатное продолжение U216 |

## Почему security не вынесена в отдельную аппаратную группу

Security level — свойство сценария, а не radio chip. Например, BLE HID для своего телефона относится к Main, passive vendor classification — к Lab, scripted injection — к Controlled Zone, а crash flood — к `BOTH`. Разносить их по разным аппаратным группам означало бы дублировать BLE и потерять общий ресурсный prerequisite. Поэтому уровни раскрываются внутри каждой `WG-*`.

## Предлагаемый порядок подробного ревью

`WG-01` → `WG-02` → `WG-03` → `WG-04` → `WG-05` → `WG-06` → `WG-07` → `WG-08` → `WG-09` → `WE-01..04` → completeness review → wishlist freeze.

Порядок идёт от платформы и обычных полевых функций к радиосетям, специализированным transceiver и дополнительным аппаратным классам. Внутри каждой группы опасность всегда возрастает от Main к contained disruptive tests.

## Вопрос текущего ревью

Подтверждает ли владелец девять `WG-*`, четыре `WE-*`, отсутствие дублей и предложенный порядок как удобную структуру дальнейшего review? Это не является принятием функций внутри групп.
