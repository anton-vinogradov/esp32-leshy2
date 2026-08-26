# H1-R2.5 · тракт аналогового FPV

[Главная](../README.ru.md) · [English](h1-r2-fpv.md)

Принят серийный функциональный кандидат приёмника и точная антенна; физическая приёмка K331 ещё не заявлена.

![Тракт аналогового FPV](images/h1-r2-fpv-path.svg)

## Результат

- `AKK K331` покрывает 5645–5945 МГц, до 200 мА и выдаёт CVBS 1 Vpp/75 Ω.
- CH1/CH2/CH3 используют уже зарезервированные Hub GPIO36/37/38; новых GPIO или расширителя нет.
- Резерв 5 В оставляет 150 мА запаса. RF идёт напрямую по 50-омной PCB-дорожке к MMCX без U.FL.
- Антенна `TBS5G8MMCXA` линейная, 5500–6000 МГц, 2.2 dBi, 102 мм; точная маркировка комплекта — `FPV · RX 5.8G`.

## Фабричная граница

Производитель показывает K331 в наличии по $29.99; точные поиски JLCPCB по `AKK K331`, `RX5808` и `RTC6715` дали 0 результатов. Поэтому до ответа private/global sourcing это отдельный модуль, а не заявленная фабричная PCBA-позиция. Антенна продаётся производителем за $6.95 и ставится в комплект после PCBA; JLCPCB для неё также не является сборочным маршрутом.

## Открытые gates

- obtain AKK-controlled maximum dimensions, land pattern and packaging/reflow evidence
- obtain a JLCPCB private/global-sourcing response or retain explicit post-PCBA hand installation
- prove the direct 50-ohm feed, MMCX launch, channel truth table, sensitivity, image rejection, decoder lock and video quality on assembled hardware
- qualify at least one supply-independent antenna fallback before antenna-kit freeze

> Точный текущий маркер: **H1-R2.5**. H1 продолжается.
