# REV-0004J — task-based display-performance decision propagation

> Последующее решение: `DEC-0052/REV-0004X` supersedes только shared-U214
> `256 B` clause; task/dirty-region thresholds настоящего review сохраняются.

- Статус: **Проведено ревью распространения решения**
- Дата: 2026-08-17
- Decision: [`DEC-0043`](../decisions/DEC-0043-task-based-display-performance.md)
- Proposal: [`IMP-0036`](../improvements/IMP-0036-task-based-display-performance.md)
- Evidence: [`DSP-0001`](../architecture/DSP-0001-display-storage-real-device-evidence.md)
- Finding: [`FND-0051`](../findings/FND-0051-legacy-display-interface-and-throughput.md)

## Проверено

| Проверка | Результат |
|---|---|
| inherited `10 full frames/s` remains active | нет; сохранён только как historical evidence |
| user-visible acceptance is explicit | critical/first menu feedback `≤100 ms`, continuous bounded waterfall, visible progress/drop evidence |
| radio/audio/storage precedence is retained | да; display bulk traffic preemptible and raw capture is not sacrificed |
| shared U214 timing is arithmetically possible | прежний `1 KiB` quantum исправлен на `256 B`; `≤250 µs` остаётся measured gate |
| exact display silently selected | нет; Waveshare/Elecrow/Riverdi remain verified references |
| independent SDMMC silently removed | нет; equivalent measured proof is still required |
| system/UI requirement updated | да; `REQ-SYS-14` now carries the accepted observable contract |
| machine-readable candidate gaps updated | да; task contract closed, exact optics/MPN/HIL remain visible |
| hardware and firmware target/current-state docs agree | да |

Scope решения и его распространения получает статус **«Проведено ревью»**.
Electrical qualification конкретной панели, touch/control topology и HIL не
проведены и не наследуют этот статус.
