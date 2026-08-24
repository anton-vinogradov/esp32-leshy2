#!/usr/bin/env python3
"""Regenerate or check all H3 virtual-verification artifacts in dependency order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = (
    ROOT / "hardware/verification/h3_input_freeze.py",
    ROOT / "hardware/verification/h3_parameter_inventory.py",
    ROOT / "hardware/verification/h3_method_contract.py",
    ROOT / "hardware/verification/h3_power_states.py",
    ROOT / "hardware/verification/h3_dc_budget.py",
    ROOT / "hardware/verification/h3_source_charge_budget.py",
    ROOT / "hardware/verification/h3_dc_consolidation.py",
    ROOT / "hardware/verification/h3_power_transitions.py",
    ROOT / "hardware/verification/h3_display_corners.py",
    ROOT / "hardware/verification/h3_audio_corners.py",
    ROOT / "hardware/verification/h3_ir_corners.py",
    ROOT / "hardware/verification/h3_battery_analog.py",
    ROOT / "hardware/verification/h3_analog_consolidation.py",
    ROOT / "hardware/verification/h3_digital_levels.py",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    flag = "--write" if args.write else "--check"
    for script in SCRIPTS:
        result = subprocess.run([sys.executable, str(script), flag], cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
