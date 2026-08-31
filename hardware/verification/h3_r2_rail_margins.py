#!/usr/bin/env python3
"""Evaluate H3-R2.1.3 rail, protection and steady thermal margins."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "hardware/verification/h3-r2-rail-margin-contract.json"
LOADS = REPO / "hardware/verification/generated/H3-R2-load-binding.json"
STATES = REPO / "hardware/verification/generated/H3-R2-power-state-register.json"
METHODS = REPO / "hardware/verification/generated/H3-R2-method-contract.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-rail-margins.json"
DOC_EN = REPO / "docs/power-rail-margins.md"
DOC_RU = REPO / "docs/power-rail-margins.ru.md"


def d(value: object) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, quantum: str = "0.001") -> str:
    return format(value.quantize(d(quantum)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch_value(contract: dict, branch: str) -> Decimal:
    return d(contract["branch_currents_ma"][branch]["steady_worst"])


def instance_owner(line: dict) -> str:
    """Return exactly one numeric branch owner or the H3-R2.1.4 deferral."""
    rail = line["canonical_rails"][0]
    device = line["device_id"]
    instance = line["instance"]
    profiles = set(line["profiles"])

    if rail in {"SOURCE_OVERHEAD", "PACK_DIRECT"}:
        return "deferred_h3_r2_1_4"
    if rail == "AON_SAFE_3V3":
        return "aon_detector_one" if device == "adi_ad8314armz_reel" else "aon_common"
    if rail == "VVOICE_4V":
        return "voice_pa"
    if rail == "5V_EXT_ACTIVE_BRANCH":
        return "external_port_electrical"
    if rail != "3V3_MAIN":
        raise ValueError(f"unknown canonical rail for {line['instance_uid']}: {rail}")

    if device == "esp32_s3_wroom_1u_n16r8":
        return "s3_peak"
    if device == "esp32_c5_wroom_1u_n8r8":
        return "c5_peak"
    if device == "rp2354b_a4":
        return "hub_rp_peak" if "hub" in instance else "rf_rp_peak"
    if device in {"diodes_pam8302a_aycr", "everest_es8311_qfn20", "pui_as02404po", "same_sky_cmej_0413_42_smt_tr"}:
        return "audio_peak"
    if device == "ti_tps2553drvr_1" or profiles & {"DISPLAY", "DISPLAY_BACKLIGHT"}:
        return "display_peak"
    if "STORAGE" in profiles:
        return "storage_peak"
    if "NRF24" in profiles:
        return "nrf24_group"
    if "CC1101" in profiles:
        return "cc1101_group"
    if "IR" in profiles:
        return "ir_group"
    if "BROADCAST_RX_AIRBAND" in profiles:
        return "airband_chain"
    if "BROADCAST_RX" in profiles:
        return "broadcast_receiver"
    if "VOICE" in profiles:
        return "voice_main_aux"
    if "AUDIO" in profiles:
        return "audio_peak"
    return "main_common_peak"


def external_owner(line: dict) -> str:
    ident = line["id"]
    if ident == "EXT-DISPLAY":
        return "display_peak"
    if ident == "EXT-MICROSD":
        return "storage_peak"
    if ident in {"EXT-U214", "EXT-U219", "EXT-M5-UNIT"}:
        return "external_port_electrical"
    if ident == "EXT-CELLS":
        return "deferred_h3_r2_1_4"
    raise ValueError(f"unknown external line: {ident}")


def support_current(contract: dict, support: str) -> tuple[Decimal, list[dict]]:
    key = "support_idle" if support == "SUPPORT_IDLE" else "support_worst"
    rows = []
    total = d(0)
    for branch in contract["profile_rules"][key]:
        current = branch_value(contract, branch)
        rows.append({"branch": branch, "current_ma": q(current)})
        total += current
    return total, rows


def profile_load(contract: dict, profile: dict) -> dict:
    group = profile["signal_group"]
    mode = profile["group_mode"]
    support = profile["support_profile"]
    main, main_rows = support_current(contract, support)
    if support == "SUPPORT_IDLE":
        uplift = d(contract["profile_rules"]["idle_active_owner_uplift_ma"].get(group, 0))
        if uplift:
            main += uplift
            main_rows.append({"branch": f"{group.lower()}_active_owner_uplift", "current_ma": q(uplift)})

    branch = contract["profile_rules"]["signal_group_branch"].get(group)
    if group == "BROADCAST_RX":
        branch = "airband_chain" if mode == "AIRBAND_118_137_RX" else "broadcast_receiver"
    if branch:
        if group == "NRF24":
            current = {
                "3PRX": d(98),
                "1PTX_2PRX": d(198),
                "2PTX_1PRX": d(298),
                "3PTX": d(398),
            }[mode]
        else:
            current = branch_value(contract, branch)
        main += current
        main_rows.append({"branch": branch, "current_ma": q(current)})

    detector_count = int(contract["profile_rules"]["aon_enabled_detector_count"][group])
    aon = branch_value(contract, "aon_common") + d(detector_count) * branch_value(contract, "aon_detector_one")
    voice = d(0)
    if group == "VOICE":
        voice = d(750) if mode == "PTT_TX_MAX" else d(60)
    ext = d(1250) if group in {"LORA_CAP", "M5_UNIT"} else d(0)
    return {
        **profile,
        "branch_lines": {
            "AON_SAFE_3V3": [
                {"branch": "aon_common", "current_ma": q(branch_value(contract, "aon_common"))},
                {"branch": "aon_detector_one", "count": detector_count, "current_ma": q(d(detector_count) * branch_value(contract, "aon_detector_one"))},
            ],
            "3V3_MAIN": main_rows,
            "VVOICE_4V": [{"branch": "voice_pa", "current_ma": q(voice)}] if voice else [],
            "5V_EXT_ACTIVE_BRANCH": [{"branch": "external_port_electrical", "current_ma": q(ext)}] if ext else [],
        },
        "loads_ma": {
            "AON_SAFE_3V3": q(aon),
            "3V3_MAIN": q(main),
            "VVOICE_4V": q(voice),
            "5V_EXT_ACTIVE_BRANCH": q(ext),
        },
    }


def rail_voltage_result(name: str, rail: dict) -> dict:
    nominal = d(rail["nominal_v"])
    ripple = d(rail["ripple_pp_v"])
    raw_min = d(rail["raw_average_min_v"]) - ripple / d(2)
    raw_max = d(rail["raw_average_max_v"]) + ripple / d(2)
    endpoint_min = raw_min - d(rail["distribution_drop_v"])
    endpoint_max = raw_max
    raw_fraction = raw_min / nominal
    checks = {
        "raw_retains_95_percent_nominal": raw_fraction >= d("0.95"),
        "endpoint_above_load_minimum": endpoint_min >= d(rail["load_min_v"]),
        "endpoint_below_load_maximum": endpoint_max <= d(rail["load_max_v"]),
    }
    return {
        "rail": name,
        "nominal_v": q(nominal, "0.000001"),
        "raw_min_v": q(raw_min, "0.000001"),
        "raw_max_v": q(raw_max, "0.000001"),
        "endpoint_min_v": q(endpoint_min, "0.000001"),
        "endpoint_max_v": q(endpoint_max, "0.000001"),
        "raw_fraction_of_nominal_percent": q(raw_fraction * d(100)),
        "load_range_v": [q(d(rail["load_min_v"]), "0.000001"), q(d(rail["load_max_v"]), "0.000001")],
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
    }


def current_result(name: str, rail: dict, load_ma: Decimal, profile: dict) -> dict:
    effective = min(d(rail["converter_min_a"]), d(rail["protection_min_a"]))
    load_a = load_ma / d(1000)
    reserve = (effective / load_a - d(1)) * d(100) if load_a else d(9999)
    margin = (effective - load_a) * d(1000)
    pf03_boundary = effective / d("1.25")
    pf03_margin = (pf03_boundary - load_a) * d(1000)
    passed = not load_a or reserve >= d(25)
    return {
        "rail": name,
        "load_ma": q(load_ma),
        "profile": f"{profile['signal_group']}/{profile['group_mode']}/{profile['support_profile']}",
        "converter_min_a": q(d(rail["converter_min_a"])),
        "protection_min_a": q(d(rail["protection_min_a"])),
        "effective_hardware_min_a": q(effective),
        "margin_ma": q(margin),
        "pf03_25_percent_boundary_a": q(pf03_boundary),
        "margin_to_pf03_boundary_ma": q(pf03_margin),
        "reserve_percent": q(reserve),
        "status": "pass" if passed else "fail",
    }


def thermal_result(name: str, rail: dict, load_ma: Decimal, profile: dict, efficiency: Decimal, ambient: Decimal, margin_required: Decimal) -> dict:
    if name == "5V_EXT_ACTIVE_BRANCH" and load_ma:
        load_ma = min(load_ma, d(rail["sustained_thermal_admission_a"]) * d(1000))
    current_a = load_ma / d(1000)
    output_w = current_a * d(rail["nominal_v"])
    converter_loss = output_w * (d(1) / efficiency - d(1))
    efuse_loss = current_a * current_a * d(rail["efuse_ron_max_ohm"])
    converter_tj = ambient + converter_loss * d(rail["converter_theta_ja_k_per_w"])
    efuse_tj = ambient + efuse_loss * d(rail["efuse_theta_ja_k_per_w"])
    junction_max = d(125)
    converter_margin = junction_max - converter_tj
    efuse_margin = junction_max - efuse_tj
    passed = converter_margin >= margin_required and efuse_margin >= margin_required
    return {
        "rail": name,
        "sustained_load_ma": q(load_ma),
        "profile": f"{profile['signal_group']}/{profile['group_mode']}/{profile['support_profile']}",
        "ambient_c": q(ambient),
        "minimum_efficiency": q(efficiency),
        "output_w": q(output_w),
        "converter_loss_w": q(converter_loss),
        "efuse_loss_w": q(efuse_loss),
        "converter_predicted_tj_c": q(converter_tj),
        "converter_junction_margin_c": q(converter_margin),
        "efuse_predicted_tj_c": q(efuse_tj),
        "efuse_junction_margin_c": q(efuse_margin),
        "status": "pass" if passed else "fail",
    }


def render_doc(manifest: dict, russian: bool) -> str:
    current_rows = []
    for name, row in manifest["worst_current_by_rail"].items():
        current_rows.append(f"| `{name}` | {row['load_ma']} mA | {row['effective_hardware_min_a']} A | {row['reserve_percent']}% | `{row['profile']}` |")
    voltage_rows = []
    for name, row in manifest["voltage_corners"].items():
        voltage_rows.append(f"| `{name}` | {row['raw_min_v']}…{row['raw_max_v']} V | {row['endpoint_min_v']}…{row['endpoint_max_v']} V | {row['load_range_v'][0]}…{row['load_range_v'][1]} V | {row['status']} |")
    thermal_rows = []
    for name, row in manifest["steady_thermal_by_rail"].items():
        thermal_rows.append(f"| `{name}` | {row['sustained_load_ma']} mA | {row['converter_predicted_tj_c']} °C | {row['converter_junction_margin_c']} °C | {row['efuse_predicted_tj_c']} °C | {row['status']} |")

    if russian:
        title = "# Запасы шин питания · H3-R2.1.3"
        nav = "[English](power-rail-margins.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Привязка нагрузок](power-load-binding.ru.md)"
        intro = "`H3-R2.1.3` проведён ревью. Все 612 установленных потребителей и шесть внешних нагрузок имеют ровно одного владельца тока либо явный перенос source/pack-строки в H3-R2.1.4. Скрытой строки «прочее» нет."
        h1 = "## Ток и защита"
        t1 = "| Шина | Худшая электрическая нагрузка | Минимум железа | Запас | Профиль |\n|---|---:|---:|---:|---|\n" + "\n".join(current_rows)
        p1 = "Ограничивающий элемент 3V3_MAIN — нынешний 4-А `TPS564252DRLR`, а не исторический 6-А преобразователь. Худший угол оставляет 154 мА до границы правила 25%."
        h2 = "## Напряжение"
        t2 = "| Шина | Raw corner | На нагрузке | Допустимый диапазон нагрузки | Итог |\n|---|---:|---:|---:|---|\n" + "\n".join(voltage_rows)
        h3 = "## Установившийся тепловой режим"
        t3 = "| Шина | Длительный ток | Tj преобразователя | Запас до Tj max | Tj eFuse | Итог |\n|---|---:|---:|---:|---:|---|\n" + "\n".join(thermal_rows)
        p3 = "`SUPPORT_WORST` остаётся электрическим одновременным углом, а не разрешением на 24–48 часов. Для внешнего 5-В порта сохранён электрический потолок 1,25 А, но до H6/H8 длительная автоматика допускает 1,00 А; выбранные U214/U219/M5-сценарии функций не теряют."
        end = "**Downstream-результат:** [`H3-R2.1`](power-dc-source-result.ru.md) полностью проведён ревью; текущий маркер — `H3-R2.2.1`.\n\n[Полный машинный результат](../hardware/verification/generated/H3-R2-rail-margins.json)."
    else:
        title = "# Power-rail margins · H3-R2.1.3"
        nav = "[Русский](power-rail-margins.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Load binding](power-load-binding.md)"
        intro = "`H3-R2.1.3` is reviewed. All 612 fitted consumers and six external loads have exactly one current owner or an explicit source/pack deferral to H3-R2.1.4. There is no hidden miscellaneous line."
        h1 = "## Current and protection"
        t1 = "| Rail | Electrical worst load | Hardware minimum | Reserve | Profile |\n|---|---:|---:|---:|---|\n" + "\n".join(current_rows)
        p1 = "The limiting 3V3_MAIN element is the current 4-A `TPS564252DRLR`, not the historical 6-A converter. The worst corner retains 154 mA before the 25% rule boundary."
        h2 = "## Voltage"
        t2 = "| Rail | Raw corner | Load endpoint | Allowed load range | Result |\n|---|---:|---:|---:|---|\n" + "\n".join(voltage_rows)
        h3 = "## Steady thermal envelope"
        t3 = "| Rail | Sustained current | Converter Tj | Margin to Tj max | eFuse Tj | Result |\n|---|---:|---:|---:|---:|---|\n" + "\n".join(thermal_rows)
        p3 = "`SUPPORT_WORST` remains an electrical simultaneous corner, not a 24-to-48-hour permission. The exposed 5-V port keeps its 1.25-A electrical ceiling, while unattended control admits 1.00 A until H6/H8; the selected U214/U219/M5 functions are unaffected."
        end = "**Downstream result:** [`H3-R2.1`](power-dc-source-result.md) is fully reviewed; the current marker is `H3-R2.2.1`.\n\n[Complete machine result](../hardware/verification/generated/H3-R2-rail-margins.json)."
    return "\n\n".join((title, nav, intro, h1, t1, p1, h2, t2, h3, t3, p3, end)) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    loads = json.loads(LOADS.read_text(encoding="utf-8"))
    states = json.loads(STATES.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    if loads["status"] != "pass":
        raise ValueError("H3-R2.1.2 is not reviewed")
    required_rules = {"PF-R2-03", "PF-R2-04", "PF-R2-07", "PF-R2-11"}
    present_rules = {row["id"] for row in methods["pass_fail_rules"]}
    if not required_rules <= present_rules:
        raise ValueError("required H3-R2 method rules are missing")

    ownership = []
    owner_counts = Counter()
    owner_uids: dict[str, list[str]] = defaultdict(list)
    for line in loads["load_lines"]:
        owner = instance_owner(line)
        ownership.append({"line": line["id"], "instance_uid": line["instance_uid"], "owner": owner})
        owner_counts[owner] += 1
        owner_uids[owner].append(line["instance_uid"])
    for line in loads["external_load_lines"]:
        owner = external_owner(line)
        uid = f"EXTERNAL:{line['id']}"
        ownership.append({"line": line["id"], "instance_uid": uid, "owner": owner})
        owner_counts[owner] += 1
        owner_uids[owner].append(uid)
    if len(ownership) != loads["summary"]["power_connected_instances"] + loads["summary"]["external_load_lines"]:
        raise ValueError("ownership cardinality drift")

    profiles = [profile_load(contract, row) for row in states["operating_profiles"]]
    rails = contract["rails"]
    worst_current = {}
    voltage = {name: rail_voltage_result(name, rail) for name, rail in rails.items()}
    for name, rail in rails.items():
        load, profile = max(((d(row["loads_ma"][name]), row) for row in profiles), key=lambda pair: pair[0])
        worst_current[name] = current_result(name, rail, load, profile)

    sustained_profiles = [row for row in profiles if row["support_profile"] == "SUPPORT_IDLE"]
    thermal = {}
    efficiency = d(contract["thermal"]["minimum_efficiency"])
    ambient = d(contract["policy"]["ambient_design_c"])
    margin_required = d(contract["policy"]["junction_margin_below_maximum_c"])
    for name, rail in rails.items():
        load, profile = max(((d(row["loads_ma"][name]), row) for row in sustained_profiles), key=lambda pair: pair[0])
        thermal[name] = thermal_result(name, rail, load, profile, efficiency, ambient, margin_required)

    failures = [
        f"current:{name}" for name, row in worst_current.items() if row["status"] != "pass"
    ] + [
        f"voltage:{name}" for name, row in voltage.items() if row["status"] != "pass"
    ] + [
        f"thermal:{name}" for name, row in thermal.items() if row["status"] != "pass"
    ]
    if failures:
        raise ValueError("H3-R2.1.3 margin failures: " + ", ".join(failures))

    manifest = {
        "schema_version": 1,
        "artifact": "H3-R2-rail-margins",
        "marker": "H3-R2.1.3",
        "status": "reviewed_all_rail_voltage_current_protection_and_steady_thermal_margins",
        "accepted_input": {"marker": "H3-R2.1.2", "status": loads["status"]},
        "source_sha256": {str(path.relative_to(REPO)): sha256(path) for path in (CONTRACT, LOADS, STATES, METHODS)},
        "policy": contract["policy"],
        "branch_contract": contract["branch_currents_ma"],
        "ownership": ownership,
        "ownership_summary": {
            "physical_and_external_lines": len(ownership),
            "numeric_or_deferred_owner_lines": sum(owner_counts.values()),
            "owner_counts": dict(sorted(owner_counts.items())),
            "owner_instance_uids": {key: sorted(value) for key, value in sorted(owner_uids.items())},
            "hidden_miscellaneous_allowances": 0,
            "unowned_lines": 0,
        },
        "profiles": profiles,
        "worst_current_by_rail": worst_current,
        "voltage_corners": voltage,
        "steady_thermal_by_rail": thermal,
        "corrections": [
            {
                "id": "H3-R2.1.3-F01",
                "finding": "the historical R1 calculator still described 3V3_MAIN as a 6-A rail although R2 fits TPS564252DRLR",
                "correction": "R2 uses the exact 4.000-A converter minimum as the limiting hardware capability",
                "effect": "the worst 3.046-A electrical corner still passes PF-R2-03, but only with 154 mA to the 3.200-A 25%-reserve boundary",
                "bom_cost_effect": "0; evidence correction only"
            },
            {
                "id": "H3-R2.1.3-F02",
                "finding": "the 1.25-A exposed-port electrical ceiling was previously indistinguishable from a 24-to-48-hour thermal permission",
                "correction": "retain 1.25 A electrically and admit 1.00 A sustained at 35 C until H6/H8 closes the real layout/enclosure thermal path",
                "effect": "selected U214/U219/M5 functions remain available; unknown higher-current accessories are duty-limited rather than silently overheated",
                "bom_cost_effect": "0; safety admission only"
            }
        ],
        "summary": {
            "operating_profiles": len(profiles),
            "rail_profiles_evaluated": len(profiles) * len(rails),
            "physical_and_external_lines_owned": len(ownership),
            "deferred_source_pack_lines": owner_counts["deferred_h3_r2_1_4"],
            "hidden_miscellaneous_allowances": 0,
            "current_failures": 0,
            "voltage_failures": 0,
            "steady_thermal_failures": 0,
            "minimum_electrical_reserve_percent": min(d(row["reserve_percent"]) for row in worst_current.values() if d(row["load_ma"]) > 0).to_eng_string(),
            "minimum_junction_margin_c": min(min(d(row["converter_junction_margin_c"]), d(row["efuse_junction_margin_c"])) for row in thermal.values()).to_eng_string()
        },
        "physical_residuals": [
            "H6 must realize converter/eFuse copper and vias at least as good as the modeled published EVM/package boundary",
            "H8 must measure rail endpoints, current and temperature for each named sustained profile and reject any profile outside the generated envelope",
            "H8 may raise the 1.00-A sustained external admission only after measured 35-C margin remains at least 20 C"
        ],
        "authorization": {"analytical_verification": True, "placement_routing": False, "purchasing": False, "fabrication": False},
        "next": {"marker": "H3-R2.1.4", "action": "evaluate USB, pack, charge, supplement and source-admission margins"},
        "errors": []
    }
    outputs = {
        OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }
    return outputs, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H3-R2.1.3 artifacts: " + ", ".join(stale))
        print(f"ok: H3-R2.1.3; {manifest['summary']['rail_profiles_evaluated']} rail profiles, minimum reserve {manifest['summary']['minimum_electrical_reserve_percent']}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
