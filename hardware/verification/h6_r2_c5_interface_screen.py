"""Source-conditioned static interface screen, not an analog circuit solver.

Ready EDG DigitalLink checks voltage/current/threshold compatibility once models
are supplied. The missing step here is admitting those models only within their
reviewed source conditions. Reuse existing exact interval validation; preserve
explicit assumptions and refuse to extrapolate the C5 3.3-V/25-C table.
"""

from fractions import Fraction as F
import copy
import hashlib
import json
from pathlib import Path

from hardware.verification.h6_power_corner_math import Interval
from hardware.verification import h6_r2_power_domain_crossings as crossings

ROOT = crossings.ROOT
SOURCES = Path(__file__).with_name("h6-c5-interface-sources.json")
RAILS = Path(__file__).with_name("h3-r2-rail-margin-contract.json")
REVIEWED_SHA256 = "3463219b5a093aa51ba624c871ba982bebab7e519fd346b225b30c1cbf4b6d1c"


def source_paths():
    return [Path(__file__), SOURCES, RAILS, Path(__file__).with_name("h6_power_corner_math.py")]


def require(condition, message):
    crossings.require(condition, message)


def interval(values):
    require(isinstance(values, list) and len(values) == 2 and all(type(v) is str for v in values),
            "explicit string interval required")
    return Interval(*values)


def covers(domain, actual):
    return domain.minimum <= actual.minimum <= actual.maximum <= domain.maximum


def load_review():
    require(SOURCES.is_file() and not SOURCES.is_symlink(), "reviewed interface source missing/symlinked")
    raw = SOURCES.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == REVIEWED_SHA256, "interface source transcription changed; new review required")
    data = json.loads(raw)
    require(data["schema_version"] == 1 and data["explicit_static_assumptions"] and data["unresolved"],
            "interface source scope missing")
    return data


def off_input_proofs(variant):
    """Pin evidence only; no current, loaded-voltage or sequencing qualification."""
    require(variant in {"main_schmitt", "aon_open_drain"}, "unknown interface recipe")
    if variant != "main_schmitt":
        return ()
    review = load_review()["buffer"]
    return ({"device_id": review["device_id"], "mpn": review["mpn"], "pads": ["2"],
             "supply_contacts": ["VCC"], "parameter": "powered_off_input_voltage_tolerance",
             "supply_v": review["powered_off_input_supply_v"], "input_v": review["input_voltage_v"],
             "source": {"path": str(SOURCES.relative_to(ROOT)), "sha256": REVIEWED_SHA256,
                        **{k: review["source"][k] for k in ("url", "revision", "selector", "reviewed_on")}}},)


def static_screen(*, buffer_v, receiver_v, temperature_c, total_static_load_ua="100"):
    record = load_review()
    b, r = record["buffer"], record["receiver"]
    bv, rv, temp = interval(buffer_v), interval(receiver_v), interval(temperature_c)
    load = interval([total_static_load_ua, total_static_load_ua]).maximum
    require(bv.minimum > 0 and rv.minimum > 0 and temp.minimum >= F("-273.15") and load >= 0,
            "invalid static screening stimulus")
    conditions = {
        "buffer_supply": covers(interval(b["operating_vcc_v"]), bv),
        "buffer_temperature": covers(interval(b["temperature_c"]), temp),
        "receiver_dc_supply": covers(interval(r["dc_table_vcc_v"]), rv),
        "receiver_dc_temperature": covers(interval(r["dc_table_temperature_c"]), temp),
        "conditional_static_load_budget": load <= F(b["output_test_current_ua"]),
        "receiver_known_input_current_within_budget": F(r["input_current_max_na"]) / 1000 <= load,
    }
    numerical = None
    if all(conditions.values()):
        # These are static source-table comparisons under the named premises,
        # never predicted transient or physically delivered voltages.
        high = F(bv.minimum) - F(b["voh_drop_max_v"]) - F(r["vih_factor"]) * F(rv.maximum)
        low = F(r["vil_factor"]) * F(rv.minimum) - F(b["vol_max_v"])
        upper = F(rv.minimum) + F(r["input_above_supply_v"]) - F(bv.maximum)
        lower = -F(r["input_below_ground_v"])
        numerical = {"high_margin_v_exact": str(high), "low_margin_v_exact": str(low),
                     "upper_voltage_margin_v_exact": str(upper),
                     "lower_voltage_margin_v_exact": str(lower),
                     "known_receiver_input_current_ua_exact": str(F(r["input_current_max_na"]) / 1000),
                     "voltage_and_logic_compatible_under_assumptions": min(high, low, upper, lower) >= 0}
    return {"status": "conditional_static_screen" if numerical is not None else "source_conditions_uncovered",
            "qualified": False, "delivered_rail_proven": False, "gpio_mode_proven": False,
            "stimulus": copy.deepcopy({"buffer_v": buffer_v, "receiver_v": receiver_v, "temperature_c": temperature_c,
                         "total_static_load_ua": total_static_load_ua}),
            "conditions": conditions, "numerical": numerical,
            "assumptions": list(record["explicit_static_assumptions"])}


def review_candidate(data, reviews, variant):
    record = load_review()
    if variant == "aon_open_drain":
        return {"status": "not_qualified", "qualified": False,
                "reason": "AON open-drain candidate still requires input-slew and powered-on output-leakage evidence"}
    require(variant == "main_schmitt", "unknown interface recipe")
    native, instances = crossings.indexes(data, reviews)
    project = "LESHY2-UI-R2"
    c5 = instances[project, "c5"]
    b, r = record["buffer"], record["receiver"]
    require(native[project, "c5"]["device_id"] == r["device_id"] and native[project, "c5"]["mpn"] == r["mpn"],
            "receiver exact identity differs")
    def contact(rows, name):
        values = [row for row in rows if row["contact"] == name]
        require(len(values) == 1, "interface contact absent/duplicate")
        return values[0]
    require(contact(c5, "3V3")["net"] == "3V3_MAIN", "receiver supply differs")
    channels = []
    for name, pad, input_net in (("GPIO23", "21", "EV_N1_C5"), ("GPIO24", "23", "EV_N7_IR")):
        sink = contact(c5, name)
        require(sink["pads"] == [pad] and sink["type"] in crossings.RECEIVERS, "receiver physical pin/type differs")
        peers = [row for rows in instances.values() for row in rows if row["project"] == project and row["net"] == sink["net"]]
        require(len(peers) == 2, "unexpected isolated output loads")
        drivers = [row for row in peers if row["type"] == "output"]
        require(len(drivers) == 1, "isolated interface needs one reviewed output")
        driver = drivers[0]
        require(driver["device_id"] == b["device_id"] and driver["mpn"] == b["mpn"]
                and driver["contact"] == "Y" and driver["pads"] == ["4"], "driver exact identity/pin differs")
        rows = instances[project, driver["instance"]]
        require(contact(rows, "A")["pads"] == ["2"] and contact(rows, "A")["net"] == input_net
                and contact(rows, "VCC")["net"] == "3V3_MAIN" and contact(rows, "GND")["net"] == "POWER_GROUND",
                "buffer channel or supply differs")
        channels.append({"receiver": name, "receiver_pad": pad, "driver_instance": driver["instance"],
                         "output_net": sink["net"], "only_expected_output_loads": len(peers) == 2,
                         "peer_endpoints": sorted(row["endpoint"] for row in peers)})
    rail = json.loads(RAILS.read_text())["rails"]["3V3_MAIN"]
    limits = [str(rail["load_min_v"]), str(rail["load_max_v"])]
    point = r["dc_table_vcc_v"]
    return {"status": "not_qualified", "qualified": False, "channels": channels,
            "off_input_source_evidence_available": True, "actual_off_pin_voltage_bounded": False,
            "gpio_mode_proven": False, "additional_output_loads_present": not all(c["only_expected_output_loads"] for c in channels),
            "source_mode": "Pinned offline transcription, not live PDF review; all table/applicability assumptions remain explicit",
            "declared_main_nominal_v": str(rail["nominal_v"]),
            "declared_voltage_module_temperature_envelope": static_screen(buffer_v=limits, receiver_v=limits,
                temperature_c=r["recommended_temperature_c"]),
            "datasheet_reference_point_not_current_nominal": static_screen(buffer_v=point, receiver_v=point,
                temperature_c=r["dc_table_temperature_c"]),
            "unresolved": list(record["unresolved"])}
