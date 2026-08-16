# INV-0002 — единый реестр хотелок продукта перед компоновкой

- Статус: **В работе; список не заморожен**
- Дата: 2026-08-16
- Основание: `DEC-0022`
- Детальный legacy-источник: `INV-0001`
- Назначение: отделить пользовательские функции от вариантов их аппаратной реализации

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
| `W-OWN-11` | dual-path consumer IR остаётся на C5 | `accepted` | `DEC-0018` |
| `W-OWN-12` | три одновременных полнофункциональных nRF24, без урезания native scope | `accepted` | `REQ-N24-0001`; physical owner не выбран |
| `W-OWN-13` | S3 — baseline native-BLE owner; C5 BLE default-off | `accepted` | `DEC-0021` |
| `W-OWN-14` | OpenThread open baseline; Zigbee optional conditional | `accepted` | `DEC-0020` |
| `W-OWN-15` | целевой готовый документ отдельно от текущей проработки в обоих репозиториях | `accepted` | `DEC-0011` |

## Полный импорт известных функциональных кандидатов

Все строки ниже раскрыты по одной в `INV-0001`; диапазон означает inclusion каждого ID, а не одну свёрнутую функцию.

| Блок | Детальные ID | Количество | Текущее состояние scope |
|---|---|---:|---|
| Wi-Fi 2.4 GHz S3 | `C-W24-01..12` | 12 | `candidate`; отдельный capability review не завершён |
| 3×nRF24 | `C-N24-01..10` | 10 | capability reviewed; physical layout deferred by `DEC-0022` |
| C5 Wi-Fi 2.4/5 GHz + IEEE 802.15.4 | `C-W5-01..09` | 9 | reviewed `REQ-W5-0001` |
| Native BLE | `C-BLE-01..12` | 12 | reviewed `REQ-BLE-0001` |
| Sub-GHz / CC1101 | `C-SUB-01..11` | 11 | `candidate`; capability review pending |
| LoRa/SX1262 | `C-LORA-01..09` | 9 | hardware attachment accepted; capability review pending |
| GNSS | `C-GPS-01..04` | 4 | reviewed `REQ-GNSS-0001` |
| Si4732 receiver | `C-RX-01..07` | 7 | reviewed `REQ-RX-0001` |
| Analog voice | `C-VHF-01..07` | 7 | reviewed `REQ-VHF-0001` |
| HF NFC/RFID | `C-NFC-01..10` | 10 | reviewed `REQ-NFC-0001` |
| Consumer IR | `C-IR-01..05` | 5 | reviewed `REQ-IR-0001` |
| System/UI/storage | `C-SYS-01..11` | 11 | reviewed `REQ-SYS-0001`; physical controls deferred |
| Cross-cutting | `C-X-01..11` | 11 | частично покрыто reviewed contracts; итоговая матрица pending |
| Составные UX sessions | `C-UX-01..03` | 3 | `candidate`; decomposition pending |
| Performance/power candidates | `C-HWX-01..04` | 4 | `candidate`; acceptance metric pending |
| **Итого** |  | **125** | полный перенос legacy и независимых additions доказан `REV-0002A` |

## Явно найденные дополнительные хотелки, ещё не принятые

Каждая строка ниже должна быть отдельно показана владельцу со знаком `⚠️`; отсутствие ответа не означает принятие или отказ.

| ID | ⚠️ Возможная хотелка | Состояние | Почему отдельный вопрос |
|---|---|---|---|
| `W-EXTRA-01` | EAPOL/PMKID capture на поддерживаемом Wi-Fi path | `needs-owner` | `IMP-0003`; passive capture надо отделить от active exploit и private patch |
| `W-EXTRA-02` | настоящий BLE connection-follow sniffer через отдельный nRF52-class accessory/onboard block | `needs-owner` | `IMP-0004`; native S3 BLE этого не даёт |
| `W-EXTRA-03` | ordinary Bluetooth Mesh node/provisioner | `needs-owner` | `IMP-0020`; новый radio не нужен, но растут key/flash/RAM/HIL scope |
| `W-EXTRA-04` | Bluetooth Classic через третий controller | `needs-owner` | `OUT-03`; S3/C5 LE-only |
| `W-EXTRA-05` | дополнительные HF/VHF/30–64 MHz/DRM RX/TX возможности вне Si4732 | `needs-owner` | `OUT-05`; требуется другой RF backend |
| `W-EXTRA-06` | full-duplex repeater или digital voice | `needs-owner` | `OUT-07`; нужен второй RF path или другой модуль |
| `W-EXTRA-07` | wideband SDR + более мощный compute/Linux analytics | `needs-owner` | `OUT-08`; другой класс устройства/расширения |
| `W-EXTRA-08` | cellular/GSM/LTE connectivity | `needs-owner` | `OUT-09`; modem, SIM/eSIM, certification и power budget |
| `W-EXTRA-09` | LF 125 kHz NFC/RFID | `needs-owner` | `OUT-06`; отдельный frontend, U216 этого не добавляет |
| `W-EXTRA-10` | двухfrontend NFC relay и тяжёлый key-recovery compute | `needs-owner` | `OUT-06`; не является бесплатной функцией U216 |

## Не хотелки, а варианты будущей реализации

Эти пункты нельзя принимать до freeze только потому, что они уже исследованы:

| Вариант | Что он решает | Состояние |
|---|---|---|
| `IMP-0002` SDIO S3↔C5 | освобождает GP-SPI C5 | ⚠️ layout candidate |
| `IMP-0010` key matrix/expander/STOP/audio control | цена, GPIO и независимый STOP | ⚠️ layout candidate |
| `IMP-0021` nRF24 owner S3/C5 | ownership, bus load и IPC | ⚠️ layout candidate |
| CE latch/direct CE/decoder | независимые CE и GPIO trade | ⚠️ component/layout candidate |
| удаление C5 UART bridge | потенциально освобождает S3 GPIO | ⚠️ recovery-dependent candidate |

## Completeness gate до wishlist freeze

- [x] все legacy capability rows импортированы без потерь;
- [x] owner additions из текущего диалога занесены;
- [x] известные найденные extras вынесены отдельно;
- [ ] завершены `REQ-*` для Wi-Fi 2.4, Sub-GHz/CC1101 и LoRa;
- [ ] завершена cross-cutting/UX/performance матрица;
- [ ] каждое `W-EXTRA-*` получило ответ владельца;
- [ ] `AUD-0001` завершил все `OUT-01..09`;
- [ ] у каждой желаемой функции есть zero-loss acceptance boundary;
- [ ] владелец подтвердил, что крупных пропущенных хотелок больше нет;
- [ ] владелец явно подтвердил wishlist freeze.

## Порядок дальнейшего прохода

1. Сначала обычные Main-функции каждого незавершённого блока.
2. Затем пассивные/защитные Lab-функции того же блока.
3. Затем active/disruptive Controlled-Zone функции с legal/containment boundary.
4. Отдельно показать каждую `W-EXTRA-*` и получить только функциональное решение — без выбора GPIO или placement.
5. После закрытия всех строк провести owner completeness review и freeze.
6. Только затем строить S3-heavy, C5-heavy и balanced/modular компоновки на одинаковом demand model.
