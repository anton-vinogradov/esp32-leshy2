# Аппаратная часть Leshy2 — текущее состояние проработки

> Снимок: 2026-08-16. Эта страница описывает, что доказано сейчас. Образ готового продукта находится в [целевом hardware README](../../README.ru.md), а готового ПО — в [целевом firmware README](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md).

- Канонические доказательства: [журнал ревью](../review/README.md)
- English version: [current-state.md](current-state.md)
- Legacy только для справки: [`drafts/legacy-2026-08-15/`](../../drafts/legacy-2026-08-15/README.md)

## Ход ревью

| Этап | Состояние |
|---|---|
| 0. Система ревью и baseline | Проведено ревью |
| 1. Видение и границы | Проведено ревью, включая трёхуровневое уточнение |
| 2. Возможности и исключения | Проведено ревью (`REV-0002AD`) |
| 3. Архитектура и владение | В работе |
| 4–10 | Не начато |

Каноническая таблица стадий — [`docs/review/stages.md`](../review/stages.md).

## Принятые целевые решения, уже отражённые на продуктовой странице

- all-in-one профиль, акт о ненападении и три уровня функциональности (`DEC-0002`, `DEC-0010`);
- консервативные TX-дефолты и явный выбор максимальной мощности (`DEC-0003`);
- оптимизация полной стоимости без потери продукта (`DEC-0005`);
- внешний M5 GNSS и внешний U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- NMEA baseline и условный per-revision advanced CASIC profile без дополнительного GNSS (`DEC-0014`);
- FM/RDS/ordinary AM baseline и открытый owner-imported SSB/CW patch loader без bundled blob (`DEC-0015`);
- условный dual-band analog-voice target на SA518 с честным UHF-only fallback на SA868S (`DEC-0016`);
- отдельный STOP-dominant `VVOICE` 4.0 V для SA518 и раздельная stuffing/supply qualification SA868S (`DEC-0025`);
- внешний M5 Unit NFC U216 как первый HF NFC backend, RFID2 как limited compatibility и custom PN7160 как qualification fallback (`DEC-0017`);
- двухтрактный consumer IR на C5 с robust RX TSOP38238 и TSMP95000 для измерения несущей 30–60 kHz (`DEC-0018`);
- калиброванный трёхантенный nRF24 RPD hit-rate поиск по секторам без выдуманных RSSI/dBm, пеленга или VSWR (`DEC-0019`);
- OpenThread как открытый Thread baseline и optional conditional Zigbee adapter без закрытия core product (`DEC-0020`);
- S3 как единственный baseline native-BLE owner; C5 BLE default-off, полный native nRF24 scope не сокращён (`DEC-0021`);
- сначала полный owner-confirmed реестр хотелок, затем несколько компоновок и сводный бюджет ресурсов (`DEC-0022`);
- замороженный wishlist из 125 leaf-функций после делегированного саморевью с границами base/optional/deferred (`DEC-0023`);
- latched physical hard STOP, который сбрасывает оба MCU, независимо inhibit/обесточивает внешние TX-домены и требует физического re-arm (`DEC-0024`);
- бортовая mono audio-архитектура ES8311 с fail-safe analog bypass (`DEC-0009`);
- IR остаётся у C5; владелец трёх полнофункциональных nRF24 открыт для сравнения этапа 3 и больше не указан как принятый C5 target (`DEC-0001`, `DEC-0023`, `FND-0028`).
- owner-controlled подписанные обновления S3/C5 с rollback и открытым developer lifecycle (`DEC-0013`) без включения необратимого hardware lockdown.

## Открытое инженерное состояние

- `FND-0001`: единственный GP-SPI C5 не может одновременно выполнять legacy-роли nRF-master и S3↔C5-slave.
- `FND-0003`: audio-архитектура принята, но pin/electrical/firmware/HIL proof ещё не выполнен.
- `FND-0006`: исходная матрица кнопок и audio-control конфликтуют на `U13.P10..P17`.
- `FND-0007`: текущий артефакт всё ещё имеет только I²C-expander STOP input. `DEC-0024` исправляет target architecture, но latch/gates/rails и fault-injection HIL не реализованы.
- `FND-0011`: текущему SA868 добавлены PTT receive-default, PD power-down-default и физический low-power H/L. `DEC-0024/0025` исправляют target STOP/power architecture; exact gates и HIL не реализованы.
- `FND-0013`: VOX не имеет microphone-capture path и явно отложен до общего audio/pin budget.
- `FND-0015`: оба документированных M5 NFC Unit требуют PORT.A power profile 5 V, а текущие `J40/J41` дают 3.3 V; электрическое исправление ждёт общего port/power design.
- `FND-0017`: legacy IR source всё ещё использует S3 ownership, generic unqualified emitter/current path и не имеет доказанных STOP/TX-state/optical behavior. Ложная `FAB-READY` пометка снята, Q58 получил reset-safe pull-down.
- `FND-0019`: три generic nRF24 PA/LNA placeholder всё ещё используют S3 bus, exact modules/STOP/TX detectors отсутствуют, а post-dual-IR C5 resource budget не доказан. Ложные `FAB-READY` пометки сняты, общий CE получил reset-safe pull-down.
- `FND-0021`: ESB/MouseJack/KeySniffer/BLE-compatible/interference claims требуют раздельных capability/security/licence/HIL gates.
- `FND-0022`: C5 source candidate и antenna comment были неверны. Они исправлены на current-standard N8R8/`C51950748` и штатный `ANT1`; final antenna/cable/power/STOP/TX-live/EMC/AVL qualification остаётся открытой.
- `FND-0023`: public C5 Wi-Fi raw TX не поддерживает arbitrary management/deauth, `AUTO` не simultaneous dual-band, а любой patched vendor binary требует отдельной provenance/licence/update/HIL границы.
- `FND-0024`: 5 GHz режимы ещё не имеют реализованных country/DFS/PMF/privacy gates; DFS SoftAP исключён текущим radio contract.
- `FND-0026`: native BLE advertising scan не является promiscuous connection-follow sniffer, rotating address не является stable identity, а RSSI не доказывает метры или направление.
- `FND-0027`: Continuity/iBeacon/Find My и attack labels требуют versioned corpus/spec/licence/peer proof; ordinary, passive и disruptive BLE-сценарии имеют разные security gates.
- `FND-0028`: прежние static nRF ownership maps были сравнены, но после `DEC-0027` перенесены в справочный архив и не являются входными ограничениями нового synthesis.
- `FND-0029`: вариант памяти S3, транспорт S3↔C5 и recovery interfaces расходуют пересекающиеся scarce pins. N8R8 не является drop-in заменой N8R2, потому что Octal PSRAM занимает GPIO35–37, а 4-bit SDIO C5 конфликтует с native USB на GPIO13/14.
- `FND-0030`: legacy voice power 5 V превышает принятый SA518 1 W profile. `DEC-0025` исправляет target отдельным rail 4.0 V; legacy schematic и conducted HIL остаются открытыми.
- `FND-0032`: старый matrix budget ошибочно освобождал U214 RESET. Corrected candidate сохраняет `EXT_RF_RST`, переносит C5 BOOT в physical recovery и агрегирует touch IRQ; matrix/U14 всё ещё требует решения и HIL.
- Существующие tsCircuit/KiCad остаются legacy-артефактами реализации до ревью производящих стадий и регенерации.

## Текущая работа ревью

System/UI/storage capability-срез завершён статусом **«Проведено ревью»** в `REV-0002I`.

GNSS/navigation срез [`REQ-GNSS-0001`](../review/requirements/REQ-GNSS-0001-navigation-integrity.md) получил статус **«Проведено ревью»** в `REV-0002K`. Владелец принял `IMP-0012/A` как [`DEC-0014`](../review/decisions/DEC-0014-casic-gnss-profile.md): NMEA — обязательный baseline квалифицированного профиля, а assistance и receiver-reported jamming/spoofing условны proof точной revision/firmware. Unsupported/timeout/parser error означают `unknown`, не «угроз нет»; host heuristics отделяются от статуса receiver.

`FND-0009` закрыт на requirement-level. UART/power hardware, parser, assistance source, поддержка advanced messages конкретными Unit/U214, RF self-desense и HIL ещё не реализованы и проверяются на последующих этапах.

Si4732-срез [`REQ-RX-0001`](../review/requirements/REQ-RX-0001-si4732-receiver.md) получил статус **«Проведено ревью»** в `REV-0002M`. Владелец принял `IMP-0013/A` как [`DEC-0015`](../review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md): открытый bounded loader входит в target, SSB blob импортируется локально и имеет отдельные integrity/provenance состояния, а synchronous-AM остаётся deferred до отдельного proof. `FND-0010` закрыт на requirement-level; RF/frontend, patch rights/compatibility, loader, audio/storage/decoder и coexistence HIL ещё не реализованы.

Analog-voice срез [`REQ-VHF-0001`](../review/requirements/REQ-VHF-0001-analog-voice-modem.md) получил статус **«Проведено ревью»** в `REV-0002O`. Владелец принял `IMP-0014/A` как [`DEC-0016`](../review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md): SA518 — предпочтительный half-duplex analog-FM target 136–174/400–470 MHz, а SA868S остаётся явно UHF-only fallback до qualification. [`DEC-0025`](../review/decisions/DEC-0025-dedicated-4v-sa518-voice-rail.md) теперь фиксирует отдельный BAT-fed `VVOICE` 4.0 V для SA518 и отдельную stuffing/supply qualification fallback. Компромисс 2 W-class→1 W принят и не считается экономией без потерь. `FND-0012` закрыт на requirement-level; microphone capture/VOX (`FND-0013`), exact STOP/power hardware, protocol, RF, audio и HIL proof остаются для следующих этапов.

NFC/RFID-срез [`REQ-NFC-0001`](../review/requirements/REQ-NFC-0001-hf-nfc-rfid.md) получил статус **«Проведено ревью»** в `REV-0002Q`. Владелец принял `IMP-0005/A` как [`DEC-0017`](../review/decisions/DEC-0017-u216-hf-nfc-backend.md): внешний M5 Unit NFC U216 за $7 — первый HF NFC target, RFID2 за $4.95 — limited compatibility, а custom PN7160 — fallback только после провала qualification. Дельта аксессуара $2.05 принята ради A/B/F/V, ISO15693/FeliCa, limited emulation и custom-mode scope и не влияет на base BOM. `FND-0016` закрыт на requirement-level явными трёхуровневыми гейтами и отказом от overclaim universal clone, relay с одним frontend, key recovery, LF 125 kHz и payment compliance. Exact IC U216 имеет статус NRND; proof точной revision/lifecycle, 5-вольтовый `PORT.A-NFC` (`FND-0015`), driver/SBOM, protocol и HIL остаются открытой реализационной работой.

Consumer-IR срез [`REQ-IR-0001`](../review/requirements/REQ-IR-0001-consumer-infrared.md) получил статус **«Проведено ревью»** в `REV-0002S`. Владелец принял `IMP-0015/A` как [`DEC-0018`](../review/decisions/DEC-0018-dual-path-consumer-ir.md): C5 использует TSOP38238 для robust demodulated 38 kHz приёма и TSMP95000 для обучения с измерением несущей 30–60 kHz, занимая оба RX RMT channels C5; TSAL6200 — первый условный кандидат 940 nm emitter. Более дешёвые single-learning/fixed-38 варианты теряют принятую функцию и не могут подменить решение молча. `FND-0018` закрыт на requirement-level; автоматическое обучение 455 kHz/out-of-band остаётся deferred. Own remote/replay находится в Main, passive analysis — в Lab, unknown replay — в Controlled Zone `AUTHORIZED_TARGET`, а TV-B-Gone/brute-force/multi-code sweep — в Controlled Zone `BOTH`. `FND-0017`, C5 pins/transport, exact BOM, STOP, optics, licences и HIL остаются открытой реализационной работой.

Capability-аудит 3×nRF24 прошёл `REV-0002T`/`REV-0002U`: [`REQ-N24-0001`](../review/requirements/REQ-N24-0001-three-nrf24-raw-2g4.md) сохраняет три одновременных полнофункциональных radio и принятый [`DEC-0019`](../review/decisions/DEC-0019-calibrated-rpd-three-antenna-hunt.md) — calibrated binary RPD hit-rate sector comparison, никогда не RSSI/dBm/bearing/VSWR. Physical owner остаётся полностью открытым. `REV-0002Z`/`AUD-0003`/`IMP-0021` являются только историческими источниками идей и рисков; новый synthesis не принимает их раскладки. По [`DEC-0026`](../review/decisions/DEC-0026-atomic-integrated-architecture-acceptance.md) owner/transport отдельно не принимаются. `FND-0019`/`FND-0021` остаются implementation gates.

C5 Wi-Fi/IEEE 802.15.4 prerequisite audit прошёл `REV-0002V`, а финальное распространение [`REV-0002W`](../review/reviews/REV-0002W-c5-wifi-802154-decision-propagation.md) дало [`REQ-W5-0001`](../review/requirements/REQ-W5-0001-c5-wifi-ieee802154.md) статус **«Проведено ревью»**. Владелец принял `IMP-0018/A` как [`DEC-0020`](../review/decisions/DEC-0020-open-first-thread-conditional-zigbee.md): OpenThread — открытый baseline, Zigbee — optional conditional adapter, не требуемый core/raw/Thread build. Main/Lab/Controlled Zone разделены; C5 shared 2.4 GHz path не выдаётся за одновременные radio. `FND-0025` закрыт на requirement-level. Source candidate N8R4→N8R8, ANT1/ANT2 и EPAD исправлены, но final RF artifact остаётся открытым (`FND-0022`); public/raw/patched boundary (`FND-0023`) и DFS/country/PMF/privacy (`FND-0024`) также ждут implementation/HIL. `IMP-0003` и private patched Wi-Fi backend не приняты автоматически.

Native BLE prerequisite audit [`REV-0002X`](../review/reviews/REV-0002X-ble-prerequisites.md) завершён решением [`DEC-0021`](../review/decisions/DEC-0021-s3-native-ble-owner.md) и распространением [`REV-0002Y`](../review/reviews/REV-0002Y-s3-native-ble-decision-propagation.md): S3 — единственный baseline native-BLE owner, C5 BLE default-off, [`REQ-BLE-0001`](../review/requirements/REQ-BLE-0001-native-ble-and-security.md) получил статус **«Проведено ревью»**, `FND-0002` закрыт. Ограничен только дополнительный experimental legacy-1M BLE-compatible subset nRF24; native PTX/PRX/Enhanced-ShockBurst/rate/channel/ACK/pipe/FIFO/IRQ/RPD функции не сокращены. Native scan не объявлен connection sniffer/идентификатором/дальномером (`FND-0026`), vendor/emulation/attack claims имеют corpus, rights и трёхуровневые gates (`FND-0027`). Dedicated nRF52 connection sniffing и Bluetooth Mesh сохранены как optional deferred-release profiles, а не блокеры base board.

Оставшиеся срезы этапа 2 получили статус **«Проведено ревью»**: [`REQ-W24-0001`](../review/requirements/REQ-W24-0001-s3-wifi-espnow.md), [`REQ-SUB-0001`](../review/requirements/REQ-SUB-0001-cc1101-subghz.md), [`REQ-LORA-0001`](../review/requirements/REQ-LORA-0001-external-sx1262.md) и [`REQ-X-0001`](../review/requirements/REQ-X-0001-cross-session-performance.md). [`INV-0004`](../review/inventories/INV-0004-wishlist-self-review.md) покрывает 125/125 кандидатов и двенадцать leaf-dispositions из десяти source-extras. `REV-0002AD` закрывает этап 2 на requirement-level; exact hardware/HIL остаются доказательствами следующих этапов.


## Активный архитектурный gate

Этап 3 перезапущен по [`DEC-0027`](../review/decisions/DEC-0027-zero-based-capability-driven-architecture.md). [`FND-0033`](../review/findings/FND-0033-legacy-layout-assumptions-leaked-into-synthesis.md) зафиксировал методическую ошибку: прежняя работа оптимизировала legacy owners/buses/pins вместо независимого вывода архитектуры из хотелок.

Полные тексты прежних `DM/BUD/PIN/SC/LAY/CMP/ADR`, nRF-owner audit и `IMP-0021` сохранены в [`drafts/stage3-legacy-derived-2026-08-16/`](../../drafts/stage3-legacy-derived-2026-08-16/README.md). Они являются только источником идей и отрицательных результатов. Ни один старый owner, transport, GPIO или layout больше не является входным ограничением.

Новая активная цепочка начинается с [`CAP-0001`](../review/architecture/CAP-0001-zero-based-capability-input.md). Она заново покрывает 15/15 owner invariants, 9/9 wishlist groups и 13/13 `REQ-*` без pin/bus allocation и получила статус **«Проведено ревью»** в [`REV-0003J`](../review/reviews/REV-0003J-zero-based-stage3-restart.md). Следующий аппаратно-нейтральный артефакт [`CON-0001`](../review/architecture/CON-0001-hardware-neutral-concurrency-model.md) разделил обязательную параллельность, time-sharing, qualification-only пары и взаимоисключения, покрыл все 21 capability atom и отказовые сценарии и получил тот же статус в [`REV-0003K`](../review/reviews/REV-0003K-zero-based-concurrency-model.md). [`RES-0001`](../review/architecture/RES-0001-hardware-neutral-resource-demand.md) затем вывел compute/interface/timing/memory/power/safety/recovery demand и sizing equations без назначения MCU/GPIO; `REV-0003L` провёл его ревью. [`SRC-0001`](../review/architecture/SRC-0001-primary-hardware-resource-facts.md) отделил primary package/controller/peripheral facts от layout assumptions и прошёл `REV-0003M`.

Заранее фиксированы только явно принятые продуктовые границы: S3 native Wi-Fi/BLE, C5 Wi-Fi 2.4/5 GHz + IEEE 802.15.4 и dual-path IR, три полнофункциональных nRF24, onboard ES8311, внешние GNSS/LoRa/NFC profiles, hard STOP и открытые подписанные обновления. Владелец/controller/bridge трёх nRF24, MCU variants, transports, buses, pins, UI topology, memory, power и recovery полностью открыты.

[`SYN-0001`](../review/architecture/SYN-0001-zero-based-whole-device-candidates.md) с нуля вывел три цельных способа закрыть один resource graph: `SYN-2A` с packet-radio service на S3 и U214/GNSS на свободных C5 interfaces, `SYN-2B` с packet-radio service на C5 и `SYN-3A` с отдельным deterministic RP2354A A4 domain. Каждый размещает весь продукт, а не только nRF; split ownership сохранён как conditional response на измеренный single-bus/load fail. `REV-0003N/3O` провели ревью набора без выбора winner.

Exact [`PIN-0002`](../review/architecture/PIN-0002-zero-based-exact-pin-maps.md) прошёл `REV-0003O`: все 36 S3 и 21 C5 pins имеют role/free/reserved state, controller collisions отсутствуют, straps/recovery и корректная latch/IRQ logic явны. `FND-0034` исправил переполнение первой формулировки `SYN-2A` без потери scope: U214 и два GNSS UART используют свободные C5 interfaces. `SYN-2A` и `SYN-2B` сошлись без безопасного generic GPIO reserve; `SYN-3A` оставляет семь обычных C5 GPIO при 30/30 GPIO RP2354 и dedicated recovery.

[`BUD-0002`](../review/architecture/BUD-0002-zero-based-memory-traffic-budget.md), проверенный в [`REV-0003P`](../review/reviews/REV-0003P-zero-based-memory-traffic-budget.md), задаёт всем трём maps одинаковые memory, traffic, admission и HIL-пороги. S3 N16R2 проходит при измеренном usable-PSRAM floor 1792 KiB (`896 KiB` resident + `512 KiB` worst overlay + `384 KiB` reserve). Гарантированный профиль трёх nRF — одновременные независимые PRX по 200 kB/s payload на radio; единая 10 Mbit/s шина занята на 57.6%. Теоретический максимум 3×nRF плюс CC занял бы 79.5% ещё до software margin и явно не обещается как lossless. Провал принятого 600 kB/s/latency HIL автоматически переоткрывает split ownership.

Все candidates проходят paper memory и admitted-throughput arithmetic; у `SYN-2A` остаётся наибольший S3 contention risk, у `SYN-2B` — single-core C5 latency risk, у `SYN-3A` — дополнительный signed firmware target. Следующая активная работа — power/RF qualification и датированный сопоставимый cost snapshot. Целевые README не меняются до атомарной приёмки по `DEC-0026`.
