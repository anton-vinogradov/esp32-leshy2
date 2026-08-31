#!/usr/bin/env python3
"""Regenerate or check the current H3-R2 evidence in dependency order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = (
    "hardware/verification/h3_r2_input_freeze.py",
    "hardware/verification/h3_r2_parameter_provenance.py",
    "hardware/verification/h3_r2_method_contract.py",
    "hardware/verification/h3_r2_power_states.py",
    "hardware/verification/h3_r2_load_binding.py",
    "hardware/verification/h3_r2_rail_margins.py",
    "hardware/verification/h3_r2_source_margins.py",
    "hardware/verification/h3_r2_dc_source_crosscheck.py",
    "hardware/verification/h3_r2_transition_sequences.py",
    "hardware/verification/h3_r2_handover.py",
    "hardware/verification/h3_r2_inrush_watchdog.py",
    # These three reviewed leaf calculations are inputs to the R2 analog
    # consolidation and must be refreshed after the device register changes.
    "hardware/verification/h3_audio_corners.py",
    "hardware/verification/h3_ir_corners.py",
    "hardware/verification/h3_battery_analog.py",
    "hardware/verification/h3_r2_airband_corners.py",
    "hardware/verification/h3_r2_analog_corners.py",
    "hardware/verification/h3_r2_digital_interfaces.py",
    "hardware/verification/h3_r2_rf_coexistence.py",
    "hardware/verification/h3_r2_thermal_fault.py",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    flag = "--write" if args.write else "--check"
    for relative in SCRIPTS:
        command = [sys.executable, str(ROOT / relative), flag]
        print("+", " ".join(command))
        subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
