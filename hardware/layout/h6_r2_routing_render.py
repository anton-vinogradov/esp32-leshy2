#!/usr/bin/env python3
"""Render and freshness-check the public H6 routing progress images."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
KICAD_CLI_CANDIDATES = (
    Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"),
    Path("/usr/bin/kicad-cli"),
    Path("/usr/local/bin/kicad-cli"),
)
LAYERS = "F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,Edge.Cuts"
BOARDS = {
    "ui": ROOT / "hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb",
    "rf": ROOT / "hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb",
}
OUTPUTS = {
    name: ROOT / f"docs/images/h6-r2-routing-{name}.svg"
    for name in BOARDS
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(name: str, board: Path) -> str:
    return (
        f'data-h6-board="{name}" '
        f'data-source-sha256="{sha256(board)}" '
        f'data-layers="{LAYERS}"'
    )


def render(name: str, board: Path, destination: Path) -> None:
    kicad_cli = next((path for path in KICAD_CLI_CANDIDATES if path.is_file()), None)
    if kicad_cli is None:
        raise SystemExit("KiCad CLI not found; cannot refresh H6 routing images")

    with tempfile.TemporaryDirectory(prefix="leshy2-h6-routing-render-") as directory:
        temporary = Path(directory) / f"{name}.svg"
        result = subprocess.run(
            [
                str(kicad_cli),
                "pcb",
                "export",
                "svg",
                "--output",
                str(temporary),
                "--layers",
                LAYERS,
                "--mode-single",
                "--page-size-mode",
                "2",
                "--fit-page-to-board",
                "--exclude-drawing-sheet",
                str(board),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode:
            raise SystemExit(result.stdout)
        svg = temporary.read_text(encoding="utf-8")

    if "<svg" not in svg:
        raise SystemExit(f"{name}: KiCad did not produce an SVG root")
    svg = svg.replace("<svg", f"<svg {metadata(name, board)}", 1)
    # KiCad embeds the export wall-clock time in <title>, which dirtied the
    # unchanged board image on every checkpoint refresh.  Make the title
    # source-derived so repeated renders are byte-for-byte reproducible.
    svg = re.sub(
        r"<title>SVG Image created as .*? date .*?</title>",
        f"<title>Leshy2 H6 routing · {name.upper()}</title>",
        svg,
        count=1,
    )
    # KiCad's SVG exporter leaves spaces at many line endings.  Normalize only
    # that presentation detail so generated documentation remains diff-clean.
    svg = "\n".join(line.rstrip() for line in svg.splitlines()) + "\n"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg, encoding="utf-8")


def check(name: str, board: Path, output: Path) -> list[str]:
    errors: list[str] = []
    if not output.is_file():
        return [f"{name}: missing {output.relative_to(ROOT)}"]
    svg = output.read_text(encoding="utf-8")
    expected = metadata(name, board)
    if expected not in svg:
        errors.append(f"{name}: routing image is stale for {board.relative_to(ROOT)}")
    if "<svg" not in svg or "</svg>" not in svg:
        errors.append(f"{name}: routing image is not a complete SVG")
    if f"<title>Leshy2 H6 routing · {name.upper()}</title>" not in svg:
        errors.append(f"{name}: routing image title is not deterministic")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.write:
        for name, board in BOARDS.items():
            render(name, board, OUTPUTS[name])

    errors = [
        error
        for name, board in BOARDS.items()
        for error in check(name, board, OUTPUTS[name])
    ]
    if errors:
        for error in errors:
            print("- " + error)
        return 1
    print("H6-R2 routing renders pass: 2 current board-linked SVG views")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
