#!/usr/bin/env python3
"""Regenerate or check current H4-R2 joined-review evidence in order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ("hardware/verification/h4_r2_input_freeze.py",)


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
