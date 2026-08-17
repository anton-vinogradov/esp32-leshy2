# Stage 3 — target product design

- Статус: **Integrated mockup приостановлен DEC-0058; active internal closure**
- Дата: 2026-08-17
- Пререквизит: repeat G2 **Проведено ревью** (`REV-0002AS`)
- Метод: [`FLOW-0001/G3`](../review/architecture/FLOW-0001-product-to-cad-gates.md)
- Working design: [`DEC-0051`](../review/decisions/DEC-0051-principled-pinout-as-working-design.md) /
  [`PIN-0003`](../review/architecture/PIN-0003-g2f-3i-principled-pinout.md)

## Reviewed inputs

- [`PD-0001`](../review/product-design/PD-0001-g3-physical-design-inputs.md) —
  field/control/safety/RF/expansion/service/power physical inputs;
- all base/optional/excluded capability dispositions through `DEC-0040`;
- no archived owner, pin map, board split or enclosure is a target constraint.

## Current artifact

[`LAY-0001`](../review/product-design/LAY-0001-form-factor-candidates.md)
сохраняет три преждевременных same-scope physical experiments:

1. `P1` compact wide — aggressive lower size bound;
2. `P2` balanced portrait — former engineering recommendation;
3. `P3` field-service chassis — RF/service feasibility upper bound.

Они больше не требуют выбора. `DEC-0041` возвращает активную работу к
logical/electrical feasibility, а затем к адаптации legacy `75×150 mm`
two-board clamshell generator. Его геометрия тоже рабочая гипотеза, не
обязательный финальный размер.

## Active prerequisite

`DEM-0001` и `SRC-0002` reviewed. `DEC-0042` создал единый источник; теперь он
содержит три structurally checked maps. `DEC-0044/NIF-0001/REV-0004L` выбрали
`G2F-3I` leading paper map. `PIN-0003/REV-0004V` дают generated principled
pinout diagram и exact pad/net tables; after direct-QSPI GPIO41/42 and accepted
audio arm the current budget честно равен S3 `32/3/1`, C5 `14/6/1`, RP
`48/0/0`, slow `24/0/0` (`DEC-0052`, `DEC-0054/REV-0005D`). Это выполняет необходимый
working-baseline checkpoint `DEC-0041`; технически он разрешил перенос в старый
reproducible mockup, но последующий `DEC-0058` ставит этот перенос на паузу до
`INT-0001/I9`. `DSP-0003/REV-0004Y` теперь сравнивают старый 4-inch
1-bit SPI reference, новый 3.5-inch direct-QSPI class и EVE fallback;
`DEC-0053/REV-0004Z` принимают 3.5-inch portrait `320×480` IPS QSPI+touch
class. `FND-0063/DSP-0005/REV-0005A` устанавливают exact current assembly
candidate `HMX035CTFT-001` и проводят ревью его paper electrical fit;
production ordering/drawing/connector/backlight/optics остаются открыты.
`AUDIO-0001/REV-0005B` likewise instantiate exact `ES8311` QFN-20 digital
contacts; `FND-0065` corrects `CE` to an address strap and P10 to external
`CODEC_PWR_EN`. `DEC-0054` accepts exact selector/buffer/gate/amp devices and
direct GPIO6 `AUDIO_ARM`; passive analog values and HIL remain open.
`FND-0060` remaining exact electrical endpoints. Profiled kit уже принят
`DEC-0055`; exact two-source assemblies и assembled RF HIL (`FND-0058`)
закрываются параллельно. Найденный physical/RF/power/service conflict меняет
рабочую карту через повторное G2F review, а не маскируется внутри макета.

Первый новый physical artifact уже появился: `PHY-0001/REV-0005H` проверяют
на масштабе U214 в заднем поперечном Cardputer-like dock над аккумуляторами.
Paper fit сохраняет base `75×150 mm`, девять верхних SMA и battery-defined
толщину, но явно требует переноса legacy encoder. `IMP-0048/D` принято как
`DEC-0057`. `MEC-0001/FND-0069` переносят работу на exact host receptacle,
rail/screw stack-up и installed-cap hand/GNSS/RF HIL.

По прямому указанию владельца `DEC-0058` останавливает дальнейший integrated
mockup до полного project-level закрытия начинки. `INT-0001` задаёт порядок
`I0…I9`; compute/recovery/service block `I1` получил **«Проведено ревью»** в
`DEC-0059/REV-0005L`: working map использует 1-bit SDIO и сохраняет полный
S3/C5/RP service. `DEC-0061/SAFE-0002/REV-0005O` затем дают safety block `I2`
**«Проведено ревью»**: exact three-domain STOP/gates и восемь evidence paths
внесены в machine source. Следующим активен power block `I3`. Цельный
enclosure/control layout не продолжается до совместного internal self-review.
`PWR-0002/FND-0073/REV-0005P` уже проводят ревью его prerequisites: valid 2S,
4-V voice и switched-branch principles сохранены, но старые BQ25887/no-power-
path, fixed-input-current, pseudo-gauge и obsolete rail sizes отклонены как
target. Владелец принял `IMP-0052/B` как `DEC-0062`: две 18650 остаются
отдельно заменяемыми, но до допуска пары аппаратно проверяются обе ячейки;
переполюсовка, mismatch, извлечение и bounce должны приводить к fail-closed.
`PWR-0003/IMP-0053` теперь выбирают между полным 5-V Type-C/NVDC и USB-PD/
buck-boost charge/power path.

## Downstream boundary

Physical packing/RF/power/service conflicts возвращаются в `G2F`; working pins
могут измениться. Whole-device optimality и только затем atomic target остаются
обязательными. Local exact-part fit checks разрешены как внутренние
feasibility inputs, но не как продолжение mockup. KiCad по-прежнему
заблокирован.
