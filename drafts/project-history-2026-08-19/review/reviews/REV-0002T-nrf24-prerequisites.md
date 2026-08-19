# REV-0002T — ревью пререквизитов 3×nRF24

- Статус: **Проведено ревью**
- Подшаг: 2T — prerequisite audit, не финальное ревью requirement set
- Артефакты: `FND-0019`–`FND-0021`, draft `REQ-N24-0001`, `IMP-0016`, `IMP-0017`
- Дата: 2026-08-16

## Проверено

- все `C-N24-01`–`C-N24-10` разложены на measurement, passive metadata, sensitive capture, active exploit, interference и test-source requirements;
- C5 ownership сохранён как target и не выдан за реализованный bus: current source всё ещё S3-owned, а `FND-0001` открыт;
- post-`DEC-0018` C5 budget теперь включает три IR RMT lines вместо legacy двух и требует полного пересчёта;
- generic 2×4 `PA/LNA` module placeholders не признаны exact BOM/RF/power/compliance evidence;
- ложные `FAB-READY` headers сняты, общий CE получил 100 kΩ reset pull-down, netlist проверен;
- `TXDET_NRF1..3` доказаны односторонними stubs без RF detectors и не считаются hardware TX-live;
- RPD определён как binary threshold около −64 dBm после 170 µs settle с temperature variation, не RSSI/dBm;
- parallel sweep остаётся реализуемым как three-radio binary sampling, но требует timestamp/schedule/calibration и не классифицирует Wi-Fi/Zigbee;
- silicon channel set исправлен с legacy 128 на 0–125, TX дополнительно ограничивается регионом/exact module;
- три антенны могут дать comparative hit-rate sectors, но не bearing/azimuth; VSWR требует отсутствующий reflectometer;
- ESB pseudo-promiscuous discovery отделён от address follow, validated payload и false-positive handling;
- MouseJack discovery отделён от active confirmation/injection, KeySniffer payload поднят в Controlled Zone;
- address brute-force, interference и constant-carrier/sweep tests требуют `BOTH`, conducted/RF-shielded containment и regulatory basis;
- nRF24 BLE-compatible advertising признан limited subset, не full BLE; native BLE improvement вынесен в `IMP-0017` до BLE-owner review;
- GPL MouseJack/RF24 references не выданы за MIT-reusable code;
- уменьшение трёх radio, асимметричные frontends или удаление safety/test parts не названы zero-loss saving.

## Результат

Prerequisite audit 3×nRF24-среза получил статус **«Проведено ревью»**. `REQ-N24-0001` остаётся **«На ревью»**: owner-level выбор `IMP-0016` определяет, будет ли baseline честным calibrated RPD hit-rate hunt либо потребует нового real-power measurement hardware.

`FND-0019` частично исправлен маркировкой/CE pull-down, но остаётся implementation finding. `FND-0020` закрывается requirement-level после выбора `IMP-0016`; `FND-0021` остаётся до BLE/licence/security propagation и implementation proof. Exact transport/pins/module/STOP/TX detector/RF/HIL не объявлены готовыми.

## Последующее состояние

Владелец принял `IMP-0016/A` как `DEC-0019`. Распространение решения и финальное ревью набора требований выполнены в `REV-0002U`; `REQ-N24-0001` получил статус **«Проведено ревью»**, а `FND-0020` закрыт на requirement-level.
