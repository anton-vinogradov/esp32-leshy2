#!/usr/bin/env python3
"""Close H3-R2.5 RF feeds, quiet states and three-nRF concurrency on R2."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34
ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "hardware/architecture/candidates/G2F-3I.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
ANTENNAS = ROOT / "hardware/architecture/antenna-kit.json"
PLACEMENT = ROOT / "hardware/product-design/generated/H1-R2-placement-audit.json"
POWER = ROOT / "hardware/verification/generated/H3-R2-power-state-register.json"
DIGITAL = ROOT / "hardware/verification/generated/H3-R2-digital-interfaces.json"
ANALOG = ROOT / "hardware/verification/generated/H3-R2-analog-corners.json"
PROVENANCE = ROOT / "hardware/verification/generated/H3-R2-parameter-provenance.json"
OUTPUT = ROOT / "hardware/verification/generated/H3-R2-rf-coexistence.json"
DOC_EN = ROOT / "docs/rf-electrical-verification.md"
DOC_RU = ROOT / "docs/rf-electrical-verification.ru.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> float:
    return float(value.quantize(Decimal(places)))


def build() -> tuple[dict[Path, str], dict]:
    candidate = load(CANDIDATE)
    devices = load(DEVICES)["devices"]
    antennas = load(ANTENNAS)
    placement = load(PLACEMENT)
    power = load(POWER)
    digital = load(DIGITAL)
    analog = load(ANALOG)
    provenance = load(PROVENANCE)

    instances = candidate["instances"]
    fixed_routes = {
        (row["from"], row["to"], row["net"])
        for row in candidate["fixed_routes"]
    }
    path_ids = set(candidate["antenna_policy"]["base_onboard_sma_paths"])
    expected_paths = {
        "S3-2G4", "C5-2G4/5", "N24-0", "N24-1", "N24-2",
        "CC-SUB", "VOICE-VHF", "VOICE-UHF", "RX-FM/SW", "RX-AM/LW",
    }

    exact_instances = {
        "s3_rf_jumper": "te_2118651_2",
        "c5_rf_jumper": "te_2118651_2",
        "nrf0_rf_jumper": "te_1_2118651_0",
        "nrf1_rf_jumper": "te_1_2118651_0",
        "nrf2_rf_jumper": "te_1_2118651_0",
        "s3_rf_board_connector": "hirose_ufl_r_smt_1_10",
        "c5_rf_board_connector": "hirose_ufl_r_smt_1_10",
        "nrf0_rf_board_connector": "hirose_ufl_r_smt_1_10",
        "nrf1_rf_board_connector": "hirose_ufl_r_smt_1_10",
        "nrf2_rf_board_connector": "hirose_ufl_r_smt_1_10",
        "s3_rf_coupler": "kyocera_avx_cp0603q5425entr",
        "c5_rf_coupler": "kyocera_avx_cp0603q5425entr",
        "nrf0_coupler": "ttm_dc2337j5010ahf",
        "nrf1_coupler": "ttm_dc2337j5010ahf",
        "nrf2_coupler": "ttm_dc2337j5010ahf",
        "cc_balun": "ttm_b0310j50100ahf",
        "cc_switch_a": "infineon_bgs13sn8e6327xtsa1",
        "cc_switch_b": "infineon_bgs13sn8e6327xtsa1",
        "voice": "nicerf_sa818s_u_v18",
        "voice_v": "nicerf_sa818s_v_v18",
        "receiver": "skyworks_si4732_a10_gsr",
    }
    exact_checks = {
        f"exact_{name}": instances.get(name) == device_id
        for name, device_id in exact_instances.items()
    }

    required_routes = {
        "s3_module_to_jumper": ("s3.ANT", "s3_rf_jumper.END_A", "S3_MODULE_RF_50R"),
        "s3_jumper_to_board": ("s3_rf_jumper.END_B", "s3_rf_board_connector.CENTER", "S3_MODULE_RF_50R"),
        "s3_coupler_to_sma": ("s3_rf_coupler.RF_OUT", "s3_external_rp_sma.RF", "S3_EXTERNAL_RF_50R"),
        "c5_module_to_jumper": ("c5.ANT1", "c5_rf_jumper.END_A", "C5_MODULE_RF_50R"),
        "c5_jumper_to_board": ("c5_rf_jumper.END_B", "c5_rf_board_connector.CENTER", "C5_MODULE_RF_50R"),
        "c5_coupler_to_sma": ("c5_rf_coupler.RF_OUT", "c5_external_rp_sma.RF", "C5_EXTERNAL_RF_50R"),
        "cc_to_balun_p": ("cc.RF_P", "cc_rf_p_dc_block.END_1", "CC_RF_P"),
        "cc_to_balun_n": ("cc.RF_N", "cc_rf_n_dc_block.END_1", "CC_RF_N"),
        "cc_selected_to_sma": ("cc_output_l2n2.END_2", "cc_external_sma.RF", "CC_EXTERNAL_RF_50R"),
        "voice_u_to_sma": ("voice.ANT", "voice_external_sma.RF", "VOICE_U_EXTERNAL_RF_50R"),
        "voice_v_to_sma": ("voice_v.ANT", "voice_v_external_sma.RF", "VOICE_V_EXTERNAL_RF_50R"),
        "fm_sw_to_match": ("receiver_fmsw_external_sma.RF", "receiver_fmi_match_inductor.END_1", "RX_FMSW_PROTECTED_RF"),
        "am_lw_to_coupling": ("receiver_amlw_external_sma.RF", "receiver_ami_coupling_cap.END_1", "RX_AMLW_PROTECTED_RF"),
    }
    for index in range(3):
        required_routes[f"nrf{index}_module_to_jumper"] = (
            f"nrf{index}.ANT", f"nrf{index}_rf_jumper.END_A", f"NRF{index}_MODULE_RF_50R"
        )
        required_routes[f"nrf{index}_jumper_to_board"] = (
            f"nrf{index}_rf_jumper.END_B", f"nrf{index}_rf_board_connector.CENTER", f"NRF{index}_MODULE_RF_50R"
        )
        required_routes[f"nrf{index}_coupler_to_sma"] = (
            f"nrf{index}_coupler.RF_OUT", f"nrf{index}_external_sma.RF", f"NRF{index}_EXTERNAL_RF_50R"
        )
    route_checks = {
        f"route_{name}": route in fixed_routes
        for name, route in required_routes.items()
    }

    topology = placement["antenna_topology"]
    microcoax = placement["rf_microcoax"]
    pcb_segments = topology["pcb_segments"]
    topology_path_ids = {row["path"] for row in pcb_segments}
    front_path_ids = {row["path"] for row in pcb_segments if row["frame"] == "ui-inner"}
    rear_path_ids = {row["path"] for row in pcb_segments if row["frame"] == "rf-inner"}
    expected_front = {"N24-0", "S3-2G4", "N24-1", "C5-2G4/5", "N24-2"}
    expected_rear = {"VOICE-VHF", "VOICE-UHF", "CC-SUB", "RX-AM/LW", "RX-FM/SW"}
    airband_segments = [
        row for row in pcb_segments
        if row["path"] == "RX-FM/SW" and row["branch"] == "converted-airband"
    ]

    ufl = devices["hirose_ufl_r_smt_1_10"]["electrical_contract"]
    jumper_30 = devices["te_2118651_2"]["electrical_contract"]
    jumper_60 = devices["te_1_2118651_0"]["electrical_contract"]
    native_coupler = devices["kyocera_avx_cp0603q5425entr"]["electrical_contract"]
    nrf_coupler = devices["ttm_dc2337j5010ahf"]["electrical_contract"]
    cc_balun = devices["ttm_b0310j50100ahf"]["electrical_contract"]
    cc_switch = devices["infineon_bgs13sn8e6327xtsa1"]["electrical_contract"]
    voice_esd = devices["nexperia_pesd24vy1bsf"]["electrical_contract"]
    receiver_esd = devices["littelfuse_sesd0402x1un_0020_090"]["electrical_contract"]

    c5_top_ghz = d("5.885")
    connector_margin_ghz = d("6") - c5_top_ghz
    nrf_loss_db = max(
        d(nrf_coupler["mainline_insertion_loss_db_max_2400_2500"]),
        d(nrf_coupler["mainline_insertion_loss_db_max_2500_3300"]),
    )
    cc_known_loss_db = d(cc_balun["insertion_loss_db_max"]) + d(2) * d(
        cc_switch["insertion_loss_db_698_to_960_typ_max"][1]
    )
    normalized_shunt = (
        d(2) * d(str(math.pi)) * d(480_000_000)
        * d(voice_esd["typical_capacitance_pf"]) * d("1e-12") * d(50)
    )
    voice_ideal_loss_db = -d(20) * d(str(math.log10(float(
        d(2) / (d(4) + normalized_shunt ** 2).sqrt()
    ))))
    am_total_cap_pf = d("1e12") / (
        (d(2) * d(str(math.pi)) * d(1_710_000)) ** 2 * d(315) * d("1e-6")
    )
    am_external_cap_pf = am_total_cap_pf - d(8)
    am_after_esd_pf = am_external_cap_pf - d(receiver_esd["maximum_unidirectional_capacitance_pf"])

    group_rows = candidate["signal_group_policy"]["groups"]
    groups = {row["id"]: row for row in group_rows}
    quiet_rows = candidate["quiet_state_policy"]["contracts"]
    quiet = {row["id"]: row for row in quiet_rows}
    operating_groups = {
        row["id"]: row for row in power["operating_contract"]["signal_groups"]
    }
    nrf_modes = operating_groups["NRF24"]["modes"]
    nrf_permutations = sum(row.get("identity_permutations", 1) for row in nrf_modes)
    nrf_profiles = [row for row in power["operating_profiles"] if row["signal_group"] == "NRF24"]
    group_to_quiet = {
        "SG-N24": ["N24_QUIET"],
        "SG-S3-24": ["S3_RF_QUIET"],
        "SG-C5-NATIVE": ["C5_RF_QUIET"],
        "SG-CC": ["CC_QUIET"],
        "SG-VOICE": ["VOICE_QUIET", "VOICE_INTERFACE_QUIET"],
        "SG-BROADCAST": ["RECEIVER_QUIET"],
        "SG-U214": ["U214_CAP_QUIET"],
        "SG-IR": ["IR_QUIET"],
        "SG-EXT-*": ["UNIT_PORT_QUIET"],
    }
    support_quiet = {"CODEC_AUDIO_QUIET", "STORAGE_QUIET", "SERVICE_IPC_QUIET"}
    radio_quiet = set(quiet) - support_quiet
    quiet_matrix = []
    for group_id in candidate["i6_consolidated_qualification_contract"]["covered_signal_groups"]:
        own = set(group_to_quiet[group_id])
        quiet_matrix.append({
            "signal_group": group_id,
            "members": groups[group_id]["members"],
            "own_quiet_contracts": sorted(own),
            "required_foreign_quiet_contracts": sorted(radio_quiet - own),
        })

    checks = {
        "upstream_h1_placement_passes": placement["status"] == "pass",
        "upstream_h3_inputs_pass": all(item["status"] == "pass" for item in (digital, analog, provenance)),
        "exactly_ten_named_onboard_paths": path_ids == expected_paths and len(path_ids) == 10,
        "physical_topology_covers_all_paths": topology_path_ids == expected_paths,
        "physical_split_is_exactly_five_plus_five": front_path_ids == expected_front and rear_path_ids == expected_rear,
        "five_removable_microcoaxes": len(topology["cables"]) == 5 and microcoax["path_count"] == 5,
        "microcoax_mix_is_two_30_plus_three_60": microcoax["thirty_mm_paths"] == 2 and microcoax["sixty_mm_paths"] == 3,
        "microcoax_has_at_least_5mm_conservative_slack": microcoax["minimum_conservative_slack_mm"] >= 5,
        "each_microcoax_identity_matches_candidate": all(
            instances[{"S3-2G4": "s3_rf_jumper", "C5-2G4/5": "c5_rf_jumper", "N24-0": "nrf0_rf_jumper", "N24-1": "nrf1_rf_jumper", "N24-2": "nrf2_rf_jumper"}[row["path"]]] == row["selected_device_id"]
            for row in microcoax["paths"]
        ),
        "both_jumper_lengths_cover_c5_frequency": min(d(jumper_30["frequency_max_ghz"]), d(jumper_60["frequency_max_ghz"]), d(ufl["frequency_max_ghz"])) >= c5_top_ghz,
        "c5_connector_has_115mhz_margin": connector_margin_ghz == d("0.115"),
        "native_coupler_covers_s3_and_c5": native_coupler["bands_mhz"][0][0] <= 2400 <= 2484 <= native_coupler["bands_mhz"][0][1] and native_coupler["bands_mhz"][1][0] <= 5180 <= 5885 <= native_coupler["bands_mhz"][1][1],
        "nrf_coupler_covers_all_channels_under_quarter_db": nrf_coupler["operating_band_mhz"][0] <= 2400 and nrf_coupler["operating_band_mhz"][1] >= 2525 and nrf_loss_db <= d("0.25"),
        "cc_known_868_915_loss_is_1p84db": cc_known_loss_db == d("1.84"),
        "voice_esd_ideal_loss_is_below_0p001db": voice_ideal_loss_db < d("0.001"),
        "amlw_external_cap_budget_is_19p5pf": d("19.4") < am_external_cap_pf < d("19.6") and am_after_esd_pf > d("19.0"),
        "airband_reuses_rx_fm_sw_port": len(airband_segments) == 1 and "AIRBAND_118_137_RX" in {row["id"] for row in operating_groups["BROADCAST_RX"]["modes"]},
        "no_rf_path_uses_m1": digital["m1"]["checks"]["no_local_payload_crosses"] and all(row["frame"] in {"ui-inner", "rf-inner"} for row in pcb_segments),
        "one_top_level_group_only": power["operating_contract"]["invariants"]["top_level_active_signal_groups_max"] == 1,
        "all_nine_active_groups_mapped": set(groups) == set(group_to_quiet) and len(groups) == 9,
        "all_13_quiet_contracts_present": set(quiet) == set(candidate["quiet_state_policy"]["required_contracts"]) and len(quiet) == 13,
        "each_group_requires_every_foreign_radio_quiet_contract": all(
            len(row["required_foreign_quiet_contracts"]) == len(radio_quiet) - len(row["own_quiet_contracts"])
            for row in quiet_matrix
        ),
        "nrf_has_three_independent_members": groups["SG-N24"]["members"] == ["nrf0", "nrf1", "nrf2"],
        "nrf_has_all_four_role_mixes": {row["id"] for row in nrf_modes} == {"3PRX", "1PTX_2PRX", "2PTX_1PRX", "3PTX"},
        "nrf_has_eight_identity_permutations": nrf_permutations == 8,
        "nrf_profiles_cover_both_support_loads": {row["support_profile"] for row in nrf_profiles} == {"SUPPORT_IDLE", "SUPPORT_WORST"},
        "nrf_has_three_independent_spi_resources": {"NRF0_SPI", "NRF1_SPI", "NRF2_SPI"}.issubset(set(candidate["exclusive_resource_contracts"])),
        "runtime_unknown_fails_closed": candidate["i6_consolidated_qualification_contract"]["runtime_invariant"]["unknown_or_timeout_result"] == "NONE_and_all_TX_disarmed",
        **exact_checks,
        **route_checks,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3-R2.5 checks failed: " + ", ".join(failed))

    feed_summary = {
        "external_ports": 10,
        "tx_capable_paths": 8,
        "receive_only_paths": 2,
        "native_2g4_coupler_loss_db_max": native_coupler["mainline_loss_max_db"]["2400_2496"],
        "native_5g_coupler_loss_db_max": native_coupler["mainline_loss_max_db"]["4900_5950"],
        "nrf_coupler_loss_db_max": q(nrf_loss_db),
        "cc_868_915_known_loss_before_passives_trace_connector_db": q(cc_known_loss_db),
        "voice_esd_ideal_loss_at_480mhz_db": q(voice_ideal_loss_db, "0.000001"),
        "amlw_total_cap_at_1710khz_315uh_pf": q(am_total_cap_pf),
        "amlw_external_cap_after_8pf_input_pf": q(am_external_cap_pf),
        "amlw_remaining_after_esd_pf": q(am_after_esd_pf),
    }
    physical_residuals = [
        "H5/J4-F: inspect exact received cable/receptacle mating, gentle service loop, bend radius, retention and strain routing for all five paths",
        "H6: field-solve and coupon-correlate every ordinary 50-ohm mainline, launch, reference plane, return path and via fence; extract RX-AM/LW capacitance separately",
        "H8: VNA-test insertion loss and return loss for all ten complete assembled feeds at every admitted band edge",
        "H8: calibrate every actual-TX detector and prove no false negative at minimum qualified output; inbound false positives may only delay",
        "H8: run the isolated baseline, foreign-group quiet matrix, maximum support-load aggression and ordered transition/fault suite",
        "H8: run all four 3xnRF role mixes and eight identity permutations with an independent observer; paper review does not claim same-channel isolation",
        "H8: measure final antenna gain/feed loss and bind regional power, duty, emission, exposure and thermal profiles",
    ]
    result = {
        "schema_version": 1,
        "artifact": "H3-R2-rf-coexistence",
        "marker": "H3-R2.5",
        "status": "pass",
        "reviewed_on": "2026-08-31",
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in (CANDIDATE, DEVICES, ANTENNAS, PLACEMENT, POWER, DIGITAL, ANALOG, PROVENANCE)},
        "summary": {
            "checks": len(checks),
            "external_ports": 10,
            "front_ports": 5,
            "rear_ports": 5,
            "microcoaxes": 5,
            "minimum_conservative_microcoax_slack_mm": microcoax["minimum_conservative_slack_mm"],
            "active_signal_groups": 9,
            "quiet_contracts": 13,
            "nrf_role_modes": 4,
            "nrf_identity_permutations": 8,
            "analytical_findings_open": 0,
            "physical_residuals": len(physical_residuals),
        },
        "feed_summary": feed_summary,
        "microcoax": microcoax,
        "path_topology": {"front": sorted(expected_front), "rear": sorted(expected_rear), "airband_branch": airband_segments[0]},
        "quiet_matrix": quiet_matrix,
        "nrf_concurrency": {
            "members": groups["SG-N24"]["members"],
            "role_modes": [row["id"] for row in nrf_modes],
            "identity_permutations": nrf_permutations,
            "support_profiles": sorted({row["support_profile"] for row in nrf_profiles}),
            "paper_limit": "same/near-channel isolation remains physical H8 evidence; no peer standby or hidden RX gap may be substituted",
        },
        "checks": checks,
        "errors": [],
        "physical_residuals": physical_residuals,
        "authorization": {
            "paper_rf_contract_reviewed": True,
            "kicad_routing_or_fabrication": False,
            "final_rf_performance_claim": False,
        },
        "next": {"marker": "H3-R2.6", "action": "thermal and duty-envelope verification"},
    }

    en = f"""# RF electrical verification · H3-R2.5

`H3-R2.5` is reviewed with **{len(checks)} passing machine checks** and no open analytical finding. [`H3-R2.6`](thermal-fault-electrical-verification.md), the H3-R2.7 phase package and global H4-R2 are also reviewed; the current marker is `H5.0.3-R1`.

The ten source-to-port paths are local to the PCB that carries their antenna: `5 + 5`, with no RF crossing M1. S3 and C5 retain exact 30-mm jumpers; the three nRF paths use exact 60-mm jumpers. The conservative generated reach test leaves at least **{microcoax['minimum_conservative_slack_mm']:.3f} mm** and bounds every nRF from the farthest corner of the complete module envelope rather than guessing the IPEX axis. Airband is a receive-only selectable branch behind the existing `RX-FM/SW` port.

Paper component limits are internally consistent: C5 keeps 115-MHz connector margin at 5.885 GHz, the nRF coupler is at most {q(nrf_loss_db):.3f} dB, the known CC1101 868/915-MHz balun-plus-switch contribution is {q(cc_known_loss_db):.3f} dB before passives/trace/connector, and the AM/LW external capacitance budget remains {q(am_external_cap_pf):.3f} pF.

Runtime still admits at most one of nine top-level signal groups and preserves all thirteen quiet contracts. The deliberate `SG-N24` internal exception keeps all three radios active in 3PRX, 1PTX+2PRX, 2PTX+1PRX and 3PTX, covering eight radio-identity permutations under both support loads.

This closes the **pre-layout electrical model**, not final RF performance. Seven physical residuals remain explicitly assigned to H5 final-assembly evidence, H6 solved/coupon-correlated routing and H8 VNA/OTA/coexistence qualification.

Machine evidence: [`H3-R2-rf-coexistence.json`](../hardware/verification/generated/H3-R2-rf-coexistence.json).
"""
    ru = f"""# Электрическая RF-проверка · H3-R2.5

`H3-R2.5` проведён ревью: **{len(checks)} машинных checks проходят**, открытых аналитических findings нет. [`H3-R2.6`](thermal-fault-electrical-verification.ru.md), пакеты фаз H3-R2.7 и H4-R2 также проведены ревью; текущий маркер — `H5.0.3-R1`.

Все десять source-to-port трактов остаются на плате своего антенного разъёма: `5 + 5`, RF через M1 не проходит. S3 и C5 сохраняют точные 30-мм перемычки, три nRF получают точные 60-мм перемычки. Консервативная проверка оставляет не меньше **{microcoax['minimum_conservative_slack_mm']:.3f} мм** и считает каждый nRF до самого дальнего угла полного корпуса модуля, не угадывая ось IPEX. Airband остаётся только приёмной выбираемой ветвью существующего порта `RX-FM/SW`.

Бумажные пределы компонентов согласованы: у C5 остаётся 115 МГц запаса разъёма на верхней частоте 5,885 ГГц, потери nRF-coupler не больше {q(nrf_loss_db):.3f} дБ, известный вклад balun+switches CC1101 на 868/915 МГц равен {q(cc_known_loss_db):.3f} дБ до passives/trace/connector, а внешний бюджет ёмкости AM/LW остаётся {q(am_external_cap_pf):.3f} пФ.

Runtime допускает максимум одну из девяти верхнеуровневых групп и сохраняет все тринадцать quiet contracts. Намеренное внутреннее исключение `SG-N24` держит активными все три радио в режимах 3PRX, 1PTX+2PRX, 2PTX+1PRX и 3PTX: восемь перестановок идентичностей под обеими support-нагрузками.

Так закрывается **pre-layout электрическая модель**, а не заявляются финальные RF-характеристики. Семь физических residuals явно назначены H5 для evidence финальной сборки, H6 для field-solved/coupon-correlated трассировки и H8 для VNA/OTA/coexistence квалификации.

Машинное evidence: [`H3-R2-rf-coexistence.json`](../hardware/verification/generated/H3-R2-rf-coexistence.json).
"""
    return {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: en,
        DOC_RU: ru,
    }, result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, result = build()
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
    else:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        if stale:
            raise SystemExit("stale H3-R2.5 artifacts: " + ", ".join(stale))
    print(
        f"ok: H3-R2.5 reviewed; {result['summary']['checks']} checks, "
        f"{result['summary']['external_ports']} RF ports, next H3-R2.6"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
