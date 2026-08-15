# REV-0002O — ревью analog voice и распространения SA518/A

- Статус: **Проведено ревью**
- Подшаг: 2O — analog voice/modem/relay capability requirements
- Решение: `DEC-0016`
- Артефакт: `REQ-VHF-0001`
- Дата: 2026-08-16

## Проверено

- все `C-VHF-01`–`C-VHF-07` и `OUT-07` покрыты стабильными requirement IDs;
- SA518 принят как preferred conditional target, а не как уже купленный/проверенный BOM item;
- SA868S fallback остаётся явно UHF-only и не получает VHF/dual-band label;
- accepted peak-power trade 2 W-class→1 W назван потерей характеристики ради dual-band, не zero-loss savings;
- exact module/revision/profile отображается production manifest и UI;
- 136–174/400–470 MHz target отделён от недоказанного SA868S 470–480 MHz края;
- proprietary SA518 short data не выдан за AX.25/APRS;
- manual PTT, automated transmitters, modem/iGate, beacon и Lab retransmission сохраняют раздельные gates;
- PMR446 false-compliance claim не возвращён;
- VOX остаётся `defer` по `FND-0013`, manual PTT от него не зависит;
- hardware safe defaults `FND-0011` сохранены, а независимый STOP `FND-0007` не объявлен готовым;
- current SA868 tsCircuit не заменён до stage-3/4 pin/power/RF artifact;
- current module selection, RF, audio, modem, legal profiles, storage/network и HIL не выданы за реализацию;
- hardware/firmware target и current-state EN/RU пары обновлены согласованно;
- относительные ссылки изменённых документов проходят проверку.

## Результат

Analog voice/modem/relay capability-срез этапа 2 получил статус **«Проведено ревью»**. Product contract предпочитает один SA518 dual-band backend с честным UHF-only SA868S fallback до qualification. `FND-0012` закрыт на requirement-level; `FND-0013`, `FND-0007` и implementation часть `FND-0011` переходят как явные gates следующих стадий.
