# REV-0002M — ревью Si4732 receiver и распространения варианта A

- Статус: **Проведено ревью**
- Подшаг: 2M — Si4732 receiver capability requirements
- Решение: `DEC-0015`
- Артефакт: `REQ-RX-0001`
- Дата: 2026-08-16

## Проверено

- все `C-RX-01`–`C-RX-07` покрыты стабильными requirement IDs;
- FM/RDS и ordinary LW/MW/SW отделены как документированный baseline квалифицированного Si4732/frontend;
- stereo output, I²S Si4732 и blanket «до 30 MHz» не добавлены поверх принятого mono analog→ES8311 пути;
- RDS validity/staleness и эфирное время не выданы за безусловно доверенные данные;
- SSB/CW условны локально импортированным совместимым volatile patch и никогда не маскируются как baseline;
- generic loader открыт, bounded и не исполняет blob как host MCU code;
- hash/integrity, provenance, license note и application-image signature не смешаны в одно ложное trust state;
- synchronous-AM сохранена как отдельный кандидат `defer`, не обещана и не подменена ordinary AM/SSB;
- bandscope честно определён как sequential tune/RSSI sweep, не FFT/IQ/real-time spectrum;
- scanner/WAV/decoder имеют storage, privacy, scope, confidence и corpus gates;
- SA868/other-TX overload, blanking, limiter, retune и desense HIL сохранены как последующие обязательные proof;
- решение не увеличивает BOM и не закрывает owner/developer firmware lifecycle;
- `FND-0010` закрыт на requirement-level, но patch rights/availability и реализация loader не объявлены доказанными;
- hardware/firmware target и current-state EN/RU пары обновлены согласованно;
- относительные ссылки изменённых документов проходят проверку.

## Результат

Si4732 capability-срез этапа 2 получил статус **«Проведено ревью»**. В target принят штатный FM/RDS/AM baseline и открытый owner-imported SSB/CW patch contract. Synchronous-AM отсутствует в текущем обещании продукта до отдельного решения и proof.

RF/frontend performance, protection/blanking, audio quality, patch provenance/compatibility, loader, storage recovery, decoder corpora и HIL остаются выходами последующих стадий.
