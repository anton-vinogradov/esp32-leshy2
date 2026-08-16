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
- [DEC-0001: IR остаётся C5; nRF24-часть переоткрыта](decisions/DEC-0001-c5-owns-nrf24-ir.md)
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
- [DEC-0016: conditional SA518 dual-band voice target с SA868S fallback](decisions/DEC-0016-conditional-sa518-dual-band-voice.md)
- [DEC-0017: M5 Unit NFC U216 — первый HF NFC target](decisions/DEC-0017-u216-hf-nfc-backend.md)
- [DEC-0018: двухтрактный consumer IR на ESP32-C5](decisions/DEC-0018-dual-path-consumer-ir.md)
- [DEC-0019: калиброванный трёхантенный RPD-hunt без ложных dBm/угла/VSWR](decisions/DEC-0019-calibrated-rpd-three-antenna-hunt.md)
- [DEC-0020: open-first Thread и optional conditional Zigbee](decisions/DEC-0020-open-first-thread-conditional-zigbee.md)
- [DEC-0021: S3 — единственный baseline native-BLE owner](decisions/DEC-0021-s3-native-ble-owner.md)
- [REQ-SYS-0001: System/UI/storage platform contract — проведено ревью](requirements/REQ-SYS-0001-system-ui-storage.md)
- [REQ-GNSS-0001: navigation/time/integrity contract — проведено ревью](requirements/REQ-GNSS-0001-navigation-integrity.md)
- [REQ-RX-0001: Si4732 receiver/scan/record/decode contract — проведено ревью](requirements/REQ-RX-0001-si4732-receiver.md)
- [REQ-VHF-0001: analog voice/modem/relay contract — проведено ревью](requirements/REQ-VHF-0001-analog-voice-modem.md)
- [REQ-NFC-0001: HF NFC/RFID contract — проведено ревью](requirements/REQ-NFC-0001-hf-nfc-rfid.md)
- [REQ-IR-0001: consumer IR contract — проведено ревью](requirements/REQ-IR-0001-consumer-infrared.md)
- [REQ-N24-0001: 3×nRF24 full-function contract — capability проведено ревью, ownership переоткрыто](requirements/REQ-N24-0001-three-nrf24-raw-2g4.md)
- [REQ-W5-0001: C5 Wi-Fi/IEEE 802.15.4 contract — проведено ревью](requirements/REQ-W5-0001-c5-wifi-ieee802154.md)
- [REQ-BLE-0001: native BLE contract — проведено ревью](requirements/REQ-BLE-0001-native-ble-and-security.md)
- [FND-0001: конфликт единственного GP-SPI C5](findings/FND-0001-c5-single-gp-spi.md)
- [FND-0002: владелец BLE расходился между legacy-репозиториями — закрыто DEC-0021](findings/FND-0002-ble-owner-conflict.md)
- [FND-0003: audio-архитектура принята, implementation proof ожидается](findings/FND-0003-missing-mcu-audio-path.md)
- [FND-0004: бортовой и внешний GNSS расходятся — закрыто DEC-0006](findings/FND-0004-gnss-scope-conflict.md)
- [FND-0005: неверная распиновка audio Si4732 — закрыто исправлением](findings/FND-0005-si4732-audio-pin-map.md)
- [FND-0006: конфликт `U13` между UI matrix и audio-control](findings/FND-0006-u13-ui-audio-pin-collision.md)
- [FND-0007: STOP сейчас является только входом I²C-экспандера](findings/FND-0007-stop-is-only-i2c-input.md)
- [FND-0008: legacy System/UI смешивал функции с реализацией — закрыто](findings/FND-0008-legacy-system-ui-contract-conflicts.md)
- [FND-0009: legacy u-blox GNSS расходится с принятым AT6668 — закрыто DEC-0014](findings/FND-0009-legacy-ublox-vs-at6668.md)
- [FND-0010: SSB patch и synchronous-AM имеют разные proof/license состояния — закрыто DEC-0015](findings/FND-0010-si4732-ssb-patch-and-sync-am.md)
- [FND-0011: SA868 floating TX controls и high-power hardware default — исправлено консервативно](findings/FND-0011-sa868-unsafe-tx-defaults.md)
- [FND-0012: SA868 API/диапазон не доказывает весь legacy scope — закрыто DEC-0016](findings/FND-0012-sa868-api-and-band-overclaims.md)
- [FND-0013: VOX не имеет microphone-capture path](findings/FND-0013-sa868-vox-has-no-microphone-capture.md)
- [FND-0014: firmware preset не создаёт licence-exempt PMR446 equipment — закрыто на уровне требований](findings/FND-0014-pmr446-preset-is-not-compliance.md)
- [FND-0015: Grove NFC Unit требуют 5 V, текущие порты дают 3.3 V](findings/FND-0015-nfc-unit-power-profile-mismatch.md)
- [FND-0016: NFC frontend не доказывает universal emulation/relay/key recovery — закрыто DEC-0017](findings/FND-0016-nfc-emulation-relay-and-attack-overclaims.md)
- [FND-0017: IR TX artifact не fail-safe/qualified — частично исправлено](findings/FND-0017-ir-tx-artifact-not-safe-or-qualified.md)
- [FND-0018: fixed 38 kHz demodulator не учит carrier — закрыто DEC-0018](findings/FND-0018-ir-fixed-demodulator-cannot-learn-carrier.md)
- [FND-0019: 3×nRF24 artifact не C5-owned/fail-safe/qualified — частично исправлено](findings/FND-0019-nrf24-artifact-not-c5-safe-or-qualified.md)
- [FND-0020: nRF24 RPD не является RSSI/VSWR — закрыто DEC-0019](findings/FND-0020-nrf24-rpd-is-not-rssi-or-vswr.md)
- [FND-0021: nRF24 security/BLE/licence overclaims](findings/FND-0021-nrf24-security-ble-and-license-overclaims.md)
- [FND-0022: C5 module/ANT1/ANT2/RF artifact — частично исправлено](findings/FND-0022-c5-module-antenna-and-radio-artifact-not-qualified.md)
- [FND-0023: C5 public Wi-Fi API и patched binary overclaims](findings/FND-0023-c5-wifi-public-api-and-patched-blob-overclaims.md)
- [FND-0024: 5 GHz DFS/country/PMF/privacy gates](findings/FND-0024-c5-dfs-country-privacy-and-pmf-gates.md)
- [FND-0025: passive-only 802.15.4 ceiling — закрыто DEC-0020](findings/FND-0025-c5-802154-passive-only-ceiling-and-coexistence.md)
- [FND-0026: native BLE scan не является connection sniff, stable identity или дальномером](findings/FND-0026-native-ble-is-not-connection-sniff-identity-or-distance.md)
- [FND-0027: BLE protocol/emulation/attack claims требуют corpus, rights и security gates](findings/FND-0027-ble-protocol-emulation-attack-and-license-overclaims.md)
- [FND-0028: владелец 3×nRF24 переоткрыт full-function/resource audit](findings/FND-0028-nrf24-owner-reopened-by-full-function-resource-audit.md)
- [IMP-0001: безопасный TX-дефолт вместо максимума — принято](improvements/IMP-0001-safe-tx-defaults.md)
- [⚠️ IMP-0002: SDIO как обход GP-SPI блокера C5 — предложение](improvements/IMP-0002-c5-sdio-link.md)
- [⚠️ IMP-0003: переоткрыть EAPOL/PMKID capture — предложение](improvements/IMP-0003-wifi-handshake-capture.md)
- [⚠️ IMP-0004: dedicated BLE connection sniffer — предложение](improvements/IMP-0004-dedicated-ble-sniffer.md)
- [IMP-0005: снять NFC ceiling готовым M5 Unit NFC U216 — принято](improvements/IMP-0005-pn7160-nfc-expansion.md)
- [⚠️ IMP-0006: исходная UI-matrix конфликтует с audio — переработано в IMP-0010](improvements/IMP-0006-ui-key-matrix.md)
- [IMP-0007: внешний Cardputer LoRa+GNSS Cap — основной профиль](improvements/IMP-0007-cardputer-lora-gnss-cap.md)
- [IMP-0008: универсальный внешний LoRa-профиль — транспорт принят, E22 опционален](improvements/IMP-0008-modular-lora-expansion.md)
- [IMP-0009: бортовой mono codec ES8311 с hardware bypass — принято](improvements/IMP-0009-onboard-mono-audio-codec.md)
- [⚠️ IMP-0010: аппаратный STOP и удаление `U14` без audio-конфликта — предложение](improvements/IMP-0010-hardware-stop-and-expander-consolidation.md)
- [IMP-0011: подписанная цепочка обновлений S3 и C5 — принято как A-open](improvements/IMP-0011-signed-update-chain.md)
- [IMP-0012: backend-native assistance и индикатор целостности GNSS — принято](improvements/IMP-0012-casic-gnss-advanced-profile.md)
- [IMP-0013: открытый lifecycle SSB-патча Si4732 — принято](improvements/IMP-0013-reproducible-ssb-patch-lifecycle.md)
- [IMP-0014: conditional migration на dual-band SA518 — принято](improvements/IMP-0014-dual-band-sa518-voice-backend.md)
- [IMP-0015: dual-path consumer IR learning — принято](improvements/IMP-0015-dual-path-consumer-ir-learning.md)
- [IMP-0016: честный calibrated three-antenna RPD hunt — принят вариант A](improvements/IMP-0016-calibrated-three-antenna-2g4-hunt.md)
- [IMP-0017: native BLE + ограниченный BLE-compatible subset nRF24 — принято](improvements/IMP-0017-native-ble-plus-nrf24-compatibility.md)
- [IMP-0018: open-first Thread + conditional Zigbee — принят вариант A](improvements/IMP-0018-open-first-thread-and-zigbee-scope.md)
- [IMP-0019: S3 как единственный baseline native-BLE owner — принято](improvements/IMP-0019-s3-primary-native-ble-owner.md)
- [⚠️ IMP-0020: ordinary Bluetooth Mesh — требуется отдельное решение](improvements/IMP-0020-ordinary-ble-mesh-scope.md)
- [⚠️ IMP-0021: S3 владеет тремя полнофункциональными nRF24 — предложение](improvements/IMP-0021-s3-owns-three-full-function-nrf24.md)
- [INV-0001: дедуплицированная инвентаризация legacy-возможностей](inventories/INV-0001-legacy-capabilities.md)
- [AUD-0001: повторный аудит legacy-исключений](audits/AUD-0001-legacy-exclusions.md)
- [AUD-0002: снижение стоимости без потерь](audits/AUD-0002-zero-loss-cost.md)
- [AUD-0003: сравнительный аудит владельца трёх полнофункциональных nRF24](audits/AUD-0003-three-nrf24-owner-placement.md)
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
- [REV-0002N: ревью пререквизитов analog voice/SA868](reviews/REV-0002N-sa868-prerequisites.md)
- [REV-0002O: ревью analog voice и распространения SA518/A](reviews/REV-0002O-voice-backend-decision-propagation.md)
- [REV-0002P: ревью пререквизитов NFC/RFID](reviews/REV-0002P-nfc-prerequisites.md)
- [REV-0002Q: ревью NFC/RFID и распространения U216/A](reviews/REV-0002Q-nfc-decision-propagation.md)
- [REV-0002R: ревью пререквизитов consumer IR](reviews/REV-0002R-ir-prerequisites.md)
- [REV-0002S: финальное ревью и распространение consumer IR решения](reviews/REV-0002S-ir-decision-propagation.md)
- [REV-0002T: ревью пререквизитов 3×nRF24](reviews/REV-0002T-nrf24-prerequisites.md)
- [REV-0002U: финальное ревью и распространение решения 3×nRF24](reviews/REV-0002U-nrf24-decision-propagation.md)
- [REV-0002V: ревью пререквизитов C5 Wi-Fi/IEEE 802.15.4](reviews/REV-0002V-c5-wifi-802154-prerequisites.md)
- [REV-0002W: финальное ревью и распространение C5 Wi-Fi/802.15.4 решения](reviews/REV-0002W-c5-wifi-802154-decision-propagation.md)
- [REV-0002X: ревью пререквизитов native Bluetooth LE](reviews/REV-0002X-ble-prerequisites.md)
- [REV-0002Y: финальное ревью и распространение S3 native-BLE ownership](reviews/REV-0002Y-s3-native-ble-decision-propagation.md)
- [REV-0002Z: ревью пререквизитов повторного выбора владельца 3×nRF24](reviews/REV-0002Z-nrf24-owner-placement-prerequisites.md)

## Статусы

`Не начато` → `Требуется решение` → `В работе` → `На ревью` → `Проведено ревью`.

Дополнительные состояния: `Заблокировано`, `Требуется повторное ревью`.

## Реестр улучшений

Предложения `IMP-*` добавляются в `improvements/`. Отсутствие предложений означает только то, что обход ещё не найден или не доказан, а не то, что legacy-ограничение принято.
