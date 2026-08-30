# Электрические prerequisites H2-R2

[English](h2-r2-electrical-prerequisites.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md)

Это живой реестр prerequisites новой production-схемы R2 с шестью доменами и
двумя RP. Здесь фиксируются проверенные результаты, а не история решений.
Native R2 ECAD/KiCad начинается только после закрытия всех трёх строк.

| Маркер | Статус | Производственный результат |
|---|---|---|
| `H2-R2.0.1` | ✅ Проведено ревью | Точный onsemi `FSUSB42MUX` / JLCPCB `C11355`, MSOP-10, Extended SMT, Economic и Standard PCBA, источник JLCPCB, MSL 1. Live-снимок 2026-08-30: stock 66 698; доступно 66 045; MOQ 1; USD 0,3179 при количестве 1. Существующие корпус и topology выводов не меняются. |
| `H2-R2.0.2` | ✅ Проведено ревью | Принят точный always-on тракт: `DMN2056U-7` / `C332302` обнаруживает VBUS только через делитель 1 МОм + 1 МОм на изолированный затвор; `SN74LVC1G74DCUR` / `C70285` асинхронно защёлкивает service ownership; `74HC20PW,118` / `C546719` разрешает очистку только при отсутствии VBUS, низком C5 EN, high-Z SDIO Hub и явном AON release request. Все три детали доступны со склада для Standard PCBA с MOQ 1. Стоимость компонентов ровно для одного тракта вместе с пятью переиспользованными пассивами — USD 0,5857. |
| `H2-R2.0.3` | ▶ Сейчас | Закрыть powered-off-Ioff границу Pack/Safety I²C и раздельные pull-up `3V3_MAIN`/AON на Hub GPIO42/43. |

## Текущая точка · H2-R2.0.3

Mux и схема service ownership больше не блокируют проект. В принятом detector
нет DC-перехода от service VBUS к какой-либо шине устройства: номинальная
нагрузка 2,5 мкА уходит через делитель 2 МОм в землю, а drain MOSFET подтянут
только от `AON_SAFE_3V3`. Одновременный низкий `PRE_N` и `CLR_N` невозможен,
поскольку то же active-low evidence VBUS входит в четырёхусловный NAND очистки.
Следующий source-артефакт — точная powered-off-Ioff граница Pack/Safety I2C.
Quote, закупка, печать и native R2 ECAD остаются заблокированы.

## Evidence и правило перепроверки

- Live-карточки фабрики: [onsemi FSUSB42MUX / C11355](https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355), [Diodes DMN2056U-7 / C332302](https://jlcpcb.com/partdetail/DiodesIncorporated-DMN2056U7/C332302), [TI SN74LVC1G74DCUR / C70285](https://jlcpcb.com/partdetail/TexasInstruments-SN74LVC1G74DCUR/C70285), [Nexperia 74HC20PW,118 / C546719](https://jlcpcb.com/partdetail/Nexperia-74HC20PW118/C546719).
- Электрическая authority: [onsemi FSUSB42 datasheet](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf), [DMN2056U datasheet](https://www.diodes.com/datasheet/download/DMN2056U.pdf), [SN74LVC1G74 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), [74HC20 datasheet](https://assets.nexperia.com/documents/data-sheet/74HC20.pdf).
- Машинный source: [`c5-sdio-service-mux-contract.json`](../hardware/architecture/c5-sdio-service-mux-contract.json).
- Сгенерированный аудит: [`H0-R2-c5-sdio-service-mux.json`](../hardware/architecture/generated/H0-R2-c5-sdio-service-mux.json).

Live-снимок доказывает маршрут только на момент выбора. Точный MPN, JLC-номер,
класс сборки, stock/явный sourcing route, MOQ и цена перепроверяются при
architecture freeze и непосредственно перед заказом ровно одного устройства.
