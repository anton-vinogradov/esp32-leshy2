<div align="center">

# ⭐ Leshy2

### Открытый автономный мультитул для радио, связи и разрешённых исследований

**Wi‑Fi 2,4/5 ГГц · BLE · 802.15.4 · 3× nRF24 · Sub‑GHz · VHF/UHF · FM/AM/SW/LW · IR · LoRa**

[Возможности](docs/hardware.ru.md) · [Макет](#макет-целевого-устройства) · [Схемы](docs/schematics.ru.md) · [Роадмап](docs/roadmap.ru.md) · [Прошивка](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md) · [English](README.md)

**OPEN HARDWARE**　·　**MODULAR RF**　·　**FAIL-SAFE TX**　·　**REPAIRABLE**

</div>

> **Сейчас: H5.0.3 · [аудит PCBA-площадки](docs/manufacturing-platform.ru.md).**
> JLCPCB Standard PCBA выбран неэксклюзивным ориентиром. Контрольный BOM Tool
> прогон сопоставил 176/209 строк и распознал все 1019 установок; exact-поиск
> разрешил все 33 outlier. Теперь у каждой строки есть маршрут `J0`–`J4` без
> замены; открыта только квалифицированная цена exact `SA518`. Закупка, PCB
> routing и печать заблокированы. Приложение JLCAPI и ключ подписи готовы вне
> Git; право Parts пока имеет статус `Reviewing` у JLCPCB.

<div align="center">

![Внешние стороны Leshy2](docs/images/current-clamshell.svg?layout=19)

**Девять независимых антенных трактов · пять вычислительных доменов · один автономный прибор**

</div>

## Что такое Leshy2

Leshy2 — переносной открытый прибор для наблюдения за радиоэфиром, связи,
диагностики и работы белого хакера с разрешения владельца. Он объединяет
разные радиотракты в одном автономном устройстве, но физически разделяет
нагруженные шины, питание и безопасность передачи.

| Возможность | Что получает пользователь |
|---|---|
| **Три независимых nRF24** | Одновременные `3R`, `1T2R`, `2T1R` и `3T`, полный RX/TX/mix |
| **Широкий набор радио** | Wi‑Fi 2,4/5 ГГц, BLE, ESP‑NOW, 802.15.4, Sub‑GHz, VHF/UHF, broadcast RX и IR |
| **Девять антенных портов** | Отдельные внешние подписанные разъёмы без RF-sharing |
| **Автономный интерфейс** | IPS touch 3,5″ `320×480`, меню, водопад, microSD и audio |
| **Модульные расширения** | M5Stack U214/Leshy LoRa Cap и защищённый M5 Unit port |
| **Восстановление** | Независимые USB, RST/BOOT и внутренние DBG10 для вычислителей |
| **Безопасность** | Quiet-state, TX evidence, watchdog, thermal shutdown и retained fault reason |

## Как он устроен

Пять изолируемых доменов разделяют пользовательский интерфейс, native radio/IR,
детерминированные радиотракты, допуск аккумуляторного пакета и независимую
safety-автоматику.

- `ESP32-S3-WROOM-1U-N16R8` — UI, display, storage, audio, Wi‑Fi/BLE.
- `ESP32-C5-WROOM-1U-N8R8` — Wi‑Fi 2,4/5 ГГц, IEEE 802.15.4 и IR.
- `SC1512-A4` / RP2354B — 3× nRF24, Sub‑GHz, voice и Cap Bus.
- `MSPM0C1106SDGS20R` №1 — независимый допуск батарейного пакета.
- `MSPM0C1106SDGS20R` №2 — watchdog, thermal supervision и TX leases.

Неиспользуемые интерфейсы аппаратно отключаются и переводятся в проверяемое
тихое состояние. Подробности — в [аппаратной архитектуре](docs/hardware.ru.md)
и [описании уровней безопасности](docs/safety.ru.md).

---

## Макет целевого устройства

Все виды ниже строятся одним генератором из реальных габаритов выбранных MPN
и общей системы координат. Надписи вне компонентов на внешних сторонах —
будущая шелкография; внутренние стороны шелкографии не содержат.

### Внешние стороны

Главный вид открывает страницу; ниже — детальные виды сервисных,
внутренних и торцевых зон.

### Прошивка и восстановление

![Внешний сервисный доступ Leshy2](docs/images/service-access.svg?layout=3)

### Серийная навигация и сменный дисплей

![Серийный блок навигации Leshy2](docs/images/navigation-cluster.svg?layout=1)

![Сменный переходник дисплея Leshy2](docs/images/display-adapter.svg?layout=1)

### Внутренние стороны бутерброда

![Внутренние стороны плат Leshy2](docs/images/internal-board-layout.svg?layout=18)

### Вид от антенного торца

![Вид Leshy2 сверху со стороны антенного торца](docs/images/top-edge-view.svg?layout=5)

### Поперечные разрезы

![Разрезы бутерброда Leshy2](docs/images/sandwich-section.svg?layout=11)

---

## Роадмап и текущая позиция

Роадмап остаётся на стартовой странице вплоть до передачи в печать/на фабрику и явной передачи производственных
файлов в печать. [Полная версия](docs/roadmap.ru.md) содержит зависимости и
критерии выхода; [результаты этапов](docs/stage-results.ru.md) ведут к
опубликованным чертежам, схемам, контрактам и проверкам.

| Этап | Статус | Результат |
|---|---|---|
| H0 · Требования и функциональная архитектура | ✅ Проведено ревью | [Открыть H0](docs/stage-results.ru.md#h0) |
| H1 · Физический дизайн устройства | ✅ Проведено ревью | [Открыть H1](docs/stage-results.ru.md#h1) |
| H2 · Production ECAD-схема | ✅ Проведено ревью и принято | [Результаты H2](docs/stage-results.ru.md#h2) |
| H3 · Виртуальная электрическая проверка | ✅ Проведено ревью и принято | [Итоговый отчёт H3](docs/h3-acceptance.ru.md) |
| H4 · Объединённый pre-layout gate | ✅ [Проведено ревью](docs/h4-prelayout-gate-report.ru.md) | механика, ECAD, H3 и firmware F3 согласованы |
| **H5 · Evidence компонентов** | **▶️ Сейчас: поиск до закупки** | [Состав H5](docs/stage-results.ru.md#h5) |
| H6 · PCB placement и routing | 🔒 Ожидает H5 | [План H6](docs/stage-results.ru.md#h6) |
| H7 · Печать прототипа и bring-up | 🔒 Ожидает H6 и одобрение заказа | [План H7](docs/stage-results.ru.md#h7) |
| H8 · Физическая квалификация | 🔒 Ожидает H7 | [План H8](docs/stage-results.ru.md#h8) |
| H9 · Производственный release | 🔒 Ожидает H8 и firmware F11 | [План H9](docs/stage-results.ru.md#h9) |

Каждая завершённая глобальная фаза `H*` получает отдельный понятный итоговый
отчёт, связанный с этой таблицей. Внутренние подэтапы обновляют точный маркер,
но не создают отдельные глобальные отчёты.

**Железо находится на H5.0.3.** [Единая корзина](docs/component-sample-basket.ru.md)
покрывает все девять residuals и 14 mechanical gates: 32 точные article line и
11 измерительных контрактов. JLCPCB Standard PCBA теперь
[неэксклюзивный производственный ориентир](docs/manufacturing-platform.ru.md):
нормализованный compact BOM сопоставил 176 строк из 209, все 1019 установок
распознаны, а exact-поиск разрешил все 33 outlier. Итоговая карта доступности:
`J0=147`, `J1=0`, `J2=45`, `J3=12`, `J4=5`; семантических подмен MPN и замен
компонентов нет. Открыта только квалифицированная цена exact `SA518`.
Приложение JLCAPI включено, credential хранится вне репозитория, а право Parts
ещё проходит ревью JLCPCB. Физические evidence, PCB layout, quote/reservation и
любые заказы не разрешены.

<details open>
<summary><strong>Текущее сокращение evidence H5 — точная детальная позиция</strong></summary>

<!-- current-substep: H5.0.3 -->

**Точный маркер: `H5.0.3`** — корзина, измерения и все 209
[маршрутов доступности JLCPCB](docs/manufacturing-platform.ru.md) опубликованы.
Read-only интеграция Parts подготовлена, но ожидает ревью права со стороны
JLCPCB. Получить одну квалифицированную цену exact `NiceRF SA518` без заказа,
затем опубликовать точную стоимость корзины для отдельного решения о закупке
образцов. Quote/reservation и закупка не разрешены.

- ✅ `H1.8` — полный физический дизайн принят 23 августа 2026 года.
- ✅ `H2.0.1` — проверен полный реестр из 1 048 схемных строк.
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
  - ✅ `H2.3.7` — `RF_32_SUBGHZ_VOICE`: 116 компонентов, 363 физических
    контакта, независимые CC1101/SA518 power, control и RF-тракты; проведено ревью.
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
- ✅ `H2.6` — [native ERC и все 191 намеренных NC проведены ревью](docs/erc-review.ru.md):
  четыре проекта дают ноль native errors/warnings, у каждого NC есть физический
  pin, точный marker и письменное обоснование.
- ✅ `H2.7` — [H1, физические контакты, nets, M1 и firmware F2 сверены](docs/hwfw-reconciliation.ru.md):
  1 046 электрических identities, 268 root nets, 80 контактов M1 и 130
  controller allocations не имеют оставшихся несоответствий.
- ✅ **`H2.8` — проведено ревью:** формальная финальная пользовательская приёмка перед H3.
  - ✅ `H2.8.1` — [пакет приёмки и deferred gates подготовлены](docs/h2-acceptance.ru.md).
  - ✅ `H2.8.2` — принято пользователем 24 августа 2026 года на hardware
    `25d9ee2` / firmware `900bb2b`.
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
  - ✅ `H3.4.4` — [проверены 162 leaf и 27 сквозных digital checks](docs/digital-verification-result.ru.md).
- ✅ **`H3.5` — проведено ревью:** RF feeds, return paths, corridors и coexistence.
  - ✅ `H3.5.1` — [проверены feed/connector/matching/loss ограничения](docs/rf-feed-constraints.ru.md) всех девяти антенных трактов.
  - ✅ `H3.5.2` — [проверены RF corridors, keepouts, reference planes и returns](docs/rf-layout-constraints.ru.md).
  - ✅ `H3.5.3` — [проверены isolation, quiet-state и одновременные 3×nRF24](docs/rf-coexistence.ru.md).
  - ✅ `H3.5.4` — [сведены 125 leaf и 22 сквозных RF checks](docs/rf-verification-result.ru.md).
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
- ✅ `H4.0.1` — evidence firmware F3 прошло ревью и связано с gate.
- ✅ `H4.1` — объединены механика H1, ECAD H2, evidence H3 и firmware F3.
- ✅ `H4.2` — три документальных несоответствия исправлены в источниках и перегенерированы.
- ✅ `H4.3` — [объединённый pre-layout gate проведён](docs/h4-prelayout-gate-report.ru.md).
- ✅ `H5.0.1` — [девять residuals и 14 механических gate’ов связаны](docs/component-evidence-map.ru.md) с точными выбранными identities, недостающими данными и pass rules.
- ✅ `H5.0.2` — [поиск первичных источников и серийных альтернатив проведён](docs/component-source-research.ru.md); два selection gap теперь имеют четыре точных серийных SKU.
- ▶️ **`H5.0.3` — сейчас:** [JLCPCB Standard PCBA выбран неэксклюзивным ориентиром](docs/manufacturing-platform.ru.md); 176/209 строк и все 1019 установок распознаны, все 33 outlier разрешены в `J0`–`J4`, открыта квалифицированная цена exact `SA518`.

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
