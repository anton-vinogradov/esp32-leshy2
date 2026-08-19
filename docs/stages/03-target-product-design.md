# Stage 3 — target product design

- Статус: **G3 active; G3-0001 geometry re-entry проведено ревью**
- Дата: 2026-08-19
- Пререквизит: repeat G2 and I1…I9 working-candidate paper scopes **Проведено ревью**
- Метод: [`FLOW-0001/G3`](../review/architecture/FLOW-0001-product-to-cad-gates.md)
- Working design: [`DEC-0051`](../review/decisions/DEC-0051-principled-pinout-as-working-design.md) /
  [`PIN-0003`](../review/architecture/PIN-0003-g2f-3i-principled-pinout.md)

## Reviewed inputs

- [`PD-0001`](../review/product-design/PD-0001-g3-physical-design-inputs.md) —
  field/control/safety/RF/expansion/service/power physical inputs;
- all base/optional/excluded capability dispositions through `DEC-0040`;
- no archived owner, pin map, board split or enclosure is a target constraint.

## Current artifact

[`G3-0001`](../review/product-design/G3-0001-current-clamshell-reentry.md)
is the active reproducible starting projection. It adapts the reviewed legacy
`75×150-mm` clamshell geometry to current MPNs, controls, board locality,
nine SMA identities, exact battery family and rear U214 envelope. Its
geometry-reentry checkpoint has **«Проведено ревью»**; G3 itself remains
active and the projection is not a final board split or enclosure.

[`LAY-0001`](../review/product-design/LAY-0001-form-factor-candidates.md)
сохраняет три преждевременных same-scope physical experiments:

1. `P1` compact wide — aggressive lower size bound;
2. `P2` balanced portrait — former engineering recommendation;
3. `P3` field-service chassis — RF/service feasibility upper bound.

Они больше не требуют выбора. `DEC-0041` возвращает активную работу к
logical/electrical feasibility, а затем к адаптации legacy `75×150 mm`
two-board clamshell generator. Его геометрия тоже рабочая гипотеза, не
обязательный финальный размер.

## Completed prerequisite and current G3 entry

`DEM-0001` и `SRC-0002` reviewed. `DEC-0042` создал единый источник; теперь он
содержит три structurally checked maps. `DEC-0044/NIF-0001/REV-0004L` выбрали
`G2F-3I` leading paper map. `PIN-0003/REV-0004V` дают generated principled
pinout diagram и exact pad/net tables; after direct-QSPI GPIO41/42, accepted
audio arm and `DEC-0086` local-control correction the current budget честно
равен S3 `33/3/0`, C5 `14/6/1`, RP `48/0/0`, main slow `24/0/0` и UI matrix
`7/1/0`. Это выполняет необходимый
working-baseline checkpoint `DEC-0041`; `DEC-0058` поставил перенос на паузу до
`INT-0001/I9`, а `I9-0001/REV-0005CD` затем провели joint review и возобновили
G3. `DSP-0003/REV-0004Y` сравнивают старый 4-inch
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

После прохождения I9 `FND-0117/G3-0001/REV-0005CE` исправляют stale legacy
projection и создают active current generator. Working locality держит S3+C5
и их UI/display/audio/IR endpoints на UI/control half, а RP+3×nRF/CC/voice,
U214 и power responsibility — на RF/power half. Все owners и nine-SMA
identities остаются machine-derived; physical split пока reopenable.

По прямому указанию владельца `DEC-0058` останавливает дальнейший integrated
mockup до полного project-level закрытия начинки. `INT-0001` задаёт порядок
`I0…I9`; compute/recovery/service block `I1` получил **«Проведено ревью»** в
`DEC-0059/REV-0005L`: working map использует 1-bit SDIO и сохраняет полный
S3/C5/RP service. `DEC-0061/SAFE-0002/REV-0005O` затем дают safety block `I2`
**«Проведено ревью»**: exact three-domain STOP/gates и восемь evidence paths
внесены в machine source. Следующим активен power block `I3`. Цельный
enclosure/control layout не продолжается до совместного internal self-review.
`FND-0090/UI-0001/DEC-0086/REV-0005AQ` теперь также закрывают paper inventory
и principled pin fit локальных controls: D-pad/OK, BACK, OPT, F1, F2 и encoder
push остаются в матрице 4x3, A/B энкодера идут напрямую в PCNT0, PTT остаётся
прямым RP input, а STOP/RE-ARM — независимым AON hardware. Exact switch
mechanics и HIL остаются активными I4 gates. `DEC-0088/DSP-0007` later close
exact ST77922 address/active-low IRQ on paper; specimen readback/IRQ/reset HIL
remains. Это не разрешает KiCad и не возобновляет integrated mockup раньше
полного закрытия начинки.
`PWR-0002/FND-0073/REV-0005P` уже проводят ревью его prerequisites: 4-V voice,
load envelope и switched-branch principles сохранены, но старые BQ25887/no-power-
path, fixed-input-current, pseudo-gauge и obsolete rail sizes отклонены как
target. Владелец принял `IMP-0052/B` как `DEC-0062`: два 18650 slots остаются
отдельно заменяемыми, а переполюсовка, mismatch, извлечение и bounce должны
приводить к fail-closed. `DEC-0063/PWR-0004` уже принимают exact sink-only
USB-PD frontend. `DEC-0064/PWR-0006` сравнивают electrical series versus
controlled-1S topology, а `DEC-0065` принимает supervised 2S; текущий exact
manager принят в `DEC-0066`. `PWR-0007/FND-0077/REV-0005W` выявляют
linear-prequal gate; `DEC-0067/REV-0005X` принимают отсутствие in-device
recovery и exact active FET/fuse/NTC/shunt/hold/supply-isolation packages.
`PWR-0016/DEC-0077/REV-0005AH` дополнительно выбирают exact polarized
`Keystone 1048P`, qualified protected-button-top compatibility, четыре
независимых slot contacts и coupling role каждого из трёх NTC.
`PWR-0018/DEC-0079/REV-0005AJ` затем фиксируют два exact
`XTAR 18650 4000mAh`, 28,8 Вт·ч на пару и 2-А charge ceiling. Документы
сертификации, specimen fit, door/thermal-stack и HIL остаются downstream gates.
`PWR-0008/DEC-0068/REV-0005Y` затем закрывают active rail topology и exact
AON/3.3/4.0/5.0-V converter, inductor, load-switch и external-eFuse first
targets; `DEC-0069/REV-0005Z` исправляют external eFuse на latch-off exact
suffix. `PWR-0009…0011/DEC-0070…0072` затем закрывают optional-PG
qualification, exact eFuse passives и 24 exact converter
energy/configuration/feedback parts; `PWR-0012/DEC-0073/REV-0005AD` first
close direct AON EN and the original nine exact EN/PG/fault resistors. `FND-0084/PWR-0019/
DEC-0080/REV-0005AK` then replace the hidden sequencer with exact AON-PG/MR,
SENSE/CT/POR and main-EN wiring. The amended profile has ten physical
resistor positions, about 3.0-V main release and no new unique MPN or GPIO.
`FND-0085/PWR-0020/DEC-0081/REV-0005AL` then add exact independent post-buck
containment to AON/main/voice, protected-side PG and a reviewed single-fault/
paper-loss profile for about USD 2.4 per board without GPIO or function loss.
`FND-0086/PWR-0021/DEC-0082/REV-0005AM` then consolidate the complete source,
heat and fault ledger and give the I3 paper electrical scope **«Проведено
ревью»**. Certification is an I8 procurement gate; exact-cell lot,
source-transition, rail, destructive-fault and thermal evidence remain named
prototype HIL. I4 paper work is now active without claiming those measurements.
`FND-0087/USB-0001/DEC-0083/REV-0005AN` далее закрывают первый I4 endpoint:
exact `DX07S016JA1R1500`, `TPD4S201RUKR`, protected CC/USB2 routes и
пересчитанные exact 220-pF CC shunts полностью внесены в machine source без
нового GPIO. Placement/cutout, total CC, USB Full-Speed RC/SI, ESD и
short-to-VBUS HIL остаются открыты; integrated mockup не возобновляется.
`FND-0088/DSP-0006/DEC-0084/REV-0005AO` затем закрывают display paper
electrical endpoint: exact first ZIF candidate, protected-main logic supply,
reset-low defaults и отдельно latch-protected PWM backlight теперь являются
машинными physical instances. Real-tail mate/orientation, standalone panel
procurement и shared-SPI/touch/current/thermal HIL остаются открыты;
integrated mockup и KiCad по-прежнему не возобновляются.
`FND-0089/STO-0001/DEC-0085/REV-0005AP` затем закрывают microSD paper
electrical endpoint: exact switched rail, card-side Ioff isolation,
CS-gated DAT0/MISO return, mandatory pulls, source damping, full socket ESD и
always-readable detect становятся machine instances без расхода GPIO.
Размещение/доступ к карте, media/endurance, shared-bus throughput, hot-remove,
ESD/short/brownout и filesystem-recovery HIL остаются открыты; mockup и KiCad
не возобновляются.
`PWR-0013/FND-0078/DEC-0074/REV-0005AE` закрывают exact 10-Ом diagnostic,
независимый non-retriggerable предел `<=50 мс` и exact PA25/PA26
divider/filter frontends, исправляя запрещённую injection-current привязку
PA24 без изменения бюджета `12/3/3`. `PWR-0017/FND-0082/DEC-0078/REV-0005AI`
исправляют физические контакты TPUL, добавляют независимый аппаратный cooldown
`>=350 мс` и две параллельные 20-Ом/2-Вт ветви нагрузки без нового GPIO или
active device. Далее закрываются exact-cell droop thresholds, lot/hot-copper
HIL, destructive post-buck fault injection и measured thermal consolidation
как физические qualification gates, а не как бумажные prerequisites I4.

## Downstream boundary

Physical packing/RF/power/service conflicts возвращаются в `G2F`; working pins
могут измениться. Whole-device optimality и только затем atomic target остаются
обязательными. Active `G3-0001` generator развивает physical mockup, но не
заменяет G4 alternatives, G5 optimality, G6 co-design или G7 atomic acceptance.
KiCad по-прежнему заблокирован.
