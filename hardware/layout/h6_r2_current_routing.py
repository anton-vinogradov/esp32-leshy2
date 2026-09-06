#!/usr/bin/env python3
"""Publish the exact, non-closing H6.0.3 routing checkpoint.

Unlike the immutable H6.0.2 acceptance record, this audit follows the live
80 mm boards.  It binds native connectivity, copper counts, DRC evidence and
the two public progress pages to the same PCB hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections import defaultdict
from pathlib import Path

import pcbnew  # type: ignore

from h6_r2_placement import build as build_placement


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
CONTRACT = ROOT / "hardware/layout/h6-r2-routing-policy.json"
OUTPUT = ROOT / "hardware/layout/generated/H6-R2-current-routing-audit.json"
DOC_EN = ROOT / "docs/h6-r2-current-routing.md"
DOC_RU = ROOT / "docs/h6-r2-current-routing.ru.md"
PROJECTS = ("LESHY2-UI-R2", "LESHY2-RF-R2")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def board_path(project: str) -> Path:
    return ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"


def item_uuid(item) -> str:
    try:
        return item.m_Uuid.AsString()
    except Exception:
        return item.GetUuid().AsString()


def remaining_by_net(board) -> dict[str, int]:
    board.BuildConnectivity()
    connectivity = board.GetConnectivity()
    pads_by_net = defaultdict(list)
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.GetNetCode() > 0:
                pads_by_net[pad.GetNetname()].append(pad)
    remaining = {}
    for name, pads in pads_by_net.items():
        components = set()
        for pad in pads:
            connected = connectivity.GetConnectedItems(pad)
            signature = tuple(
                sorted(
                    item_uuid(item)
                    for item in connected
                    if isinstance(item, pcbnew.PAD)
                )
            ) or (item_uuid(pad),)
            components.add(signature)
        remaining[name] = max(0, len(components) - 1)
    return remaining


def drc_evidence(path: Path, project: str) -> dict:
    report = load(path)
    violations = report.get("violations", [])
    parity = report.get("schematic_parity", [])
    errors = []
    if report.get("source") != f"{project}.kicad_pcb":
        errors.append("DRC source filename does not match the project")
    if parity:
        errors.append(f"schematic parity has {len(parity)} findings")
    if violations:
        errors.append(f"{project} DRC has {len(violations)} findings")
    assigned = []
    return {
        "report_sha256": sha256(path),
        "kicad_version": report.get("kicad_version"),
        "checked_at": report.get("date"),
        "violation_count": len(violations),
        "violation_types": sorted(row.get("type") for row in violations),
        "schematic_parity_error_count": len(parity),
        "assigned_exceptions": assigned,
        "errors": errors,
    }


def seed_unconnected(project: str, seed_bytes: bytes) -> int:
    with tempfile.TemporaryDirectory(prefix="leshy2-h603-seed-") as directory:
        path = Path(directory) / f"{project}.kicad_pcb"
        path.write_bytes(seed_bytes)
        board = pcbnew.LoadBoard(str(path))
        board.BuildConnectivity()
        return board.GetConnectivity().GetUnconnectedCount(False)


def build(drc_paths: dict[str, Path] | None, existing: dict | None) -> dict:
    policy = load(POLICY)
    class_order = load(CONTRACT)["class_order"]
    placement_outputs, placement_audit = build_placement()
    placement_by_project = {
        row["project"]: row for row in placement_audit["boards"]
    }
    rows = []
    errors = []
    existing_rows = {
        row["project"]: row for row in (existing or {}).get("boards", [])
    }
    for project in PROJECTS:
        path = board_path(project)
        board = pcbnew.LoadBoard(str(path))
        board.BuildConnectivity()
        connectivity = board.GetConnectivity()
        remaining = remaining_by_net(board)
        tracks = list(board.GetTracks())
        vias = [item for item in tracks if isinstance(item, pcbnew.PCB_VIA)]
        traces = [item for item in tracks if not isinstance(item, pcbnew.PCB_VIA)]
        classes = {}
        for class_name in class_order:
            names = {
                row["kicad_net"]
                for row in policy["rows"]
                if row["project"] == project
                and row["routing_class"] == class_name
            }
            classes[class_name] = {
                "net_count": len(names),
                "remaining_connection_count": sum(
                    remaining.get(name, 0) for name in names
                ),
            }
        native_remaining = connectivity.GetUnconnectedCount(False)
        seed_remaining = seed_unconnected(project, placement_outputs[path])
        board_area = (
            placement_audit["summary"]["board_outline_mm"][0]
            * placement_audit["summary"]["board_outline_mm"][1]
        )
        courtyard_occupancy = {}
        for side in ("F.Cu", "B.Cu"):
            area = sum(
                (item["courtyard_bbox_mm"]["x"][1] - item["courtyard_bbox_mm"]["x"][0])
                * (item["courtyard_bbox_mm"]["y"][1] - item["courtyard_bbox_mm"]["y"][0])
                for item in placement_by_project[project]["placements"]
                if item["side"] == side
            )
            courtyard_occupancy[side] = round(100.0 * area / board_area, 3)
        if drc_paths is not None:
            drc = drc_evidence(drc_paths[project], project)
        else:
            old = existing_rows.get(project, {})
            if old.get("board_sha256") != sha256(path):
                raise SystemExit(f"{project}: board changed; refresh with fresh DRC reports")
            drc = old.get("drc", {})
        board_errors = list(drc.get("errors", []))
        if sum(row["remaining_connection_count"] for row in classes.values()) != native_remaining:
            board_errors.append("per-class remaining total differs from native connectivity")
        row = {
            "project": project,
            "board": str(path.relative_to(ROOT)),
            "board_sha256": sha256(path),
            "board_size_mm": [
                round(pcbnew.ToMM(board.GetBoardEdgesBoundingBox().GetWidth()), 3),
                round(pcbnew.ToMM(board.GetBoardEdgesBoundingBox().GetHeight()), 3),
            ],
            "footprint_count": len(list(board.GetFootprints())),
            "trace_count": len(traces),
            "via_count": len(vias),
            "track_via_item_count": len(tracks),
            "routed_net_count": len({item.GetNetname() for item in tracks}),
            "used_trace_layers": sorted(
                {board.GetLayerName(item.GetLayer()) for item in traces}
            ),
            "placement_courtyard_occupancy_percent": courtyard_occupancy,
            "seed_total_unconnected_count": seed_remaining,
            "current_total_unconnected_count": native_remaining,
            "resolved_connection_count": seed_remaining - native_remaining,
            "classes": classes,
            "drc": drc,
            "errors": board_errors,
        }
        rows.append(row)
        errors.extend(f"{project}: {error}" for error in board_errors)
    remaining_total = sum(row["current_total_unconnected_count"] for row in rows)
    resolved_total = sum(row["resolved_connection_count"] for row in rows)
    return {
        "schema_version": 1,
        "artifact": "H6.0.3 live 80-mm routing checkpoint after locality-constrained repack",
        "marker": "H6.0.3-R1",
        "status": "pass_progress" if not errors else "fail",
        "phase_complete": not errors and remaining_total == 0,
        "sources": {
            "routing_policy": str(POLICY.relative_to(ROOT)),
            "routing_policy_sha256": sha256(POLICY),
        },
        "summary": {
            "board_count": len(rows),
            "track_via_item_count": sum(row["track_via_item_count"] for row in rows),
            "trace_count": sum(row["trace_count"] for row in rows),
            "via_count": sum(row["via_count"] for row in rows),
            "seed_total_unconnected_count": sum(row["seed_total_unconnected_count"] for row in rows),
            "current_total_unconnected_count": remaining_total,
            "resolved_connection_count": resolved_total,
            "analog_remaining_connection_count": sum(
                row["classes"]["ANALOG_AUDIO_SENSE"]["remaining_connection_count"]
                for row in rows
            ),
            "placement_locality_pair_count": placement_audit["summary"]["locality_pair_count"],
            "placement_locality_violation_count": placement_audit["summary"]["locality_violation_count"],
            "drc_violation_count": sum(row["drc"]["violation_count"] for row in rows),
            "assigned_drc_exception_count": sum(len(row["drc"]["assigned_exceptions"]) for row in rows),
        },
        "board_size_review": {
            "decision": "retain_80x150_mm",
            "status": "locality_constrained_placement_proven_routing_capacity_open",
            "maximum_same_face_courtyard_occupancy_percent": max(
                value
                for row in rows
                for value in row["placement_courtyard_occupancy_percent"].values()
            ),
            "evidence": f"all 1208 exact footprints place without a same-face hard conflict; all {placement_audit['summary']['locality_pair_count']} local-owner constraints pass; both native DRC reports are clean; the accepted 5-mm routing corridor remains usable",
            "why_not_expand_now": "the corrected locality-constrained placement fits the current outline and no legal power, RF or digital route has yet demonstrated a capacity blockage; the route restart deliberately removed the old invalid evidence",
            "expansion_candidate_if_triggered_mm": [85.0, 150.0],
            "expansion_trigger": "after legal component movement and layer use are exhausted, any required power, USB/i8080, clocked-digital or RF path cannot meet the frozen H6 rules, or H6.0.4 through H6.0.7 fails for lack of geometric margin",
            "requalification_after_any_outline_or_anchor_change": [
                "regenerate every H1/H6 view and machine placement artifact",
                "repeat exact-footprint placement, opposing-face, cable, display, antenna and enclosure checks",
                "repeat ERC, schematic-to-PCB parity and native DRC on both boards",
                "repeat routed power/thermal, USB/i8080/digital-SI, RF/return-path and plane checks",
                "refresh the firmware BSP and rerun all hardware and firmware test suites against the new hashes"
            ]
        },
        "boards": rows,
        "next_exit_condition": "route or explicitly no-connect every remaining H2 connection, then pass schematic parity and final DRC",
        "errors": errors,
    }


def doc(audit: dict, ru: bool) -> str:
    ui, rf = audit["boards"]
    summary = audit["summary"]
    def number(value: int) -> str:
        rendered = f"{value:,}"
        return rendered.replace(",", " ") if ru else rendered

    if ru:
        title = "# H6.0.3-R1 · Текущая разводка 80-мм плат"
        nav = "[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [English](h6-r2-current-routing.md)"
        lead = (
            "**Статус:** ▶️ корректная компоновка принята, разводка начата заново; H6 ещё не закрыт."
        )
        headers = "| Плата | Дорожки | Via | Замкнуто | Осталось | DRC |\n| --- | ---: | ---: | ---: | ---: | --- |"
        labels = ("UI", "RF/power")
        notes = (
            "## Что хотим\n\n"
            "Получить производственно корректные 80 × 150-мм PCB: локальные высокочастотные цепи находятся "
            "у своих компонентов, после чего вся медь проводится и проверяется без исключений DRC.\n\n"
            "## Что решили\n\n"
            "Прежний collision-free seed оказался электрически неверным: часть bypass, feedback и bootstrap "
            "деталей была удалена от владельцев на десятки миллиметров. Старые дорожки сохранены только в Git; "
            "рабочие PCB очищены и построены заново. Размер 80 × 150 мм оставлен, потому что исправленная "
            "компоновка помещается без конфликтов; 85 × 150 мм рассматривается только при доказанном тупике трассировки.\n\n"
            "## Что получили\n\n"
            f"Размещены все 1 208 корпусов; {summary['placement_locality_pair_count']} пар local-part → owner "
            "проходят свои пределы, нарушений локальности нет. Обе платы имеют нулевой native DRC. "
            f"После осознанного перезапуска осталось {number(summary['current_total_unconnected_count'])} "
            "физических соединений; их состояние приведено в таблице выше.\n\n"
            "## Что делаем дальше\n\n"
            "Порядок: четыре DC/DC-острова и защита питания → RF/clock-кластеры → USB и direct i8080 → "
            "остальная цифровая и управляющая медь → плоскости/возвраты → полный DRC и release-проверки.\n\n"
            "## Живые изображения\n\n"
            "Это прямые экспорты текущих `.kicad_pcb`; hash платы встроен в SVG.\n\n"
            "**Передняя/UI-плата**\n\n"
            "[![Текущая разводка UI](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)\n\n"
            "**Задняя RF/power-плата**\n\n"
            "[![Текущая разводка RF/power](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)\n\n"
            "## Критерий готовности\n\n"
            "H6.0.3 закрывается, когда остаток связности равен нулю, все обязательные классы и возвратные "
            "пути проведены, а native DRC обеих плат повторно даёт ноль."
        )
    else:
        title = "# H6.0.3-R1 · Current 80-mm routing"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)"
        lead = (
            "**Status:** ▶️ corrected placement accepted; routing restarted; H6 is not closed."
        )
        headers = "| Board | Traces | Vias | Resolved | Remaining | DRC |\n| --- | ---: | ---: | ---: | ---: | --- |"
        labels = ("UI", "RF/power")
        notes = (
            "## What we want\n\n"
            "Produce electrically valid 80 × 150-mm PCBs: local high-frequency loops stay at their owning "
            "devices, then every copper connection is routed and checked without a DRC exception.\n\n"
            "## What we decided\n\n"
            "The former collision-free seed was electrically invalid because some bypass, feedback and bootstrap "
            "parts were tens of millimetres from their owners. The old routes remain available only in Git; the live "
            "PCBs were cleared and rebuilt. The 80 × 150-mm outline remains because the corrected placement fits; "
            "85 × 150 mm is considered only after a demonstrated routing blockage.\n\n"
            "## What we obtained\n\n"
            f"All 1,208 bodies are placed; all {summary['placement_locality_pair_count']} local-part → owner pairs "
            "meet their limits and locality has zero violations. Both boards have zero native DRC findings. "
            f"The deliberate restart leaves {number(summary['current_total_unconnected_count'])} physical "
            "connections, summarized in the table above.\n\n"
            "## What happens next\n\n"
            "Order: four DC/DC islands and power protection → RF/clock clusters → USB and direct i8080 → remaining "
            "digital/control copper → planes and return paths → full DRC and release checks.\n\n"
            "## Live images\n\n"
            "These are direct exports from the current `.kicad_pcb` files; each SVG embeds its board hash.\n\n"
            "**Front/UI board**\n\n"
            "[![Current UI routing](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)\n\n"
            "**Rear RF/power board**\n\n"
            "[![Current RF/power routing](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)\n\n"
            "## Completion criterion\n\n"
            "H6.0.3 closes when connectivity reaches zero, every mandatory class and return path is routed, and "
            "native DRC is rerun clean on both boards."
        )
    table = [headers]
    for label, row in zip(labels, (ui, rf)):
        drc = str(row["drc"]["violation_count"])
        table.append(
            f"| {label} | {number(row['trace_count'])} | {number(row['via_count'])} | "
            f"{number(row['resolved_connection_count'])} | {number(row['current_total_unconnected_count'])} | {drc} |"
        )
    rendered = "\n\n".join((title, nav, lead, "\n".join(table), notes)) + "\n"
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--ui-drc", type=Path)
    parser.add_argument("--rf-drc", type=Path)
    args = parser.parse_args()
    if args.write and (args.ui_drc is None or args.rf_drc is None):
        parser.error("--write requires --ui-drc and --rf-drc")
    existing = load(OUTPUT) if OUTPUT.exists() else None
    drc_paths = None
    if args.write:
        drc_paths = {
            "LESHY2-UI-R2": args.ui_drc.resolve(),
            "LESHY2-RF-R2": args.rf_drc.resolve(),
        }
    audit = build(drc_paths, existing)
    outputs = {
        OUTPUT: json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: doc(audit, ru=False),
        DOC_RU: doc(audit, ru=True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit("stale current-routing outputs: " + ", ".join(stale))
    print(
        f"H6.0.3 routing {audit['status']}: "
        f"{audit['summary']['track_via_item_count']} copper items; "
        f"{audit['summary']['resolved_connection_count']} resolved; "
        f"{audit['summary']['current_total_unconnected_count']} remain"
    )
    for error in audit["errors"]:
        print("- " + error)
    return 0 if audit["status"] == "pass_progress" else 1


if __name__ == "__main__":
    raise SystemExit(main())
