# DEC-0017 — M5 Unit NFC U216 как первый HF-NFC backend

- Статус: **Принято владельцем**
- Дата: 2026-08-16
- Источник: `IMP-0005`, вариант A
- Закрывает на уровне требований: `FND-0016`
- Не закрывает electrical implementation: `FND-0015`
- Затрагивает: `REQ-NFC-0001`, `OUT-06`, accessory/power/I²C, storage/privacy и Controlled Zone

## Контекст

Legacy использовал внешний M5 RFID2/WS1850S как потолок NFC и затем предлагал custom PN7160 board для A/B/F/V и card emulation. Актуальный готовый M5 Unit NFC U216 за $7 уже предоставляет ST25R3916, antenna/matching, 5 V Grove I²C, A/B/F/V reader/writer, NFC-A/F emulation, custom protocol mode и MIT driver с ESP-IDF 5.x examples. RFID2 стоит $4.95, но потеря advanced modes не является zero-loss saving.

## Решение

1. Первый целевой external HF 13.56 MHz backend — **M5Stack Unit NFC U216** с exact-SKU/revision qualification.
2. RFID2 U031-B сохраняется как необязательный ограниченный compatibility profile для уже имеющегося либо минимального reader/writer use. Его UI/manifest показывает только доказанные операции; он не определяет ceiling продукта и не является равноправным target.
3. Custom PN7160 hardware сейчас не проектируется. Вариант возвращается только при документированном провале U216 по lifecycle/availability, driver/timing, required protocol/emulation или production HIL.
4. U216 остаётся внешним accessory: base board не получает NFC IC/antenna. Доплата $2.05 относительно RFID2 осознанно принимается ради capability и сокращения custom-hardware engineering; это не zero-cost saving.
5. Exact `ST25R3916-AQWT` текущей U216 revision имеет vendor status NRND. Stage-4 gate проверяет M5 SKU/revision/stock/lifecycle, exact IC, совместимость возможной новой revision и fallback trigger; имя `U216` не означает вечную неизменность внутренностей.
6. Target hardware предоставляет квалифицированный `PORT.A-NFC`: 5 V power, 3.3 V-safe I²C, bounded current, power/removal policy and recovery. Текущий `J40/J41=3.3 V` artifact не совместим и остаётся открытым `FND-0015` до stage-3/6 redesign.
7. Ordinary tag read/write относится к Main с privacy/destructive confirmation; passive credential analysis — к Lab; recovery, credential clone/write, emulation и relay — к Controlled Zone с `AUTHORIZED_TARGET` и отдельным per-tool arming.
8. U216 capability не означает universal secure-card clone, secrets extraction, one-unit relay или payment-terminal compliance. Relay требует два frontend; LF 125 kHz требует отдельное hardware; hardnested/darkside требуют отдельные license/runtime/corpus proof.
9. Официальная MIT-библиотека является предпочтительным upstream reference, но интеграция фиксирует version/commit, SBOM/licence, bounded parser/timing behavior и on-target tests; upstream example не выдаётся за готовый product driver.

## Fallback gate

Custom PN7160 либо другой advanced accessory рассматривается, если U216 недоступен с приемлемым lifecycle, exact revision нельзя воспроизводимо идентифицировать, аппаратный/driver timing не проходит на shared I²C или обязательные A/B/F/V/emulation fixtures не проходят. Причина и потерянные функции публикуются; RFID2 fallback не маркируется advanced A/B/F/V backend.

## Первичные источники

- [M5Stack Unit NFC U216 documentation](https://docs.m5stack.com/en/unit/Unit_NFC)
- [M5Stack Unit NFC U216 official store](https://shop.m5stack.com/products/nfc-universal-unit-st25r3916)
- [M5Stack M5Unit-NFC MIT library](https://github.com/m5stack/M5Unit-NFC)
- [M5Stack RFID2 U031-B](https://docs.m5stack.com/en/unit/rfid2)
- [STMicroelectronics ST25R3916 product/lifecycle page](https://www.st.com/en/nfc/st25r3916.html)
- [NXP PN7160 product page](https://www.nxp.com/products/PN7160)
