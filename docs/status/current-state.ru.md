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
- `FND-0016`: capability NFC frontend сам по себе не доказывает universal credential emulation, two-ended relay, key recovery, LF 125 kHz или payment compliance.
- Существующие tsCircuit/KiCad остаются legacy-артефактами реализации до ревью производящих стадий и регенерации.

## Текущая работа ревью

System/UI/storage capability-срез завершён статусом **«Проведено ревью»** в `REV-0002I`.

GNSS/navigation срез [`REQ-GNSS-0001`](../review/requirements/REQ-GNSS-0001-navigation-integrity.md) получил статус **«Проведено ревью»** в `REV-0002K`. Владелец принял `IMP-0012/A` как [`DEC-0014`](../review/decisions/DEC-0014-casic-gnss-profile.md): NMEA — обязательный baseline квалифицированного профиля, а assistance и receiver-reported jamming/spoofing условны proof точной revision/firmware. Unsupported/timeout/parser error означают `unknown`, не «угроз нет»; host heuristics отделяются от статуса receiver.

`FND-0009` закрыт на requirement-level. UART/power hardware, parser, assistance source, поддержка advanced messages конкретными Unit/U214, RF self-desense и HIL ещё не реализованы и проверяются на последующих этапах.

Si4732-срез [`REQ-RX-0001`](../review/requirements/REQ-RX-0001-si4732-receiver.md) получил статус **«Проведено ревью»** в `REV-0002M`. Владелец принял `IMP-0013/A` как [`DEC-0015`](../review/decisions/DEC-0015-open-si4732-ssb-patch-loader.md): открытый bounded loader входит в target, SSB blob импортируется локально и имеет отдельные integrity/provenance состояния, а synchronous-AM остаётся deferred до отдельного proof. `FND-0010` закрыт на requirement-level; RF/frontend, patch rights/compatibility, loader, audio/storage/decoder и coexistence HIL ещё не реализованы.

Analog-voice срез [`REQ-VHF-0001`](../review/requirements/REQ-VHF-0001-analog-voice-modem.md) получил статус **«Проведено ревью»** в `REV-0002O`. Владелец принял `IMP-0014/A` как [`DEC-0016`](../review/decisions/DEC-0016-conditional-sa518-dual-band-voice.md): SA518 — предпочтительный half-duplex analog-FM target 136–174/400–470 MHz, а текущий SA868S остаётся явно UHF-only fallback до проверки цены, поставки, PCB/power и conducted RF. Компромисс 2 W-class→1 W принят и не считается экономией без потерь. `FND-0012` закрыт на requirement-level; microphone capture/VOX (`FND-0013`), независимый STOP, high-power control, точное железо, protocol, RF, audio и HIL proof остаются для следующих этапов.

NFC/RFID prerequisite audit получил статус **«Проведено ревью»** в `REV-0002P`; [`REQ-NFC-0001`](../review/requirements/REQ-NFC-0001-hf-nfc-rfid.md) остаётся **«На ревью»**. Актуальные источники дали более сильный путь, чем прежняя custom-PN7160-first идея: внешний M5 Unit NFC U216 за $7 даёт A/B/F/V, ISO15693/FeliCa, NFC-A/F emulation, custom mode и MIT-библиотеку с ESP-IDF 5.x, тогда как RFID2 за $4.95 экономит только $2.05 и теряет advanced modes. **⚠️ Предложение [`IMP-0005`](../review/improvements/IMP-0005-pn7160-nfc-expansion.md)** рекомендует U216 как первый target, RFID2 как limited compatibility, а custom PN7160 — только fallback. Exact IC U216 имеет статус NRND, напряжение текущего порта неверно (`FND-0015`), а universal clone/relay/key-recovery claims запрещены (`FND-0016`).

## Отложенный архитектурный gate

[`IMP-0010`](../review/improvements/IMP-0010-hardware-stop-and-expander-consolidation.md) остаётся открытым, но [`DEC-0012`](../review/decisions/DEC-0012-defer-imp-0010-to-pin-budget.md) переносит выбор A/B на этап 3. Новый ответ владельца не запрашивается, пока сводный pin/GPIO/resource budget не учтёт оба MCU, экспандеры, fixed-function pins, межпроцессорный transport, audio, UI/touch, внешние модули и действительно освободившиеся линии onboard GNSS/LoRa.

`FND-0006` и `FND-0007` остаются открытыми. Перенос не выбирает `U14`/матрицу 3×3 и не доказывает аппаратный STOP.
