#!/usr/bin/env python3
"""Prove the H2.6.3 post-correction ERC and symbol-library state is clean."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from h2_review_erc_snapshot import ECAD, REPO, native_snapshot, sha256
from h2_symbol_library import OUTPUT as SYMBOL_LIBRARY, build as build_symbol_library


GENERATED = ECAD / "generated"
OUTPUT = GENERATED / "H2-REV63-erc-clean.json"
NC_REVIEW = GENERATED / "H2-REV62-no-connects.json"


def build() -> tuple[str, dict]:
    nc = json.loads(NC_REVIEW.read_text(encoding="utf-8"))
    if nc.get("stage") != "H2.6.2" or nc.get("open_findings"):
        raise ValueError("H2.6.2 is not closed")
    expected_library = build_symbol_library()
    actual_library = SYMBOL_LIBRARY.read_text(encoding="utf-8")
    if actual_library != expected_library:
        raise ValueError("controlled symbol library differs from embedded schematic definitions")
    projects, version, sources = native_snapshot()
    findings = [
        {"project": row["project"], **finding}
        for row in projects for finding in row["classification"]
    ]
    if findings:
        raise ValueError(f"post-correction native ERC findings remain: {findings}")
    manifest = {
        "schema_version": 1,
        "stage": "H2.6.3",
        "status": "reviewed_clean_native_erc",
        "tool": {"name": "kicad-cli", "version": version},
        "method": "fresh native ERC after corrections plus exact controlled-library reconstruction and closed NC prerequisite",
        "source_hashes": {
            **sources,
            str(SYMBOL_LIBRARY.relative_to(REPO)): sha256(SYMBOL_LIBRARY),
            str(NC_REVIEW.relative_to(REPO)): sha256(NC_REVIEW),
        },
        "projects": projects,
        "checks": {
            "native_error_or_warning_count": 0,
            "shared_symbol_library_equals_embedded_union": True,
            "only_ignored_erc_rule": "lib_symbol_mismatch",
            "intentional_no_connects_reconciled": nc["summary"]["intentional_no_connects"],
            "unexplained_or_unaccounted_findings": 0,
        },
        "corrected_findings": [{
            "id": "H2.6.3-F01",
            "finding": "the root native checks previously treated locally generated symbol-copy diagnostics as expected visible warnings",
            "correction": "root checks now require empty native ERC and the exact library-copy invariant is enforced outside ERC",
        }],
        "open_findings": [],
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content, manifest = build()
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
    elif not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
        print(f"stale: {OUTPUT.relative_to(REPO)}")
        return 1
    else:
        print(f"ok: H2.6.3 native ERC is clean across {len(manifest['projects'])} projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
