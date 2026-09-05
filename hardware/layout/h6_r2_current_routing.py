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
    if project == "LESHY2-UI-R2":
        if violations:
            errors.append(f"UI DRC has {len(violations)} findings")
        assigned = []
    else:
        types = sorted(row.get("type") for row in violations)
        descriptions = " ".join(
            item.get("description", "")
            for row in violations
            for item in row.get("items", [])
        )
        expected = ["hole_clearance", "solder_mask_bridge"]
        if types != expected or "BT1" not in descriptions or "J12" not in descriptions:
            errors.append("RF DRC differs from the two assigned BT1/J12 exceptions")
        assigned = [
            "BT1 pad 1 versus J12 NPTH hole clearance",
            "BT1 pad 1 versus J12 front-mask bridge",
        ]
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
    placement_outputs, _ = build_placement()
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
    return {
        "schema_version": 1,
        "artifact": "H6.0.3 live 80-mm routing checkpoint",
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
            "resolved_connection_count": sum(row["resolved_connection_count"] for row in rows),
            "analog_remaining_connection_count": sum(
                row["classes"]["ANALOG_AUDIO_SENSE"]["remaining_connection_count"]
                for row in rows
            ),
            "drc_violation_count": sum(row["drc"]["violation_count"] for row in rows),
            "assigned_drc_exception_count": sum(len(row["drc"]["assigned_exceptions"]) for row in rows),
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
            "**Статус:** ▶️ проверенный промежуточный срез, не закрытие H6. "
            f"В двух текущих PCB {number(summary['track_via_item_count'])} элементов меди; "
            f"штатная связность KiCad показывает {number(summary['current_total_unconnected_count'])} оставшихся "
            f"и {number(summary['resolved_connection_count'])} уже замкнутых физических соединений."
        )
        headers = "| Плата | Дорожки | Via | Замкнуто | Осталось | DRC |\n| --- | ---: | ---: | ---: | ---: | --- |"
        labels = ("UI", "RF/power")
        notes = (
            "## Что изменилось в этом срезе\n\n"
            "После перехода 75 → 80 мм бесконфликтные аналоговые/audio/sense-трассы перенесены по точным "
            "якорям площадок. Конфликтующие старые ветви отброшены, а не протащены через новую геометрию; "
            "оставшиеся восемь UI-связей затем заново проложены в текущей геометрии и прошли DRC. "
            "На RF/power локально раскрыты eFuse-кластеры U17 и U100, добавлены пять недостающих аналоговых "
            "связей, а вытесненная safety/control-медь полностью переложена до принятия результата. "
            "В аудиокластере замкнуты `CODEC_DACVREF` и оба входа ADC; соседние headphone- и `CODEC_TX_AC`-трассы "
            "полностью переложены и сохранили исходную связность. "
            "Для `AUDIO_CAPTURE_MIC_SEL` низкоскоростной pull-down R53 перенесён из коридора выхода U106, "
            "после чего обе соседние цепи U106 получили независимые пути без нового DRC. "
            f"В классе `ANALOG_AUDIO_SENSE` осталось {summary['analog_remaining_connection_count']} физических соединений: "
            f"{ui['classes']['ANALOG_AUDIO_SENSE']['remaining_connection_count']} на UI и "
            f"{rf['classes']['ANALOG_AUDIO_SENSE']['remaining_connection_count']} на RF/power.\n\n"
            "Штатный DRC KiCad даёт ноль замечаний на UI. На RF/power остаются только два уже назначенных "
            "исключения одного места `BT1`/`J12`: зазор отверстий и объединение апертур передней маски. "
            "Новых нарушений разводка не добавляет.\n\n"
            "## Живые изображения\n\n"
            "Это прямые экспорты из текущих `.kicad_pcb`; hash платы встроен в SVG.\n\n"
            "**Передняя/UI-плата**\n\n"
            "[![Текущая разводка UI](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)\n\n"
            "**Задняя RF/power-плата**\n\n"
            "[![Текущая разводка RF/power](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)\n\n"
            "## Что ещё не доказано\n\n"
            "Свободная площадь и 5-мм коридор пока достаточны для принятой меди, но запас нельзя считать "
            "окончательно подтверждённым до завершения питания, USB/i8080/тактируемых шин, RF и плоскостей. "
            "H6.0.3 закрывается только при нулевом необъяснённом остатке."
        )
    else:
        title = "# H6.0.3-R1 · Current 80-mm routing"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)"
        lead = (
            "**Status:** ▶️ checked progress snapshot, not H6 closure. "
            f"The two live PCBs contain {number(summary['track_via_item_count'])} copper items; native KiCad "
            f"connectivity reports {number(summary['current_total_unconnected_count'])} remaining and "
            f"{number(summary['resolved_connection_count'])} already resolved physical connections."
        )
        headers = "| Board | Traces | Vias | Resolved | Remaining | DRC |\n| --- | ---: | ---: | ---: | ---: | --- |"
        labels = ("UI", "RF/power")
        notes = (
            "## What changed in this snapshot\n\n"
            "After the 75 → 80 mm transition, conflict-free analogue/audio/sense routing was transferred by exact "
            "pad anchors. Old branches that conflicted with the new geometry were discarded rather than forced into "
            "the board; the remaining eight UI connections were then rerouted in the live geometry and passed DRC. "
            "On RF/power, the U17 and U100 eFuse neighbourhoods were locally opened, five missing analogue "
            "connections were added, and the displaced safety/control copper was fully rerouted before acceptance. "
            "In the audio cluster, `CODEC_DACVREF` and both ADC inputs are now connected; the neighbouring headphone "
            "and `CODEC_TX_AC` routes were fully rerouted while preserving their original connectivity. "
            "For `AUDIO_CAPTURE_MIC_SEL`, the low-speed R53 pull-down was moved out of the U106 escape corridor, "
            "then both adjacent U106 nets received independent paths without a new DRC finding. "
            f"`ANALOG_AUDIO_SENSE` now has {summary['analog_remaining_connection_count']} physical connections "
            f"left: {ui['classes']['ANALOG_AUDIO_SENSE']['remaining_connection_count']} on UI and "
            f"{rf['classes']['ANALOG_AUDIO_SENSE']['remaining_connection_count']} on RF/power.\n\n"
            "Native KiCad DRC reports zero UI findings. RF/power retains only the two already assigned findings at "
            "the single `BT1`/`J12` location: hole clearance and a front-mask aperture bridge. The new routing adds no violation.\n\n"
            "## Live images\n\n"
            "These are direct exports from the live `.kicad_pcb` files; each SVG embeds its board hash.\n\n"
            "**Front/UI board**\n\n"
            "[![Current UI routing](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)\n\n"
            "**Rear RF/power board**\n\n"
            "[![Current RF/power routing](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)\n\n"
            "## What is not proven yet\n\n"
            "The available area and 5-mm corridor are sufficient for the accepted copper so far, but final margin "
            "cannot be claimed before power, USB/i8080/clocked buses, RF and reference planes are complete. H6.0.3 "
            "closes only with no unexplained connectivity residual."
        )
    table = [headers]
    for label, row in zip(labels, (ui, rf)):
        drc = "0" if row["drc"]["violation_count"] == 0 else "2 assigned BT1/J12"
        table.append(
            f"| {label} | {number(row['trace_count'])} | {number(row['via_count'])} | "
            f"{number(row['resolved_connection_count'])} | {number(row['current_total_unconnected_count'])} | {drc} |"
        )
    rendered = "\n\n".join((title, nav, lead, "\n".join(table), notes)) + "\n"
    if ru:
        rendered = rendered.replace("2 assigned BT1/J12", "2 назначенных BT1/J12")
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
