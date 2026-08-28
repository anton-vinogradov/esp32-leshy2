#!/usr/bin/env python3
"""Freeze accepted H2 inputs and publish the complete H3 verification matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
VERIFICATION = REPO / "hardware/verification"
ECAD = REPO / "hardware/ecad"
OUTPUT = VERIFICATION / "generated/H3-VRF01-input-freeze.json"
DOC_EN = REPO / "docs/virtual-verification.md"
DOC_RU = REPO / "docs/virtual-verification.ru.md"

FIXED_INPUTS = (
    ECAD / "h2-schematic-plan.json",
    ECAD / "generated/H2-REV81-acceptance-package.json",
    ECAD / "generated/H2-REV56-safety-consolidated.json",
    ECAD / "generated/H2-REV64-erc-consolidated.json",
    ECAD / "generated/H2-REV75-hwfw-consolidated.json",
    ECAD / "generated/H2-hwfw-contract.json",
    ECAD / "generated/H2-instance-ledger.json",
    REPO / "hardware/product-design/generated/H1-physical-source-table.json",
    REPO / "hardware/product-design/generated/H1-unified-coordinate-table.json",
    REPO / "hardware/architecture/candidates/G2F-3I.json",
    REPO / "hardware/architecture/c5-procurement-invariant.json",
    REPO / "hardware/accessories/leshy2-lora-cap-01.json",
)

MATRIX = (
    ("H3.1", "steady_state_power", "analytic_envelope", "rail/source/load/charge margin tables", "H8 measured current and temperature"),
    ("H3.2", "power_transitions", "equation_and_circuit_simulation", "startup/shutdown/handover/brownout/load-step traces", "H8 oscilloscope traces"),
    ("H3.2", "safety_loop_dynamics", "timed_state_and_fault_injection", "watchdog/latch/FAULT_KILL timing evidence", "H8 injected-fault timing"),
    ("H3.3", "display_and_backlight", "worst_case_corner_analysis", "supply/current/timing/thermal margins", "H5 received-panel identity and H8 optical/current checks"),
    ("H3.3", "audio", "small_signal_power_and_corner_analysis", "gain/noise/clipping/load/thermal margins", "H8 acoustic and EMI measurements"),
    ("H3.3", "infrared", "pulse_current_threshold_and_thermal_analysis", "TX/RX/duty-cycle envelopes", "H8 range and temperature measurements"),
    ("H3.3", "battery_analog", "tolerance_and_threshold_analysis", "sense/thermistor/fault threshold margins", "H8 calibrated threshold tests"),
    ("H3.4", "digital_levels_and_defaults", "static_interface_proof", "levels/pulls/reset/no-back-power matrix", "H8 pin-state measurements"),
    ("H3.4", "digital_timing_and_bandwidth", "timing_and_occupancy_budget", "display/storage/audio/radio bus margins", "firmware F3 target/emulator traces and H8 logic-analyzer traces"),
    ("H3.4", "interboard_and_expansion", "loading_and_boundary_analysis", "M1/U214/M5/service loading margins", "H5 mating evidence and H8 signal-integrity measurements"),
    ("H3.5", "rf_feeds", "transmission_line_and_loss_budget", "50-ohm/matching/connector/loss constraints", "H6 field-solver/layout evidence and H8 VNA"),
    ("H3.5", "rf_returns_and_corridors", "prelayout_geometry_constraint_analysis", "keepouts/reference-plane/return-current rules", "H6 routed-board review"),
    ("H3.5", "rf_coexistence", "state_space_and_isolation_budget", "one-active-group and 3x-nRF24 concurrency constraints", "H8 coexistence and spectrum tests"),
    ("H3.6", "thermal", "lumped_worst_case_thermal_model", "board/battery/enclosure temperature bounds", "H8 thermocouple/thermal-camera validation"),
    ("H3.6", "single_fault_tree", "fault_tree_and_fmea", "independent shutdown and recovery coverage", "H8 safe fault injection"),
    ("H3.6", "unattended_operation", "bounded_energy_and_state_analysis", "extended-operation and configurable self-test policy without a runtime claim", "H8 24/48-hour qualified-USB endurance and battery-to-protected-cutoff measurements"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted_inputs() -> list[Path]:
    native = sorted((ECAD / "kicad").glob("**/*.kicad_sch"))
    projects = sorted((ECAD / "kicad").glob("**/*.kicad_pro"))
    paths = list(FIXED_INPUTS) + native + projects
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise ValueError("missing accepted input: " + ", ".join(str(path) for path in missing))
    return paths


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Историческая виртуальная электрическая проверка Leshy2 · R1"
        nav = "[English](virtual-verification.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Принятый H2](h2-acceptance.ru.md)"
        intro = "Этот H3 сохраняет воспроизводимые расчёты прежней одно-RP архитектуры R1. Он не доказывает текущую dual-RP R2; физические измерения также не подменяются."
        freeze_h = "## Принятый исходный материал"
        freeze = f"Ревизия H2 с независимыми SA818S-V/U принята 26 августа 2026 года и привязана к исходникам SHA-256. Заморожено {manifest['summary']['frozen_files']} файла; изменение любого из них повторно открывает затронутые проверки."
        matrix_h = "## Матрица проверки"
        headers = "| Этап | Область | Метод до изготовления | Артефакт H3 | Остаточная физическая проверка |\n|---|---|---|---|---|"
        current = "**Исторический маркер:** `H3.0.1-R1`. **Текущий аппаратный маркер:** `H1-R2.30`; R2 должна пройти собственный H2/H3. Закупка, PCB layout и fabrication не разрешены."
    else:
        title = "# Historical Leshy2 virtual electrical verification · R1"
        nav = "[Русский](virtual-verification.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Accepted H2](h2-acceptance.md)"
        intro = "This H3 retains reproducible analysis for the former single-RP R1 architecture. It does not prove current dual-RP R2, and physical measurements are not imitated."
        freeze_h = "## Accepted input"
        freeze = f"The H2 revision with independent SA818S-V/U paths was accepted on 26 August 2026 and is source-bound by SHA-256. {manifest['summary']['frozen_files']} files are frozen; changing any one reopens the affected verification."
        matrix_h = "## Verification matrix"
        headers = "| Stage | Area | Pre-fabrication method | H3 artifact | Residual physical check |\n|---|---|---|---|---|"
        current = "**Historical marker:** `H3.0.1-R1`. **Current hardware marker:** `H1-R2.30`; R2 must pass its own H2/H3. Purchasing, PCB layout and fabrication are not authorized."
    rows = "\n".join(
        f"| `{row['stage']}` | `{row['area']}` | {row['method']} | {row['h3_output']} | {row['physical_evidence']} |"
        for row in manifest["verification_matrix"]
    )
    evidence = "[Машинный freeze](../hardware/verification/generated/H3-VRF01-input-freeze.json)." if russian else "[Machine freeze](../hardware/verification/generated/H3-VRF01-input-freeze.json)."
    return "\n\n".join((title, nav, intro, freeze_h, freeze, matrix_h, headers + "\n" + rows, current, evidence)) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    h2_plan = json.loads((ECAD / "h2-schematic-plan.json").read_text(encoding="utf-8"))
    acceptance = json.loads((ECAD / "generated/H2-REV81-acceptance-package.json").read_text(encoding="utf-8"))
    if h2_plan.get("status") != "reviewed" or acceptance.get("decision", {}).get("status") != "accepted_by_user":
        raise ValueError("H2 is not accepted; H3 input freeze is forbidden")
    if (
        h2_plan.get("authority", {}).get("current_r2_authority") is not False
        or acceptance.get("authority", {}).get("allowed_as_r2_authority") is not False
    ):
        raise ValueError("historical H3 may consume only an explicitly non-R2 H2 boundary")
    paths = accepted_inputs()
    matrix = [
        {"stage": stage, "area": area, "method": method, "h3_output": output, "physical_evidence": physical}
        for stage, area, method, output, physical in MATRIX
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H3.0.1-R1",
        "status": "reviewed_accepted_h2_inputs_and_complete_verification_matrix_frozen",
        "authority": {"baseline": "R1", "lifecycle": "historical_single_rp_evidence", "allowed_as_r2_authority": False, "superseded_by": "hardware/architecture/h0-r2-rebaseline.json"},
        "accepted_baseline": {
            "date": "2026-08-26",
            "binding": "source_hashes",
            "superseded_architecture": "single SA518 voice path",
        },
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in paths},
        "verification_matrix": matrix,
        "summary": {
            "frozen_files": len(paths),
            "verification_domains": len(matrix),
            "unassigned_virtual_checks": 0,
            "unassigned_physical_checks": 0,
        },
        "open_findings": [],
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [path for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H3.0.1 input freeze is current; {manifest['summary']['frozen_files']} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
