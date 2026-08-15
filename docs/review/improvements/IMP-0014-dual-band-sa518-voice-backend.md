# IMP-0014 — заменить UHF-only SA868S на квалифицируемый dual-band SA518

- Статус: **⚠️ Предложение; требуется решение владельца**
- Этап решения: 2 — capability scope; component/BOM/RF proof — этапы 3–6 и 10
- Связано: `FND-0012`, `FND-0013`, `FND-0014`, `REQ-VHF-0001`, `OUT-07`, `DEC-0005`
- Обнаружено: 2026-08-16

## Контекст

Текущий SA868S — один UHF-вариант 400–480 MHz, причём опубликованный AT command range заканчивается на 470 MHz. Он сохраняет 2 W-class high-power option, но не покрывает VHF/2 m, а legacy прямо признаёт потерю обычных VHF APRS scenarios.

В 2026 году NiceRF выпустил SA518: один SMD-модуль одновременно поддерживает VHF 136–174 и UHF 400–470 MHz, voice и короткую transparent data, 0.5/1 W, CTCSS/CDCSS, RSSI и EEPROM. Это снимает старый single-band hardware ceiling одним backend, но не является drop-in replacement.

## Вариант A — рекомендуемый: условно перевести target на SA518, SA868S оставить fallback до qualification

Stage 2 принимает dual-band voice-radio result, но stage 4 обязан подтвердить exact SA518 revision, цену/AVL, RF/antenna path, footprint и protocol до снятия SA868S fallback. Если gate не проходит, target возвращается на явно UHF-only SA868S без ложного dual-band обещания.

Плюсы:

- один модуль покрывает VHF и UHF без второй рации/антенного разъёма;
- открывает 2 m voice и технический путь к регионально разрешённым VHF AFSK1200/APRS/AX.25 profiles;
- добавляет короткий transparent-data mode, который можно квалифицировать отдельно;
- 1 W peak и 0.5 W low уменьшают PA/power/thermal stress относительно 2 W-class SA868S.

Цена и потери:

- footprint/pinout несовместимы; модуль 39.5×24.0 mm против примерно 35.6×19.0 mm SA868S — около 40% больше площади;
- UHF peak падает примерно с 31–33 dBm до 29–31 dBm; это потеря максимальной RF-мощности, а не zero-loss cost optimization;
- продукт новый, LCSC/JLC stock и tier pricing пока не доказаны;
- dual-band antenna/filter/layout и harmonic/spurious compliance требуют нового RF proof;
- transparent data не называется AX.25/APRS без interoperability test;
- стандартная SA518 не решает host VOX; кастомная VOX-версия по datasheet теряет data transmission.

## Вариант B — сохранить SA868S UHF baseline

Оставить меньший зрелый 2 W-class UHF модуль. VHF/2 m и common VHF APRS не входят в onboard target; их можно рассмотреть через будущий внешний voice-radio expansion.

Преимущества: минимум аппаратных изменений, сохраняется UHF peak, текущий footprint/stock известнее. Минусы: all-in-one остаётся UHF-only, а старый VHF потолок не обходится.

## Вариант C — SA868S onboard плюс второй VHF backend

Сохраняет 2 W-class UHF и добавляет VHF без компромисса peak power, но требует второй module, RF isolation/antenna path, питания, площади и TX arbitration. Это самый дорогой вариант и не соответствует текущей цели снижения полной стоимости.

## Что ни один вариант не решает автоматически

- внешний SMA не становится licence-exempt PMR446 equipment (`FND-0014`);
- independent hardware STOP/PTT kill остаётся обязательным (`FND-0007`);
- VOX требует mic-capture/специальной variant (`FND-0013`);
- full-duplex repeater и DMR/C4FM/dPMR не появляются у analog half-duplex backend;
- каждый TX profile требует region/licence/callsign/power/duty/timeout gates.

## Рекомендация

Принять A как **conditional target with fallback**, а не немедленно объявлять SA518 выбранным BOM-компонентом. Это позволяет обойти старый UHF ceiling и сохранить один radio backend, но честно удерживает SA868S до цены, availability и RF/HIL proof. Потеря 2 W peak должна быть осознанно принята владельцем как обмен на dual-band, а не названа экономией без потерь.

## Первичные источники

- [NiceRF SA868S datasheet rev. 1.7](https://www.nicerf.com/upload/20250730/550a4fb20f0ddcdaf5c265201a056c73.pdf)
- [NiceRF SA518 dual-band product page](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html)
- [NiceRF SA518 datasheet rev. 1.1](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
