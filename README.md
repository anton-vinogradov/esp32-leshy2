<div align="center">

# Leshy2 ⭐

### Open autonomous hardware for radio, communications and authorized research

**2.4/5-GHz Wi-Fi · BLE · 802.15.4 · 3× nRF24 · Sub-GHz · VHF/UHF · FM/AM/SW/LW/Airband · analog FPV RX · IR · LoRa expansion**

[Capabilities](docs/hardware.md) · [How it is built](docs/h0-r2-functional-architecture.md) · [Schematics](docs/schematics.md) · [Roadmap](docs/roadmap.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware) · [Русский](README.ru.md)

</div>

> **Current hardware marker: `H1-R2.32`.** The exact dual-RP GPIO/M1 map and
> C5 SDIO/service-mux electrical join are closed as current H1 authority. The
> accepted same-slot U214/U219 role now has all five active host packages and
> all 43 existing Cap/evidence bodies registered with source-backed courtyards.
> Support passives, NFC pickup geometry and installed-antenna swept volume
> remain the three explicit H1 blockers before
> complete mock-up acceptance. R2 H2/KiCad has not started,
> and ordering remains blocked.

> **R2 authority gate:** current H0/H1 has six compute domains and two `SC1512-A4`
> controllers: a front Hub RP and a rear RF RP. The checked-in G2F/H2/KiCad
> material is preserved historical single-RP R1 evidence, not current R2 authority.
> It cannot authorize firmware, R2 KiCad, fabrication or ordering. The exact
> dual-RP/C5 electrical authority is the current H1 machine contract; H2 will be
> a new R2 export only after physical H1 closes.

## What it is

Leshy2 is a portable, repairable instrument for radio observation,
communications, diagnostics and authorized security work. It keeps the user
interface responsive while active radio groups run on local buses and unused
interfaces enter a hardware-verifiable quiet state.

| Capability | Finished-device result |
|---|---|
| Three nRF24 radios | Concurrent full RX/TX/mixed modes: `3R`, `1T2R`, `2T1R`, `3T` |
| Native wireless | S3 Wi-Fi/BLE and C5 2.4/5-GHz Wi-Fi, 802.15.4 and IR |
| Dedicated RF | CC1101 Sub-GHz, independent VHF/UHF voice, FM/AM/SW/LW/Airband RX |
| Video | Receive-only analog 5.8-GHz FPV through a dedicated rear MMCX |
| Interface | 3.5-inch 320×480 touch IPS over direct 32-MHz i8080-8, S3-local buttons through `TCA9539PWR`, waterfall, microSD and audio |
| Expansion | One protected rear Cap slot for U214 LoRa or U219 CC1101+NFC, plus a protected M5 Unit interface |
| Recovery | Four independent USB paths, recessed per-controller controls and DBG10 fallbacks |
| Unattended safety | TX evidence, watchdog, thermal supervision, hard power-off and retained fault reason |

Transmission and intrusive laboratory functions are separated from ordinary
use by the [three-level safety model](docs/safety.md). Installation requires the
user to accept the non-aggression/authorized-use terms.

## Physical mock-up

![Current four-face Leshy2 mock-up](docs/images/h1-r2-four-faces.svg?rev=h1-r2.23-cost-display-1)

[Open the legend for all 168 numbered references](docs/images/h1-r2-component-legend.svg?rev=h1-r2.23-cost-display-1) ·
[detailed exterior](docs/images/h1-r2-external-layout.svg?rev=h1-r2.23-cost-display-1) ·
[front inner face](docs/images/h1-r2-inner-ui.svg) ·
[rear inner face](docs/images/h1-r2-inner-rf.svg)

The exterior silkscreen identifies `UI PCB · R2-EVT1 · REV A` and
`RF/PWR PCB · R2-EVT1 · REV A`; `H1-R2.xx` remains documentation-only.

## How it is built

![Leshy2 functional architecture](docs/images/h0-r2-functional-architecture.svg)

The front UI/radio PCB owns S3, C5, all three complete nRF24 islands, the front
RP, microSD and the TVP5150 decoder. The rear RF/power PCB owns CC1101,
VHF/UHF voice, broadcast/Airband, audio, the one-of-two K331/AWM666V FPV bay, M5 and the mutually exclusive U214/U219 Cap slot, the rear RP, power
and independent safety.

Only one 75-ohm CVBS signal crosses the 80-contact M1 connector. The decoder's
11-line camera bus and the independent i8080-8 display TX path remain local to
S3; nRF payload remains local to the front RP. M1 is fully assigned: 25 live
signals, 14 main-power contacts, 2 AON contacts, 25 defined returns and 14 NC
reserves.

The drawings are generated from one machine-readable placement source. Inner
labels are drawing references, not silkscreen. The complete component legend is
linked beside the mock-up; individual inner views remain links without repeating
the same diagrams on the page.

[Open the readable physical result](docs/h1-r2-physical-layout.md) ·
[Component cost ranking](docs/h1-r2-cost.md) ·
[Power and thermal result](docs/h1-r2-power-thermal.md) ·
[Analog-FPV path](docs/h1-r2-fpv.md) ·
[Airband filter feasibility](docs/h1-airband-filter.md)

## Schematics and interfaces

The public site keeps the principle schematics needed to understand the finished
device:

- [component and bus schematics](docs/schematics.md);
- [working principle pin design](docs/h0-r2-functional-architecture.md#working-principle-pin-design);
- [external programming and recovery](docs/h1-r2-physical-layout.md#what-the-user-sees);
- [safety and hard-off architecture](docs/safety.md).

## Roadmap and current position

The roadmap stays on this landing page until prototype fabrication is approved.
Firmware has its own [independent roadmap](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/docs/roadmap.md).

| Stage | Status | Published result |
|---|---|---|
| H0 · Requirements and functional architecture | ✅ Reviewed · R2 | [H0-R2 result](docs/h0-r2-functional-architecture.md) |
| **H1 · Physical product design** | **▶ Current · `H1-R2.32`** | [Current placement](docs/h1-r2-physical-layout.md) · [cost ranking](docs/h1-r2-cost.md) |
| H2 · Production ECAD schematic | ⏳ Waiting for R2 H1 | [Stage page](docs/stage-results.md#h2) |
| H3 · Virtual electrical verification | ⏳ Waiting for R2 H2 | [Stage page](docs/stage-results.md#h3) |
| H4 · Joined hardware/firmware pre-layout gate | ⏳ Waiting for R2 H3 and firmware contract | [Stage page](docs/stage-results.md#h4) |
| H5 · Component and factory evidence | ⏳ Waiting for R2 H4 | [Stage page](docs/stage-results.md#h5) |
| H6 · KiCad placement and routing | 🔒 Waiting for R2 H5 | [Stage page](docs/stage-results.md#h6) |
| H7 · Prototype fabrication and bring-up | 🔒 Waiting for H6 and explicit order approval | [Stage page](docs/stage-results.md#h7) |
| H8 · Physical qualification | 🔒 Waiting for H7 | [Stage page](docs/stage-results.md#h8) |
| H9 · Manufacturing release | 🔒 Waiting for H8 and firmware F11 | [Stage page](docs/stage-results.md#h9) |

### Current H1 composition

- ✅ Exact front/rear RP GPIO0..47 maps, five Hub↔RF M1 signals and C5 SDIO/service-mux electrical join are machine-checked; budgets are `46/48` (2 free) and `44/48` (4 free: GP15/29/37/38).
- ✅ Ten main antenna ports repartitioned `5 + 5`; no main RF trace crosses M1.
- ✅ Direct i8080-8 display closes at 32 MB/s; buttons stay on the S3-local `TCA9539PWR` path, while encoder, USB and camera RX remain direct S3 paths.
- ✅ M1 has a complete 80-contact map and an enclosure load path: four 11-mm stops, anti-shear datums and independent PCB capture.
- ✅ Antenna silkscreen passes generated body/cable/accessory/fastener no-overlap checks.
- ✅ Vertical Molex `73415-2063` FPV MMCX: exact JLCPCB route, SMT-only, no interboard tail.
- ✅ Enlarged `30 × 24 × 8 mm` K331/AWM666V post-PCBA bay; exactly one receiver is installed and the unused RF branch is isolated at the MMCX launch.
- ✅ C5 DBG10 moved beside S3 DBG10; the structural audit of all currently registered bodies, including corrected maximum U219 package envelopes, reports zero same-face collisions and 2.59 mm minimum opposing clearance against 0.70 mm required.
- ✅ Public exterior, separate readable inner faces, service surface and real section views regenerated.
- ✅ Official Sinopine `SP331R-MANUAL-V1.0` controls the axes of the tolerant 14-pad K331 hand-solder land; exact-drawing AWM666V is the seven-channel fallback. Neither receiver enters the normal PCBA BOM.
- ✅ The 210-line `H1-R2.30` base BOM is cost-ranked per fitted device, five-device trial lot and 100-device projection. The later U219 host delta is shown separately as a provisional known-active subtotal; its support passives remain intentionally unpriced until exact values/MPNs close.
- ✅ U219 is accepted as the second mutually exclusive Cap profile: CC1101 is hard RX-only, NFC is poll/read-only, pin 10 is fail-disconnected and NFC field evidence joins `ANY_TX_AON_N`. Pin 7 power identity remains a received-unit gate, not an H2 claim.
- ✅ The two DCK boundaries, two BAT54S bridges and LMV331 comparator use official maximum full-package envelopes and source-backed courtyards; all five fit their bounded islands without overlap.
- ✅ All 43 existing Cap/evidence bodies now have exactly one source-backed coordinate and conservative placement courtyard; substitution, omission or duplicate projection fails generation.
- ▶ **Exact current point:** close the U219 support-passive values/MPNs and courtyards, locate and tune the NFC pickup, bound the installed U219 antenna swept volume, then review and explicitly accept the complete mock-up. A later AKK/Sinopine package can simplify the K331 footprint but no longer blocks H1.
- 🔒 KiCad, prototype purchase and fabrication remain unauthorized.

Every closed top-level `H*` phase publishes a bilingual readable report linked
from the table. Internal substeps update this exact marker and both repositories,
but do not pretend that a whole phase has been reviewed.

<!-- current-substep: H1-R2.32 -->

## Repository

Hardware documentation and generators live here. Firmware lives in
[`esp32-leshy2-firmware`](https://github.com/anton-vinogradov/esp32-leshy2-firmware).
Both repositories are open; signed releases protect update authenticity without
preventing owners from building and signing their own firmware.
