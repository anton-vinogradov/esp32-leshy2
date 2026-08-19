# REV-0002P — ревью пререквизитов NFC/RFID

- Статус: **Проведено ревью**
- Подшаг: 2P — prerequisite audit, не финальное ревью requirement set
- Артефакты: `FND-0015`, `FND-0016`, draft `REQ-NFC-0001`, переработанный `IMP-0005`
- Дата: 2026-08-16

## Проверено

- `C-NFC-01`–`C-NFC-10`, `OUT-06` и system/storage/security intersections получили стабильные будущие requirement IDs;
- legacy RFID2 ceiling пересмотрен по текущим первичным источникам, а не только по старой MFRC522 модели;
- новый M5 U216 сопоставлен с RFID2 и custom PN7160 по protocol, emulation, host interface, цене и разработке;
- U216 подтверждает A/B/F/V, MIFARE/NTAG/DESFire, FeliCa/ISO15693, NFC-A/F emulation и custom-mode direction, но каждое действие оставлено conditional до corpus/HIL;
- официальный M5 driver имеет MIT license и ESP-IDF 5.x examples; это не считается готовой интеграцией Leshy2;
- найден `FND-0015`: current `J40/J41=3.3 V` расходится с официальным 5 V pin profile обоих M5 NFC Unit;
- ложная source-пометка `FAB-READY` удалена, а `U44` обозначен как электрически несовместимый legacy placeholder до redesign;
- 5 V power и 3.3 V I²C safety не исправлялись поспешной заменой rail до общего stage-3 power/pin decision;
- найден lifecycle risk: exact `ST25R3916-AQWT` U216 помечен ST как NRND, хотя M5 Unit новый и доступен; fallback gate обязателен;
- `FND-0016` разделил silicon/frontend primitive и готовые product functions;
- ordinary tag read/write, credential analysis, recovery, destructive write, emulation и relay разнесены по трём уровням;
- Controlled-Zone operations получили `AUTHORIZED_TARGET`, fresh entry banner и отдельный action/target gate;
- one-frontend relay не обещан; future relay требует два frontend и latency/isolation HIL;
- LF 125 kHz не исключён навсегда, но честно требует отдельного hardware;
- hardnested/darkside не отброшены legacy-фразой «Linux-class» и не обещаны без license/runtime/corpus proof;
- IC-level EMV capability не выдана за payment-terminal compliance;
- стоимость сравнивается как total accessory+engineering cost: $2.05 экономии RFID2 не сохраняют advanced capability.

## Результат

Аудит пререквизитов NFC/RFID capability-среза получил статус **«Проведено ревью»**. `REQ-NFC-0001` остаётся **«На ревью»** до выбора варианта `IMP-0005`; открыт ровно один owner-level вопрос.

Exact accessory target, electrical port artifact, driver integration, sensitive storage, protocol corpus и HIL не объявлены реализованными: это доказательства следующих стадий.

Последующее состояние: владелец принял `IMP-0005/A` как `DEC-0017`, propagation review выполнен в `REV-0002Q`, а `REQ-NFC-0001` получил статус **«Проведено ревью»**.
