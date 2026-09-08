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

from h6_r2_drc import validate_provenance, validate_receipt
from h6_r2_manual_copper import build as build_manual_copper, copper_signature
from h6_r2_placement import build as build_placement, placement_signature_bytes


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
CONTRACT = ROOT / "hardware/layout/h6-r2-routing-policy.json"
MANUAL_COPPER_AUDIT = ROOT / "hardware/layout/generated/H6-R2-manual-copper-audit.json"
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
    provenance = validate_provenance(path, project)
    report = load(path)
    violations = report.get("violations", [])
    parity = report["schematic_parity"]
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
        "provenance": provenance,
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
    if placement_audit["status"] != "pass":
        raise SystemExit("current-routing publication requires a passing placement audit")
    manual_outputs, manual_audit = build_manual_copper()
    if MANUAL_COPPER_AUDIT.read_bytes() != manual_outputs[MANUAL_COPPER_AUDIT]:
        raise SystemExit("manual copper inputs changed; regenerate successfully before publishing routing")
    manual_by_project = {row["project"]: row for row in manual_audit["boards"]}
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
        actual_placement = hashlib.sha256(placement_signature_bytes(project, board)).hexdigest()
        if actual_placement != placement_by_project[project]["placement_signature_sha256"]:
            raise SystemExit(f"{project}: board placement differs from the current placement contract")
        expected_copper = [tuple(row) for row in manual_by_project[project]["copper_signature"]]
        if copper_signature(board) != expected_copper:
            raise SystemExit(f"{project}: board copper differs from the current manual routing contract")
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
            validate_receipt(drc.get("provenance", {}), project, drc.get("report_sha256", ""))
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
            "manual_copper": str(MANUAL_COPPER_AUDIT.relative_to(ROOT)),
            "manual_copper_sha256": sha256(MANUAL_COPPER_AUDIT),
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
            "placement_critical_pad_pair_count": placement_audit["summary"]["critical_pad_pair_count"],
            "placement_critical_pad_pair_violation_count": placement_audit["summary"]["critical_pad_pair_violation_count"],
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
            "evidence": f"all 1208 currently modeled footprints place without a same-face hard conflict; all {placement_audit['summary']['locality_pair_count']} local-owner constraints and {placement_audit['summary']['critical_pad_pair_count']} critical pad-pair limits pass; both native DRC reports are clean; the accepted 5-mm routing corridor remains usable. The separate native interface review still contains footprint, cutout and assembly-access findings; these checks do not certify the modeled geometry against every real part",
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
        "next_exit_condition": "close H6-NATIVE-ELECTRICAL-SEMANTICS with reviewed physical-pin types, rail-source/output checks and fresh ERC; route or explicitly no-connect every remaining H2 connection, then pass schematic parity and final DRC",
        "errors": errors,
    }


def doc(audit: dict, manual_copper: dict, ru: bool) -> str:
    ui, rf = audit["boards"]
    summary = audit["summary"]
    active_route_count = len(manual_copper["routes"])
    controlled_rf = [
        row for row in manual_copper["routes"] if row["routing_class"] == "RF_CONTROLLED"
    ]
    rf_route_count = len(controlled_rf)
    rf_resolved_count = sum(row["resolved_connections"] for row in controlled_rf)
    rf_via_route_count = sum(row["via_count"] > 0 for row in controlled_rf)
    rf_via_free_route_count = rf_route_count - rf_via_route_count
    def number(value: int) -> str:
        rendered = f"{value:,}"
        return rendered.replace(",", " ") if ru else rendered

    if ru:
        title = "# H6.0.3-R1 · Текущая разводка 80-мм плат"
        nav = "[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [English](h6-r2-current-routing.md)"
        lead = (
            "**Статус:** ▶️ разводка и исправление физических интерфейсов продолжаются; H6 ещё не закрыт. "
            "[Ревью настоящих PCB](h6-r2-interface-review.ru.md) выявило ошибки ориентации, сочленения и обязательных отверстий; нулевой DRC не означает готовность сборки."
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
            f"проходят свои пределы; набор из {summary['placement_critical_pad_pair_count']} точных проверок "
            "расстояния между площадками охватывает все импульсные цепи и выбранные локальные bypass-цепи, "
            "нарушений нет. "
            "Все десять торцевых SMA развёрнуты корпусом наружу; площадки пайки на F.Cu и B.Cu "
            "находятся внутри контура PCB, а исправленное размещение повторно зафиксировано. "
            "Совместимость допусков толщины PCB и посадочного зазора SMA остаётся открытым вопросом "
            "[механического стека](h6-r2-mechanical-stack.ru.md). "
            "Исправлены исторические power-alias S3/C5: оба домена теперь подключены к `3V3_MAIN`; "
            "десять bypass-компонентов возвращены к своим владельцам, уточнена локальность дросселя LNA. "
            "Это исправление электрического воплощения и компоновки, без изменения функций устройства. "
            "Все пять oscillator-узлов — два RP2354, CC1101, Si5351A и Si4732 — остаются проведёнными "
            "и проходят DRC; исправление RF-корпусов их не затронуло.\n\n"
            "Проверка первичных чертежей обнаружила ошибки top/bottom-view нумерации TTM, ориентации "
            "портов CP0603 и площадок WBC. После исправления посадочных мест из текущей разводки "
            "сняты 23 затронутых RF-маршрута: они не считаются готовыми, а их прежняя медь доступна в Git. "
            "Точный список и причина зафиксированы в "
            "[контракте ручной меди](../hardware/layout/h6-r2-manual-copper.json). "
            f"Текущий аудит содержит {number(active_route_count)} активных ручных маршрутов всех классов; "
            "снятые маршруты уже исключены из этих чисел и таблицы связности. "
            f"Оставшиеся controlled-RF маршруты: {number(rf_route_count)}; закрыто соединений: {number(rf_resolved_count)}. "
            f"Из них без via — {number(rf_via_free_route_count)}, с via — {number(rf_via_route_count)}. "
            "Тракты S3, C5, трёх nRF24, CC1101 и Airband не объявляются полностью разведёнными: "
            "затронутые RF-переходы и ответвления детекторов требуется провести заново к исправленным площадкам. "
            "RF-launch, сплошные плоскости и возвратные пути ещё предстоит завершить и проверить. "
            "Обе платы имеют нулевой native DRC. "
            f"После осознанного перезапуска осталось {number(summary['current_total_unconnected_count'])} "
            "физических соединений; их состояние приведено в таблице выше.\n\n"
            "Два UI-маршрута `NRF0_TX_LED_A` и `S3_TX_LED_A` добавлены как проверенные вручную "
            "предложения `GENERAL_CONTROL`: 10 дорожек по 0,15 мм и два сквозных via 0,4/0,2 мм. "
            "Их via находятся вне корпусов на обеих сторонах; исходная медь и все позиции сохранены. "
            "Конечный список из этих двух сетей, хеши геометрии, связность и native DRC проверяются отдельно: "
            "разрешение вспомогательного маршрутизатора не является автоматическим приёмом результата.\n\n"
            "## Предел текущего ERC\n\n"
            "Рабочая библиотека по-прежнему использует `passive` для подключаемых выводов; "
            "её нулевой ERC не доказывает наличие питания или совместимость выходов. Проверенные типы "
            "применены только к изолированным копиям схем: совпадение reference/pin → net в исходном и "
            "типизированном XML проверяется без изменения топологии. Текущий "
            "[типизированный ERC](h6-r2-electrical-semantics.ru.md) сохраняет 24 замечания: "
            "22 `power_pin_not_driven`, одно о выходах ACDRV1/ACDRV2 и одно `pin_not_driven` "
            "на SA818S H/L. [Разбор источников](../hardware/verification/h6-electrical-source-triage.json) "
            "имеет статус `triaged_not_cleared`: объяснения цепей и допустимых конфигураций не подавляют "
            "ERC, не добавляют безусловных источников и не квалифицируют питание или запуск. "
            "Общий электрический gate остаётся `review_required`; типы не перенесены в рабочую "
            "библиотеку, производство не разрешено.\n\n"
            "Первый [электрический ревью-проход](h6-r2-electrical-semantics.ru.md) исправил "
            "распиновку трёх типов микросхем и восстановил питание встроенной flash обоих RP2354. "
            "Их конденсаторы перенесены к выводу 69. Частичный ERC на копиях с уточнёнными типами "
            "выводов уже выполнен; он не закрывает электрическую проверку целиком.\n\n"
            "## Что делаем дальше\n\n"
            "Продолжаем `H6-NATIVE-ELECTRICAL-SEMANTICS`: проверку остальных типов физических выводов, источников шин, "
            "конфликтов выходов и повторного ERC. Затем четыре DC/DC-острова и защита питания → RF/clock-кластеры → USB и direct i8080 → "
            "остальная цифровая и управляющая медь → плоскости/возвраты → полный DRC и release-проверки.\n\n"
            "## Живые изображения\n\n"
            "Это прямые экспорты текущих `.kicad_pcb`; hash платы встроен в SVG.\n\n"
            "**Передняя/UI-плата**\n\n"
            "[![Текущая разводка UI](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)\n\n"
            "**Задняя RF/power-плата**\n\n"
            "[![Текущая разводка RF/power](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)\n\n"
            "## Критерий готовности\n\n"
            "H6.0.3 закрывается, когда пройден `H6-NATIVE-ELECTRICAL-SEMANTICS`, "
            "остаток связности равен нулю, все обязательные классы и возвратные "
            "пути проведены, а native DRC обеих плат повторно даёт ноль."
        )
    else:
        title = "# H6.0.3-R1 · Current 80-mm routing"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-current-routing.ru.md)"
        lead = (
            "**Status:** ▶️ routing and physical-interface corrections continue; H6 is not closed. "
            "The [native PCB review](h6-r2-interface-review.md) found orientation, mating and required-hole defects; clean DRC does not establish assembly readiness."
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
            f"meet their limits; {summary['placement_critical_pad_pair_count']} actual pad-centre pairs cover every "
            "switching-node net and selected local bypasses with zero violations. "
            "All ten edge-launch SMA bodies face outward; their F.Cu and B.Cu solder lands remain inside "
            "the PCB outline, and the corrected placement is frozen again. The PCB-thickness and SMA-slot "
            "tolerance fit remains an open item in the [mechanical stack](h6-r2-mechanical-stack.md). "
            "The historical S3/C5 power aliases are corrected: both domains now use `3V3_MAIN`; "
            "ten bypass parts were returned to their owners and the LNA choke locality was corrected. "
            "These electrical-realization and placement fixes do not change product functionality. "
            "All five oscillator cells — two RP2354s, CC1101, Si5351A and Si4732 — remain routed and "
            "DRC-clean; the RF-package correction did not change them.\n\n"
            "Primary-drawing review found TTM top/bottom-view numbering errors, CP0603 port-orientation "
            "errors and incorrect WBC lands. After correcting the footprints, 23 affected RF routes were "
            "withdrawn from the current routing: they no longer count as complete, and their former copper "
            "remains available in Git. The exact list and reason are recorded in the "
            "[manual-copper contract](../hardware/layout/h6-r2-manual-copper.json). "
            f"The current audit contains {number(active_route_count)} active manual routes across all classes; "
            "the withdrawn routes are already excluded from these counts and the connectivity table. "
            f"The remaining {number(rf_route_count)} controlled-RF routes close {number(rf_resolved_count)} connections; "
            f"{number(rf_via_free_route_count)} are via-free and {number(rf_via_route_count)} use vias. "
            "The S3, C5, three nRF24, CC1101 and Airband paths are not claimed to be fully routed: "
            "the affected RF interconnects and detector branches must be rerouted to the corrected pads. "
            "RF launches, continuous planes and return paths still require completion and verification. "
            "Both boards have zero native DRC findings. "
            f"The deliberate restart leaves {number(summary['current_total_unconnected_count'])} physical "
            "connections, summarized in the table above.\n\n"
            "The two UI nets `NRF0_TX_LED_A` and `S3_TX_LED_A` were added as hand-reviewed "
            "`GENERAL_CONTROL` proposals: ten 0.15 mm traces and two 0.4/0.2 mm through vias. "
            "Their vias are outside bodies on both faces; existing copper and every placement are retained. "
            "The finite two-net allowlist, geometry hashes, connectivity and native DRC are checked separately: "
            "permission to use a routing helper does not automatically admit its result.\n\n"
            "## Current ERC limitation\n\n"
            "The production library still uses `passive` for connectable pins; its zero ERC result "
            "does not establish supply availability or compatible outputs. Reviewed types are applied "
            "only to isolated schematic copies: original and typed XML reference/pin-to-net membership "
            "must remain identical, without topology changes. The current "
            "[typed ERC](h6-r2-electrical-semantics.md) retains 24 findings: 22 `power_pin_not_driven`, "
            "one ACDRV1/ACDRV2 output conflict and one `pin_not_driven` on SA818S H/L. "
            "The [source-path triage](../hardware/verification/h6-electrical-source-triage.json) remains "
            "`triaged_not_cleared`: source/configuration explanations do not suppress ERC, add "
            "unconditional power sources or qualify rail and startup behavior. The electrical gate "
            "remains `review_required`; reviewed types have not been promoted to the production library "
            "and manufacturing is not authorized.\n\n"
            "The first [electrical-review pass](h6-r2-electrical-semantics.md) corrected three "
            "device pin maps and restored both RP2354 internal-flash supplies. Their bypasses moved "
            "beside pad 69. Partial ERC has run on copies with reviewed pin types; this does not "
            "close the whole electrical review.\n\n"
            "## What happens next\n\n"
            "Continue `H6-NATIVE-ELECTRICAL-SEMANTICS`: remaining physical-pin types, rail sources, output conflicts "
            "and fresh ERC. Then four DC/DC islands and power protection → RF/clock clusters → USB and direct i8080 → remaining "
            "digital/control copper → planes and return paths → full DRC and release checks.\n\n"
            "## Live images\n\n"
            "These are direct exports from the current `.kicad_pcb` files; each SVG embeds its board hash.\n\n"
            "**Front/UI board**\n\n"
            "[![Current UI routing](images/h6-r2-routing-ui.svg)](images/h6-r2-routing-ui.svg)\n\n"
            "**Rear RF/power board**\n\n"
            "[![Current RF/power routing](images/h6-r2-routing-rf.svg)](images/h6-r2-routing-rf.svg)\n\n"
            "## Completion criterion\n\n"
            "H6.0.3 closes when `H6-NATIVE-ELECTRICAL-SEMANTICS` passes, connectivity reaches zero, "
            "every mandatory class and return path is routed, and "
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
    if audit["errors"]:
        raise SystemExit("current-routing publication failed: " + "; ".join(audit["errors"]))
    manual_copper = load(MANUAL_COPPER_AUDIT)
    outputs = {
        OUTPUT: json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: doc(audit, manual_copper, ru=False),
        DOC_RU: doc(audit, manual_copper, ru=True),
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
