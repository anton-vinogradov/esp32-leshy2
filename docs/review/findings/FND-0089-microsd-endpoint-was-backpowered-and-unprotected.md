# FND-0089 — the microSD endpoint was back-powered and unprotected

- Status: **исправлено на бумажном уровне; physical/media/electrical HIL open**
- Scope: I4 removable-storage endpoint
- Decision: [`DEC-0085`](../decisions/DEC-0085-exact-isolated-microsd-electrical-endpoint.md)
- Architecture: [`STO-0001`](../architecture/STO-0001-exact-isolated-microsd-endpoint.md)

## Finding

The previous map named exact socket `DM3AT-SF-PEJM5` and a quiet-state
`TPS22919DCKR`, but it did not form a complete removable-card endpoint:

- SCK, CMD, CS and DAT0 still connected the live S3 domain directly to a
  card whose VDD could be off, so quiet-state power removal could inject
  through card pads;
- the card DAT0/MISO conductor also shared display QSPI D1 without an explicit
  hardware high-impedance boundary;
- mandatory SD pull-ups, local energy, source damping and reset defaults were
  not physical BOM instances;
- the seven non-ground card electrical contacts and the mechanical detect
  contact had no exact ESD boundary;
- the detect pair was named but had no always-powered pull/filter circuit;
- firmware sequencing did not require SPI-mode entry before other shared-bus
  traffic after every card-power cycle.

An exact socket by itself was therefore insufficient evidence for an exact
paper electrical endpoint.

## Self-review correction

Keeping the socket permanently powered would avoid one sequencing problem, but
would violate the accepted rule that unused interfaces physically turn off and
would leave card/display contention dependent on media behavior. Moving microSD
to a new dedicated MCU bus would consume pins that the completed resource map
does not have.

The corrected circuit keeps the shared S3 SPI2 allocation and adds card-side
Ioff isolation. `SN74LVC3G34DCUR` buffers SCK, CMD and CS toward the switched
domain. `SN74LVC1G125DCKR` returns DAT0/MISO only while `SD_CS_N` is low and is
high-impedance both when deselected and when the card rail is off. This closes
powered-off back-feed and display-D1 contention without a new GPIO.

## Corrected state

`STO-0001/DEC-0085` now instantiate exact input/output energy, fail-low power
control, all required card pull-ups, host reset defaults, four 22-Ohm buffered
source resistors, two eight-channel-total ESD arrays and a filtered card-detect
input. Every physical position is a separate machine instance and diagram node.

Socket placement, enclosure access, real-card compatibility/endurance,
throughput under display traffic, hot insertion/removal, destructive ESD/short
tests and corruption recovery remain HIL. This correction does not authorize a
footprint freeze or KiCad.
