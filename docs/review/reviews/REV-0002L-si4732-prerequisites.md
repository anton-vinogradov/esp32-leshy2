# REV-0002L — ревью пререквизитов Si4732 receiver

- Статус: **Проведено ревью**
- Подшаг: 2L — prerequisite audit, не финальное ревью requirement set
- Артефакты: `FND-0010`, draft `REQ-RX-0001`, `IMP-0013`
- Дата: 2026-08-16

## Проверено

- `C-RX-01`–`C-RX-07` и пересекающиеся storage/audio/privacy/TX-coexistence кандидаты получили будущие requirement IDs;
- Si4732-A10 и принятая mono ES8311/analog-bypass архитектура не подменены stereo/I²S обещаниями;
- FM/RDS, обычная AM, tune/seek/RSSI/SNR/AGC отделены как документированный receiver baseline;
- официальные диапазоны и будущая RF/frontend qualification отделены от заявления «всё до 30 MHz»;
- bandscope определён как sequential tune/RSSI sweep с timing/staleness limits, а не FFT/IQ/real-time spectrum;
- scanner log отделён от content recording, а WAV/decode наследуют `DEC-0009` и explicit privacy gate;
- decoder names не выданы за полную protocol support без corpora, scope и false-positive thresholds;
- SA868/other-TX overload, blanking, limiter и recovery сохранены как обязательные HIL prerequisites;
- найден `FND-0010`: MIT driver library, внешний SSB patch и synchronous-AM имеют разные proof/license состояния;
- для сохранения SSB/CW без роста BOM предложен открытый generic loader `IMP-0013/A`;
- signed base firmware не выдана за источник прав или доверия пользовательскому patch blob;
- synchronous-AM оставлена `defer`, а не молча исключена и не подменена ordinary AM/SSB;
- на момент аудита открыт ровно один owner-level выбор: `IMP-0013`.

## Результат

Аудит пререквизитов Si4732 capability-среза получил статус **«Проведено ревью»**. `REQ-RX-0001` остаётся **«На ревью»** до решения `IMP-0013`; затем требуются decision propagation, закрытие либо уточнение `FND-0010` и отдельный финальный review artifact.

RF/front-end performance, patch availability/rights, electrical protection, audio quality, storage recovery, decoder corpora и HIL не объявлены реализованными: это доказательства последующих стадий.
