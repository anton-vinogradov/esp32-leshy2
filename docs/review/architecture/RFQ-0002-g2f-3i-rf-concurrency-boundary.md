# RFQ-0002 — G2F-3I RF concurrency boundary

- Статус: **Проведено ревью фактов; nRF full-mix acceptance открыт**
- Дата: 2026-08-17
- Digital prerequisite: [`NIF-0001`](NIF-0001-digital-noninterference-layout.md)
- Prior neutral model: [`RFQ-0001`](RFQ-0001-zero-based-rf-zoning-coexistence.md)
- Finding: [`FND-0053`](../findings/FND-0053-arbitrary-colocated-rf-concurrency-is-impossible.md)
- Proposal: [`IMP-0038`](../improvements/IMP-0038-visible-qualified-rf-arbiter.md)
- Decision: [`DEC-0045`](../decisions/DEC-0045-one-active-signal-group.md)
- Quiet-state decision: [`DEC-0046`](../decisions/DEC-0046-unused-interface-quiet-by-default.md)
- Open nRF choice: [`IMP-0039`](../improvements/IMP-0039-three-nrf-full-mix-acceptance.md)

## Scope

Этот документ накладывает reviewed RF-факты на ведущую бумажную карту
`G2F-3I`. Он не выбирает antenna MPN, matching/filter values, shield can,
coax/connector или координаты PCB. Его задача — отделить достижимую
параллельность от физически ложного обещания до conceptual placement.

## G2F-3I path inventory

| Path | Owner / exact current boundary | Native physical limit |
|---|---|---|
| `S3-24` | ESP32-S3-WROOM-1U | одна 2.4 GHz Wi-Fi/BLE chain; native TDM coexistence |
| `C5-DUAL` | ESP32-C5-WROOM-1U-N8R8 | одна 1T1R 2.4/5 GHz chain shared with 2.4 GHz 802.15.4 |
| `N24-0..2` | three nRF24L01+ paths; E01-ML01S remains geometry/reference candidate | three independent transceivers; every simultaneous PTX/PRX mix mandatory, exact mixed-RF sensitivity not yet qualified |
| `CC` | CC1101 bare-IC boundary | one qualified 300/400/800–900 MHz matching/filter/antenna profile at a time |
| `VOICE` | conditional SA518 preferred | half-duplex 136–174/400–470 MHz, up to 1 W |
| `RX` | exact Si473x variant still open | receive-only AM/FM/SW/LW frontend |
| `U214` | removable Cap LoRa-1262 | 868–923 MHz LoRa up to +22 dBm plus GNSS, own accessory geometry |
| `M5` | qualified Unit/Cap profile | each added RF accessory reopens the affected pair matrix |

IR remains digitally independent on C5, but its pulsed current and optical
driver noise belong to power/EMI HIL, not this far-field radio matrix.

## Pair classes после `DEC-0045`

`P` = required parallel, `T` = visible time-sharing, `Q` = parallel only after
exact HIL, `X` = prohibited simultaneous state, `A` = accessory-conditional.

| Session/pair | Class before exact HIL | Acceptance/fallback |
|---|---|---|
| nRF0/nRF1/nRF2 any `PRX`/`PTX` mix | `P` digitally, RF acceptance open | all roles run concurrently without hidden standby/gaps; `IMP-0039` selects the channel/power/sensitivity envelope |
| nRF control/FIFO service ↔ any other digital interface | `P` | already independent in `NIF-0001`; timing HIL remains |
| S3 Wi-Fi ↔ S3 BLE | `T` | Espressif native coexistence; dwell/preemption/gaps/loss visible |
| C5 2.4 Wi-Fi ↔ C5 5 GHz ↔ C5 802.15.4 | `T` | one 1T1R RF domain; active owner/channel and gaps visible |
| S3/C5 2.4 TX ↔ any nRF RX | `X` cross-group | group switch stops the native RF stack or nRF group before activation |
| one or two nRF TX ↔ peer nRF RX | required, not yet physically qualified | no automatic standby/time-slicing; same/near-channel weak-signal isolated sensitivity is not claimed before exact OTA/conducted HIL |
| CC ↔ U214 in 868/915 overlap | `X+A` cross-group | `SG-CC` and `SG-U214` are mutually exclusive |
| CC RX ↔ voice TX in 400–464 overlap | `X` | RX is paused and marked stale/lost before PTT; no same-channel internal exception |
| Si473x/GNSS RX ↔ any TX | `Q` | band filtering, harmonics, common-rail and enclosure desense test; fallback visible stale/unknown |
| C5 5 GHz ↔ non-C5 receive paths | `Q` | different band is useful but not proof against harmonics, clocks or common-rail coupling |
| any two independent signal groups | `X` | one-active-group invariant; system planes continue without RF permission |

## Physical invariants for the next placement artifact

1. S3 and C5 `-1U` antenna connectors exit to different enclosure sectors;
   pigtails never cross packet-radio antenna keep-outs.
2. Three nRF radiators retain independent, indexed geometry and maximum
   practical separation; no RF switch replaces a transceiver.
3. Voice PA/filter/feed is placed farthest from CC, Si473x, GNSS, codec input
   and their rails; PTT cannot assert before RF arbiter grant.
4. CC receives its own band-specific matching/filter/measurement point; a
   universal 300–928 MHz antenna claim is forbidden without exact multi-profile
   proof.
5. U214 remains at the edge/outside the base PCB, with known antenna/cable
   pose; unsupported folding over a native radiator blocks TX.
6. Shield boundaries, via fences, filters, antenna keep-outs and conducted test
   points are functional BOM, not optional post-layout fixes.
7. Actual-TX evidence drives the coexistence state machine; commanded state
   alone cannot certify that a neighbour is safe to receive.

## Принятая runtime boundary

[`DEC-0045`](../decisions/DEC-0045-one-active-signal-group.md) принимает один
active signal-group manifest. Cross-group RF pairs не требуют дорогой попытки
universal isolation и не повышаются в base product. Qualification теперь
состоит из isolated-path HIL, обязательной внутригрупповой concurrency
(`SG-N24` full digital mix, native vendor TDM, declared U214 support members),
safe atomic group switching, inactive-interface quiet states и
digital-aggression EMI tests. `IMP-0039` still decides whether base acceptance
uses a qualified channel/power envelope or attempts a materially different
remote/self-cancellation architecture.
