# Электрические prerequisites H2-R2

[English](h2-r2-electrical-prerequisites.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md)

Это живой реестр prerequisites новой production-схемы R2 с шестью доменами и
двумя RP. Здесь фиксируются проверенные результаты, а не история решений.
Все три строки prerequisites закрыты. Native R2 inventory прошёл `H2-R2.1.1`;
exact ledger symbols/contacts/footprints прошёл `H2-R2.1.2`, а сверка 4 243
endpoints и генерация [трёх native-проектов KiCad](h2-r2-native-kicad.ru.md)
пройдены в `H2-R2.1.3`, включая ERC без замечаний. Сквозная сверка sheets и
HW↔FW прошла в `H2-R2.1.5`. Печать и заказ по-прежнему запрещены.

| Маркер | Статус | Производственный результат |
|---|---|---|
| `H2-R2.0.1` | ✅ Проведено ревью | Точный onsemi `FSUSB42MUX` / JLCPCB `C11355`, MSOP-10, Extended SMT, Economic и Standard PCBA, источник JLCPCB, MSL 1. Live-снимок 2026-08-30: stock 66 698; доступно 66 045; MOQ 1; USD 0,3179 при количестве 1. Существующие корпус и topology выводов не меняются. |
| `H2-R2.0.2` | ✅ Проведено ревью | Принят точный always-on тракт: `DMN2056U-7` / `C332302` обнаруживает VBUS только через делитель 1 МОм + 1 МОм на изолированный затвор; `SN74LVC1G74DCUR` / `C70285` асинхронно защёлкивает service ownership; `74HC20PW,118` / `C546719` разрешает очистку только при отсутствии VBUS, низком C5 EN, high-Z SDIO Hub и явном AON release request. Все три детали доступны со склада для Standard PCBA с MOQ 1. Стоимость компонентов ровно для одного тракта вместе с пятью переиспользованными пассивами — USD 0,5857. |
| `H2-R2.0.3` | ✅ Проведено ревью | Точный TI `TCA9803DGKR` / JLCPCB `C2687966`, VSSOP-8, Extended SMT, Economic и Standard PCBA. Live-снимок 2026-08-30: stock 1 864; доступно 1 818; MOQ 1; USD 0,3525 при количестве 1. На MAIN A-side стоят две подтяжки `2,2 кОм`; AON B-side использует только внутренние источники 3,3 мА, поскольку TI запрещает внешние pull-up на B-side. Два точных Basic 1 мкФ `C52923` и два Basic 100 нФ `C1525` завершают локальную развязку обеих шин. Стоимость компонентов ровно для одного тракта — USD 0,3953. |

## Результат · все три prerequisites прошли ревью

Все три электрические схемы до ECAD теперь точны и устанавливаются фабрикой. В
состоянии `MAIN=off, AON=on` A-side TCA9803 находится в powered-off high-Z,
поэтому always-on mailboxes не подпитывают Hub. В обратном аварийном состоянии
powered-off защита bus pins не позволяет подпитать AON. Буфер не требует
определённого соотношения VCCA/VCCB, работает на 400 кГц и запускается не дольше
350 мкс. Залипшая mailbox-шина может убрать диагностику, но не блокирует
независимый `FAULT_KILL` и локальный watchdog Safety.

Результат H2 прошёл ревью как **`H2-R2.1.5`**; теперь H3 фиксирует его точные
входы и хеши. Quote, закупка и печать остаются запрещены.

## Evidence и правило перепроверки

- Live-карточки фабрики: [onsemi FSUSB42MUX / C11355](https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355), [Diodes DMN2056U-7 / C332302](https://jlcpcb.com/partdetail/DiodesIncorporated-DMN2056U7/C332302), [TI SN74LVC1G74DCUR / C70285](https://jlcpcb.com/partdetail/TexasInstruments-SN74LVC1G74DCUR/C70285), [Nexperia 74HC20PW,118 / C546719](https://jlcpcb.com/partdetail/Nexperia-74HC20PW118/C546719), [TI TCA9803DGKR / C2687966](https://jlcpcb.com/partdetail/TexasInstruments-TCA9803DGKR/C2687966), [Samsung 1 мкФ / C52923](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL05A105KA5NQNC/C52923), [Samsung 100 нФ / C1525](https://jlcpcb.com/partdetail/SamsungElectroMechanics-CL05B104KO5NNNC/C1525).
- Электрическая authority: [onsemi FSUSB42 datasheet](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf), [DMN2056U datasheet](https://www.diodes.com/datasheet/download/DMN2056U.pdf), [SN74LVC1G74 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), [74HC20 datasheet](https://assets.nexperia.com/documents/data-sheet/74HC20.pdf), [TCA9803 datasheet](https://www.ti.com/lit/ds/symlink/tca9803.pdf), [MSPM0C1106 datasheet](https://www.ti.com/lit/ds/symlink/mspm0c1106.pdf).
- Машинные sources: [`c5-sdio-service-mux-contract.json`](../hardware/architecture/c5-sdio-service-mux-contract.json) и [`pack-safety-i2c-boundary-contract.json`](../hardware/architecture/pack-safety-i2c-boundary-contract.json).
- Сгенерированные аудиты: [`H0-R2-c5-sdio-service-mux.json`](../hardware/architecture/generated/H0-R2-c5-sdio-service-mux.json) и [`H2-R2-pack-safety-i2c-boundary.json`](../hardware/architecture/generated/H2-R2-pack-safety-i2c-boundary.json).

Live-снимок доказывает маршрут только на момент выбора. Точный MPN, JLC-номер,
класс сборки, stock/явный sourcing route, MOQ и цена перепроверяются при
architecture freeze и непосредственно перед заказом ровно одного устройства.
