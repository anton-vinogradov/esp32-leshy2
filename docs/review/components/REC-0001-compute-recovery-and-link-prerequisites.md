# REC-0001 — compute recovery and inter-domain link prerequisites

- Статус: **Проведено ревью пререквизитов; physical-access topology ожидает owner decision**
- Дата: 2026-08-16
- Строки BOM: `C-006`, `C-007`
- Входы: `DEC-0028`, `PIN-0002`, `PWR-0001`, `BOM-0002`
- Finding: [`FND-0037`](../findings/FND-0037-c5-usb-download-strap-misidentified.md)
- Proposal: [`IMP-0026`](../improvements/IMP-0026-connectorless-owner-recovery-fixture.md)

## Evidence boundary

Этот артефакт фиксирует ROM/debug prerequisites и допустимую электрическую
границу. Он не выбирает owner-facing physical access без решения владельца и
не выдаёт Q до schematic/ERC/layout/fixture/HIL.

## Recovery primitives that cannot depend on application firmware

| Domain | Independent primitive | Required physical controls | Primary consequence |
|---|---|---|---|
| S3 | USB Serial/JTAG ROM download; UART0 fallback | native USB D−/D+, `GPIO0`, `EN`; UART0 TX/RX retained for RF-test/manufacturing fallback | application can disable/repurpose USB, therefore strap control remains physical |
| C5 | USB Serial/JTAG or UART0 Joint Download Boot 0 | native USB GPIO13/14, `GPIO28=0`, `GPIO27=1`, `CHIP_PU`; UART0 GPIO11/12 | `GPIO26` is not the USB BOOT selector; see `FND-0037` |
| RP2354A | ROM USB BOOTSEL and independent SWD | USB DP/DM, `QSPI_SS/USB_BOOT` through 1 kΩ, `RUN`, `SWDIO`, `SWCLK` | internal 2 MiB flash does not remove the USB_BOOT requirement |

S3 and C5 manufacturer guidance recommends retaining UART download because
current RF-test firmware uses UART. The service contract therefore retains
those signals even though normal owner recovery prefers USB.

Primary sources:

- [ESP32-S3 download guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/download-guidelines.html)
- [ESP32-C5 download guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/download-guidelines.html)
- [ESP32-C5 schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html)
- [Hardware design with RP2350](https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf)

## USB electrical baseline

| Domain | Series baseline | Routing/protection obligation |
|---|---:|---|
| S3 | reserve 22/33 Ω at the module | GPIO19/20 remain a 90 Ω differential route to the product USB path; DNP shunt-cap footprints only if layout permits tuning |
| C5 | reserve 22/33 Ω at the module | GPIO13/14 remain dedicated to recovery; no SDIO D2/D3 overlay; local two-line low-capacitance ESD at the service boundary |
| RP | 27 Ω at the MCU | 90 Ω differential route; no external USB speed pull resistors; local two-line low-capacitance ESD at the service boundary |

Service USB VBUS may not feed `3V3_CORE`. A fixture sees ground and a
current-limited voltage-reference sense only; the board is powered through its
normal protected input. This prevents a host cable from partially powering one
MCU or backfeeding the common rail.

`TPD2EUSB30DRTR` is a technically compatible ESD candidate (active TI part,
two channels, 0.7 pF typical, ±8 kV IEC contact), but its exact AVL/cost/
assembly disposition follows the physical-access choice and does not receive Q
here.

## Inter-domain electrical contract

`PWR-0001` places S3, C5 and RP on the same `3V3_CORE` rail. Normal firmware
may reset a peer but may not individually power-gate these three compute
domains. Therefore the accepted direct SDIO/SPI links do not require an active
level translator or bus-isolation IC in the current architecture.

| Link | Boot-safe baseline | Separation/tuning provision |
|---|---|---|
| S3→C5 1-bit SDIO | C5 GPIO7/8/9/10 only; pull-ups and a series footprint on every line; GPIO3=1/GPIO25=0 selects the recorded falling-sample/rising-drive profile | individually removable series elements, compact test pads, SI tuning and exact-speed HIL |
| S3→RP SPI1 | `CS_N` pull-up; SCK/MOSI source damping at S3; MISO source damping at RP; RP output high-Z unless selected | individually removable series elements and compact test pads |
| RP→S3 alert | open-drain/high-Z through reset with one `3V3_CORE` pull-up; not a push-pull boot source into S3 GPIO3 | removable series element and event/timing test point |

The common-rail invariant is normative, not an assumption hidden in layout.
If a later change introduces individual S3/C5/RP load switches, `C-007` must
reopen and add Ioff-qualified isolation before that change can be accepted.
Reset-only fault containment remains available now without the cost, delay and
new control dependency of an unnecessary active mux.

## HIL exit gates

1. Each domain recovers from erased flash and from an application that disables
   its normal USB function, without executable code on either peer.
2. C5 enters Joint Download Boot 0 only through GPIO28 low + GPIO27 high and
   returns to normal boot when service control is removed.
3. RP enters BOOTSEL through the 1 kΩ USB_BOOT path and also remains recoverable
   over SWD/RUN.
4. Fixture attach/remove does not arm TX, power a board, backfeed a host or
   disturb boot when no service action is requested.
5. SDIO and SPI pass throughput/latency/error/load tests at cold/hot and rail
   ramp; reset peers never drive conflicting states.
6. An open/shorted inter-domain series element produces a detected degraded
   state and safe TX-off behavior, not uncontrolled re-arm.

The factual prerequisite set receives **«Проведено ревью»**. Exact pad access,
ESD placement and enclosure exposure remain blocked only by `IMP-0026`; exact
resistor MPNs and measured values remain implementation/HIL gates.
