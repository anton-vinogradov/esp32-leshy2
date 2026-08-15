# DEC-0014 — NMEA baseline и квалифицируемый advanced CASIC profile

- Статус: **Принято владельцем проекта**
- Дата принятия: 2026-08-16
- Принимает: `IMP-0012`, вариант A
- Закрывает на уровне требований: `FND-0009`
- Затрагивает: `REQ-GNSS-0001`, `C-GPS-01`, `C-GPS-03`, `C-GPS-04`, `C-X-06`, `C-X-07`, `DEC-0006`, `DEC-0008`

## Решение

GNSS-контракт разделяется на два независимых уровня:

1. **NMEA baseline** обязателен для каждого квалифицированного M5Stack Unit GPS v1.1 и GNSS-профиля U214. Он покрывает позицию, качество/возраст fix, навигацию, треки, вейпоинты, геозоны, geotag и безопасную синхронизацию времени.
2. **Advanced CASIC profile** является условной возможностью точного сочетания product/revision/firmware. Он может включать backend-native assistance и receiver-reported jamming/spoofing status только после воспроизводимого on-target proof.

Одновременно активен один GNSS backend. Совпадение AT6668, разъёма или общей protocol specification не является доказательством advanced compatibility другой ревизии.

## Assistance

- Торговое имя u-blox AssistNow и UBX-команды удаляются из целевого контракта AT6668.
- Разрешены проверенные CASIC initial position/time/frequency и constellation-specific ephemeris/UTC/ionosphere records.
- Пакет может поступать по Wi-Fi или с SD и обязан иметь источник, acquisition time, applicability, expiry, size bound и integrity validation.
- Постоянный Интернет и vendor-only cloud не требуются.
- Текущие координаты не отправляются наружу без отдельного явного согласия; допускаются manual/last-known hints с видимой неопределённостью.
- Ускорение cold/warm/hot start не обещается до измерения на каждой поддерживаемой ревизии.

## Индикатор целостности

После profile proof firmware может отображать receiver-reported `TXT-JSM`, `MON-JSM` или `MON-SEC`. Пользовательские состояния различают как минимум:

- `unavailable` — аксессуар отсутствует;
- `unsupported` — baseline работает, advanced command не поддерживается;
- `unknown` — ответ неопределён, устарел, повреждён или потерян;
- `normal` — receiver не сообщил признак в актуальном ответе;
- `suspected/strong interference`;
- `suspected/strong spoofing`.

`Unsupported`, timeout и parser error никогда не отображаются как `normal` или «угроз нет». Даже актуальный `normal` означает только отсутствие receiver-reported признака и не гарантирует истинность координат.

Host sanity checks по age/fix/satellites/DOP/time/velocity и доступным независимым источникам разрешены как второй защитный слой. UI и logs всегда отделяют `receiver-reported` от `host heuristic`; эвристика не называется аппаратным обнаружением spoofing.

## Стоимость и расширения

Решение не добавляет новый компонент или разъём в baseline и поэтому не увеличивает BOM. Цена — CASIC parser/driver, fixtures, test vectors и HIL на каждую поддерживаемую ревизию.

M5Stack Module GPS v2.1 или другой третий GNSS не становится обязательным. Такой backend может быть квалифицирован отдельно при будущем требовании к PPS, внешней антенне, иной механике или более сильной integrity telemetry.

## Обязательный proof следующих этапов

- сохранить identity и raw UART traces Unit GPS v1.1 и U214;
- доказать NMEA baseline, malformed-frame resilience, stale/loss/reconnect и storage recovery;
- составить per-profile capability descriptor поддерживаемых CASTXT/CASBIN IDs;
- доказать assistance rejection для corrupt/stale/wrong-constellation records и измерить TTFF delta;
- проверить mapping normal/interference/spoofing, включая `unknown`/timeout/unsupported;
- реальные RF interference/spoofing испытания проводить только в экранированной или иначе доказанно изолированной среде;
- измерить GNSS self-desense U214 при LoRa TX.

До этого решение принимает продуктовый контракт, но не объявляет advanced CASIC-функции реализованными конкретным аксессуаром.

## Первичные источники

- [M5Stack Unit GPS v1.1](https://docs.m5stack.com/en/unit/Unit-GPS%20v1.1)
- [M5Stack U214](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [CASIC Multi-mode Satellite Navigation Receiver Protocol Specification v6.3.2](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1173/CASIC_Multi-mode_Satellite_Navigation_Receiver_Protocol_Specification.pdf)
- [M5Stack Module GPS v2.1](https://docs.m5stack.com/en/module/Module_GPS_v2.1)
