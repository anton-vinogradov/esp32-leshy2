# DEC-0066 — MAX17320 plus MSPM0 fail-closed 2S manager

- Статус: **Принято владельцем; распространено**
- Дата: 2026-08-18
- Owner choice: [`IMP-0054/A`](../improvements/IMP-0054-fail-closed-2s-admission-manager.md)
- Device/contact review: [`PWR-0005`](../architecture/PWR-0005-replaceable-2s-manager-options.md)
- Propagation review: [`REV-0005V`](../reviews/REV-0005V-2s-manager-decision-propagation.md)

## Decision

1. Exact pack gauge/protector is `MAX17320G20+T`: 24-pin TQFN, I2C,
   2S–4S high-side CHG/DIS protection, ModelGauge state estimation, four
   thermistor inputs and cell balancing.
2. Exact admission controller is `MSPM0C1104SDGS20R`: 20-pin DGS VSSOP,
   16-kB flash/1-kB SRAM, watchdog, ADC, I2C, UART and permanent SWD/reset
   recovery.
3. The exact `G20` order code is the I2C variant without SHA-256. Battery
   authentication, a secret-key dependency and irreversible owner lock are
   not introduced.
4. `MAX17320 ALRT` is consumed as the reset-default FET override. The factory
   fixture must program and read back the complete protected gauge image,
   checksum and `OvrdEn=1` before an energized cell assembly is permitted.
   A blank, corrupt or wrong image is a manufacturing/service reject.
5. The admission controller locally verifies gauge identity/configuration,
   both cells, temperatures, mismatch and bounded diagnostic-load response.
   S3 receives a read-only state/fault interface and cannot force release.
6. Normal admission work may use `MAX17320 AOLDO` only at a measured
   low-clock/duty operating point below its `<2 mA` source budget. Blank-device
   programming/recovery uses an isolated fixture supply; in-product update
   uses an admitted system rail. Exact source selection and backfeed isolation
   remain the next circuit selection.

## Working contact allocation

| MSPM0 contact | Physical pin | Working role |
|---|---:|---|
| `PA0`, `PA11` | 4, 11 | system I2C target without consuming reset |
| `PA2`, `PA4` | 8, 9 | dedicated bit-banged MAX17320 I2C |
| `PA6` | 10 | request to release the external reset-default ALRT hold |
| `PA16/A8` | 12 | `PFAIL` input |
| `PA17`, `PA18/A7` | 13, 14 | permanent service UART TX/RX |
| `PA22/A4` | 17 | bounded diagnostic one-shot trigger, reset-default low |
| `PA23` | 18 | request through a reset-safe open-drain system-IRQ stage |
| `PA1/NRST`, `PA19/SWDIO`, `PA20/SWCLK` | 5, 15, 16 | permanent recovery; never runtime-repurposed |
| `PA25/A2`, `PA26/A1` | 20, 1 | current protected midpoint/full-stack ADC evidence after `DEC-0074/FND-0078` |
| `PA24/A3`, `PA27/A0`, `PA28/A5` | 19, 2, 3 | current free set; PA24 must not receive battery-derived injection current |

## Consequences

- The living target diagram contains two distinct boxes and MPNs for the gauge
  and admission controller; neither is hidden in a generic `PACKMGR` block.
- Both devices retain direct fixture access independent of S3. The admission
  firmware becomes a fourth independently recoverable signed/configured image
  domain, with a deliberately small state machine and no TX authority.
- `I3` continues with the exact 2S cell-tap network, CHG/DIS MOSFETs, fuses,
  NTCs, shunt, diagnostic load, ALRT hold and dual-source MCU supply isolation,
  then the downstream rail/loss/thermal tree.
- This is not authorization to begin KiCad. Exact passives, MOSFET SOA,
  thresholds, removal timing and physical HIL remain blocking.

`DEC-0067` subsequently closes the recovery/FET branch and updates the live
MSPM0 budget to `12 used / 3 permanent service / 3 free`; `DEC-0074/FND-0078`
retain that budget while correcting the two ADC contacts.
