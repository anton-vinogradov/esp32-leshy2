# DEC-0031 — permanent three-domain development access

- Статус: **Requirement retained; compute service topology restored by `DEC-0059`**
- Дата: 2026-08-16
- Основание: владелец выбрал `IMP-0026/B` и потребовал полный debug/recovery access каждого MCU
- Этап: 4 — `C-006`, с зависимостями на `C-001…003/007`
- Реализационный контракт: [`SVC-0001`](../components/SVC-0001-three-domain-development-access.md)

> Retained owner requirement: every programmable chip selected by the future
> architecture has permanent independent programming, recovery and diagnostic
> access suitable for prototype bring-up and owner repair. The three USB-C,
> DBG10, exact buttons, pin mappings and parts below are a candidate study, not
> an accepted product topology.

> Subsequent resolution: `DEC-0059` accepts the independent S3/C5/RP
> USB/UART/SWD topology and exact compute contacts. Connector/protection/button
> BOM and mechanics below remain first targets for `INT-0001/I7/I8`, not frozen
> product parts.

## Решение

1. S3, C5 и RP2354A получают по независимому постоянно установленному USB-C,
   без data mux или software-controlled selector.
2. Каждый compute domain получает постоянно установленный keyed 10-pin debug
   header единого формата и собственные физические `BOOT` и `RESET` buttons.
3. Минимальный доступ:
   - S3: native USB, GPIO0, EN, UART0 TX/RX;
   - C5: native USB GPIO13/14, GPIO28, CHIP_PU, UART0 GPIO11/12; GPIO27 имеет
     обязательный high default;
   - RP2354A: native USB, QSPI_SS/USB_BOOT через 1 kΩ, RUN, SWDIO/SWCLK.
4. Ни один BOOT/RESET/debug path не проходит через peer MCU, GPIO expander,
   firmware, USB mux или внешний accessory.
5. Все три debug headers используют одинаковые позиции для `VTREF_SENSE`,
   GND, active-low RESET/BOOT и двух debug signals. Два пассивных ID inputs
   позволяют fixture определить домен до включения своих outputs.
6. S3 USB остаётся product data/power path. C5/RP USB являются data-only
   self-powered service ports; их VBUS не соединяется с power tree. Плата
   питается через нормальный protected input, поэтому несколько подключённых
   host/debugger не соединяют свои VBUS sources.
7. Вход в ROM recovery, reset или потеря debug link не вооружают TX. Reset/BOOT
   инвалидируют leases; любой RF-transmit diagnostic всё равно проходит
   обычные safety/legal/fixture gates.
8. USB и debug headers маркируются доменом на silkscreen и в корпусе. Buttons
   имеют различимые `BOOT`/`RESET` labels и защищены от случайного нажатия
   расположением/recess.

## Cost and production consequence

Решение B осознанно дороже первоначально рекомендованного connectorless A:
добавляются два USB-C assembly относительно one-port baseline, три permanent
debug headers, шесть buttons, три USB ESD channels и enclosure/service area.
Эта стоимость принята ради интенсивного prototype bring-up, независимой
диагностики и owner repairability.

Ни один из этих интерфейсов не переводится в DNP production-вариант молча.
Такое сокращение было бы изменением принятого product/service contract и
потребовало бы отдельного решения с доказательством эквивалентного доступа.

## Boundary

Решение фиксирует topology/access scope, но не выдаёт C-006 final Q. Exact CAD,
CC/passives, ESD layout, connector retention, enclosure access, multi-cable
EMC, assembly/AVL и erased/corrupt-image HIL остаются обязательными.
