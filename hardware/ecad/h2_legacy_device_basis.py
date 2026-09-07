"""Immutable device input for the nineteen historical UI/RF sheet checks.

The output manifests already identify these sheets as R1, non-authoritative
for native R2. Their recorded devices.json SHA256 names the exact bytes from
commit b450e56d0688283a49843856e910db0145d2bba5. Keep those bytes available in
source archives without requiring Git history. They deliberately contain old
pin mappings and are NOT an approved production-part register.

Only legacy checkers import this module. Current R2 reads the live register.
The old source-path key in immutable manifests is retained as historical
provenance, not reinterpreted as the bytes at that path in today's checkout.
All other source hashes and generated-output comparisons remain live checks.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "hardware/architecture/devices.json"
SNAPSHOT = ROOT / "hardware/ecad/legacy-inputs/h2-r1-devices.json"
SOURCE_COMMIT = "b450e56d0688283a49843856e910db0145d2bba5"
SOURCE_SHA256 = "a11701b3df0156dbd533867d3e4bd0d57b731623c12b083cccf493b03775d0fa"
AUTHORITY = {
    "baseline": "R1",
    "lifecycle": "historical_pre_r2_sheet_scaffold",
    "allowed_as_r2_authority": False,
    "superseded_by": "hardware/architecture/h0-r2-rebaseline.json",
}


def snapshot_bytes(path: Path | None = None) -> bytes:
    data = (SNAPSHOT if path is None else path).read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError("historical H2 device input differs from its immutable SHA256")
    return data


def load_historical_devices() -> dict:
    return json.loads(snapshot_bytes())["devices"]


def source_sha256(path: Path) -> str:
    data = snapshot_bytes() if path.resolve() == SOURCE_PATH.resolve() else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def require_historical_check(parser, args) -> None:
    if args.write:
        parser.error("historical R1 sheets are immutable: use --check; edit native R2 sources for current hardware")


def verify_historical_scope(manifest: dict) -> None:
    if manifest.get("authority") != AUTHORITY:
        raise ValueError("historical device input cannot be used as current R2 authority")
    source_key = str(SOURCE_PATH.relative_to(ROOT))
    if manifest.get("source_hashes", {}).get(source_key) != source_sha256(SOURCE_PATH):
        raise ValueError("historical sheet has a different device input basis")
