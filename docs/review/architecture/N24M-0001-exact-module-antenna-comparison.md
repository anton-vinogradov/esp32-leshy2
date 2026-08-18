# N24M-0001 — exact nRF module and antenna comparison

- Статус: **Проведено ревью входов; external-SMA direction принят `DEC-0048`**
- Дата: 2026-08-17
- Requirement: [`REQ-N24-0001`](../requirements/REQ-N24-0001-three-nrf24-raw-2g4.md)
- RF policy: [`DEC-0047`](../decisions/DEC-0047-qualified-nrf-mix-with-external-observer.md)
- Fixture: [`N24H-0001`](N24H-0001-two-device-full-mix-fixture.md)
- Exact electrical endpoint: [`N24E-0001`](N24E-0001-exact-three-nrf-electrical-endpoint.md)
- Legacy geometry: [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md)

## Проверенные реальные варианты

| Exact module | RF/antenna | Реально выведенные контакты | Механика | Питание и ток | Вывод для Leshy2 |
|---|---|---|---|---|---|
| Ebyte `E01-ML01S` | nRF24L01P, 0 dBm, встроенная PCB antenna | 8 castellated pads: `VCC/CE/CSN/SCK/MOSI/MISO/IRQ/GND`, шаг 1.27 mm | `12×19×1.63 mm` nominal | 2.0–3.6 V; TX 13 mA, RX 12 mA | минимальный BOM, но три модуля требуют трёх честных edge/antenna keep-out зон; скрывать их внутри clamshell или рядом с батареями нельзя |
| Ebyte `E01-ML01IPX` | nRF24L01P, 0 dBm, IPEX 50 Ω | те же 8 сигналов и порядок pads | `12×19×2.0 mm` nominal | 2.0–3.6 V; TX 13 mA, RX 12 mA | согласуется с тремя разнесёнными внешними/FPC антеннами и legacy SMA-bank через короткие pigtails; добавляет cable/connector/retention BOM |
| Ebyte `E01-2G4M27D` | nRF24L01P + PA/LNA, 27 dBm, SMA-K | 12 DIP pins: 8 functional signals, pins 9–12 additional GND | `18×33.4 mm` без SMA, высокая DIP/SMA сборка | 2.5–5.5 V; TX 490 mA at 3.3 V, RX 22 mA | три simultaneous TX требуют `1.47 A` только для nRF modules и ухудшают local leakage на 27 dB против 0 dBm; base handheld candidate не сходится |

`E01-ML01S` и `E01-ML01IPX` имеют одинаковый порядок восьми pads, размер тела
`12×19 mm` и nominal pad pitch. Это делает общий land pattern правдоподобным,
но не делает варианты механически взаимозаменяемыми в любой позиции:

- PCB-antenna version требует свободной от меди, деталей, батарей и корпуса
  antenna zone у кромки;
- IPEX version требует доступ к connector, cable bend radius, strain relief и
  воспроизводимую трассу до каждого radiator;
- общий footprint можно принять только после сверки land pattern двух exact
  revisions и specimen fit; до этого это optimization candidate, не BOM fact.

## Наложение на рабочую legacy geometry

Legacy генератор уже задаёт три разнесённые nRF antenna positions на внешней
задней грани `75×150 mm` clamshell и короткие pigtails от внутренних radio
modules. Он не задаёт owner и не доказывает RF isolation, но эта механика
непосредственно соответствует `E01-ML01IPX`. Встроенная antenna
`E01-ML01S` потребовала бы переразместить сами модули к трём свободным кромкам
и повторно доказать body/battery shadowing; просто поставить их в прежнюю
component zone нельзя.

Высота обоих compact modules укладывается в прежний 11 mm межплатный зазор на
бумаге. Для IPEX отдельно остаются cable stack, bend и fold collision checks.
Три high-power DIP/SMA modules этому compact placement не эквивалентны.

## Два уровня стенда

Заказанный второй **ESP32-DIV** образует ранний стенд `L0 DIV↔DIV`: он полезен
для воспроизведения режимов, packet manifests, потерь и самого факта
self-desense. Его exact nRF modules, rail, bus sharing и antenna geometry не
совпадают с Leshy2, поэтому `L0` не закрывает production sensitivity/power/
thermal acceptance.

Финальный `T1` выполняется на exact Leshy2 target revision: два сопоставимых
экземпляра либо один Leshy2 DUT и калиброванный conducted/OTA peer. Только
`T1` может утвердить versioned envelope `3R/1T2R/2T1R/3T`.

## Результат ревью

- exact real-module contacts, dimensions and current classes проверены;
- 27 dBm module исключён из рекомендуемого base direction, но не из отдельной
  Laboratory accessory study;
- compact 0 dBm IPEX принят как target layout/reference direction; PCB-antenna
  variant остаётся только bench/reference alternate;
- цена не объявляется без dated authorized-source quote;
- nRF24 series остаётся NRND, поэтому lot identity, genuine-silicon evidence,
  incoming inspection и alternate-source plan обязательны при любом выборе.
- `DEC-0091` now physically closes the reference's digital power boundary and
  full-band forward-power evidence without pretending that `IPX` proves a
  U.FL mate. Exact received pigtail/SMA qualification remains blocking.

## Первичные источники

- [Ebyte E01-ML01S product page/manual](https://www.cdebyte.com/products/E01-ML01S/4)
- [Ebyte E01-ML01IPX product page](https://www.ebyte.com/product/47.html)
- [Ebyte E01-ML01IPX 2025 specification](https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf)
- [Ebyte E01-2G4M27D product page/manual](https://www.cdebyte.com/products/E01-2G4M27D/4)
- [Nordic nRF24 series lifecycle page](https://www.nordicsemi.com/Products/nRF24-series)
- [ESP32-DIV upstream hardware overview](https://github.com/cifertech/ESP32-DIV)
