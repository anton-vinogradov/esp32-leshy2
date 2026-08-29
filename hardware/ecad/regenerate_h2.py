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
SYMBOL_LIBRARY_GENERATOR = "hardware/ecad/h2_symbol_library.py"
ROOT_GENERATORS = (
    "hardware/ecad/h2_ui_root.py",
    "hardware/ecad/h2_rf_root.py",
    "hardware/ecad/h2_lora_cap_root.py",
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
    "hardware/ecad/h2_rf_u214_m5_ext.py",
    "hardware/ecad/h2_rf_rear_controls.py",
    "hardware/ecad/h2_rf_audio_io_amp.py",
    "hardware/ecad/h2_rf_interboard_m1.py",
    "hardware/ecad/h2_rf_tx_safety_evidence.py",
    "hardware/ecad/h2_rf_testpoints_manufacturing.py",
    # h2_display_adapter.py is preserved R1 40-to-40 evidence.  The accepted
    # 40-to-50 EastRising adapter is H1 physical input only; its R2 H2 sheet is
    # intentionally not generated before H1 acceptance.
    "hardware/ecad/h2_lora_cap_radio_control.py",
    "hardware/ecad/h2_lora_cap_power_bus.py",
    "hardware/ecad/h2_lora_cap_tx_evidence.py",
)
REVIEW_GENERATORS = (
    "hardware/ecad/h2_review_power_paths.py",
    "hardware/ecad/h2_review_recovery_paths.py",
    "hardware/ecad/h2_review_no_back_power.py",
    "hardware/ecad/h2_review_quiet_state.py",
    "hardware/ecad/h2_review_fault_kill.py",
    "hardware/ecad/h2_review_safety_consolidated.py",
    "hardware/ecad/h2_review_erc_snapshot.py",
    "hardware/ecad/h2_review_no_connects.py",
    "hardware/ecad/h2_review_erc_clean.py",
    "hardware/ecad/h2_review_erc_consolidated.py",
    "hardware/ecad/h2_review_canonical_inventories.py",
    "hardware/ecad/h2_review_physical_contacts.py",
    "hardware/ecad/h2_review_named_nets_m1.py",
    "hardware/ecad/h2_review_firmware_contract.py",
    "hardware/ecad/h2_review_hwfw_consolidated.py",
    "hardware/ecad/h2_acceptance_package.py",
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
    run(REPO, SYMBOL_LIBRARY_GENERATOR, "--write")
    for generator in ROOT_GENERATORS:
        run(REPO, generator, "--write")
    run(REPO, ARCHITECTURE_GENERATOR, "--write")
    if sync_firmware:
        if not FIRMWARE_REPO.is_dir():
            raise FileNotFoundError(f"firmware sibling not found: {FIRMWARE_REPO}")
        run(FIRMWARE_REPO, "tools/import_hardware_contract.py", "--write")
        run(FIRMWARE_REPO, "tools/import_hardware_contract.py", "--check")
    for generator in REVIEW_GENERATORS:
        run(REPO, generator, "--write")
    if sync_firmware:
        run(FIRMWARE_REPO, "tools/import_hardware_contract.py", "--check")


def verify(kicad_check: bool, sync_firmware: bool) -> None:
    run(REPO, ARCHITECTURE_GENERATOR, "--check")
    run(REPO, PRODUCT_GENERATOR, "--check")
    run(REPO, SCHEMATIC_LEDGER_GENERATOR, "--check")
    for generator in ROOT_GENERATORS:
        run(REPO, generator, "--check")
    for generator in IMPLEMENTED_CHILD_GENERATORS:
        run(REPO, generator, "--check")
    run(REPO, SYMBOL_LIBRARY_GENERATOR, "--check")
    for generator in REVIEW_GENERATORS:
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
