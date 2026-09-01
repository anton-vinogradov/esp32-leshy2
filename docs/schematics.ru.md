# Принципиальные схемы Leshy2

[На главную](../README.ru.md) · [Аппаратная часть](hardware.ru.md) · [English](schematics.md)

Здесь собраны актуальные принципиальные схемы `H0-R2`/`H1-R2.38` готового
устройства: владельцы функций, шины, локальность RF, питание и сервисный
доступ. Точные dual-RP GPIO/M1 и электрический стык C5 SDIO/service-mux закрыты
как authority H1. Native production ECAD R2 уже существует как два
KiCad-проекта и проходит ERC с нулём ошибок и предупреждений;
cross-sheet и HW/FW reconciliation проходит в результате H2-R2.1.5. Placement
host-корпусов, все 18 компонентов U219, NFC pickup-loop, swept volume штатной
антенны и точный дисплей EastRising с прямым ZIF закрыты H1 и
материализованы в H2.

Сохранённое дерево G2F/H2/KiCad — проведённое ревью исторического **single-RP
R1**. В текущем H0/H1 шесть доменов, передний Hub RP, задний RF RP и новый M1.
Старое дерево не является authority R2 и не может использоваться для firmware
pin binding, печати R2 или заказа.

## Архитектура компонентов и шин

![Актуальная архитектура компонентов и шин H0-R2](images/h0-r2-functional-architecture.svg)

Передняя UI/radio-плата содержит S3, C5, все три полных острова nRF24,
передний RP и microSD. Задняя RF/power-плата содержит CC1101, оба
voice-радио, broadcast/Airband, аудио, M5 и взаимоисключающий Cap-слот U214/U219, задний RP,
питание и безопасность.

Точные рабочие группы GPIO и их бюджеты опубликованы в
[архитектуре H0-R2](h0-r2-functional-architecture.ru.md#рабочая-принципиальная-распиновка).

## Принцип межплатной связи

```mermaid
flowchart TD
  S3["ESP32-S3-WROOM-1U-N16R8<br/>UI через локальный TCA9539, прямой i8080-8"]
  C5["ESP32-C5-WROOM-1U-N8R8<br/>2,4/5 ГГц, 802.15.4, IR"]
  FRP["SC1512-A4 · передний RP<br/>3× nRF24, microSD"]
  RRP["SC1512-A4 · задний RP<br/>RF, audio, расширения"]
  LCD["ER-TFT035IPS-6 + ER-TPC035-6<br/>ILI9488/FT6236 · прямой 8-bit i8080 · точные 20 МГц"]
  M1["Hirose FX8C-80<br/>31 сигнал · 14 main-power · 2 AON<br/>24 возврата · 9 NC"]

  S3 -->|"LCD_CAM TX + GDMA"| LCD
  S3 <-->|"quad data + clock"| FRP
  FRP <-->|"4-bit SDIO"| C5
  FRP <-->|"проверенный RP-link 1,5 МБ/с"| RRP
```

Через M1 не проходят ни payload nRF, ни основной антенный RF-тракт. Удалённый
бортовой видеотракт оставляет шесть текущих свободных GPIO S3 и девять
настоящих NC-контактов M1. M1 выполняет только
электрическую функцию и совмещение; силовую нагрузку несут четыре 11-мм упора,
anti-shear datums корпуса и независимые захваты PCB.

## Физическая реализация принципа

![Внешние стороны и прямые виды после переворота плат](images/h1-r2-four-faces.svg?rev=h1-r2.36-complete-tx-evidence-1)

[Внутренняя сторона передней платы](images/h1-r2-inner-ui.svg) ·
[Внутренняя сторона задней платы](images/h1-r2-inner-rf.svg)

Внутренние номера — ссылки чертежа, а не шелкография. Текущий аудит размещения:
ноль коллизий корпусов на одной стороне и минимальный встречный зазор 2,59 мм
при требовании 0,70 мм.

## Отдельные сигнальные и силовые тракты

- [Входной фильтр Airband](h1-airband-filter.ru.md)
- [Питание, аккумуляторный pack и thermal supervision](h1-r2-power-thermal.ru.md)
- [Внешнее программирование, recovery и физические разрезы](h1-r2-physical-layout.ru.md)
- [Безопасность, watchdog и жёсткое отключение](safety.ru.md)

Принятый принцип U219 использует защищённый Cap-слот U214 и изолированные
I²C/SPI-тракты заднего RF RP. Pin 8 fail-low, pin 10 fail-disconnected, CC1101
RX-only, NFC poll/read-only, а независимое физическое evidence NFC-поля входит
в `ANY_TX_AON_N`. Идентичность питания pin 7 остаётся received-unit gate. Новые
Host-switch, AON gate, два bridge, comparator, вспомогательные пассивы,
геометрия reserve pickup-loop и swept volume установленной антенны
зарегистрированы и входят в результат H1/H2, прошедший ревью.

## Статус ECAD

Прежние KiCad-листы R1 и машинные отчёты сохранены в репозитории как
историческое инженерное evidence. Это **не** production-схема R2, и печатать
по ним нельзя. Текущий native R2 source — два проекта из
[результа `H2-R2.1.3`](h2-r2-native-kicad.ru.md): 22 sheets, 1 183
устанавливаемых позиций, 4 243 физических pins и 816 канонических nets. Он
ERC-clean; [результат H2-R2.1.5](h2-acceptance.ru.md) также проходит six-domain
cross-sheet/HW↔FW reconciliation. Placement, routing и последующие release-gates
остаются обязательными до печати.
