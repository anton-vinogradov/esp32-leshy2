# INV-0002 — единый реестр хотелок продукта перед компоновкой

- Статус: **125 прежних leaves проведено ревью; G2 точечно переоткрыт `FND-0040/AUD-0004`**
- Дата: 2026-08-16
- Основание: `DEC-0022`
- Детальный legacy-источник: `INV-0001`
- Назначение: отделить пользовательские функции от вариантов их аппаратной реализации
- Группированный пакет: `INV-0003`; итоговое саморевью: `INV-0004`

## Правило реестра

В реестр сначала попадает всё, что владелец может захотеть сохранить или добавить. Наличие строки не обещает реализацию. До wishlist freeze обсуждаются пользовательский результат, уровень безопасности, честный предел, legal/technical prerequisite и критерий «без потерь». MCU owner, transport, GPIO и layout выбираются позже.

Состояния:

- `accepted` — желание уже подтверждено владельцем;
- `candidate` — сохранённый legacy-кандидат, ещё не ставший требованием;
- `needs-owner` — найденная дополнительная возможность, требующая явного ответа;
- `defer-release` — желание сохраняется, но не обязательно для первой версии;
- `exclude-proven` — текущий класс hardware доказанно не способен, возможен только новый аппаратный блок;
- `rejected-by-owner` — владелец явно отказался от функции.

## Неподвижные продуктовые хотелки владельца

| ID | Хотелка | Состояние | Каноническая граница |
|---|---|---|---|
| `W-OWN-01` | автономный all-in-one полевой прибор | `accepted` | `DEC-0002` |
| `W-OWN-02` | Main → Lab → вложенная Controlled Zone | `accepted` | `DEC-0010` |
| `W-OWN-03` | install-time акт о ненападении плюс технические interlock | `accepted` | `DEC-0002`, `DEC-0010` |
| `W-OWN-04` | консервативный TX default; максимум только явно | `accepted` | `DEC-0003` |
| `W-OWN-05` | снижение полной стоимости без потери продукта | `accepted` | `DEC-0005` |
| `W-OWN-06` | повторно рассматривать legal+technical legacy ceilings и обходы | `accepted` | `DEC-0004` |
| `W-OWN-07` | открытая owner-controlled цепочка подписанных обновлений без обязательного lockdown | `accepted` | `DEC-0013` |
| `W-OWN-08` | бортового GNSS нет; внешний M5 GPS или GNSS комбинированного expansion | `accepted` | `DEC-0006`, `DEC-0014` |
| `W-OWN-09` | бортового LoRa нет; U214 Cap и модульный expansion path для общепринятых 868/915 profiles | `accepted` | `DEC-0008` |
| `W-OWN-10` | onboard ES8311 mono digital audio с fail-safe analog bypass | `accepted` | `DEC-0009` |
| `W-OWN-11` | dual-path consumer IR с robust receive и отдельным carrier-learning path | `accepted` | `DEC-0018`; physical owner открыт `DEC-0032` |
| `W-OWN-12` | три одновременных полнофункциональных nRF24, без урезания native scope | `accepted` | `REQ-N24-0001`; physical owner не выбран |
| `W-OWN-13` | baseline native BLE с одним явным product identity/key-vault owner | `accepted` | controller/physical owner открыт `DEC-0032`; former S3 profile — reference |
| `W-OWN-14` | OpenThread open baseline; Zigbee optional conditional | `accepted` | `DEC-0020` |
| `W-OWN-15` | целевой готовый документ отдельно от текущей проработки в обоих репозиториях | `accepted` | `DEC-0011` |
| `W-OWN-16` | M5-first low-rate Unit/Cap expansion плюс отдельный high-throughput class; без native M5-Bus | `accepted` | `DEC-0034`, `REQ-EXT-0001` |

## Полный импорт известных функциональных кандидатов

Все строки ниже раскрыты по одной в `INV-0001`; диапазон означает inclusion каждого ID, а не одну свёрнутую функцию.

| Блок | Детальные ID | Количество | Текущее состояние scope |
|---|---|---:|---|
| Wi-Fi 2.4 GHz / ESP-NOW | `C-W24-01..12` | 12 | reviewed capability `REQ-W24-0001`; backend открыт |
| 3×nRF24 | `C-N24-01..10` | 10 | capability reviewed; physical layout deferred by `DEC-0022` |
| Wi-Fi 2.4/5 GHz + IEEE 802.15.4 | `C-W5-01..09` | 9 | reviewed capability `REQ-W5-0001`; backend открыт |
| Native BLE | `C-BLE-01..12` | 12 | reviewed `REQ-BLE-0001` |
| Sub-GHz / CC1101 | `C-SUB-01..11` | 11 | reviewed `REQ-SUB-0001` |
| LoRa/SX1262 | `C-LORA-01..09` | 9 | reviewed `REQ-LORA-0001` |
| GNSS | `C-GPS-01..04` | 4 | reviewed `REQ-GNSS-0001` |
| Si4732 receiver | `C-RX-01..07` | 7 | reviewed `REQ-RX-0001` |
| Analog voice | `C-VHF-01..07` | 7 | reviewed `REQ-VHF-0001` |
| HF NFC/RFID | `C-NFC-01..10` | 10 | reviewed `REQ-NFC-0001` |
| Consumer IR | `C-IR-01..05` | 5 | reviewed `REQ-IR-0001` |
| System/UI/storage | `C-SYS-01..11` | 11 | reviewed `REQ-SYS-0001`; physical controls deferred |
| Cross-cutting | `C-X-01..11` | 11 | reviewed `REQ-X-0001` |
| Составные UX sessions | `C-UX-01..03` | 3 | reviewed `REQ-X-0001` |
| Performance/power candidates | `C-HWX-01..04` | 4 | reviewed as acceptance mechanisms, `REQ-X-0001`/`REQ-LORA-0001` |
| **Итого** |  | **125** | полный перенос legacy и независимых additions доказан `REV-0002A` |

## Явно найденные дополнительные хотелки после саморевью

Десять source-строк получили решение по делегированному саморевью. Две смешанные строки декомпозированы, поэтому leaf-решений двенадцать; полные boundaries — в `INV-0004`.

| ID | ⚠️ Возможная хотелка | Состояние | Почему отдельный вопрос |
|---|---|---|---|
| `W-EXTRA-01` | EAPOL/PMKID capture на поддерживаемом Wi-Fi path | `conditional` | passive Lab only; no onboard cracking |
| `W-EXTRA-02` | BLE connection-follow sniffer | `defer-release` | optional nRF52-class accessory |
| `W-EXTRA-03` | ordinary Bluetooth Mesh | `defer-release` | optional software profile, no new radio |
| `W-EXTRA-04` | Bluetooth Classic | `defer-release` | optional external controller only |
| `W-EXTRA-05` | дополнительные HF/VHF/30–64 MHz/DRM | `defer-release` | optional RF/SDR expansion |
| `W-EXTRA-06A` | digital voice | `defer-release` | optional protocol/backend profile |
| `W-EXTRA-06B` | full-duplex repeater | `defer-release` | optional dual-RF architecture |
| `W-EXTRA-07` | wideband SDR + Linux analytics | `defer-release` | external SDR/compute profile |
| `W-EXTRA-08` | cellular/GSM/LTE | `defer-release` | external/tethered certified modem profile |
| `W-EXTRA-09` | LF 125 kHz NFC/RFID | `defer-release` | external LF frontend |
| `W-EXTRA-10A` | two-frontend NFC relay | `defer-release` | optional Controlled-Zone attachment |
| `W-EXTRA-10B` | heavy key-recovery compute | `defer-release` | owner-controlled off-device compute |

## Current competitor delta — решения открыты

[`AUD-0004`](../audits/AUD-0004-current-competitor-capability-gap.md) добавил
не принятые функции, а полный список отсутствовавших вопросов. До owner
disposition они имеют состояние `needs-owner` и не входят в target молча.

| ID | ⚠️ Возможная хотелка | Состояние |
|---|---|---|
| `W-EXTRA-11` | iButton/1-Wire read/emulate и bounded write | `accepted-external`: `DEC-0033`, passive M5-style Port-B adapter; no base pad |
| `W-EXTRA-12` | modern FIDO2/CTAP USB authenticator + U2F compatibility | `needs-owner`: `AUD-0006/IMP-0029` |
| `W-EXTRA-13` | haptic feedback | `needs-owner` |
| `W-EXTRA-14` | IMU/orientation/motion | `needs-owner` |
| `W-EXTRA-15` | physical text keyboard as product archetype | `needs-owner`, G3 |
| `W-EXTRA-16` | dual-role/high-speed USB accessory host | `needs-owner` |
| `W-EXTRA-17` | 6 GHz/Wi-Fi 6E beyond accepted 5 GHz | `needs-owner` |

## Исторические идеи реализации, не входные ограничения

Эти пункты зафиксированы только как справочный материал из прежней документации. Они не являются активными кандидатами, не задают оси сравнения и могут попасть в новую архитектуру лишь тогда, когда независимо заново выводятся из `CAP-0001`, `CON-0001` и `RES-0001`:

| Вариант | Что он решает | Состояние |
|---|---|---|
| `IMP-0002` SDIO S3↔C5 | освобождает GP-SPI C5 | архивная идея; требуется независимый повторный вывод |
| `IMP-0010` key matrix/expander/STOP/audio control | цена, GPIO и независимый STOP | архивная идея; требуется независимый повторный вывод |
| `IMP-0021` nRF24 owner S3/C5 | ownership, bus load и IPC | архивная идея; прежняя постановка owner S3/C5 не ограничивает новый синтез |
| CE latch/direct CE/decoder | независимые CE и GPIO trade | архивная идея; требуется независимый повторный вывод |
| удаление C5 UART bridge | потенциально освобождает S3 GPIO | архивная идея; требуется независимый повторный вывод |

## Historical completeness gate and reopened delta

- [x] все legacy capability rows импортированы без потерь;
- [x] owner additions из текущего диалога занесены;
- [x] известные найденные extras вынесены отдельно;
- [x] группировка `INV-0003` прошла делегированное саморевью;
- [x] завершены `REQ-*` для Wi-Fi 2.4, Sub-GHz/CC1101 и LoRa;
- [x] завершена cross-cutting/UX/performance матрица;
- [x] каждое `W-EXTRA-*` получило disposition;
- [x] `AUD-0001` завершил product-level disposition `OUT-01..09`;
- [x] у каждой желаемой функции есть zero-loss acceptance boundary;
- [x] completeness проверена по legacy, owner additions и extras;
- [x] freeze принят по явной делегации владельца в `DEC-0023`.
- [ ] current competitor delta получает owner disposition: `W-EXTRA-11`
  закрыт `DEC-0033`, infrastructure `IMP-0028` закрыт `DEC-0034`;
  `W-EXTRA-12` reviewed facts/open `IMP-0029`; `W-EXTRA-13..17` открыты;
- [ ] G2 проходит новое propagation review после решений.

## Следующий этап после закрытия delta

Corrected `FLOW-0001` сначала принимает target product design, затем заново
выводит complete whole-device candidates без заранее назначенного radio owner,
transport или pin map. Former `CAP/CON/RES/SYN` studies сохранены только как
reference и не являются обязательными inputs. Pin budget не используется для
удаления wishlist задним числом.
