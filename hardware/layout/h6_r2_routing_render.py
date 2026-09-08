#!/usr/bin/env python3
"""Refresh/check routing images and the four-face component views together.

Only visualization artifacts are written. Component writes need pcbnew, so a
plain system-Python invocation delegates them to an available KiCad runtime.
Both freshness checks remain usable without importing pcbnew.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
KICAD_CLI_CANDIDATES = (
    Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"),
    Path("/usr/bin/kicad-cli"),
    Path("/usr/local/bin/kicad-cli"),
)
KICAD_PYTHON_CANDIDATES = (
    # Same bundled runtime used by the native placement and routing checks.
    Path("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3"),
    Path("/usr/bin/python3"),
    Path("/usr/local/bin/python3"),
)
COMPONENT_RENDER_SCRIPT = ROOT / "hardware/layout/h6_r2_component_render.py"
PRODUCT_RENDER_SCRIPT = ROOT / "hardware/layout/h6_r2_product_view.py"
INTENT_SCRIPT = ROOT / "hardware/layout/h6_r2_placement_intent.py"
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


def component_python() -> str:
    """Find an already installed pcbnew runtime; never install or alter one."""
    failures = []
    candidates = dict.fromkeys((Path(sys.executable), *KICAD_PYTHON_CANDIDATES))
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            result = subprocess.run(
                [str(candidate), "-c", "import pcbnew; assert hasattr(pcbnew, 'LoadBoard')"],
                cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            failures.append(f"{candidate}: {exc}")
            continue
        if result.returncode == 0:
            return str(candidate)
        failures.append(f"{candidate}: {(result.stdout or '').strip()}")
    details = "; ".join(failures) or "no candidate interpreter exists"
    raise RuntimeError(f"No installed Python with pcbnew; cannot refresh component views: {details}")


def component_views(mode: str, python: str | None = None) -> list[str]:
    """Delegate to the existing component writer/checker and preserve failures."""
    if mode not in {"--write", "--check"}:
        raise ValueError(f"unsupported component-view mode: {mode}")
    if python is None:
        python = component_python() if mode == "--write" else sys.executable
    try:
        result = subprocess.run(
            [str(python), str(COMPONENT_RENDER_SCRIPT), mode], cwd=ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
    except OSError as exc:
        return [f"component views {mode} could not run: {exc}"]
    if result.returncode:
        return [f"component views {mode} failed (exit {result.returncode}):\n{(result.stdout or '').strip()}"]
    return []


def product_view(mode: str) -> list[str]:
    if mode not in {"--write", "--check"}:
        raise ValueError(f"unsupported product-view mode: {mode}")
    try:
        result = subprocess.run([sys.executable, str(PRODUCT_RENDER_SCRIPT), mode],
                                cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as exc:
        return [f"product view {mode} could not run: {exc}"]
    return [] if result.returncode == 0 else [f"product view {mode} failed:\n{result.stdout}"]


def placement_intent(python: str) -> list[str]:
    try:
        result = subprocess.run([python, str(INTENT_SCRIPT), "--write"], cwd=ROOT,
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as exc:
        return [f"placement intent could not run: {exc}"]
    return [] if result.returncode == 0 else [f"placement intent failed:\n{result.stdout}"]


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.write:
        # Fail before writing either image group when pcbnew is unavailable.
        try:
            python = component_python()
        except RuntimeError as exc:
            print("- " + str(exc))
            return 1
        errors = placement_intent(python)
        if errors:
            print("\n".join(errors))
            return 1
        for name, board in BOARDS.items():
            render(name, board, OUTPUTS[name])
        errors = component_views("--write", python)
        if errors:
            for error in errors:
                print("- " + error)
            return 1
        errors = product_view("--write")
        if errors:
            for error in errors:
                print("- " + error)
            return 1

    errors = [
        error
        for name, board in BOARDS.items()
        for error in check(name, board, OUTPUTS[name])
    ]
    errors.extend(component_views("--check"))
    errors.extend(product_view("--check"))
    if errors:
        for error in errors:
            print("- " + error)
        return 1
    print("H6-R2 routing renders pass: 2 routing SVGs + 4 component faces and overview are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
