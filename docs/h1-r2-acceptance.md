# H1-R2 result · Physical product design

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h1-r2-acceptance.ru.md)

> **Reviewed on 30 August 2026.** The complete `H1-R2.37` physical model was
> accepted as the working product layout. This closes H1; it does not authorize
> native R2 KiCad work, component purchase or fabrication.

![Reviewed H1-R2 four-face layout](images/h1-r2-four-faces.svg?rev=h1-r2.37-reviewed-1)

## Finished result

| Property | Reviewed value |
|---|---:|
| Product structure | Two 75 × 150 mm PCBs with independently captured interboard stack |
| Registered physical bodies | 226 |
| Same-face collisions | 0 |
| Minimum opposing-face clearance | 2.59 mm against a 0.70 mm rule |
| Main antenna ports | 10, permanently assigned 5 + 5 |
| Interboard M1 | 80 contacts: 31 signals, 14 main-power, 2 AON, 24 returns, 9 true NC; contact 35 carries latched `FAULT_KILL` to the front indicator and contact 36 is the bounded S3 fault-UI reset |
| Base-BOM groups / fitted placements | 208 / 1,096 |
| Current electronics planning floor | USD 273.42 before five unpriced lines, PCBs and assembly |
| Accepted no-loss savings | USD 10.4192 |

The front PCB owns the user interface, exact EastRising 3.5-inch touch display
over direct 24-MHz i8080-8, S3, C5, three complete nRF24 islands, microSD and
the front Hub RP. The rear PCB owns broadcast/Airband reception, CC1101,
independent VHF/UHF voice, audio, power, safety, M5 Unit, the mutually exclusive
U214/U219 Cap slot and the rear RF RP.

All ten antenna connectors terminate on their owning PCB. Two identical
`ANT-433-CW-QW-SMA` antennas remain permanently assigned to the separate
SUB-GHz and UHF VOICE transmit-capable ports; they are not a swappable shared
load. Onboard analog video and every owner-soldered production module were
removed from the product boundary.

## Reviewed evidence

- [Readable placement, component legend and all generated views](h1-r2-physical-layout.md)
- [Grouped component cost ranking and top-20 audit](h1-r2-cost.md)
- [Power and thermal envelope](h1-r2-power-thermal.md)
- [Airband receive-path feasibility](h1-airband-filter.md)
- [Working principle pin design](h0-r2-functional-architecture.md#working-principle-pin-design)

## Boundary of this review

H1 confirms that the selected bodies, interfaces, labels, antenna ownership,
service access and interboard stack form one physically coherent device. It is
not proof of a routed PCB, ERC, signal integrity, power-up behaviour or
factory-buildability from released Gerbers/CPL/BOM.

H2 is now reviewed at **H2-R2.1.5**. Its prerequisite ledger is closed:

1. ✅ `H2-R2.0.1`: live Standard-PCBA route, MOQ and price for onsemi `FSUSB42MUX` / JLCPCB `C11355`;
2. ✅ `H2-R2.0.2`: exact factory-placeable `DMN2056U-7` detector, `SN74LVC1G74DCUR` ownership latch and `74HC20PW,118` release qualifier;
3. ✅ `H2-R2.0.3`: the exact `TCA9803DGKR/C2687966` powered-off boundary and
   rail-local termination for Pack/Safety I²C on Hub GPIO42/43.

The native R2 source/sheet/component inventory passed review as `H2-R2.1.1`.
The exact 237-board-group symbol/contact/value/footprint ledger passed review
as `H2-R2.1.2`. `H2-R2.1.3` then materialized 1,187 fitted positions and 4,327
physical pins across three native KiCad projects; all three pass ERC with zero
errors and zero warnings. Cross-sheet and machine-readable hardware/firmware
reconciliation passed at `H2-R2.1.4`; H3 now freezes the reviewed result.

KiCad, purchasing and fabrication remain unauthorized.
