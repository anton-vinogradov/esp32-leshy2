# ⭐ Результаты этапов Leshy2

[На главную](../README.ru.md) · [Полный роадмап](roadmap.ru.md) · [English](stage-results.md)

Здесь собраны не обсуждения и не история решений, а актуальные результаты
каждого этапа. Закрытый этап получает статус «проведено ревью» только после
выполнения своего критерия выхода.

<a id="h0"></a>
## ⭐ H0 · Требования и функциональная архитектура

**Статус:** ✅ проведено ревью.

- [Аппаратная архитектура](hardware.ru.md) — возможности, владельцы и границы.
- [Точная распиновка](pinout.ru.md) — GPIO, периферия, направления и nets.
- [Карта M1](interconnect.ru.md) — физическое пересечение двух плат.
- [HW↔FW integration contract](../hardware/architecture/target-integration-contract.json).
- [Машинный целевой BOM](../hardware/architecture/generated/G2F-3I-target-bom.csv).

<a id="h1"></a>
## ⭐ H1 · Физический дизайн устройства

**Статус:** ✅ проведено ревью.

- [Внешние стороны](images/current-clamshell.svg),
  [сервисный доступ](images/service-access.svg) и
  [зеркальные внутренние стороны](images/internal-board-layout.svg).
- [Настоящий вид от антенного торца](images/top-edge-view.svg) и
  [разрезы бутерброда](images/sandwich-section.svg).
- [Серийная навигация](images/navigation-cluster.svg) и
  [сменный display-adapter](images/display-adapter.svg).
- [Реестр физических первоисточников](physical-source-register.ru.md).
- [Machine acceptance package](../hardware/product-design/generated/H1-cross-view-acceptance.json).

<a id="h2"></a>
## ⭐ H2 · Production ECAD-схема

**Статус:** ✅ проведено ревью и принято пользователем 24 августа 2026 года.

- [Публичная страница схем](schematics.ru.md) — принципиальные диаграммы и
  ссылки на текущие native KiCad-листы.
- [План H2](../hardware/ecad/h2-schematic-plan.json) — точный состав и статусы
  подзадач.
- [Полный instance ledger](../hardware/ecad/generated/H2-instance-ledger.json).
- [HW↔FW export](../hardware/ecad/generated/H2-hwfw-contract.json).
- [Архитектура питания](power-architecture.ru.md) — итоговые источники,
  аккумуляторный тракт и все формируемые шины; H2.5.1 проведено ревью по
  полной KiCad-netlist.
- [Прошивка и восстановление](service-recovery.ru.md) — независимые USB,
  DBG10, SWD/UART и fixture-пути; H2.5.2 проведено ревью по 61 цепи.
- [Изоляция внешних интерфейсов](interface-isolation.ru.md) — три USB,
  межплатная граница и две expansion-ветви; H2.5.3 проведено ревью.
- [Тихое состояние](quiet-state.ru.md) — все 13 неактивных групп и их
  аппаратные границы; H2.5.4 проведено ревью.
- [Аварийное отключение](fault-shutdown.ru.md) — watchdog, три thermal-зоны,
  девять TX-evidence каналов и аппаратный latch; H2.5.5 проведено ревью.
- [Итог safety-ревью](safety-review.ru.md) — H2.5 закрыт, пять findings
  исправлены, открытых paper/ECAD findings нет.
- [ERC и NC-ревью](erc-review.ru.md) — все четыре проекта дают ноль native
  errors/warnings, все 189 физических NC обоснованы.
- [Полный реестр NC](no-connects.ru.md) — точный symbol, pin и причина для
  каждого намеренно открытого контакта.
- [Сквозная HW/FW-сверка](hwfw-reconciliation.ru.md) — H1, 1 026
  электрических identities, 266 root nets, все контакты M1 и firmware F2 совпадают.
- [Пакет приёмки H2](h2-acceptance.ru.md) — завершённая область, принятые
  baseline commits и все deferred H3/F3/H5/H6/H8 gates.
- Проведено ревью всей UI/control PCB, всех двенадцати RF/power child-листов,
  пассивного display-adapter и всех листов LoRa Cap. Закрыты quiet state,
  fault shutdown, native ERC/NC и сквозная H1/M1/F2-сверка. H2.8.2 фиксирует
  явную пользовательскую приёмку.
- [`RF_30_RP2354_CORE_SERVICE`](../hardware/ecad/kicad/LESHY2-RF/RF_30_RP2354_CORE_SERVICE.kicad_sch)
  содержит 48 точных компонентов, все 81 контакта корпуса SC1512-A4,
  референсные цепи core regulator и кварца 12 МГц, native USB/recovery и 13
  явных NC; [машинное ревью](../hardware/ecad/generated/H2-RF30-rp2354-core-service.json)
  проходит native KiCad.
- [`RF_31_NRF24_X3`](../hardware/ecad/kicad/LESHY2-RF/RF_31_NRF24_X3.kicad_sch)
  содержит 105 точных компонентов ledger плюс три границы заводских IPEX, 311
  физических контактов, три независимых PIO SPI- и RF-тракта и два явных NC;
  [машинное ревью](../hardware/ecad/generated/H2-RF31-nrf24-x3.json) проходит
  native KiCad.
- [`RF_32_SUBGHZ_VOICE`](../hardware/ecad/kicad/LESHY2-RF/RF_32_SUBGHZ_VOICE.kicad_sch)
  содержит 116 компонентов и 363 физических контакта: независимые CC1101 data
  и SA518 voice power/control/RF-тракты, 32 интерфейса и 11 явных NC;
  [машинное ревью](../hardware/ecad/generated/H2-RF32-subghz-voice.json) проходит
  native KiCad. Посадка SA518 остаётся честно ограниченным H5 land-fit gate.
- [`RF_34_U214_M5_EXT`](../hardware/ecad/kicad/LESHY2-RF/RF_34_U214_M5_EXT.kicad_sch)
  содержит 53 символа, 52 устанавливаемых компонента, 228 контактов и 27
  интерфейсов. [Машинное ревью](../hardware/ecad/generated/H2-RF34-u214-m5-ext.json)
  подтверждает отдельные защищённые тракты U214 и native M5 Unit; сам U214 —
  внешнее стыкуемое изделие, а не фиктивный компонент платы.
- [`RF_35_REAR_CONTROLS`](../hardware/ecad/kicad/LESHY2-RF/RF_35_REAR_CONTROLS.kicad_sch)
  содержит семь устанавливаемых компонентов и 36 контактов.
  [Машинное ревью](../hardware/ecad/generated/H2-RF35-rear-controls.json)
  закрывает независимые encoder A/B/push и PTT с локальной ESD-защитой;
  ручка остаётся внешней механической деталью.
- [`RF_36_AUDIO_IO_AMP`](../hardware/ecad/kicad/LESHY2-RF/RF_36_AUDIO_IO_AMP.kicad_sch)
  содержит 14 символов и 34 контакта.
  [Машинное ревью](../hardware/ecad/generated/H2-RF36-audio-io-amp.json)
  закрывает точный направленный вниз микрофон, исправленный компактный
  U-DFN-усилитель, reset-low shutdown и два независимых floating-BTL выхода.
- [`RF_40_INTERBOARD_M1`](../hardware/ecad/kicad/LESHY2-RF/RF_40_INTERBOARD_M1.kicad_sch)
  содержит точный 80-контактный receptacle и 51 hierarchy interface.
  [Машинное ревью](../hardware/ecad/generated/H2-RF40-interboard-m1.json)
  доказывает построчное равенство с UI-side M1, включая все повторные rails и
  returns, без reserve и NC.
- [`RF_50_TX_SAFETY_EVIDENCE`](../hardware/ecad/kicad/LESHY2-RF/RF_50_TX_SAFETY_EVIDENCE.kicad_sch)
  содержит 97 компонентов и 369 физических контактов.
  [Машинное ревью](../hardware/ecad/generated/H2-RF50-tx-safety-evidence.json)
  закрывает явные AON supply/bypass, единый RUN/KILL, независимые
  watchdog/latch/reset и пять каналов физического RF evidence; native KiCad
  проходит с 22 точными намеренными NC.
- [`RF_60_TESTPOINTS_MANUFACTURING`](../hardware/ecad/kicad/LESHY2-RF/RF_60_TESTPOINTS_MANUFACTURING.kicad_sch)
  выводит 52 точных медных площадки 1,0 мм без покупного MPN и BOM-
  строк. [Машинное ревью](../hardware/ecad/generated/H2-RF60-testpoints-manufacturing.json)
  покрывает 13 recovery-путей, 6 RF-evidence каналов, thermal, RUN/FAULT и
  rail references; native KiCad принимает полную RF-иерархию без child stub и
  отложенных fixture labels.

<a id="h3"></a>
## H3 · Виртуальная электрическая проверка

**Статус:** ▶️ сейчас, точный маркер `H3.3.4`.

- [Текущая страница виртуальной проверки](virtual-verification.ru.md).
- [Машиночитаемый план](../hardware/verification/h3-verification-plan.json).
- [Freeze принятого H2 и матрица из 16 областей](../hardware/verification/generated/H3-VRF01-input-freeze.json).
- [Реестр параметров и моделей](parameter-model-register.ru.md) — 1 035
  экземпляра, 217 используемых типов и их первичные источники.
- [Машинный реестр H3.0.2](../hardware/verification/generated/H3-VRF02-parameter-inventory.json).
- [Методы проверки](verification-methods.ru.md) и
  [машинный контракт H3.0.3](../hardware/verification/generated/H3-VRF03-method-contract.json).
- [Состояния питания](power-state-register.ru.md) и
  [машинный реестр H3.1.1](../hardware/verification/generated/H3-VRF11-power-state-register.json).
- [Бюджет шин](dc-power-budget.ru.md), [источники и заряд](source-charge-budget.ru.md)
  и [проверенный результат H3.1](dc-verification-result.ru.md).
- [Startup/KILL](power-transition-startup.ru.md), [handover](power-handover.ru.md),
  [inrush/load-step](inrush-load-step.ru.md), [watchdog/fault UI](watchdog-fault-display.ru.md)
  и [проверенный результат H3.2](power-transition-result.ru.md).
- [Результат проверки питания дисплея, подсветки и direct-QSPI](display-electrical-verification.ru.md)
  и [машинное evidence H3.3.1](../hardware/verification/generated/H3-VRF31-display.json).
- [Результат проверки аудиотракта](audio-electrical-verification.ru.md)
  и [машинное evidence H3.3.2](../hardware/verification/generated/H3-VRF32-audio.json).
- [Результат электрической проверки IR](ir-electrical-verification.ru.md)
  и [машинное evidence H3.3.3](../hardware/verification/generated/H3-VRF33-ir.json).

`H3.0.1–H3.0.3` проведены ревью: входы, параметры и десять единых
pass/fail-правил заморожены. `H3.1` проведено ревью: 2 032 полных состояния и
200 rail-профилей проходят без незакрытых findings после исправления одного
порога eFuse. `H3.2` проведено ревью: power transitions и safety-loop проходят,
две source-ошибки исправлены. `H3.3.1` проведено ревью после исправления ещё
двух source-ошибок; `H3.3.2` — после четырёх исправлений аудиотракта. В
`H3.3.3` проверено после четырёх исправлений IR-источников. В `H3.3.4`
проверяются battery sensing, thermistors и analog fault thresholds.

<a id="h4"></a>
## H4 · Объединённый pre-layout gate

**Статус:** 🔒 ожидает H1–H3 и firmware F3.

Единое ревью механики, production ECAD, виртуальных electrical evidence и
target-visible firmware contracts. F3 требует сборки образов всех пяти доменов,
size/rollback gates, S3 QEMU и portable/host-моделей для targets без точного
эмулятора.

<a id="h5"></a>
## H5 · Образцы компонентов

**Статус:** 🔒 ожидает H4 и отдельного одобрения стоимости.

Минимальная закупка закрывает только физически неразрешимые по документам
неопределённости: received-part identity, mating, stack-up и реальные размеры.
Это не production basket.

<a id="h6"></a>
## H6 · PCB placement и routing

**Статус:** 🔒 ожидает H5.

Результат — две реальные платы с закрытыми DRC, impedance, return current,
RF isolation, antenna feed, thermal, assembly и manufacturability reviews.

<a id="h7"></a>
## H7 · Печать прототипа и bring-up

**Статус:** 🔒 ожидает H6, уже закрытого через H4 firmware F3 и явного
одобрения заказа.

Да, к этому этапу неполные target-прошивки уже должны быть собраны и прогнаны
в доступных эмуляторах/host-моделях. На H7 появляется первая небольшая партия
плат; выполняются rail, boot, recovery и interface smoke tests. Эмуляция не
заменяет этот bring-up, но печать не должна быть первым запуском кода.

<a id="h8"></a>
## H8 · Физическая квалификация

**Статус:** 🔒 ожидает H7.

HIL, RF, antenna/VNA, coexistence, thermal, power, safety, endurance и полный
`3R/1T2R/2T1R/3T` прогон трёх nRF24.

<a id="h9"></a>
## H9 · Производственный release

**Статус:** 🔒 ожидает H8 и firmware F11.

Воспроизводимый BOM/fab/assembly/fixture/calibration/test package, ноль blocker
и явно связанные release tags железа и прошивки.
