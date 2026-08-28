# H1-R2.24 · analog-FPV receive path

[Home](../README.md) · [Русский](h1-r2-fpv.ru.md)

H1 accepts a replaceable one-of-two post-PCBA analog-FPV receiver land: primary K331 or documented AWM666V fallback.

![Analog-FPV receive path](images/h1-r2-fpv-path.svg)

## Result

- `AKK K331` covers 5645–5945 MHz, draws at most 200 mA and emits 1-Vpp/75-ohm CVBS.
- Official AKK-hosted media confirms the [331RX application circuit](https://www.akktek.com/media/catalog/product/6/1/614ind1rmzl._sl1100_.jpg), [all 14 pin functions](https://www.akktek.com/media/catalog/product/6/1/61ruo85qnbl._sl1100_.jpg) and the [24-channel table](https://www.akktek.com/media/catalog/product/7/1/71tyrmpocol._sl1100_.jpg). The tolerant hand-solder axes use the official `SP331R-MANUAL-V1.0`: 28.7 × 23.1 mm, 2.54-mm pitch and 1.4-mm edge offset. It is not represented as an AKK production footprint.
- The same bay accepts exact-drawing `AWM666V RX`, 26.16 × 16.38 × 3.70 mm, on its manufacturer land. It is a seven-channel 5725–5875-MHz fallback, not a functionally equal K331 replacement.
- CH1/CH2/CH3 use rear-RP GPIO32/33/34; GPIO30/31 serve power/video lock. The official pinout marks K331 pin 6 `RSSI (NC)`, so GPIO15 remains free.
- The 5-V reserve retains 150 mA. One selected RF branch runs directly to MMCX; the alternate is isolated at the launch, leaving no U.FL, cable or live stub.
- The common reserve is enlarged to `30 × 24 × 8 mm`; after relocating C5 DBG10, minimum opposing clearance is 1.05 mm against 0.70 mm required.
- `TBS5G8MMCXA` is linear, 5500–6000 MHz, 2.2 dBi and 102 mm; its exact kit mark is `FPV · RX 5.8G`. Independent linear fallback `FXP831.09.0100C` covers 4.9–6.0 GHz and retains MMCX, but is presently backorder-only with a 16-week lead time.

## Receivers reviewed

- `AKK K331` — primary post-PCBA module: AKK-hosted media closes functional integration, while the official Sinopine SP331RX manual controls the 14 contact axes used by the tolerant hand-solder land; formal equivalence and the production package remain optional footprint-simplification evidence, while received-part and solder qualification moves to H5/H7.
- `AWM682 RX` — rejected as primary: controlled body is more than twice the reserved area and its band/channel coverage is narrower.
- `AWM666V RX` — accepted as the exact-drawing mutually exclusive post-PCBA fallback: its manufacturer body and recommended land pattern fit inside the 30 x 24 x 8 mm bay and its 210-mA maximum fits power, but it covers only seven 5725-5875-MHz channels versus K331's 24 channels across 5645-5945 MHz and has no public JLCPCB route.
- `TUE-RFVRX-58-D` — rejected as primary: exceeds the 350-mA reserve and the 11-mm interboard channel before tolerance.
- `SP166RX` — rejected as a drop-in fallback: its manufacturer drawing is 42.418 x 29.46 mm before height, so it exceeds the 30 x 24 mm bay; its RF summary contradicts its 24-channel table, no current order route is published and exact JLCPCB search returns zero results.
- `MM238R-MCU` — rejected as production fallback despite the functional and physical fit: the available sheet is reseller-hosted, the stated SFT identity does not lead to a controlled current manufacturer route, both located sellers are out of stock or discontinued and exact JLCPCB search returns zero results.
- `RichWave RTC6715 IC` — rejected as primary: it is an unavailable bare IC, not a receiver module; the public preliminary sheet lacks the reference RF/IF application and PCB layout needed to reduce 5.8-GHz implementation risk.
- `generic RX5808` — rejected as production identity: the public card has zero stock and no manufacturer identity, controlled drawing or purchasable factory route.

## Factory boundary

JLCPCB confirmed that K331 is unavailable in both Parts Library and Global Sourcing and found no direct replacement; AWM666V also has no public factory route. The normal PCBA BOM therefore omits the receiver and exactly one module is installed after reflow. Consigned Parts remains an optional later simplification. H5/H7 qualifies received body, hand soldering, Z, retention and process; an AKK/Sinopine response can replace only the tolerant land with a regular footprint without changing any interface.

## FPV blockers for H1

- None: the selected post-PCBA architecture removes the K331 production package from the H1 critical path.

## Later verification — does not block H1

- **H5/H6/H7:** qualify the received K331 on the tolerant 14-pad post-PCBA land, prove the 8-mm Z reserve and solder/process durability, then choose owner installation or an approved optional Consigned Parts route; qualify AWM666V only if the fallback is populated
- **H3/H6/H8:** prove the direct 50-ohm feed, MMCX launch, channel truth table, sensitivity, image rejection, decoder lock and video quality before production release
- **H5/H8:** qualify FXP831.09.0100C on the assembled enclosure and secure available stock before relying on its current 16-week backorder route

> Exact current marker: **H1-R2.24**. H1 remains in progress.
