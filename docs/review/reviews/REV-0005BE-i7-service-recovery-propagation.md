# REV-0005BE — I7 service/recovery propagation

Статус: **проведено ревью; physical/HIL не выполнено**.

| Проверка | Результат |
|---|---|
| independent recovery of all programmable compute domains | pass: S3 product USB+UART, C5 independent USB+UART, RP independent USB+SWD |
| real exposed contacts | pass: S3/C5 module and RP2354B package contacts checked; no unavailable GPIO invented |
| service VBUS backfeed | pass in paper topology: no board-power path; only 1-MΩ bleeder and high-impedance pad |
| service D-line board-off backfeed | fixed: one power-off-protected `FSUSB42MUX` per C5/RP port |
| USB orientation/CC/ESD/series | pass: both orientation contacts, separate 5.1-kΩ Rd, connector ESD and MCU-side 22/27 Ω instantiated |
| debug access | pass: three separate keyed populated DBG10 headers; all 30 contacts accounted |
| service controls | pass: six separate current-orderable `SKQGADE010`; all four lands represented per switch |
| reset contention | fixed: push-pull direct drive removed; AON open-drain inverter plus three NMOS sinks and passive target pulls |
| STOP/AON behavior | pass by paper truth table: STOP or AON loss asserts all resets; recovery cannot arm TX |
| C5 straps | pass: GPIO28 physical boot control; GPIO27 exact fixed-high/read-only |
| RP BOOTSEL | pass: real `QSPI_SS_USB_BOOT` through exact 1 kΩ |
| GPIO/slow-I/O budget | pass: unchanged |
| cost | recorded at USD 10.5…11.5 qty 100; no functionality-reducing cost-down accepted |
| diagram propagation | pass: generated atlas and both product diagrams name separate physical devices with MPN and roles |
| firmware propagation | pass: runtime contract keeps service attach diagnostic-only, invalid IDs fail closed and all recovery boots TX-off |
| physical qualification | open: footprint/mechanics, USB SI, board-off leakage, multi-host, ESD and erased-image HIL |

## Verdict

`FND-0106…0108/SVC-0002/DEC-0099` close the remaining I7 paper electrical
subblock. I7 has **«Проведено ревью»** without claiming any measurement or
authorizing KiCad. I8 consolidated BOM/lifecycle/cost/alternate evidence is
the next dependency step; failed physical HIL reopens its owning I7 circuit.

