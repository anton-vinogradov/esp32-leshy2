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
| 2F. Logical/electrical feasibility | **In progress; current paper baseline reviewed**: `PIN-0003/REV-0004V/0004X` close owners/controllers/exact compute contacts and the current QSPI-amended budget; final electrical endpoints, RF/power and HIL remain open |
| 3. Target physical/product design | **Starting from the `DEC-0051/PIN-0003` visible working design**: adapt the legacy clamshell generator; P1/P2/P3 remain reference-only and conflicts loop back to G2F |
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

These are product inputs. `G2F-3I/PIN-0003` is now the reviewed, reopenable
working owner/bus/compute-pin baseline for G3, not the final atomic
architecture. Board count, connectors, exact electrical parts and enclosure
remain unaccepted; physical/RF/power conflict may change working pins.

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
and correct the former shared-U214 quantum from 1 KiB to 256 B.
`DSP-0002/REV-0004W` expose `FND-0061`: U214 has moved to a dedicated RP bus,
so the fixed 256 B limit is stale. `DEC-0052/REV-0004X` close the finding by
accepting direct QSPI on S3 `GPIO41/42` and measured `<=1 ms` display
occupancy; the then-current S3 budget became `31/3/2`. `DSP-0003/REV-0004Y` show
that old 4-inch ST7796S remains an A0 workload fixture but not a QSPI target;
`DEC-0053/REV-0004Z` accept a 3.5-inch portrait `320×480` IPS direct-QSPI
capacitive-touch class. `FND-0063/DSP-0005/REV-0005A` correct the primary
source: official QDtech schematic exposes exact assembly `HMX035CTFT-001` and
its 40-contact paper fit now terminates in `G2F-3I`. Production
orderability/drawing/lifecycle, connector, backlight, optics and HIL remain
open.
`CTL-0001/REV-0004K` found that the first maps
closed MCU accounting only. The owner delegated layout search; `DEC-0044`
accepts `IMP-0037/A`, while `NIF-0001/REV-0004L` review the leading `G2F-3I`:
RP2354B/QFN80, five independent radio/accessory SPI paths, dedicated SDIO
S3↔C5, dedicated SPI3 S3↔RP, 23/24 slow endpoints and isolated U214 I²C.
The only high-rate scheduled pair is display+SD on SPI2 with bounded quanta;
radio FIFO/IPC never waits for it. `DEC-0059` subsequently narrows C5 SDIO to
1-bit and restores both C5 USB+UART and S3 USB+UART service without changing
controller independence. A repeated exact-device check found and fixed an
RP2354B PIO GPIO-window crossing; PIO data is now on `GPIO30..46`, fixed mux
groups are contracted, and capacity closes with seven of twelve PIO state
machines plus three of sixteen DMA channels in reserve. `DEC-0045` accepts one
active top-level signal group but defines `SG-N24` as all three radios active in
every PTX/PRX mix. `DEC-0046/QST-0001` require all unused interfaces quiet and
consume RP GPIO15/GPIO23 plus C5 GPIO4 as group-level power controls. Exact
`DEC-0047` accepts a qualified nRF RF envelope. The ordered second ESP32-DIV
becomes an early `L0 DIV↔DIV` pre-HIL observer, but does not replace the target
`T1 Leshy2` fixture. `N24M-0001` verifies real `E01-ML01S`,
`E01-ML01IPX` and `E01-2G4M27D` boundaries; `DEC-0048` accepts `IMP-0040/A`:
all onboard antenna endpoints are external SMA and the three nRF paths use
three compact IPEX→SMA feeds. `ANT-0001/REV-0004P` verify S3/C5/nRF/SA518
endpoint counts and expose `FND-0055`: exact Si4732 has separate `FMI` FM/SW
and `AMI` AM/LW inputs, while a generic long coax can violate the latter's
capacitance budget. `DEC-0049/REV-0004Q` close `IMP-0041` with option A: nine
labelled SMA and separate `RX-FM/SW`/`RX-AM/LW`; AM/LW requires a short
loop/pod or qualified buffered profile. Measured envelope
points, exact production lots,
power parts, self-desense
and target HIL remain the next gates. The same exact-device pass found
`FND-0056`: SA518 rev 1.1 has no dedicated SQ pin, so maps now reserve neutral
`VOICE_ACTIVITY`, while pin-17 UPDATE access remains a fixture proof gate.
`RFH-0001/REV-0004R` review the module-to-panel interface: S3/C5 have an
explicit first-generation U.FL/MHF I/AMC boundary, while Ebyte documents only
generic `IPX`. `FND-0057` corrects the machine source and requires a
specimen-fit/VNA gate. `RFH-0002/REV-0004S` separately review real antenna
ecosystems: RP-SMA is typical for native Wi-Fi, Ebyte/nRF uses standard SMA,
and sub-GHz has both polarities. `DEC-0050/REV-0004T` accept bounded
`2 native-Wi-Fi RP-SMA + 7 standard SMA`, a two-source antenna gate and a
machine connector/mate map without choosing mount/length or replacing exact
antenna qualification with connector popularity. `FND-0050` records nRF24 NRND
and corrects CC1101 to ACTIVE.

`ANT-0002/REV-0004U` review exact current commercial antenna candidates. One
dual-band RP-SMA MPN can serve S3/C5, one standard-SMA MPN can serve all three
identical nRF paths, and Taoglas `TI.08.C.0112` combines the common 868/915
profiles. No no-loss universal 315–915 or full-range VHF/UHF antenna was
established: CC needs interchangeable 315/433/868+915 profiles, VOICE needs
separate VHF/UHF antennas, and Si4732 retains whip and loop/pod profiles.
`FND-0058` corrects the earlier overstatement: the shortlist is reviewed, but
two-source production assemblies and target VNA/sensitivity/EIRP/HIL are not
closed.

`PIN-0003/REV-0004V` now provide a dedicated generated principled-pinout
atlas: the owner diagram, every MCU GPIO and physical module/package pad,
fixed mux, service/recovery, PIO/DMA budget and all slow routes come from one
JSON source. Self-review found `FND-0059`: old `NIF-0001/REV-0004L` displayed
the pre-`DEC-0046` budget. After `DEC-0052` and accepted audio `DEC-0054`, the
current result is S3 `32U/3R/1F`, C5 `14U/6R/1F`, RP `48U/0R/0F` and slow
plane `24U/0R/0F`; a regression now
locks those counts. Exact SA518 `UPDATE/UART/PD` service and Si4732 control/
FMI/AMI contacts are also instantiated. `FND-0067` found the previously
omitted ordinary RX-audio mux control and now places it on slow P27. `FND-0060`
keeps the remaining
abstract display/codec/IR/power/STOP/protection endpoints visible: the current
paper pinout is reviewed, while the final electrical schematic is not.
`DEC-0051` publishes this reviewed map in the target README as the principled
working design for G3 while keeping it reopenable until atomic architecture.

`IMP-0043/A` is accepted as `DEC-0055`: the profiled antenna kit shares MPNs
only across the equivalent S3/C5 and three nRF paths, combines 868/915, and
keeps separate 315/433, VHF/UHF, FM/SW whip and AM/LW pod profiles. Every
profile change disarms TX and unknown/mismatch keeps TX disabled. Availability
is checked again only when an exact MPN is selected.

`MFG-0001` establishes that a turnkey/kitting RFQ can combine PCBA and loose
antennas. `IMP-0047/B` is accepted as `DEC-0056`: this is the preferred first
RFQ but not a hard factory constraint; worse total cost, lead time, quality/test
scope or supply risk permits separate procurement.

`IMP-0044/A` is accepted as `DEC-0052`: the QSPI-first S3 display path uses
`GPIO41/42` for D2/D3 and a `<=1 ms` bus-occupancy contract. BT817/BT818 EVE
is the fallback; no fourth MCU is added to the baseline.

`IMP-0045/A` is accepted as `DEC-0053`: the target is a 3.5-inch portrait
`320×480` QSPI IPS+touch class; `DLE06235B/ES3C35P` (`ST77922`) is primary
HIL, Waveshare SKU `31137` (`AXS15231B`) is secondary HIL, and the old 4-inch
ST7796S stays A0 control/fallback. `HMX035CTFT-001` is the exact current paper
candidate, not yet a production-qualified BOM line; remaining unknown parts
stay explicit `TBD` entries in `DSP-0004`.

`AUDIO-0001/REV-0005B` verify exact ES8311 digital/contact fit. Complete-path
review `AUDIO-0002/REV-0005C` then corrects the analog assumption: a direct
6-kΩ-class ES8311 input can load the ordinary Si4732 bypass, PAM8302A already
accepts differential DAC, and SA518 TX requires heavy attenuation. It also
finds that P11/P12 expander outputs may remain stale through S3 reset.

`IMP-0046/A` is accepted as `DEC-0054`: ES8311 is retained with exact
`TLV9061IDBVR` high-Z capture, `TMUX1136DGSR` differential speaker selector,
`TS5A63157DCKR` TX selector and `SN74LVC2G08DCUR` reset-safe gate. Direct S3
GPIO6 is now `AUDIO_ARM`; passive capture remains a measured cost-down option.
The machine map and diagrams show the resulting S3 `32U/3R/1F` accounting.

[`AUD-0013`](../review/audits/AUD-0013-legacy-layout-generator-reuse.md)
accepts reuse of the old 75×150 mm two-board clamshell and its
collision/fold/mezzanine checks after the pin map is reviewed. Its old owners,
onboard LoRa, antenna count and generic nRF dimensions are not inherited.

`FND-0068/REV-0005G` find the next physical omission: the official U214 has an
`84×24×15.2 mm` body, direct 14-pin dock, its own RP-SMA and GNSS ceramic
antenna, while the legacy 75-mm SVG does not draw it. `PHY-0001/REV-0005H`
review a scaled rear-above-battery candidate: Cardputer-like transverse rail,
4.5-mm side overhang, all nine top SMA preserved and 15.11-mm protrusion inside
the bare-18650 18.6-mm depth silhouette. The owner accepts `IMP-0048/D` as
`DEC-0057`; the legacy encoder must move. `MEC-0001` verifies the official
male/female `2×7 2.54-mm` interface and two M2/56-mm retention, while
`FND-0069` keeps the missing exact host MPN/stack-up and installed-cap HIL open.

The principled pinout is no longer deferred, but the owner now pauses the
integrated physical mockup through `DEC-0058`. `INT-0001` requires complete
project-level internal review first: compute/service, safety, power,
UI/storage, audio, RF/IR/voice, expansion and consolidated component evidence.
Local part-envelope checks remain allowed; enclosure/control layout does not.

`INT-0001/I1` has **Проведено ревью** through `DEC-0059/REV-0005L`.
`FND-0070/IMP-0049` are closed by option A: current 1-bit C5 SDIO leaves C5
native USB GPIO13/14 and S3 default UART0 GPIO43/44 independent. M5 Unit UART
uses UART1 on its unchanged GPIO7/8 port. Framed-throughput/reset/RF-load HIL
remains required; 4-bit is fallback only after failure.

The owner accepted `IMP-0050/A`. `DEC-0061/SAFE-0002/REV-0005O` give `I2`
**Проведено ревью**: exact AON supervisor/latch/Ioff reset fan-out now resets S3
`CHIP_PU`, C5 `CHIP_PU` and RP2354B `RUN`; hardware gates cover 3×nRF CE,
nRF/CC/voice/accessory rails, IR carrier and voice PTT. Five LTC5532, two
LTC5507 and optical VEMD1060X01 feed two TLV1824 comparators, a local-I²C
TCA9534A source mask and a direct BAT54ALT1G/`RP.GPIO22`/red-LED aggregate.
Machine source and all living diagrams are updated. U214 without accessory
evidence remains `unknown/unavailable`; the BAT15 coupon stays cost-down HIL.

`PWR-0002/FND-0073/REV-0005P` complete the first `I3` prerequisite pass. The
current load/scenario ledger retains 2S, the 2.5/3-A 3.3-V envelope and the
dedicated 4-V voice result, while rejecting the legacy sheet as a target:
BQ25887 has no system power path, its ADC is not a fuel gauge, two Rd resistors
do not prove a 3-A source, the old master switch blocks off-state charging, and
the old rails omit current safety/quiet-state branches. **⚠️ Proposal
`IMP-0052`** is now the
explicit owner gate because the legacy mockup's two separately replaceable
18650 cells may be an unstated feature rather than disposable implementation.
Exact AON source/hold-up, battery/charger/power path, every load switch and
discharge path, monitoring, reverse current and calculated loss/thermal/fault
budgets remain active after that answer.
`FND-0058`,
`FND-0060/0066/0067` and later prototype-only HIL remain explicit. KiCad stays
blocked; `G2F-2R/3D` and `LAY-0001` P1/P2/P3 remain references.

`REV-0005K` now makes the `Principled solution design` diagram vertical and a
living internals projection. Both target README views and the generated atlas
must change in the same commit as any accepted device/owner/bus/path change;
the regression suite checks orientation and current-candidate MPN coverage.

`FND-0072/IMP-0051` found that target README files had again started narrating
engineering chronology. The owner accepted `DEC-0060`, and `REV-0005N` reviews
the correction. All four root EN/RU pages are now product landing pages without
`DEC/REV/FND/IMP` chains or open-gate narrative. Maturity, findings and history
remain here and in the review ledger; hardware pin groups use a responsive
`<details>` list linked to the generated atlas.
