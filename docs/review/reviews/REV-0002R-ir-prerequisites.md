# REV-0002R — ревью пререквизитов consumer IR

- Статус: **Проведено ревью**
- Подшаг: 2R — prerequisite audit, не финальное ревью requirement set
- Артефакты: `FND-0017`, `FND-0018`, draft `REQ-IR-0001`, `IMP-0015`
- Дата: 2026-08-16

## Проверено

- `C-IR-01`–`C-IR-05` и system/storage/security intersections получили стабильные requirement IDs;
- C5 ownership сохранён как target и не выдан за доказанный S3↔C5 transport;
- ESP32-C5 подтверждён с 2 TX + 2 RX RMT channels; dual-RX architecture технически возможна, но расходует оба RX resources;
- current `TSOP38238` отделён от carrier-learning sensor: его demodulated envelope не содержит measured carrier;
- `TSMP95000` подтверждён как 30–60 kHz carrier-out learning path с typ. 1.8 m, а не безусловная robust-RX замена;
- out-of-band learning, включая 455 kHz, не обещан текущими frontend;
- current D57 — unqualified 0603 placeholder, 47 Ω не признан current proof без exact emitter/driver/rail/duty;
- ложная `FAB-READY` пометка снята, добавлен 100 kΩ Q58 base-emitter pull-down для reset/high-Z off;
- отдельный hardware TX-state/optical proof, STOP/dead-man, back-power, thermal and eye-safety остаются implementation gates;
- Main own remote/replay, Lab passive analysis и Controlled-Zone active tests разделены;
- TV-B-Gone/multi-code/brute-force sweep подняты из legacy Lab в Controlled Zone `BOTH`;
- unknown replay/service code получает `AUTHORIZED_TARGET`, а quick replay не обходит arming;
- protocol/code/AC databases получили provenance/licence/reproducible-generation gate;
- fixed receiver, learning receiver и dual-path сравниваются как разные функциональные варианты, поэтому меньший BOM не назван zero-loss автоматически.

## Результат

Prerequisite audit IR-среза получил статус **«Проведено ревью»**. `REQ-IR-0001` остаётся **«На ревью»**: открыт один owner-level выбор `IMP-0015` между dual-path A, single-learning B и fixed-38 C.

`FND-0017` частично исправлен безопасным pull-down/маркировкой, но остаётся implementation finding. `FND-0018` закрывается requirement-level только после выбора receiver architecture. Exact C5 pins, transport, optics, BOM, protocol port and HIL не объявлены готовыми.

Последующее состояние: владелец принял `IMP-0015/A` как `DEC-0018`, propagation review выполнен в `REV-0002S`, `FND-0018` закрыт на уровне требований, а `REQ-IR-0001` получил статус **«Проведено ревью»**.
