#!/usr/bin/env python3
"""Build the controlled symbol library from populated H2 sheet symbols.

Each populated sheet embeds the exact symbols required to make the schematic
self-contained.  This helper mirrors those same definitions into the shared
``Leshy2`` library so KiCad can resolve every library identifier without one
sheet generator overwriting another sheet's symbols.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
PROJECT_DIR = ECAD / "kicad/LESHY2-UI"
OUTPUT = ECAD / "libraries/leshy2.kicad_sym"


def matching_paren(text: str, start: int) -> int:
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
    raise ValueError("unterminated KiCad S-expression")


def embedded_symbols(text: str) -> list[tuple[str, str]]:
    marker = text.find("\n\t(lib_symbols")
    if marker < 0:
        return []
    block_start = text.find("(", marker)
    block_end = matching_paren(text, block_start)
    block = text[block_start:block_end]
    result: list[tuple[str, str]] = []
    cursor = len("(lib_symbols")
    while True:
        match = re.search(r'\(symbol "Leshy2:([^"]+)"', block[cursor:])
        if not match:
            break
        start = cursor + match.start()
        end = matching_paren(block, start)
        name = match.group(1)
        definition = block[start:end].replace(
            f'(symbol "Leshy2:{name}"', f'(symbol "{name}"', 1
        )
        result.append((name, definition))
        cursor = end
    return result


def build(replacements: dict[Path, str] | None = None) -> str:
    replacements = replacements or {}
    paths = sorted(set(PROJECT_DIR.glob("UI_*.kicad_sch")) | set(replacements))
    definitions: dict[str, str] = {}
    for path in paths:
        if path in replacements:
            content = replacements[path]
        elif path.is_file():
            content = path.read_text(encoding="utf-8")
        else:
            continue
        for name, definition in embedded_symbols(content):
            if name in definitions and definitions[name] != definition:
                raise ValueError(f"conflicting generated symbol definition: {name}")
            definitions[name] = definition
    lines = [
        "(kicad_symbol_lib",
        "\t(version 20251024)",
        '\t(generator "leshy2-h2-symbol-library")',
        '\t(generator_version "1.0")',
    ]
    for name in sorted(definitions):
        lines.append("\n".join("\t" + line for line in definitions[name].splitlines()))
    lines += [")", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = build()
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(REPO)}")
        return 0
    if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
        print(f"stale: {OUTPUT.relative_to(REPO)}")
        return 1
    print("ok: controlled H2 symbol library is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
