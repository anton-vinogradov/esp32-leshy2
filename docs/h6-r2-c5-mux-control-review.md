# H6 · C5 USB/SDIO mux control review

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-c5-mux-control-review.ru.md)

Status, 2026-09-14: **installed control/power-domain defects remain open; a correction candidate is under executable review, not implemented or production-selected.** This review does not authorize production or qualify switching timing. The routing-policy/native-alias correction protects the shared data pair; it does not repair the control circuit described here. See [current routing](h6-r2-current-routing.md) for the separate board checkpoint.

## What the circuit must do

C5 GPIO13 is USB D− / SDIO DAT3; GPIO14 is USB D+ / SDIO DAT2. The FSUSB42 mux selects service USB at `SEL=0`, runtime SDIO at `SEL=1`, and disconnects both branches at `OE=1`.

The [mux contract](../hardware/architecture/c5-sdio-service-mux-contract.json) requires asynchronous hardware seizure of service ownership, Hub reset while service owns the interface, and a disconnected interval before changing branch in **both** directions. Ownership may clear only with service VBUS absent, C5 reset asserted, Hub reset/high-impedance proof and an explicit always-on release request. These are requirements, not proof that the present implementation meets them.

## Confirmed physical graph

The [R2 topology overrides](../hardware/ecad/h2-r2-topology-overrides.json), [native net ledger](../hardware/ecad/generated/H2-R2-native-net-ledger.json), and native UI/RF pad memberships agree on these connections:

| Signal | Exact current endpoints / function |
| --- | --- |
| `C5_MUX_SEL` | UI U22.2 and R92.1 only; R92.2 is ground. **No active selector driver.** |
| `C5_MUX_SEL_REQUEST` | RF U111.15 (`P12`) → J12.55 / UI J18.55 → R87.1. RF R255.1 also biases this request; both resistors return to ground. This is not the SEL net. |
| `C5_SERVICE_PATH_ACK` | RF U111.16 (`P13`) → J12.56 / UI J18.56 → U17.1. RF R256 supplies its pull-down default. |
| `AON_SERVICE_RELEASE_REQ` | RF U111.17 (`P14`) → M1 pin 57 → UI U19.5; one input of the qualified owner-clear gate. |
| `C5_SERVICE_OWNED` | UI U18.5 → U19.9, Hub-reset sink Q2.5 and M1 pin 58 → RF U111.18 (`P15`, observation). |
| `C5_MUX_DISABLE` / OE | UI U17.4 → U22.10, C5-reset sink Q3.1 and R91.1; R91.2 is ground. |

Here M1 means UI J18 mating with RF J12. U111 is the always-on safety controller's TCA9535 expander, not a direct C5/Hub/S3 firmware output. The separate REQUEST/SEL names do not establish a missing buffer implementation: no concrete qualified-selector driver is present in the reviewed graph.

The installed U17 inverter / U19 NAND connections give:

```text
ACK_N = NOT ACK
DISABLE_N = NOT (OWNER AND ACK_N)
OE = OWNER AND NOT ACK
```

| OWNER | ACK | Current OE | Consequence |
| ---: | ---: | ---: | --- |
| 0 | 0 or 1 | 0 | No commanded disconnection is possible during runtime / after owner clear. |
| 1 | 0 | 1 | Both branches disconnected; Q3 asserts C5 reset. |
| 1 | 1 | 0 | Selected branch connected; OWNER still holds Hub reset. |

Thus the undriven, pulled-low SEL cannot select runtime SDIO. Separately, the OE equation cannot perform the required disconnected interval for both transition directions. On asynchronous service seizure with ACK still high, this OE path also does not assert C5 reset. Merely joining REQUEST to SEL, or renaming the data nets, does not resolve these defects.

The existing [digital-interface checks](../hardware/verification/h3_r2_digital_interfaces.py) check defaults, data endpoints and the presence of latch/reset components. Those checks do not establish an active selector driver or the transition truth table. Zero native DRC is likewise not functional proof.

## Correction candidate, not the installed circuit

The [executable candidate](../hardware/verification/c5_mux_control_candidate.py) and [regression tests](../hardware/architecture/tests/test_c5_mux_control_candidate.py) separate Boolean/order checks from real electrical and timing evidence. Define `O=OWNER`, `R=REQUEST`, `A=ACK` used as **permission to connect**, `L=RELEASE_REQ`, `P=RUN_PERMIT`, and `F=FAULT_ASSERT_N`:

```text
SEL = R
VALID = NOT (O AND R)
OE = NOT (A AND VALID AND P AND F)
HUB_HOLD = O OR L OR NOT R
```

This permits a commanded disconnection in either mode, vetoes SDIO while service owns the interface, and always holds Hub in reset while USB is selected. Existing independent KILL/fault reset sinks stay in place. No additional M1 signal or GPIO is needed. The candidate reuses the qualified owner-clear NAND, repurposes the other U19 NAND and both U17 inverters, and adds one dual four-input NAND plus bypass. Output loading still needs closure before choosing the fitted gate/bias combination.

Use U17 to generate `NOT O` and `NOT L`; **do not substitute U18.Q_N for `NOT O`**. The SN74LVC1G74 function table permits both Q and Q_N HIGH while preset and clear are simultaneously asserted. A direct Q_N-based Hub gate could then release Hub. Deriving the inversion from Q removes that specific counterexample, not the remaining asynchronous-latch timing obligations. [TI function table 8-1](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf).

The ordered protocol is equally important:

- USB takeover: a hot-inserted service owner first disconnects an active SDIO branch and holds both processors reset. Explicitly write `A=0`, hold Hub with `L=1`, establish reset/high-Z, then change `R=0`; connect with `A=1` only after settling. Changing R while A remains 1 is rejected.
- Return to SDIO: with service VBUS absent, establish `L=1` and `A=0` before changing R. Select `R=1`, clear ownership only through the existing qualified-clear conditions, then connect with `A=1`. Hold Hub through C5 reset release and at least the 3 ms strap interval; release L only after the required startup/ready condition. Separate, confirmed expander writes are required, not one combined selector/enable write.
- Wait markers in the model are **assumptions**, not measured delays. Bad firmware, an interrupted flash and a failed I2C transaction require the real Safety service manager, ROM entry and fail-closed handling; that manager is not implemented by this model.

## Power-domain and factory-part review

The current FSUSB42 has another independent defect: its SEL/OE absolute maximum is **its own VCC**, but these controls are powered from AON while U22 uses MAIN. The switch-port power-off isolation does not protect its control inputs. Moving only the selector wire is therefore insufficient. Moving U22 to AON would remove that voltage conflict, but could leave the data path connected after MAIN collapses unless an independently bounded MAIN-invalid interlock is provided. [onsemi, limits and electrical tables, pp. 3–4](https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf).

TI TS3USB221E is the leading **unselected** alternative: 2.3–3.6 V supply, control-input leakage specified at VCC=0 with VIN up to 3.6 V, and separate powered-off switch-port leakage. It could remain on MAIN without the FSUSB42 control-overvoltage problem. This does **not** establish behavior during `0 < VCC < 2.3 V`, settle the project's open MAIN voltage margin, or qualify SDIO. Its pinout is not interchangeable: pins 1–10 are USB+, USB−, SDIO DAT2, SDIO DAT3, GND, OE, common−, common+, SEL, VCC. [TI TS3USB221E, pp. 3–6](https://www.ti.com/lit/ds/symlink/ts3usb221e.pdf).

Read-only live JLCPCB observations from this session, recorded **2026-09-14T00:03:22Z**; no order or library purchase:

| Exact part / JLC number | Factory route and observed quantity | MOQ / USD unit price |
| --- | --- | --- |
| Texas Instruments [TS3USB221ERSER / C129313](https://jlcpcb.com/partdetail/TexasInstruments-TS3USB221ERSER/C129313) | Extended, SMT, Economic + Standard; stock 2,998, available 2,993 | 1; $0.3416 at 1, $0.2678 at 50, $0.2360 at 150, $0.1967 at 500, $0.1791 at 3,000, $0.1685 at 6,000 |
| Texas Instruments [TS3USB221EDRCR / C130084](https://jlcpcb.com/partdetail/TexasInstruments-TS3USB221EDRCR/C130084) | Extended, SMT, Economic + Standard; stock 0; explicit Pre-order offered, lead time not established | 8; estimated $1.1393 |

The RSE footprint is 1.5 × 2 mm with **ten pads and no exposed pad**, despite the JLC catalog's “EP” label. The checked KiCad `Texas_UQFN-10_1.5x2mm_P0.5mm` fits U22's current corridor; the larger DRC library courtyard does not fit there without repositioning. RSE needs microscope/hot-air rework, so it is not described as hand-solder-friendly. U22's ten current nets have no copper items yet; the replacement would still require remapping all contacts and moving C28 near the new VCC pin. Hub/RF FSUSB42 instances must not be changed through a shared definition.

The candidate's reused Nexperia [74HC20PW,118 / C546719](https://jlcpcb.com/partdetail/Nexperia-74HC20PW118/C546719) and YAGEO [CC0402KRX7R9BB104 / C131394](https://jlcpcb.com/partdetail/YAGEO-CC0402KRX7R9BB104/C131394) were checked at **2026-09-13T23:35:36Z**: both SMT, Economic + Standard, MOQ 1; respectively stock/available 21,855/21,854 at $0.2452 and 7,667,848/7,238,354 at $0.0103. These observations support sourcing evaluation, not electrical acceptance; recheck selected MPNs at freeze and immediately before order.

### Output-loading gate

At the conditional AON range 3.181696–3.376 V, R91=100 kΩ ±1% alone loads HIGH OE by up to 34.10 µA, exceeding the HC20 table's 20 µA light-load condition. Changing it to 1 MΩ reduces load but does not itself prove VOH throughout this supply range. **SN74LV20A**, not an assumed “74LVC20A”, has compatible TSSOP-14 pins and guarantees VOH≥VCC−0.1 V / VOL≤0.1 V at 50 µA throughout VCC=2–5.5 V. It is a candidate for both NAND packages, not a fitted replacement. [HC20 electrical table](https://assets.nexperia.com/documents/data-sheet/74HC20.pdf), [TI LV20A, sections 3/4.5](https://www.ti.com/lit/ds/symlink/sn74lv20a.pdf).

Live [SN74LV20APWR / C2862070](https://jlcpcb.com/partdetail/TexasInstruments-SN74LV20APWR/C2862070), recorded **2026-09-14T00:10:12Z**: Texas Instruments, Extended, SMT, Economic + Standard, stock 0, explicit Pre-order, MOQ 21, estimated $0.4265 each; lead time unestablished. This is not an in-stock solution. Independently, Q2 **2N7002DW** specifies RDS(on) at 5/10 V gate drive, not the proposed ~3.08 V guaranteed HIGH. Gate threshold or room-temperature typical curves do not prove reset LOW. Close the sink/leakage/temperature budget and TCA9535-to-gate thresholds before implementation. [Diodes Q2 electrical table](https://www.diodes.com/assets/Datasheets/2N7002DW.pdf). The AON range itself remains an unqualified rail-model premise.

## Unclosed invariants and next step

Finish control-output loading and power-sequence review, then integrate one coherent native correction: driver graph, mux MPN/pinout/footprint/bypass, source contracts and firmware boundary. The candidate above is not evidence that the installed circuit changed. Joining REQUEST to SEL alone is not an accepted correction.

Actual mux turn-off, RP2354 reset-to-pad-high-Z delay, expander initialization, power-up and hot insertion/removal still need a complete sequence review. A reset-line observation is not itself a measured pad-high-Z delay. A minimum break-before-make interval is not a maximum switching delay; the contract's 1 µs waits remain to be justified. The present Q3 connection also couples mux reconnection to C5 reset release, which must be reconciled with strap setup and the required 3 ms hold.

USB differential geometry remains mandatory for the shared segment in either mode, alongside—not instead of—single-ended SDIO signal integrity, full CLK/CMD/DAT0–3 timing and the existing 20/40 MHz/HIL obligations. No PCB, MPN, firmware or production gate is changed by this report.
