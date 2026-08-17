# Аппаратная часть Leshy2 — текущее состояние проработки

> Снимок: 2026-08-17. Здесь указана доказанная зрелость. Образ готового
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
dedicated 4-bit SDIO S3↔C5, dedicated SPI3 S3↔RP, 23/24 slow endpoints и
изолированный U214 I²C. Единственная high-rate scheduled pair — display+SD на
SPI2 с bounded quantum; radio FIFO/IPC её не ждут. C5 UART0+EN/BOOT/strap
остаётся recovery path, потому что GPIO13/14 заняты SDIO. Повторная
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
antenna, а legacy 75-mm SVG его вообще не рисует. `IMP-0048` предлагает первый
active candidate: нижний съёмный bay с 4.5-mm overhang по сторонам, чтобы
сохранить base width и девять верхних SMA.

Принципиальная распиновка больше не отложена: current paper step завершён и
может войти в адаптированный legacy physical generator как reopenable working
map. Следующий проход начинает G3 physical/product mockup с реальными
envelopes; найденный packing/RF/power conflict возвращается в `G2F-3I`, а не
маскируется. Параллельно остаются `FND-0058` antenna qualification
и оставшиеся `FND-0060/0066/0067` exact electrical/HIL endpoints. Exact production nRF,
SMA/feed/protection, quiet-state parts, SI/power/RF/HIL обязаны закрыться до
atomic target и KiCad. `G2F-2R/3D` и `LAY-0001` P1/P2/P3 остаются references.
