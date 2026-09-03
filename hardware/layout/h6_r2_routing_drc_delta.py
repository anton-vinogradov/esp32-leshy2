#!/usr/bin/env python3
"""Compare KiCad DRC JSON for a clean round-trip and a routed candidate."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
NET_IN_DESCRIPTION = re.compile(r"\[([^\]<>]+)\]")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def item_net(description: str) -> str | None:
    match = NET_IN_DESCRIPTION.search(description)
    return match.group(1) if match else None


def violation_fingerprint(row: dict) -> tuple:
    return (
        row["type"],
        row["description"],
        tuple(sorted(item["uuid"] for item in row["items"])),
    )


def allowed_unconnected(rows: list[dict], allowed_nets: set[str]) -> list[dict]:
    return [
        row
        for row in rows
        if any(item_net(item["description"]) in allowed_nets for item in row["items"])
    ]


def compare(project: str, baseline_path: Path, candidate_path: Path) -> dict:
    audit = load(AUDIT)
    allowed_classes = set(audit["automatic_helper"]["allowed_classes"])
    allowed_nets = {
        row["kicad_net"]
        for row in audit["rows"]
        if row["project"] == project and row["routing_class"] in allowed_classes
    }
    baseline = load(baseline_path)
    candidate = load(candidate_path)
    baseline_fingerprints = {
        violation_fingerprint(row) for row in baseline["violations"]
    }
    new_violations = [
        row
        for row in candidate["violations"]
        if violation_fingerprint(row) not in baseline_fingerprints
    ]
    baseline_allowed = allowed_unconnected(baseline["unconnected_items"], allowed_nets)
    candidate_allowed = allowed_unconnected(candidate["unconnected_items"], allowed_nets)
    new_types = Counter((row["severity"], row["type"]) for row in new_violations)
    status = "pass" if not new_violations and not candidate_allowed else "fail"
    return {
        "schema_version": 1,
        "artifact": "H6-R2 routing-candidate DRC delta",
        "status": status,
        "project": project,
        "allowed_classes": sorted(allowed_classes),
        "allowed_net_count": len(allowed_nets),
        "baseline": {
            "report": str(baseline_path),
            "violation_count": len(baseline["violations"]),
            "unconnected_count": len(baseline["unconnected_items"]),
            "allowed_unconnected_count": len(baseline_allowed),
        },
        "candidate": {
            "report": str(candidate_path),
            "violation_count": len(candidate["violations"]),
            "unconnected_count": len(candidate["unconnected_items"]),
            "allowed_unconnected_count": len(candidate_allowed),
        },
        "allowed_unconnected_reduction": len(baseline_allowed) - len(candidate_allowed),
        "new_violation_count": len(new_violations),
        "new_violation_counts": [
            {"severity": severity, "type": kind, "count": count}
            for (severity, kind), count in sorted(new_types.items())
        ],
        "new_violations": new_violations,
        "acceptance": "zero new DRC violations and zero remaining allowed-class unconnected items",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compare(
        args.project,
        args.baseline.resolve(),
        args.candidate.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"H6-R2 routing DRC delta {report['status']}: {report['project']}; "
        f"{report['allowed_unconnected_reduction']} allowed connections resolved; "
        f"{report['candidate']['allowed_unconnected_count']} remain; "
        f"{report['new_violation_count']} new violations"
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
