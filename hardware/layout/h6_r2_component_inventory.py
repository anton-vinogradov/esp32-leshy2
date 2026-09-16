"""Read-only two-board completeness gate against the independent H2 inventory.

No PCB is an expected-inventory source. Pad geometry remains the responsibility
of h6_r2_footprint_parity; repeated pad numbers are not component duplicates.
"""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
from uuid import UUID

from hardware.ecad import h2_r2_instance_ledger as instances
from hardware.ecad import h2_r2_native_inventory as inventory
from hardware.ecad import h2_r2_symbol_footprint_ledger as definitions
from hardware.ecad.h2_r2_native_kicad import stable_uuid
from hardware.layout.h6_r2_footprint_parity import PROJECTS


ROOT = Path(__file__).resolve().parents[2]
PLACEMENT = ROOT / "hardware/layout/h6-r2-placement-contract.json"
FIELDS = ("footprint", "value", "device_id", "instance", "schematic_path",
          "board_only", "bom_excluded", "position_excluded", "dnp")
BOOLEAN_FIELDS = ("board_only", "bom_excluded", "position_excluded", "dnp")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity_hash(rows):
    ordered = sorted(rows, key=lambda r: (r["project"], r["reference"]))
    return hashlib.sha256(json.dumps(ordered, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def expected_inventory():
    """Rebuild the existing acyclic source chain, rejecting stale ledgers."""
    sources, rebuilt = {}, {}
    for name, module in (("inventory", inventory), ("definitions", definitions),
                         ("instances", instances)):
        current = module.build()
        if current.get("status") != "pass" or current.get("errors"):
            raise ValueError(f"Independent H2 {name} source validation failed")
        if current != json.loads(module.OUTPUT.read_text()):
            raise ValueError(f"Independent H2 {name} ledger is stale")
        rebuilt[name] = current
        for path in (module.CONTRACT, module.OUTPUT, Path(module.__file__)):
            sources[str(path.relative_to(ROOT))] = sha(path)
        for source in (list(current.get("sources", {}).values())
                       + current.get("historical_hint_sources", [])):
            sources[source["path"]] = source["sha256"]
    # Printed schematic features can also carry the native board_only flag.
    # Derive this from the independently validated controlled library, never
    # from a candidate PCB (notably L32's required NFC pickup-loop footprint).
    board_only = {}
    for row in rebuilt["definitions"]["groups"]:
        definition = row.get("footprint_definition") or {}
        if definition.get("path"):
            path = ROOT / definition["path"]
            sources[definition["path"]] = definition["sha256"]
            attrs = re.findall(r"^\s*\(attr\s+([^()]*)\)\s*$", path.read_text(), re.M)
            if len(attrs) > 1:
                raise ValueError("Controlled footprint has ambiguous attributes")
            board_only[row["device_id"]] = bool(attrs and "board_only" in attrs[0].split())
    expected = []
    for row in rebuilt["instances"]["rows"]:
        project, sheet, instance = row["project"], row["sheet"], row["instance"]
        hierarchy = stable_uuid(f"hierarchy:{project}:{sheet}")
        symbol = stable_uuid(f"symbol:{project}:{sheet}:{instance}")
        # BOM-excluded printed features and DNP instances still need footprints.
        expected.append({"project": project, "reference": row["reference"],
                         "footprint": row["footprint"], "value": row["mpn"],
                         "device_id": row["device_id"], "instance": instance,
                         "schematic_path": f"/{hierarchy}/{symbol}",
                         "board_only": board_only.get(row["device_id"], False),
                         "bom_excluded": bool(row["bom_excluded"]),
                         "position_excluded": bool(row["bom_excluded"]),
                         "dnp": bool(row.get("dnp", False))})
    contract = json.loads(PLACEMENT.read_text())
    holes = contract["mechanical"]["mounting_holes"]
    if holes["diameter_mm"] != 2.7 or len(holes["centres_mm"]) != 4:
        raise ValueError("Mechanical exemption no longer matches the controlled M2.5 holes")
    # Exact board-only features created by add_mechanical_geometry(), not a
    # prefix-based exemption that would hide unexpected MH/TP components.
    for project in PROJECTS:
        for number in range(1, len(holes["centres_mm"]) + 1):
            expected.append({"project": project, "reference": f"MH{number}",
                             "footprint": "MountingHole:MountingHole_2.7mm_M2.5",
                             "value": "M2.5 compression-stop axis", "device_id": "",
                             "instance": "", "schematic_path": "", "board_only": True,
                             "bom_excluded": True, "position_excluded": True, "dnp": False})
    for path in (PLACEMENT, ROOT / "hardware/layout/h6_r2_placement.py",
                 ROOT / "hardware/ecad/h2_r2_native_kicad.py"):
        sources[str(path.relative_to(ROOT))] = sha(path)
    exemptions = [{"device_id": row["device_id"], "quantity": row["quantity_per_product"],
                   "disposition": row["ecad_disposition"]}
                  for row in rebuilt["inventory"]["component_groups"]
                  if row["ecad_disposition"] != "schematic_component_group"]
    return expected, dict(sorted(sources.items())), exemptions


def compare_inventory(expected, observed):
    """Compare whole footprint records; never collapse duplicate references."""
    def index(rows, label):
        if not isinstance(rows, list):
            raise ValueError(label + " inventory must be a list")
        grouped = defaultdict(list)
        for row in rows:
            if (not isinstance(row, dict) or any(not isinstance(row.get(k), str)
                    or not row[k] for k in ("project", "reference"))
                    or any(type(row.get(k)) is not bool for k in BOOLEAN_FIELDS)
                    or any(not isinstance(row.get(k), str)
                           for k in FIELDS if k not in BOOLEAN_FIELDS)):
                raise ValueError("Malformed " + label + " component identity")
            grouped[row["project"], row["reference"]].append(row)
        return grouped

    want, got = index(expected, "expected"), index(observed, "native")
    if not expected or {r["project"] for r in expected} != set(PROJECTS):
        raise ValueError("Independent source must cover both assigned boards")
    if any(len(rows) != 1 for rows in want.values()):
        raise ValueError("Independent source has duplicate project/reference identities")
    findings = []
    for project, ref in sorted(want.keys() | got.keys()):
        key = (project, ref)
        entry = {"project": project, "reference": ref}
        if key not in got:
            findings.append(dict(entry, type="missing_component"))
            continue
        if len(got[key]) != 1:
            findings.append(dict(entry, type="duplicate_reference", count=len(got[key])))
        if key not in want:
            findings.append(dict(entry, type="unexpected_component"))
            continue
        for row in got[key]:
            changes = {field: {"expected": want[key][0][field], "actual": row[field]}
                       for field in FIELDS if row[field] != want[key][0][field]}
            if changes:
                findings.append(dict(entry, type="component_identity_mismatch", fields=changes))
    native_uuids, paths = defaultdict(list), defaultdict(list)
    for row in observed:
        owner = [row["project"], row["reference"]]
        uid = row.get("uuid")
        try:
            if not isinstance(uid, str) or str(UUID(uid)) != uid or UUID(uid).int == 0:
                raise ValueError()
        except (ValueError, AttributeError):
            findings.append({"type": "invalid_native_uuid", "component": owner})
        else:
            native_uuids[uid].append(owner)
        if row["schematic_path"]:
            paths[row["schematic_path"]].append(owner)
    for kind, groups in (("duplicate_native_uuid", native_uuids),
                         ("duplicate_schematic_identity", paths)):
        for identity, owners in sorted(groups.items()):
            if len(owners) > 1:
                findings.append({"type": kind, "identity": identity, "components": owners})
    projects = sorted({r["project"] for r in expected} | {r["project"] for r in observed})
    return {"status": "pass" if not findings else "fail", "findings": findings,
            "summary": {"expected_footprints": len(expected), "native_footprints": len(observed),
                        "schematic_components": sum(bool(r["schematic_path"]) for r in expected),
                        "mechanical_features": sum(not r["schematic_path"] for r in expected),
                        "finding_count": len(findings)},
            "boards": [{"project": p, "expected": sum(r["project"] == p for r in expected),
                        "observed": sum(r["project"] == p for r in observed)} for p in projects]}


def native_inventory(board_paths):
    """Load both boards read-only, retaining duplicate footprint references."""
    import pcbnew
    if set(board_paths) != set(PROJECTS):
        raise ValueError("Both assigned product boards are required")
    rows, board_hashes = [], {}
    for project in PROJECTS:
        path = Path(board_paths[project])
        before = path.read_bytes()
        board = pcbnew.LoadBoard(str(path))
        if not isinstance(board, pcbnew.BOARD):
            raise ValueError(f"Unable to load native PCB for component inventory: {path}")
        for fp in board.GetFootprints():
            nickname = str(fp.GetFPID().GetLibNickname())
            name = str(fp.GetFPID().GetLibItemName())
            ref = fp.GetReference()
            if not nickname and ref in {"MH1", "MH2", "MH3", "MH4"} and name == "MountingHole_2.7mm_M2.5":
                nickname = "MountingHole"
            def field(key):
                value = fp.GetField(key)
                return value.GetText() if value else ""
            attrs = fp.GetAttributes()
            rows.append({"project": project, "reference": ref, "uuid": fp.m_Uuid.AsString(),
                         "footprint": f"{nickname}:{name}", "value": fp.GetValue(),
                         "device_id": field("Description"), "instance": field("Leshy2Instance"),
                         "schematic_path": fp.GetPath().AsString(),
                         "board_only": bool(attrs & pcbnew.FP_BOARD_ONLY),
                         "bom_excluded": bool(attrs & pcbnew.FP_EXCLUDE_FROM_BOM),
                         "position_excluded": bool(attrs & pcbnew.FP_EXCLUDE_FROM_POS_FILES),
                         "dnp": bool(attrs & pcbnew.FP_DNP)})
            # SWIG child proxies must be released while their board still
            # exists, including the last footprint captured by field().
            del field, fp
        if path.read_bytes() != before:
            raise ValueError("PCB changed during read-only inventory inspection")
        board_hashes[project] = hashlib.sha256(before).hexdigest()
    return rows, board_hashes


def build(board_paths=None):
    """Integration API: explicit candidate paths or the two production PCBs.

    Raises on stale/invalid authority sources; status=fail lists PCB findings.
    Does not write an audit, alter a PCB, invoke kicad-cli, or run DRC.
    """
    expected, sources, exemptions = expected_inventory()
    paths = board_paths if board_paths is not None else {
        p: ROOT / f"hardware/ecad/kicad/{p}/{p}.kicad_pcb" for p in PROJECTS}
    observed, board_hashes = native_inventory(paths)
    result = compare_inventory(expected, observed)
    if any(sha(ROOT / name) != digest for name, digest in sources.items()):
        raise ValueError("Authority source changed during inventory inspection")
    if any(sha(paths[project]) != digest for project, digest in board_hashes.items()):
        raise ValueError("PCB changed during two-board inventory inspection")
    return {"schema_version": 1, "artifact": "H6-R2 independent component completeness",
            **result, "source_sha256": sources, "board_sha256": board_hashes,
            "expected_inventory_sha256": identity_hash(expected),
            "observed_inventory_sha256": identity_hash(observed),
            "non_pcb_dispositions": exemptions, "dnp_footprint_omission_allowed": False,
            "read_only": True, "drc_checked": False, "fabrication_ready": False,
            "scope": "Exact assigned PCB/reference, schematic UUID path, footprint, MPN/value, device/instance identity and assembly flags; unique native UUIDs. Mechanical holes are explicit required features; non-PCB groups are excluded only by the H2 source contract. Pad/body geometry and electrical qualification are separate gates."}
