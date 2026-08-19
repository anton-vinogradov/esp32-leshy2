# IMP-0005 — снять NFC ceiling готовым M5 Unit NFC U216

- Статус: **Принято владельцем: вариант A, `DEC-0017`**
- Связано: `OUT-06`, `C-NFC-*`, `FND-0015`, `FND-0016`, `REQ-NFC-0001`
- Зона: Main для ordinary tag read/write; Lab для passive credential analysis; Controlled Zone для emulation/recovery/clone/relay
- Первоначально открыто: 2026-08-15 как custom PN7160; переработано 2026-08-16 после появления U216

## Почему исходный PN7160-вариант больше не лучший первый ход

Custom PN7160 действительно снимает часть старого ceiling, но требует собственной платы, antenna/matching, NCI port и дополнительных `IRQ`/`VEN`; он не является прямой заменой четырёхпроводного M5 Grove Unit. После исходного аудита M5Stack выпустила готовый **Unit NFC U216** на ST25R3916:

- NFC-A/B, NFC-F/FeliCa и NFC-V/ISO15693 reader/writer;
- NFC-A/NFC-F card emulation и custom protocol mode;
- официальный MIT driver с ESP-IDF 5.x examples;
- MIFARE Classic/Ultralight/NTAG/DESFire, FeliCa и ISO15693 support matrix;
- готовые antenna, matching, корпус, 5 V Grove I²C и product certifications;
- официальный retail $7 и ≤40 mm, против $4.95 и <20 mm у RFID2 на дату аудита.

То есть +$2.05 к **опциональному аксессуару**, не к base-device BOM, заменяет разработку custom PN7160 board и расширяет возможности. Это не zero-cost saving, но сильное снижение total engineering/procurement cost при заметном capability gain.

## Рассмотренные варианты

### A — U216 как первый target backend; RFID2 compatibility и PN7160 fallback (рекомендация)

- Product target требует один квалифицированный U216 profile для HF NFC.
- RFID2 остаётся необязательным ограниченным compatibility profile для уже имеющегося/самого дешёвого reader, но не определяет ceiling продукта.
- Custom PN7160 не проектируется сейчас; возвращается только если U216 провалит lifecycle, firmware, timing или required-mode qualification.
- Base BOM не получает NFC IC/antenna; аппаратная цена — корректный 5 V-safe `PORT.A-NFC`, который требуется и для RFID2.

Плюсы: один основной готовый аксессуар, минимальная разработка, широкий protocol set, официальная MIT-библиотека. Минусы: U216 новый; exact `ST25R3916-AQWT` у ST имеет статус NRND, поэтому M5 SKU/revision/availability и возможная замена IC обязательны в manifest/qualification.

### B — U216 и RFID2 как два равноправных target backend

Пользователь может выбрать $4.95 reader-only либо $7 advanced Unit. Base BOM также не растёт, но firmware/UI/HIL, документация и support matrix дублируются. RFID2 не даёт функционально эквивалентную экономию: FeliCa/ISO15693/emulation/custom-mode теряются.

### C — custom PN7160 как основной advanced backend

Сохраняет active NXP silicon/NCI path и контролируемую ревизию платы, но требует отдельного connector/bridge из-за `IRQ`/`VEN`, antenna/RF design, PCB/BOM/assembly и ESP-IDF port. Этот вариант оправдан только если готовый U216 не проходит требуемые тесты или supply gate.

## Что ни один вариант не обещает автоматически

- universal secure-card clone либо secrets protected credential;
- one-unit NFC relay;
- hardnested/darkside с приемлемым временем и license-clean implementation;
- 125 kHz LF;
- EMV payment-terminal compliance;
- безопасную работу на текущем 3.3 V `J40/J41` artifact.

## Gate варианта A

1. exact U216 hardware/IC/firmware/library revisions и license/SBOM;
2. 5 V power, current, I²C timing/contention, removal/recovery и shared-bus HIL;
3. golden-card corpus для A/B/F/V и каждого заявленного R/W operation;
4. emulation fixtures с настоящими test readers без claims о protected credentials;
5. M5 availability/lifecycle и fallback trigger из-за NRND `AQWT`;
6. отдельные Controlled-Zone gates для recovery/emulation/clone/relay.

## Первичные источники

- [M5Stack Unit NFC U216 product documentation](https://docs.m5stack.com/en/unit/Unit_NFC)
- [M5Stack Unit NFC U216 official store](https://shop.m5stack.com/products/nfc-universal-unit-st25r3916)
- [M5Stack M5Unit-NFC MIT library](https://github.com/m5stack/M5Unit-NFC)
- [M5Stack RFID2 U031-B official store](https://shop.m5stack.com/products/rfid-unit-2-ws1850s)
- [STMicroelectronics ST25R3916 features and lifecycle](https://www.st.com/en/nfc/st25r3916.html)
- [NXP PN7160 product page](https://www.nxp.com/products/PN7160)
- [NXP PN7160/PN7161 datasheet](https://www.nxp.com/docs/en/data-sheet/PN7160_PN7161.pdf)

## Решение владельца

2026-08-16 принят вариант A: U216 — первый target HF-NFC backend, RFID2 — limited compatibility, custom PN7160 — conditional fallback. Канонический контракт — `DEC-0017`.
