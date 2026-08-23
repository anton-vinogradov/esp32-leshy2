#!/usr/bin/env python3
"""Regenerate or verify every currently implemented H2 derivative in order.

This is the single command used after the architecture/device registry changes.
It prevents source-hash fan-out from leaving otherwise unchanged KiCad sheets,
public diagrams, BOM reports or the optional sibling firmware contract stale.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
FIRMWARE_REPO = REPO.parent / "esp32-leshy2-firmware"

ARCHITECTURE_GENERATOR = "hardware/architecture/generate.py"
PRODUCT_GENERATOR = "hardware/product-design/g3_clamshell.py"
SCHEMATIC_LEDGER_GENERATOR = "hardware/ecad/h2_schematic.py"
ROOT_GENERATORS = (
    "hardware/ecad/h2_ui_root.py",
    "hardware/ecad/h2_rf_root.py",
)
IMPLEMENTED_CHILD_GENERATORS = (
    "hardware/ecad/h2_ui_s3_core.py",
    "hardware/ecad/h2_ui_display_touch_storage.py",
    "hardware/ecad/h2_ui_controls_indicators.py",
    "hardware/ecad/h2_ui_audio_codec_headset.py",
    "hardware/ecad/h2_ui_c5_radio_ir_service.py",
    "hardware/ecad/h2_ui_fm_am_receiver.py",
    "hardware/ecad/h2_ui_interboard_m1.py",
    "hardware/ecad/h2_ui_tx_safety_evidence.py",
    "hardware/ecad/h2_ui_testpoints_manufacturing.py",
    "hardware/ecad/h2_rf_usb_pd_charge.py",
    "hardware/ecad/h2_rf_pack_safety_aon.py",
    "hardware/ecad/h2_rf_main_rails_domain_gates.py",
    "hardware/ecad/h2_rf_rp2354_core_service.py",
    "hardware/ecad/h2_rf_nrf24_x3.py",
    "hardware/ecad/h2_rf_subghz_voice.py",
)


def run(repo: Path, relative: str, *arguments: str) -> None:
    command = [sys.executable, str(repo / relative), *arguments]
    print("+", " ".join(command))
    subprocess.run(command, cwd=repo, check=True)


def regenerate(sync_firmware: bool) -> None:
    run(REPO, ARCHITECTURE_GENERATOR, "--write")
    run(REPO, PRODUCT_GENERATOR, "--write")
    run(REPO, SCHEMATIC_LEDGER_GENERATOR, "--write")
    for generator in ROOT_GENERATORS:
        run(REPO, generator, "--write")
    for generator in IMPLEMENTED_CHILD_GENERATORS:
        run(REPO, generator, "--write")
    for generator in ROOT_GENERATORS:
        run(REPO, generator, "--write")
    run(REPO, ARCHITECTURE_GENERATOR, "--write")
    if sync_firmware:
        if not FIRMWARE_REPO.is_dir():
            raise FileNotFoundError(f"firmware sibling not found: {FIRMWARE_REPO}")
        run(FIRMWARE_REPO, "tools/import_hardware_contract.py", "--write")
        run(FIRMWARE_REPO, "tools/import_hardware_contract.py", "--check")


def verify(kicad_check: bool, sync_firmware: bool) -> None:
    run(REPO, ARCHITECTURE_GENERATOR, "--check")
    run(REPO, PRODUCT_GENERATOR, "--check")
    run(REPO, SCHEMATIC_LEDGER_GENERATOR, "--check")
    for generator in ROOT_GENERATORS:
        run(REPO, generator, "--check")
    for generator in IMPLEMENTED_CHILD_GENERATORS:
        run(REPO, generator, "--check")
    if kicad_check:
        for generator in ROOT_GENERATORS:
            run(REPO, generator, "--check", "--kicad-check")
    if sync_firmware:
        if not FIRMWARE_REPO.is_dir():
            raise FileNotFoundError(f"firmware sibling not found: {FIRMWARE_REPO}")
        run(FIRMWARE_REPO, "tools/import_hardware_contract.py", "--check")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument(
        "--kicad-check", action="store_true",
        help="run native KiCad ERC accounting once for each populated hierarchy",
    )
    parser.add_argument(
        "--sync-firmware", action="store_true",
        help="also import/check the generated contract in ../esp32-leshy2-firmware",
    )
    args = parser.parse_args()
    if args.kicad_check and not args.check:
        parser.error("--kicad-check requires --check")
    if args.write:
        regenerate(args.sync_firmware)
    else:
        verify(args.kicad_check, args.sync_firmware)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
