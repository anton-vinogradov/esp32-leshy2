# REV-0004A — вход этапа 4 и component evidence register

- Статус: **Проведено ревью реестра; компоненты не квалифицированы этим review**
- Дата: 2026-08-16
- Артефакт: [`BOM-0001`](../components/BOM-0001-stage4-component-evidence-register.md)
- Пререквизит: stage 3 **Проведено ревью** (`REV-0003U`)

## Проверки

| Проверка | Результат |
|---|---|
| все три compute domains, inter-domain passives и recovery paths перечислены | да, `C-001..007` |
| accepted power/STOP rails/functions перечислены | да, `P-001..008` |
| UI/display/touch/storage/service/power-wake controls перечислены | да, `U-001..008` |
| audio/receiver/dual IR перечислены | да, `A/R/I-*` |
| три независимых nRF, CC, voice и antenna/evidence paths перечислены | да, `RF/V-*` |
| external GNSS/LoRa/NFC не смешаны с base frontend BOM | да, `X-*` разделяет accessory и board-side obligations |
| named exact, conditional и still-abstract functions различимы | да, types `A/C/F/X` |
| evidence maturity не выдана за pass | да, `E0…E4/Q`; register review не присваивает component `Q` |
| известные legacy mismatches сохранены и имеют correction stage | да, семь строк mismatch table |
| зависимость от простого compute к safety/power и затем TX hardware явна | да, `BOM-0002…0008` |
| zero-loss substitution и «лишнее» имеют change-control rule | да |

## Результат

Вход этапа 4 полный и непротиворечивый. `BOM-0001` получает статус **«Проведено ревью»** только как реестр и порядок работы. Ни один exact component, rail topology, RF module или alternate не считается квалифицированным этим решением.

Следующий шаг без owner decision — `BOM-0002`: primary/current verification exact S3/C5/RP/TCA targets, затем clock, recovery, stepping/marking, lifecycle, AVL, assembly и compatibility identity.
