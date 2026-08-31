# Аппаратный роадмап Лешего2

[На главную](../README.ru.md) · [English](roadmap.md) ·
[Роадмап прошивки](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.ru.md)

> **▶ Текущая аппаратная граница: `H3-R2.7`.** H0, H1, [H2-R2.1.5](h2-acceptance.ru.md), [DC/source H3-R2.1](power-dc-source-result.ru.md), весь [workstream переходов питания H3-R2.2](power-transition-result.ru.md), [аналоговая проверка H3-R2.3](analog-electrical-verification.ru.md), [цифровая проверка H3-R2.4](digital-electrical-verification.ru.md), [RF-проверка H3-R2.5](rf-electrical-verification.ru.md) и [thermal/fault-проверка H3-R2.6](thermal-fault-electrical-verification.ru.md) прошли ревью. H3-R2.7 выполняет итоговый cross-check, реестр физических остатков и двуязычный отчёт фазы.
> KiCad routing R2, quote, reservation и заказ не разрешены.

Статус сверен: **1 сентября 2026 года**.

## Правила статусов

- ✅ **Проведено ревью** — результат фазы и evidence существуют.
- ▶ **Сейчас** — первая незавершённая аппаратная фаза.
- ⏳ **Ожидает** — предыдущая фаза ещё не завершена.
- 🔒 **Заблокировано** — downstream-действие запрещено до gate.

Аппаратные фазы идут последовательно. Закрытая глобальная фаза `H*` публикует
двуязычный итоговый отчёт со ссылкой ниже. Внутренний подшаг обновляет только
точный маркер и чеклист; он не выдаётся за ревью всей фазы.

## Текущая граница продукта

| Область | Текущий результат |
|---|---|
| Функциональная архитектура | ✅ [H0-R2 проведено ревью](h0-r2-functional-architecture.ru.md): передний UI/radio и задний RF/power домены, явные владельцы, transport, quiet-state и safety-crossings |
| Физический дизайн | ✅ [H1-R2.37 проведено ревью](h1-r2-acceptance.ru.md): полная модель двух плат, десять постоянных назначений антенн, точный EastRising-дисплей, слот U214/U219 и TX-evidence-острова физически согласованы; [все 210 MPN-групп базового BOM ранжированы](h1-r2-cost.ru.md) |
| Принципиальные диаграммы | Опубликованы актуальные связи компонентов/шин, внешний мокап, отдельные читаемые внутренние стороны, service map и диаграммы питания/фильтра |
| Production ECAD | ✅ [H2-R2.1.5 проведено ревью](h2-acceptance.ru.md): три native-проекта KiCad материализуют 1 185 экземпляров, 4 323 физических pins и 823 канонических nets без замечаний ERC; six-domain сверка sheets/HW↔FW проходит; G2F/H2/KiCad — только историческое evidence R1 |
| Пререквизит прошивки | ✅ firmware F1-R2 проведено ревью; F2-R2.4 квалифицировал все 12 target builds, 60 artifacts, 16 maps и 16 size gates, а F2-R2.5 reproducibility сейчас в отдельном [роадмапе F0–F11](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.ru.md); отдельный fail-closed `F-PO` требует диагностические образы, эмуляцию и recovery до заказа |
| Заказ | 🔒 Ровно один собранный `R2-EVT1` — только после H6, `F-PO`, immutable release-package и явного одобрения exact-one quote; производство — только на H9 |

## Проведённое ревью H1 · точный состав

<!-- current-substep: H3-R2.7 -->

**Маркер ревью: `H1-R2.37`.** Пакет компоновки принят 2026-08-30. Текущий
аппаратный маркер — `H3-R2.7`.

### 1. Размещение функциональных островов

- ✅ Передняя UI/radio-плата: S3, C5, три полных острова nRF24, передний RP и microSD.
- ✅ Задняя RF/power-плата: CC1101, VHF/UHF voice, FM/SW/AM/LW/Airband,
  аудио, M5, exact-one слот U214/U219, задний RP, питание и безопасность.
- ✅ Authority закрыто fail-closed: H0/H1 владеет шестью доменами и двумя RP;
  старые G2F/H2/KiCad содержат пять доменов, один RP и прежний M1, поэтому это
  только исторический R1 reference. Точные GPIO0..47 обоих RP, пять сигналов
  Hub↔RF через M1 и стык C5 SDIO/service-mux теперь machine-checked authority H1.
- ✅ GPIO переднего RP: `47/48`, свободна 1 линия; заднего RP: `43/48`, свободны 5 (GP32/33/34/37/38).
- ✅ Точный `ER-TFT035IPS-6` + `ER-TPC035-6` работает по прямому i8080-8 на точных 20 МГц через пассивный `L2-DISP-ADP-001-B`; клавиши остаются на локальном для S3 `TCA9539PWR`, а энкодер и USB — на прямых интерфейсах S3. После замыкания reset/service-трактов свободными остаются 6 GPIO.

### 2. Локальность RF и антенн

- ✅ Десять основных SMA разделены `5 + 5`; каждый заканчивается на плате,
  которой принадлежит его радиоостров.
- ✅ Передний порядок: `N24-0`, `S3-2G4`, `N24-1`, `C5-2G4/5`, `N24-2`.
- ✅ Задний порядок: `RX-FM/SW`, `RX-AM/LW`, `CC-SUB`, `VOICE-VHF`, `VOICE-UHF`.
- ✅ Ни один основной RF-тракт не пересекает M1; каждый из десяти антенных портов заканчивается на владеющей им плате.

### 3. Межплатный transport

- ✅ M1 полностью посчитан: 31 сигнал, 14 main-power, 2 AON, 24 определённых
  возврата и 9 настоящих NC; step 4,25 А даёт 0,3036 А на main-контакт.
- ✅ M1 не несёт силовой нагрузки: четыре упора 11,00 мм, минимум два
  anti-shear datums и независимый захват плат закрывают случай одного ослабленного винта.
- ✅ Заднее аудио занимает менее 0,4 МБ/с на проверенном RP-link 1,5 МБ/с;
  payload nRF локален передней плате.

### 4. Физический и сервисный аудит

- ✅ Коллизии корпусов на одной стороне: `0`.
- ✅ Минимальный встречный зазор: `2,59 мм`; требуется `0,70 мм`.
- ✅ Сохранены четыре независимых USB, восемь утопленных внешних recovery-кнопок
  и четыре ключевых fallback DBG10.
- ✅ Публичные схемы показывают по одной плате на изображение. Полная нумерованная
  проекция 226 references опубликована ссылкой как machine-review evidence.
- ✅ Главный мокап ставит прямой вид после переворота каждой платы сразу под её внешней стороной;
  шелкография антенн проходит проверки против корпусов, кабеля, U214, дисплея и крепежа.
- ✅ На внешней шелкографии печатаются `UI PCB · R2-EVT1 · REV A` и
  `RF/PWR PCB · R2-EVT1 · REV A`; изменяемый H1-R2.xx не попадает на платы,
  а PCB REV повышается только при изменении выпущенных производственных файлов.
- ✅ Генерируемый ценовой аудит ранжирует каждую строку BOM по установленному
  количеству и проекции на 100 устройств. BOM Tool capture на пять плат — только historical evidence; закупка целится в один полностью собранный протип без аккумуляторов.
- ✅ Исправлена недооценка R1→R2: cost-аудит теперь добавляет полный типовой
  набор второго RP2354B, четвёртые USB/recovery-группы и считает 1096 установок.
  Проверенные более дешёвые кнопки, держатели и Tag-Connect не приняты из-за
  ухудшения ESD/механики/service-workflow; их прежняя ожидаемая экономия удалена.
- ✅ Пять pre-order-буферов `74LVC2G126DC,125` заменены складским вариантом
  того же семейства `74LVC2G126DP,125` (`C503392`). Логика, порядок выводов,
  Schmitt-входы, `Ioff` и тайминги не изменились; увеличенные TSSOP-корпуса
  прошли повторные H2, H3 и физические проверки. Наблюдавшаяся строка партии
  из пяти устройств снизилась с `$40,60` до `$12,1425`.
- ✅ Поиск складских разъёмов без гаек сохранил независимые edge-launch GCT
  `RFPC-SMA31/32-FN-175-A` без общей антенной рамки. HenryTech направлены
  перпендикулярно плате, а DreamLNK `SMA-KWE901/902` имеют высоту около 10,2 мм
  и сквозные хвосты. Ни один вариант не является равноценной механической заменой.
- ✅ Точная GCT-посадка использует выбранный двусторонний принцип крепления:
  корпус SMA охватывает торец, две земляные лапы
  припаиваются к каждой стороне платы. Односторонняя edge-пайка запрещена
  машинным substitution-gate. Точная посадка A1 использует зазор корпуса
  `1,75 мм`, центры земляных лап `x=±2,55 мм` и RF-пяту шириной `1,87 мм`;
  H5 фиксирует документы/план, H7 проверяет каждый установленный разъём на
  единственном собранном прототипе; H8 выполняет обычную сборку/разборку,
  continuity/inspection и проверку каждого RF-тракта без искусственного
  старения, падений и vibration-программы.
- ✅ C5 сохраняет официальный MPN `ESP32-C5-WROOM-1U-N8R8`; active route
  Standard PCBA — Espressif `C54951858` с supplier code `...-V1.2`, stock 460,
  available 440 и MOQ 1. Production допускает только совпадающие MD/lot identity
  и eFuse revision >=v1.2; v1.0 остаётся engineering-only, а `C51950748`, v0.1,
  unknown identity и любое расхождение fail closed.

### 5. Интеграция U219 Cap

- ✅ U214 и U219 — взаимоисключающие профили одного защищённого Cap-слота.
  CC1101 U219 жёстко RX-only; NFC — poll/read-only и не включает поле без
  независимого `EV_N9` evidence в `ANY_TX_AON_N`.
- ✅ Pin 8 fail-low, pin 10 отключён до qualification, а точные SCL/SDA
  используют существующий изолированный I²C-тракт заднего RF RP.
- ⚠️ Идентичность питания U219 pin 7 остаётся received-unit gate. Если
  continuity, polarity и exact revision не докажут защищённые 5 В, профиль
  остаётся выключенным.
- ✅ Полные цепи pin-10 и NFC evidence содержат 18 точных production-корпусов с
  текущими JLC-маршрутами, официальными envelope и source-backed courtyards;
  каждый корпус помещается в свой ограниченный остров.
- ✅ Полноразмерный NFC pickup-loop, DNP tuning-bank и внешний swept volume
  штатной 108-мм антенны зарегистрированы. Пропуск, повторная проекция, подмена
  корпуса или незакрытая physical feature останавливают генерацию.

### 6. Итог ревью H1

- ✅ Бортовой аналоговый видеоприёмник, декодер, MMCX, антенна и физическая зона
  удалены. После PCBA нет скрытого активного модуля, требующего пайки владельцем.
- ✅ Точный текущий резерв: 6 GPIO у S3, 5 у заднего RP и 9 настоящих NC у M1;
  контакт 35 переносит latched `FAULT_KILL` к независимому лицевому индикатору,
  контакт 36 несёт отдельный S3 fault-UI reset.
- ✅ Полный внешний вид, обе внутренние стороны после физического переворота
  плат и реальные разрезы приняты 2026-08-30. [Открыть отчёт фазы](h1-r2-acceptance.ru.md).

## Проведённое ревью H2-R2.1.5 · native-проекты и сверка

**Маркер ревью: `H2-R2.1.5`.** Все prerequisites и exact ledgers закрыты.
Три native-проекта KiCad R2 теперь материализуют 1 185 устанавливаемых
экземпляров, 4 323 физических pins и 823 канонических nets. Все три root-
схемы читаются и экспортируются; ERC даёт ноль ошибок и ноль предупреждений.
Сквозная сверка sheets и HW↔FW проходит. Placement и routing ещё не начинались.

- ✅ `H2-R2.0.1`: точный маршрут Standard PCBA onsemi `FSUSB42MUX` / `C11355`
  прошёл ревью по live-поверхности: stock 66 698; доступно 66 045; MOQ 1;
  USD 0,3179 при количестве 1.
- ✅ `H2-R2.0.2`: по live-поверхностям Standard PCBA проведено ревью точного
  detector `DMN2056U-7` / `C332302` с изолированным затвором, асинхронной
  защёлки `SN74LVC1G74DCUR` / `C70285` и четырёхусловного release-gate
  `74HC20PW,118` / `C546719`. Стоимость установленных компонентов ровно для
  одного тракта — USD 0,5857.
- ✅ `H2-R2.0.3`: точная powered-off-граница TI `TCA9803DGKR` / `C2687966`
  прошла ревью с двумя MAIN-local pull-up 2,2 кОм, AON-local источниками 3,3 мА,
  четырьмя Basic decoupler и стоимостью компонентов USD 0,3953 для одного тракта.
- ✅ `H2-R2.1.1`: проведено ревью 3 native-проектов, 23 sheets, 6 владельцев
  доменов, 240 точных MPN-групп и 1 195 позиций.
- ✅ `H2-R2.1.2`: у 234 board groups есть по одной symbol- и footprint-identity;
  шесть non-PCBA groups явны; 1 658 логических контактов и все sheet affinities
  hash-bound, незакрытых групп нет.
- ✅ Contact-checkpoint `H2-R2.1.3`: 1 599 контактов платы во всех 234 группах
  сопоставлены реальным площадкам выбранных footprints или трём явным RF-интерфейсам
  на модулях; каждая именованная площадка учтена. Точный 50-контактный footprint
  Hirose FH34 и six-pad Coilcraft transformer материализованы по официальным чертежам.
- ✅ Symbol-checkpoint `H2-R2.1.3`: детерминированная library `Leshy2_R2`
  содержит 234 exact-MPN symbols и 1 612 уникальных electrical-pad pins; KiCad 10
  читает, пересохраняет и экспортирует контрольные symbols без ошибок.
- ✅ Instance-checkpoint `H2-R2.1.3`: все 1 185 устанавливаемых позиций из 234
  групп распределены по трём native-проектам; старый ledger R1 не передаёт ни
  одного net, reference designator или правила топологии.
- ✅ Net-checkpoint `H2-R2.1.3`: все 4 323 контакта устанавливаемых экземпляров
  сведены в 4 063 подключённых endpoints, 256 явных board no-connects и 823
  канонических nets; неразрешённых endpoints нет.
- ✅ Native-KiCad-checkpoint `H2-R2.1.3`: 3 проекта, 23 sheets графа, 1 185 symbols
  и 4 323 физических pins проходят parser/export и ERC без замечаний.
- ✅ `H2-R2.1.4`: шесть доменов, 173 строки контроллеров, 52 межпроектные и
  238 межлистовых nets сведены без незакрытых границ.
- ✅ `H2-R2.1.5`: [двуязычный отчёт фазы](h2-acceptance.ru.md) опубликован;
  синхронизированный firmware H2 gate открыт.
- 🔒 PCB placement, routing, quote, закупка и печать остаются запрещены.

[Открыть результат native KiCad](h2-r2-native-kicad.ru.md) ·
[результат net-checkpoint](h2-r2-net-ledger.ru.md) ·
[результат instance-checkpoint](h2-r2-instance-ledger.ru.md) ·
[живой реестр prerequisites](h2-r2-electrical-prerequisites.ru.md).

## Полный аппаратный путь

| Фаза | Статус | Результат | Критерий выхода |
|---|---|---|---|
| H0 · Требования и функциональная архитектура | ✅ [R2 проведено ревью](h0-r2-functional-architecture.ru.md) | Функции продукта, владельцы, transport, safety и рабочие pin-бюджеты | У каждой функции один владелец; все рабочие бюджеты сходятся |
| H1 · Физический дизайн продукта | ✅ [Проведено ревью · `H1-R2.37`](h1-r2-acceptance.ru.md) | Внешний вид, отдельные внутренние стороны, разрезы, точные корпуса, RF-локальность, сервис и power-envelope | Нет коллизий bodies/fasteners/silkscreen/antennas/accessories/opposing sides; точный MPN или контролируемый reserve; мокап принят |
| H2 · Production ECAD-схема | ✅ [Проведено ревью · `H2-R2.1.5`](h2-acceptance.ru.md) | Точные R2 symbols, contacts, nets, values, protection и footprints | Native KiCad, ERC без замечаний и сверка sheets/HW↔FW проходят |
| **H3 · Виртуальная электрическая проверка** | **▶ Сейчас · `H3-R2.7`** | Полная симуляция power, digital, RF, audio, timing, thermal и faults | Все разрешённые состояния и переходы проходят до печати |
| H4 · Объединённый pre-layout gate | ⏳ Ожидает H3 и firmware R2 evidence | Одно текущее mechanics/ECAD/electrical/firmware review | Нет виртуального blocker; каждой физической неопределённости назначен тест |
| H5 · Компоненты и фабричные evidence | ⏳ Ожидает H4 | Точная актуальная фабричная карта и контролируемые external routes | У каждой BOM-строки есть текущий фабричный маршрут без молчаливой замены |
| H6 · KiCad placement, routing и release candidate | 🔒 Ожидает H5 | Две разведённые платы, routed re-analysis и hash-locked fabrication candidate | Placement; DRC/ERC parity; power/thermal; SI/returns/USB; RF/extracted parasitics; STEP/stack/cables; outputs и независимый DFM/CPL review проходят |
| `F-PO` · Допуск первого экземпляра | 🔒 Ожидает H2/H6 и firmware R2 | Шесть diagnostic images, S3 QEMU, fake-HAL/dev-board evidence, flash/recovery и owner bring-up script | `FPO1`–`FPO7` проведены ревью на тех же H2/H6 candidate hashes; платный factory FCT не требуется |
| H7 · Печать прототипа и bring-up | 🔒 Ожидает H6, `F-PO`, immutable release и одобрение exact-one quote | Ровно один фабрично собранный `R2-EVT1` и owner bring-up log | Released assembly package не требует догадок фабрики; owner current-limited USB power-on проверяет rails, recovery, UI, storage, audio, radio и expansion |
| H8 · Физическая квалификация | 🔒 Ожидает H7 | HIL, RF, thermal, power, safety и endurance evidence | Concurrent nRF modes, quiet interfaces, coexistence, VNA, watchdog и single-fault tests проходят |
| H9 · Manufacturing release | 🔒 Ожидает H8 и firmware F11 | Воспроизводимый manufacturing/test package с выпущенной прошивкой | Ноль blocker и согласованные hardware/firmware release tags |

## Правила продвижения

1. Несоответствие исправляется в source-артефакте; downstream-вида перегенерируются.
2. Неожиданная функция не удаляется молча: сначала проверяется пропущенное требование.
3. Недорогое улучшение принимается автоматически только без изменения поведения продукта.
4. Каждый точный production MPN проверяется на актуальной JLCPCB Standard PCBA при выборе, architecture freeze и непосредственно перед заказом.
5. RF-передача и опасные тесты выполняются только на своей нагрузке, с разрешением владельца или в изолированной лаборатории.
6. Эмуляция не заменяет bring-up, но H7 не может стать первым запуском прошивки: до заказа обязателен [`F-PO`](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/config/first_spin_preorder_gate.json).

## Текущий путь выполнения H3

1. ✅ `H2-R2.1.1`: зафиксировать native R2 sources, sheet map и точный component inventory.
2. ✅ `H2-R2.1.2`: сформировать exact ledger symbols, contacts, values, protection и footprints.
3. ✅ `H2-R2.1.3`: материализовать 1 185 проверенных экземпляров и 823 канонических nets в трёх native-проектах KiCad; пройти ERC без замечаний.
4. ✅ `H2-R2.1.4`: пройти cross-sheet и HW↔FW reconciliation.
5. ✅ `H2-R2.1.5`: опубликовать двуязычный отчёт H2 и открыть H3.
6. ✅ [`H3-R2.0.1`](h3-r2-input-freeze.ru.md): связать хешами 14 входов H2 и ровно один раз назначить все 23 native-листа семи workstreams.
7. ✅ [`H3-R2.0.2`](parameter-model-register.ru.md): связать все 240 групп R2 и 1 185 устанавливаемых позиций с точным provenance, классами параметров и владельцами H3.
8. ✅ [`H3-R2.0.3`](verification-methods.ru.md): зафиксировать девять воспроизводимых методов, двенадцать pass/fail rules и fail-closed назначения для всех 240 групп.
9. ✅ [`H3-R2.1`](power-dc-source-result.ru.md): проверить worst-case DC, source, charge и power states.
   - ✅ [`H3-R2.1.1`](power-state-register.ru.md): перечислить все 2 266 разрешённых состояния.
   - ✅ [`H3-R2.1.2`](power-load-binding.ru.md): связать все 613 устанавливаемых питаемых экземпляров — 597 прямых и 16 косвенных — и шесть внешних нагрузок без скрытого aggregate.
   - ✅ [`H3-R2.1.3`](power-rail-margins.ru.md): провести ревью 224 профилей шин; все четыре шины проходят проверки напряжения, защиты и установившегося нагрева с минимальным запасом тока 30,560% и температуры кристалла 24,706 °C.
   - ✅ [`H3-R2.1.4`](power-source-margins.ru.md): назначить владельца всем 75 source/pack-строкам и безопасно допустить все 2 266 состояний; максимальный ток pack — 3,516 А против границы 8 А, заряд всегда уступает системной нагрузке.
   - ✅ [`H3-R2.1.5`](power-dc-source-result.ru.md): пройти все 15 cross-checks ownership, states, rails, sources и authorization и опубликовать H3-R2.1.
10. ✅ [`H3-R2.2`](power-transition-result.ru.md): проверить startup, shutdown, source handover, brownout, inrush и watchdog.
    - ✅ [`H3-R2.2.1`](power-transition-sequences.ru.md): проверить 14 упорядоченных сценариев startup, shutdown, reset и recovery без автоматического перезапуска.
    - ✅ [`H3-R2.2.2`](power-handover.ru.md): проверить все 7 316 переходов USB/pack, DPM, brownout и потерю источника.
    - ✅ [`H3-R2.2.3`](inrush-load-step.ru.md): проверить пять запусков защищённых шин, четыре load-step envelope, watchdog kill и сохранённое сообщение об ошибке.
    - ✅ [`H3-R2.2.4`](power-transition-result.ru.md): выполнить cross-check и опубликовать результат H3-R2.2.
11. ✅ [`H3-R2.3`](analog-electrical-verification.ru.md): проверить analog corners дисплея, аудио, IR, аккумуляторов и Airband.
12. ✅ [`H3-R2.4`](digital-electrical-verification.ru.md): проверить digital levels, timing, schematic loading, USB/service ownership, M1 adjacency и прямой i8080-8 на точных 20 МГц.
13. ✅ [`H3-R2.5`](rf-electrical-verification.ru.md): проверить RF feeds, coexistence, quiet states и одновременное обслуживание всех трёх nRF24; 71 проверка проходит для десяти постоянных портов и пяти съёмных microcoax.
14. ✅ [`H3-R2.6`](thermal-fault-electrical-verification.ru.md): проверить все 56 thermal-профилей, 30 single-fault сценариев и extended-operation policy; 25 сводных checks проходят, семь физических остатков назначены H6/H8.
15. ▶ `H3-R2.7`: выполнить cross-check всех текущих результатов R2, свести реестр физических остатков и опубликовать двуязычный отчёт фазы H3.

Следующее действие — итоговый cross-check и отчёт H3-R2.7. Placement, routing,
quote и любой заказ остаются заблокированы.
