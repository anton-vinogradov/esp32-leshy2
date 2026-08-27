<div align="center">

# ⭐ Leshy2

### Открытый автономный мультитул для радио, связи и разрешённых исследований

**Wi‑Fi 2,4/5 ГГц · BLE · 802.15.4 · 3× nRF24 · Sub‑GHz · VHF/UHF · FM/AM/SW/LW/Airband · аналоговый FPV RX · IR · LoRa**

[Возможности](docs/hardware.ru.md) · [Макет](#макет-целевого-устройства) · [Схемы](docs/schematics.ru.md) · [Роадмап](docs/roadmap.ru.md) · [Прошивка](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md) · [English](README.md)

**OPEN HARDWARE**　·　**MODULAR RF**　·　**FAIL-SAFE TX**　·　**REPAIRABLE**

</div>

> **Сейчас: H1-R2.12 · K331 остаётся основным после поиска полнофункциональных fallback; физический и фабричный гейты открыты.**
> [H0-R2](docs/h0-r2-functional-architecture.ru.md) добавляет второй
> `SC1512-A4` Hub, прямой захват аналогового FPV на S3 и обязательный
> receive-only Airband AM. Владение GPIO и фабричный active-BOM Airband закрыты.
> Hub, корпуса Airband и сменная зона FPV-приёмника K331 уже получили проверенную
> физическую проекцию. Официальные материалы на сайте AKK теперь подтверждают
> схему включения K331, функции всех 14 контактов и таблицу 24 каналов. K331
> вписывается в зарезервированные GPIO и питание; его
> контролируемый чертёж корпуса и фабричный маршрут ещё открыты. 27 августа точные
> запросы evidence отправлены AKK и JLCPCB; оба ответа ожидаются. Точная линейная
> антенна FPV выбрана. Эти два внешних пункта — единственные текущие блокеры H1;
> проверка собранного RF/video-тракта и квалификация запасной Taoglas остаются
> обязательными у последующих владельцев H3/H5/H6/H8. Новые публичные карточки
> `RTC6715`/`RX5808` имеют нулевой склад и не дают доступного module route;
> у голого RTC6715 также нет публичного reference RF/IF application, поэтому
> это не менее рискованная замена. MMCX исправлен: вместо целиком вынесенного за плату
> placeholder теперь показаны реальные 3,6 мм на плате и 3,0 мм снаружи;
> выводы wave soldering и боковые service-коридоры проходят аудит координат.
> Фильтр Airband получил генерируемый nominal/stress-аудит
> и увеличенную ячейку настройки. Новая ячейка 3V3_MAIN размещена и принимает
> 3,75 А continuous / 4,25 А step. Полные текущие физические виды сгенерированы,
> включая исправленный четвёртый независимый recovery-набор; их граница K331,
> схемы R2 и firmware-контракты остаются in progress. H1–H5 R1 остаются только evidence.
> Закупка, PCB routing и печать заблокированы.

<div align="center">

![Текущие внешние стороны Leshy2 H1-R2](docs/images/h1-r2-external-layout.svg)

**Прямые UI и дисплей · шесть вычислительных доменов · изолированные радиогруппы · один автономный прибор**

</div>

## Что такое Leshy2

Leshy2 — переносной открытый прибор для наблюдения за радиоэфиром, связи,
диагностики и работы белого хакера с разрешения владельца. Он объединяет
разные радиотракты в одном автономном устройстве, но физически разделяет
нагруженные шины, питание и безопасность передачи.

| Возможность | Что получает пользователь |
|---|---|
| **Три независимых nRF24** | Одновременные `3R`, `1T2R`, `2T1R` и `3T`, полный RX/TX/mix |
| **Широкий набор радио** | Wi‑Fi 2,4/5 ГГц, BLE, ESP‑NOW, 802.15.4, Sub‑GHz, VHF/UHF, FM/SW/Airband RX, аналоговый 5,8-ГГц FPV RX и IR |
| **Одиннадцать антенных входов** | Десять подписанных SMA/RP-SMA-трактов и отдельный MMCX `FPV RX 5.8G`; VHF и UHF независимы |
| **Автономный интерфейс** | IPS touch 3,5″ `320×480`, меню, водопад, microSD и audio |
| **Модульные расширения** | M5Stack U214/Leshy LoRa Cap и защищённый M5 Unit port |
| **Восстановление** | Независимые USB, RST/BOOT и внутренние DBG10 для вычислителей |
| **Безопасность** | Quiet-state, TX evidence, watchdog, thermal shutdown и retained fault reason |

## Как он устроен

Шесть изолируемых доменов разделяют пользовательский интерфейс, native radio/IR,
детерминированные радиотракты, высокоскоростной fan-out периферии, допуск
аккумуляторного пакета и независимую safety-автоматику.

- `ESP32-S3-WROOM-1U-N16R8` — UI, direct-QSPI display, захват аналогового FPV и Wi‑Fi/BLE.
- `ESP32-C5-WROOM-1U-N8R8` — Wi‑Fi 2,4/5 ГГц, IEEE 802.15.4 и IR.
- `SC1512-A4` / RF RP2354B — 3× nRF24, Sub‑GHz, voice и Cap Bus.
- `SC1512-A4` / Hub RP2354B — fan-out C5/RF, storage, audio, FM/SW/Airband и M5 Unit.
- `MSPM0C1106SDGS20R` №1 — независимый допуск батарейного пакета.
- `MSPM0C1106SDGS20R` №2 — watchdog, thermal supervision и TX leases.

Неиспользуемые интерфейсы аппаратно отключаются и переводятся в проверяемое
тихое состояние. Подробности — в [аппаратной архитектуре](docs/hardware.ru.md)
и [описании уровней безопасности](docs/safety.ru.md).

---

## Макет целевого устройства

Компактная схема ниже — текущая R2-архитектура. H1-R2.12 теперь генерирует
полные текущие внешние стороны, обе правильно зеркальные внутренние стороны,
сервисную поверхность четырёх доменов, антенный торец и четыре реальные
плоскости разреза. До закрытия корпуса и маршрута установки K331 они остаются
в работе, а не проведённым ревью.

![Функциональная архитектура Leshy2 H0-R2](docs/images/h0-r2-functional-architecture.svg)

![Полное внутреннее размещение Leshy2 H1-R2.12](docs/images/h1-r2-inner-complete.svg)

![Положение и зоны подключения MMCX Leshy2 H1-R2.12](docs/images/h1-r2-mmcx-service.svg)

![Питание и тепловой запас Leshy2 H1-R2.4](docs/images/h1-r2-power-thermal.svg)

[Открыть читаемое текущее размещение](docs/h1-r2-physical-layout.ru.md) ·
[результат питания и тепла](docs/h1-r2-power-thermal.ru.md) ·
[тракт аналогового FPV](docs/h1-r2-fpv.ru.md) ·
[проверка реализуемости фильтра Airband](docs/h1-airband-filter.ru.md).

![Текущий тракт аналогового FPV Leshy2](docs/images/h1-r2-fpv-path.svg)

Все виды ниже строятся одним генератором из реальных габаритов выбранных MPN
и общей системы координат. Надписи вне компонентов на внешних сторонах —
будущая шелкография; внутренние стороны шелкографии не содержат.

### Внешние стороны

Главный вид открывает страницу; ниже — детальные виды сервисных,
внутренних и торцевых зон.

### Прошивка и восстановление

![Внешний сервисный доступ Leshy2 H1-R2](docs/images/h1-r2-service-access.svg)

### Серийная навигация и сменный дисплей

![Серийный блок навигации Leshy2](docs/images/navigation-cluster.svg?layout=1)

![Сменный переходник дисплея Leshy2](docs/images/display-adapter.svg?layout=1)

### Внутренние стороны бутерброда

![Внутренние стороны плат Leshy2 H1-R2](docs/images/h1-r2-inner-complete.svg)

### Вид от антенного торца

![Вид Leshy2 со стороны антенного торца H1-R2](docs/images/h1-r2-antenna-edge.svg)

### Поперечные разрезы

![Внутренние разрезы бутерброда Leshy2 H1-R2](docs/images/h1-r2-inner-sections.svg)

![Разрезы внешних зон бутерброда Leshy2 H1-R2](docs/images/h1-r2-sandwich-sections.svg)

---

## Роадмап и текущая позиция

Роадмап остаётся на стартовой странице вплоть до передачи в печать/на фабрику и явной передачи производственных
файлов в печать. [Полная версия](docs/roadmap.ru.md) содержит зависимости и
критерии выхода; [результаты этапов](docs/stage-results.ru.md) ведут к
опубликованным чертежам, схемам, контрактам и проверкам.

| Этап | Статус | Результат |
|---|---|---|
| H0 · Требования и функциональная архитектура | ✅ Проведено ревью R2 | [Отчёт H0-R2](docs/h0-r2-functional-architecture.ru.md) |
| **H1 · Физический дизайн устройства** | **▶️ Сейчас: H1-R2.12, K331 основной после поиска полнофункциональных fallback** | [Текущий результат](docs/h1-r2-physical-layout.ru.md) |
| H2 · Production ECAD-схема | ⏳ Evidence R1 сохранено; ожидает H1 R2 | [Результаты H2](docs/stage-results.ru.md#h2) |
| H3 · Виртуальная электрическая проверка | ⏳ повтор после H2 R2 | [Отчёт R1](docs/h3-acceptance.ru.md) |
| H4 · Объединённый pre-layout gate | ⏳ повтор после H3 R2 и firmware-контракта R2 | [Отчёт R1](docs/h4-prelayout-gate-report.ru.md) |
| H5 · Evidence компонентов | ⏳ Маршруты R1 сохранены; пересборка после H4 R2 | [Состав R1](docs/stage-results.ru.md#h5) |
| H6 · PCB placement и routing | 🔒 Ожидает H5 R2 | [План H6](docs/stage-results.ru.md#h6) |
| H7 · Печать прототипа и bring-up | 🔒 Ожидает H6 и одобрение заказа | [План H7](docs/stage-results.ru.md#h7) |
| H8 · Физическая квалификация | 🔒 Ожидает H7 | [План H8](docs/stage-results.ru.md#h8) |
| H9 · Производственный release | 🔒 Ожидает H8 и firmware F11 | [План H9](docs/stage-results.ru.md#h9) |

Каждая завершённая глобальная фаза `H*` получает отдельный понятный итоговый
отчёт, связанный с этой таблицей. Внутренние подэтапы обновляют точный маркер,
но не создают отдельные глобальные отчёты.

**Железо находится на H1-R2.12.** H0-R2 фиксирует шесть вычислительных доменов,
33/33 занятых GPIO S3, 45/48 занятых GPIO Hub и receive-only частотный план
Airband. Incremental active-BOM Airband проверен в живом каталоге JLCPCB и
стоит `$20.2038` до passives/assembly. Начальное R2-размещение добавляет четыре
точных устройства Airband, Hub RP2354B, TVP5150 и размерный MMCX без коллизий
на одной стороне. AKK-брендированный размерный кадр у продавца уточняет номинал
платы K331 до 28,7×23,1 мм; модель коллизий намеренно резервирует 30×24×4 мм.
С этим увеличенным резервом 27 встречных проекций сохраняют минимум 1,44 мм при
требовании 0,70 мм. Полные текущие внешние виды, обе зеркальные внутренние
стороны, карта сервиса, вид со стороны антенн и четыре плоскости разреза
генерируются из единого источника размещения. Перегенерация обнаружила и
исправила расхождение H0↔H1: Hub RP получил собственные data-only USB-C, две
утопленные кнопки RESET/BOOT и внутренний ключевой DBG10. Итого у устройства
четыре независимых USB-тракта, восемь внешних recovery-кнопок и четыре внутренних
fallback; все три повторно используемых точных MPN проверены вживую у JLCPCB.
Точный `TPS7A2018PDBVR` для шины 1,8 В принят по текущей фабричной поверхности.
Компактный генерируемый LC-кандидат Airband проходит номинальную
маску и stress-точки 95/105/155/220 МГц, но в худшем случае на 180 МГц даёт
34,62 дБ вместо требуемых 40 дБ. Это ещё не production BOM: зарезервирована
экранированная землёй ячейка 24×11 мм с альтернативными/DNP-площадками. H3
использует ограниченные pre-layout-паразитики, H6 повторяет расчёт с extraction
до заказа H7, а H8 закрывает fitted/DNP-state измерением VNA. Порты и антенны комплекта получили совпадающие
текстовые коды; цвет только дублирует их. Старый main-rail R1 2,5 А заменён
размещённой ячейкой `TPS566231PRQFR` / `PSPMAA0605H-2R2M-ANP`. Двенадцать
разрешённых групп достигают максимум 2,823 А; принята envelope 3,75 А
continuous / 4,25 А step с гарантированным порогом eFuse 4,340 А и без новых
коллизий корпусов. Материалы на сайте AKK подтверждают схему включения 331RX,
функции всех 14 контактов K331 и таблицу 24 каналов; `AKK K331` проходит
проверку зарезервированных GPIO Hub и 5-В бюджета, а `TBS5G8MMCXA` стала точной 13-й антенной комплекта для
ключованного MMCX `FPV RX 5.8G`. K331 остаётся физическим резервом до получения
контролируемых AKK размеров и маршрута JLCPCB private/global sourcing либо явной
ручной установки. Контролируемый производителем `AWM666V RX` входит в ту же ячейку 30×24×4 мм и
силовой бюджет как fallback, но его семиканальный план 5725–5875 МГц заметно
уже K331, а точный поиск JLCPCB даёт 0 результатов, поэтому замена не принята.
Поиск полнофункциональной замены также не дал production-варианта:
контролируемый `SP166RX` имеет 42,418×29,46 мм ещё без высоты, а его RF-summary
противоречит таблице каналов; `MM238R-MCU` подходит функционально и по размерам,
но не имеет контролируемого текущего маршрута производителя и найден только
отсутствующим/снятым с продажи. Точные поиски JLCPCB дали 0 результатов для обоих.
Точные запросы механических/assembly-данных и sourcing-маршрута отправлены AKK
и JLCPCB 27 августа 2026 года; ожидаемые ответы не закрывают ни
один gate. Точный `DL-MMCX-KWE-90` теперь правильно пересекает правую кромку
платы; его выводы номинально входят в межплатный просвет на 1,2 мм и не имеют
встречного корпуса. Машинно проверены минимум 4,5 мм для проёма стенки и
Ø12×20 мм для подключения штекера. JLCPCB относит позицию к wave soldering
Economic/Standard PCBA; стыковка полученных деталей, финальный допуск стенки,
удержание и strain остаются evidence H5. H3 ещё доказывает эффективную ёмкость,
load-step, switching loss и тепло корпуса. Полные физические виды остаются in
progress до фиксации контролируемого корпуса K331 и маршрута его установки.
Заказ не разрешён.

<!-- current-substep: H1-R2.12 -->

**Точный маркер: `H1-R2.12`** — [текущее размещение](docs/h1-r2-physical-layout.ru.md),
[результат питания](docs/h1-r2-power-thermal.ru.md) и [результат FPV](docs/h1-r2-fpv.ru.md)
проходят machine-аудиты. Далее нужно получить контролируемые корпусные/посадочные
данные K331 и закрыть JLCPCB sourcing либо явный маршрут установки после PCBA;
после этого сгенерированные виды можно перевести в reviewed. Маркер, machine-state
и обе языковые страницы меняются вместе.

<details>
<summary><strong>Evidence R1 сохранено для переиспользования — это не текущий дизайн</strong></summary>

<!-- historical-substep: H5.0.3-R1 -->

**Точный маркер: `H5.0.3-R1`** — обновлённые [карта физических residuals](docs/component-evidence-map.ru.md)
и [поиск первичных источников](docs/component-source-research.ru.md) проведены.
[Неустранимая корзина](docs/component-sample-basket.ru.md) теперь содержит 33
priced lines на `$286.43`; [карта площадки](docs/manufacturing-platform.ru.md)
назначает всем 210 строкам BOM и 1052 установкам точные маршруты
`J0`–`J3`/`J4-F`/`J4-P` без замен. Публичные/read-only источники исчерпаны.
Частичный ответ JLCPCB от 26 августа подтверждает для SA818S-V MOQ 1 и
типичные 8–15 рабочих дней pre-order. Фабрика ошибочно поняла независимые U/V
позиции как возможную замену на одном designator, оставила большинство
J4-F/J4-P без ответа и проверяет Function Test только после заказа.
Аккумуляторы — пользовательский `J5-U`, не supplier-gate. Точное уточнение
подготовлено, но ещё не отправлено.
[`H5-EVR08`](hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json)
сохраняет PCBWay как неотправленный резерв полной сборки, а Seeed — как второй
источник PCBA.
Закупка, placement, routing и печать не разрешены.

- ✅ `H1.8` — полный физический дизайн принят 23 августа 2026 года.
- ✅ `H2.0.1` — проверен полный реестр из 1 081 схемной строки.
- ✅ `H2.0.2` — проверены четыре проекта, границы плат и имена цепей.
- ✅ `H2.0.3` — проверены HW↔FW/BSP-контракт и drift checks двух репозиториев.
- ✅ `H2.1` — созданы четыре независимых KiCad-проекта и 28 native-листов.
- ✅ `H2.2` — проведено ревью всех десяти листов UI/control PCB.
- ✅ `H2.3` — все 12 функциональных листов RF/power PCB реализованы и прошли ревью.
  - ✅ `H2.3.1` — `RF_00_ROOT`.
  - ✅ `H2.3.2` — `RF_01_USB_PD_CHARGE`.
  - ✅ `H2.3.3` — `RF_02_PACK_SAFETY_AON`.
  - ✅ `H2.3.4` — `RF_03_MAIN_RAILS_DOMAIN_GATES`.
  - ✅ `H2.3.5` — `RF_30_RP2354_CORE_SERVICE`.
  - ✅ `H2.3.6` — `RF_31_NRF24_X3`.
  - ✅ `H2.3.7-R1` — `RF_32_SUBGHZ_VOICE`: 143 компонента, 473 физических
    контакта, независимые CC1101, SA818S-V и SA818S-U; проведено ревью.
  - ✅ `H2.3.8` — `RF_34_U214_M5_EXT`: 53 символа, 52 устанавливаемых
    компонента, 228 контактов и две независимо защищённые ветви expansion;
    проведено ревью.
  - ✅ `H2.3.9` — `RF_35_REAR_CONTROLS`: семь устанавливаемых компонентов,
    36 контактов и четыре независимых прямых органа управления; проведено ревью.
  - ✅ `H2.3.10` — `RF_36_AUDIO_IO_AMP`: 14 символов, 34 контакта, точные
    footprints микрофона/усилителя и два независимых floating-BTL тракта;
    проведено ревью.
  - ✅ `H2.3.11` — `RF_40_INTERBOARD_M1`: все 80 физических контактов и 51
    интерфейс построчно совпадают с UI-side M1; проведено ревью.
  - ✅ `H2.3.12` — `RF_50_TX_SAFETY_EVIDENCE`: 97 компонентов и 369
    контактов, явные AON power/bypass, аппаратные watchdog/latch/reset и пять
    независимых каналов физического RF evidence; проведено ревью.
  - ✅ `H2.3.13` — `RF_60_TESTPOINTS_MANUFACTURING`: 52 физических
    test-площадок, 13 recovery-путей и 6 RF-evidence каналов;
    без покупных деталей, stub и отложенных fixture labels; проведено ревью.
- `H2.4` — схемы display-adapter и LoRa Cap.
  - ✅ `H2.4.1` — пассивный display-adapter: оба точных серийных разъёма,
    все 40 проводников один-к-одному и footprint FH34 по заводскому чертежу
    прошли native KiCad review.
  - ✅ `H2.4.2` — корневой лист LoRa Cap, все три дочерних листа и точная
    14-контактная host-граница; native KiCad review пройдено.
  - ✅ `H2.4.3` — два точных региональных one-of-two варианта модуля, прямой
    конечный RF-тракт, направленный coupler, SMA и forward-power detector;
    проведено ревью.
  - ✅ `H2.4.4` — защищённые 3,3 В и шина идентификации: восемь серийных
    компонентов, 22 контакта и все пять интерфейсов прошли native KiCad review.
  - ✅ `H2.4.5` — независимый physical-TX evidence: 11 серийных компонентов,
    34 контакта и аппаратный импульс около 13,3 мс; native KiCad review пройдено.
- ✅ **`H2.5` — проведено ревью:** независимое ревью safety-трактов.
  - ✅ `H2.5.1` — источники, допуск аккумуляторов, зарядка и все шины:
    [проведено ревью](docs/power-architecture.ru.md).
  - ✅ `H2.5.2` — reset, boot, service и recovery:
    [проведено ревью](docs/service-recovery.ru.md).
  - ✅ `H2.5.3` — no-back-power на USB, межплатной и expansion-границах:
    [проведено ревью](docs/interface-isolation.ru.md).
  - ✅ `H2.5.4` — reset-safe quiet state и изоляция неактивных интерфейсов:
    [проведено ревью](docs/quiet-state.ru.md).
  - ✅ `H2.5.5` — watchdog, thermal/fault supervision и `FAULT_KILL`:
    [проведено ревью](docs/fault-shutdown.ru.md).
  - ✅ `H2.5.6` — [сводка findings и закрытие ревью](docs/safety-review.ru.md).
- ✅ `H2.6` — [native ERC и все 202 намеренных NC проведены ревью](docs/erc-review.ru.md):
  четыре проекта дают ноль native errors/warnings, у каждого NC есть физический
  pin, точный marker и письменное обоснование.
- ✅ `H2.7` — [H1, физические контакты, nets, M1 и firmware F2 сверены](docs/hwfw-reconciliation.ru.md):
  1 079 электрических identities, 270 root nets, 80 контактов M1 и 130
  controller allocations не имеют оставшихся несоответствий.
- ✅ **`H2.8` — проведено ревью:** формальная финальная пользовательская приёмка перед H3.
  - ✅ `H2.8.1` — [пакет приёмки и deferred gates подготовлены](docs/h2-acceptance.ru.md).
  - ✅ `H2.8.2-R1` — принято пользователем 26 августа 2026 года; точный
    baseline по hash исходников записан в пакете приёмки.
- ✅ **`H3.0` — проведено ревью:** воспроизводимые входы и методы виртуальной проверки.
  - ✅ `H3.0.1` — [принятый H2 и все 16 областей проверки заморожены](docs/virtual-verification.ru.md).
  - ✅ `H3.0.2` — [реестр параметров и моделей собран](docs/parameter-model-register.ru.md);
    оставлены три полнофункциональных nRF24-модуля.
  - ✅ `H3.0.3` — [методы и десять pass/fail-правил зафиксированы](docs/verification-methods.ru.md).
- ✅ **`H3.1` — проведено ревью:** worst-case DC budget.
  - ✅ `H3.1.1` — [перечислены 43 source/charge и 2 032 полных состояния](docs/power-state-register.ru.md).
  - ✅ `H3.1.2` — [все 200 rail-профилей проходят](docs/dc-power-budget.ru.md); исправлен один порог eFuse.
  - ✅ `H3.1.3` — [все 2 032 состояния источников, заряда и разряда проходят](docs/source-charge-budget.ru.md).
  - ✅ `H3.1.4` — [DC evidence сведены и проведены ревью](docs/dc-verification-result.ru.md).
- ✅ **`H3.2` — проведено ревью:** переходы питания и динамика safety-loop.
  - ✅ `H3.2.1` — [startup, orderly shutdown и hard `FAULT_KILL`](docs/power-transition-startup.ru.md).
  - ✅ `H3.2.2` — [USB↔pack handover, DPM и brownout](docs/power-handover.ru.md).
  - ✅ `H3.2.3` — [eFuse, inrush и load steps](docs/inrush-load-step.ru.md).
  - ✅ `H3.2.4` — [watchdog, retained fault record и fault-only UI](docs/watchdog-fault-display.ru.md).
  - ✅ `H3.2.5` — [сводное ревью H3.2](docs/power-transition-result.ru.md); исправлены две source-ошибки.
- ✅ **`H3.3` — проверено:** analog peripheral corners.
  - ✅ `H3.3.1` — [display supply, backlight и direct-QSPI проведены ревью](docs/display-electrical-verification.ru.md); исправлены две source-ошибки.
  - ✅ `H3.3.2` — [codec, microphone, headset, speaker и voice-TX проведены ревью](docs/audio-electrical-verification.ru.md); исправлены четыре source-ошибки.
  - ✅ `H3.3.3` — [IR RX/TX, optical evidence и thermal limits проверены](docs/ir-electrical-verification.ru.md); исправлены четыре source-ошибки.
  - ✅ `H3.3.4` — [battery sensing, thermistors и analog fault thresholds проведены ревью](docs/battery-analog-verification.ru.md); исправлены четыре source-ошибки.
  - ✅ `H3.3.5` — [проверены 154 leaf и 22 сводных checks](docs/analog-corner-result.ru.md); закрыты 14 source-исправлений.
- ✅ **`H3.4` — проверено:** digital levels, timing и loading.
  - ✅ `H3.4.1` — [voltage levels, pulls, reset defaults и no-back-power проведены ревью](docs/digital-levels-verification.ru.md).
  - ✅ `H3.4.2` — [bandwidth, latency и timing проведены ревью](docs/digital-timing-verification.ru.md).
  - ✅ `H3.4.3` — [loading M1, U214, M5 Unit и service boundaries проведён ревью](docs/boundary-loading-verification.ru.md).
  - ✅ `H3.4.4` — [проверены 171 leaf и 27 сквозных digital checks](docs/digital-verification-result.ru.md).
- ✅ **`H3.5` — проведено ревью:** RF feeds, return paths, corridors и coexistence.
  - ✅ `H3.5.1` — [проверены feed/connector/matching/loss ограничения](docs/rf-feed-constraints.ru.md) всех десяти антенных трактов.
  - ✅ `H3.5.2` — [проверены RF corridors, keepouts, reference planes и returns](docs/rf-layout-constraints.ru.md).
  - ✅ `H3.5.3` — [проверены isolation, quiet-state и одновременные 3×nRF24](docs/rf-coexistence.ru.md).
  - ✅ `H3.5.4` — [сведены 128 leaf и 22 сквозных RF checks](docs/rf-verification-result.ru.md).
- ✅ **`H3.6` — проведено ревью:** thermal, fault-tree и unattended-operation verification.
  - ✅ `H3.6.1` — [тепловая модель плат, аккумуляторов и корпуса проведена ревью](docs/thermal-model.ru.md); исправлены charger TREG/TSHUT.
  - ✅ `H3.6.2` — [30 единичных отказов проведены через независимое shutdown и recovery](docs/single-fault-review.ru.md).
  - ✅ `H3.6.3` — [приняты `0…35 °C` как инженерная цель, USB для долгой работы и настраиваемый self-test](docs/unattended-operation.ru.md); обещаний времени работы нет.
  - ✅ `H3.6.4` — [проверены 70 leaf и 24 thermal/fault/endurance consolidation checks](docs/thermal-fault-result.ru.md).
- ✅ **`H3.7` — проведено ревью:** финальное закрытие virtual verification.
  - ✅ `H3.7.1` — [все требования H3, artifacts, H2 instances и root nets сверены](docs/h3-crosscheck.ru.md).
  - ✅ `H3.7.2` — [все 85 physical-only residual-строк опубликованы с владельцами evidence](docs/physical-evidence-register.ru.md).
  - ✅ `H3.7.3` — [формальный пакет приёмки H3 подготовлен](docs/h3-acceptance.ru.md).
  - ✅ `H3.7.4` — явное подтверждение пользователя записано.
- ✅ `H4.0.1-R1` — текущие hashes H3 связаны с принятым evidence firmware F3.
- ✅ `H4.1-R1` — объединены механика H1, ECAD H2, evidence H3 и firmware F3.
- ✅ `H4.2-R1` — повторный join не содержит stale source или открытых виртуальных противоречий.
- ✅ `H4.3-R1` — [обновлённый объединённый pre-layout gate проведён](docs/h4-prelayout-gate-report.ru.md).
- ✅ `H5.0.1-R1` — [девять residuals и 14 механических gates пересобраны](docs/component-evidence-map.ru.md) для обоих серийных SA818S.
- ✅ `H5.0.2-R1` — [первичные источники и серийные альтернативы проведены](docs/component-source-research.ru.md); exact U/V-маршруты сохранены, CE записан как немолчаливая qualified-pending UHF-замена.
- ▶️ `H5.0.3-R1` — корзина и карта 210 маршрутов готовы; частичный ответ JLCPCB записан, MOQ/типичный срок exact SA818S-V известен; аккумуляторы — пользовательский `J5-U`; уточнение по двум designator/J4-F/J4-P открыто; резерв PCBWay не опрошен.

Проверенный план H2 — [`h2-schematic-plan.json`](hardware/ecad/h2-schematic-plan.json),
завершённые H3/H4 — [`h3-verification-plan.json`](hardware/verification/h3-verification-plan.json)
и [`h4-prelayout-plan.json`](hardware/verification/h4-prelayout-plan.json),
текущий — [`h5-component-evidence-plan.json`](hardware/verification/h5-component-evidence-plan.json).
Закрытие каждой подзадачи меняет этот маркер и обе страницы roadmap в том же commit.

</details>

Firmware F3 уже прошла до H7: target-skeleton образы всех пяти доменов
собираются, size/rollback gates проходят, S3 исполняется в точном QEMU, а
недоступное non-S3 peripheral evidence назначено последующим dev-board/HIL
gates. Этот проверенный вход наследуется через H4 и не разрешает fabrication.

<!-- BEGIN GENERATED PRINCIPLE DIAGRAMS -->

## Принципиальные схемы и электрическая реализация

Принципиальные схемы устройства остаются частью сайта, но вынесены из главной страницы в [читаемый комплект по функциональным доменам](docs/schematics.ru.md). Рядом доступны [точная распиновка](docs/pinout.ru.md), [карта межплатного M1](docs/interconnect.ru.md) и [описание аппаратной архитектуры](docs/hardware.ru.md).

<!-- END GENERATED PRINCIPLE DIAGRAMS -->

## Документация

| Раздел | Содержимое |
|---|---|
| [Аппаратная архитектура](docs/hardware.ru.md) | Возможности, MPN и устройство доменов |
| [Принципиальные схемы](docs/schematics.ru.md) | Все связи компонентов и актуальные листы KiCad |
| [Распиновка](docs/pinout.ru.md) | Точные GPIO, nets, направления и владельцы |
| [Межплатный M1](docs/interconnect.ru.md) | Все 80 контактов и физическое прохождение |
| [Память и rollback](docs/memory.ru.md) | Flash/PSRAM, partitions и восстановление |
| [Безопасность](docs/safety.ru.md) | Три уровня функций, TX leases и FAULT_KILL |
| [LoRa Cap](docs/lora-cap.ru.md) | Съёмный региональный LoRa-модуль |
| [Производственная площадка](docs/manufacturing-platform.ru.md) | PCBA-ориентир, уровни доступности и точная граница сборки |
| [Физические первоисточники](docs/physical-source-register.ru.md) | Габариты и источники каждого корпуса |
| [Результаты этапов](docs/stage-results.ru.md) | Артефакты и evidence по H0…H9 |

<div align="center">

**Leshy2 — видеть эфир, понимать тракт, сохранять контроль.**

</div>
