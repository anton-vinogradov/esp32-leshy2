# H1-R2.19 · analog-FPV receive path

[Home](../README.md) · [Русский](h1-r2-fpv.ru.md)

The serial receiver functional candidate and exact antenna are selected; K331 physical acceptance is not claimed yet.

![Analog-FPV receive path](images/h1-r2-fpv-path.svg)

## Result

- `AKK K331` covers 5645–5945 MHz, draws at most 200 mA and emits 1-Vpp/75-ohm CVBS.
- Official AKK-hosted media confirms the [331RX application circuit](https://www.akktek.com/media/catalog/product/6/1/614ind1rmzl._sl1100_.jpg), [all 14 pin functions](https://www.akktek.com/media/catalog/product/6/1/61ruo85qnbl._sl1100_.jpg) and the [24-channel selection table](https://www.akktek.com/media/catalog/product/7/1/71tyrmpocol._sl1100_.jpg). The official Sinopine `SP331R-MANUAL-V1.0` controls 28.7 × 23.1 mm nominal XY, 2.54-mm contact pitch and 1.4-mm edge offset for the matching SP331RX family. Formal equivalence to the supplied AKK K331 is not claimed; collision audit retains the enlarged 30 × 24 × 4 mm reserve.
- CH1/CH2/CH3 use rear-RP GPIO32/33/34; GPIO30/31 serve power/video lock. The official pinout marks K331 pin 6 `RSSI (NC)`, so GPIO15 remains free.
- The 5-V reserve retains 150 mA. RF runs directly over a 50-ohm PCB trace to MMCX without U.FL.
- `TBS5G8MMCXA` is linear, 5500–6000 MHz, 2.2 dBi and 102 mm; its exact kit mark is `FPV · RX 5.8G`. Independent linear fallback `FXP831.09.0100C` covers 4.9–6.0 GHz and retains MMCX, but is presently backorder-only with a 16-week lead time.

## Why K331 remains the leading candidate

- `AKK K331` — leading candidate: AKK-hosted media closes functional integration, while the official Sinopine SP331RX manual confirms 28.7 x 23.1 mm nominal XY, 2.54-mm contact pitch and 1.4-mm edge offset for the matching 331RX family; formal K331 equivalence, maximum Z/tolerances, recommended land/paste and assembly evidence remain open.
- `AWM682 RX` — rejected as primary: controlled body is more than twice the reserved area and its band/channel coverage is narrower.
- `AWM666V RX` — retained as the best controlled physical fallback, not the primary: its manufacturer drawing and recommended land pattern fit inside the existing 30 x 24 x 4 mm bay and its 210-mA maximum fits power, but it covers only seven 5725-5875-MHz channels versus K331's 24 channels across 5645-5945 MHz and has no public JLCPCB route.
- `TUE-RFVRX-58-D` — rejected as primary: exceeds the 350-mA reserve and the 11-mm interboard channel before tolerance.
- `SP166RX` — rejected as a drop-in fallback: its manufacturer drawing is 42.418 x 29.46 mm before height, so it exceeds the 30 x 24 mm bay; its RF summary contradicts its 24-channel table, no current order route is published and exact JLCPCB search returns zero results.
- `MM238R-MCU` — rejected as production fallback despite the functional and physical fit: the available sheet is reseller-hosted, the stated SFT identity does not lead to a controlled current manufacturer route, both located sellers are out of stock or discontinued and exact JLCPCB search returns zero results.
- `RichWave RTC6715 IC` — rejected as primary: it is an unavailable bare IC, not a receiver module; the public preliminary sheet lacks the reference RF/IF application and PCB layout needed to reduce 5.8-GHz implementation risk.
- `generic RX5808` — rejected as production identity: the public card has zero stock and no manufacturer identity, controlled drawing or purchasable factory route.

## Factory boundary

The manufacturer lists K331 in stock at $29.99. JLCPCB confirmed that it is unavailable in both Parts Library and Global Sourcing, found no direct replacement and accepts genuine AKK modules through a Consigned Parts application before shipment. Its `RichWave RTC6715` `C7464354` and generic `RX5808` `C9900139392` cards remain unavailable: zero stock, MOQ 442 and no purchasable module route. Exact `SP166RX` and `MM238R-MCU` searches return zero results; the former does not fit the present bay, while the latter has no controlled current production identity and was found only out of stock or discontinued. RTC6715 is a bare QFN48 whose public 2007 preliminary sheet has no reference application or PCB layout; a custom RF/IF path would add risk without fixing supply. Genuine AKK supply plus JLCPCB Consigned Parts is therefore the selected conditional factory route. The $6.95 antenna remains a post-PCBA kit accessory. The open H1 package is now narrower: either an AKK-native production package or formal K331-to-SP331RX equivalence is required, together with maximum Z/tolerances, recommended land/paste and packaging/soldering/reflow. Final Gerber/BOM/CPL DFM and optional 5-V/channel-select/CVBS function-test review follow in H5/H6/H7.

## What blocks H1 now

- close one controlled K331 production identity: either AKK supplies its own package or AKK/Sinopine formally confirms K331-to-SP331RX equivalence; in either case obtain maximum Z/tolerances, recommended land/paste geometry and packaging/soldering/reflow evidence for the fixed body and Consigned Parts application

## Later verification — does not block H1

- **H5/H6/H7:** submit the genuine AKK K331 Consigned Parts application, pass final Gerber/BOM/CPL DFM and obtain feasibility plus quotation for the 5-V/channel-select/CVBS function test
- **H3/H6/H8:** prove the direct 50-ohm feed, MMCX launch, channel truth table, sensitivity, image rejection, decoder lock and video quality before production release
- **H5/H8:** qualify FXP831.09.0100C on the assembled enclosure and secure available stock before relying on its current 16-week backorder route

> Exact current marker: **H1-R2.19**. H1 remains in progress.
