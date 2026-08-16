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
| 2. Возможности и исключения | В работе |
| 3–10 | Не начато |

Каноническая таблица стадий — [`docs/review/stages.md`](../review/stages.md).

## Принятые целевые решения, уже отражённые на продуктовой странице

- all-in-one профиль, акт о ненападении и три уровня функциональности (`DEC-0002`, `DEC-0010`);
- консервативные TX-дефолты и явный выбор максимальной мощности (`DEC-0003`);
- оптимизация полной стоимости без потери продукта (`DEC-0005`);
- внешний M5 GNSS и внешний U214 LoRa+GNSS (`DEC-0006`, `DEC-0008`);
- NMEA baseline и условный per-revision advanced CASIC profile без дополнительного GNSS (`DEC-0014`);
- FM/RDS/ordinary AM baseline и открытый owner-imported SSB/CW patch loader без bundled blob (`DEC-0015`);
- условный dual-band analog-voice target на SA518 с честным UHF-only fallback на SA868S (`DEC-0016`);
- внешний M5 Unit NFC U216 как первый HF NFC backend, RFID2 как limited compatibility и custom PN7160 как qualification fallback (`DEC-0017`);
- двухтрактный consumer IR на C5 с robust RX TSOP38238 и TSMP95000 для измерения несущей 30–60 kHz (`DEC-0018`);
- бортовая mono audio-архитектура ES8311 с fail-safe analog bypass (`DEC-0009`);
- целевое владение C5 для 3×nRF24 и IR (`DEC-0001`) без заявления о готовом межпроцессорном транспорте.
- owner-controlled подписанные обновления S3/C5 с rollback и открытым developer lifecycle (`DEC-0013`) без включения необратимого hardware lockdown.

## Открытое инженерное состояние

- `FND-0001`: единственный GP-SPI C5 не может одновременно выполнять legacy-роли nRF-master и S3↔C5-slave.
- `FND-0002`: владелец BLE расходится между legacy-репозиториями.
- `FND-0003`: audio-архитектура принята, но pin/electrical/firmware/HIL proof ещё не выполнен.
- `FND-0006`: исходная матрица кнопок и audio-control конфликтуют на `U13.P10..P17`.
- `FND-0007`: текущий STOP — только вход I²C-экспандера, а не независимый аппаратный TX-kill.
- `FND-0011`: текущему SA868 добавлены PTT receive-default, PD power-down-default и физический low-power H/L; независимый STOP и управляемый high-power path ещё требуют stage-3 proof.
- `FND-0013`: VOX не имеет microphone-capture path и явно отложен до общего audio/pin budget.
- `FND-0015`: оба документированных M5 NFC Unit требуют PORT.A power profile 5 V, а текущие `J40/J41` дают 3.3 V; электрическое исправление ждёт общего port/power design.
- `FND-0017`: legacy IR source всё ещё использует S3 ownership, generic unqualified emitter/current path и не имеет доказанных STOP/TX-state/optical behavior. Ложная `FAB-READY` пометка снята, Q58 получил reset-safe pull-down.
- `FND-0019`: три generic nRF24 PA/LNA placeholder всё ещё используют S3 bus, exact modules/STOP/TX detectors отсутствуют, а post-dual-IR C5 resource budget не доказан. Ложные `FAB-READY` пометки сняты, общий CE получил reset-safe pull-down.
- `FND-0020`: nRF24 RPD является binary threshold, а не RSSI/dBm/bearing; radio может дать test carrier, но не измерить VSWR.
- `FND-0021`: ESB/MouseJack/KeySniffer/BLE-compatible/interference claims требуют раздельных capability/security/licence/HIL gates.
- Существующие tsCircuit/KiCad остаются legacy-артефактами реализации до ревью производящих стадий и регенерации.

## Текущая работа ревью

System/UI/storage capability-срез завершён статусом **«Проведено ревью»** в `REV-0002I`.

GNSS/navigation срез [`REQ-GNSS-0001`](../review/requirements/REQ-GNSS-0001-navigation-integrity.md) получил статус **«Проведено ревью»** в `REV-0002K`. Владелец принял `IMP-0012/A` как [`DEC-0014`](../review/decisions/DEC-0014-casic-gnss-profile.md): NMEA — обязательный baseline квалифицированного профиля, а assistance и receiver-reported jamming/spoofing условны proof точной revision/firmware. Unsupported/timeout/parser error означают `unknown`, не «угроз нет»; host heuristics отделяются от статуса receiver.

`FND-0009` закрыт на requirement-level. UART/power hardware, parser, assistance source, поддержка advanced messages конкретными Unit/U214, RF self-desense и HIL ещё не реализованы и проверяются на последующих этапах.

Si4732-срез [`REQ-RX-0001`](../review/requirements/REQ-RX-0001-si4732-receiver.md) получил статус **«Проведено ревью»** в `REV-0002M`. Владелец принял `IMP-0013/A` как [`DEC-0015`](../review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md): открытый bounded loader входит в target, SSB blob импортируется локально и имеет отдельные integrity/provenance состояния, а synchronous-AM остаётся deferred до отдельного proof. `FND-0010` закрыт на requirement-level; RF/frontend, patch rights/compatibility, loader, audio/storage/decoder и coexistence HIL ещё не реализованы.

Analog-voice срез [`REQ-VHF-0001`](../review/requirements/REQ-VHF-0001-analog-voice-modem.md) получил статус **«Проведено ревью»** в `REV-0002O`. Владелец принял `IMP-0014/A` как [`DEC-0016`](../review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md): SA518 — предпочтительный half-duplex analog-FM target 136–174/400–470 MHz, а текущий SA868S остаётся явно UHF-only fallback до проверки цены, поставки, PCB/power и conducted RF. Компромисс 2 W-class→1 W принят и не считается экономией без потерь. `FND-0012` закрыт на requirement-level; microphone capture/VOX (`FND-0013`), независимый STOP, high-power control, точное железо, protocol, RF, audio и HIL proof остаются для следующих этапов.

NFC/RFID-срез [`REQ-NFC-0001`](../review/requirements/REQ-NFC-0001-hf-nfc-rfid.md) получил статус **«Проведено ревью»** в `REV-0002Q`. Владелец принял `IMP-0005/A` как [`DEC-0017`](../review/decisions/DEC-0017-u216-hf-nfc-backend.md): внешний M5 Unit NFC U216 за $7 — первый HF NFC target, RFID2 за $4.95 — limited compatibility, а custom PN7160 — fallback только после провала qualification. Дельта аксессуара $2.05 принята ради A/B/F/V, ISO15693/FeliCa, limited emulation и custom-mode scope и не влияет на base BOM. `FND-0016` закрыт на requirement-level явными трёхуровневыми гейтами и отказом от overclaim universal clone, relay с одним frontend, key recovery, LF 125 kHz и payment compliance. Exact IC U216 имеет статус NRND; proof точной revision/lifecycle, 5-вольтовый `PORT.A-NFC` (`FND-0015`), driver/SBOM, protocol и HIL остаются открытой реализационной работой.

Consumer-IR срез [`REQ-IR-0001`](../review/requirements/REQ-IR-0001-consumer-infrared.md) получил статус **«Проведено ревью»** в `REV-0002S`. Владелец принял `IMP-0015/A` как [`DEC-0018`](../review/decisions/DEC-0018-dual-path-consumer-ir.md): C5 использует TSOP38238 для robust demodulated 38 kHz приёма и TSMP95000 для обучения с измерением несущей 30–60 kHz, занимая оба RX RMT channels C5; TSAL6200 — первый условный кандидат 940 nm emitter. Более дешёвые single-learning/fixed-38 варианты теряют принятую функцию и не могут подменить решение молча. `FND-0018` закрыт на requirement-level; автоматическое обучение 455 kHz/out-of-band остаётся deferred. Own remote/replay находится в Main, passive analysis — в Lab, unknown replay — в Controlled Zone `AUTHORIZED_TARGET`, а TV-B-Gone/brute-force/multi-code sweep — в Controlled Zone `BOTH`. `FND-0017`, C5 pins/transport, exact BOM, STOP, optics, licences и HIL остаются открытой реализационной работой.

Prerequisite audit 3×nRF24 получил статус **«Проведено ревью»** в `REV-0002T`; draft [`REQ-N24-0001`](../review/requirements/REQ-N24-0001-three-nrf24-raw-2g4.md) остаётся **«На ревью»**. Текущее железо всё ещё проводит три generic module placeholder через S3, не имеет реальных `TXDET_NRF1..3` detector circuits и не доказывает post-dual-IR C5 pin budget. Source-маркировка и reset-default общего CE исправлены, но `FND-0019` остаётся implementation blocker. RPD теперь задан как calibrated binary hit-rate statistics, никогда не RSSI/dBm/bearing; constant-carrier mode — только source для внешнего прибора, не VSWR meter (`FND-0020`). Passive ESB/MouseJack discovery, sensitive KeySniffer capture, active injection, address brute-force и interference tests получили разные gates; interference/carrier sweep допустимы только conducted/RF-shielded `BOTH`, а GPL references не считаются MIT code (`FND-0021`). **⚠️ Предложение [`IMP-0016`](../review/improvements/IMP-0016-calibrated-three-antenna-2g4-hunt.md)** рекомендует сравнительный RPD hit-rate baseline без нового BOM; альтернатива — добавить real-power RF hardware. **⚠️ Предложение [`IMP-0017`](../review/improvements/IMP-0017-native-ble-plus-nrf24-compatibility.md)** отложено до BLE-owner review.

## Отложенный архитектурный gate

[`IMP-0010`](../review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) остаётся открытым, но [`DEC-0012`](../review/decisions/DEC-0012-defer-imp-0010-to-pin-budget.md) переносит выбор A/B на этап 3. Новый ответ владельца не запрашивается, пока сводный pin/GPIO/resource budget не учтёт оба MCU, экспандеры, fixed-function pins, межпроцессорный transport, audio, UI/touch, внешние модули и действительно освободившиеся линии onboard GNSS/LoRa.

`FND-0006` и `FND-0007` остаются открытыми. Перенос не выбирает `U14`/матрицу 3×3 и не доказывает аппаратный STOP.
