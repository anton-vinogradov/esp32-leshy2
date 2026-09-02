#!/usr/bin/env python3
"""Publish the global H5-R1 component and factory-route result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = {
    f"H5-EVR{index:02d}": ROOT / f"hardware/verification/generated/H5-EVR{index:02d}-{suffix}"
    for index, suffix in (
        (1, "residual-map.json"),
        (2, "source-research.json"),
        (3, "irreducible-sample-basket.json"),
        (4, "pcba-platform-baseline.json"),
        (5, "jlcpcb-bom-match.json"),
        (6, "jlcpcb-outlier-resolution.json"),
        (7, "supplier-response-gate.json"),
        (8, "fallback-factory-readiness.json"),
    )
}
ASSEMBLY = ROOT / "hardware/product-design/assembly-coordinate-model.json"
SUPPLIER = ROOT / "hardware/procurement/H5.0.3-R1-supplier-response.json"
OUTPUT = ROOT / "hardware/verification/generated/H5-R1-acceptance-package.json"
DOC_EN = ROOT / "docs/h5-r1-acceptance.md"
DOC_RU = ROOT / "docs/h5-r1-acceptance.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    ev = {key: load(path) for key, path in EVIDENCE.items()}
    assembly = load(ASSEMBLY)
    supplier = load(SUPPLIER)
    manifest = ev["H5-EVR03"]
    platform = ev["H5-EVR04"]
    resolved = ev["H5-EVR06"]
    supplier_gate = ev["H5-EVR07"]
    fallback = ev["H5-EVR08"]
    routes = resolved["summary"]["availability_routes"]
    fastener = manifest["supply_constraints"]["sandwich_fastener"]

    checks = {
        "residual_and_source_research_are_reviewed": ev["H5-EVR01"]["status"] == "reviewed_mapping_only"
        and ev["H5-EVR02"]["status"] == "reviewed_research_only",
        "sole_prototype_manifest_is_reviewed_and_fully_priced": manifest["status"]
        == "reviewed_order_manifest_owner_final_assembly_h6_and_order_gates_assigned"
        and manifest["summary"]["article_lines"] == 33
        and manifest["summary"]["measurement_contracts"] == 12
        and manifest["summary"]["unpriced_manufacturer_lines"] == 0,
        "all_current_bom_lines_have_exact_controlled_routes": platform["summary"]["target_bom_lines"] == 210
        and platform["summary"]["target_placements_parsed"] == 1050
        and resolved["summary"]["unmapped_lines"] == 0
        and resolved["summary"]["component_replacements"] == 0
        and sum(routes.values()) == 210,
        "jlcpcb_pcba_supplier_gate_passes": supplier_gate["status"]
        == "passed_pcba_supplier_gate_owner_final_assembly"
        and supplier_gate["summary"]["factory_gate_passed"]
        and supplier_gate["summary"]["blocking_decline_count"] == 0,
        "owner_final_assembly_is_explicit": supplier["owner_assembly_boundary"]["complete_factory_device_required"] is False
        and supplier["owner_assembly_boundary"]["display_and_fpc_installed_by_owner"]
        and supplier["owner_assembly_boundary"]["microcoax_jumpers_installed_by_owner"]
        and supplier["owner_assembly_boundary"]["sandwich_and_enclosure_assembled_by_owner"],
        "four_screw_stack_has_exact_eleven_mm_stop": assembly["stack"]["interboard_gap_mm"] == 11.0
        and assembly["mounting_holes"]["diameter_mm"] == 2.7
        and fastener["compression_stop_mpn"] == "Ettinger 007.02.611"
        and fastener["installed_quantity"] == 4
        and "owned_by_H6" in fastener["status"],
        "fallback_response_is_optional": fallback["status"]
        == "optional_full_device_inquiry_response_open_pcba_path_unblocked",
        "commercial_actions_remain_zero": manifest["supply_constraints"]["sourcing_requests_submitted"] == 0
        and manifest["supply_constraints"]["orders_submitted"] == 0
        and supplier_gate["summary"]["orders_authorized"] == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H5-R1 global acceptance failed: " + ", ".join(failed))

    result = {
        "schema_version": 1,
        "artifact": "H5-R1-acceptance-package",
        "marker": "H5.0.3-R1",
        "status": "reviewed",
        "source_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (*EVIDENCE.values(), ASSEMBLY, SUPPLIER)
        },
        "result": {
            "bom_lines": 210,
            "placements": 1050,
            "availability_routes": routes,
            "unmapped_lines": 0,
            "component_replacements": 0,
            "owner_assembly_article_lines": 33,
            "owner_measurement_contracts": 12,
            "known_material_budget_usd": manifest["summary"]["known_engineering_material_budget_usd"],
            "exact_interboard_stop": "Ettinger 007.02.611",
            "supplier_gate_passed": True,
            "failed_checks": 0,
        },
        "checks": checks,
        "handoff": {
            "H6": [
                "place and route the two PCBAs against all reviewed H1-H5 constraints",
                "lock enclosure wall thickness and select the exact Essentra 50M025045Pxxx nylon screw length",
                "emit Gerber/BOM/CPL and obtain the real two-PCBA MOQ price",
            ],
            "pre_order": [
                "confirm final SA818S-V pre-order charge and lead time",
                "recheck every selected exact production MPN on the live JLCPCB surface",
            ],
            "H7": [
                "dry-fit display FPC orientation, bend, slack and image/backlight/touch before PSA bonding",
                "install five microcoax jumpers vertically with the correct tool and no cable pull",
                "assemble one finished prototype from two factory-populated PCBAs",
            ],
        },
        "claims": {
            "h5_component_and_factory_route_reviewed": True,
            "h6_placement_and_routing_may_start": True,
            "pcb_layout_proven": False,
            "first_prototype_proven": False,
            "purchase_authorized": False,
            "fabrication_authorized": False,
        },
        "next": {"stage": "H6", "marker": "H6.0.1-R1", "action": "create the routed mechanical/electrical release candidate"},
    }

    en = f"""# H5-R1 global result · components and factory route

[Русский](h5-r1-acceptance.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Stage results](stage-results.md#h5)

**H5-R1 is reviewed.** Every current BOM line has one controlled production, external owner-assembly or user-supplied route. JLCPCB confirmed exact `SA818S-U/V` placement at separate designators and no silent substitution. The owner accepted deterministic post-PCBA installation of the display, five microcoax jumpers, knob and enclosure, so full-device box build is no longer a release gate.

```mermaid
flowchart LR
  A["210 BOM lines<br/>1050 placements"] --> B["210 controlled routes<br/>0 unmapped · 0 substitutions"]
  B --> C["JLCPCB PCBA<br/>supplier gate passed"]
  C --> D["H6<br/>placement · routing · enclosure"]
  D --> E["one exact quote<br/>then F-PO and H7"]
```

## Result at a glance

| Reviewed evidence | Result |
|---|---:|
| BOM lines / fitted placements | 210 / 1,050 |
| Routes `J0 / J2 / J3 / J4-F / J4-P / J5-U` | {routes['J0']} / {routes['J2']} / {routes['J3']} / {routes['J4-F']} / {routes['J4-P']} / {routes['J5-U']} |
| Unmapped lines / substitutions | 0 / 0 |
| Integrated owner-kit article lines | 33 |
| H7/H8 measurement contracts | 12 |
| Known conservative material budget | ${manifest['summary']['known_engineering_material_budget_usd']} |
| Supplier-gate blockers | 0 |

The four-board-corner stack keeps the Div-like **four long plastic screw** concept. Four exact unthreaded polyamide `Ettinger 007.02.611` sleeves set the 11.00-mm board gap; enclosure capture lips and anti-shear datums carry side load. The exact screw family is qualified, while H6 selects its length after both enclosure walls are dimensioned.

## What remains, with exact owners

- **H6:** placement/routing, routed electrical/RF/mechanical re-analysis, enclosure wall thickness, exact nylon screw length, Gerber/BOM/CPL and the resulting two-PCBA MOQ quote.
- **Immediately before the one order:** final `SA818S-V` pre-order charge/lead and a live stock/price recheck of every selected production MPN.
- **H7 owner assembly:** display/FPC dry fit and powered image/backlight/touch check before irreversible PSA bonding, careful five-jumper microcoax installation, knob and enclosure closure.

None of these is an unresolved H5 identity or factory-route problem. PCBWay's pending reply remains an optional cost/convenience comparison. No purchase, reservation, sourcing request or fabrication was authorized.

[Machine acceptance package](../hardware/verification/generated/H5-R1-acceptance-package.json) · [article manifest](component-sample-basket.md) · [factory map](manufacturing-platform.md).
"""

    ru = f"""# Глобальный итог H5-R1 · компоненты и фабричный маршрут

[English](h5-r1-acceptance.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Результаты этапов](stage-results.ru.md#h5)

**H5-R1 проведён ревью.** У каждой текущей BOM-строки есть один контролируемый production-, внешний owner-assembly- или user-supplied-маршрут. JLCPCB подтвердил установку exact `SA818S-U/V` на отдельных designator и запрет молчаливой замены. Владелец принял детерминированную post-PCBA установку дисплея, пяти microcoax, ручки и корпуса, поэтому полный box build больше не является release gate.

```mermaid
flowchart LR
  A["210 BOM-строк<br/>1050 установок"] --> B["210 контролируемых маршрутов<br/>0 unmapped · 0 замен"]
  B --> C["JLCPCB PCBA<br/>supplier gate пройден"]
  C --> D["H6<br/>placement · routing · корпус"]
  D --> E["одна точная цена<br/>затем F-PO и H7"]
```

## Результат кратко

| Проверенное evidence | Результат |
|---|---:|
| BOM-строк / устанавливаемых позиций | 210 / 1 050 |
| Маршруты `J0 / J2 / J3 / J4-F / J4-P / J5-U` | {routes['J0']} / {routes['J2']} / {routes['J3']} / {routes['J4-F']} / {routes['J4-P']} / {routes['J5-U']} |
| Неназначенных строк / замен | 0 / 0 |
| Строк единого owner-комплекта | 33 |
| Контрактов измерений H7/H8 | 12 |
| Известный консервативный material budget | ${manifest['summary']['known_engineering_material_budget_usd']} |
| Блокеров supplier gate | 0 |

Четыре угла sandwich сохраняют Div-подобную идею **четырёх длинных пластиковых винтов**. Четыре точные проходные полиамидные втулки `Ettinger 007.02.611` задают межплатные 11,00 мм; боковую нагрузку несут capture lips и anti-shear datums корпуса. Семейство винтов квалифицировано, а точную длину H6 выбирает после размеров обеих стенок корпуса.

## Что осталось и кому назначено

- **H6:** placement/routing, повторный routed-анализ электричества/RF/механики, толщина стенок корпуса, точная длина nylon-винтов, Gerber/BOM/CPL и получаемая по ним цена двух PCBA при MOQ.
- **Непосредственно перед единственным заказом:** финальные charge/lead pre-order `SA818S-V` и live-перепроверка stock/price каждого выбранного production MPN.
- **Owner assembly в H7:** сухая примерка дисплея/FPC и проверка изображения/подсветки/touch до необратимой наклейки PSA, аккуратная установка пяти microcoax, ручки и корпуса.

Ни один из этих пунктов не является нерешённой проблемой identity или фабричного маршрута H5. Ожидаемый ответ PCBWay остаётся optional-сравнением цены/удобства. Закупка, reservation, sourcing request и fabrication не разрешались.

[Машинный пакет приёмки](../hardware/verification/generated/H5-R1-acceptance-package.json) · [article manifest](component-sample-basket.ru.md) · [фабричная карта](manufacturing-platform.ru.md).
"""

    return {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: en,
        DOC_RU: ru,
    }, result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, result = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit("stale H5-R1 acceptance artifacts: " + ", ".join(stale))
    print(
        "ok: H5-R1 reviewed; 210/210 routes, 0 substitutions, "
        f"${result['result']['known_material_budget_usd']} known material, H6 next"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
