# FND-0009 — legacy GNSS-функции привязаны к u-blox, а принятые M5-профили используют AT6668

- Статус: **Открыто до решения `IMP-0012`**
- Серьёзность: нельзя переносить `C-GPS-01`, `C-GPS-03` и `C-GPS-04` как готовый firmware-контракт
- Затрагивает: `DEC-0006`, `DEC-0008`, `C-GPS-*`, `C-X-06`, `C-X-07`, hardware/firmware и приёмочные испытания
- Обнаружено: 2026-08-16

## Несоответствие

Legacy `FW-CAP §6` называет группу «GPS (u-blox)» и требует:

- конфигурировать модуль через SparkFun u-blox GNSS library;
- загружать u-blox AssistNow offline assistance;
- показывать помехи и spoofing через UBX-MON-HW `jamInd` и NAV-STATUS `spoofDetState`.

После `DEC-0006` и `DEC-0008` оба принятых GNSS-профиля — M5Stack Unit GPS v1.1 `U032-V11` и GNSS в U214 — построены на `ATGM336H-6N@AT6668`. Их штатный поток — UART `115200 8N1`, NMEA 0183 4.1; UBX-команды и AssistNow к ним неприменимы. Простая замена имени библиотеки оставила бы требования технически ложными.

## Найденный обход старого ограничения

Связанный M5Stack официальный CASIC protocol specification документирует backend-native механизмы:

- обычные NMEA PVT/quality/time сообщения для базовой навигации;
- `TXT-JSM`, `MON-JSM` и `MON-SEC` с receiver-reported уровнями jamming и spoofing;
- `AID-INI` для начальной позиции/времени/частотной ошибки;
- входные `MSG-*EPH`, UTC и ionosphere records для нескольких созвездий.

Это делает сохранение пользовательских результатов технически правдоподобным без третьего GNSS и без возврата бортового u-blox. Но protocol specification отдельно предупреждает, что часть сообщений зависит от firmware receiver. Ссылка M5Stack на документ не доказывает поддержку каждой команды конкретной ревизией Unit/U214.

`TXT-RFE` использовать как baseline нельзя: спецификация явно ограничивает его security timing products. Для `TXT-JSM`/`MON-JSM`/`MON-SEC` такого примечания нет, однако их наличие всё равно требуется проверить запросом версии, positive/negative HIL и сохранённым UART trace на каждом квалифицированном profile/revision.

## Почему ещё один M5 GPS Module не закрывает находку автоматически

M5Stack Module GPS v2.1 также основан на AT6668. Он добавляет другой stackable form factor, внешнюю антенну и PPS, но не возвращает u-blox API и не доказывает поддержку advanced CASIC-команд для уже принятых Unit/U214. Добавлять его только ради замены названий протокола — лишние connector/mechanical/BOM и qualification work.

## Gate закрытия

Нужно решить `IMP-0012`, после чего:

1. базовую навигацию отделить от необязательного advanced CASIC profile;
2. убрать из требований торговое имя AssistNow и конкретные UBX-поля;
3. не выдавать эвристику host за аппаратное обнаружение receiver;
4. считать advanced capability доступной только после per-profile proof;
5. проверить согласованность hardware/firmware target/current-state и EN/RU страниц.

## Первичные источники

- [M5Stack Unit GPS v1.1: AT6668, UART/NMEA и характеристики](https://docs.m5stack.com/en/unit/Unit-GPS%20v1.1)
- [M5Stack U214: AT6668 GNSS и официальный protocol link](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [CASIC Multi-mode Satellite Navigation Receiver Protocol Specification v6.3.2](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1173/CASIC_Multi-mode_Satellite_Navigation_Receiver_Protocol_Specification.pdf)
- [M5Stack Module GPS v2.1](https://docs.m5stack.com/en/module/Module_GPS_v2.1)
