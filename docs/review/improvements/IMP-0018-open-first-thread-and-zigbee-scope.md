# IMP-0018 — open-first Thread и условный Zigbee на встроенном C5 radio

- Статус: **Принято — вариант A (`DEC-0020`)**
- Связано: `C-W5-09`, `FND-0025`, draft `REQ-W5-0001`
- Зоны: Main ordinary networking; Lab passive analysis; Controlled Zone active security tests
- Дата: 2026-08-16

## Контекст решения

ESP32-C5 уже содержит IEEE 802.15.4 radio. Legacy ошибочно ограничил его passive sniff/energy scan: официальный стек позволяет raw RX/TX, OpenThread и Zigbee roles без новой платы или RF BOM. Но Wi-Fi/BLE/802.15.4 делят один 2.4 GHz RF path, а официальный Zigbee SDK использует proprietary prebuilt core. Значит выбор затрагивает продуктовую пользу, открытость, flash/RAM profiles и coexistence — не только пункт меню.

## Варианты

### A — open-first expansion (рекомендация)

- Main: обычные commissioning/join/control/diagnostics только собственных или администрируемых сетей;
- OpenThread — обязательный открытый baseline для Thread roles, которые пройдут memory/coexistence/HIL;
- Zigbee ordinary full-stack — conditional optional backend: официальный binary допускается только при явных version/provenance/redistribution/SBOM/hash/update gates и никогда не требуется для сборки core product, raw 802.15.4 или Thread;
- Lab: passive raw 802.15.4 sniff, ED/CCA и bounded PCAP с privacy/redaction;
- Controlled Zone `AUTHORIZED_TARGET`: bounded raw injection/replay/commissioning-security tests exact authorized fixture;
- Controlled Zone `BOTH`: flood/interference/resilience only conducted/RF-shielded with no-leakage proof, hard timeout и STOP;
- hardware BOM не растёт; цена — firmware profiles, flash/RAM, coexistence, maintenance и HIL.

Плюс: максимальная законная полезность имеющегося silicon без закрытия проекта. Минус: optional Zigbee backend добавляет бинарную зависимость, которую придётся строго изолировать и сопровождать.

### B — только полностью открытый Thread + raw 802.15.4

Оставить OpenThread, raw RX/TX и те же трёхуровневые gates, но не включать full-stack Zigbee backend. Это проще для воспроизводимости и открытости, однако устройство не сможет быть обычным Zigbee coordinator/router/end device без будущего отдельного решения.

### C — legacy passive-only

Оставить лишь sniff/ED. Самый малый firmware scope, но сознательно теряет технически доступные ordinary networking и authorized test functions без экономии hardware BOM.

## Почему не предлагается второй 802.15.4 SoC сейчас

Отдельный radio/antenna улучшил бы одновременную Wi-Fi+Thread/Zigbee работу, но увеличивает BOM, площадь, RF-isolation и power. Это не zero-loss saving и не prerequisite для handheld node. Если HIL покажет неприемлемую потерю пакетов в принятом сценарии, dual-SoC станет отдельным архитектурным предложением с измеримой причиной.

## Рекомендация

Выбрать A: сохранить открытый OpenThread/core baseline, а Zigbee сделать отключаемым conditional adapter с отдельной бинарной provenance boundary. Так устройство не становится закрытым из-за одной optional функции и не теряет доступную владельцу пользу.

## Вопрос владельцу

Владелец принял вариант A. OpenThread становится открытым baseline; Zigbee остаётся optional conditional adapter с отдельной binary provenance boundary и не требуется для core product, raw IEEE 802.15.4 или Thread.
