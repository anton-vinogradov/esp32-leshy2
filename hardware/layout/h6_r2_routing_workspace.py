#!/usr/bin/env python3
"""Export temporary Specctra workspaces with H6 fail-closed routing classes.

The generated DSN files are disposable helper inputs, never release artifacts.
Run with KiCad's bundled Python so pcbnew can export the native boards.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "hardware/layout/h6-r2-routing-policy.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
PLACEMENT = ROOT / "hardware/layout/h6-r2-placement-contract.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matching_close(text: str, start: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("unterminated Specctra class block")


def wrap_atoms(prefix: str, atoms: list[str], indent: str = "      ", limit: int = 112) -> list[str]:
    lines = [prefix]
    for atom in atoms:
        if len(lines[-1]) + 1 + len(atom) <= limit:
            lines[-1] += " " + atom
        else:
            lines.append(indent + atom)
    return lines


def class_block(project: str, policy: dict, audit: dict, classes_to_emit: set[str]) -> str:
    rows = [row for row in audit["rows"] if row["project"] == project]
    grouped = {name: [] for name in policy["class_order"]}
    for row in rows:
        grouped[row["routing_class"]].append(row["kicad_net"])
    lines = []
    for class_name in policy["class_order"]:
        if class_name not in classes_to_emit:
            continue
        names = sorted(grouped[class_name])
        if not names:
            continue
        width_mm = policy["classes"][class_name]["nominal_track_width_mm"]
        width_um = int(round((width_mm if width_mm is not None else 0.15) * 1000))
        class_lines = wrap_atoms(f"    (class {class_name}", names)
        class_lines.extend([
            "      (circuit",
            '        (use_via "Via[0-5]_400:200_um")',
            "      )",
            "      (rule",
            f"        (width {width_um})",
            "        (clearance 150)",
            "      )",
            "    )",
        ])
        lines.extend(class_lines)
    return "\n".join(lines)


def replace_default_class(
    dsn: str,
    project: str,
    policy: dict,
    audit: dict,
    classes_to_emit: set[str],
) -> str:
    marker = "(class kicad_default"
    start = dsn.find(marker)
    if start < 0:
        raise ValueError(f"{project}: kicad_default class is absent")
    line_start = dsn.rfind("\n", 0, start) + 1
    end = matching_close(dsn, start)
    replaced = dsn[:line_start] + class_block(project, policy, audit, classes_to_emit) + dsn[end:]
    emitted_class_count = sum(
        1
        for class_name in policy["class_order"]
        if class_name in classes_to_emit
        and any(row["project"] == project and row["routing_class"] == class_name for row in audit["rows"])
    )
    if replaced.count("(class ") != emitted_class_count:
        raise ValueError(f"{project}: emitted routing-class count differs from policy")
    if "(class kicad_default" in replaced:
        raise ValueError(f"{project}: default class survived replacement")
    return replaced


def prune_network_to_allowed(dsn: str, project: str, allowed_nets: set[str]) -> str:
    network_marker = "(network"
    network_start = dsn.find(network_marker)
    if network_start < 0:
        raise ValueError(f"{project}: network block is absent")
    network_end = matching_close(dsn, network_start)
    network = dsn[network_start:network_end]
    matches = list(re.finditer(r"(?m)^    \(net ([^\s()]+)", network))
    present = {match.group(1) for match in matches}
    missing = sorted(allowed_nets - present)
    if missing:
        raise ValueError(f"{project}: allowed nets absent from DSN: {missing[:10]}")
    for match in reversed(matches):
        if match.group(1) in allowed_nets:
            continue
        block_start = match.start()
        paren_start = block_start + 4
        block_end = matching_close(network, paren_start)
        if block_end < len(network) and network[block_end] == "\n":
            block_end += 1
        network = network[:block_start] + network[block_end:]
    if network.count("\n    (net ") != len(allowed_nets):
        raise ValueError(f"{project}: pruned helper-net count differs from allow-list")
    return dsn[:network_start] + network + dsn[network_end:]


def export(output_dir: Path) -> dict:
    try:
        import pcbnew  # type: ignore
    except ModuleNotFoundError as exc:
        raise SystemExit("run with KiCad's bundled Python 3.9 runtime") from exc
    policy = load(POLICY)
    audit = load(AUDIT)
    placement = load(PLACEMENT)
    if audit["status"] != "pass":
        raise SystemExit("routing policy audit is not passing")
    output_dir.mkdir(parents=True, exist_ok=True)
    projects = []
    for project, board_data in sorted(placement["boards"].items()):
        board_path = ROOT / board_data["output"]
        raw_path = output_dir / f"{project}.raw.dsn"
        output_path = output_dir / f"{project}.routing.dsn"
        board = pcbnew.LoadBoard(str(board_path))
        if not pcbnew.ExportSpecctraDSN(board, str(raw_path)):
            raise SystemExit(f"KiCad failed to export {project}")
        allowed_classes = set(policy["automatic_helper"]["allowed_classes"])
        allowed_nets = {
            row["kicad_net"]
            for row in audit["rows"]
            if row["project"] == project and row["routing_class"] in allowed_classes
        }
        transformed = prune_network_to_allowed(
            raw_path.read_text(encoding="utf-8"), project, allowed_nets
        )
        transformed = replace_default_class(
            transformed, project, policy, audit, allowed_classes
        )
        output_path.write_text(transformed, encoding="utf-8")
        raw_path.unlink()
        counts = audit["boards"][project]["class_counts"]
        projects.append({
            "project": project,
            "board": str(board_path.relative_to(ROOT)),
            "board_sha256": sha256(board_path),
            "dsn": str(output_path),
            "dsn_sha256": sha256(output_path),
            "physical_net_count": audit["boards"][project]["physical_net_count"],
            "class_counts": counts,
            "helper_net_count": len(allowed_nets),
            "omitted_protected_net_count": audit["boards"][project]["physical_net_count"] - len(allowed_nets),
            "emitted_class_count": sum(1 for name in allowed_classes if counts[name]),
        })
    ignored = policy["automatic_helper"]["locked_or_ignored_classes"]
    manifest = {
        "schema_version": 1,
        "artifact": "temporary H6-R2 constrained routing workspace",
        "status": "pass",
        "source_hashes": {
            str(POLICY.relative_to(ROOT)): sha256(POLICY),
            str(AUDIT.relative_to(ROOT)): sha256(AUDIT),
            str(PLACEMENT.relative_to(ROOT)): sha256(PLACEMENT),
        },
        "projects": projects,
        "freerouting_ignore_classes": ignored,
        "freerouting_ignore_argument": ",".join(ignored),
        "allowed_classes": policy["automatic_helper"]["allowed_classes"],
        "headless_filter_method": "protected net definitions omitted from disposable DSN because Freerouting 2.3.0 applies -inc inside its GUI loader only; original KiCad boards remain complete",
        "acceptance": policy["automatic_helper"]["acceptance"],
    }
    manifest_path = output_dir / "routing-workspace-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = export(args.output_dir.resolve())
    print(
        "H6-R2 routing workspace pass: "
        f"{len(manifest['projects'])} DSNs; allowed {','.join(manifest['allowed_classes'])}; "
        f"omitted {len(manifest['freerouting_ignore_classes'])} protected classes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
