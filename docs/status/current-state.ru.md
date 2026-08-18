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
| 2F. Logical/electrical feasibility | **В работе; I1…I5 paper reviewed, I6 active**: exact compute, safety, power, UI/storage, audio/receiver, three-nRF, native S3/C5, CC1101 three-band и SA518 RF endpoints входят в machine projection; IR, expansion, physical и HIL evidence открыты |
| 3. Target physical/product design | **Начинается от `DEC-0051/PIN-0003` visible working design**: адаптируется legacy clamshell generator; P1/P2/P3 reference only, конфликты возвращаются в G2F |
| 4–6. Whole-device alternatives, optimality и conceptual co-design | Не начаты; G2F/G3 образуют проверяемый loop |
| 7. Atomic architecture | **Переоткрыта** решением `DEC-0032` |
| 8. Components/BOM | Заблокирован; прежние evidence только candidate/reference |
| 9. Electrical/CAD/firmware architecture | Заблокирован; активного canonical KiCad нет |
| 10–11. PCB, fabrication и bring-up | Не начаты |

Каноническая таблица — [`stages.md`](../review/stages.md).

Для текущего I4 control/touch endpoint **проведено paper review** через
[`UI-0001`](../review/architecture/UI-0001-complete-local-control-topology.md)
[`UI-0002`](../review/architecture/UI-0002-exact-switch-and-control-protection.md)
и [`DSP-0007`](../review/architecture/DSP-0007-exact-integrated-st77922-touch-endpoint.md):
полный набор D-pad/OK/BACK/OPT/F1/F2/encoder/PTT/STOP/RE-ARM сохранён, а exact
switch/protection routes входят в machine projection; integrated ST77922 touch
зафиксирован на адресе `0x38` с active-low IRQ на shared GPIO37.
Cap/guard/harness/enclosure и specimen/electrical HIL остаются открыты.

Для зависимого I5 audio/receiver block теперь **проведено paper review** через
[`AUDIO-0003`](../review/architecture/AUDIO-0003-exact-audio-and-receiver-endpoint.md),
`DEC-0090` и `REV-0005AU`. ES8311, Si4732 и SA518 получили exact reset-off
power и physical interface isolation; receiver/microphone capture, bypass/
codec playback, ordinary/codec-injected TX и exact microphone, speaker и
switched-headphone endpoints завершены на бумаге. P00/P01/P02 реализуют
capture source, speaker enable и headphone sensing; выбор диапазона CC1101
теперь занимает P03/P04 и оставляет P05 свободным. Полный D-pad, PTT, STOP,
F1/F2 и encoder не изменены. Acoustic,
RF, specimen и concurrent-load HIL остаются явными; активен I6.

Первые четыре подблока I6 теперь также получили **«Проведено ревью»** на
paper-уровне. Три полнофункциональных nRF-тракта имеют независимую Ioff-
изоляцию, локальную энергию и направленное evidence в диапазоне
2400…2525 МГц. Раздельные S3 2,4-ГГц и C5 2,4/5-ГГц тракты идут от реальных
RF-контактов модулей через exact платные U.FL и `CP0603Q5425ENTR` в полные
каналы LTC5532; C5 ANT2 остаётся default-disabled/no-connect. CC1101 теперь
использует два одинаково управляемых `BGS13SN8E6327XTSA1` вокруг exact
first-pass ветвей 315/433/868–915 МГц: код `00` изолирует оба конца; P03/P04
задают диапазон только при снятом питании, а P05 остаётся единственным
свободным main slow-I/O. Полная линия имеет exact ESD и actual-TX sample на
`AD8314ACPZ-RL7` после всех switch/matching элементов. Точные джамперы и
корпусные разъёмы, пороги, VNA/conducted и RF/coexistence HIL всего устройства
открыты. SA518 ANT contact 7 теперь идёт на direct controlled-50-Ом SMA boundary
с exact 24-В `PESD24VY1BSF` и `AD8314ACPZ-RL7` actual-TX sample через
5,1 кОм/52,3 Ом. Непроверенный filter bank не расходует P05; measured
conducted failure переоткроет этот выбор. Далее активны IR и consolidated
coexistence.

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
contact/collision/accounting/strap/service checks, но exact IR
implementation и часть control/power всё ещё blockers.
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
3×nRF CE, nRF/CC/voice/accessory rails, IR carrier и voice PTT. Два LTC5532,
пять AD8314 и optical VEMD1060X01 идут в два TLV1824, local-I²C TCA9534A source
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
`12 used / 3 permanent service / 3 free` реальных GPIO; `DEC-0074/FND-0078`
позже исправляют exact контакты на PA25/PA26 без изменения бюджета.
Затем
владелец принял `IMP-0053/B` как `DEC-0063`: основной порт — sink-only USB-PD с
fallback 5 В, 9 В/3 А и 15 В/2 А, максимум 30 Вт, без source/power-bank/
20-V/PPS/OTG и с прямыми USB2-линиями S3. `PWR-0004/FND-0074/REV-0005R`
создают и проверяют exact `TPS25751DREFR`, `BQ25798RQMR`, обязательную boot/
config EEPROM `CAT24C512WI-GT3` и `TVS2200DRVR`. S3 повторно использует SYS
I2C0 и wired-low system IRQ, поэтому сам этот endpoint не занял тогда ещё
свободный GPIO47. Blank/corrupt
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
оставались активны на этом checkpoint. `PWR-0008/DEC-0068/REV-0005Y` теперь проводят ревью active
downstream tree: exact `TPS629203DRLR` AON, три независимых фиксированных
`TPS564252DRLR` stage 3.3/4.0/5.0 В, exact Sunlord inductors, пять отдельных
quiet-state switches `TPS22919DCKR` и connector-side reverse blocking/current
limit `TPS259470LRPWR`. `DEC-0069/REV-0005Z` заменяют ранний auto-retry suffix
на latch-off с теми же footprint/ценой и исправляют nominal limit на
tolerance-safe target 1,50 А. Проверка реального корпуса также исправляет pin 4
TPS564252 на `PG` (bootstrap встроен). Пассивы энергии/feedback, hot loss и HIL
оставались активным закрытием I3 на этом checkpoint. Эта проверка PG также выявила реальный дефект
агрегации: optional converter штатно держит PG low, пока выключен.
`PWR-0009/DEC-0070/REV-0005AA` теперь вводят два отдельных
`MMBT3904-7-F`, реализующих `EN AND NOT(PG)` перед `POWER_FAULT_N`; прямое
optional-PG объединение удалено, GPIO не потрачен, а два компонента добавляют
около `$0.032` при проверенной цене на 50 штук.
`PWR-0010/DEC-0071/REV-0005AB` затем исправляют контракт внешней eFuse:
`RILM` немедленно ограничивает ток уже при запуске, конденсатор `dVdt` 4,7 нФ
пропускает ёмкостную нагрузку, а 2 А допустимы только как ограниченный после
запуска импульс с таймером 220 нФ. Exact OVLO, локальные bypass-конденсаторы и
резистор разряда 1 кОм заменяют абстрактную цепь; все восемь физических
экземпляров отдельно показаны в machine source и target diagrams. Их
проверенная recurring cost — около `$0.10` на плату при 100 штуках.
`PWR-0011/DEC-0072/REV-0005AC` теперь закрывают следующий бумажный
пререквизит: open AON VSET, exact AON mode/input/output и независимые
TPS564252 input/output/feed-forward banks с фиксированными 1% делителями
представлены 24 физическими экземплярами. Номиналы main/voice/external равны
3,318/4,000/5,000 В; полные бумажные диапазоны допусков совместимы с
принятыми нагрузками, а максимум внешней линии остаётся ниже порога OVLO
eFuse. Lifecycle review отклоняет устаревшие 45,0 кОм в пользу активного MPN
45,3 кОм; recurring passive estimate — около `$1.8` на плату при 100 штуках.
`PWR-0012/DEC-0073/REV-0005AD` сначала закрывают converter control profile.
`FND-0084/PWR-0019/DEC-0080/REV-0005AK` теперь заменяют скрытый source
sequencer точными связями `AON_PG_N → TPS3808.MR_N` и задержанным
`POR_N → TPS564252 #MAIN.EN`. Exact pull-up POR 10 кОм и уже применяемый MPN
100 кОм дают около 3,0 В при release; amended profile содержит десять
физических позиций без GPIO и нового unique MPN. Исходный 85% reserve
защищённого входного тракта делает заряд system-first для фактических
5/9/15-В контрактов; source-transition behavior остаётся HIL.
`FND-0085/PWR-0020/DEC-0081/REV-0005AL` затем закрывают бумажный single-fault
пробел в этой последовательности. Exact `TPS25961DRVR` защищает
`AON_SAFE_3V3`, а два физически отдельных `TPS25974LRPWR` защищают main и
voice. Каждый компонент OVLO/ILIM-or-ILM/dVdt/ITIMER/PGTH/output внесён в
machine source; supervisor и runtime fault logic используют защищённую
сторону, а raw PG преобразователей остаётся только для оснастки. Full-corner
окна отсечки: 3,505…3,809 В AON, 3,438…3,578 В main и 4,314…4,610 В voice.
Расчётные потери — около 61 мВт typical на main при 2,5 А и 15 мВт на voice
при 1,25 А. Прибавка около USD 2,4 на плату не расходует GPIO и сохраняет все
функции; trip energy, hot temperature, load step и destructive
high-side-short HIL остаются открыты.
`FND-0086/PWR-0021/DEC-0082/REV-0005AM` затем проводят сводный I3-аудит
источников, тепла и отказов. Неразрешённых бумажных архитектурных
решений, скрытых деталей, нагрузок или recovery owner не остаётся,
поэтому бумажная электрическая часть I3 получает **«Проведено ревью»**,
а I4 становится активным бумажным блоком. Документы на ячейки/
держатель остаются procurement-gate I8; received-lot, source-transition,
rail, destructive-fault и thermal evidence остаются явным prototype HIL.
Этот переход не фиксирует BOM и не разрешает KiCad.
`FND-0087/USB-0001/DEC-0083/REV-0005AN` закрывают первый endpoint I4. Exact
`JAE DX07S016JA1R1500` заменяет абстрактный основной USB-C, а один
`TPD4S201RUKR` защищает обе CC и обе native USB2-линии S3 от connector-side
short-to-VBUS/ESD без расхода GPIO47. Support VPWR, VBIAS и FLT защиты
полностью exact; `FLT` остаётся только для оснастки. После добавления защиты
два шунта CC 330 пФ заменены exact C0G 220 пФ: published-value subtotal равен
369…471 пФ до паразитики трасс и оставляет минимум 129 пФ до потолка USB-PD.
Материал порта теперь оценён примерно в `$1.9…2.6` на плату. Placement/cutout,
полная ёмкость CC, USB Full-Speed RC/SI, ESD и short-to-VBUS HIL остаются
открыты; I4 продолжается, KiCad остаётся заблокирован.
`FND-0088/DSP-0006/DEC-0084/REV-0005AO` закрывают второй paper endpoint I4.
`FH12-40S-0.5SH(55)` теперь exact first-кандидат 40-контактного разъёма;
логика панели получает protected `3V3_MAIN`, локальные 10 мкФ/100 нФ и два
раздельных default-low reset. `TPS2553DRVR-1`, ILIM 133 кОм,
`ERJ-P08F10R0V` и `DMN2056U-7` образуют latch-off и reset-dark путь подсветки.
Отдельный switch всей панели отклонён: живые QSPI/I2C могли бы подпитывать его
отключённую шину. На этом endpoint S3 оставался `32/3/1`; проверенная добавка — примерно
`$2.5…2.9` вместе с обязательным разъёмом. Standalone procurement панели,
реальный fit/orientation шлейфа, shared-SPI/touch, current/thermal и fault HIL
остаются открыты; I4 продолжается к остальным UI endpoints.
`FND-0089/STO-0001/DEC-0085/REV-0005AP` закрывают третий paper endpoint I4.
Exact active socket `DM3AT-SF-PEJM5` теперь получает controlled/QOD switched
rail, card-side `SN74LVC3G34DCUR`, CS-gated возврат DAT0 через
`SN74LVC1G125DCKR`, обязательные CMD/DAT pulls, безопасные host defaults,
четыре exact 22-Ом выхода, две сборки `TPD4E05U06DQAR` и фильтрованный
always-readable detect. Выключенная карта больше не подпитывает host и не
может занять D1 дисплея. Добавка — около `$0.75…1.00` при 100 шт. без уже
выбранного socket и без новых GPIO. Placement/access гнезда, media/endurance,
shared-bus throughput/contention, hot removal, ESD/short/brownout и
filesystem-recovery HIL остаются открыты; I4 продолжается к оставшимся UI
endpoints, KiCad остаётся заблокирован.
`FND-0090/UI-0001/DEC-0086/REV-0005AQ` затем исправляют унаследованную
проекцию controls и закрывают четвёртый paper endpoint I4 для inventory и
principled pin fit. Сохранены D-pad/OK, BACK, OPT, F1, F2, encoder/push,
отдельный PTT, независимый normally-closed STOP и утопленный RE-ARM. Один exact
Отдельный `TCA9534APWR` P0…P6 и десять `1N4148WT` образуют interrupt-driven
матрицу 4x3; P7 зарезервирован, а main TCA6424 P00…P05 доступны зависимому
audio block. A/B энкодера занимают S3 GPIO39/GPIO47 PCNT0, а touch IRQ входит
в GPIO37. I5 затем назначает P00/P01/P02, а I6 — P03/P04 для выбора CC band.
S3 теперь `33/3/0`, main slow I/O `23/0/1`, UI I/O `7/1/0`; PTT остаётся
прямым RP GPIO21, а STOP/RE-ARM
— вне I2C. Exact mechanics переключателей, SYS-I2C collision scan,
encoder/U214 fit и HIL матрицы/энкодера остаются открыты;
KiCad заблокирован.
`FND-0091` также исправляет exact addressing TCA9534A с невозможных legacy
значений: all-low straps RP evidence дают `0x38`, all-high straps UI — candidate
`0x3F`; отдельный TPS25751D `0x20` не меняется.
`FND-0092/UI-0002/DEC-0087/REV-0005AR` затем закрывают exact switch current,
default-state и разделённую ESD-защиту, не убирая PTT, STOP, F1, F2 или D-pad.
`FND-0093/DSP-0007/DEC-0088/REV-0005AS` идентифицируют integrated ST77922,
exact address `0x38` и active-low TP_INT; exact raw pull-up 10 кОм и fixed
non-inverting `SN74LVC1G07DCKR` ведут сигнал на shared GPIO37, прежний inverter
option удалён. Specimen readback/IRQ/reset, shared-source и physical HIL
остаются открыты; следующий шаг — consolidated I4 audit.
`PWR-0013/FND-0078/DEC-0074/REV-0005AE` затем закрывают диагностический
frontend. Принятая pulse-proof нагрузка 10 Ом управляется только
non-retriggerable one-shot TPUL2G223: около 34,4 мс nominal и консервативный
бумажный C0G-диапазон 28,7-40,7 мс; production принимает только измеренные
импульсы 25-50 мс. Midpoint/stack ADC переносятся с ошибочного
PA24/PA25 на PA25/PA26, потому что PA24 не допускает injection current. Exact
делители 2x220k/169k и 5x220k/169k с двумя фильтрами 10 нФ остаются ниже
внутреннего reference 1,4 В в заданных fault-screen corners; эти first-pass
physical instances остаются явными и ниже исправлены PWR-0017.
`PWR-0014/DEC-0075/REV-0005AF` теперь закрывают физический профиль BQ25798:
exact 2S/750-kHz PROG, дроссель 2,2 мкГн/7 А, 19 capacitor instances, BATP,
прямой non-ignored TS, hardware ILIM, pulls I2C/INT, reset-high CE с
open-drain GPIO1 и Rev-C termination специальных контактов. `FND-0079`
возвращает product USB-C/USB2 protection в зависимый I4 и выявляет следующим
бумажным пунктом I3 support passives TPS25751/CAT24C512.
`PWR-0015/FND-0080/DEC-0076/REV-0005AG` затем закрывают этот paper profile:
обе raw-VBUS группы, hardware SafeMode, автономный EEPROM startup, 17
отдельных support components и полные local/host pulls представлены явно.
`PWR-0016/FND-0081/DEC-0077/REV-0005AH` далее заменяют placeholder держателя
на exact polarized `Keystone 1048P`, четыре функционально независимых
контакта, qualified protected-button-top boundary и отдельную изолированную
поджатую coupling role каждого из трёх NTC. Bounded rear-fit теперь использует
`39,8 × 86,0 мм` и installed reference envelope `20,7 мм`; для U214 остаются
paper reserves `9,719 мм` в плане и `5,59 мм` по глубине.
`PWR-0017/FND-0082/DEC-0078/REV-0005AI` затем исправляют WQFN-карту
TPUL2G223 (`2Q` — контакт 5, `VCC` — контакт 16), каскадируют второй канал в
измеряемый аппаратный cooldown `350…860 мс` и заменяют один 1-Вт load двумя
параллельными exact `CRM2512-FX-20R0ELF` по 20 Ом/2 Вт. Залипший или враждебный
trigger теперь аппаратно ограничен одним импульсом `<=50 мс` за каждые
`>=350 мс`, а штатная firmware ждёт минимум 10 секунд. Exact-cell droop
thresholds и lot/hot-copper HIL импульса/cooldown теперь опираются на
`PWR-0018/FND-0083/DEC-0079/REV-0005AJ`: два отдельных exact
`XTAR 18650 4000mAh` дают 28,8 Вт·ч nominal, 10-А discharge class, 2-А
standard/product charge ceiling и максимальный envelope `18,7 × 69,7 мм`.
Exact assembly certification documents, received fit, droop distributions,
effective-capacitance/load-step, thermal-stack, continuity/thermal,
destructive-fault/hot-loss/layout и перечисленные
startup/shutdown/brownout/multi-fault gates остаются обязательными
физическими свидетельствами по `DEC-0082`; они больше не маскируются
под незакрытый бумажный дизайн I3.
`FND-0058`,
`FND-0060/0066/0067` и последующие prototype-only HIL остаются явными. KiCad
заблокирован; `G2F-2R/3D` и `LAY-0001` P1/P2/P3 остаются references.

`REV-0005K` теперь делает диаграмму `Principled solution design` вертикальной
и живой проекцией начинки. Обе стартовые README-диаграммы и generated atlas
обязаны меняться в том же коммите, что и принятое изменение устройства,
owner, шины или тракта; regression проверяет orientation и покрытие MPN
текущего candidate.

Текущая зрелость dependency chain: I1/I2/I4…I7 **reviewed в paper scope**.
I8 inventory coverage проведён, а sourcing/lifecycle/cost/alternate work
активен; `FND-0109` узко переоткрывает MAX17320 support внутри I3, потому что
обязательные детали обвязки остались prose/abstract, а не физическими machine
instances.
`FND-0105/EXP-0001/DEC-0098/REV-0005BD` закрывают независимые power/signal
границы U214 и native Unit. `FND-0106…0108/SVC-0002/DEC-0099/REV-0005BE`
закрывают оставшуюся service/recovery схему: два board-off-isolated data-only
USB, три keyed DBG10, шесть отдельных controls, exact straps/passives и
passive-drain hard-STOP resets внесены в machine source. GPIO budgets и весь
набор controls не изменились. Physical connector/mechanics, USB
SI/backfeed/ESD, fixture и erased-image HIL остаются named reopen gates; KiCad
и integrated mockup заблокированы до завершения I8/I9.

`FND-0109/BOM-0008` теперь генерируют consolidated narrow-screen review и CSV:
791 current placements сворачиваются в 185 used lines, у 151 есть датированное
orderability evidence, у 34 его нет; ни одна строка пока не имеет
machine-readable comparable cost или alternate/no-substitution disposition.
Тот же аудит отдельно учитывает 9 SMA bodies, 5 RF cable assemblies, 2 M5
connector bodies, 8 actual-TX threshold networks, MAX17320 support residue и
12-item antenna-kit variant вместо выдачи этих абстракций за нулевую стоимость.

`FND-0072/IMP-0051` выявили, что target README снова начали пересказывать
инженерную chronology. Владелец принял `DEC-0060`; `REV-0005N` провёл ревью
исправления. Четыре корневые EN/RU страницы теперь являются product landing
pages без цепочек `DEC/REV/FND/IMP` и open-gate narrative. Здесь и в review
ledger сохранены вся зрелость, находки и история; hardware pin groups доступны
в responsive `<details>` и generated atlas.
