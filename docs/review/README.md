# Журнал ревью Leshy2

Этот каталог — единственная точка учёта стадий, решений, находок и доказательств ревью для hardware- и firmware-репозиториев.

## Правила

1. Каждый этап начинается только после проверки его пререквизитов.
2. Требования, решения и находки получают устойчивые идентификаторы: `REQ-*`, `DEC-*`, `FND-*`.
3. Итоговый статус этапа — **«Проведено ревью»** — выставляется только после закрытия находок и воспроизводимой проверки выходных артефактов.
4. Изменение проверенного входа переводит зависимые этапы в **«Требуется повторное ревью»**.
5. Явное несоответствие исправляется и перепроверяется. Неочевидное или потенциально «лишнее» сначала выносится на решение владельца проекта.
6. Значимое улучшение оформляется как предложение и становится решением только после согласия владельца проекта.
7. Ограничения из legacy-документов не наследуются как неизменные. Если найден реалистичный обход, он оформляется как `IMP-*`: старое ограничение, новая возможность или доказательство, цена, риск и затрагиваемые требования. Владелец проекта информируется до изменения scope; после согласия предложение превращается в `DEC-*`.
8. Этап подтверждается автоматически, если его проверки пройдены и по нему нет открытых вопросов, предложений или находок. При наличии хотя бы одного такого пункта статус «Проведено ревью» требует решения владельца проекта.
9. Каждый legacy-пункт `OUT-*` обязан пройти повторную техническую и правовую проверку. Ограничение конкретного старого компонента не считается ограничением продукта: рассматриваются разумная замена, дополнительный модуль и изолированный/проводной лабораторный сценарий. Окончательное исключение получает статус `exclude-proven` только с актуальными первичными источниками, указанной юрисдикцией и оценкой цены обхода.
10. Стоимость сокращается только по правилу `DEC-0005`: экономия должна сохранять принятые функции и измеримые характеристики, safety/legal-гейты, надёжность, автономность, ремонтопригодность и тестируемость. Более дешёвая, но неэквивалентная конфигурация считается отдельным вариантом, а не экономией без потерь.
11. Каждое открытое предложение в журнале и сообщениях владельцу явно помечается `⚠️ Предложение`; принятые или отклонённые предложения предупреждением больше не маркируются.
12. Вопрос о решении всегда содержит необходимый контекст в том же сообщении: текущее состояние, причину вопроса, существенные варианты и их последствия, рекомендацию и один явно сформулированный вопрос. Независимые решения разделяются и по возможности принимаются последовательно.
13. Корневые README обоих репозиториев описывают целевой готовый продукт только через принятые контракты и всегда отделяют target от текущей реализации.
14. Текущие стадии, доказательства реализации, открытые находки и `⚠️ Предложение` публикуются в `docs/status/current-state.*.md`, а не смешиваются с образом готового продукта.
15. При распространении принятого решения проверяются hardware/firmware, target/current-state и EN/RU пары; открытое условие нельзя превращать в безусловное обещание.

## Реестр

- [Целевой hardware-продукт](../../README.ru.md)
- [Текущее состояние hardware-проработки](../status/current-state.ru.md)
- [Целевой firmware-продукт](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md)
- [Текущее состояние firmware-проработки](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/status/current-state.ru.md)
- [Baseline](baseline.md)
- [Этапы и статусы](stages.md)
- [DEC-0001: целевое владение C5 для nRF24 и IR; реализация не доказана](decisions/DEC-0001-c5-owns-nrf24-ir.md)
- [DEC-0002: all-in-one, Лаборатория и акт о ненападении](decisions/DEC-0002-project-vision.md)
- [DEC-0003: безопасный TX-дефолт](decisions/DEC-0003-safe-tx-defaults.md)
- [DEC-0004: обязательный пересмотр legacy-исключений](decisions/DEC-0004-reconsider-legacy-exclusions.md)
- [DEC-0005: снижение стоимости без потери продукта](decisions/DEC-0005-zero-loss-cost.md)
- [DEC-0006: внешний GNSS через M5Stack Unit GPS v1.1](decisions/DEC-0006-external-m5-gnss.md)
- [DEC-0007: оба внешних LoRa-варианта — изменено DEC-0008](decisions/DEC-0007-dual-external-lora-profiles.md)
- [DEC-0008: U214 для общепринятых LoRa-частот; E22 не обязателен](decisions/DEC-0008-u214-common-lora-bands.md)
- [DEC-0009: бортовой ES8311 с аппаратным analog bypass](decisions/DEC-0009-onboard-es8311-audio.md)
- [DEC-0010: три уровня функциональности и вложенная контролируемая зона](decisions/DEC-0010-three-functional-levels.md)
- [DEC-0011: целевой README отдельно от текущего состояния](decisions/DEC-0011-target-readme-current-state.md)
- [DEC-0012: решение по IMP-0010 после сводного pin budget](decisions/DEC-0012-defer-imp-0010-to-pin-budget.md)
- [DEC-0013: открытая owner-controlled цепочка подписанных обновлений](decisions/DEC-0013-owner-controlled-signed-updates.md)
- [DEC-0014: NMEA baseline и квалифицируемый advanced CASIC profile](decisions/DEC-0014-casic-gnss-profile.md)
- [DEC-0015: открытый owner-imported SSB patch loader Si4732](decisions/DEC-0015-open-si4732-ssb-patch-loader.md)
- [REQ-SYS-0001: System/UI/storage platform contract — проведено ревью](requirements/REQ-SYS-0001-system-ui-storage.md)
- [REQ-GNSS-0001: navigation/time/integrity contract — проведено ревью](requirements/REQ-GNSS-0001-navigation-integrity.md)
- [REQ-RX-0001: Si4732 receiver/scan/record/decode contract — проведено ревью](requirements/REQ-RX-0001-si4732-receiver.md)
- [FND-0001: конфликт единственного GP-SPI C5](findings/FND-0001-c5-single-gp-spi.md)
- [FND-0002: владелец BLE расходится между legacy-репозиториями](findings/FND-0002-ble-owner-conflict.md)
- [FND-0003: audio-архитектура принята, implementation proof ожидается](findings/FND-0003-missing-mcu-audio-path.md)
- [FND-0004: бортовой и внешний GNSS расходятся — закрыто DEC-0006](findings/FND-0004-gnss-scope-conflict.md)
- [FND-0005: неверная распиновка audio Si4732 — закрыто исправлением](findings/FND-0005-si4732-audio-pin-map.md)
- [FND-0006: конфликт `U13` между UI matrix и audio-control](findings/FND-0006-u13-ui-audio-pin-collision.md)
- [FND-0007: STOP сейчас является только входом I²C-экспандера](findings/FND-0007-stop-is-only-i2c-input.md)
- [FND-0008: legacy System/UI смешивал функции с реализацией — закрыто](findings/FND-0008-legacy-system-ui-contract-conflicts.md)
- [FND-0009: legacy u-blox GNSS расходится с принятым AT6668 — закрыто DEC-0014](findings/FND-0009-legacy-ublox-vs-at6668.md)
- [FND-0010: SSB patch и synchronous-AM имеют разные proof/license состояния — закрыто DEC-0015](findings/FND-0010-si4732-ssb-patch-and-sync-am.md)
- [IMP-0001: безопасный TX-дефолт вместо максимума — принято](improvements/IMP-0001-safe-tx-defaults.md)
- [⚠️ IMP-0002: SDIO как обход GP-SPI блокера C5 — предложение](improvements/IMP-0002-c5-sdio-link.md)
- [⚠️ IMP-0003: переоткрыть EAPOL/PMKID capture — предложение](improvements/IMP-0003-wifi-handshake-capture.md)
- [⚠️ IMP-0004: dedicated BLE connection sniffer — предложение](improvements/IMP-0004-dedicated-ble-sniffer.md)
- [⚠️ IMP-0005: заменить NFC ceiling через PN7160 — предложение](improvements/IMP-0005-pn7160-nfc-expansion.md)
- [⚠️ IMP-0006: исходная UI-matrix конфликтует с audio — переработано в IMP-0010](improvements/IMP-0006-ui-key-matrix.md)
- [IMP-0007: внешний Cardputer LoRa+GNSS Cap — основной профиль](improvements/IMP-0007-cardputer-lora-gnss-cap.md)
- [IMP-0008: универсальный внешний LoRa-профиль — транспорт принят, E22 опционален](improvements/IMP-0008-modular-lora-expansion.md)
- [IMP-0009: бортовой mono codec ES8311 с hardware bypass — принято](improvements/IMP-0009-onboard-mono-audio-codec.md)
- [⚠️ IMP-0010: аппаратный STOP и удаление `U14` без audio-конфликта — предложение](improvements/IMP-0010-hardware-stop-and-expander-consolidation.md)
- [IMP-0011: подписанная цепочка обновлений S3 и C5 — принято как A-open](improvements/IMP-0011-signed-update-chain.md)
- [IMP-0012: backend-native assistance и индикатор целостности GNSS — принято](improvements/IMP-0012-casic-gnss-advanced-profile.md)
- [IMP-0013: открытый lifecycle SSB-патча Si4732 — принято](improvements/IMP-0013-reproducible-ssb-patch-lifecycle.md)
- [INV-0001: дедуплицированная инвентаризация legacy-возможностей](inventories/INV-0001-legacy-capabilities.md)
- [AUD-0001: повторный аудит legacy-исключений](audits/AUD-0001-legacy-exclusions.md)
- [AUD-0002: снижение стоимости без потерь](audits/AUD-0002-zero-loss-cost.md)
- [Контракт владения](../contracts/ownership.md)
- [REV-0000: ревью этапа 0](reviews/REV-0000-stage-0.md)
- [REV-0000A: ревью целевых и текущих стартовых страниц](reviews/REV-0000A-document-entrypoints.md)
- [REV-0001: ревью этапа 1](reviews/REV-0001-stage-1.md)
- [REV-0001A: повторное ревью трёхуровневой границы](reviews/REV-0001A-three-functional-levels.md)
- [REV-0002A: ревью инвентаризации возможностей](reviews/REV-0002A-capability-inventory.md)
- [REV-0002B: ревью scope внешнего GNSS](reviews/REV-0002B-external-gnss.md)
- [REV-0002C: историческое ревью прежнего LoRa scope](reviews/REV-0002C-modular-lora-scope.md)
- [REV-0002D: повторное ревью U214 и общепринятых LoRa-частот](reviews/REV-0002D-u214-common-bands.md)
- [REV-0002E: ревью вариантов цифрового audio-path](reviews/REV-0002E-audio-options.md)
- [REV-0002F: ревью распространения решения ES8311](reviews/REV-0002F-es8311-decision-propagation.md)
- [REV-0002G: ревью переноса IMP-0010 на сводный pin budget](reviews/REV-0002G-defer-imp-0010-to-pin-budget.md)
- [REV-0002H: ревью пререквизитов System/UI/storage](reviews/REV-0002H-system-ui-prerequisites.md)
- [REV-0002I: ревью System/UI/storage и распространения A-open](reviews/REV-0002I-system-ui-decision-propagation.md)
- [REV-0002J: ревью пререквизитов GNSS/navigation](reviews/REV-0002J-gnss-prerequisites.md)
- [REV-0002K: ревью GNSS/navigation и распространения варианта A](reviews/REV-0002K-gnss-decision-propagation.md)
- [REV-0002L: ревью пререквизитов Si4732 receiver](reviews/REV-0002L-si4732-prerequisites.md)
- [REV-0002M: ревью Si4732 receiver и распространения варианта A](reviews/REV-0002M-si4732-decision-propagation.md)

## Статусы

`Не начато` → `Требуется решение` → `В работе` → `На ревью` → `Проведено ревью`.

Дополнительные состояния: `Заблокировано`, `Требуется повторное ревью`.

## Реестр улучшений

Предложения `IMP-*` добавляются в `improvements/`. Отсутствие предложений означает только то, что обход ещё не найден или не доказан, а не то, что legacy-ограничение принято.
