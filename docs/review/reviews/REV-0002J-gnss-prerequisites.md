# REV-0002J — ревью пререквизитов GNSS/navigation

- Статус: **Проведено ревью**
- Подшаг: 2J — prerequisite audit, не финальное ревью requirement set
- Артефакты: `FND-0009`, draft `REQ-GNSS-0001`, `IMP-0012`
- Дата: 2026-08-16

## Проверено

- `C-GPS-01`–`C-GPS-04` и пересекающиеся `C-X-06`, `C-X-07`, `C-X-11`, `C-UX-01` имеют будущие requirement IDs;
- бортовой GNSS не возвращён, Unit GPS v1.1 и U214 остаются альтернативами с одним активным backend;
- базовая NMEA-навигация отделена от advanced receiver-specific функций;
- найдено и зафиксировано `FND-0009`: legacy u-blox library, AssistNow и UBX flags несовместимы с принятым AT6668;
- официальный M5/CASIC protocol предоставляет возможный обход через assistance/ephemeris input и собственные jamming/spoofing messages;
- protocol-level наличие не выдано за доказанную поддержку firmware конкретного аксессуара;
- unsupported/timeout не разрешено отображать как отсутствие угрозы;
- GNSS time не может молча ломать monotonic timers или откатывать wall clock;
- track/geotag хранит fix quality и privacy consent, не подставляет last-known как live;
- geofence не выдан за safety-of-life гарантию;
- отключение U214 пересечено с disarm LoRa, а LoRa self-desense оставлен обязательным HIL;
- M5 Module GPS v2.1 рассмотрен как возможное расширение, но не добавлен без требования: тот же AT6668 не исправляет u-blox-привязку;
- открыт ровно один owner-level выбор: `⚠️ IMP-0012`.

## Результат

Аудит пререквизитов GNSS/navigation проведён ревью. `REQ-GNSS-0001` остаётся **«На ревью»** до решения `IMP-0012`; затем требуется decision propagation, закрытие либо уточнение `FND-0009` и отдельный финальный review artifact.

Физическая доступность команд, UART levels/power, parser, RF self-desense, storage recovery и HIL не объявлены реализованными: это доказательства последующих стадий.
