#!/usr/bin/env python3
"""Validate the pinned Leshy2 critical-compute KiCad library.

The checks intentionally use only Python's standard library so they can run in
CI and on a clean review workstation.  They lock both the reviewed file
snapshots and canonical pin/pad signatures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


KICAD_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = KICAD_ROOT / "provenance" / "critical-compute-libraries.json"
TOKEN_RE = re.compile(r'\s*(?:(\()|(\))|("(?:\\.|[^"\\])*")|([^()\s]+))')


class ValidationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tokenize(text: str) -> Iterable[str]:
    pos = 0
    while pos < len(text):
        match = TOKEN_RE.match(text, pos)
        if not match:
            if text[pos:].strip():
                raise ValidationError(f"cannot tokenize near byte {pos}")
            return
        pos = match.end()
        opening, closing, quoted, atom = match.groups()
        if opening:
            yield "("
        elif closing:
            yield ")"
        elif quoted is not None:
            yield json.loads(quoted)
        elif atom is not None:
            yield atom


def parse_sexpr(path: Path) -> list[Any]:
    stack: list[list[Any]] = []
    roots: list[Any] = []
    for token in tokenize(path.read_text(encoding="utf-8")):
        if token == "(":
            form: list[Any] = []
            if stack:
                stack[-1].append(form)
            else:
                roots.append(form)
            stack.append(form)
        elif token == ")":
            if not stack:
                raise ValidationError(f"{path}: unexpected ')'")
            stack.pop()
        else:
            if not stack:
                raise ValidationError(f"{path}: atom outside list")
            stack[-1].append(token)
    if stack:
        raise ValidationError(f"{path}: unclosed list")
    if len(roots) != 1:
        raise ValidationError(f"{path}: expected one root expression, got {len(roots)}")
    return roots[0]


def direct_forms(form: list[Any], key: str) -> list[list[Any]]:
    return [
        item
        for item in form[1:]
        if isinstance(item, list) and item and item[0] == key
    ]


def walk_forms(form: list[Any], key: str) -> Iterable[list[Any]]:
    for item in form:
        if not isinstance(item, list) or not item:
            continue
        if item[0] == key:
            yield item
        yield from walk_forms(item, key)


def first_direct(form: list[Any], key: str) -> list[Any] | None:
    forms = direct_forms(form, key)
    return forms[0] if forms else None


def symbol_form(path: Path, name: str) -> list[Any]:
    root = parse_sexpr(path)
    if not root or root[0] != "kicad_symbol_lib":
        raise ValidationError(f"{path}: not a KiCad symbol library")
    for form in direct_forms(root, "symbol"):
        if len(form) > 1 and form[1] == name:
            return form
    raise ValidationError(f"{path}: top-level symbol {name!r} not found")


def properties(symbol: list[Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for prop in direct_forms(symbol, "property"):
        offset = 1
        if len(prop) > 1 and prop[1] == "private":
            offset = 2
        if len(prop) > offset + 1:
            result[str(prop[offset])] = str(prop[offset + 1])
    return result


def pin_rows(symbol: list[Any]) -> list[list[str]]:
    rows: list[list[str]] = []
    for pin in walk_forms(symbol, "pin"):
        if len(pin) < 3:
            continue
        name = first_direct(pin, "name")
        number = first_direct(pin, "number")
        if name and number and len(name) > 1 and len(number) > 1:
            rows.append([str(number[1]), str(name[1]), str(pin[1])])
    return sorted(rows, key=lambda row: (int(row[0]) if row[0].isdigit() else 10**9, row))


def scrub_geometry(value: Any) -> Any:
    if not isinstance(value, list):
        return value
    if value and value[0] in {"uuid", "tstamp"}:
        return None
    cleaned = [scrub_geometry(item) for item in value]
    return [item for item in cleaned if item is not None]


def footprint_form(path: Path, name: str) -> list[Any]:
    root = parse_sexpr(path)
    if not root or root[0] != "footprint" or len(root) < 2:
        raise ValidationError(f"{path}: not a KiCad footprint")
    if root[1] != name:
        raise ValidationError(f"{path}: footprint is {root[1]!r}, expected {name!r}")
    return root


def pad_rows(footprint: list[Any]) -> list[list[Any]]:
    return [scrub_geometry(pad) for pad in walk_forms(footprint, "pad")]


def signature(value: Any) -> str:
    canonical = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def number_set(rows: list[list[str]]) -> list[int]:
    return sorted({int(row[0]) for row in rows if row and str(row[0]).isdigit()})


def pad_numbers(pads: list[list[Any]]) -> list[int]:
    return sorted({int(pad[1]) for pad in pads if len(pad) > 1 and str(pad[1]).isdigit()})


def numbered_pad_count(pads: list[list[Any]]) -> int:
    return sum(1 for pad in pads if len(pad) > 1 and str(pad[1]).isdigit())


def actual_record(entry: dict[str, Any]) -> dict[str, Any]:
    symbol_spec = entry["symbol"]
    symbol_path = KICAD_ROOT / symbol_spec["path"]
    symbol = symbol_form(symbol_path, symbol_spec["name"])
    pins = pin_rows(symbol)

    inherited = symbol_spec.get("inherits")
    if inherited:
        extends = first_direct(symbol, "extends")
        if not extends or len(extends) < 2 or extends[1] != inherited["name"]:
            raise ValidationError(
                f"{entry['id']}: expected extends {inherited['name']!r}"
            )
        base_path = KICAD_ROOT / inherited["path"]
        pins = pin_rows(symbol_form(base_path, inherited["name"]))

    footprint_spec = entry["footprint"]
    footprint_path = KICAD_ROOT / footprint_spec["path"]
    footprint = footprint_form(footprint_path, footprint_spec["name"])
    pads = pad_rows(footprint)

    return {
        "id": entry["id"],
        "symbol_sha256": sha256(symbol_path),
        "pin_signature": signature(pins),
        "pin_numbers": number_set(pins),
        "symbol_properties": properties(symbol),
        "footprint_sha256": sha256(footprint_path),
        "pad_signature": signature(pads),
        "pad_numbers": pad_numbers(pads),
        "numbered_pad_count": numbered_pad_count(pads),
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_entry(entry: dict[str, Any], actual: dict[str, Any]) -> None:
    symbol_spec = entry["symbol"]
    footprint_spec = entry["footprint"]
    label = entry["id"]

    require(actual["symbol_sha256"] == symbol_spec["sha256"], f"{label}: symbol hash drift")
    require(actual["pin_signature"] == symbol_spec["pin_signature"], f"{label}: pin table drift")
    require(actual["pin_numbers"] == symbol_spec["pin_numbers"], f"{label}: pin-number set drift")
    require(actual["footprint_sha256"] == footprint_spec["sha256"], f"{label}: footprint hash drift")
    require(actual["pad_signature"] == footprint_spec["pad_signature"], f"{label}: pad geometry drift")
    require(actual["pad_numbers"] == footprint_spec["pad_numbers"], f"{label}: pad-number set drift")
    require(
        actual["numbered_pad_count"] == footprint_spec["numbered_pad_count"],
        f"{label}: numbered pad multiplicity drift",
    )

    props = actual["symbol_properties"]
    require(props.get("Value") == symbol_spec["value"], f"{label}: exact Value/MPN drift")
    require(
        props.get("Footprint") == f"Leshy2_Compute:{footprint_spec['name']}",
        f"{label}: symbol is not bound to the local exact footprint",
    )
    require(props.get("Datasheet") == symbol_spec["datasheet"], f"{label}: datasheet drift")

    if label == "C-002":
        target_path = KICAD_ROOT / symbol_spec["path"]
        rows = pin_rows(symbol_form(target_path, symbol_spec["name"]))
        pin19 = [row for row in rows if row[0] == "19"]
        require(
            pin19 == [["19", "NC_PSRAM_SPICS1", "no_connect"]],
            "C-002: N8R8 must not expose PSRAM SPICS1 as usable GPIO15",
        )
    if label == "C-005":
        target_path = KICAD_ROOT / symbol_spec["path"]
        rows = pin_rows(symbol_form(target_path, symbol_spec["name"]))
        grounds = {row[0]: row[1] for row in rows if row[0] in {"2", "4"}}
        require(grounds == {"2": "G", "4": "G"}, "C-005: crystal ground pins drift")


def validate_tables() -> None:
    sym_table = (KICAD_ROOT / "sym-lib-table").read_text(encoding="utf-8")
    fp_table = (KICAD_ROOT / "fp-lib-table").read_text(encoding="utf-8")
    require(
        "${KIPRJMOD}/lib/Leshy2_Compute.kicad_symdir" in sym_table,
        "sym-lib-table does not bind the repository-local directory library",
    )
    require(
        "${KIPRJMOD}/lib/Leshy2_Compute.pretty" in fp_table,
        "fp-lib-table does not bind the repository-local footprint library",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        action="store_true",
        help="print actual hashes/signatures without enforcing pinned values",
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = [actual_record(entry) for entry in manifest["artifacts"]]
    if args.report:
        print(json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    validate_tables()
    require((KICAD_ROOT / "third_party" / "KICAD-LIBRARY-LICENSE.md").is_file(), "license missing")
    require((KICAD_ROOT / "third_party" / "NOTICE.md").is_file(), "attribution notice missing")
    for entry, actual in zip(manifest["artifacts"], records, strict=True):
        validate_entry(entry, actual)
        print(
            f"PASS {entry['id']}: {entry['symbol']['name']} -> "
            f"{entry['footprint']['name']}"
        )
    print(f"PASS {len(records)} critical compute CAD rows")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
