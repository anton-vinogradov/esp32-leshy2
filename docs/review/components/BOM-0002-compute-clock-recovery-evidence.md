# BOM-0002 — compute, clock and recovery evidence

- Статус: **Проведено ревью фактов и C5 stepping decision; component qualification не завершена**
- Дата snapshot: 2026-08-16
- Пререквизиты: `BOM-0001`, `DEC-0028`, `PIN-0002`, `BUD-0002`
- Review: [`REV-0004B`](../reviews/REV-0004B-compute-clock-recovery-evidence.md)
- Finding: [`FND-0035`](../findings/FND-0035-rp2354a-order-code-stock-correction.md)
- CAD evidence: [`LIB-0001`](LIB-0001-compute-cad-library-audit.md),
  [`DEC-0030`](../decisions/DEC-0030-vendored-critical-cad-libraries.md),
  [`REV-0004D/E`](../reviews/REV-0004E-vendored-critical-cad-libraries.md)
- Recovery/link prerequisites: [`REC-0001`](REC-0001-compute-recovery-and-link-prerequisites.md),
  [`REV-0004F`](../reviews/REV-0004F-compute-recovery-link-prerequisites.md)
- Physical development access: [`DEC-0031`](../decisions/DEC-0031-permanent-three-domain-development-access.md),
  [`SVC-0001`](SVC-0001-three-domain-development-access.md),
  [`REV-0004G`](../reviews/REV-0004G-three-domain-development-access.md)

## Evidence boundary

`BOM-0002` разделяет:

1. manufacturer primary fact — identity, package, memory, pins, reset/errata;
2. dated authorised-distributor observation — stock/lead-time, который может измениться;
3. unclosed implementation proof — schematic/ERC/layout/thermal/assembly/fixture/HIL.

Ни одна supplier page не присваивает строке `Q`. Финальное **«Проведено ревью»** компонента возможно только после всех применимых `E1…E4` и совместного exact manifest.

## Exact compute identities

| ID | Exact target / order identity | Проверенные primary facts | Supply snapshot | Disposition |
|---|---|---|---|---|
| `C-001` | `ESP32-S3-WROOM-1U-N16R2` | [official module datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf): 16 MB Quad flash, 2 MB Quad PSRAM, external antenna connector, −40…85 °C; native USB/boot straps remain normative from `PIN-0002` | [authorised storefront](https://www.mouser.com/ProductDetail/Espressif-Systems/ESP32-S3-WROOM-1U-N16R2) shows exact MPN and qty above 500, but regional inventory is dynamic | architecture identity retained; `E1`, partial `E3`; schematic/thermal/recovery/HIL open |
| `C-002` | `ESP32-C5-WROOM-1U-N8R8`, production ≥v1.2 (`MD` for v1.2) | [official module datasheet](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html): 8 MB Quad flash, 8 MB Quad PSRAM, external ANT1 default, dual-band Wi-Fi/802.15.4 and SDIO slave; silicon revision is not encoded in the MPN | [Mouser](https://www.mouser.com/en/ProductDetail/Espressif-Systems/ESP32-C5-WROOM-1U-N8R8) shows exact MPN and qty above 500, but generic listing does not promise revision-committed lot | `DEC-0029` accepted; `E1`, partial `E3`; exact v1.2 lot quote/schematic/recovery/HIL open |
| `C-003` | `SC1511-A4`; packaging-equivalent `SC1511(13)-A4` | [official RP2350 family facts](https://www.raspberrypi.com/documentation/microcontrollers/microcontroller-chips.html): RP2354A A4, QFN60 7×7 mm, 30 GPIO, 520 KB SRAM and stacked 2 MB flash; A4 identity is explicit | exact A4 public stock clears 500 at Mouser/DigiKey; see `FND-0035` | `E1`, partial `E3`; allocation claim corrected; QFN60 assembly/yield/fixture/HIL open |
| `C-004` | `TCA9535PWR` | [TI datasheet](https://www.ti.com/lit/ds/symlink/tca9535.pdf): active/production TSSOP-24, 1.65…5.5 V, 400 kHz, power-on all-I/O-input state, active-low interrupt; output latch must be loaded before changing direction where glitch-free state matters | active manufacturer status is verified; two authorised production quotes still absent | `E1`, partial `E3`; address/pulls/current and power-on sequence schematic proof open |

## C5 stepping and errata gate

Stage 3 originally accepted C5 silicon `≥v1.0`. Current [Espressif errata](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32c5/03-errata-description/index.html) changed the production-risk picture:

| Erratum | v1.0 | v1.2 | Architecture consequence |
|---|---:|---:|---|
| `CPU-718` PSRAM read-after-write consistency | affected | fixed | v1.0 needs workload restrictions/delays for affected access patterns |
| `SRAM-436` corruption after peripheral-domain power-down | affected | fixed | ESP-IDF disables the feature on v1.0; lower-power behavior differs |
| `HUK-576` HUK recovery can fail at power-on | affected; no workaround | fixed | v1.0 cannot be the trustworthy base for HUK/Key Manager use |
| `FLASH-938` manual flash encryption at 240 MHz | affected | affected | provisioning must run at ≤160 MHz on either revision |
| `ECC-833` ECDSA_DS verification under forced ECC power-down | affected | affected | do not use ECDSA_DS under that condition; exact security design remains a later gate |

[Espressif identification](https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32c5/01-chip-identification/index.html) gives module specification identifier `MC` for v1.0 and `MD` for v1.2; runtime eFuse verification is also available. [Key Manager documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-reference/peripherals/key_manager.html) explicitly supports the peripheral only on `≥v1.2`.

No accepted feature currently requires irreversible flash encryption or HUK. Nevertheless, production v1.0 would preserve a no-workaround security defect and two fixed memory/power defects inside a new design.

> **Принято в [`DEC-0029`](../decisions/DEC-0029-c5-v1.2-production-floor.md):** production/release/qualification floor is C5 v1.2, with `MD`/eFuse identity; v1.0 remains labelled engineering-only under the recorded restrictions.

[`REV-0004C`](../reviews/REV-0004C-c5-v1.2-propagation.md) verifies propagation to `DEC-0028/PKG-0001`, target READMEs, ownership and firmware runtime contract. This does not enable HUK, encryption or irreversible lockdown.

## Clock and recovery implementation baseline

| ID | Baseline fixed by primary guidance | Still open before `Q` |
|---|---|---|
| `C-005` | RP reference clock candidate becomes exact `ABM8-272-T3`, 12 MHz, with 15 pF to ground on each side and 1 kΩ series damping at 3.3 V IOVDD, following [Raspberry Pi hardware design](https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf) | exact capacitor/resistor MPN/voltage/temp; placement; startup, ppm and temperature HIL; any cheaper alternate must repeat oscillator qualification |
| `C-006` | `DEC-0031/SVC-0001`: three direct USB-C, three permanent common-pinout DBG10 headers and BOOT+RESET buttons for every domain; exact first targets are USB4105/FTSH/KMR221/TPD2EUSB30A; RP USB uses 27 Ω at MCU and all USB routes target 90 Ω differential | project-local CAD, exact passives/CC/VBUS isolation, AVL/assembly/mechanics, accidental access and erased/corrupt-image/multi-host HIL |
| `C-007` | preserve C5 1-bit SDIO and RP SPI+alert boot-safe pulls, source damping, separable series elements and test points; direct links depend normatively on common `3V3_CORE` with reset-only compute domains | exact resistor MPN/values, peer-reset/rail-ramp leakage, SI measurement and test-point loading; any future individual core power gate reopens Ioff isolation |

`ABM8-272-T3` is the manufacturer-recommended reference, not yet a qualified zero-loss monopoly. A cheaper crystal is allowed only after equal startup/temperature/USB/timestamp evidence; catalog similarity alone is insufficient.

## Prerequisite and artifact check

| Check | Result |
|---|---|
| exact MPN/stepping or exact missing decision named | yes |
| memory/package/antenna identities match accepted architecture | yes |
| C5 SDIO architecture remains compatible | yes; production stepping is separate from link choice |
| RP stock contradiction resolved | yes, `FND-0035`; public qty-500 availability passes, quotes/traceability remain open |
| clock reference is no longer generic | yes, exact manufacturer-recommended candidate and circuit recorded |
| recovery paths remain independent and owner-accessible | yes as a schematic contract; implementation proof open |
| exact project-local C-001…005 CAD snapshot exists and parses | yes; five bindings pass pin/pad/hash validation and KiCad 10.0.5 parser checks in `REV-0004E` |
| any component receives `Q` | no |

## Exit gate

`BOM-0002` can receive final **«Проведено ревью»** only after:

1. ~~owner disposition of `IMP-0024` and propagation to both repositories~~ — complete in `DEC-0029/REV-0004C`;
2. ~~exact project-local KiCad symbols/footprints for `C-001…005`~~ —
   complete in `DEC-0030/REV-0004E`; exact `C-006/007` implementation and
   the combined schematic/ERC contract remain open;
3. two authorised quotes/AVL entries and explicit C5 lot-revision commitment;
4. assembly/yield quote for RP QFN60 and module/reflow constraints;
5. recovery, boot-strap, peer-unpowered, clock startup/temperature and inter-domain link HIL.

The verified factual subset is safe input to schematic planning, but no downstream step may treat the compute platform as fully qualified yet.
