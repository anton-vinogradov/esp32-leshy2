# G2F-3I — generated target BOM coverage review

- Статус: **I8 inventory complete; sourcing/cost/alternate review active**
- Source of truth: `hardware/architecture/devices.json` and `hardware/architecture/candidates/G2F-3I.json`
- Regenerate: `python3 hardware/architecture/generate.py --write`

> Файл сгенерирован. Он показывает полноту входа в I8, а не выдаёт незакрытые строки за factory quote.

## Что уже посчитано

- **858** machine-instantiated physical placements collapse to **188** used exact-device/MPN lines.
- Current orderability evidence exists for **187/188** used lines; **1** need a current source check.
- Machine-readable quantity-100 cost evidence exists for **0/188** lines.
- Machine-readable alternate/no-substitution evidence exists for **1/188** lines.
- Cost basis: USD quantity 100 component material only; PCB, assembly, test, enclosure, tax, freight, yield and tooling stay separate until factory RFQ.

Scopes: `base_product` — 855 placements; `optional_external_accessory` — 1 placements; `regional_replaceable_cell_kit` — 2 placements.

The complete per-line manifest is the adjacent `G2F-3I-target-bom.csv`; unused comparison-device definitions are deliberately excluded.

## Physical items not yet instantiated

### `external_sma_bodies` — 9 item(s)

- Scope: `base_product`.
- Role: two RP-SMA and seven standard-SMA external RF connector bodies.
- Blocking evidence: exact attachment style and MPN depend on the physical connector plane; polarity and radio ownership are already fixed.

### `rf_cable_assemblies` — 5 item(s)

- Scope: `base_product`.
- Role: two native-radio double-ended microcoax jumpers and three nRF module-to-coupler pigtails.
- Blocking evidence: exact mating family, length and strain relief require received-module microscopy and internal placement.

### `m5_connector_bodies` — 2 item(s)

- Scope: `base_product`.
- Role: rear Cap-Bus receptacle and native HY2.0-4P Unit receptacle.
- Blocking evidence: manufacturer order codes are not published; received U214/cable mate and retention coupon are required.

### `external_antenna_kit` — 12 item(s)

- Scope: `costed_product_variant`.
- Role: two native, three nRF, three CC, two voice and two receiver antennas/pods.
- Blocking evidence: one first target exists for most profiles, but second-source, AM/LW pod and package-variant disposition remain open.

## Used lines without current orderability evidence

This is deliberately rendered as vertical cards so the document remains usable on a narrow screen.

<details><summary><code>HMX035CTFT-001 (QDtech schematic assembly marking)</code> — qty 1</summary>

- Device id: `qdtech_hmx035ctft_001`
- Scope: `base_product`
- Lifecycle claim awaiting I8 recheck: `assembly_marking_and_contacts_disclosed_in_official_reference_schematic; standalone_orderability_drawing_and_lifecycle_unverified`
- Qualification: `verified_candidate`
- Placements: `display`

</details>

## Non-MPN physical features

- ground and via fields.
- no-connects and fixed copper straps.
- protected test pads.
- reserved DNP footprints.

These need exact library/geometry and manufacturing rules, but must not be padded into component cost as fictitious purchased parts.

## I8 exit

every installed or supplied physical item has a scope, exact first target or explicit measured/received-item gate, current lifecycle/orderability evidence, cost snapshot and no-silent-substitution policy.

Until those conditions pass, the BOM has **not** received «Проведено ревью», no total COGS is claimed and KiCad remains unauthorized.
