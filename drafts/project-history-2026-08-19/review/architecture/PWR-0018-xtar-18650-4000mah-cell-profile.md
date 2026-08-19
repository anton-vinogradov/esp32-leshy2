# PWR-0018 — exact XTAR 18650 4000mAh cell profile

- Статус: **Проведено ревью paper electrical/mechanical fit; qualification HIL open**
- Дата: 2026-08-18
- Decision: [`DEC-0079`](../decisions/DEC-0079-xtar-18650-4000mah-qualification-target.md)
- Finding: [`FND-0083`](../findings/FND-0083-generic-cell-placeholder-blocked-real-limits.md)
- Propagation review: [`REV-0005AJ`](../reviews/REV-0005AJ-exact-cell-propagation.md)

## Selection boundary

The product requires two separately replaceable protected button-top cells,
not two raw cell cores. The completed assembly must fit `Keystone 1048P`,
support the reviewed current envelope, accept the existing charge target and
have an exact identity that can be placed in regional battery kits.

The leading classes were screened as follows:

| Exact product | Useful facts | Result |
|---|---|---|
| `XTAR 18650 4000mAh` | 4.0 Ah, 10-A discharge, 2-A standard/4-A max charge, protected button top, max 18.7×69.7 mm, official-store `$14.50` | **selected first target** |
| `Fenix ARB-L18-4000` | 4.0 Ah, 7-A output, 2-A recommended/4-A max charge, 18.75×69.2 mm, about `$24.95` | electrically adequate but roughly `$10` more per cell |
| `Nitecore NL1836` | 3.6 Ah and 3-A continuous discharge | only 0.22-A paper margin over the 2.78-A transient before tolerance/aging/ripple; rejected |
| Jauch `250669` | industrial documentation, 3.35 Ah, 5-A discharge | max charge 1.005 A and max 19×70.5 mm; materially slower charge and worse fit target |
| Liion Wholesale `lgmj1pcb` | strong assembly certifications, 3.5 Ah, 10 A | exact page was out of stock; 1.675-A standard charge and max 19.0-mm diameter |

This is a target selection, not a claim that retail stock substitutes for a
production supply agreement.

## Exact manufacturer profile

The official two-page XTAR datasheet and current exact product page give:

| Property | Exact target |
|---|---:|
| manufacturer-published model | `XTAR 18650 4000mAh` protected, button top, no USB port; no separate order code is published on the exact product page |
| nominal / minimum capacity | `4000 / 3800 mAh` |
| nominal energy | `14.4 Wh` per cell; `28.8 Wh` per 2S pair |
| nominal / charge voltage | `3.6 V / 4.2±0.03 V` |
| product discharge floor | `3.0 V` per cell; manufacturer cutoff is `2.5 V` |
| maximum continuous discharge | `10 A` |
| initial resistance | `<=40 mOhm` |
| standard / maximum charge | `2 A / 4 A` |
| discharge overcurrent protection | `11…14 A` |
| nominal / maximum envelope | `18.4×69.2 / 18.7×69.7 mm` |
| weight | `<=50 g` |
| published operation / storage | `-20…60 / -20…40 °C` |

The firmware charge window remains the conservative `0…45 °C` because the
datasheet's generic operating range does not separately authorize sub-zero
charging. The three direct NTC paths enforce that boundary without trusting a
UI process.

## Product-current and energy fit

The accepted 2S load calculation is `2.22 A` continuous and `2.78 A`
transient per series cell at a 6.0-V stack and 90% conversion. The exact
10-A rating therefore provides approximately `4.5×` continuous and `3.6×`
transient paper ratios before specimen derating. Each slot fuse retains its
independent board-level role and has a `5 A` nominal rating below the cell's
published `11…14 A` electronic trip class. That comparison is not a
selectivity proof: exact fuse time-current, cell-protection trip and hot-path
coordination remain mandatory HIL gates.

At `28.8 Wh`, the pair contains 2.4 hours of ideal energy at a constant 12-W
load. That is not a runtime promise: conversion loss, RF duty, screen level,
temperature, minimum voltage, aging and reserve policy must be applied first.

The `2 A` product charge ceiling now equals the exact cell's standard charge
current. The existing 1-A reset default remains a useful conservative startup;
ordinary firmware may reach 2 A only after source, system-load, pair and all
three temperature checks pass.

## Mechanical fit and identity

The maximum cell envelope is within the class for which Keystone describes
the 1048P as intended: longer 18650 cells with built-in protection. The holder
drawing does not publish a guaranteed accepted cell-diameter/length range, so
paper class compatibility is not a received-part fit proof. Two cells from
each incoming lot must pass insertion force, full-contact compression,
retention, removal cycles, no-wrapper damage and all three sensor-contact tests
before footprint/enclosure freeze.

The device cannot authenticate an untagged two-terminal cell electrically.
Regional kits therefore carry the exact model, source, lot and packaging
authenticity record. XTAR's packaging security code can support receiving, but
it is not a runtime cryptographic cell identity. Mixed MPN, visibly damaged
wrapper, missing lot evidence or anomalous electrical results fail closed.

## Diagnostic and thermal follow-on

At the diagnostic current class `0.57…0.88 A`, the published `<=40 mOhm`
initial cell resistance alone corresponds to no more than about 35 mV of
new-cell internal droop per cell. Protection board, holder, fuse, copper and
aging add to that number. Therefore neither 40 mOhm nor 35 mV is a production
admission threshold.

The HIL matrix must measure baseline/loaded voltage, calibrated load current,
cell and path resistance, both cell NTCs, charger NTC, holder/contact
temperature and recovery time across lot, state of charge, `0…45 °C` charge,
qualified discharge temperatures, aging and contact contamination. It then
derives separate warn/reject distributions and may increase the 10-s retry
interval. Missing or inconsistent evidence remains a fail-closed result.

## Availability, paperwork and cost

The exact protected model is current on the manufacturer site and the official
store, which listed China/USA shipment variants at `$14.50` per cell. EU and
US specialist retailers also listed it. Retail availability is adequate for
prototype lots, not evidence of production allocation.

XTAR identifies the item by the manufacturer/model string `18650 4000mAh` and
does not publish a separate orderable part code on the exact product page.
Procurement identity therefore comprises manufacturer, exact product URL,
protected button-top/no-USB construction and received packaging/lot evidence;
a capacity-only marketplace title is not an equivalent MPN.

The public manufacturer material states protection, RoHS/CE and an MSDS link,
but the paper review did not obtain an exact assembly-matching UN38.3 test
summary or IEC/CB certificate. Those documents are a hard regional-kit gate.
If XTAR cannot supply them for the ordered assembly/revision, production may
not silently ship it; the exact-cell decision reopens to a documented
alternative and its charge/fit/cost consequences.

Primary sources:

- [XTAR exact protected-cell product page](https://www.xtar.cc/product/xtar-18650-4000mah-10a-battery.html)
- [XTAR exact two-page datasheet download](https://www.xtar.cc/download/18650-4000mah-data-sheet)
- [XTAR official-store exact listing](https://xtardirect.com/products/xtar-high-capacity-36v-18650-4000mah-10a-protected-lithium-ion-battery)
- [Keystone 1048P exact holder](https://www.keyelco.com/product.cfm/product_id/13959)
- [Fenix ARB-L18-4000 comparison listing](https://www.fenixlight.co.uk/product/fenix-arb-l18-4000-18650-battery-1870)
- [Jauch 250669 protected-cell datasheet](https://www.jauch.com/downloadfile/5e200d2f610958478c59ddb760bb61954/3250mah_-_li18650jl_protected.pdf)

## Review result

Exact cell identity, paper current/energy/charge fit, maximum geometry,
conservative charge-temperature boundary and supply/certification gates receive
**«Проведено ревью»**. Received-cell fit, certification documents, protection
trip, droop distributions, thermal stack and lifecycle HIL remain open. This
does not authorize KiCad.
