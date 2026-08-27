# H1-R2.6 · analog-FPV receive path

[Home](../README.md) · [Русский](h1-r2-fpv.ru.md)

The serial receiver functional candidate and exact antenna are selected; K331 physical acceptance is not claimed yet.

![Analog-FPV receive path](images/h1-r2-fpv-path.svg)

## Result

- `AKK K331` covers 5645–5945 MHz, draws at most 200 mA and emits 1-Vpp/75-ohm CVBS.
- CH1/CH2/CH3 use already-reserved Hub GPIO36/37/38; no new GPIO or expander is needed.
- The 5-V reserve retains 150 mA. RF runs directly over a 50-ohm PCB trace to MMCX without U.FL.
- `TBS5G8MMCXA` is linear, 5500–6000 MHz, 2.2 dBi and 102 mm; its exact kit mark is `FPV · RX 5.8G`. Independent linear fallback `FXP831.09.0100C` covers 4.9–6.0 GHz and retains MMCX, but is presently backorder-only with a 16-week lead time.

## Why K331 remains the leading candidate

- `AKK K331` — leading candidate: only option reviewed that fits the reserved pins, power and working envelope; controlled body/factory evidence remains open.
- `AWM682 RX` — rejected as primary: controlled body is more than twice the reserved area and its band/channel coverage is narrower.
- `TUE-RFVRX-58-D` — rejected as primary: exceeds the 350-mA reserve and the 11-mm interboard channel before tolerance.
- `generic RX5808` — rejected as production identity: published integration evidence exists but there is no unique manufacturer-controlled order code, drawing and factory route.

## Factory boundary

The manufacturer lists K331 in stock at $29.99; exact JLCPCB searches for `AKK K331`, `RX5808` and `RTC6715` returned zero results. It therefore remains a separate module until a private/global-sourcing response exists, not a claimed factory PCBA line item. The $6.95 antenna is a post-PCBA kit accessory and likewise not an assembly line item. On 2026-08-27, exact mechanical, assembly and sourcing evidence requests were sent to AKK and JLCPCB; both replies are pending.

## Open gates

- obtain AKK-controlled maximum dimensions, land pattern and packaging/reflow evidence
- obtain a JLCPCB private/global-sourcing response or retain explicit post-PCBA hand installation
- prove the direct 50-ohm feed, MMCX launch, channel truth table, sensitivity, image rejection, decoder lock and video quality on assembled hardware
- qualify FXP831.09.0100C on the assembled enclosure and secure available stock before relying on its current 16-week backorder route

> Exact current marker: **H1-R2.6**. H1 remains in progress.
