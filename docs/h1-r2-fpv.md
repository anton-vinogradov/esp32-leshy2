# H1-R2.5 · analog-FPV receive path

[Home](../README.md) · [Русский](h1-r2-fpv.ru.md)

The serial receiver functional candidate and exact antenna are selected; K331 physical acceptance is not claimed yet.

![Analog-FPV receive path](images/h1-r2-fpv-path.svg)

## Result

- `AKK K331` covers 5645–5945 MHz, draws at most 200 mA and emits 1-Vpp/75-ohm CVBS.
- CH1/CH2/CH3 use already-reserved Hub GPIO36/37/38; no new GPIO or expander is needed.
- The 5-V reserve retains 150 mA. RF runs directly over a 50-ohm PCB trace to MMCX without U.FL.
- `TBS5G8MMCXA` is linear, 5500–6000 MHz, 2.2 dBi and 102 mm; its exact kit mark is `FPV · RX 5.8G`.

## Factory boundary

The manufacturer lists K331 in stock at $29.99; exact JLCPCB searches for `AKK K331`, `RX5808` and `RTC6715` returned zero results. It therefore remains a separate module until a private/global-sourcing response exists, not a claimed factory PCBA line item. The $6.95 antenna is a post-PCBA kit accessory and likewise not an assembly line item.

## Open gates

- obtain AKK-controlled maximum dimensions, land pattern and packaging/reflow evidence
- obtain a JLCPCB private/global-sourcing response or retain explicit post-PCBA hand installation
- prove the direct 50-ohm feed, MMCX launch, channel truth table, sensitivity, image rejection, decoder lock and video quality on assembled hardware
- qualify at least one supply-independent antenna fallback before antenna-kit freeze

> Exact current marker: **H1-R2.5**. H1 remains in progress.
