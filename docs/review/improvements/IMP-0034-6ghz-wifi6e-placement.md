# IMP-0034 — place 6 GHz/Wi-Fi 6E in the product architecture

- Статус: **⚠️ Требуется решение владельца**
- Дата: 2026-08-17
- Delta: `W-EXTRA-17`
- Evidence: [`AUD-0012`](../audits/AUD-0012-6ghz-wifi6e-product-scope.md)
- Finding: [`FND-0048`](../findings/FND-0048-5ghz-does-not-imply-6ghz.md)

## Контекст

6 GHz is radio work and fits the refined mission, but it is a separate physical
capability. The accepted autonomous 2.4/5 GHz target remains unchanged in every
option. Current ESP32-C5 does not reach 6 GHz; current 6E parts are host-attached
SDIO/PCIe radios with additional antenna, software, power and regional
qualification burden.

## Options

### A — native 6 GHz in every base architecture

Every complete Leshy2 candidate must autonomously provide qualified 6 GHz
discovery, STA diagnostics and the explicitly allowed active/Lab profiles.

- Плюсы: strongest all-in-one radio coverage; no external module for ordinary
  6E work; competitor gap closes in the base product.
- Минусы: immediately constrains compute/interconnect, RF paths, antennas,
  enclosure, battery, driver stack and certification; raises base cost for every
  unit before we have measured use frequency or an MCU-class implementation.

### B — preserve 6 GHz as a qualified optional radio/compute profile

The base remains autonomous at 2.4/5 GHz. G3/G4 preserve a credible attachment
envelope only after an exact 6E profile defines results, transport, power,
mechanics, host/driver and regional modes. It may become a detachable module or
an owner-controlled companion; it gets no base component or assumed connector.

- Плюсы: retains a mission-aligned upgrade path and lets current 6E silicon
  mature without forcing Linux/M.2/PCIe or a second high-band radio into every
  device; protects cost, size and runtime.
- Минусы: 6 GHz is not an out-of-box base result; a future profile may expose
  that no acceptable transport/host envelope fits and require a new hardware
  revision or companion compute.

### C — reject 6 GHz from the target

Leshy2 stops at autonomous 2.4/5 GHz; owners use a separate instrument for 6E.

- Плюсы: smallest scope and no 6E-driven architecture/certification burden.
- Минусы: intentionally leaves a growing radio band uncovered and removes the
  preserved upgrade path despite strong mission fit.

## Recommendation

Choose **B**. It preserves the capability honestly while avoiding premature
base cost and a hidden application-processor architecture. Unlike generic USB
host, 6 GHz itself is a valid radio result; therefore rejection is unnecessary.
Unlike accepted 5 GHz, current evidence is not strong enough to make it a
zero-loss base invariant before G3/G4 compare form factor, cost and host burden.

## Decision question

Choose `A`, `B` or `C`. No option changes the accepted 2.4/5 GHz baseline.
