<div align="center">

# ⭐ Leshy2

### An open autonomous multi-tool for radio, communications and authorized research

**2.4/5-GHz Wi‑Fi · BLE · 802.15.4 · 3× nRF24 · Sub‑GHz · VHF/UHF · FM/AM/SW/LW · IR · LoRa**

[Capabilities](docs/hardware.md) · [Mockup](#target-device-mockup) · [Schematics](docs/schematics.md) · [Roadmap](docs/roadmap.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware) · [Русский](README.ru.md)

**OPEN HARDWARE**　·　**MODULAR RF**　·　**FAIL-SAFE TX**　·　**REPAIRABLE**

</div>

> **Now: H3 · virtual electrical verification.** Production ECAD H2 is
> accepted; PCB routing, purchasing and fabrication remain blocked.

<div align="center">

![Leshy2 external faces](docs/images/current-clamshell.svg?layout=19)

**Nine independent antenna paths · five compute domains · one autonomous instrument**

</div>

## What Leshy2 is

Leshy2 is a portable open instrument for radio observation, communications,
diagnostics and authorized security work. It brings different radio paths into
one autonomous device while physically separating loaded buses, power domains
and transmit safety.

| Capability | What the user gets |
|---|---|
| **Three independent nRF24 radios** | Concurrent `3R`, `1T2R`, `2T1R` and `3T`, with full RX/TX/mix |
| **Broad radio coverage** | 2.4/5-GHz Wi‑Fi, BLE, ESP‑NOW, 802.15.4, Sub‑GHz, VHF/UHF, broadcast RX and IR |
| **Nine antenna ports** | Separate labelled external connectors with no RF sharing |
| **Autonomous interface** | 3.5-inch `320×480` touch IPS, menus, waterfall, microSD and audio |
| **Modular expansion** | M5Stack U214/Leshy LoRa Cap and a protected M5 Unit port |
| **Recovery access** | Independent USB, RST/BOOT and internal DBG10 for compute owners |
| **Safety** | Quiet-state, TX evidence, watchdog, thermal shutdown and retained fault reason |

## How it is built

Five isolatable domains split the user interface, native radio/IR,
deterministic radio paths, battery-pack admission and independent safety
automation.

- `ESP32-S3-WROOM-1U-N16R8` — UI, display, storage, audio and Wi‑Fi/BLE.
- `ESP32-C5-WROOM-1U-N8R8` — 2.4/5-GHz Wi‑Fi, IEEE 802.15.4 and IR.
- `SC1512-A4` / RP2354B — 3× nRF24, Sub‑GHz, voice and Cap Bus.
- `MSPM0C1106SDGS20R` #1 — independent battery-pack admission.
- `MSPM0C1106SDGS20R` #2 — watchdog, thermal supervision and TX leases.

Unused interfaces are physically disabled and enter a verifiable quiet state.
See the [hardware architecture](docs/hardware.md) and
[safety levels](docs/safety.md) for details.

---

## Target device mockup

Every view below is generated from the real envelopes of selected MPNs and one
coordinate model. Text outside component bodies on outer PCB faces is intended
silkscreen; inner faces carry no silkscreen.

### Outer faces

The main view opens this page; the detailed service, inner and edge views follow below.

### Programming and recovery

![Leshy2 external service access](docs/images/service-access.svg?layout=3)

### Series navigation and replaceable display

![Leshy2 series navigation cluster](docs/images/navigation-cluster.svg?layout=1)

![Leshy2 replaceable display adapter](docs/images/display-adapter.svg?layout=1)

### Inner sandwich faces

![Leshy2 inner board faces](docs/images/internal-board-layout.svg?layout=18)

### Antenna-edge view

![Leshy2 top view from the antenna edge](docs/images/top-edge-view.svg?layout=5)

### Cross-sections

![Leshy2 sandwich sections](docs/images/sandwich-section.svg?layout=11)

---

## Roadmap and current position

The roadmap remains on the landing page through printing/fabrication until manufacturing files are
explicitly released. The [full roadmap](docs/roadmap.md) contains dependencies
and exit criteria; [stage results](docs/stage-results.md) link published
drawings, schematics, contracts and checks.

| Stage | Status | Result |
|---|---|---|
| H0 · Product requirements and functional architecture | ✅ Reviewed | [Open H0](docs/stage-results.md#h0) |
| H1 · Physical product design | ✅ Reviewed | [Open H1](docs/stage-results.md#h1) |
| H2 · Production ECAD schematic | ✅ Reviewed and accepted | [H2 results](docs/stage-results.md#h2) |
| **H3 · Virtual electrical verification** | **▶️ Current** | [Current H3 results](docs/stage-results.md#h3) |
| H4 · Joined pre-layout gate | 🔒 Waiting for H1–H3 and firmware F3 | [H4 plan](docs/stage-results.md#h4) |
| H5 · Component evidence samples | 🔒 Waiting for H4 and cost approval | [H5 plan](docs/stage-results.md#h5) |
| H6 · PCB placement and routing | 🔒 Waiting for H5 | [H6 plan](docs/stage-results.md#h6) |
| H7 · Prototype fabrication and bring-up | 🔒 Waiting for H6, firmware F3 and order approval | [H7 plan](docs/stage-results.md#h7) |
| H8 · Physical qualification | 🔒 Waiting for H7 | [H8 plan](docs/stage-results.md#h8) |
| H9 · Manufacturing release | 🔒 Waiting for H8 and firmware F11 | [H9 plan](docs/stage-results.md#h9) |

**Hardware is at H3.** The accepted production schematic is undergoing virtual
electrical verification; PCB layout, target/emulator gate and every order
remain unauthorized.

<details open>
<summary><strong>Current H3 phase — exact detailed position</strong></summary>

<!-- current-substep: H3.3.4 -->

**Exact marker: `H3.3.4`** — the [IR path](docs/ir-electrical-verification.md)
is reviewed with no unresolved analytical finding; battery sensing,
thermistors and analog fault thresholds are being verified.

- ✅ `H1.8` — complete physical design accepted on 23 August 2026.
- ✅ `H2.0.1` — complete 1,035-row circuit inventory reviewed.
- ✅ `H2.0.2` — four projects, PCB boundaries and net names reviewed.
- ✅ `H2.0.3` — HW↔FW/BSP contract and cross-repository drift checks reviewed.
- ✅ `H2.1` — four independent KiCad projects and 28 native sheets created.
- ✅ `H2.2` — all ten UI/control PCB sheets reviewed.
- ✅ `H2.3` — all 12 functional RF/power PCB sheets are implemented and reviewed.
  - ✅ `H2.3.1` — `RF_00_ROOT`.
  - ✅ `H2.3.2` — `RF_01_USB_PD_CHARGE`.
  - ✅ `H2.3.3` — `RF_02_PACK_SAFETY_AON`.
  - ✅ `H2.3.4` — `RF_03_MAIN_RAILS_DOMAIN_GATES`.
  - ✅ `H2.3.5` — `RF_30_RP2354_CORE_SERVICE`.
  - ✅ `H2.3.6` — `RF_31_NRF24_X3`.
  - ✅ `H2.3.7` — `RF_32_SUBGHZ_VOICE`: 116 components, 363 physical
    contacts, independent CC1101/SA518 power, control and RF paths; reviewed.
  - ✅ `H2.3.8` — `RF_34_U214_M5_EXT`: 53 symbols, 52 board-fitted
    components, 228 contacts and two independently protected expansion paths;
    reviewed.
  - ✅ `H2.3.9` — `RF_35_REAR_CONTROLS`: seven fitted components, 36
    contacts and four independent direct controls; reviewed.
  - ✅ `H2.3.10` — `RF_36_AUDIO_IO_AMP`: 14 symbols, 34 contacts, exact
    microphone/amplifier footprints and two independent floating-BTL paths;
    reviewed.
  - ✅ `H2.3.11` — `RF_40_INTERBOARD_M1`: all 80 physical contacts and 51
    interfaces match UI-side M1 row-for-row; reviewed.
  - ✅ `H2.3.12` — `RF_50_TX_SAFETY_EVIDENCE`: 97 components and 369
    contacts, explicit AON power/bypass, hardware watchdog/latch/reset and five
    independent physical-RF evidence channels; reviewed.
  - ✅ `H2.3.13` — `RF_60_TESTPOINTS_MANUFACTURING`: 52 physical test pads,
    13 recovery paths and 6 RF-evidence channels; no purchased parts, child
    stubs or deferred fixture labels; reviewed.
- `H2.4` — display-adapter and LoRa Cap schematics.
  - ✅ `H2.4.1` — passive display adapter: both exact serial connectors, all
    40 one-to-one conductors and the manufacturer-derived FH34 footprint pass
    native KiCad review.
  - ✅ `H2.4.2` — LoRa Cap root, all three child sheets and the exact
    14-contact host boundary; native KiCad review passed.
  - ✅ `H2.4.3` — two exact regional one-of-two module options, direct final
    RF path, directional coupler, SMA and forward-power detector; reviewed.
  - ✅ `H2.4.4` — protected 3.3-V power and identity bus; eight serial
    components, 22 contacts and all five interfaces pass native KiCad review.
  - ✅ `H2.4.5` — independent physical-TX evidence: 11 serial components,
    34 contacts and a nominal 13.3-ms hardware pulse; native KiCad review passed.
- ✅ **`H2.5` — reviewed:** independent safety-path review.
  - ✅ `H2.5.1` — all sources, pack admission, charging and generated rails:
    [reviewed](docs/power-architecture.md).
  - ✅ `H2.5.2` — reset, boot, service and recovery:
    [reviewed](docs/service-recovery.md).
  - ✅ `H2.5.3` — no-back-power across USB, interboard and expansions:
    [reviewed](docs/interface-isolation.md).
  - ✅ `H2.5.4` — reset-safe quiet state and isolation of unused interfaces:
    [reviewed](docs/quiet-state.md).
  - ✅ `H2.5.5` — watchdog, thermal/fault supervision and `FAULT_KILL`:
    [reviewed](docs/fault-shutdown.md).
  - ✅ `H2.5.6` — [consolidated findings and closed review](docs/safety-review.md).
- ✅ `H2.6` — [native ERC and all 189 intentional NCs reviewed](docs/erc-review.md):
  four projects report zero native errors/warnings and every NC has a physical
  pin, exact marker and written rationale.
- ✅ `H2.7` — [H1, physical contacts, nets, M1 and firmware F2 reconciled](docs/hwfw-reconciliation.md):
  1,026 electrical identities, 266 root nets, 80 M1 contacts and 130
  controller allocations have zero remaining mismatch.
- ✅ **`H2.8` — reviewed:** formal final user acceptance before H3.
  - ✅ `H2.8.1` — [acceptance package and deferred gates prepared](docs/h2-acceptance.md).
  - ✅ `H2.8.2` — accepted by the user on 24 August 2026 at hardware
    `25d9ee2` / firmware `900bb2b`.
- ✅ **`H3.0` — reviewed:** reproducible virtual-verification inputs and methods.
  - ✅ `H3.0.1` — [accepted H2 input and all 16 verification domains frozen](docs/virtual-verification.md).
  - ✅ `H3.0.2` — [parameter and model register complete](docs/parameter-model-register.md);
    three full-function nRF24 modules remain.
  - ✅ `H3.0.3` — [methods and ten pass/fail rules frozen](docs/verification-methods.md).
- ✅ **`H3.1` — reviewed:** worst-case DC budget.
  - ✅ `H3.1.1` — [43 source/charge and 2,032 complete states enumerated](docs/power-state-register.md).
  - ✅ `H3.1.2` — [all 200 rail profiles pass](docs/dc-power-budget.md); one eFuse threshold mismatch was corrected.
  - ✅ `H3.1.3` — [all 2,032 source/charge/discharge states pass](docs/source-charge-budget.md).
  - ✅ `H3.1.4` — [DC evidence consolidated and reviewed](docs/dc-verification-result.md).
- ✅ **`H3.2` — reviewed:** power transitions and safety-loop dynamics.
  - ✅ `H3.2.1` — [startup, orderly shutdown and hard `FAULT_KILL`](docs/power-transition-startup.md).
  - ✅ `H3.2.2` — [USB↔pack handover, DPM and brownout](docs/power-handover.md).
  - ✅ `H3.2.3` — [eFuse, inrush and load steps](docs/inrush-load-step.md).
  - ✅ `H3.2.4` — [watchdog, retained fault record and fault-only UI](docs/watchdog-fault-display.md).
  - ✅ `H3.2.5` — [H3.2 consolidation](docs/power-transition-result.md); two source errors corrected.
- ▶️ **`H3.3` — current:** analog peripheral corners.
  - ✅ `H3.3.1` — [display supply, backlight and direct-QSPI reviewed](docs/display-electrical-verification.md); two source errors corrected.
  - ✅ `H3.3.2` — [codec, microphone, headset, speaker and voice TX reviewed](docs/audio-electrical-verification.md); four source errors corrected.
  - ✅ `H3.3.3` — [IR receive, transmit, optical evidence and thermal limits reviewed](docs/ir-electrical-verification.md); four source errors corrected.
  - ▶️ **`H3.3.4` — current:** battery sensing, thermistors and analog fault thresholds.
  - ⏳ `H3.3.5` — analog-corner consolidation.

The reviewed H2 plan is [`h2-schematic-plan.json`](hardware/ecad/h2-schematic-plan.json).
The current machine-readable plan is
[`h3-verification-plan.json`](hardware/verification/h3-verification-plan.json).
Closing each subtask changes this marker and both roadmap pages in the same commit.

</details>

Firmware F3 must already pass before H7: target skeletons for all five domains
build, image-size/rollback gates run, S3 executes in available QEMU, and C5,
RP2354B and MSPM0 code uses portable/host models plus later dev-board evidence
where no exact emulator exists. This is a pre-order H4 gate, so H7 fabrication
cannot bypass it.

<!-- BEGIN GENERATED PRINCIPLE DIAGRAMS -->

## Principle diagrams and electrical implementation

The device principle diagrams remain part of the site, but the landing page now routes to a [readable functional-domain atlas](docs/schematics.md). The [exact pin assignment](docs/pinout.md), [inter-board M1 map](docs/interconnect.md) and [hardware architecture](docs/hardware.md) are published alongside it.

<!-- END GENERATED PRINCIPLE DIAGRAMS -->

## Documentation

| Section | Contents |
|---|---|
| [Hardware architecture](docs/hardware.md) | Capabilities, MPNs and domain structure |
| [Principle diagrams](docs/schematics.md) | Component links and current KiCad sheets |
| [Pin assignment](docs/pinout.md) | Exact GPIOs, nets, directions and owners |
| [Inter-board M1](docs/interconnect.md) | All 80 contacts and physical crossing |
| [Memory and rollback](docs/memory.md) | Flash/PSRAM, partitions and recovery |
| [Safety](docs/safety.md) | Three feature levels, TX leases and FAULT_KILL |
| [LoRa Cap](docs/lora-cap.md) | Removable regional LoRa module |
| [Physical sources](docs/physical-source-register.md) | Envelope source for every body |
| [Stage results](docs/stage-results.md) | H0…H9 artifacts and evidence |

<div align="center">

**Leshy2 — see the spectrum, understand the path, stay in control.**

</div>
