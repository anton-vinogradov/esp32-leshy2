# Leshy2 Hardware — current engineering state

> Snapshot: 2026-08-17. This page describes proven maturity. The intended
> behavior is in the [hardware target README](../../README.md); software behavior
> is in the [firmware target README](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.md).

- Canonical evidence: [review ledger](../review/README.md)
- Russian version: [current-state.ru.md](current-state.ru.md)
- Corrected gate chain: [`FLOW-0001`](../review/architecture/FLOW-0001-product-to-cad-gates.md)

## Review progress

| Gate | State |
|---|---|
| 0. Review baseline | Reviewed |
| 1. Product intent and safety/legal boundaries | Reviewed |
| 2. Capabilities, exclusions, concurrency/failure needs | **Reviewed again**: `REV-0002AS`; competitor delta closed |
| 2F. Logical/electrical feasibility | **In progress**: `G2F-3I` closes digital buses; `DEC-0045/0046` add one active group, three-nRF full mix and inactive-interface quiet states; exact nRF RF envelope, power parts and HIL remain open |
| 3. Target physical/product design | Waiting for G2F; P1/P2/P3 are reference-only, then the legacy clamshell generator is adapted |
| 4–6. Whole-device alternatives, optimality and conceptual co-design | Not started; G2F/G3 form an explicit review loop |
| 7. Atomic architecture | **Reopened** by `DEC-0032` |
| 8. Components/BOM | Blocked; previous evidence is candidate/reference only |
| 9. Electrical/CAD/firmware architecture | Blocked; no active canonical KiCad implementation |
| 10–11. PCB, fabrication and bring-up | Not started |

The canonical table is [`stages.md`](../review/stages.md).

## Competitor-delta closure

- `W-EXTRA-11` is closed: [`DEC-0033/REQ-IBTN-0001`](../review/decisions/DEC-0033-external-m5-ibutton-profile.md)
  accepts an external passive M5-style Port-B iButton adapter and no base pad;
- infrastructure is closed by [`DEC-0034/REQ-EXT-0001`](../review/decisions/DEC-0034-m5-first-two-tier-expansion.md): M5-first Unit/Cap plus a separate high-throughput class, without native M5-Bus;
- former `W-EXTRA-12` FIDO acceptance is removed from target by [`DEC-0039`](../review/decisions/DEC-0039-radio-key-scope-correction.md);
- `W-EXTRA-13` is closed by [`DEC-0036`](../review/decisions/DEC-0036-no-product-haptic.md): no product haptic, motor, dedicated profile or mount;
- `W-EXTRA-14` is closed by [`DEC-0037`](../review/decisions/DEC-0037-optional-external-imu-measurement-pose.md)/[`REQ-IMU-0001`](../review/requirements/REQ-IMU-0001-external-measurement-pose.md);
- `W-EXTRA-15` is closed by [`DEC-0038`](../review/decisions/DEC-0038-phone-assisted-text-no-integrated-keyboard.md): no integrated keyboard, bounded phone-assisted text;
- `W-EXTRA-16` generic High-Speed USB host is rejected by `DEC-0039`; only RF-derived transport remains;
- `W-EXTRA-17` 6 GHz/Wi-Fi 6E is fully rejected by `DEC-0040`; accepted
  autonomous 2.4/5 GHz remains unchanged.

`REV-0002AS` closes repeated G2 review. `DEC-0041` makes G2F active before the
physical mockup; `DEC-0042` accepts its machine-readable exact-device/net source.

## What remains reviewed

- all-in-one autonomous field-product intent, non-aggression onboarding and the
  Main/Lab/Controlled-Zone safety model;
- conservative TX defaults, explicit maximum-power choice, hard STOP/no
  automatic re-arm and separate actual-TX evidence;
- the complete 125-leaf wishlist review and no-loss cost rule;
- three full-function nRF24 paths with every simultaneous PTX/PRX role mix;
- ordinary 2.4/5 GHz Wi-Fi, IEEE 802.15.4, native BLE and 2.4 GHz/ESP-NOW
  capability requirements;
- packet Sub-GHz, broadcast receive, analog voice, audio, IR, external
  GNSS/LoRa/NFC, the external iButton/1-Wire adapter and their safety/evidence
  boundaries;
- open owner-controlled signed updates and the requirement that every selected
  programmable chip retain independent programming/recovery/diagnostics.

These are product inputs. Exact MCU/module ownership, pins, buses, board count,
connectors, parts and enclosure are not accepted.

## Correction completed

[`FND-0039`](../review/findings/FND-0039-architecture-frozen-before-product-design.md)
found that the former architecture chain skipped target physical design,
whole-product optimality and conceptual placement. The owner selected reopen
option A in [`DEC-0032`](../review/decisions/DEC-0032-reopen-product-design-before-cad.md).

Consequences:

- `DEC-0028/PKG-0001/SYN-3A` are historical candidate/reference evidence, not
  the target;
- C5 revision, compute ownership, pin and three-domain service studies are
  conditional candidate facts;
- the previously active C-001…005 KiCad library and CI are archived under
  [`premature-compute-cad-2026-08-16`](../../drafts/premature-compute-cad-2026-08-16/README.md);
- the pre-commit C-006 experiment is recorded as discarded in
  [`premature-service-cad-2026-08-16`](../../drafts/premature-service-cad-2026-08-16/README.md), without claiming a reproducible snapshot;
- active [`hardware/kicad`](../../hardware/kicad/README.md) contains only the
  upstream gate, not symbols, schematic or PCB.

`REV-0004H` reviews this correction. It does not review the new product design.

## Active artifacts

[`DEM-0001`](../review/architecture/DEM-0001-current-semantic-signal-demand.md)
records all required semantic endpoints without former owners.
[`SRC-0002`](../review/architecture/SRC-0002-real-device-pin-provenance.md)
forbids counting a pin without the SoC→package→exact module/device→actual
pad/header/connector chain. `DEC-0042/REV-0003Y` add the checked source;
[`G2F-pin-ledger`](../review/architecture/generated/G2F-pin-ledger.md) now has
three consumers and `G2F-3I` is the leading paper map. They pass
contact/collision/accounting/strap/service checks, but exact nRF,
CC RF implementation, voice/IR and several control/power devices remain
qualification blockers. `DSP-0001/REV-0003Z` review three real display/touch
boundaries and one microSD socket. `FND-0051` proves that the old 10-full-frame
ST7796S budget and generic 24-pin connector cannot be reused. `DEC-0043/REV-0004J`
accept task/dirty-region performance with `≤100 ms` critical/menu first response
and correct the shared-U214 display quantum from 1 KiB to 256 B; exact display,
optics and HIL remain open. `CTL-0001/REV-0004K` found that the first maps
closed MCU accounting only. The owner delegated layout search; `DEC-0044`
accepts `IMP-0037/A`, while `NIF-0001/REV-0004L` review the leading `G2F-3I`:
RP2354B/QFN80, five independent radio/accessory SPI paths, dedicated 4-bit
SDIO S3↔C5, dedicated SPI3 S3↔RP, 23/24 slow endpoints and isolated U214 I²C.
The only high-rate scheduled pair is display+SD on SPI2 with bounded quanta;
radio FIFO/IPC never waits for it. C5 UART0+EN/BOOT/strap is the recovery path
because GPIO13/14 carry SDIO. A repeated exact-device check found and fixed an
RP2354B PIO GPIO-window crossing; PIO data is now on `GPIO30..46`, fixed mux
groups are contracted, and capacity closes with seven of twelve PIO state
machines plus three of sixteen DMA channels in reserve. `DEC-0045` accepts one
active top-level signal group but defines `SG-N24` as all three radios active in
every PTX/PRX mix. `DEC-0046/QST-0001` require all unused interfaces quiet and
consume RP GPIO15/GPIO23 plus C5 GPIO4 as group-level power controls. Exact
`DEC-0047` accepts a qualified nRF RF envelope. The ordered second ESP32-DIV
becomes an early `L0 DIV↔DIV` pre-HIL observer, but does not replace the target
`T1 Leshy2` fixture. `N24M-0001` verifies real `E01-ML01S`,
`E01-ML01IPX` and `E01-2G4M27D` boundaries; `IMP-0040` opens the exact compact
module/antenna direction. Measured envelope points, power parts, self-desense
and target HIL remain the next gates. `FND-0050` records nRF24 NRND
and corrects CC1101 to ACTIVE.

[`AUD-0013`](../review/audits/AUD-0013-legacy-layout-generator-reuse.md)
accepts reuse of the old 75×150 mm two-board clamshell and its
collision/fold/mezzanine checks after the pin map is reviewed. Its old owners,
onboard LoRa, antenna count and generic nRF dimensions are not inherited.

Next, the owner decides `IMP-0040`; `G2F-3I` then fixes exact nRF
modules/antennas and advances `N24H-0001` from `L0 DIV↔DIV` pre-HIL to target
`T1` profiles. It then receives quiet-state power-part, physical
RF/self-desense, exact peripheral,
signal-integrity, power and HIL closure. It can then become a working electrical
baseline and feed the adapted legacy physical generator. `G2F-2R/3D` and
`LAY-0001` P1/P2/P3 remain references; no selection is requested. KiCad stays
blocked until the later atomic architecture gates pass.
