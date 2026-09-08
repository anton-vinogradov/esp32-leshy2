<div align="center">

# Leshy2 ⭐

### An open standalone pocket tool for radio, communication and authorised research

**2.4/5-GHz Wi‑Fi · BLE · 802.15.4 · 3× nRF24 · Sub‑GHz · VHF/UHF · FM/AM/SW/LW/Airband · IR · LoRa/CC1101+NFC Cap**

[Capabilities](docs/hardware.md) · [Roadmap](docs/roadmap.md) · [Stage reports](docs/stage-results.md) · [Schematics](docs/schematics.md) · [Firmware](https://github.com/anton-vinogradov/esp32-leshy2-firmware) · [Русский](README.ru.md)

</div>

<!-- current-substep: H6.0.3-R1 -->

## What we want

Leshy2 is intended to be a repairable hobby device combining spectrum
observation, communication, diagnostics and safe experimentation without a
mandatory laptop. The first order targets one genuinely working prototype:
the factory supplies two populated PCBAs and the owner completes a simple,
solder-free final assembly.

| Area | Intended result |
|---|---|
| Radio | S3 Wi‑Fi/BLE, C5 2.4/5-GHz Wi‑Fi and 802.15.4, 3× full nRF24, CC1101, VHF/UHF voice, FM/AM/SW/LW/Airband RX and IR |
| Interface | 3.5-inch 320×480 touch IPS, direct i8080‑8, buttons, encoder, microSD and audio |
| Expansion | Protected Cap slot for U214 LoRa or U219 CC1101+NFC and an M5 Unit port |
| Reliability | Four independent USB ports, accessible recovery, hardware TX evidence and fail-closed safety |

Transmission and hazardous laboratory functions are constrained by the
[safety model](docs/safety.md); the device is only for lawful use with the
system owner's permission.

## What we decided

- Two 80 × 150-mm six-layer boards: front UI/radio and rear RF/power.
- Six compute domains: S3, C5, front Hub RP, rear RF RP, Pack and Safety.
- Ten permanent antenna ports are split 5+5; each RF path remains board-local and reaches its external connector directly or through one removable microcoax.
- The EastRising `ER-TFT035IPS-6 + ER-TPC035-6` display connects directly to S3 through a 50-contact ZIF and i8080‑8; its FPC points toward the antenna edge, folds without twist and retains at least 5 mm of relaxed reserve.
- The factory fabricates and populates two PCBAs. Without soldering, the owner fits the display on a stock rectangular PSA pad, five microcoax jumpers, knob, fasteners and enclosure.
- The 80-contact M1 carries no structural load; four nylon screws, compression stops and the enclosure carry it.
- The 80 × 150-mm outline remains while routing meets its rules. If a required power, USB/i8080 or RF path cannot route after legal local rearrangement, the next candidate is 85 × 150 mm followed by complete requalification.

## What is designed

### Physical layout

The current preview below is composed from the actual PCBs: exterior faces share one scale, without an extra rear-board mirror. Only the installed display panel's envelope is added in blue. This is not an assembled 3D validation. Inspect the inner sides in [all four current component views](docs/h6-r2-component-views.md). Coordinates and cable paths are available in the [exact-placement](docs/h6-r2-exact-placement.md) and [microcoax](docs/h6-r2-microcoax-service.md) views.

![Current native PCB arrangement with the display-panel envelope](docs/images/h6-r2-product-exterior.svg)

H1-to-native correspondence is not fully verified: H1 remains a concept archive, not a picture of current positions. [H6 corrections and open interface findings](docs/h6-r2-interface-review.md) describe the current boards.

[Placement corrections and their verification](docs/h6-r2-placement-repair.md) explain the holder, encoder, port/card access and internal audio assembly. The routing phase is still open.

[Component unification](docs/h6-r2-component-unification.md): GCT USB4105-GF-A ×4 is installed on the native boards; fresh DRC/parity and preservation checks pass. Other candidates and necessary functional differences remain separate.

[Archive: H1 concept four-face Leshy2 mock-up](docs/images/h1-r2-four-faces.svg?rev=h1-r2.39-views-20260907)

[Legend for 223 H1 concept bodies](docs/images/h1-r2-component-legend.svg?rev=h1-r2.39-views-20260907) ·
[physical-design report](docs/h1-r2-physical-layout.md) ·
[functional-architecture report](docs/h0-r2-functional-architecture.md) ·
[front inner face](docs/images/h1-r2-inner-ui.svg) ·
[rear inner face](docs/images/h1-r2-inner-rf.svg) ·
[display mounting](docs/images/display-mount.svg) ·
[physical sections](docs/images/h1-r2-inner-sections.svg)

![Leshy2 functional architecture](docs/images/h0-r2-functional-architecture.svg)

### Current routing

These are exports from the live `.kicad_pcb` files, not illustrative mock-ups.
Open either board for the full-size SVG.

<table>
  <tr>
    <td width="50%"><a href="docs/images/h6-r2-routing-ui.svg"><img src="docs/images/h6-r2-routing-ui.svg" alt="Current UI-board routing" width="100%"></a></td>
    <td width="50%"><a href="docs/images/h6-r2-routing-rf.svg"><img src="docs/images/h6-r2-routing-rf.svg" alt="Current RF/power-board routing" width="100%"></a></td>
  </tr>
  <tr><td align="center">UI PCB</td><td align="center">RF / power PCB</td></tr>
</table>

### Current components · both faces

All four views use the same scale. Outer faces are above; inner faces below
are viewed after turning each board over, with the antenna edge still at the top.
Grey shows component outlines/references; blue is actual silkscreen.
Known footprint defects remain visible — these views do not certify assembly.
[Full-size views and legend](docs/h6-r2-component-views.md). Gold shows all 50 SMA lands and the two-sided copper lands of USB, Cap and encoder interfaces; NFC endpoints are distinguished in the legend.

<table>
  <tr><th width="50%">Front / UI</th><th width="50%">Rear / RF-power</th></tr>
  <tr>
    <td><a href="docs/images/h6-r2-components-ui-outer.svg"><img src="docs/images/h6-r2-components-ui-outer.svg" alt="UI components, outer face" width="100%"></a></td>
    <td><a href="docs/images/h6-r2-components-rf-outer.svg"><img src="docs/images/h6-r2-components-rf-outer.svg" alt="RF components, outer face" width="100%"></a></td>
  </tr>
  <tr>
    <td><a href="docs/images/h6-r2-components-ui-inner.svg"><img src="docs/images/h6-r2-components-ui-inner.svg" alt="UI components, inner face after turning over" width="100%"></a></td>
    <td><a href="docs/images/h6-r2-components-rf-inner.svg"><img src="docs/images/h6-r2-components-rf-inner.svg" alt="RF components, inner face after turning over" width="100%"></a></td>
  </tr>
</table>

Component views refresh together with routing exports; the common freshness
check rejects images that no longer match the PCB files.

## What we obtained and verified

**Current hardware marker: `H6.0.3-R1`.**

- The historical H0–H5 reviews, including H2 native production ECAD, retain their own baseline scope; their reports are collected in [one index](docs/stage-results.md).
- **Current H3 is `review_required`.** The [current analytical result](docs/h3-r2-acceptance.md) and [rail-voltage paths](docs/power-rail-margins.md) now use the fitted MAIN converter/divider/current-setting resistor. They expose current and voltage shortfalls; MAIN temperature is not established. The MAIN/AON circuit remains unqualified for production or battery energization.
- Both native KiCad boards pass the current [exact-placement checks](docs/h6-r2-exact-placement.md).
- Manufacturer-drawing corrections are being integrated into both PCBs. The [native interface review](docs/h6-r2-interface-review.md) separates applied corrections from remaining assembly gates; clean DRC alone does not prove physical assembly.
- Routing is in progress. Live copper/connectivity counts, hash-bound DRC results and the electrical-review limitations have one owner: [H6.0.3-R1](docs/h6-r2-current-routing.md).
- Native ERC currently uses passive symbol pins; zero findings do not prove correct rail sources or compatible outputs. This electrical-semantics gap blocks release; [corrected pin mappings and partial typed-ERC review](docs/h6-r2-electrical-semantics.md) describe the current evidence and remaining work.

## What remains

1. Correct the native interface/assembly findings and close the electrical-pin/rail-source review gap, then finish every connection and zero schematic-to-PCB parity in H6.0.3.
2. Re-run power/thermal, USB/i8080/M1, RF/Airband, plane and return-current checks on the actual copper.
3. Check STEP, enclosure, cables and final assembly; produce Gerber/BOM/CPL and complete independent DFM/CPL review.
4. Build the first-spin firmware package: reproducible images, fake HAL, available emulation, display test patterns and a safe first-power-on procedure.
5. Immediately before ordering, recheck every exact MPN against JLCPCB Standard PCBA stock/MOQ/price and approve the single actual quote.

Ordering and fabrication remain blocked.

## How the documentation is organised

Each kind of information now has one owner so the same decision is not retold
on several pages:

| Document | Sole role |
|---|---|
| This page | Product story: intent → decisions → implementation → result → remaining work |
| [Roadmap](docs/roadmap.md) | Stage order, current marker and transition criteria only |
| [Stage reports](docs/stage-results.md) | Links to immutable completed-phase results only |
| [Physical design](docs/h1-r2-physical-layout.md), [schematics](docs/schematics.md), [cost](docs/h1-r2-cost.md) | Detail for one subject area |
| `hardware/**/generated` and release contracts | Machine-checkable truth |

Navigation links may repeat; substantive claims belong to their one owner. The
English pages are translations of the Russian pages with the same structure,
not a second independent narrative.

Licensed under [CERN Open Hardware Licence Version 2 — Strongly Reciprocal](LICENSE).
