# H1-R2.10 · analog-FPV receive path

[Home](../README.md) · [Русский](h1-r2-fpv.ru.md)

The serial receiver functional candidate and exact antenna are selected; K331 physical acceptance is not claimed yet.

![Analog-FPV receive path](images/h1-r2-fpv-path.svg)

## Result

- `AKK K331` covers 5645–5945 MHz, draws at most 200 mA and emits 1-Vpp/75-ohm CVBS.
- Official AKK-hosted media confirms the [331RX application circuit](https://www.akktek.com/media/catalog/product/6/1/614ind1rmzl._sl1100_.jpg), [all 14 pin functions](https://www.akktek.com/media/catalog/product/6/1/61ruo85qnbl._sl1100_.jpg) and the [24-channel selection table](https://www.akktek.com/media/catalog/product/7/1/71tyrmpocol._sl1100_.jpg). An AKK-branded reseller image gives a 28.7 × 23.1 mm nominal board outline; collision audit uses an enlarged 30 × 24 × 4 mm reserve.
- CH1/CH2/CH3 use already-reserved Hub GPIO36/37/38; no new GPIO or expander is needed.
- The 5-V reserve retains 150 mA. RF runs directly over a 50-ohm PCB trace to MMCX without U.FL.
- `TBS5G8MMCXA` is linear, 5500–6000 MHz, 2.2 dBi and 102 mm; its exact kit mark is `FPV · RX 5.8G`. Independent linear fallback `FXP831.09.0100C` covers 4.9–6.0 GHz and retains MMCX, but is presently backorder-only with a 16-week lead time.

## Why K331 remains the leading candidate

- `AKK K331` — leading candidate: manufacturer-hosted media confirms its application circuit, complete 14-pin functions and 24-channel truth table; a separate AKK-branded reseller image gives 28.7 x 23.1 mm nominal XY, so collision work uses a conservative 30 x 24 x 4 mm reserve while controlled maximum XYZ/land/factory evidence remains open.
- `AWM682 RX` — rejected as primary: controlled body is more than twice the reserved area and its band/channel coverage is narrower.
- `AWM666V RX` — retained as the best controlled physical fallback, not the primary: its manufacturer drawing and recommended land pattern fit inside the existing 30 x 24 x 4 mm bay and its 210-mA maximum fits power, but it covers only seven 5725-5875-MHz channels versus K331's 24 channels across 5645-5945 MHz and has no public JLCPCB route.
- `TUE-RFVRX-58-D` — rejected as primary: exceeds the 350-mA reserve and the 11-mm interboard channel before tolerance.
- `RichWave RTC6715 IC` — rejected as primary: it is an unavailable bare IC, not a receiver module; the public preliminary sheet lacks the reference RF/IF application and PCB layout needed to reduce 5.8-GHz implementation risk.
- `generic RX5808` — rejected as production identity: the public card has zero stock and no manufacturer identity, controlled drawing or purchasable factory route.

## Factory boundary

The manufacturer lists K331 in stock at $29.99; JLCPCB has no exact public K331 card. Its `RichWave RTC6715` `C7464354` and generic `RX5808` `C9900139392` cards are unavailable: zero stock, MOQ 442 and Consign/Request-a-Quote only. RTC6715 is a bare QFN48 whose public 2007 preliminary sheet has no reference application or PCB layout; a custom RF/IF path would add risk without fixing supply. K331 therefore remains a separate module until a private/global-sourcing response exists, not a claimed factory PCBA line item. The $6.95 antenna is a post-PCBA kit accessory and likewise not an assembly line item. On 2026-08-27, exact mechanical, assembly and sourcing evidence requests were sent to AKK and JLCPCB; both replies are pending.

## What blocks H1 now

- obtain AKK-controlled maximum XYZ dimensions, pad pitch/land pattern and packaging/reflow evidence
- obtain a JLCPCB private/global-sourcing response or retain explicit post-PCBA hand installation

## Later verification — does not block H1

- **H3/H6/H8:** prove the direct 50-ohm feed, MMCX launch, channel truth table, sensitivity, image rejection, decoder lock and video quality before production release
- **H5/H8:** qualify FXP831.09.0100C on the assembled enclosure and secure available stock before relying on its current 16-week backorder route

> Exact current marker: **H1-R2.10**. H1 remains in progress.
