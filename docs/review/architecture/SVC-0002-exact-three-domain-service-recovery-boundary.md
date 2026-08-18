# SVC-0002 — exact three-domain service and recovery boundary

- Статус: **Проведено ревью paper electrical scope; physical/HIL open**
- Дата: 2026-08-19
- Решение: [`DEC-0099`](../decisions/DEC-0099-exact-three-domain-service-recovery-boundary.md)
- Предшественники: [`REC-0001`](../components/REC-0001-compute-recovery-and-link-prerequisites.md),
  [`SVC-0001`](../components/SVC-0001-three-domain-development-access.md)
- Findings: [`FND-0106`](../findings/FND-0106-reset-fanout-contended-service-controls.md),
  [`FND-0107`](../findings/FND-0107-data-only-service-usb-was-not-data-isolated.md),
  [`FND-0108`](../findings/FND-0108-obsolete-service-switch-and-inexact-header.md)

## Product guarantee

S3, C5 и RP2354B независимо программируются, восстанавливаются и
диагностируются даже при стёртом или повреждённом firmware соседей. Сервисный
кабель/fixture не питает плату, не обходит hard STOP и не создаёт скрытой
runtime-периферии. Кнопки PTT, STOP, F1/F2 и весь D-pad не затронуты.

## Exact physical set

| Qty | Exact MPN | Role | Selection evidence |
|---:|---|---|---|
| 2 | `GCT USB4105-GF-A` | C5/RP independent data-only USB-C receptacles | active 16-contact top-mount, through-hole stakes, 20k mating cycles; official drawing exposes every contact and four shell stakes |
| 2 | `TPD2EUSB30ADRTR` | connector-side service D+/D− ESD | active, two channel, 0.7-pF typical, 3.6-V standoff, ±8-kV IEC contact |
| 2 | `onsemi FSUSB42MUX` | board-off D+/D− isolation | active USB2 DPDT, 720-MHz bandwidth, 6.5-Ω max RON at 3 V, Ioff ≤2 µA over 0…4.3 V with VCC=0 |
| 3 | `Samtec FTSH-105-01-L-DV-K-P-TR` | keyed populated DBG10 | active 2×5 1.27-mm SMT, polarization key and pick-and-place pad |
| 6 | `Alps Alpine SKQGADE010` | separate RESET/BOOT controls | mass-produced automotive SPST-NO, 2.55 N, 0.25 mm, 100k cycles, −40…90 °C |
| 3 | `TPD4E05U06DQAR` | four protected lines per DBG10 | existing exact low-capacitance array; RESET, BOOT, DBG0 and DBG1 each receive one channel |
| 1 | `SN74LVC1G06DCKR` | AON open-drain RUN-permit inverter | active Ioff device; avoids a push-pull high on manual reset targets |
| 2 | `2N7002DW-7-F` | three reset sinks plus one inert spare | active dual NMOS; passive drains allow wired-low STOP/button/fixture reset |
| exact instances | `ERJ-2RKF22R0X`, `ERJ-2RKF27R0X`, `RC0402FR-071KL`, `RC0402FR-07470RL`, `RC0402FR-0710KL`, `RC0402FR-075K1L`, `RC0402FR-071ML`, `C1005X7R1H104K050BB` | USB series, fixture current limits, IDs, pulls, CC Rd, VBUS bleeders and bypass | current active/orderable exact passives; every physical instance is machine-listed |

S3 continues to use the already reviewed protected product USB-C. Therefore
the complete product has three independent USB data paths, but only **two new
data-only service receptacles**, not three duplicate `USB4105` parts.

## USB electrical boundary

For C5 and RP, both orientation contacts join at the receptacle. D+/D− then
reach a connector-side ESD shunt and the common port of one `FSUSB42MUX`.
`OE=0`, `SEL=0`; only HSD1 is populated. VCC and a local 100-nF capacitor use
`3V3_MAIN`, so an unpowered board disconnects the data lines. HSD2 is NC.

C5 HSD1 reaches real exposed module GPIO14/GPIO13 through separate 22-Ω
resistors. RP reaches real package USB_DP/USB_DM through separate 27-Ω
resistors required by the RP2350 design guide. Each CC contact has its own
5.1-kΩ Rd. All four VBUS contacts join only a 1-MΩ bleeder and high-impedance
test pad; no charger, LDO or application rail attaches. SBU is NC and the shell
bonds directly to the local connector/ESD ground through multiple short vias.

## Common keyed DBG10

| Pin | Meaning | Exact electrical path |
|---:|---|---|
| 1 | `VTREF_SENSE` | `3V3_MAIN` through 1 kΩ; fixture input only |
| 2 | GND | ground-first fixture return |
| 3 | `RESET_N` | ESD shunt, physical RESET in parallel, 1 kΩ to target |
| 4 | `BOOT_N` | ESD shunt, physical BOOT in parallel, 1 kΩ to target |
| 5 | `DBG0` | ESD shunt, 470 Ω, UART TX or SWDIO |
| 6 | `DBG1` | ESD shunt, 470 Ω, UART RX or SWCLK |
| 7 | GND | adjacent signal return |
| 8 | `ID0` | 10-kΩ passive strap; fixture input only |
| 9 | GND | identity guard/return |
| 10 | `ID1` | 10-kΩ passive strap; fixture input only |

Codes `ID1:ID0` are `00=S3`, `01=C5`, `10=RP`, `11=invalid/unattached`.
The fixture reads ID and VTREF before it drives pins 3…6, and begins with every
drive high-Z.

| Domain | RESET | BOOT | DBG0 | DBG1 | USB |
|---|---|---|---|---|---|
| S3 | module `EN` | module GPIO0 | GPIO43 UART0 TX | GPIO44 UART0 RX | protected product USB GPIO19/20 |
| C5 | module `EN/CHIP_PU` | real module GPIO28 | GPIO11 UART0 TX | GPIO12 UART0 RX | real module GPIO13/14 data-only service USB; GPIO27 separately fixed high/read-only |
| RP2354B | package `RUN` | `QSPI_SS_USB_BOOT` through 1 kΩ | package SWDIO | package SWCLK | package USB_DP/USB_DM data-only service USB |

## Conflict-free hard-STOP reset

`RUN_PERMIT=1` makes `SN74LVC1G06DCKR` hold `RESET_KILL_GATE` low, leaving
all reset NMOS off. STOP makes `RUN_PERMIT=0`; the open-drain output releases,
the main-domain 10-kΩ gate pull-up turns all three sinks on and holds S3 EN,
C5 CHIP_PU and RP RUN low. AON loss with main power still present has the same
fail-reset result. Each target has its own 10-kΩ main pull-up.

Buttons and fixture paths see no push-pull high source. The spare transistor in
the second dual package has G/S grounded and D NC. Recovery never bypasses STOP
or grants an RF/TX lease; every recovered domain boots into TX-off state.

## Cost and exit gates

First-pass qty-100 material addition is approximately **USD 10.5…11.5** before
fixture cables, enclosure hatches and assembly quote. Three keyed Samtec
headers contribute about USD 5.10 and dominate the number; retaining all three
is the already accepted prototype/repairability tradeoff. Cost-down alternate
headers belong to I8 only after equal keying, access, retention and automation.

Paper electrical scope has **«Проведено ревью»**. Before physical freeze:

1. received connector/header/switch land-pattern and enclosure-actuation coupon;
2. USB Full-Speed SI plus attach/detach through each switch;
3. one/three-host VBUS and D-line board-off backfeed measurement;
4. independent erased/corrupt/wrong-image USB/UART/SWD recovery;
5. invalid ID, held/misordered controls, fixture overdrive and ESD injection;
6. STOP/AON-loss reset assertion in every service mode without RF re-arm.

