# H6 · C5 USB/SDIO mux control review

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-c5-mux-control-review.ru.md)

Status, 2026-09-14: **the TS3/LV correction is implemented in source and native ECAD, not merely proposed.** Source/H3 topology checks and the full 17-step H6 refresh pass; both corrected native boards have zero DRC violations and zero schematic-parity errors. This is an engineering schematic selection, not completed routing, electrical/HIL or production qualification. The Safety service manager is **not implemented**, and hardware KILL/fault policy is unchanged. See [current routing](h6-r2-current-routing.md) for the board checkpoint.

## What the circuit must do

C5 GPIO13 is USB D− / SDIO DAT3; GPIO14 is USB D+ / SDIO DAT2. The current TS3USB221ERSER mux selects service USB at `SEL=0`, runtime SDIO at `SEL=1`, and disconnects both branches at `OE=1`.

The [mux contract](../hardware/architecture/c5-sdio-service-mux-contract.json) requires asynchronous hardware seizure of service ownership, Hub reset while service owns the interface, and a disconnected interval before changing branch in **both** directions. Ownership may clear only with service VBUS absent, C5 reset asserted, Hub reset/high-impedance proof and an explicit always-on release request. These are requirements, not proof that the present implementation meets them.

## Defects retained as pre-correction history

Before this correction, `C5_MUX_SEL` connected only U22.2/R92.1, while the expander drove the separate `C5_MUX_SEL_REQUEST`. The old U17/U19 chain produced `OE = OWNER AND NOT ACK`: runtime could not command disconnection, and asynchronous ownership with ACK high did not assert C5 reset. These are historical findings, not the current graph. The [topology source](../hardware/ecad/h2-r2-topology-overrides.json) and [net ledger](../hardware/ecad/generated/H2-R2-native-net-ledger.json) now describe the correction below.

The former presence-only digital checks did not detect those faults. The [current H3 checks](../hardware/verification/h3_r2_digital_interfaces.py) now join exact part identities, physical pins and complete control-net membership. Their [source-topology PASS](../hardware/verification/generated/H3-R2-digital-interfaces.json) is not routed-signal or functional proof.

## Implemented control topology; execution still open

The [executable candidate](../hardware/verification/c5_mux_control_candidate.py) and [regression tests](../hardware/architecture/tests/test_c5_mux_control_candidate.py) separate Boolean/order checks from real electrical and timing evidence. Define `O=OWNER`, `R=REQUEST`, `A=ACK` used as **permission to connect**, `L=RELEASE_REQ`, `P=RUN_PERMIT`, and `F=FAULT_ASSERT_N`:

```text
SEL = R
VALID = NOT (O AND R)
OE = NOT (A AND VALID AND P AND F)
HUB_HOLD = O OR L OR NOT R
```

The settled Boolean model permits commanded disconnection in either mode, vetoes SDIO during service ownership and holds Hub reset while USB is selected. UI U19 and added U59 use SN74LV20APWR; C86 is the added bypass. U19 retains the four-condition owner-clear gate and generates VALID; U59 generates OE and HUB_HOLD. U17 generates NOT(O)/NOT(L), and U18.Q_N is NC. `C5_MUX_SEL_REQUEST` now directly reaches U22.9; U59.6 drives U22.6/Q3.G, and U59.8 drives UI Q2.5. RF U111 P12/P13/P14 remain R/A/L through existing M1 contacts. No additional M1 signal or GPIO is needed. Board dimensions and all 857 copper objects' geometry/UUIDs are preserved; routing is not complete.

Use U17 to generate `NOT O` and `NOT L`; **do not substitute U18.Q_N for `NOT O`**. The SN74LVC1G74 function table permits both Q and Q_N HIGH while preset and clear are simultaneously asserted. A direct Q_N-based Hub gate could then release Hub. Deriving the inversion from Q removes that specific counterexample, not the remaining asynchronous-latch timing obligations. [TI function table 8-1](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf).

The ordered protocol is equally important:

- USB takeover: a hot-inserted service owner first disconnects an active SDIO branch and holds both processors reset. Explicitly write `A=0`, hold Hub with `L=1`, establish reset/high-Z, then change `R=0`; connect with `A=1` only after settling. Changing R while A remains 1 is rejected.
- Return to SDIO: with service VBUS absent, establish `L=1` and `A=0` before changing R. Select `R=1`, clear ownership only through the existing qualified-clear conditions, then connect with `A=1`. Hold Hub through C5 reset release and at least the 3 ms strap interval; release L only after the required startup/ready condition. Separate, confirmed expander writes are required, not one combined selector/enable write.
- Wait markers in the model are **assumptions**, not measured delays. Bad firmware, an interrupted flash and a failed I2C transaction require the real Safety service manager, ROM entry and fail-closed handling; that manager is not implemented by this model.

## Power-domain and factory-part review

The former C5 FSUSB42 had a separate domain defect: SEL/OE absolute maximum equals **its own VCC**, while AON drove those pins with U22 on MAIN. Port power-off isolation did not protect the controls; connecting REQUEST alone could not correct this. The Hub/RF FSUSB42 instances are unchanged. [onsemi, pp. 3–4](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf).

TI TS3USB221ERSER is now the engineering selection on MAIN: 2.3–3.6 V supply, control-input leakage specified at VCC=0 with VIN up to 3.6 V, and separate powered-off port leakage. This removes the former absolute-maximum mismatch at those specified endpoints, **not** uncertainty during `0 < VCC < 2.3 V`, the open MAIN voltage margin or SDIO qualification. The remapped pins 1–10 are USB+, USB−, SDIO DAT2, SDIO DAT3, GND, OE, common−, common+, SEL, VCC. [TI, pp. 3–6](https://www.ti.com/lit/ds/symlink/ts3usb221e.pdf).

Read-only live JLCPCB observations from this session, recorded **2026-09-14T00:03:22Z**; no order or library purchase:

| Exact part / JLC number | Factory route and observed quantity | MOQ / USD unit price |
| --- | --- | --- |
| Texas Instruments [TS3USB221ERSER / C129313](https://jlcpcb.com/partdetail/TexasInstruments-TS3USB221ERSER/C129313) | Extended, SMT, Economic + Standard; stock 2,998, available 2,993 | 1; $0.3416 at 1, $0.2678 at 50, $0.2360 at 150, $0.1967 at 500, $0.1791 at 3,000, $0.1685 at 6,000 |
| Texas Instruments [TS3USB221EDRCR / C130084](https://jlcpcb.com/partdetail/TexasInstruments-TS3USB221EDRCR/C130084), retained unselected alternative | Extended, SMT, Economic + Standard; stock 0; explicit Pre-order offered, lead time not established | 8; estimated $1.1393 |

The implemented RSE footprint is 1.5 × 2 mm with **ten pads and no exposed pad**, despite the JLC “EP” label. Contacts and local bypass placement have been updated; existing copper is preserved, not newly routed. RSE needs microscope/hot-air rework and is not described as hand-solder-friendly.

Historical sourcing at **2026-09-13T23:35:36Z** recorded HC20/C546719 stock/available 21,855/21,854 at $0.2452 and bypass C131394 7,667,848/7,238,354 at $0.0103, both SMT Economic + Standard, MOQ 1. HC20 is no longer the chosen C5 NAND; these observations do not qualify the circuit. Recheck selected MPNs at freeze and before order.

### Output-loading gate

At conditional AON 3.181696–3.376 V, R91=100 kΩ ±1% alone loads HIGH OE by up to 34.10 µA, outside HC20's 20 µA light-load condition. The selected **SN74LV20A** has compatible TSSOP-14 pins and VOH≥VCC−0.1 V / VOL≤0.1 V at 50 µA throughout VCC=2–5.5 V. This supports the engineering choice, not full fan-out/leakage or power-ramp qualification. [HC20 table](https://assets.nexperia.com/documents/data-sheet/74HC20.pdf), [TI LV20A](https://www.ti.com/lit/ds/symlink/sn74lv20a.pdf).

Live [SN74LV20APWR / C2862070](https://jlcpcb.com/partdetail/TexasInstruments-SN74LV20APWR/C2862070), recorded **2026-09-14T00:10:12Z**: TI, Extended SMT, Economic + Standard, **stock 0, explicit Pre-order, MOQ 21**, estimated $0.4265 each; no established lead time. Two fitted parts allocate $0.8530 to one product, not a two-piece order; the estimated MOQ material minimum is $8.9565 before other charges.

Three reset packages—UI Q2/Q6 and RF Q6—now use **NX3008NBKS,115**, with logical half names remapped to preserve physical pins; UI Q2.5 intentionally changes from OWNER to HUB_HOLD. Its 2.8 Ω maximum at VGS=1.8 V is a **25 °C** condition, not a full-temperature reset-low guarantee. Pack RF Q2/Q3 remain 2N7002DW and **unqualified**; their cell-side startup is not validated by the reset substitution. [Nexperia primary](https://assets.nexperia.com/documents/data-sheet/NX3008NBKS.pdf). Existing independent KILL/fault sinks remain active.

## Unclosed invariants and next step

The coherent source/native correction and H6 refresh are complete; the remaining qualification is separate. No top-level hardware or firmware phase is closed by this change.

Actual mux turn-off, RP2354 reset-to-pad-high-Z delay, expander initialization, power-up and hot insertion/removal remain unmeasured. The old 1 µs assurance is removed: waits are explicit model assumptions, and a reset observation is not pad-high-Z timing. Q3 couples reconnection to C5 reset release; L must hold Hub through the required ≥3 ms strap interval and readiness. The resistor-only VBUS gate estimate also does not establish leakage/temperature or asynchronous latch behavior. The required Safety service manager and KILL/update-policy resolution are still open.

USB differential geometry remains mandatory alongside single-ended SDIO and full CLK/CMD/DAT0–3 timing: 20 MHz is bring-up only; 40 MHz / 7.5 MB/s remains a HIL target, not an achieved throughput. No production release follows from source tests or clean DRC.
