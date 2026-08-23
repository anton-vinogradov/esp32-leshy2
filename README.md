<div align="center">

# ⭐ Leshy2

### An open autonomous multi-tool for radio, communications and authorized research

**2.4/5-GHz Wi‑Fi · BLE · 802.15.4 · 3× nRF24 · Sub‑GHz · VHF/UHF · FM/AM/SW/LW · IR · LoRa**

[Capabilities](docs/hardware.md) · [Mockup](#target-device-mockup) · [Schematics](docs/schematics.md) · [Roadmap](docs/roadmap.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware) · [Русский](README.ru.md)

**OPEN HARDWARE**　·　**MODULAR RF**　·　**FAIL-SAFE TX**　·　**REPAIRABLE**

</div>

> **Now: H2 · production ECAD schematic.** H1 physical design is accepted.
> PCB routing, purchasing and fabrication remain blocked.

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
| **H2 · Production ECAD schematic** | **▶️ Current** | [Current H2 results](docs/stage-results.md#h2) |
| H3 · Virtual electrical verification | ⏳ Waiting for H2 | [H3 plan](docs/stage-results.md#h3) |
| H4 · Joined pre-layout gate | 🔒 Waiting for H1–H3 and firmware F3 | [H4 plan](docs/stage-results.md#h4) |
| H5 · Component evidence samples | 🔒 Waiting for H4 and cost approval | [H5 plan](docs/stage-results.md#h5) |
| H6 · PCB placement and routing | 🔒 Waiting for H5 | [H6 plan](docs/stage-results.md#h6) |
| H7 · Prototype fabrication and bring-up | 🔒 Waiting for H6, firmware F3 and order approval | [H7 plan](docs/stage-results.md#h7) |
| H8 · Physical qualification | 🔒 Waiting for H7 | [H8 plan](docs/stage-results.md#h8) |
| H9 · Manufacturing release | 🔒 Waiting for H8 and firmware F11 | [H9 plan](docs/stage-results.md#h9) |

**Hardware is at H2.** The production schematic is being created; PCB layout
and the full target/emulator gate are not closed, and no order is authorized.

<details open>
<summary><strong>Current H2 phase — exact detailed position</strong></summary>

<!-- current-substep: H2.4.2 -->

**Exact marker: `H2.4.2`** — implement the LoRa Cap project root and exact
14-contact host interface.

- ✅ `H1.8` — complete physical design accepted on 23 August 2026.
- ✅ `H2.0.1` — complete 1,028-row circuit inventory reviewed.
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
  - ✅ `H2.3.13` — `RF_60_TESTPOINTS_MANUFACTURING`: 30 physical test pads,
    7 recovery paths and 6 RF-evidence channels; no purchased parts, child
    stubs or deferred fixture labels; reviewed.
- `H2.4` — display-adapter and LoRa Cap schematics.
  - ✅ `H2.4.1` — passive display adapter: both exact serial connectors, all
    40 one-to-one conductors and the manufacturer-derived FH34 footprint pass
    native KiCad review.
  - ▶️ **`H2.4.2` — current:** LoRa Cap root and 14-contact host interface.
  - ⏳ `H2.4.3` — LoRa radio, control and RF path.
  - ⏳ `H2.4.4` — protected power and identity bus.
  - ⏳ `H2.4.5` — independent physical-TX evidence.
- ⏳ `H2.5` — independent power/boot/recovery/quiet-state/`FAULT_KILL` review.
- ⏳ `H2.6` — close ERC and every intentional NC.
- ⏳ `H2.7` — reconcile schematic contacts with H1, M1 and firmware F2.
- 🔒 `H2.8` — formal final user acceptance before H3.

The exact machine-readable plan is
[`h2-schematic-plan.json`](hardware/ecad/h2-schematic-plan.json). Closing each
subtask changes this marker and both roadmap pages in the same commit.

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
