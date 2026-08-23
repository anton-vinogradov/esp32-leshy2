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

**Статус:** ▶️ сейчас, точный маркер `H2.3.5`.

- [Публичная страница схем](schematics.ru.md) — принципиальные диаграммы и
  ссылки на текущие native KiCad-листы.
- [План H2](../hardware/ecad/h2-schematic-plan.json) — точный состав и статусы
  подзадач.
- [Полный instance ledger](../hardware/ecad/generated/H2-instance-ledger.json).
- [HW↔FW export](../hardware/ecad/generated/H2-hwfw-contract.json).
- Проведено ревью всей UI/control PCB и первых четырёх RF/power-листов;
  выполняется точное ядро/USB/recovery RP2354B.

<a id="h3"></a>
## H3 · Виртуальная электрическая проверка

**Статус:** ⏳ ожидает H2.

Результатом станут worst-case DC budget, startup/shutdown и handover simulation,
fault tree, thermal/power/transient evidence, digital timing/levels и RF
pre-layout constraints. До закрытия виртуально проверяемого blocker переход к
layout запрещён.

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
