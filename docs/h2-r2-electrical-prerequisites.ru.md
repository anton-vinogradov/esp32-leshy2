# Электрические prerequisites H2-R2

[English](h2-r2-electrical-prerequisites.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md)

Это живой реестр prerequisites новой production-схемы R2 с шестью доменами и
двумя RP. Здесь фиксируются проверенные результаты, а не история решений.
Native R2 ECAD/KiCad начинается только после закрытия всех трёх строк.

| Маркер | Статус | Производственный результат |
|---|---|---|
| `H2-R2.0.1` | ✅ Проведено ревью | Точный onsemi `FSUSB42MUX` / JLCPCB `C11355`, MSOP-10, Extended SMT, Economic и Standard PCBA, источник JLCPCB, MSL 1. Live-снимок 2026-08-30: stock 66 698; доступно 66 045; MOQ 1; USD 0,3179 при количестве 1. Существующие корпус и topology выводов не меняются. |
| `H2-R2.0.2` | ▶ Сейчас | Выбрать и доказать точный устанавливаемый фабрикой always-on detector/latch service-VBUS. Он должен асинхронно захватывать service ownership C5 без питания платы от service VBUS и без зависимости от прошивки. |
| `H2-R2.0.3` | ⏳ Ожидает | Закрыть powered-off-Ioff границу Pack/Safety I²C и раздельные pull-up `3V3_MAIN`/AON на Hub GPIO42/43. |

## Текущая точка · H2-R2.0.2

Фабричный маршрут mux больше не блокирует проект. Следующий исходный артефакт —
точная схема detector/latch с MPN, defaults, допустимыми переходами,
powered-off leakage, фабричным маршрутом, MOQ и ценой. Quote, закупка, печать и
native R2 ECAD остаются заблокированы.

## Evidence и правило перепроверки

- Live-карточка фабрики: [onsemi FSUSB42MUX / C11355](https://jlcpcb.com/partdetail/onsemi-FSUSB42MUX/C11355).
- Электрическая authority: [onsemi FSUSB42 datasheet](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf).
- Машинный source: [`c5-sdio-service-mux-contract.json`](../hardware/architecture/c5-sdio-service-mux-contract.json).
- Сгенерированный аудит: [`H0-R2-c5-sdio-service-mux.json`](../hardware/architecture/generated/H0-R2-c5-sdio-service-mux.json).

Live-снимок доказывает маршрут только на момент выбора. Точный MPN, JLC-номер,
класс сборки, stock/явный sourcing route, MOQ и цена перепроверяются при
architecture freeze и непосредственно перед заказом ровно одного устройства.
