# REV-0003O — ревью zero-based exact pin/controller maps

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3, шаг 5a
- Артефакты: `PIN-0002`, corrected `SYN-0001`, `FND-0034`

## Проверка

| Gate | Результат |
|---|---|
| Complete module maps | все 36 S3 и 21 C5 GPIO каждого candidate имеют role/free/reserved state |
| Controller collisions | два S3 SDMMC slots, GP-SPI, C5 fixed SDIO/USB/RMT и sole GP-SPI не double-booked |
| Memory/package coupling | все candidates фиксируют S3 `N16R2`; GPIO35…37 не объявлены доступными N16R8 |
| Recovery | S3/C5 native USB + boot/EN и RP dedicated USB/SWD/RUN сохранены |
| Strap state | S3 0/3/45/46 и C5 3/7/25…28 имеют explicit reset behavior |
| Full nRF semantics | three `CSN/CE/IRQ` states direct либо safe-latch + retained-level aggregate; no common CE |
| Latch correctness | radio SCK не shifting clock для deassert; mixed active levels задаются OE + safe pulls |
| No-loss correction | `FND-0034` переносит U214/GNSS на C5 resources в `SYN-2A` вместо удаления функции |
| Third-domain completeness | RP2354A maps 30 GPIO and retains non-GPIO recovery; no hidden external flash |
| Honest reserve | stage-3 straps/recovery pins не названы свободными; `SYN-3A` initially retained seven useful generic C5 GPIO. Later `DEC-0031/FND-0038` honestly reclassifies GPIO11/12 as service UART and leaves five generic GPIO |

## Re-review `SYN-0001`

Изменение `SYN-2A` затронуло physical placement U214/GNSS. Capability, concurrency, safety, external profile, update и recovery contracts не изменились; все остаются покрыты. `SYN-0001` повторно проверен и сохраняет статус **«Проведено ревью набора candidates»**.

## Итог

Все три candidates имеют collision-free exact module/controller maps и могут перейти к количественным memory/traffic/power/RF/cost gates. Ни один candidate не принят: нулевой spare `SYN-2A/2B`, дополнительный firmware domain `SYN-3A` и все measurement/quote gates остаются предметом atomic comparison.
