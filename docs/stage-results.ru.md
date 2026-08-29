# Результаты этапов железа Leshy2

[На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [English](stage-results.md)

Здесь показан текущий результат каждого глобального этапа железа. Статус
**«проведено ревью»** появляется только после выполнения собственного критерия
выхода этапа. Работы старого baseline R1 — справочное evidence, а не приёмка
нового устройства R2.

<a id="h0"></a>
## H0 · Требования и функциональная архитектура

**Статус:** ✅ проведено ревью.

- [Текущая архитектура железа](hardware.ru.md)
- [Функциональная схема двух плат](images/h0-r2-functional-architecture.svg)
- [Машинная модель архитектуры](../hardware/architecture/h0-r2-rebaseline.json)

Результат: устройство разделено на переднюю UI/radio- и заднюю RF/power-плату.
UI остаётся локальным для S3, все три полных nRF24 — для переднего RP, а CC1101,
voice, broadcast/Airband, audio, FPV, расширения и safety — для заднего RP. Через
M1 идут transport управления/данных, один CVBS, safety evidence и питание, но не
основные RF-payload.

<a id="h1"></a>
## H1 · Физический дизайн устройства

**Статус:** ▶️ сейчас **`H1-R2.32`**.

- [Текущий физический дизайн](h1-r2-physical-layout.ru.md)
- [Внешние стороны](images/h1-r2-external-layout.svg?rev=h1-r2.21-dual-fpv-7)
- [Внутренняя сторона передней платы](images/h1-r2-inner-ui.svg)
- [Внутренняя сторона задней платы](images/h1-r2-inner-rf.svg)
- [Внешний сервисный доступ](images/h1-r2-service-access.svg?rev=h1-r2.21-dual-fpv-7)
- [Проверка вертикального FPV MMCX](images/h1-r2-mmcx-service.svg)
- [Машинный аудит размещения](../hardware/product-design/generated/H1-R2-placement-audit.json)
- [Тракт аналогового FPV](h1-r2-fpv.ru.md)
- [Приёмный тракт Airband](h1-airband-filter.ru.md)
- [Питание и thermal-архитектура](h1-r2-power-thermal.ru.md)
- [Machine-policy U214/U219](../hardware/architecture/generated/H1-R2-U219-cap-policy.json)

Точные dual-RP GPIO/M1 и электрический стык C5 SDIO/service-mux закрыты как
текущая H1-authority. Принятый профиль U219 делит защищённый Cap-слот с U214,
оставляет CC1101 RX-only и NFC poll/read-only и добавляет независимое evidence
NFC-поля в существующий safety aggregate.

Текущий физический результат: десять основных SMA разделены 5+5; FPV использует отдельный
вертикальный Molex `73415-2063` (`C588480`) MMCX на задней стороне. В
генерируемом размещении двух плат нет коллизий на одной стороне, минимальный
встречный зазор — 2,59 мм, включая исправленные официальные максимальные
full-package envelope U219. Увеличенная зона 30×24×8 мм содержит
взаимоисключающие post-PCBA-посадки K331 и AWM666V; устанавливается ровно один
приёмник, а C5 DBG10 перенесён. Проверка фактического модуля и пайки относится
к H5/H7. Пять активных host-корпусов U219 и их source-backed courtyards
помещаются в два выделенных острова, а все 43 текущих Cap/evidence-корпуса
получили fail-closed регистрацию координат и courtyards. Одна точная
документированная production-панель дисплея с контролируемым чертежом и
детерминированным маршрутом фабричной стыковки, footprints вспомогательных
пассивов, геометрия NFC pickup и swept volume установленной антенны — четыре
блокера финального принятия мокапа. Legacy-панель HMX остаётся только reference
evidence и не может попасть в R2 order BOM.
Экран физически развёрнут шлейфом к антенному торцу; прошивка поворачивает
память дисплея и touch-координаты на 180°. Первая безопасная замена pre-order
меняет пять `74LVC2G126DC,125` на складские буферы того же семейства
`74LVC2G126DP,125` (`C503392`) и снижает наблюдавшуюся строку пробной партии с
`$40,60` до `$12,1425` без изменения функции схемы. Более дешёвые складские
пары SMA/RP-SMA без гаек отклонены там, где направление, высота или сквозные
хвосты ухудшают принятую геометрию; независимая пара GCT сохранена.
Официальная identity C5 остаётся `ESP32-C5-WROOM-1U-N8R8`, а active stocked
route Standard PCBA — `C54951858` / supplier code `...-V1.2`. Для production
MD/lot identity и eFuse revision должны независимо доказать >=v1.2; v1.0 —
только engineering, исторический `C51950748` нельзя выбрать как active.
Эти placement-числа теперь включают host-switch U219, AON gate, два field bridge,
компаратор и явно неразмещённый reserve pickup-loop. Выбор точной документированной
production-панели дисплея, завершение канонического реестра, значений/MPN и
courtyards вспомогательных пассивов, геометрии pickup и swept volume установленной
антенны — текущая работа H1; после неё принимается перегенерированный мокап.
R2 H2/KiCad не начинались.

<a id="h2"></a>
## H2 · Production-схема

**Статус:** ⏳ ждёт H1.

Прежний результат G2F/H2/KiCad с проведённым ревью сохранён как историческое
single-RP evidence R1 и явно отменён как current authority. H2 R2 остаётся
переоткрытым до экспорта шести доменов, обоих RP и точного M1 из H0.

Ожидаемый результат: native KiCad-схемы, заново сформированные из архитектуры
R2, сверенная распиновка, ERC/NC-ревью и синхронный HW↔FW-контракт. На
[странице схем](schematics.ru.md) принципиальные диаграммы остаются видимыми, а
сохранённый ECAD R1 явно помечен как неактуальное evidence.

<a id="h3"></a>
## H3 · Виртуальная электрическая проверка

**Статус:** 🔒 ждёт проведённого ревью H2.

Ожидаемый результат: полная симуляция power, digital, RF, audio, timing,
thermal и faults. Все разрешённые состояния и переходы должны пройти до печати.

<a id="h4"></a>
## H4 · Объединённый pre-layout gate

**Статус:** 🔒 ждёт проведённого ревью H3 и актуального firmware R2 evidence.

Ожидаемый результат: одно актуальное mechanics/ECAD/electrical/firmware review
без virtual-blocker и с назначенным downstream-тестом для каждой физической неопределённости.

<a id="h5"></a>
## H5 · Компоненты и фабричные evidence

**Статус:** 🔒 ждёт проведённого ревью H4.

Ожидаемый результат: повторная проверка каждого точного MPN на текущей
поверхности JLCPCB, список аксессуаров после PCBA, qualification
consigned/private/global sourcing и назначение измерений полученных деталей контролируемым downstream-gates.

<a id="h6"></a>
## H6 · KiCad placement, routing и release candidate

**Статус:** 🔒 ждёт проведённого ревью H5.

Ожидаемый результат: две разведённые платы, сменный display-adapter и один
hash-locked fabrication package. H6 закрывается только после восьми проверяемых
подэтапов:

1. placement обеих сторон всех плат;
2. routed DRC/ERC и parity schema↔PCB для net/footprint/courtyard/fitted options;
3. повторный power/PDN/current/thermal/startup/load-step анализ на routed values;
4. digital SI, return paths, USB и M1;
5. RF 50 Ω, ground/via fences, isolation и extracted Airband parasitics;
6. STEP/stack/cables/swept volumes/enclosure collision review;
7. Gerber/drill/BOM/CPL/STEP/schematic/assembly outputs и test access;
8. независимый DFM и CPL-orientation review.

H6 сам по себе заказ не разрешает.

<a id="f-po"></a>
## F-PO · Допуск первого экземпляра

**Статус:** 🔒 ждёт финальные H2/H6 и firmware R2.

До оплаты должны пройти семь [machine-readable gates](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/first_spin_preorder_gate.json): импорт точной H2/H6 authority; шесть воспроизводимых diagnostic images; S3 QEMU; host/fake-HAL UI, controls и faults; доступные target dev-board прогоны; единый flash/recovery bundle; current-limited owner bring-up script. Полные продуктовые F6–F8 до заказа не обязательны, но диагностический путь каждого установленного устройства уже существует. Factory Function Test необязателен.

После `F-PO` отдельный immutable-release фиксирует одинаковыми hash Gerber,
drill, BOM, CPL, STEP, схемы, firmware и assembly instructions. Только затем
можно одобрить quote ровно одного собранного `R2-EVT1`.

<a id="h7"></a>
## H7 · Печать прототипа и bring-up

**Статус:** 🔒 ждёт проведённых H6 и `F-PO`, immutable release и явного одобрения exact-one quote.

До этого этапа прошивка прогоняется в host-тестах и на эмулированном железе. H7
заказывается ровно один фабрично собранный прототип без аккумуляторов. Released package не оставляет фабрике выбора компонентов, display mating или способа сборки; платный factory Function Test необязателен, а первый полный USB power-on делает владелец. H7 всё равно нужен для первой реальной платы: проверяются последовательность шин,
recovery, display/touch, controls, storage, radios, audio и safety.

<a id="h8"></a>
## H8 · RF-, safety- и endurance-проверка

**Статус:** 🔒 ждёт H7.

Ожидаемый результат: conducted/radiated RF, coexistence, идентичность антенн,
thermal/watchdog shutdown, сохранение причины аварии и 24–48 часов endurance.

<a id="h9"></a>
## H9 · Production release

**Статус:** 🔒 ждёт проведённого ревью H8.

Ожидаемый результат: замороженный manufacturing package, воспроизводимый
factory test, версионированные BOM/прошивка, release notes и финальная
документация продукта.
