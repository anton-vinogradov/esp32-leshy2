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

**Статус:** ✅ проведено ревью **`H1-R2.38`** 2026-08-30.

- [Отчёт по завершённой фазе H1](h1-r2-acceptance.ru.md)
- [Текущий физический дизайн](h1-r2-physical-layout.ru.md)
- [Внешние стороны](images/h1-r2-external-layout.svg?rev=h1-r2.38-fpc-slack-1)
- [Внутренняя сторона передней платы](images/h1-r2-inner-ui.svg)
- [Внутренняя сторона задней платы](images/h1-r2-inner-rf.svg)
- [PSA дисплея, ненатянутый путь FPC и прямой ZIF](images/display-mount.svg?rev=h1-r2.38-4910sq-1)
- [Настоящие разрезы бутерброда](images/h1-r2-inner-sections.svg?rev=h1-r2.38-fpc-slack-1)
- [Внешний сервисный доступ](images/h1-r2-service-access.svg?rev=h1-r2.38-fpc-slack-1)
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
декодер, разъём, антенна и физическая зона удалены. Шесть GPIO S3, пять GPIO
заднего RP и девять контактов M1 остаются резервами; скрытой ручной пайки нет.

Физических блокеров H1 больше нет. Полный мокап явно принят 2026-08-30. Это
ревью не разрешает KiCad или заказ.

<a id="h2"></a>
## H2 · Production-схема

**Статус:** ✅ проведено ревью **`H2-R2.1.5`** 2026-08-31.

Прежний G2F/H2/KiCad сохранён как историческое single-RP evidence R1. Все три
электрических prerequisites нового R2, native source/sheet/component inventory,
exact ledger symbols/contacts/footprints и сверка 4 243 endpoints nets прошли
ревью. Три native-проекта KiCad проходят ERC без замечаний; сверка sheets и
HW↔FW проходит. Placement/routing не начинались.

Точный текущий чеклист:

1. ✅ `H2-R2.0.1`: точный live-маршрут Standard PCBA onsemi `FSUSB42MUX` /
   JLCPCB `C11355` прошёл ревью: stock 66 698; доступно 66 045; MOQ 1;
   USD 0,3179 при количестве 1;
2. ✅ `H2-R2.0.2`: точные detector `DMN2056U-7` / `C332302`, latch владения
   `SN74LVC1G74DCUR` / `C70285` и release-qualifier `74HC20PW,118` / `C546719`
   прошли ревью вместе с полными Standard-PCBA routes и fail-closed truth table;
3. ✅ `H2-R2.0.3`: точная граница TI `TCA9803DGKR` / `C2687966` для Pack/Safety
   прошла ревью с rail-local termination, четырьмя Basic decoupler и ценой USD 0,3953;
4. ✅ `H2-R2.1.1`: проведено ревью 2 проектов, 22 sheets, 6 владельцев доменов
   и 238 точных MPN-групп;
5. ✅ `H2-R2.1.2`: 232 board groups, шесть явных non-PCBA groups и 1 578
   логических контактов отображены без незакрытых групп;
6. ✅ Definitions/instances `H2-R2.1.3`: 232 controlled symbols, 1 532 PCB-pad
   pins и все 1 183 устанавливаемых экземпляров проходят раскладку по двум проектам;
7. ✅ Nets `H2-R2.1.3`: 4 239 контактов устанавливаемых экземпляров сведены в
   816 канонических nets либо 237 явных board no-connects; незакрытых endpoints нет;
8. ✅ `H2-R2.1.3`: два native-проекта KiCad материализуют 4 243 физических pins
   и проходят ERC без ошибок и предупреждений;
9. ✅ `H2-R2.1.4`: шесть доменов, 173 строки контроллеров, 35 межпроектных и
   230 межлистовых nets сведены без незакрытых границ;
10. ✅ `H2-R2.1.5`: двуязычный итоговый отчёт опубликован, синхронизированный
    firmware H2 gate открыт.

[Итог ревью H2](h2-acceptance.ru.md) ·
[Native R2 inventory](h2-r2-native-inventory.ru.md) ·
[точные symbols/footprints](h2-r2-symbol-footprint-ledger.ru.md) ·
[распределение экземпляров](h2-r2-instance-ledger.ru.md) ·
[сверка native nets](h2-r2-net-ledger.ru.md) ·
[результат native KiCad](h2-r2-native-kicad.ru.md).

Ожидаемый результат: native KiCad-схемы, заново сформированные из архитектуры
R2, сверенная распиновка, ERC/NC-ревью и синхронный HW↔FW-контракт. На
[странице схем](schematics.ru.md) принципиальные диаграммы остаются видимыми, а
сохранённый ECAD R1 явно помечен как неактуальное evidence.

<a id="h3"></a>
## H3 · Виртуальная электрическая проверка

**Статус:** ✅ проведена на **`H3-R2.7`**. [Двуязычный итог фазы](h3-r2-acceptance.ru.md) · [реестр физических evidence](physical-evidence-register-r2.ru.md).

[`H3-R2.0.1`](h3-r2-input-freeze.ru.md) провёл ревью hash-bound входа H2 и полной
матрицы проверки R2. [`H3-R2.0.2`](parameter-model-register.ru.md) провёл ревью
точного происхождения параметров/моделей 238 групп и 1 183 устанавливаемых
позиций. [`H3-R2.0.3`](verification-methods.ru.md) фиксирует девять методов и
двенадцать pass/fail rules для всех 238 групп. [`H3-R2.1.1`](power-state-register.ru.md)
проводит ревью всех 2 266 разрешённых source, charge, fault и operating states.
[`H3-R2.1.2`](power-load-binding.ru.md) проводит ревью явной привязки 613
устанавливаемых питаемых экземпляров и шести внешних нагрузок. [`H3-R2.1.3`](power-rail-margins.ru.md)
проводит ревью 224 проходящих профилей всех четырёх шин с минимальным запасом
тока 30,560% и температуры кристалла 24,706 °C. [`H3-R2.1.4`](power-source-margins.ru.md)
проводит ревью всех 75 source/pack-строк и 2 266 состояний: максимальный ток
pack — 3,516 А, длительный допуск — 1,549 А, заряд уступает системной нагрузке.
[Cross-check H3-R2.1](power-dc-source-result.ru.md) сводит все 617 установленных/внешних нагрузок,
224 rail-профиля и 2 266 состояний в 15 проходящих проверках, поэтому H3-R2.1
проведён ревью. [`H3-R2.2.1`](power-transition-sequences.ru.md) проводит ревью
всех 14 упорядоченных сценариев startup, shutdown, reset и recovery без автоматического
перезапуска; S3 сохраняет fault-UI, а C5/RF RP сбрасываются напрямую.
[`H3-R2.2.2`](power-handover.ru.md) проводит ревью всех 7 316 случаев
USB/pack/DPM/brownout/source-loss без опасного допуска и автоматического
перезапуска. [`H3-R2.2.3/.4`](power-transition-result.ru.md) проводит ревью пяти
запусков защищённых шин, четырёх load-step envelope и десяти
watchdog/fault-display cases без аналитических failures или автоматического
перезапуска. [`H3-R2.3`](analog-electrical-verification.ru.md) проводит ревью всех
рассчитываемых analog corners дисплея, аудио, IR, аккумуляторов и Airband.
[`H3-R2.4`](digital-electrical-verification.ru.md) проводит ревью уровней,
таймингов, schematic loading, USB/service ownership, M1 и прямого i8080-8 на
точных 20 МГц. [`H3-R2.5`](rf-electrical-verification.ru.md) проводит ревью 71
проверки RF feeds, topology, cable slack, quiet-state и одновременной работы трёх
nRF24. [`H3-R2.6`](thermal-fault-electrical-verification.ru.md) проводит ревью всех
56 thermal-профилей, 30 single-fault сценариев и local-only extended-operation
policy через 25 проходящих checks. [`H3-R2.7`](h3-r2-acceptance.ru.md) сводит
20 текущих evidence-artifacts и все записанные source hashes без mismatch или
открытого аналитического finding. [Физический реестр](physical-evidence-register-r2.ru.md)
сохраняет все 51 небумажную строку открытой и назначенной H5/H6/H8.

<a id="h4"></a>
## H4 · Объединённый pre-layout gate

**Статус:** ✅ проведено ревью как **`H4-R2.3`**. [`H4-R2.0.1`](h4-r2-input-freeze.ru.md)
зафиксировал 24 точных входа. Сохранённая диагностика
[`H4-R2.0.2/H4-R2.1`](h4-r2-contract-reconciliation.ru.md) нашла один назначенный
38-строчный пробел генерации BSP в C5, Pack и Safety.
[`H4-R2.2`](h4-r2-correction-closure.ru.md) восстановил 173/173 строки и повторно
квалифицировал все 12 target-сборок. [Глобальный двуязычный итог H4](h4-r2-acceptance.ru.md)
закрыт без противоречий и передаёт все 51 physical-остаток.

<a id="h5"></a>
## H5 · Компоненты и фабричные evidence

**Статус:** ▶️ сейчас **`H5.0.3-R1`**.

JLCPCB подтвердил exact dual-module/no-substitution PCBA, но установил PCBA MOQ
2, отказался от полной сборки устройства и отложил special-process feasibility
до post-order review. Поэтому information-only запрос PCBWay от 2 сентября
теперь является активным full-device gate; quote, sourcing request, reservation,
purchase и order не создавались.

Ожидаемый результат: повторная проверка каждого точного MPN на текущей
поверхности JLCPCB, список аксессуаров после PCBA, qualification
consigned/private/global sourcing и назначение измерений полученных деталей контролируемым downstream-gates.

<a id="h6"></a>
## H6 · KiCad placement, routing и release candidate

**Статус:** 🔒 ждёт проведённого ревью H5.

Ожидаемый результат: две разведённые платы с точной панелью в прямом ZIF передней платы и один
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
