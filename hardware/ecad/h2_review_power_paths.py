#!/usr/bin/env python3
"""Independently review H2.5.1 power paths in the exported KiCad netlist.

The child-sheet generators and the architecture model are not accepted as
evidence by themselves here.  This review exports each complete hierarchy
through KiCad, rejects ambiguous references, and compares the RF power nets
that KiCad actually sees with a frozen, human-reviewed set of path members.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
GENERATED = ECAD / "generated"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
LEDGER_PATH = GENERATED / "H2-instance-ledger.json"
OUTPUT_MANIFEST = GENERATED / "H2-REV51-power-paths.json"
OUTPUT_DOC_EN = REPO / "docs/power-architecture.md"
OUTPUT_DOC_RU = REPO / "docs/power-architecture.ru.md"

PROJECTS = {
    "LESHY2-UI": ECAD / "kicad/LESHY2-UI/LESHY2-UI.kicad_sch",
    "LESHY2-RF": ECAD / "kicad/LESHY2-RF/LESHY2-RF.kicad_sch",
    "LESHY2-LORA-CAP-01": ECAD / "kicad/LESHY2-LORA-CAP-01/LESHY2-LORA-CAP-01.kicad_sch",
}
EXPECTED_COMPONENT_COUNTS = {
    "LESHY2-UI": 387,
    "LESHY2-RF": 678,
    "LESHY2-LORA-CAP-01": 27,
}

# These additions are intentional physical aliases that are not separately
# enumerated by the architecture fixed-route endpoint list: test pads,
# interboard boundaries, local sense/bypass pins and one local rail alias.
EXPECTED_ROUTE_ADDITIONS = {
    "PD_NEGOTIATED_VBUS": {
        "charger_vbus_cap0", "charger_vbus_cap1", "charger_vbus_hf_cap",
    },
    "AON_RAW_3V3": {"aon_buck"},
    "AON_SAFE_3V3": {"pd_vin_cap", "m1_rf_receptacle", "TP_AON_SAFE_3V3"},
    "3V3_MAIN": {"m1_rf_receptacle", "TP_3V3_MAIN"},
}

REVIEWED_NETS = (
    "USB_C_VBUS_RAW",
    "PD_NEGOTIATED_VBUS",
    "PACK_SLOT0_POSITIVE_RAW",
    "PACK_SLOT1_POSITIVE_RAW",
    "PACK_2S_MIDPOINT",
    "BATTERY_STACK_POSITIVE",
    "PROTECTED_PACK_POSITIVE",
    "NVDC_SYS",
    "AON_RAW_3V3",
    "AON_SAFE_3V3",
    "MAIN_RAW_3V3",
    "3V3_MAIN",
    "VVOICE_RAW_4V",
    "VVOICE_4V",
    "5V_EXT_PREPROTECT",
    "5V_U214_PROTECTED",
    "5V_UNIT_PROTECTED",
)

CRITICAL_COMPONENTS = (
    "product_usb_connector", "product_usb_protector", "pd_controller", "nvdc_charger",
    "pack_holder", "pack_fuse0", "pack_fuse1", "pack_gauge", "pack_admission",
    "pack_power_fet", "pack_shunt", "aon_buck", "aon_efuse", "main_buck",
    "main_efuse", "voice_buck", "voice_efuse", "ext_buck", "ext_efuse", "unit_efuse",
)

CONTRACT_EXPECTATIONS = {
    "product_port": "one exact S3 USB-C receptacle carries four-line-protected native S3 USB2 data and sink-only power; C5/RP service VBUS cannot power or backfeed the board",
    "battery_topology": "two individually replaceable qualified 18650 cells in a supervised 2S arrangement; both cells required for battery operation; working boundary 6.0V to 8.4V",
    "sink_pdos": ["5V fallback at advertised Type-C current (<=3A)", "9V@3A", "15V@2A"],
    "maximum_input_power_w": 30,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def instance_reference_maps() -> tuple[dict[str, dict[str, str]], dict[str, dict]]:
    by_project: dict[str, dict[str, str]] = defaultdict(dict)
    details: dict[str, dict] = {}
    for path in sorted(GENERATED.glob("H2-*.json")):
        if path == OUTPUT_MANIFEST:
            continue
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        project = manifest.get("project")
        for row in manifest.get("instances", []):
            reference = row.get("reference")
            instance = row.get("instance")
            if not project or not reference or not instance:
                continue
            previous = by_project[project].setdefault(reference, instance)
            if previous != instance:
                raise ValueError(
                    f"{project} reference {reference} maps to both {previous} and {instance}"
                )
            details[instance] = row
    return by_project, details


def export_project(project: str, schematic: Path, destination: Path) -> tuple[dict[str, set[str]], dict]:
    kicad_cli = shutil.which("kicad-cli")
    if not kicad_cli:
        mac = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        if mac.is_file():
            kicad_cli = str(mac)
    if not kicad_cli:
        raise FileNotFoundError("kicad-cli is required for H2.5.1 netlist review")
    result = subprocess.run(
        [kicad_cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(destination), str(schematic)],
        cwd=REPO, text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"KiCad netlist export failed for {project}:\n{result.stdout}{result.stderr}")
    if "not annotated" in (result.stdout + result.stderr).lower():
        raise ValueError(f"KiCad reports ambiguous/unannotated references in {project}")

    tree = ET.parse(destination)
    components = [node.get("ref", "") for node in tree.findall(".//components/comp")]
    duplicates = sorted(ref for ref, count in Counter(components).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate references in {project}: {duplicates}")
    if len(components) != EXPECTED_COMPONENT_COUNTS[project]:
        raise ValueError(
            f"{project} component count drifted: {len(components)} != {EXPECTED_COMPONENT_COUNTS[project]}"
        )

    nets: dict[str, set[str]] = defaultdict(set)
    for net in tree.findall(".//nets/net"):
        name = (net.get("name") or "").split("/")[-1]
        nets[name].update(node.get("ref", "") for node in net.findall("node"))
    return nets, {
        "component_count": len(components),
        "unique_reference_count": len(set(components)),
        "duplicate_references": duplicates,
        "net_count": len(tree.findall(".//nets/net")),
        "annotation_warnings": 0,
    }


def expected_rf_members(candidate: dict, ledger: dict) -> dict[str, set[str]]:
    rf_instances = {
        row["instance"] for row in ledger["rows"] if row["project"] == "LESHY2-RF"
    }
    expected = {net: set() for net in REVIEWED_NETS}
    for route in candidate["fixed_routes"]:
        net = route["net"]
        if net not in expected:
            continue
        for endpoint in (route["from"], route["to"]):
            instance = endpoint.split(".", 1)[0]
            if instance in rf_instances:
                expected[net].add(instance)
    for net, additions in EXPECTED_ROUTE_ADDITIONS.items():
        expected[net].update(additions)
    return expected


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    power = candidate["power_contract"]
    for key, expected in CONTRACT_EXPECTATIONS.items():
        if power[key] != expected:
            raise ValueError(f"power contract {key} drifted: {power[key]!r}")

    reference_maps, details = instance_reference_maps()
    export_stats = {}
    exported_nets = {}
    with tempfile.TemporaryDirectory(prefix="leshy2-h251-") as temp_dir:
        for project, schematic in PROJECTS.items():
            nets, stats = export_project(project, schematic, Path(temp_dir) / f"{project}.xml")
            exported_nets[project] = nets
            export_stats[project] = stats

    rf_ref_to_instance = reference_maps["LESHY2-RF"]
    expected = expected_rf_members(candidate, ledger)
    reviewed = []
    for net in REVIEWED_NETS:
        actual_refs = exported_nets["LESHY2-RF"].get(net, set())
        unknown_refs = sorted(actual_refs - rf_ref_to_instance.keys())
        if unknown_refs:
            raise ValueError(f"{net} contains unmapped RF references: {unknown_refs}")
        actual_instances = {rf_ref_to_instance[ref] for ref in actual_refs}
        if actual_instances != expected[net]:
            raise ValueError(
                f"{net} membership drifted; missing={sorted(expected[net] - actual_instances)}, "
                f"extra={sorted(actual_instances - expected[net])}"
            )
        reviewed.append({
            "net": net,
            "status": "reviewed",
            "component_count": len(actual_instances),
            "instances": sorted(actual_instances),
        })

    critical_parts = []
    for instance in CRITICAL_COMPONENTS:
        row = details.get(instance)
        if not row:
            raise ValueError(f"critical power component lacks generated instance evidence: {instance}")
        if not row.get("mpn") or not row.get("footprint"):
            raise ValueError(f"critical power component lacks exact MPN/footprint: {instance}")
        critical_parts.append({
            "instance": instance,
            "reference": row["reference"],
            "mpn": row["mpn"],
            "footprint": row["footprint"],
        })

    manifest = {
        "schema_version": 1,
        "stage": "H2.5.1",
        "status": "reviewed_power_sources_admission_charge_and_rails",
        "method": "fresh KiCad XML netlist export of every complete hierarchy plus exact RF power-net membership comparison",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, LEDGER_PATH, *PROJECTS.values())
        },
        "hierarchy_exports": export_stats,
        "corrected_findings": [{
            "id": "H2.5.1-F01",
            "severity": "fabrication_blocking",
            "finding": "child sheets reused local R1/C1/U1-style references, making whole-project flat netlists ambiguous",
            "correction": "deterministic sheet-scoped reference blocks now produce globally unique references in all three projects",
            "evidence": "all complete KiCad exports have zero duplicate references and zero annotation warnings",
        }],
        "reviewed_nets": reviewed,
        "critical_components": critical_parts,
        "power_contract": {
            "input": "one sink-only S3 USB-C port; 5 V fallback, 9 V/3 A and 15 V/2 A; 30 W maximum",
            "battery": "two individually removable protected 18650 cells in supervised 2S; 6.0–8.4 V",
            "charge_path": "USB_C_VBUS_RAW -> TPS25751D PPHV -> BQ25798 -> NVDC_SYS / protected 2S pack",
            "pack_path": "two fused cell slots -> MAX17320 + MSPM0 admission -> back-to-back FET -> PROTECTED_PACK_POSITIVE",
            "rails": [
                "NVDC_SYS -> TPS629203 -> TPS25961 -> AON_SAFE_3V3",
                "NVDC_SYS -> TPS564252 -> TPS25974 -> 3V3_MAIN",
                "NVDC_SYS -> TPS564252 -> TPS25974 -> VVOICE_4V",
                "NVDC_SYS -> TPS564252 -> two independent TPS259470 branches -> protected U214 and M5 Unit 5 V",
            ],
        },
        "review_boundary": {
            "complete": [
                "all three complete hierarchies export without duplicate or unannotated references",
                "the USB sink, negotiated input, charger, 2S pack and every raw/protected rail are traced in the actual RF netlist",
                "every critical active/protection component has an exact MPN and footprint",
            ],
            "deferred": [
                "component-value tolerance, startup/handover and transient simulation in H3",
                "placement, copper current density, thermal spreading and routing in H6",
                "received-cell/holder continuity and physical power HIL in H5/H7/H8",
            ],
        },
    }
    outputs = {
        OUTPUT_MANIFEST: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        OUTPUT_DOC_EN: render_doc(manifest, russian=False),
        OUTPUT_DOC_RU: render_doc(manifest, russian=True),
    }
    return outputs, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    parts = {row["instance"]: row for row in manifest["critical_components"]}
    if russian:
        title = "# Питание Leshy2"
        intro = (
            "[English](power-architecture.md) · [На главную](../README.ru.md) · "
            "[Принципиальные схемы](schematics.ru.md)\n\n"
            "Это итоговая архитектура питания готового устройства. Она проверяется по "
            "полной netlist, которую экспортирует сам KiCad."
        )
        source = "## Источники"
        source_text = (
            "- Единственный внешний источник — основной USB-C S3: только sink, до 30 Вт "
            "(5 В fallback, 9 В × 3 А или 15 В × 2 А). Сервисные USB C5 и RP2354B "
            "питание устройства не принимают.\n"
            "- Автономный источник — два съёмных защищённых 18650, последовательно, "
            "рабочий диапазон 6,0–8,4 В. Для работы от аккумуляторов нужны оба элемента."
        )
        charge = "## Вход, заряд и аккумуляторы"
        rails = "## Формируемые шины"
        rail_headers = "| Выход | Тракт | Назначение |\n|---|---|---|"
        rail_rows = [
            "| `AON_SAFE_3V3` | `NVDC_SYS` → TPS629203 → TPS25961 | Всегда включённая safety-логика |",
            "| `3V3_MAIN` | `NVDC_SYS` → TPS564252 → TPS25974 | Процессоры, UI и обычная логика |",
            "| `VVOICE_4V` | `NVDC_SYS` → TPS564252 → TPS25974 | Только голосовой RF-тракт |",
            "| `5V_U214_PROTECTED` | `NVDC_SYS` → TPS564252 → TPS259470 | Съёмный U214 LoRa Cap |",
            "| `5V_UNIT_PROTECTED` | тот же buck → отдельный TPS259470 | M5 Unit; отказ одной ветви не питает другую |",
        ]
        review = "## Результат H2.5.1"
        review_text = (
            f"✅ **Проведено ревью:** {len(manifest['reviewed_nets'])} критичных силовых "
            "цепей прослежены в реальной KiCad-netlist. UI, RF и LoRa Cap содержат "
            "соответственно 387, 678 и 27 уникально обозначенных компонентов; коллизий "
            "references нет.\n\n"
            "Исправлен fabrication-blocker: локальные `R1/C1/U1` разных дочерних листов "
            "заменены детерминированными диапазонами по номеру листа."
        )
    else:
        title = "# Leshy2 power architecture"
        intro = (
            "[Русский](power-architecture.ru.md) · [Home](../README.md) · "
            "[Schematics](schematics.md)\n\n"
            "This is the final product power architecture. It is checked against the "
            "complete netlist exported by KiCad itself."
        )
        source = "## Sources"
        source_text = (
            "- The sole external source is the main S3 USB-C port: sink only, up to 30 W "
            "(5 V fallback, 9 V × 3 A or 15 V × 2 A). C5 and RP2354B service USB ports "
            "cannot power the product.\n"
            "- Portable power uses two removable protected 18650 cells in series, "
            "6.0–8.4 V. Both cells are required for battery operation."
        )
        charge = "## Input, charging and pack"
        rails = "## Generated rails"
        rail_headers = "| Output | Path | Purpose |\n|---|---|---|"
        rail_rows = [
            "| `AON_SAFE_3V3` | `NVDC_SYS` → TPS629203 → TPS25961 | Always-on safety logic |",
            "| `3V3_MAIN` | `NVDC_SYS` → TPS564252 → TPS25974 | Processors, UI and ordinary logic |",
            "| `VVOICE_4V` | `NVDC_SYS` → TPS564252 → TPS25974 | Voice RF path only |",
            "| `5V_U214_PROTECTED` | `NVDC_SYS` → TPS564252 → TPS259470 | Removable U214 LoRa Cap |",
            "| `5V_UNIT_PROTECTED` | same buck → separate TPS259470 | M5 Unit; one branch cannot feed the other |",
        ]
        review = "## H2.5.1 result"
        review_text = (
            f"✅ **Reviewed:** {len(manifest['reviewed_nets'])} critical power nets are "
            "traced in the actual KiCad netlist. UI, RF and LoRa Cap contain 387, 678 "
            "and 27 uniquely annotated components; there are no reference collisions.\n\n"
            "A fabrication blocker was corrected: child-sheet-local `R1/C1/U1` references "
            "now use deterministic sheet-number ranges."
        )

    pd = parts["pd_controller"]["mpn"]
    charger = parts["nvdc_charger"]["mpn"]
    gauge = parts["pack_gauge"]["mpn"]
    admission = parts["pack_admission"]["mpn"]
    charge_text = (
        f"`USB-C` → **{pd}** → **{charger}** → `NVDC_SYS`.\n\n"
        f"`2× 18650` → "
        f"{'два независимых предохранителя 5 А' if russian else 'two independent 5 A fuses'} → "
        f"**{gauge}** + **{admission}** → "
        f"{'встречно включённые силовые MOSFET' if russian else 'back-to-back power FET'} → "
        f"{'зарядник' if russian else 'charger'}/`NVDC_SYS`."
    )
    return "\n\n".join((
        title, intro, source, source_text, charge, charge_text,
        rails, rail_headers + "\n" + "\n".join(rail_rows), review, review_text,
        "[Machine review evidence](../hardware/ecad/generated/H2-REV51-power-paths.json).",
    )) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [
            path for path, content in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(
            f"ok: H2.5.1 power review is current; "
            f"{len(manifest['reviewed_nets'])} critical nets reviewed"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
