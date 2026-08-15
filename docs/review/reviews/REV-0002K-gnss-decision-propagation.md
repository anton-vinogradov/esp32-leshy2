# REV-0002K — ревью GNSS/navigation и распространения варианта A

- Статус: **Проведено ревью**
- Подшаг: 2K — GNSS/navigation capability requirements
- Решение: `DEC-0014`
- Артефакт: `REQ-GNSS-0001`
- Дата: 2026-08-16

## Проверено

- все `C-GPS-01`–`C-GPS-04` покрыты стабильными requirement IDs;
- пересекающиеся `C-X-06`, `C-X-07`, `C-X-11` и GNSS-часть `C-UX-01` не потеряны;
- NMEA baseline обязателен только для квалифицированных Unit GPS v1.1/U214 и не зависит от advanced profile;
- одновременно активен один GNSS backend, sensor fusion и blanket AT6668/M5 compatibility не обещаны;
- u-blox AssistNow/UBX удалены из целевого AT6668-контракта и заменены backend-native conditional mechanisms;
- assistance не создаёт постоянную Internet/vendor-cloud зависимость и имеет source/expiry/privacy gates;
- receiver-reported status отделён от host heuristics;
- unsupported/timeout/parser error дают `unknown`, а не false-safe `normal`;
- `normal` не назван гарантией истинности позиции;
- track/geotag, time discipline, geofence и accessory-loss имеют storage/privacy/fail-safe acceptance criteria;
- U214 LoRa self-desense и изолированный RF-test сохранены как обязательные proof;
- третий GNSS/M5 Module GPS v2.1 не добавлен без отдельного требования и BOM не увеличен;
- `FND-0009` закрыт на requirement-level, но per-revision firmware/HIL proof не объявлен готовым;
- hardware/firmware target и current-state EN/RU пары обновлены согласованно;
- относительные ссылки изменённых документов проходят проверку.

## Результат

GNSS/navigation capability-срез этапа 2 получил статус **«Проведено ревью»**. Это принимает продуктовый NMEA baseline и условный advanced CASIC contract, но не объявляет готовыми UART/power hardware, firmware parser, assistance source, конкретную поддержку advanced commands или RF/HIL результаты.
