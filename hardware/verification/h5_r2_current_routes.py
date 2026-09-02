#!/usr/bin/env python3
"""Publish the current R2 component/factory-route revalidation.

H5-R1 remains the historical JLCPCB BOM-tool and supplier-response evidence.
This small R2 layer joins that evidence to the authoritative native inventory,
adds every post-H5 component group, and fails closed when any current group has
no controlled route.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "hardware/ecad/generated/H2-R2-native-inventory.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
LEGACY = ROOT / "hardware/verification/generated/H5-EVR06-jlcpcb-outlier-resolution.json"
COST = ROOT / "hardware/product-design/generated/H1-R2-cost-audit.json"
OUTPUT = ROOT / "hardware/verification/generated/H5-R2-current-route-revalidation.json"
EN = ROOT / "docs/h5-r2-current-route.md"
RU = ROOT / "docs/h5-r2-current-route.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_for(device: dict) -> dict:
    return device.get("orderable_source") or device.get("source") or {}


def build() -> dict:
    inventory = load(INVENTORY)
    devices = load(DEVICES)["devices"]
    legacy = load(LEGACY)
    cost = load(COST)
    legacy_by_id = {row["device_id"]: row for row in legacy["final_routes"]}
    routes = []
    errors = []

    for group in inventory["component_groups"]:
        if group.get("bom_excluded"):
            continue
        device_id = group["device_id"]
        device = devices.get(device_id)
        if not device:
            errors.append(f"missing device record: {device_id}")
            continue
        old = legacy_by_id.get(device_id)
        source = source_for(device)
        disposition = group["ecad_disposition"]
        lifecycle = device.get("lifecycle", "")
        if group["scope"] == "regional_replaceable_cell_kit":
            route_class = "owner_supplied_not_factory"
        elif disposition != "schematic_component_group":
            route_class = "controlled_external_or_owner_assembly"
        elif "global_sourcing_required" in lifecycle:
            route_class = "jlcpcb_global_sourcing_required"
        elif "presale" in lifecycle or "preorder" in lifecycle:
            route_class = "jlcpcb_preorder"
        elif group.get("jlcpcb_part_number"):
            route_class = "jlcpcb_exact_part"
        elif old:
            route_class = f'validated_h5_r1_{old["route"]}'
        else:
            route_class = "controlled_external_source"
        evidence_url = source.get("url") or (old or {}).get("target_bom_source")
        if not evidence_url:
            errors.append(f"missing orderable evidence URL: {device_id}")
        routes.append({
            "device_id": device_id,
            "mpn": group["mpn"],
            "quantity_per_product": group["quantity_per_product"],
            "scope": group["scope"],
            "route_class": route_class,
            "jlcpcb_part_number": group.get("jlcpcb_part_number"),
            "evidence_url": evidence_url,
            "evidence_checked": source.get("checked"),
            "legacy_h5_route": (old or {}).get("route"),
            "legacy_h5_status": (old or {}).get("tool_status"),
            "order_time_recheck": True,
        })

    route_counts: dict[str, int] = {}
    for row in routes:
        route_counts[row["route_class"]] = route_counts.get(row["route_class"], 0) + 1
    sourcing_gates = [
        row for row in routes
        if row["route_class"] == "jlcpcb_global_sourcing_required"
    ]
    expected = {
        "component_groups": 249,
        "component_articles": 1216,
        "legacy_routes_reused": 209,
        "new_or_replaced_routes": 40,
        "current_global_sourcing_gates": 1,
    }
    actual = {
        "component_groups": len(routes),
        "component_articles": sum(row["quantity_per_product"] for row in routes),
        "legacy_routes_reused": sum(row["legacy_h5_route"] is not None for row in routes),
        "new_or_replaced_routes": sum(row["legacy_h5_route"] is None for row in routes),
        "current_global_sourcing_gates": len(sourcing_gates),
    }
    if actual != expected:
        errors.append(f"current route counts drifted: expected={expected}; actual={actual}")
    if {row["mpn"] for row in sourcing_gates} != {"WBC16-1TLC"}:
        errors.append("WBC16-1TLC must be the sole current global-sourcing gate")
    if cost["summary"]["bom_lines"] != 249:
        errors.append("cost report is not based on the same 249 current groups")
    if cost["summary"]["base_fitted_placements"] != 1213:
        errors.append("current base-product article quantity drifted")

    return {
        "schema_version": 1,
        "artifact": "H5-R2-current-route-revalidation",
        "marker": "H5-R2.1",
        "checked_on": "2026-09-02",
        "status": "reviewed_with_one_order_time_global_sourcing_gate" if not errors else "fail",
        "inputs": {
            str(path.relative_to(ROOT)): digest(path)
            for path in (INVENTORY, DEVICES, LEGACY, COST)
        },
        "summary": {
            **actual,
            "route_counts": route_counts,
            "unmapped_groups": len(errors),
            "known_electronics_usd": cost["summary"]["planning_base_plus_post_pcba_usd_per_device"],
            "known_external_antennas_usd": cost["summary"]["antenna_known_first_target_usd"],
            "known_combined_usd": cost["summary"]["planning_plus_known_antenna_usd_per_device"],
            "unpriced_component_groups": cost["summary"]["remaining_unpriced_base_lines"],
            "unpriced_antenna_groups": cost["summary"]["antenna_unpriced_lines"],
        },
        "routes": routes,
        "current_order_time_gate": {
            "mpn": "WBC16-1TLC",
            "jlcpcb_part": "C22402290",
            "state": "zero_live_stock_global_sourcing_required",
            "non_bom_candidate": "HenryTech H3-TC16-161T+ / LCSC C22383426",
            "candidate_state": "electrically_plausible_and_stocked_at_lcsc__exact_jlcpcb_route_pin_map_and_rf_qualification_open",
            "layout_policy": "retain the accepted WBC16-1TLC footprint until the candidate is fully qualified; do not silently substitute",
        },
        "boundary": {
            "h6_may_continue": not errors,
            "order_release_may_continue": False,
            "reason": "layout can retain the exact accepted footprint, but the single order must not be released until WBC16-1TLC has a confirmed JLCPCB sourcing/private-library route or a fully qualified replacement",
        },
        "errors": errors,
    }


def render_doc(result: dict, ru: bool) -> str:
    s = result["summary"]
    if ru:
        return f"""# Глобальный итог H5-R2 · актуальный маршрут компонентов

**H5-R2.1 проведён ревью.** Текущая R2-поверхность содержит **{s['component_groups']} закупаемых групп / {s['component_articles']} изделий**: {s['legacy_routes_reused']} маршрутов унаследованы из полного H5-R1-аудита, ещё {s['new_or_replaced_routes']} добавлены или заменены текущим H2. Непривязанных групп нет.

```mermaid
flowchart LR
  A["249 текущих групп<br/>1216 изделий"] --> B["209 повторно проверенных<br/>маршрутов H5-R1"]
  A --> C["40 новых или заменённых<br/>точных маршрутов"]
  B --> D["H6 · placement / routing"]
  C --> D
  C --> E["1 order-time gate<br/>WBC16-1TLC"]
  E -. "до заказа" .-> F["JLCPCB sourcing<br/>или квалифицированная замена"]
```

## Что изменилось

- Стоимостной отчёт и H5 теперь используют один и тот же native R2 inventory, а не исторический 210-строчный BOM.
- Исправленная известная база электроники: **${s['known_electronics_usd']:.2f}**; известные внешние антенны: **${s['known_external_antennas_usd']:.2f}**; вместе **${s['known_combined_usd']:.2f}** до платы, сборки, корпуса, доставки и ещё {s['unpriced_component_groups']} групп компонентов / {s['unpriced_antenna_groups']} групп антенн без цены.
- `WBC16-1TLC` остаётся точной схемной деталью, но склад JLCPCB сейчас нулевой. `H3-TC16-161T+` найден как массовый кандидат, однако не войдёт в BOM без проверки pin map, RF-параметров и точного factory route.

## Граница

H6 может продолжать компоновку с принятым footprint `WBC16-1TLC`. Заказ остаётся fail-closed до подтверждённого JLCPCB sourcing/private-library маршрута либо полностью квалифицированной замены. Молчаливая замена запрещена.

[Машинный результат](../hardware/verification/generated/H5-R2-current-route-revalidation.json) · [актуальный топ-20 стоимости](h1-r2-cost.ru.md)
"""
    return f"""# H5-R2 global result · current component route

**H5-R2.1 is reviewed.** The current R2 surface contains **{s['component_groups']} purchasable groups / {s['component_articles']} articles**: {s['legacy_routes_reused']} routes inherit the complete H5-R1 audit and {s['new_or_replaced_routes']} are current H2 additions or replacements. No group is unmapped.

```mermaid
flowchart LR
  A["249 current groups<br/>1216 articles"] --> B["209 revalidated<br/>H5-R1 routes"]
  A --> C["40 new or replaced<br/>exact routes"]
  B --> D["H6 · placement / routing"]
  C --> D
  C --> E["1 order-time gate<br/>WBC16-1TLC"]
  E -. "before order" .-> F["JLCPCB sourcing<br/>or qualified replacement"]
```

## What changed

- The cost report and H5 now consume the same native R2 inventory instead of the historical 210-line BOM.
- Corrected known electronics are **${s['known_electronics_usd']:.2f}**; known external antennas are **${s['known_external_antennas_usd']:.2f}**; combined they are **${s['known_combined_usd']:.2f}** before PCB, assembly, enclosure, delivery and {s['unpriced_component_groups']} unpriced component groups / {s['unpriced_antenna_groups']} unpriced antenna groups.
- `WBC16-1TLC` remains the exact schematic part but JLCPCB live stock is now zero. `H3-TC16-161T+` is a mass-market candidate, but it does not enter the BOM without pin-map, RF and exact factory-route qualification.

## Boundary

H6 may continue placement with the accepted `WBC16-1TLC` footprint. Order release remains fail-closed until a confirmed JLCPCB sourcing/private-library route or a fully qualified replacement exists. Silent substitution is forbidden.

[Machine result](../hardware/verification/generated/H5-R2-current-route-revalidation.json) · [current cost top 20](h1-r2-cost.md)
"""


def render() -> dict[Path, str]:
    result = build()
    return {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        EN: render_doc(result, False),
        RU: render_doc(result, True),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    if result["errors"]:
        for error in result["errors"]:
            print(f"ERROR: {error}")
        return 1
    artifacts = render()
    if args.write:
        for path, content in artifacts.items():
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
        return 0
    stale = [str(path.relative_to(ROOT)) for path, content in artifacts.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        print("stale H5-R2 artifacts: " + ", ".join(stale))
        return 1
    print("ok: H5-R2 current routes are complete; one order-time sourcing gate remains")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
