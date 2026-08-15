# IMP-0012 — backend-native assistance и индикатор целостности GNSS

- Статус: **Принято владельцем как вариант A; см. `DEC-0014`**
- Этап решения: 2 — capability scope; implementation proof — этапы 4, 7, 8 и 10
- Связано: `FND-0009`, `REQ-GNSS-0001`, `C-GPS-01`, `C-GPS-03`, `C-GPS-04`, `DEC-0006`, `DEC-0008`
- Обнаружено: 2026-08-16

## Контекст

Принятые M5Stack Unit GPS v1.1 и U214 используют AT6668, тогда как legacy обещает u-blox AssistNow и UBX-флаги `jamInd`/`spoofDetState`. Перенести эти механизмы буквально нельзя.

Одновременно официальный CASIC protocol, на который ссылается M5Stack, содержит собственные input records assistance и receiver-reported jamming/spoofing status. Поэтому старый пользовательский результат можно попытаться сохранить без дополнительного GNSS-модуля, но только после доказательства на конкретных M5 revision/firmware.

## Вариант A — рекомендуемый: базовый NMEA + квалифицируемый advanced CASIC profile

1. Базовая навигация, треки, вейпоинты, геозоны и безопасная синхронизация времени работают через NMEA и не зависят от proprietary service.
2. Advanced profile включается только для явно квалифицированных сочетаний product/revision/firmware и может:
   - подавать проверенные position/time/ephemeris assistance records с source, acquisition time и expiry;
   - читать `TXT-JSM`, `MON-JSM` либо `MON-SEC` и показывать именно receiver-reported `unknown / normal / suspected / strong` состояния.
3. При отсутствии ответа или неподдерживаемой firmware UI показывает **«не поддерживается/неизвестно»**, а не «помех нет».
4. Host sanity checks по age/fix/satellite/DOP/time/velocity могут повышать недоверие к fix, но всегда маркируются отдельно как heuristic и не выдаются за доказанное обнаружение spoofing.
5. Assistance package может поступать по Wi-Fi либо с SD, проходит schema/size/source/expiry validation и не становится обязательной cloud-зависимостью. Координаты не отправляются наружу без отдельного явного согласия.
6. M5 Module GPS v2.1 не добавляется в baseline: он остаётся будущим отдельно квалифицируемым аксессуаром, если появится требование к PPS/внешней антенне/другой механике.

Преимущества: сохраняет защитный readout и шанс ускоренного старта без дополнительного BOM, u-blox и vendor-only cloud. Цена: отдельный CASIC parser/driver, fixture, test vectors и HIL для каждой ревизии; наличие advanced функций пока не обещается без proof.

## Вариант B — только NMEA baseline

Сохранить позицию, навигацию, логи и время; `C-GPS-03` и receiver-reported часть `C-GPS-04` исключить. Это дешевле по firmware/test effort, но теряет две полезные возможности, которые текущий чип, вероятно, способен предоставить.

## Вариант C — обязать дополнительный u-blox/high-integrity backend

Вернуть отдельный модуль с заранее доказанными assistance и integrity telemetry. Это даёт наиболее определённый API, но увеличивает перечень аксессуаров, стоимость, connector/mechanical work и acceptance matrix. Существующие M5 GPS v1.1/U214 всё равно придётся поддерживать как уже принятые профили.

## Сравнение стоимости и риска

| Вариант | Дополнительный BOM | Firmware/HIL | Результат |
|---|---:|---:|---|
| A — CASIC profile | нет | средний | сохраняет максимум функций, честно conditional |
| B — NMEA only | нет | минимальный | утрата assistance и receiver integrity status |
| C — третий backend | модуль, interface/mechanics | высокий | наиболее определённые advanced-функции ценой расширения scope |

## Критерии proof для варианта A

- сохранить product/revision/firmware identity и raw UART trace для Unit GPS v1.1 и U214;
- malformed/oversized NMEA, CASTXT и CASBIN frames не повреждают state и не блокируют parser;
- запросы advanced messages дают документированный ответ либо однозначный unsupported timeout;
- recorded normal/interference/spoofing vectors проверяют mapping UI; реальный RF-тест проводится только в экранированной/изолированной среде;
- отсутствие/обрыв GNSS, stale fix и `unknown` не отображаются как trusted/no-interference;
- просроченные, wrong-constellation и повреждённые assistance records отклоняются;
- cold/warm/hot start сравниваются с/без assistance; маркетинговое ускорение не обещается без измерения;
- LoRa TX U214 проверяется на GNSS self-desense отдельно по `IMP-0007`.

## Решение владельца

Владелец принял **вариант A**: дешёвый NMEA baseline сохраняется, а assistance и индикатор помех/подмены становятся advanced CASIC-функциями только после проверки конкретной прошивки каждого M5-профиля. Третий GNSS не добавляется; недоказанная функция отображается как unsupported/unknown, а не как работающий детектор. Канонический контракт — `DEC-0014`.

## Первичные источники

- [M5Stack Unit GPS v1.1](https://docs.m5stack.com/en/unit/Unit-GPS%20v1.1)
- [M5Stack U214](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [CASIC protocol: assistance, ephemeris input and jamming/spoofing status](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1173/CASIC_Multi-mode_Satellite_Navigation_Receiver_Protocol_Specification.pdf)
- [M5Stack Module GPS v2.1](https://docs.m5stack.com/en/module/Module_GPS_v2.1)
