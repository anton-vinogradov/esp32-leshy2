#!/usr/bin/env python3
"""Reproduce one CURRENT R2 polarity-only Keystone1048P footprint.

The manufacturer-authored Rev A TOP view has +/-, -/+ cell polarity.
Logical pads1/2/3/4 retain SLOT0_POS/NEG,SLOT1_POS/NEG. Only the physical
positions of3 and4 change. Undersized legacy lands, missing locator holes and
the approximate body reserve are deliberately NOT qualified by this patch.
Never writes historical R1, native PCB/SCH, net roles or approval artifacts.
"""

import argparse
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "hardware/ecad/libraries/Leshy2.pretty/Keystone-1048P.kicad_mod"
LEGACY_SHA256 = "dbcec95dcfe56d7d1e1bd2631640c065c30b064adc02f4f9810d4fc38ee02a9e"
NAME = "Keystone-1048P-POLARITY-CORRECTED"
OUTPUT = ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty" / (NAME + ".kicad_mod")
SOURCE_URL = "https://file.aichiplink.com/r/datasheets/keystoneelectronics-1048p-datasheets-1060.pdf"
SOURCE_SHA256 = "6135bff212f9eab9ed8158febcbbd0d18b9479caac384a7f51f2818d1328e26b"
SOURCE_SECTION = "Keystone Electronics exact1048P Rev A10.08.13, full one-page component TOP view; manufacturer-authored distributor-hosted copy"
MECHANICS_QUALIFIED = False
PRODUCTION_RELEASE_AUTHORIZED = False
DESCRIPTION = (
    "POLARITY ONLY; MECHANICS NOT QUALIFIED. Current R2 clone of the unqualified legacy Keystone1048P footprint. "
    "Manufacturer-authored1048P Rev A TOP view: upper row +/-, lower row -/+; logical1/2/3/4 remain SLOT0_POS/NEG,SLOT1_POS/NEG. "
    "Only positions3/4 exchanged. Approximate4x6-mm lands, absent locator holes and86x39.8-mm body reserve retained; "
    "not a manufacturing-ready land pattern or thermal-contact qualification. " + SOURCE_URL
)


def corrected_text(legacy_text: str) -> str:
    if hashlib.sha256(legacy_text.encode("utf-8")).hexdigest() != LEGACY_SHA256:
        raise ValueError("Legacy1048P geometry changed; review the bounded polarity-only derivation before regeneration")
    text = legacy_text.replace('(footprint "Keystone-1048P"', f'(footprint "{NAME}"', 1)
    text, count = re.subn(r'\(descr "[^"\n]*"\)', f'(descr "{DESCRIPTION}")', text)
    if count != 1:
        raise ValueError("Expected one legacy footprint description")
    for number, before, after in (("3", "-41.000", "41.000"), ("4", "41.000", "-41.000")):
        old = f'(pad "{number}" smd rect (at {before} 9.550)'
        new = f'(pad "{number}" smd rect (at {after} 9.550)'
        if text.count(old) != 1:
            raise ValueError(f"Expected one exact legacy pad{number}")
        text = text.replace(old, new, 1)
    return text


def build():
    return {OUTPUT: corrected_text(LEGACY.read_text(encoding="utf-8"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, text in build().items():
        if args.write:
            path.write_text(text, encoding="utf-8")
        elif not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"Stale current R2 polarity-only footprint: {path}")
    print("CURRENT R2 holder polarity: PASS scoped; mechanics NOT qualified; no PCB or R1 writes")


if __name__ == "__main__":
    main()
