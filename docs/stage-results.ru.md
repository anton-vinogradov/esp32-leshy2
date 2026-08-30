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
voice, broadcast/Airband, audio, расширения и safety — для заднего RP. Через
M1 идут transport управления/данных, safety evidence и питание, но не
основные RF-payload.

<a id="h1"></a>
## H1 · Физический дизайн устройства

**Статус:** ✅ проведено ревью **`H1-R2.37`** 2026-08-30.

- [Отчёт по завершённой фазе H1](h1-r2-acceptance.ru.md)
- [Текущий физический дизайн](h1-r2-physical-layout.ru.md)
- [Внешние стороны](images/h1-r2-external-layout.svg?rev=h1-r2.37-reviewed-1)
- [Внутренняя сторона передней платы](images/h1-r2-inner-ui.svg)
- [Внутренняя сторона задней платы](images/h1-r2-inner-rf.svg)
- [Внешний сервисный доступ](images/h1-r2-service-access.svg?rev=h1-r2.37-reviewed-1)
- [Машинный аудит размещения](../hardware/product-design/generated/H1-R2-placement-audit.json)
- [Приёмный тракт Airband](h1-airband-filter.ru.md)
- [Питание и thermal-архитектура](h1-r2-power-thermal.ru.md)
- [Machine-policy U214/U219](../hardware/architecture/generated/H1-R2-U219-cap-policy.json)

Точные dual-RP GPIO/M1 и электрический стык C5 SDIO/service-mux закрыты как
текущая H1-authority. Принятый профиль U219 делит защищённый Cap-слот с U214,
оставляет CC1101 RX-only и NFC poll/read-only и добавляет независимое evidence
NFC-поля в существующий safety aggregate.

Текущий физический результат: десять основных SMA разделены 5+5. Точный экран —
EastRising `ER-TFT035IPS-6 + ER-TPC035-6` option 5344 через
Hirose `FH34SRJ-50S-0.5SH(50)` (`C3169104`) и сменный адаптер i8080-8. Панель
развёрнута шлейфом к антенному торцу; прошивка поворачивает изображение и
touch-координаты на 180°.

Единая координатная модель содержит 226 тел: все корпуса компонентов, все 18
тел U219, NFC pickup-loop, swept volume внешней антенны, разъёмы, органы
управления, сквозную механику, все восемь TX-детекторов и все пять обязательных
coupler. Восемь ограниченных локальных evidence-островов физически замыкают
каждый активный TX-тракт; шесть AD8314 используют принятый маршрут
`AD8314ARMZ-REEL` / `C652687`. Сгенерированные четыре стороны, внешние и
внутренние виды, антенный торец и разрез дают ноль коллизий на одной стороне и
минимальный встречный зазор 2,59 мм при норме 0,70 мм. Бортовой видеоприёмник,
декодер, разъём, антенна и физическая зона удалены. Одиннадцать GPIO S3, восемь
GPIO заднего RP и контакты M1 35–36 остаются резервами; скрытой ручной пайки нет.

Физических блокеров H1 больше нет. Полный мокап явно принят 2026-08-30. Это
ревью не разрешает KiCad или заказ.

<a id="h2"></a>
## H2 · Production-схема

**Статус:** ▶️ сейчас **`H2-R2.1.3`**.

Прежний G2F/H2/KiCad сохранён как историческое single-RP evidence R1. Все три
электрических prerequisites нового R2 и native source/sheet/component inventory
и exact ledger symbols/contacts/footprints прошли ревью. Сейчас создаются
controlled native definitions и joined nets; placement/routing не начинались.

Точный текущий чеклист:

1. ✅ `H2-R2.0.1`: точный live-маршрут Standard PCBA onsemi `FSUSB42MUX` /
   JLCPCB `C11355` прошёл ревью: stock 66 698; доступно 66 045; MOQ 1;
   USD 0,3179 при количестве 1;
2. ✅ `H2-R2.0.2`: точные detector `DMN2056U-7` / `C332302`, latch владения
   `SN74LVC1G74DCUR` / `C70285` и release-qualifier `74HC20PW,118` / `C546719`
   прошли ревью вместе с полными Standard-PCBA routes и fail-closed truth table;
3. ✅ `H2-R2.0.3`: точная граница TI `TCA9803DGKR` / `C2687966` для Pack/Safety
   прошла ревью с rail-local termination, четырьмя Basic decoupler и ценой USD 0,3953;
4. ✅ `H2-R2.1.1`: проведено ревью 3 проектов, 23 sheets, 6 владельцев доменов
   и 213 точных MPN-групп; native symbols/nets не создавались;
5. ✅ `H2-R2.1.2`: 208 board groups, пять явных non-PCBA groups и 1 555
   логических контактов отображены без незакрытых групп;
6. ▶ `H2-R2.1.3`: материализовать controlled definitions и соединить rails,
   M1, transports и явные NC.

[Native R2 inventory](h2-r2-native-inventory.ru.md) ·
[точные symbols/footprints](h2-r2-symbol-footprint-ledger.ru.md).

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
