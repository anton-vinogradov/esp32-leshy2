# REV-0005AL — internal-rail containment propagation review

- Статус: **Проведено ревью**
- Дата: 2026-08-18
- Decision: [`DEC-0081`](../decisions/DEC-0081-independent-internal-rail-containment.md)
- Analysis: [`PWR-0020`](../architecture/PWR-0020-independent-post-buck-containment.md)
- Finding: [`FND-0085`](../findings/FND-0085-uncontained-internal-buck-high-side-short.md)

## Reviewed propagation

| Surface | Result |
|---|---|
| AON | `TPS25961DRVR` and exact ILIM/OVLO/bypass parts split raw converter output from `AON_SAFE_3V3` |
| supervisor/POR | SENSE, PG pull-up and POR pull-up now depend on protected AON; a tripped eFuse disables main without firmware |
| main | exact `TPS25974LRPWR`, ILM/dVdt/ITIMER/OVLO/PGTH/output parts split `MAIN_RAW_3V3` from `3V3_MAIN` |
| voice | a second physically separate TPS25974 and exact settings split `VVOICE_RAW_4V` from the module/audio rail |
| evidence | main/voice runtime truth uses protected eFuse PG; raw buck PG is fixture-only |
| machine source | every active device, passive, contact and route is instantiated; generated pin ledger/diagram are current |
| target site | EN/RU vertical diagrams show each physical part in its own exact-MPN/role box without review chronology |
| firmware contract | protected PG only, latch-fault lease revocation and no software bypass/reset are required |
| cost/resources | approximately USD 2.4/board at 100-piece component class; no GPIO, bus or product-mode change |

## Remaining gates

Prototype HIL must measure loaded startup, load steps, short/overvoltage trip
energy, fault latch/recovery, hot loss and battery/USB handover. The paper
topology, calculations, single-fault direction and all propagated artifacts
receive **«Проведено ревью»**; measured electrical closure does not. KiCad
remains blocked by the wider internal-design sequence.

