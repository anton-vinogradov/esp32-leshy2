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
| 2F. Logical/electrical feasibility | **В работе**: `G2F-3I` закрывает digital buses; `DEC-0045/0046` добавляют одну active group, three-nRF full mix и quiet states неиспользуемых interfaces; exact nRF RF envelope, power parts и HIL открыты |
| 3. Target physical/product design | Ожидает G2F; P1/P2/P3 reference only, далее адаптируется legacy clamshell generator |
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

Это входы продукта. Exact MCU/module ownership, pins, buses, board count,
connectors, parts и enclosure не приняты.

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
`≤100 ms` и исправляют shared-U214 display quantum с 1 KiB до 256 B; exact
display, optics и HIL остаются открыты. `CTL-0001/REV-0004K` обнаружили, что
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
`DEC-0047` принимает qualified nRF RF envelope и reversible план второго
device-observer/peer. Exact modules, измеренные envelope points, power parts,
self-desense и named HIL остаются открытыми. `FND-0050` фиксирует nRF24 NRND и
исправляет статус CC1101 на ACTIVE.

[`AUD-0013`](../review/audits/AUD-0013-legacy-layout-generator-reuse.md)
подтверждает переиспользование старого `75×150 mm` two-board clamshell и его
collision/fold/mezzanine checks после согласования pin map. Старые owners,
onboard LoRa, antenna count и generic nRF dimensions не наследуются.

Далее `G2F-3I` выбирает exact nRF modules/antennas и превращает `N24H-0001` в
измеряемые profiles; затем проходит quiet-state power-part, physical
RF/self-desense, exact peripheral,
signal-integrity, power и HIL closure. После этого leading paper map может
стать working electrical baseline и войти в адаптированный legacy physical
generator. `G2F-2R/3D` остаются сравнимыми references; `LAY-0001` P1/P2/P3
также reference, выбирать его не нужно.
