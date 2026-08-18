# Аппаратная часть Leshy2 — текущее состояние проработки

> Снимок: 2026-08-18. Здесь указана доказанная зрелость. Образ готового
> продукта — в [целевом hardware README](../../README.ru.md), software — в
> [целевом firmware README](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md).

- Канонические evidence: [журнал ревью](../review/README.md)
- English version: [current-state.md](current-state.md)
- Исправленная gate chain: [`FLOW-0001`](../review/architecture/FLOW-0001-product-to-cad-gates.md)

## Ход ревью

| Gate | Состояние |
|---|---|
| 0. Review baseline | Проведено ревью |
| 1. Product intent и safety/legal boundaries | Проведено ревью |
| 2. Capabilities, exclusions, concurrency/failure needs | **Повторно проведено ревью**: `REV-0002AS`; competitor delta закрыт |
| 2F. Logical/electrical feasibility | **В работе; current paper baseline reviewed**: `PIN-0003/REV-0004V/0004X` закрывают owners/controllers/exact compute contacts и current QSPI-amended budget; final electrical endpoints, RF/power и HIL открыты |
| 3. Target physical/product design | **Начинается от `DEC-0051/PIN-0003` visible working design**: адаптируется legacy clamshell generator; P1/P2/P3 reference only, конфликты возвращаются в G2F |
| 4–6. Whole-device alternatives, optimality и conceptual co-design | Не начаты; G2F/G3 образуют проверяемый loop |
| 7. Atomic architecture | **Переоткрыта** решением `DEC-0032` |
| 8. Components/BOM | Заблокирован; прежние evidence только candidate/reference |
| 9. Electrical/CAD/firmware architecture | Заблокирован; активного canonical KiCad нет |
| 10–11. PCB, fabrication и bring-up | Не начаты |

Каноническая таблица — [`stages.md`](../review/stages.md).

## Закрытие competitor delta

- `W-EXTRA-11` закрыт: [`DEC-0033/REQ-IBTN-0001`](../review/decisions/DEC-0033-external-m5-ibutton-profile.md)
  принимает внешний пассивный M5-style Port-B iButton adapter без base pad;
- infrastructure закрыт [`DEC-0034/REQ-EXT-0001`](../review/decisions/DEC-0034-m5-first-two-tier-expansion.md): M5-first Unit/Cap плюс отдельный high-throughput class, без native M5-Bus;
- former `W-EXTRA-12` FIDO acceptance удалён из target решением [`DEC-0039`](../review/decisions/DEC-0039-radio-key-scope-correction.md);
- `W-EXTRA-13` закрыт [`DEC-0036`](../review/decisions/DEC-0036-no-product-haptic.md): в продукте нет haptic, мотора, специального профиля или mount;
- `W-EXTRA-14` закрыт [`DEC-0037`](../review/decisions/DEC-0037-optional-external-imu-measurement-pose.md)/[`REQ-IMU-0001`](../review/requirements/REQ-IMU-0001-external-measurement-pose.md);
- `W-EXTRA-15` закрыт [`DEC-0038`](../review/decisions/DEC-0038-phone-assisted-text-no-integrated-keyboard.md): no integrated keyboard, bounded phone-assisted text;
- `W-EXTRA-16` generic High-Speed USB host rejected `DEC-0039`; остаётся только RF-derived transport;
- `W-EXTRA-17` 6 GHz/Wi-Fi 6E полностью отклонён `DEC-0040`; принятые
  автономные 2.4/5 GHz остаются без изменений.

`REV-0002AS` закрывает повторное G2 review. `DEC-0041` вводит активный G2F до
физического макета; `DEC-0042` принимает единый machine-readable источник
exact devices/nets.

## Что остаётся проверенным

- all-in-one автономный field-product, акт о ненападении и модель
  Main/Lab/Controlled Zone;
- консервативные TX defaults, явный выбор максимума, hard STOP без automatic
  re-arm и отдельное actual-TX evidence;
- полный self-review 125 wishlist leaves и правило снижения стоимости без потерь;
- три полнофункциональных nRF24 с любым одновременным PTX/PRX role mix;
- требования обычных Wi-Fi 2.4/5 ГГц, IEEE 802.15.4, native BLE и
  Wi-Fi 2.4/ESP-NOW;
- packet Sub-GHz, broadcast receive, analog voice, audio, IR, внешние
  GNSS/LoRa/NFC, внешний iButton/1-Wire adapter и их safety/evidence boundaries;
- open owner-controlled signed updates и независимые programming/recovery/
  diagnostics каждого в итоге выбранного programmable chip.

Это входы продукта. `G2F-3I/PIN-0003` теперь является reviewed reopenable
working baseline владельцев, шин и compute pins для G3, но не final atomic
architecture. Board count, connectors, exact electrical parts и enclosure не
приняты; physical/RF/power conflict может изменить working pins.

## Завершённое исправление

[`FND-0039`](../review/findings/FND-0039-architecture-frozen-before-product-design.md)
зафиксировал, что прежняя цепочка пропустила target physical design,
whole-product optimality и conceptual placement. Владелец выбрал вариант A в
[`DEC-0032`](../review/decisions/DEC-0032-reopen-product-design-before-cad.md).

Последствия:

- `DEC-0028/PKG-0001/SYN-3A` — historical candidate/reference, а не target;
- C5 revision, compute ownership, pin и three-domain service studies являются
  только условными candidate facts;
- прежняя active C-001…005 KiCad library вместе с CI сохранена в
  [`premature-compute-cad-2026-08-16`](../../drafts/premature-compute-cad-2026-08-16/README.md);
- прерванный до коммита C-006 experiment отмечен как discarded в
  [`premature-service-cad-2026-08-16`](../../drafts/premature-service-cad-2026-08-16/README.md), без ложного обещания воспроизводимого snapshot;
- active [`hardware/kicad`](../../hardware/kicad/README.md) содержит только
  upstream gate, без symbols, schematic или PCB.

`REV-0004H` проверяет это исправление, но не новый product design.

## Текущие активные артефакты

[`DEM-0001`](../review/architecture/DEM-0001-current-semantic-signal-demand.md)
фиксирует все обязательные semantic endpoints без старых owners.
[`SRC-0002`](../review/architecture/SRC-0002-real-device-pin-provenance.md)
запрещает считать вывод без цепочки SoC→package→exact module/device→реальный
pad/header/connector. `DEC-0042/REV-0003Y` добавили проверяемый источник;
[`G2F-pin-ledger`](../review/architecture/generated/G2F-pin-ledger.md) теперь
содержит три consumer, а `G2F-3I` является ведущей paper map. Все проходят
contact/collision/accounting/strap/service checks, но exact nRF, CC RF
implementation, voice/IR и часть control/power всё ещё blockers.
`DSP-0001/REV-0003Z` проверяют три реальные display/touch boundaries и один
microSD socket. `FND-0051` доказывает, что старые 10 full frames/s для ST7796S
и generic 24-pin connector переиспользовать нельзя. `DEC-0043/REV-0004J`
принимают task/dirty-region performance с первым critical/menu response
`≤100 ms` и для прежней shared-U214 карты исправляют quantum с 1 KiB до
256 B. `DSP-0002/REV-0004W` обнаружили `FND-0061`: U214 уже перенесён на
dedicated RP bus, поэтому fixed limit устарел. `DEC-0052/REV-0004X` закрывают
находку: принимают direct QSPI на S3 `GPIO41/42` и measured `≤1 ms` display
occupancy; тогдашний S3 budget стал `31/3/2`. `DSP-0003/REV-0004Y`
показывают, что старый 4-inch ST7796S годится как A0 workload fixture, но не
как QSPI target. `DEC-0053/REV-0004Z` принимают 3.5-inch portrait `320×480`
IPS direct-QSPI capacitive-touch class; `DSP-0004` перечисляет все известные
part numbers. `FND-0063/DSP-0005/REV-0005A` исправляют primary source:
official QDtech schematic раскрывает exact assembly `HMX035CTFT-001`, а его
40-contact paper fit теперь заканчивается в `G2F-3I`. Production
orderability/drawing/lifecycle, connector, backlight, optics и HIL открыты.
`CTL-0001/REV-0004K` обнаружили, что
первые карты закрывали только MCU accounting. Владелец делегировал перебор
компоновки; `DEC-0044` принял `IMP-0037/A`, а `NIF-0001/REV-0004L` проверили
ведущий `G2F-3I`: RP2354B/QFN80, пять независимых radio/accessory SPI paths,
dedicated SDIO S3↔C5, dedicated SPI3 S3↔RP, 23/24 slow endpoints и
изолированный U214 I²C. Единственная high-rate scheduled pair — display+SD на
SPI2 с bounded quantum; radio FIFO/IPC её не ждут. `DEC-0059` затем сужает
C5 SDIO до 1-bit и восстанавливает C5 USB+UART и S3 USB+UART service без
изменения controller independence. Повторная
exact-device проверка обнаружила и исправила crossing реального RP2354B PIO
GPIO-window; PIO data теперь `GPIO30…46`, fixed mux закреплён контрактами, а
capacity закрыта с резервом 7/12 PIO SM и 3/16 DMA. `DEC-0045` принимает одну active top-level
signal group, но определяет `SG-N24` как все три radio одновременно активные в
любом PTX/PRX mix. `DEC-0046/QST-0001` требуют quiet-state всех неиспользуемых
interfaces и отдают RP GPIO15/GPIO23 плюс C5 GPIO4 под group-level power gates.
`DEC-0047` принимает qualified nRF RF envelope. Заказанный второй ESP32-DIV
становится ранним `L0 DIV↔DIV` pre-HIL observer, но не заменяет target
`T1 Leshy2` fixture. `N24M-0001` проверяет реальные `E01-ML01S`,
`E01-ML01IPX` и `E01-2G4M27D`; `DEC-0048` принимает `IMP-0040/A`: все
бортовые antenna endpoints внешние SMA, а три nRF используют три compact
IPEX→SMA paths. `ANT-0001/REV-0004P` проверяют count для S3/C5/nRF/SA518 и
фиксируют `FND-0055`: у exact Si4732 отдельные `FMI` FM/SW и `AMI` AM/LW, а
generic long coax способен нарушить capacitance budget AMI. Поэтому
`DEC-0049/REV-0004Q` закрывают `IMP-0041` вариантом A: приняты 9 labelled SMA
с отдельными `RX-FM/SW` и `RX-AM/LW`; AM/LW требует короткий loop/pod либо
квалифицированный buffered profile. Измеренные envelope points, exact production lots, power parts,
self-desense и target HIL остаются открытыми. Та же exact-device проверка
нашла `FND-0056`: у SA518 rev 1.1 нет dedicated SQ, поэтому maps теперь
резервируют neutral `VOICE_ACTIVITY`, а pin-17 UPDATE остаётся fixture proof
gate. `RFH-0001/REV-0004R` проверили module-to-panel interface: S3/C5 имеют
явный first-generation U.FL/MHF I/AMC boundary, а Ebyte документирует только
generic `IPX`. `FND-0057` исправляет machine source и требует specimen-fit/VNA
gate. `RFH-0002/REV-0004S` отдельно проверяют реальные antenna ecosystems:
RP-SMA типичен для native Wi-Fi, Ebyte/nRF использует standard SMA, а sub-GHz
имеет обе polarity. `DEC-0050/REV-0004T` принимают ограниченный
`2 native-Wi-Fi RP-SMA + 7 standard SMA`, two-source antenna gate и machine
connector/mate map, не выбирая mount/length и не подменяя exact antenna
qualification популярностью разъёма. `FND-0050`
фиксирует nRF24 NRND и
исправляет статус CC1101 на ACTIVE.

`ANT-0002/REV-0004U` провели ревью exact current commercial antenna
candidates. Один dual-band RP-SMA MPN может обслуживать S3/C5, один
standard-SMA MPN — три одинаковых nRF paths, а Taoglas `TI.08.C.0112`
объединяет common 868/915 profiles. При этом no-loss universal 315–915 и
full-range VHF/UHF antenna не подтверждены: CC требует сменных 315/433/868+915,
VOICE — отдельных VHF/UHF, а Si4732 сохраняет whip и loop/pod.
`FND-0058` исправляет прежнее слишком сильное обещание: shortlist проведён
ревью, но two-source production assemblies и target VNA/sensitivity/EIRP/HIL
ещё не закрыты.

`PIN-0003/REV-0004V` теперь дают отдельный generated principled pinout atlas:
owner diagram, каждый MCU GPIO с physical module/package pad, fixed mux,
service/recovery, PIO/DMA budget и все slow routes берутся из одного JSON.
Саморевью обнаружило `FND-0059`: старый `NIF-0001/REV-0004L` показывал
pre-`DEC-0046` budget. После `DEC-0052` и принятого audio `DEC-0054` current
result — S3 `32U/3R/1F`, C5 `14U/6R/1F`, RP `48U/0R/0F`, slow plane
`24U/0R/0F`; regression теперь
проверяет эти числа. SA518 `UPDATE/UART/PD` service и exact Si4732 control/
FMI/AMI contacts также внесены. `FND-0067` нашёл пропущенный ordinary control
RX-audio mux и теперь размещает его на slow P27. `FND-0060` сохраняет видимыми ещё abstract
display/codec/IR/power/STOP/protection endpoints: current paper pinout прошёл
ревью, final electrical schematic — нет.
`DEC-0051` публикует эту reviewed карту в целевом README как принципиальный
working design для G3, сохраняя её reopenable до atomic architecture.

`IMP-0043/A` принято как `DEC-0055`: profiled antenna kit использует общие MPN
только для электрически одинаковых S3/C5 и трёх nRF paths, combined 868/915,
отдельные 315/433, VHF/UHF, FM/SW whip и AM/LW pod. При смене TX profile arm
сбрасывается, unknown/mismatch оставляет TX disabled. Availability повторно
проверяется только при выборе exact MPN.

`MFG-0001` подтверждает, что PCBA и loose antennas можно заказать одним
turnkey/kitting RFQ. `IMP-0047/B` принято как `DEC-0056`: это предпочтительный
первый RFQ, но не жёсткое ограничение фабрики; худший total cost, срок,
quality/test scope или supply risk разрешает раздельную закупку.

`IMP-0044/A` принято как `DEC-0052`: QSPI-first display path на S3 использует
`GPIO41/42` под D2/D3 и `≤1 ms` bus-occupancy contract. BT817/BT818 EVE
остаётся fallback, четвёртый MCU в baseline не добавляется.

`IMP-0045/A` принято как `DEC-0053`: target — 3.5-inch portrait `320×480`
QSPI IPS+touch class; `DLE06235B/ES3C35P` (`ST77922`) — primary HIL,
Waveshare SKU `31137` (`AXS15231B`) — secondary HIL, старый 4-inch ST7796S —
A0 control/fallback. `HMX035CTFT-001` — exact current paper candidate, но ещё
не production-qualified BOM line; остальные неизвестные parts остаются
явными `TBD` в `DSP-0004`.

`AUDIO-0001/REV-0005B` проверяют exact digital/contact fit ES8311. Затем
complete-path review `AUDIO-0002/REV-0005C` исправляет analog assumption:
direct 6-kΩ-class input ES8311 способен нагрузить обычный Si4732 bypass,
PAM8302A уже принимает differential DAC, а SA518 TX требует большого
attenuation. Кроме того, P11/P12 expander могут удерживать старое значение
через S3 reset.

`IMP-0046/A` принято как `DEC-0054`: ES8311 сохраняется с exact
`TLV9061IDBVR` high-Z capture, `TMUX1136DGSR` differential speaker selector,
`TS5A63157DCKR` TX selector и `SN74LVC2G08DCUR` reset-safe gate. Direct S3
GPIO6 теперь `AUDIO_ARM`; passive capture остаётся измеряемой cost-down
option. Machine map и диаграммы показывают итоговый S3 `32U/3R/1F`.

[`AUD-0013`](../review/audits/AUD-0013-legacy-layout-generator-reuse.md)
подтверждает переиспользование старого `75×150 mm` two-board clamshell и его
collision/fold/mezzanine checks после согласования pin map. Старые owners,
onboard LoRa, antenna count и generic nRF dimensions не наследуются.

`FND-0068/REV-0005G` находят следующий physical omission: official U214 имеет
корпус `84×24×15.2 mm`, direct 14-pin dock, собственный RP-SMA и GNSS ceramic
antenna, а legacy 75-mm SVG его вообще не рисует. `PHY-0001/REV-0005H`
проверяют масштабированный задний candidate над аккумуляторами: поперечный
Cardputer-like rail, 4.5-mm overhang по сторонам, сохранение девяти верхних SMA
и protrusion 15.11 mm внутри bare-18650 silhouette 18.6 mm. Владелец принимает
`IMP-0048/D` как `DEC-0057`; legacy encoder требуется перенести. `MEC-0001`
проверяет official male/female `2×7 2.54-mm` interface и два M2 с шагом 56 mm,
а `FND-0069` сохраняет отсутствующие exact host MPN/stack-up и installed-cap
HIL открытыми.

Принципиальная распиновка больше не отложена, но владелец ставит integrated
physical mockup на паузу решением `DEC-0058`. `INT-0001` требует сначала
полного project-level review начинки: compute/service, safety, power,
UI/storage, audio, RF/IR/voice, expansion и consolidated component evidence.
Локальные проверки габаритов деталей разрешены; enclosure/control layout — нет.

`INT-0001/I1` получил **«Проведено ревью»** в `DEC-0059/REV-0005L`.
`FND-0070/IMP-0049` закрыты вариантом A: current 1-bit C5 SDIO оставляет C5
native USB GPIO13/14 и S3 default UART0 GPIO43/44 независимыми. M5 Unit UART
использует UART1 на прежнем порту GPIO7/8. Framed-throughput/reset/RF-load HIL
остаётся обязательным; 4-bit — только fallback после провала.

Владелец принял `IMP-0050/A`. `DEC-0061/SAFE-0002/REV-0005O` дают `I2`
**«Проведено ревью»**: exact AON supervisor/latch/Ioff reset fan-out теперь
сбрасывает S3 `CHIP_PU`, C5 `CHIP_PU` и RP2354B `RUN`; hardware gates покрывают
3×nRF CE, nRF/CC/voice/accessory rails, IR carrier и voice PTT. Пять LTC5532,
два LTC5507 и optical VEMD1060X01 идут в два TLV1824, local-I²C TCA9534A source
mask и direct BAT54ALT1G/`RP.GPIO22`/red-LED aggregate. Machine source и все
living diagrams обновлены. U214 без accessory evidence остаётся
`unknown/unavailable`; BAT15 coupon — cost-down HIL.

`PWR-0002/FND-0073/REV-0005P` проводят первый prerequisite pass `I3`. Новый
load/scenario ledger сохраняет 3.3-V envelope `2.5/3 A` и отдельный 4-V
voice result, но отклоняет legacy sheet как target: у BQ25887 нет system power
path, его ADC не является fuel gauge, два Rd не доказывают 3-A source, старый
master switch блокирует зарядку в OFF, а прежние rails не содержат current
safety/quiet-state branches. Владелец принял `IMP-0052/B` как `DEC-0062`: два
слота 18650 остаются отдельно заменяемыми, но произвольные ячейки/сочетания не
допускаются. Механическая защита от переполюсовки и наблюдение до допуска
обязаны держать опасные slot paths открытыми при mismatch, извлечении или
дребезге контакта. Распространение проверено в `REV-0005Q`.
`DEC-0064/PWR-0006/FND-0076/REV-0005S` затем переоткрывают и сравнивают
электрические series/controlled-1S варианты. Direct parallel отклонён, для 1S
рассчитаны двойной общий ток и новые rail classes. Владелец выбирает
supervised 2S в `DEC-0065/REV-0005T`; `PWR-0005/REV-0005U` повторно проверяют
exact devices, а владелец принимает `MAX17320G20+T + MSPM0C1104SDGS20R` в
`DEC-0066/REV-0005V`. Оба устройства отдельно внесены в machine source и
living diagrams; после exact two-ADC allocation в `DEC-0067` DGS20 имеет
`12 used / 3 permanent service / 3 free` реальных GPIO.
Затем
владелец принял `IMP-0053/B` как `DEC-0063`: основной порт — sink-only USB-PD с
fallback 5 В, 9 В/3 А и 15 В/2 А, максимум 30 Вт, без source/power-bank/
20-V/PPS/OTG и с прямыми USB2-линиями S3. `PWR-0004/FND-0074/REV-0005R`
создают и проверяют exact `TPS25751DREFR`, `BQ25798RQMR`, обязательную boot/
config EEPROM `CAT24C512WI-GT3` и `TVS2200DRVR`. S3 повторно использует SYS
I2C0 и wired-low system IRQ, поэтому GPIO47 остаётся свободным. Blank/corrupt
image recovery, reset-high EEPROM WP и charge-disable CE указаны явно;
target README diagrams и firmware contracts обновлены. `PWR-0007/FND-0077/
REV-0005W` выявили линейную модуляцию CHG FET в prequal. Владелец принял
`IMP-0056/A` в `DEC-0067/REV-0005X`: продукт отклоняет банку ниже
квалифицированного порога, отключает zero-volt/prequal recovery, а любое
исследование восстановления возможно только внешней изолированной оснасткой
Controlled Zone. Active `CSD87313DMST`, две `0451005.MRL`,
`WSL25125L000FEA`, две `B57332V5103F360`, `2N7002DW-7-F`, `BAV70LT1G` и
`BAT54-7-F` перенесены в machine source и living diagrams; устаревший
`FDMC8030` отклонён lifecycle-проверкой. Exact cell-tap/passive/diagnostic
values, source-handover HIL, AON source/hold-up, все load switches/discharge
paths, monitoring, reverse current и рассчитанные loss/thermal/fault budgets
остаются активны. `PWR-0008/DEC-0068/REV-0005Y` теперь проводят ревью active
downstream tree: exact `TPS629203DRLR` AON, три независимых фиксированных
`TPS564252DRLR` stage 3.3/4.0/5.0 В, exact Sunlord inductors, пять отдельных
quiet-state switches `TPS22919DCKR` и connector-side reverse blocking/current
limit `TPS259470LRPWR`. `DEC-0069/REV-0005Z` заменяют ранний auto-retry suffix
на latch-off с теми же footprint/ценой и исправляют nominal limit на
tolerance-safe target 1,50 А. Проверка реального корпуса также исправляет pin 4
TPS564252 на `PG` (bootstrap встроен). Exact passive values, hot loss и HIL
остаются активным закрытием I3. Эта проверка PG также выявила реальный дефект
агрегации: optional converter штатно держит PG low, пока выключен.
`PWR-0009/DEC-0070/REV-0005AA` теперь вводят два отдельных
`MMBT3904-7-F`, реализующих `EN AND NOT(PG)` перед `POWER_FAULT_N`; прямое
optional-PG объединение удалено, GPIO не потрачен, а два компонента добавляют
около `$0.032` при проверенной цене на 50 штук.
`FND-0058`,
`FND-0060/0066/0067` и последующие prototype-only HIL остаются явными. KiCad
заблокирован; `G2F-2R/3D` и `LAY-0001` P1/P2/P3 остаются references.

`REV-0005K` теперь делает диаграмму `Principled solution design` вертикальной
и живой проекцией начинки. Обе стартовые README-диаграммы и generated atlas
обязаны меняться в том же коммите, что и принятое изменение устройства,
owner, шины или тракта; regression проверяет orientation и покрытие MPN
текущего candidate.

`FND-0072/IMP-0051` выявили, что target README снова начали пересказывать
инженерную chronology. Владелец принял `DEC-0060`; `REV-0005N` провёл ревью
исправления. Четыре корневые EN/RU страницы теперь являются product landing
pages без цепочек `DEC/REV/FND/IMP` и open-gate narrative. Здесь и в review
ledger сохранены вся зрелость, находки и история; hardware pin groups доступны
в responsive `<details>` и generated atlas.
