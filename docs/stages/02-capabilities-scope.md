# Этап 2 — возможности и исключения

- Статус: **В работе**
- Пререквизит: этап 1 — проведено ревью
- Основной выход: проверенная матрица `REQ-*`

## Входы

- `DEC-0002`: all-in-one профиль, возрастающая серьёзность security-функций, обязательная «Лаборатория» и акт о ненападении;
- `DEC-0001`: принято целевое владение C5 для 3× nRF24 и IR, но реализуемость ещё не подтверждена из-за `FND-0001`;
- `DEC-0005`: каждую функцию и архитектурный пререквизит требуется проверить на функционально эквивалентную реализацию меньшей полной стоимости;
- `DEC-0006`: бортового GNSS нет; GPS-функции предоставляются подключаемым M5Stack Unit GPS v1.1 через отдельный 5-вольтовый UART `PORT.C`;
- `DEC-0008`: бортового LoRa нет; U214 — первый модуль `EXT-RF14`, другие carrier опциональны, один активный backend;
- `DEC-0009`: бортовой ES8311, существующий RX mux и два default-to-analog selector — целевая mono audio-архитектура; реализация ещё требует pin/electrical/firmware proof;
- `DEC-0010`: три уровня функциональности; `LAB-P` по умолчанию находится в обычной «Лаборатории», `LAB-I`/`LAB-D` — во вложенной «Контролируемой зоне» с banner при каждом входе;
- `DEC-0012`: `IMP-0010` остаётся открытым, а выбор STOP/UI/audio pin-map переносится на этап 3 после сводного pin/GPIO/resource budget;
- `DEC-0013`: штатные S3/C5 updates используют owner-controlled signatures, validation и rollback без обязательного hardware lockdown;
- `DEC-0014`: NMEA — обязательный GNSS baseline, advanced CASIC assistance/integrity условны per-revision proof и не требуют третьего GNSS;
- `DEC-0015`: Si4732 SSB/CW использует открытый bounded loader и owner-imported patch без bundled blob; synchronous AM остаётся deferred;
- `DEC-0016`: SA518 — preferred conditional dual-band analog-voice target, SA868S — честный UHF-only fallback до qualification;
- `DEC-0017`: внешний M5 Unit NFC U216 — первый HF NFC backend, RFID2 — limited compatibility, custom PN7160 — fallback после qualification failure;
- `DEC-0018`: consumer IR использует на C5 два RX path — robust TSOP38238 и carrier-learning TSMP95000 30–60 kHz; TSAL6200 — первый условный TX candidate;
- legacy capability tree обоих репозиториев — только источник кандидатов, не требований;
- datasheet-ограничения и проверяемые safety/legal-гейты для каждого кандидата.

## Порядок работы

1. Собрать без потерь все legacy-кандидаты и устранить дубли между репозиториями.
2. Для каждого кандидата определить пользовательскую задачу, владельца реализации и аппаратный пререквизит.
3. Отнести security-кандидаты только в «Лабораторию», выбрать уровень 2/3 и для уровня 3 указать `ISOLATED_ONLY`, `AUTHORIZED_TARGET` либо `BOTH`.
4. Проверить реализуемость на выбранном кремнии; неподтверждённые функции не обещать.
5. Зафиксировать safety/legal-гейты, состояние по умолчанию и проверяемый критерий приёмки.
6. Повторно проверить каждый legacy-потолок по `DEC-0004`, включая замену старого компонента и изолированный лабораторный сценарий.
7. Отдельно отметить `include`, `conditional`, `defer` или `exclude-proven` с обоснованием.
8. Для включаемой функции зафиксировать стоимостный драйвер и запретить «экономию», ухудшающую её критерий приёмки.

## Принятое сквозное решение

`IMP-0001` принят и преобразован в `DEC-0003`: все передатчики стартуют выключенными, Lab-инструменты — разоружёнными, первая передача использует консервативный профиль, а максимальная мощность доступна только после явного выбора. Это обязательный вход для всех передающих возможностей.

`DEC-0010` добавляет независимую UX/safety-границу: действительно опасные функции находятся во вложенной «Контролируемой зоне». Каждый вход требует нового banner и hold-to-confirm, но не вооружает инструмент; `REV-0001A` подтвердило распространение решения.

## Инвентаризация legacy

Полная дедуплицированная инвентаризация зафиксирована в `INV-0001` и прошла ревью `REV-0002A`. Ни один кандидат этим не получил статус требования.

Инвентаризация и первый стоимостный проход вскрыли три расхождения:

- `FND-0002`: legacy не согласован, S3 или C5 владеет BLE;
- `FND-0003`: firmware-кандидаты требуют цифрового RX/TX audio-path через MCU, которого нет в legacy hardware;
- `FND-0004`: legacy-текст объявляет GPS внешним, но актуальный legacy tsCircuit всё ещё содержит бортовой SAM-M8Q и не содержит обещанного `J_GPS`; закрыто решением `DEC-0006`, scope-подшаг прошёл `REV-0002B`.

## Аудит старых исключений

По решению владельца проекта `DEC-0004` все девять групп `OUT-*` проходят новый аудит `AUD-0001`. Уже найдены четыре реалистичных обхода (`IMP-0002`–`IMP-0005`); `IMP-0005` принят как `DEC-0017`, остальные пока не меняют scope.

Сравнение audio-вариантов завершено и прошло `REV-0002E`: current analog, native ADC/sigma-delta S3, ES8311, ES8388, TLV320AIC3204 и внешний M5Stack M144 проверены вместе с GPIO, стоимостью и правовым режимом. Владелец принял `IMP-0009` как `DEC-0009`: ES8311 mono codec с существующим RX mux и двумя аппаратными default-to-analog selector.

Повторное ревью распространения `REV-0002F` подтвердило: архитектурная неопределённость `FND-0003` снята, а связанные capability теперь `conditional`, но существующий hardware-артефакт ещё не реализует codec. Полное закрытие находки требует pin/electrical/firmware/HIL proof следующих этапов.

Первый проход базового `System/UI/storage` выявил новое пересечение: исходный `IMP-0006` занимает все свободные `U13.P10..P17` matrix+STOP+touch, а `DEC-0009` рассчитывает на тот же пул для трёх audio-control (`FND-0006`). Одновременно схема показала, что `SW_STOP` сейчас является только входом `U14` и не имеет независимого пути к MCU reset, PTT или RF power gates (`FND-0007`).

`⚠️ IMP-0010` предлагает объединённое исправление: аппаратный STOP с аварийной безопасной перезагрузкой, девять остальных кнопок в `3×3` matrix, touch на `U13`, а audio-control — на оставшейся линии `U13` и двух линиях `U12`, освобождённых удалением onboard LoRa. По `DEC-0012` выбор варианта отложен до сводного pin/GPIO/resource budget этапа 3. Предложение и находки остаются открытыми, но не блокируют ревью корректно условных System/UI capability-требований этапа 2.

Prerequisite audit `REV-0002H` дополнительно обнаружил `FND-0008`: legacy привязывает C5 OTA к заблокированному `SPI3`, обещает hot-plug на одновременно названных non-hot-swap Grove-портах, смешивает разные M5 electrical profiles и не задаёт trust/rollback update chain. `REQ-SYS-0001` исправляет эти границы, сохраняет все одиннадцать групп `C-SYS-*` и выносит BadUSB только в Controlled Zone.

Владелец принял `IMP-0011` как открытый `A-open` в `DEC-0013`: штатные S3/C5 update paths требуют owner-authorized signatures и rollback, но ключи, offline build/signing и developer firmware остаются у владельца; необратимый hardware lockdown не принят. Распространение прошло `REV-0002I`, `FND-0008` закрыт на requirement-level, а System/UI/storage capability-срез получил статус **«Проведено ревью»**.

Следующий GNSS/navigation prerequisite audit прошёл `REV-0002J`. Он выявил `FND-0009`: legacy требует SparkFun u-blox, AssistNow и UBX flags, тогда как оба принятых M5-профиля используют AT6668. Официальный CASIC protocol предоставляет backend-native assistance/ephemeris input и receiver-reported jamming/spoofing messages, поэтому функции не исключены автоматически. Владелец принял `IMP-0012/A` как `DEC-0014`: NMEA остаётся обязательным baseline, advanced CASIC profile условен per-revision proof, а unsupported/unknown никогда не становится false-safe. Распространение прошло `REV-0002K`, `FND-0009` закрыт на requirement-level, и `REQ-GNSS-0001` получил статус **«Проведено ревью»**.

Si4732 prerequisite audit прошёл `REV-0002L`. Документированный FM/RDS и ordinary AM baseline отделён от conditional SSB/CW, sweep-RSSI bandscope, WAV и decoder proof. `FND-0010` зафиксировал, что MIT driver не включает внешний volatile SSB patch, а synchronous-AM не подтверждена тем же Skyworks/PU2CLR API. Владелец принял `IMP-0013/A` как `DEC-0015`: открытый bounded loader входит в target, конкретный blob импортируется локально и не наследует доверие application signature, synchronous-AM остаётся deferred. Распространение прошло `REV-0002M`, `FND-0010` закрыт на requirement-level, а `REQ-RX-0001` получил статус **«Проведено ревью»**.

Analog voice/SA868 prerequisite audit прошёл `REV-0002N`. `FND-0011` исправил доказанный high-power/floating-control default: PTT теперь имеет RX pull-up, PD — power-down pull-down, H/L физически ограничен low до stage-3 safe control. `FND-0012` отделил UHF variant, 400–470 AT range, binary scan/raw RSSI и conditional host tone scan. `FND-0013` оставляет VOX `defer` без mic capture; `FND-0014` удаляет ложное обещание licence-free PMR446 через firmware preset. Владелец принял `IMP-0014/A` как `DEC-0016`: SA518 dual-band — preferred conditional target, SA868S — UHF-only fallback до price/AVL/RF proof, а падение peak 2 W-class→1 W принято как trade-off. Распространение прошло `REV-0002O`, `FND-0012` закрыт на requirement-level, `REQ-VHF-0001` получил статус **«Проведено ревью»**.

NFC/RFID prerequisite audit прошёл `REV-0002P`. Новый готовый M5 Unit NFC U216/ST25R3916 за $7 снимает A/B/F/V, ISO15693/FeliCa и limited emulation ceiling без custom PN7160 board; официальный MIT driver уже имеет ESP-IDF 5.x examples. `FND-0015` фиксирует, что текущие `J40/J41` дают 3.3 V вместо официальных 5 V обоих M5 NFC Unit. `FND-0016` отделяет frontend primitives от universal clone, two-endpoint relay, key recovery, LF и payment compliance. Владелец принял `IMP-0005/A` как `DEC-0017`: U216 — первый target, RFID2 — limited compatibility, custom PN7160 — fallback только после qualification failure; дополнительные $2.05 против RFID2 приняты как цена сохранения advanced scope, а не base-BOM cost. Распространение прошло `REV-0002Q`, `FND-0016` закрыт на requirement-level, `REQ-NFC-0001` получил статус **«Проведено ревью»**. Exact U216 revision/lifecycle, 5-вольтовый `PORT.A-NFC`, driver/SBOM и HIL остаются implementation gates; `FND-0015` открыт.

Consumer IR prerequisite audit прошёл `REV-0002R`. `FND-0017` снял ложную `FAB-READY` пометку IR artifact и добавил Q58 base-emitter pull-down, но C5 ownership, exact emitter/driver/current, STOP, TX-state и optical HIL остаются открыты. `FND-0018` доказал, что fixed `TSOP38238` не измеряет carrier. Владелец принял `IMP-0015/A` как `DEC-0018`: C5 получает robust `TSOP38238` и отдельный `TSMP95000` learning path 30–60 kHz, а `TSAL6200` остаётся первым условным emitter candidate. Более дешёвые B/C имеют явную потерю функции и не применяются без нового решения. `REQ-IR-0001` разделяет own remote/replay в Main, passive analysis в Lab, unknown replay в Controlled Zone `AUTHORIZED_TARGET`, а TV-B-Gone/brute-force/multi-code sweep — в Controlled Zone `BOTH`. Распространение прошло `REV-0002S`, `FND-0018` закрыт на requirement-level, `REQ-IR-0001` получил статус **«Проведено ревью»**; C5 pins/transport, exact TX/RX BOM, STOP, optics, licences и HIL остаются implementation gates.

3×nRF24 prerequisite audit прошёл `REV-0002T`. `FND-0019` показывает, что current `FAB-READY` claim был ложным: SPI/CE/CS/IRQ всё ещё принадлежат S3, modules являются generic 2×4 placeholders, а `TXDET_NRF1..3` не имеют RF detector source. Маркировка исправлена, общий CE получил 100 kΩ pull-down, но transport/pins/module/STOP/TX-live/RF proof открыты; после dual-path IR старый C5 pin budget дополнительно устарел. `FND-0020` отделяет binary RPD threshold от RSSI/dBm/bearing и внешний constant-carrier source от отсутствующего VSWR meter; silicon имеет RF_CH 0–125, не 128. `FND-0021` разносит passive ESB/MouseJack discovery, sensitive KeySniffer capture, active injection, address brute-force и interference tests по Lab/Controlled Zone; jam/carrier/sweep доступны только `BOTH` в conducted/RF-shielded setup. GPL reference code не выдан за MIT reuse. Draft `REQ-N24-0001` остаётся **«На ревью»** до выбора `IMP-0016` между честным calibrated RPD hit-rate hunt и новым real-power RF hardware. **⚠️ Предложение `IMP-0017`** направляет ordinary BLE на native ESP backend, оставляя nRF24 лишь limited compatibility, но ждёт отдельного BLE-owner review.

При этом исправлено отдельное доказанное несоответствие `FND-0005`: tsCircuit ошибочно суммировал Si4732 pin 2 (`GPO3/DCLK`) вместо pin 16 (`ROUT/DOUT`). Исправление проведено ревью, но не закрывает цифровой audio blocker.

## Аудит стоимости

По `DEC-0005` начат `AUD-0002`. Исходный схемный кандидат `IMP-0006` предлагал удалить третий PCA9555 и занять `U13` matrix+STOP+touch, но после `DEC-0009` эта pin-map признана конфликтующей. Переработанный `IMP-0010` сохраняет идею matrix, выносит STOP в независимую hardware safety-chain и перераспределяет audio-control; предложение не принято и по `DEC-0012` рассматривается только после сводного pin budget и UI/safety proof этапа 3.

Принятое внешнее GNSS уменьшает base BOM, но полная дельта считается вместе с 5-вольтовым UART connector/protection и внешним Unit. Перенос функции во внешний аксессуар здесь не скрытая экономия, а явно принятое владельцем ограничение scope.

`IMP-0007` выявил, что готовый U214 функционально близок к legacy SX1262 и добавляет GNSS, но его официальное окно `868–923 MHz` уже legacy E22 `850–930 MHz`. Владелец уточнил через `DEC-0008`, что полный legacy-диапазон не требуется: целевой baseline — общепринятые профили 868/915 в пределах hardware window и региональных правил.

Модульный `EXT-RF14` сохраняется, U214 принят первым LoRa+GNSS backend, а другие carrier добавляются только по отдельному решению. E22 carrier не обязательна; blanket-совместимость со всеми Cardputer Caps или UART LoRaWAN Units не обещается. Исправленный scope-подшаг прошёл `REV-0002D`.

## Следующий артефакт

Продолжение `AUD-0001` и декомпозиция следующей capability-группы в `include` / `conditional` / `defer` / `exclude-proven` с проверяемыми гейтами и стоимостным драйвером.
