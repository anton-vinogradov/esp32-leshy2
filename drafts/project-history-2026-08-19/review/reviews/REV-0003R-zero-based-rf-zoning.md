# REV-0003R — ревью zero-based RF zoning/coexistence

- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Этап: 3, шаг 5d
- Артефакт: `RFQ-0001`

## Проверка

| Gate | Результат |
|---|---|
| Equal RF product | все candidates сохраняют одинаковые S3/C5/3×nRF/CC/Si4732/voice/U214/NFC paths |
| No owner inheritance | controller placement взят из new `SYN/PIN`; legacy antenna/layout не является input |
| Equal comparison fixture | nRF sector geometry, exact modules, enclosure/display/battery/accessory state одинаковы |
| Mandatory concurrency | 3×nRF PRX remains `P`; exact sensitivity delta ≤3 dB from isolated reference and `BUD` service gate required |
| Honest coexistence | every other cross-domain pair starts `Q`, TX↔TX starts `X`; fallback is visible `T/D` |
| RF vs authorization | authorized white-hat role does not bypass spectrum/no-leakage/shielded-room gate or per-entry banner |
| Measurement | conducted access, actual-TX evidence, antenna identity and repeatable receiver fixture required |
| No false instrumentation | RPD not dBm/bearing/VSWR; current/register state not RF compliance proof |
| Candidate-specific risk | `2B` highest concentration, `3A` cleanest partition but adds oscillator; no unmeasured dB awarded |

## Саморевью «лишних» трактов

Отдельные `RF-CC`, `RF-RX` и `RF-VOICE` могут выглядеть избыточными из-за частичного пересечения диапазонов. Объединение сейчас не является zero-loss: оно добавляет switch/filter insertion loss, связывает TX fault с receive path и может удалить требуемую параллельность. Поэтому вопрос владельцу не требуется — shared-antenna вариант остаётся допустимым только как будущий полный equal-proof component/layout candidate, а не как молчаливая экономия.

Три nRF antenna paths также не заменяются одним radiator/switch: это прямо уничтожает simultaneous sector PRX и уже запрещено capability contract.

## Итог

Архитектурная RF-модель получает статус **«Проведено ревью»**. Все восемь layout/conducted/OTA gates остаются реальными будущими измерениями. Следующий сравнимый вход — dated recurring BOM и NRE/update/HIL burden, после чего возможен атомарный выбор.
