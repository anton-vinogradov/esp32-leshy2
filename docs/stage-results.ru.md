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

**Статус:** ▶️ сейчас `H1-R2.9`; результат R1 сохранён как evidence, а не как текущая приёмка.

- [Текущее физическое размещение H1-R2.9](h1-r2-physical-layout.ru.md) — новые
  Hub, Airband и корпуса/резервы аналогового FPV в общей системе координат,
  с генерируемыми проверками коллизий, встречного зазора и точного service MMCX.
- [Точный вид установки/service MMCX](images/h1-r2-mmcx-service.svg): исправленная
  привязка к кромке, keepout выводов wave soldering и коридоры стенки/штекера.
- [Машинный аудит размещения H1-R2.9](../hardware/product-design/generated/H1-R2-placement-audit.json).
- [Функциональный тракт аналогового FPV](h1-r2-fpv.ru.md) и его
  [машинный аудит](../hardware/product-design/generated/H1-R2-fpv-audit.json):
  распиновка/питание K331, точный MMCX-тракт, точная антенна TBS и живое
  отклонение недоступных карточек RTC6715/RX5808 как менее рискованных замен.
- [Проверка реализуемости фильтра Airband](h1-airband-filter.ru.md) и её
  [машинный аудит](../hardware/product-design/generated/H1-Airband-filter-audit.json).
- [Rail/thermal-архитектура шести доменов](h1-r2-power-thermal.ru.md) и её
  [машинный аудит](../hardware/product-design/generated/H1-R2-power-thermal-audit.json).

Сохранённые входы R1, которые пересобираются:

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

**Статус:** ⏳ Evidence R1 сохранено; production-схема R2 ждёт закрытия H1-R2.

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
  errors/warnings, все 202 физических NC обоснованы.
- [Полный реестр NC](no-connects.ru.md) — точный symbol, pin и причина для
  каждого намеренно открытого контакта.
- [Сквозная HW/FW-сверка](hwfw-reconciliation.ru.md) — H1, 1 079
  электрических identities, 270 root nets, все контакты M1 и firmware F2 совпадают.
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
  содержит 143 компонента и 473 физических контакта: независимые CC1101,
  SA818S-V и SA818S-U power/control/RF-тракты, 40 интерфейсов и 20 явных NC;
  [машинное ревью](../hardware/ecad/generated/H2-RF32-subghz-voice.json) проходит
  native KiCad. Оба официальных 18-land корпуса остаются received-part gate H5.
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
  содержит 113 компонентов и 421 физический контакт.
  [Машинное ревью](../hardware/ecad/generated/H2-RF50-tx-safety-evidence.json)
  закрывает явные AON supply/bypass, единый RUN/KILL, независимые
  watchdog/latch/reset и шесть каналов физического RF evidence; native KiCad
  проходит с 24 точными намеренными NC.
- [`RF_60_TESTPOINTS_MANUFACTURING`](../hardware/ecad/kicad/LESHY2-RF/RF_60_TESTPOINTS_MANUFACTURING.kicad_sch)
  выводит 51 точную медную площадку 1,0 мм без покупного MPN и BOM-
  строк. [Машинное ревью](../hardware/ecad/generated/H2-RF60-testpoints-manufacturing.json)
  покрывает 13 recovery-путей, 6 RF-evidence каналов, thermal, RUN/FAULT и
  rail references; native KiCad принимает полную RF-иерархию без child stub и
  отложенных fixture labels.

<a id="h3"></a>
## H3 · Виртуальная электрическая проверка

**Статус:** ✅ текущая ревизия проведена ревью и автоматически принята 26 августа 2026 года.

- [Итоговый отчёт H3](h3-acceptance.ru.md) — краткий результат, схема,
  исправления, границы доказанного и переход к H4.
- [Текущая страница виртуальной проверки](virtual-verification.ru.md).
- [Машиночитаемый план](../hardware/verification/h3-verification-plan.json).
- [Freeze принятого H2 и матрица из 16 областей](../hardware/verification/generated/H3-VRF01-input-freeze.json).
- [Реестр параметров и моделей](parameter-model-register.ru.md) — 1 081
  экземпляр, 218 используемых типов и их первичные источники.
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
- [Результат battery sensing и thermal analog](battery-analog-verification.ru.md)
  и [машинное evidence H3.3.4](../hardware/verification/generated/H3-VRF34-battery-analog.json).
- [Сводный результат analog corners](analog-corner-result.ru.md)
  и [машинное evidence H3.3.5](../hardware/verification/generated/H3-VRF35-analog-consolidation.json).
- [Digital levels, reset defaults и no-back-power](digital-levels-verification.ru.md)
  и [машинное evidence H3.4.1](../hardware/verification/generated/H3-VRF41-digital-levels.json).
- [Digital bandwidth, latency и timing](digital-timing-verification.ru.md)
  и [машинное evidence H3.4.2](../hardware/verification/generated/H3-VRF42-digital-timing.json).
- [Loading M1, expansions и service boundaries](boundary-loading-verification.ru.md)
  и [машинное evidence H3.4.3](../hardware/verification/generated/H3-VRF43-boundary-loading.json).
- [Сводный результат digital interfaces](digital-verification-result.ru.md)
  и [машинное evidence H3.4.4](../hardware/verification/generated/H3-VRF44-digital-consolidation.json).
- [Контракты всех десяти RF-трактов](rf-feed-constraints.ru.md) и
  [машинное evidence H3.5.1](../hardware/verification/generated/H3-VRF51-rf-feed-constraints.json).
- [RF corridor, plane и return contracts](rf-layout-constraints.ru.md) и
  [машинное evidence H3.5.2](../hardware/verification/generated/H3-VRF52-rf-layout-constraints.json).
- [One-group isolation, quiet state и полные 3×nRF24](rf-coexistence.ru.md) и
  [машинное evidence H3.5.3](../hardware/verification/generated/H3-VRF53-rf-coexistence.json).
- [Сводный результат RF-проверки](rf-verification-result.ru.md) и
  [машинное evidence H3.5.4](../hardware/verification/generated/H3-VRF54-rf-consolidation.json).

`H3.0.1–H3.0.3` проведены ревью: входы, параметры и десять единых
pass/fail-правил заморожены. `H3.1` проведено ревью: 2 032 полных состояния и
200 rail-профилей проходят без незакрытых findings после исправления одного
порога eFuse. `H3.2` проведено ревью: power transitions и safety-loop проходят,
две source-ошибки исправлены. `H3.3.1` проведено ревью после исправления ещё
двух source-ошибок; `H3.3.2` — после четырёх исправлений аудиотракта.
`H3.3.3` проверено после четырёх исправлений IR-источников, `H3.3.4` — после
четырёх battery-analog исправлений. `H3.3.5` закрывает 156 leaf и 22 сводных
checks. `H3.4.1` закрывает digital levels/defaults 82 машинными checks,
`H3.4.2` закрывает bandwidth/latency/timing 40 checks, `H3.4.3` закрывает
loading M1, expansions и service boundaries 49 checks. `H3.4.4` закрывает фазу
27 сквозными checks поверх всех 171 leaf checks. `H3.5.1` закрывает 75 checks
feed/connectors/matching/loss всех десяти портов. `H3.5.2` закрывает 23 checks
corridors, keepouts, planes и returns. `H3.5.3` закрывает 30 checks one-group,
quiet-state и полных 3×nRF24. `H3.5.4` закрывает фазу 22 сквозными checks поверх
128 leaf checks. В `H3.6.1` [тепловая модель](thermal-model.ru.md) проведена
ревью 21 check; [проверка единичных отказов](single-fault-review.ru.md) закрывает 30 сценариев и 25 checks;
[длительная работа и self-test](unattended-operation.ru.md) закрыты 24 checks без обещаний времени работы.
[Сведение H3.6](thermal-fault-result.ru.md) закрывает 70 leaf и 24 сквозных
checks. [H3.7.1](h3-crosscheck.ru.md) соединяет каждое требование, artifact,
H2 instance и root net. [H3.7.2](physical-evidence-register.ru.md) назначает
все 85 физических строк H5/H6/H8. [Пакет приёмки H3](h3-acceptance.ru.md)
фиксирует принятый baseline и сохраняет каждый физический остаток.

<a id="h4"></a>
## H4 · Объединённый pre-layout gate

**Статус:** ✅ текущая dual-SA818S ревизия проведена ревью 26 августа 2026 года.

Ревью объединяет механику, production ECAD, пересчитанные electrical evidence и
target-visible firmware contracts. Проверенный
[итог firmware F3](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/f3-boot-memory-emulation-report.ru.md)
даёт точное S3 QEMU execution, воспроизводимые artifacts пяти targets и
названные физические gates для targets без точного эмулятора.

[Понятный итог H4](h4-prelayout-gate-report.ru.md) и
[`H4-PLG13`](../hardware/verification/generated/H4-PLG13-acceptance-package.json)
фиксируют 33 чистые объединённые проверки по новым hashes H2/H3. Все 85 физических
residuals сохраняют владельцев H5/H6/H8; закупка, PCB layout и fabrication не разрешены.

<a id="h5"></a>
## H5 · Образцы компонентов

**Статус:** ▶️ сейчас `H5.0.3-R1`. Обновлённые [карта residuals](component-evidence-map.ru.md)
и [ревью источников](component-source-research.ru.md) связывают все девять H5
residuals и 14 механических gates с 210-строчным dual-SA818S BOM.
[Неустранимая корзина](component-sample-basket.ru.md) содержит 33 строки на
`$286.43`, а [карта площадки](manufacturing-platform.ru.md) назначает всем 210
строкам BOM / 1052 установкам точные маршруты без замен. Закупка не разрешена.

Текущий [машинный план](../hardware/verification/h5-component-evidence-plan.json)
фиксирует `H5.0.1-R1` и `H5.0.2-R1` как проведённые и прежние SA518-артефакты как отменённые. Новое evidence должно покрыть обе
identity SA818S, общий land pattern, два независимых RF-тракта и
qualified-pending UHF alternate SA818S-CE. Текущая
[страница PCBA-площадки](manufacturing-platform.ru.md) сохраняет JLCPCB Standard
как неэксклюзивный ориентир. Прежний capture из 209 строк используется только
для 208 неизменившихся identity; exact U/V-страницы завершают текущую карту 210
строк. Все маршруты назначены, семантических подмен MPN и замен компонентов нет.
Частичный ответ JLCPCB от 26 августа подтверждает для exact SA818S-V MOQ 1 и
типичные 8–15 рабочих дней pre-order и условную post-order цену Function Test.
Аккумуляторы — пользовательский `J5-U`, вне поставки и supplier-gates. Ответ не
закрывает реальную схему с двумя designator U/V,
большинству J4-F/J4-P и exact-MPN control. Fail-closed
[`H5-EVR07`](../hardware/verification/generated/H5-EVR07-supplier-response-gate.json)
фиксирует 16 полей без ответа и ноль отказов в актуальном supplier-scope, не
разрешая заказ. Отказ JLCPCB работать с аккумуляторами относится к исключённому
из поставки пользовательскому `J5-U` и потому не является отказом по устройству.
[Уточнение](../hardware/procurement/H5.0.3-R1-jlcpcb-clarification-reply.md)
подготовлено, но не отправлено. JLCAPI app/key готовы вне Git, но право Parts
остаётся отклонённым. [Поддержка ответила](../hardware/procurement/H5.0.3-R1-parts-api-support-inquiry.md),
что у нового аккаунта нет истории заказов, при этом автор ответа не входит в
API review team и не назвал порог одобрения. Повторная заявка не отправлена;
пока действует ручной evidence-путь.
[`H5-EVR08`](../hardware/verification/generated/H5-EVR08-fallback-factory-readiness.json)
сохраняет PCBWay как неотправленный первый резерв полной сборки, а Seeed — как
второй источник PCBA, поэтому отрицательный ответ JLCPCB не перезапускает фазу.
Quote/reservation и закупка не разрешены. Это не production order.

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
