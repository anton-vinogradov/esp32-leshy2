# REQ-IR-0001 — consumer IR receive, learn, remote and controlled-test contract

- Статус набора: **Проведено ревью capability; owner/backend открыт `DEC-0032`**
- Этап: 2 — возможности и исключения
- Источники кандидатов: `C-IR-01`–`C-IR-05`, пересечения `C-X-01`, `C-X-02`, `C-X-05`, `C-X-07`, `C-X-11`
- Обязательные решения: `DEC-0001`, `DEC-0002`, `DEC-0003`, `DEC-0005`, `DEC-0010`, `DEC-0013`, `DEC-0018`
- Находки: `FND-0001`, `FND-0017`, `FND-0018`
- Условные входы реализации: selected-owner timer/GPIO budget, transport if any, exact optical/electrical path, STOP, storage/licence и HIL

## Граница документа

Этот набор отделяет обычный пульт для собственных устройств от passive protocol analysis и disruptive multi-code actions. По `DEC-0018` сохраняются robust demodulated receive и отдельный carrier-learning path 30–60 kHz; прежний C5+TSOP38238+TSMP95000 остаётся reference profile, не target owner/BOM. `Universal remote` означает только corpus-proven device/protocol/carrier profiles; это не blanket compatibility со всем оптическим оборудованием. Demodulated raw envelope, measured carrier и carrier metadata из protocol/database/import/manual input — разные типы evidence.

## Матрица требований

| ID | Legacy-кандидат | Статус | Уровень | Требование и обязательный prerequisite |
|---|---|---|---|---|
| `REQ-IR-01` | все | `conditional` | Сквозной | Physical owner располагает локальными IR TX/RX timing resources и выдаёт typed records/events. UI/policy owner может совпадать либо использовать bounded transport; невозможный legacy dual-SPI transport не наследуется (`FND-0001`). |
| `REQ-IR-02` | `C-IR-01` | `conditional` | Основной | Recognized-protocol receive показывает protocol/address/command/repeat/toggle/confidence и одновременно хранит bounded raw envelope. Unknown/malformed/overflow остаётся raw/unsupported без ложного decode. |
| `REQ-IR-03` | `C-IR-01`, `C-IR-02` | `conditional` | Основной | По `DEC-0018` dual RX path сохраняет robust envelope и отдельно измеряет carrier 30–60 kHz. Learning record хранит carrier value и provenance: `measured`, `protocol`, `database`, `imported` или `manual`; fixed-demodulator output не подменяет `measured` (`FND-0018`). |
| `REQ-IR-04` | `C-IR-04` | `conditional` | Основной | Universal remote покрывает только versioned corpus-proven TV/media/projector/audio/HVAC profiles. Stateful HVAC хранит полный state/checksum/model, а не отправляет произвольный stateless key. Unsupported model видим и не получает generic success. |
| `REQ-IR-05` | `C-IR-02` | `conditional` | Основной own-device | Decoded command и own-tagged raw replay требуют явного press-to-send, выбранного target/profile и bounded repeats. Quick replay не стартует из boot/restore/import/playlist и прекращается при release/timeout/STOP. |
| `REQ-IR-06` | `C-IR-01` | `conditional` | Лаборатория | Passive analysis неизвестного/чужого remote signal декодирует timings/carrier evidence без автоматического replay; записи получают provenance/consent label и не превращаются в Main own-tag автоматически. |
| `REQ-IR-07` | `C-IR-02`, `C-IR-05` | `conditional` | Контролируемая зона, `AUTHORIZED_TARGET` | Unknown-provenance raw replay, imported service/factory code и single-target security test требуют fresh banner, explicit authorized target, per-action preview/hold and hard duration/repeat bounds. |
| `REQ-IR-08` | `C-IR-03`, `C-IR-05` | `conditional` | Контролируемая зона, `BOTH` | TV-B-Gone/multi-code power sweep, brute-force/de-Bruijn/service-code sweep и multi-target playlists работают только в изолированной line-of-sight зоне на явно авторизованных targets. Показываются code count, target set, max duration и progress; STOP прекращает следующий carrier burst. |
| `REQ-IR-09` | `C-IR-05` | `conditional` | Сквозной storage | Native typed record и documented `.ir` import/export сохраняют timings, carrier/provenance, protocol fields, repeats, target label, safety class, source/license and integrity. Parser bounded/fuzzed; import никогда не запускает TX и не становится trusted/own-tag сам. |
| `REQ-IR-10` | `C-IR-03`, `C-IR-04` | `conditional` | Сквозной licence | Bundled protocol/code/AC/TV-B-Gone records входят в release только с per-source provenance, compatible licence and reproducible generator. GPL/LGPL reference implementation или database не копируется молча; owner-imported records остаются отдельным content lifecycle. |
| `REQ-IR-11` | все TX | `conditional` | Сквозной hardware safety | Exact emitter/driver/current limit has hardware-off reset default, no back-power from dead rail, bounded peak/average current/duty/temperature and IEC 62471 assessment. `IR_TX` low/high-Z means optically off; generic D57/47 Ω is not qualification (`FND-0017`). |
| `REQ-IR-12` | все TX | `conditional` | Сквозной STOP/state | Owner-local dead-man, product STOP path and independent hardware-off gate terminate TX across link loss if present, stuck task, watchdog, reset and session exit. UI distinguishes commanded electrical TX from optically verified result; selected carrier/repeat profile remains visible. |
| `REQ-IR-13` | все | `acceptance` | Сквозной | HIL covers each claimed protocol/carrier/device class, unknown/raw overflow, ambient light, range/angle/window, self-blinding, long HVAC frame, repeats/toggles, storage full/corrupt, reset/brownout/link loss/STOP and exact electrical/optical safe state. |

## Acceptance corpus

- NEC/extended NEC, RC5/RC6, Sony/SIRC, Samsung, JVC, Panasonic/Kaseikyo and protocol-negative/malformed fixtures;
- at least two stateful HVAC families only if claimed, with full-state round-trip and checksum verification;
- 30/33/36/38/40/56 kHz fixtures for any accepted learned-carrier range;
- known out-of-band fixture, including 455 kHz, must return explicit unsupported/deferred unless separately qualified;
- native and imported raw records at timing/count/storage boundaries;
- owned single-device replay plus isolated authorized sweep fixtures for every Controlled-Zone route;
- min/nom/max battery/rail, temperature, enclosure/window, bright ambient and reflected-path measurements.

## Безопасность по умолчанию

- power/reset/update/link loss: emitter physically off;
- Main remote: one selected own target, finite repeats, press-to-send;
- Lab analysis: RX only;
- Controlled Zone entry banner does not arm TX; each tool additionally confirms target/action/environment;
- background job, external command, quick action, restored screen and imported playlist cannot bypass the same state machine.

## Стоимость без потери продукта

По `DEC-0018` dual path принят ради сохранения robust receive и measured-carrier learning одновременно; дополнительный receiver/GPIO/площадь не называются экономией. Exact emitter/driver may reduce part count only after comparing electrical/optical equivalence, placement cost and safe-state components; a missing pull-down, STOP path, TX indication or optical acceptance is not an economy. Удаление одного RX path требует нового owner decision.

## Первичные источники

- [ESP32-C5 datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [ESP-IDF RMT API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c5/api-reference/peripherals/rmt.html)
- [Vishay TSOP382/384 datasheet](https://www.vishay.com/docs/82491/tsop382.pdf)
- [Vishay TSMP95000 datasheet](https://www.vishay.com/docs/82907/tsmp95000.pdf)
- [Vishay TSAL6200 datasheet](https://www.vishay.com/docs/81010/tsal6200.pdf)
- [Vishay IEC 62471 eye-safety note](https://www.vishay.com/docs/81935/eyesafe.pdf)
- [Arduino-IRremote MIT reference](https://github.com/Arduino-IRremote/Arduino-IRremote)
- [IRremoteESP8266 protocol matrix](https://github.com/crankyoldgit/IRremoteESP8266/blob/master/SupportedProtocols.md)
- [IRremoteESP8266 LGPL-2.1 licence](https://github.com/crankyoldgit/IRremoteESP8266/blob/master/LICENSE.txt)
