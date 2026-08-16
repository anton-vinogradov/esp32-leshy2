# REQ-EXT-0001 — M5-first two-tier external expansion contract

- Статус: **Проведено ревью требований; exact implementation открыта**
- Дата: 2026-08-16
- Решение: [`DEC-0034`](../decisions/DEC-0034-m5-first-two-tier-expansion.md)
- Evidence: [`AUD-0005`](../audits/AUD-0005-m5-expansion-ecosystem-coverage.md)

## Требования

| ID | Contract | Acceptance boundary |
|---|---|---|
| `REQ-EXT-01` | M5 Unit A/B/C/custom — основной low-rate accessory tier. | Exact profile declares voltage, direction, protocol, pull-ups, current and fault behavior; unknown/mismatched profile remains unpowered. |
| `REQ-EXT-02` | Native Unit power starts off and is independently controllable. | Current limiting, backfeed blocking, discharge, ESD and observable power/fault state are proven for every exposed surface. |
| `REQ-EXT-03` | Powered insertion/removal is not a blanket promise. | Hot-plug is enabled only for an exact profile that passes insertion/removal, short, stuck-bus and brownout HIL. |
| `REQ-EXT-04` | Native Cardputer-compatible Cap preserves U214 without reducing it. | SPI `SCK/MOSI/MISO/NSS`, `BUSY/IRQ/RESET`, GNSS UART, I²C and controlled `5VIN/5VOUT/GND` are all available concurrently as the profile requires. |
| `REQ-EXT-05` | External power cannot backfeed or silently arm an accessory. | Both 5 V directions are controlled; reset/update/STOP/accessory fault invalidates every TX lease and leaves external transmitters safe-off. |
| `REQ-EXT-06` | M5-Bus is not native base compatibility. | Each requested Module needs an exact carrier, host mapping, power/enable, retention, firmware identity and recovery qualification. |
| `REQ-EXT-07` | A separate high-throughput class preserves SDR/compute/host reachability. | G3/G4 compare connector/role/power/ESD/driver alternatives; low-rate command links are never reported as raw-data equivalence. |
| `REQ-EXT-08` | Combined tiers target at least 90% of reviewed attachment classes. | Coverage is recomputed against user results, not catalog size; every result distinguishes reachability, catalog availability and qualified completion. |
| `REQ-EXT-09` | Profiles reserve shared resources atomically. | Bus, address, pins, power, RF coexistence and latency conflicts are reported before power-up; repeated I²C addresses use isolated buses/mux qualification. |
| `REQ-EXT-10` | Active accessories participate in the update/recovery trust model. | UI exposes accessory identity/version/compatibility and recovery limits; a programmable accessory never silently inherits trust from the connector. |
| `REQ-EXT-11` | Mechanics are part of compatibility. | G3 covers antenna/cable bend, retention, strain, enclosure collision, glove handling and safe removal for every intended field profile. |
| `REQ-EXT-12` | Cost remains visible at three product levels. | Base device, likely field kit and maximum Lab kit BOM/NRE/service burden are reported independently under `DEC-0005`. |

## Deferred implementation choices

Port count/placement, passive docks, high-speed connector and USB role, exact
MCU/bus/pins, power limits and carrier construction are downstream choices.
Deferral does not permit deleting the full U214 contract or high-throughput
class after an accepted accessory depends on them.

## Exit evidence

- G3 reviewed connector/mechanical/accessory-use surfaces;
- G4 at least two complete architectures cover this same contract;
- G7 exact owners/resources and simultaneous profiles converge atomically;
- G9 electrical protection and firmware manifest/state-machine specifications;
- G11 wrong-profile, power/backfeed/fault/STOP/update/recovery and throughput HIL.

