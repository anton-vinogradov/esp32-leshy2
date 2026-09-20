"""Narrow RON table-domain screen. Never certifies a component or circuit.

The offline reviewed transcription is pinned. This is deliberately not a PDF
parser: a changed source needs a new human/source review, not auto-acceptance.
Only inclusive numeric domains are supported. No extrapolation from a test
point, typical-to-maximum promotion, or implied qualification of header biases.
"""

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re

from h6_power_corner_math import Interval, _decimal

ROWS_PATH = Path(__file__).with_name("h6-main-ron-sources.json")
REVIEWED_SHA256 = "ff38497a614855fecffc65429155fa7c8d45bdf4f6aec794838c8ea97482aa6d"
AXES = {"vin_v", "iout_a", "tj_c"}


def _interval(values):
    if not isinstance(values, list) or len(values) != 2 or any(not isinstance(v, str) for v in values):
        raise ValueError("two explicit inclusive bounds required")
    return Interval(*values)


def validate_row(row):
    if not isinstance(row, dict) or set(row) != {
            "id", "mpn", "parameter", "value", "unit", "bound_kind", "conditions",
            "unmodeled_header_conditions", "source"}:
        raise ValueError("unknown/missing RON row fields")
    if any(not isinstance(row[key], str) or not row[key].strip() for key in ("id", "mpn")):
        raise ValueError("explicit row and exact part identities required")
    if row["parameter"] != "RON" or row["bound_kind"] not in ("max", "typ", "min"):
        raise ValueError("unsupported RON parameter/column")
    if not isinstance(row["value"], str) or row["unit"] not in ("ohm", "mohm") or _decimal(row["value"], "RON") <= 0:
        raise ValueError("positive RON in ohm or mohm required")
    if not isinstance(row["conditions"], dict) or set(row["conditions"]) != AXES:
        raise ValueError("all VIN/IOUT/Tj source conditions required")
    domains = {key: _interval(value) for key, value in row["conditions"].items()}
    if domains["vin_v"].minimum <= 0 or domains["iout_a"].minimum < 0 or domains["tj_c"].minimum < _decimal("-273.15", "absolute zero"):
        raise ValueError("unphysical source conditions")
    headers = row["unmodeled_header_conditions"]
    if not isinstance(headers, list) or not headers or any(not isinstance(v, str) or not v.strip() for v in headers):
        raise ValueError("unmodeled table header conditions must remain explicit")
    primary = row["source"]
    if not isinstance(primary, dict) or set(primary) != {"url", "revision", "pdf_sha256", "page", "reviewed_on"}:
        raise ValueError("incomplete primary-source identity")
    if (not isinstance(primary["url"], str) or not primary["url"].startswith("https://www.ti.com/lit/")
            or not isinstance(primary["revision"], str) or not primary["revision"].strip()
            or not isinstance(primary["pdf_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", primary["pdf_sha256"])
            or type(primary["page"]) is not int or primary["page"] < 1
            or not isinstance(primary["reviewed_on"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", primary["reviewed_on"])):
        raise ValueError("invalid primary-source identity")
    return domains


def load_reviewed_rows():
    if ROWS_PATH.is_symlink() or not ROWS_PATH.is_file():
        raise ValueError("missing or symlinked RON source transcription")
    raw = ROWS_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != REVIEWED_SHA256:
        raise ValueError("RON source transcription changed; new review required")
    record = json.loads(raw)
    if set(record) != {"schema_version", "scope", "screening_tj_c", "temperature_basis", "rows"} or type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise ValueError("invalid reviewed source schema")
    _interval(record["screening_tj_c"])
    rows = record["rows"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("missing/duplicate reviewed rows")
    for row in rows:
        validate_row(row)
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("duplicate reviewed rows")
    return record


def evaluate_row(row, *, mpn, vin, tj, loads):
    domains = validate_row(row)
    if mpn != row["mpn"]:
        raise ValueError("exact MPN mismatch")
    if not isinstance(vin, Interval) or not isinstance(tj, Interval) or vin.minimum <= 0 or tj.minimum < _decimal("-273.15", "absolute zero"):
        raise ValueError("physical VIN/Tj application intervals required")
    if not isinstance(loads, list) or not loads:
        raise ValueError("nonempty named exact load cases required")
    names = set()
    for pair in loads:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError("named exact load case required")
        name, current = pair
        if not isinstance(name, str) or not name.strip() or name in names or not isinstance(current, F) or current < 0:
            raise ValueError("unique named nonnegative Fraction loads required")
        names.add(name)
    covered = lambda domain, low, high: F(domain.minimum) <= low <= high <= F(domain.maximum)
    missing = [axis for axis, actual in (("vin_v", vin), ("tj_c", tj))
               if not covered(domains[axis], F(actual.minimum), F(actual.maximum))]
    uncovered = [name for name, current in loads if not covered(domains["iout_a"], current, current)]
    if uncovered:
        missing.append("iout_a")
    maximum = row["bound_kind"] == "max"
    ron = _decimal(row["value"], "RON") / (1000 if row["unit"] == "mohm" else 1)
    return {"id": row["id"], "mpn": mpn, "qualified": False,
            "bound_kind": row["bound_kind"], "source_max_ohm": str(ron) if maximum else None,
            "numeric_domains_covered": maximum and not missing,
            "missing_source_domains": sorted(missing), "uncovered_load_cases": uncovered,
            "checked_load_cases": len(loads), "conditions": row["conditions"], "source": row["source"],
            "unmodeled_header_conditions": row["unmodeled_header_conditions"],
            "qualification_note": "Numeric coverage is not full header-bias, circuit, supply, thermal or physical qualification; no extrapolation from point tests"}


def assess_main(data):
    record = load_reviewed_rows()
    rail = data["rail"]
    # These are required voltage limits, not a claim that this unfinished rail
    # already meets them. Screening Tj is explicit, not copied from resistor Ta.
    vin = Interval(_decimal(str(rail["nominal_v"]), "nominal") * _decimal(str(data["policy"]["raw_regulated_voltage_minimum_fraction_of_nominal"]), "raw floor"),
                   str(rail["load_max_v"]))
    tj = _interval(record["screening_tj_c"])
    rows = record["rows"]
    if rows[0]["mpn"] != data["efuse_mpn"]:
        raise ValueError("reviewed fitted RON row no longer matches native MAIN eFuse")
    return {"qualified": False, "status": "source_scope_screen_only",
            "application": {"required_vin_v": [str(vin.minimum), str(vin.maximum)],
                            "screening_tj_c": record["screening_tj_c"], "temperature_basis": record["temperature_basis"],
                            "load_cases_a_exact": [[n, str(i)] for n, i in data["cases"]]},
            "rows": [evaluate_row(row, mpn=data["efuse_mpn"] if index == 0 else row["mpn"],
                                  vin=vin, tj=tj, loads=data["cases"]) for index, row in enumerate(rows)],
            "supply_checked": False, "replacement_adopted": False,
            "source_mode": "offline pinned reviewed transcription; no live freshness or automatic PDF interpretation"}
