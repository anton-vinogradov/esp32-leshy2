# FND-0035 — RP2354A availability was searched by the wrong identity

- Статус: **Исправлено; проведено ревью факта**
- Дата проверки: 2026-08-16
- Затронутые артефакты: `CST-0001`, `PKG-0001`, `REV-0003S/T`, current-state обоих репозиториев

## Несоответствие

Первый cost snapshot использовал distributor SKU `C41378174` и перенёс остаток одной LCSC-карточки в вывод «immediate stock RP2354A below 500». Одна карточка по общему наименованию не доказывает глобальную доступность exact A4 stepping и не должна была становиться allocation conclusion.

## Проверенные exact identities

| Identity | Meaning | Датированный публичный факт |
|---|---|---|
| `SC1511-A4` | RP2354A A4, 7-inch reel, 500 pcs | [Mouser](https://www.mouser.com/ProductDetail/Raspberry-Pi/SC1511-A4) показывает 782 available и $1.00/pc на full reel; [DigiKey](https://www.digikey.com/en/products/detail/raspberry-pi/SC1511-A4/28172162) — active part и отдельную 500-piece упаковку |
| `SC1511(13)-A4` | тот же RP2354A A4, 13-inch reel, 3400 pcs | [DigiKey](https://www.digikey.com/en/products/detail/raspberry-pi/SC1511-13-A4/28172169) показывает 6640 available; отличие — packaging quantity, не silicon/function |

Официальные [Raspberry Pi product facts](https://www.raspberrypi.com/documentation/microcontrollers/microcontroller-chips.html) подтверждают для RP2354A QFN60, 30 GPIO и stacked flash 2 MB. Exact A4 identity остаётся обязательной; generic `RP2354A` без order code/stepping в production manifest недостаточен.

## Исправление и граница вывода

- утверждение «public immediate stock below 500» снято;
- публичный snapshot теперь подтверждает возможность закрыть 500-unit quantity exact A4 part;
- `KG-01` не закрыт: distributor webpage не заменяет две письменные quotes, lot/stepping traceability, authorised-channel check и QFN60 assembly/yield evidence;
- историческая LCSC arithmetic в `CST-0001` не пересчитывается смесью currencies/suppliers и ещё не квалифицированного generic crystal. Её ranges остаются датированным conservative comparison, не current production COGS;
- exact stage-4 quote должна одновременно включать `SC1511-A4`/packaging-equivalent A4, recommended crystal, passives, assembly, yield and test time.

## Review result

Поиск по exact manufacturer order code устраняет исходный allocation claim без изменения принятой architecture. Finding получает **«Проведено ревью факта»**; коммерческая qualification остаётся открыта в `BOM-0002/0008`.
