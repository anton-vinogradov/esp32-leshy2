# H1-R2.5 · тракт аналогового FPV

[Главная](../README.ru.md) · [English](h1-r2-fpv.md)

Принят серийный функциональный кандидат приёмника и точная антенна; физическая приёмка K331 ещё не заявлена.

![Тракт аналогового FPV](images/h1-r2-fpv-path.svg)

## Результат

- `AKK K331` покрывает 5645–5945 МГц, до 200 мА и выдаёт CVBS 1 Vpp/75 Ω.
- CH1/CH2/CH3 используют уже зарезервированные Hub GPIO36/37/38; новых GPIO или расширителя нет.
- Резерв 5 В оставляет 150 мА запаса. RF идёт напрямую по 50-омной PCB-дорожке к MMCX без U.FL.
- Антенна `TBS5G8MMCXA` линейная, 5500–6000 МГц, 2.2 dBi, 102 мм; точная маркировка комплекта — `FPV · RX 5.8G`. Независимый линейный резерв `FXP831.09.0100C` покрывает 4,9–6,0 ГГц и сохраняет MMCX, но сейчас доступен только под заказ с lead time 16 недель.

## Почему K331 остаётся ведущим кандидатом

- `AKK K331` — ведущий кандидат: единственный рассмотренный вариант, вписывающийся в зарезервированные GPIO, питание и рабочий габарит; контролируемый корпус и фабричный маршрут открыты.
- `AWM682 RX` — отклонён как основной: документированный корпус более чем вдвое превышает резерв по площади, а диапазон и число каналов уже.
- `TUE-RFVRX-58-D` — отклонён как основной: ещё до допуска превышает резерв 350 мА и межплатный просвет 11 мм.
- `generic RX5808` — отклонён как production-identity: опубликованные integration-evidence есть, но нет уникального order code, чертежа производителя и фабричного маршрута.

## Фабричная граница

Производитель показывает K331 в наличии по $29.99; точные поиски JLCPCB по `AKK K331`, `RX5808` и `RTC6715` дали 0 результатов. Поэтому до ответа private/global sourcing это отдельный модуль, а не заявленная фабричная PCBA-позиция. Антенна продаётся производителем за $6.95 и ставится в комплект после PCBA; JLCPCB для неё также не является сборочным маршрутом. 2026-08-27 запросы с точным перечнем механических, assembly и sourcing-свидетельств отправлены AKK и JLCPCB; оба ответа ожидаются.

## Открытые gates

- obtain AKK-controlled maximum dimensions, land pattern and packaging/reflow evidence
- obtain a JLCPCB private/global-sourcing response or retain explicit post-PCBA hand installation
- prove the direct 50-ohm feed, MMCX launch, channel truth table, sensitivity, image rejection, decoder lock and video quality on assembled hardware
- qualify FXP831.09.0100C on the assembled enclosure and secure available stock before relying on its current 16-week backorder route

> Точный текущий маркер: **H1-R2.5**. H1 продолжается.
