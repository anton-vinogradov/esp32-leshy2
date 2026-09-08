# H6 · C5 USB/SDIO mux control review

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-c5-mux-control-review.ru.md)

Status, 2026-09-08: **confirmed open control-topology defect; correction not selected or implemented.** This review does not authorize production or qualify switching timing. The routing-policy/native-alias correction protects the shared data pair; it does not repair the control circuit described here. See [current routing](h6-r2-current-routing.md) for the separate board checkpoint.

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

## Unclosed invariants and next step

The correction must establish a driven selector, hardware service-owner veto, and commanded disconnection in both transition directions. The four M1 signals and existing owner-clear/reset dependencies must be evaluated together; no new control topology or replacement MPN is selected by this report. Joining REQUEST to SEL alone is not an accepted correction.

Actual mux turn-off, RP2354 reset-to-pad-high-Z delay, expander initialization, power-up and hot insertion/removal still need a complete sequence review. A reset-line observation is not itself a measured pad-high-Z delay. A minimum break-before-make interval is not a maximum switching delay; the contract's 1 µs waits remain to be justified. The present Q3 connection also couples mux reconnection to C5 reset release, which must be reconciled with strap setup and the required 3 ms hold.

USB differential geometry remains mandatory for the shared segment in either mode, alongside—not instead of—single-ended SDIO signal integrity, full CLK/CMD/DAT0–3 timing and the existing 20/40 MHz/HIL obligations. No PCB, MPN, firmware or production gate is changed by this report.
