#!/usr/bin/env python3
"""Derive H3.5.1 RF feed, connector, matching and loss constraints."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
DIGITAL_PATH = REPO / "hardware/verification/generated/H3-VRF44-digital-consolidation.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF51-rf-feed-constraints.json"
DOC_EN = REPO / "docs/rf-feed-constraints.md"
DOC_RU = REPO / "docs/rf-feed-constraints.ru.md"

SOURCES = {
    "s3_module": "https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf",
    "c5_module": "https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf",
    "jumper": "https://www.te.com/en/product-2118651-2.html",
    "ufl": "https://www.hirose.com/product/series/U.FL",
    "sma": "https://gct.co/connector/rfpc-sma31-fn",
    "rp_sma": "https://gct.co/connector/rfpc-sma32-fn",
    "native_coupler": "https://datasheets.kyocera-avx.com/cp0302.pdf",
    "nrf_coupler": "https://cdn.ttm.com/repository/products/wireless-xinger/10-20-30-dB-directional-couplers/DC2337J5010AHF/DC2337J5010AHF.pdf",
    "cc1101": "https://www.ti.com/lit/ds/symlink/cc1101.pdf",
    "cc_balun": "https://cdn.ttm.com/repository/products/wireless-xinger/balun-transformers/B0310J50100AHF/B0310J50100AHF.pdf",
    "cc_switch": "https://www.infineon.com/assets/row/public/documents/24/49/infineon-bgs13sn8-datasheet-en.pdf",
    "voice": "https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf",
    "receiver": "https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf",
    "receiver_guidance": "https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN383.pdf",
}


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    digital = json.loads(DIGITAL_PATH.read_text(encoding="utf-8"))
    instances = candidate["instances"]
    routes = {(row["from"], row["to"], row["net"]) for row in candidate["fixed_routes"]}

    exact_instances = {
        "s3": "esp32_s3_wroom_1u_n16r8",
        "c5": "esp32_c5_wroom_1u_n8r8",
        "s3_external_rp_sma": "gct_rfpc_sma32_fn_175_a",
        "c5_external_rp_sma": "gct_rfpc_sma32_fn_175_a",
        "receiver_fmsw_external_sma": "gct_rfpc_sma31_fn_175_a",
        "receiver_amlw_external_sma": "gct_rfpc_sma31_fn_175_a",
        "nrf0_external_sma": "gct_rfpc_sma31_fn_175_a",
        "nrf1_external_sma": "gct_rfpc_sma31_fn_175_a",
        "nrf2_external_sma": "gct_rfpc_sma31_fn_175_a",
        "cc_external_sma": "gct_rfpc_sma31_fn_175_a",
        "voice_external_sma": "gct_rfpc_sma31_fn_175_a",
        "voice_v_external_sma": "gct_rfpc_sma31_fn_175_a",
        "s3_rf_jumper": "te_2118651_2",
        "c5_rf_jumper": "te_2118651_2",
        "nrf0_rf_jumper": "te_2118651_2",
        "nrf1_rf_jumper": "te_2118651_2",
        "nrf2_rf_jumper": "te_2118651_2",
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
        "cc": "cc1101rgpr",
        "cc_balun": "ttm_b0310j50100ahf",
        "cc_switch_a": "infineon_bgs13sn8e6327xtsa1",
        "cc_switch_b": "infineon_bgs13sn8e6327xtsa1",
        "voice": "nicerf_sa818s_u_v18",
        "voice_v": "nicerf_sa818s_v_v18",
        "receiver": "skyworks_si4732_a10_gsr",
    }
    exact_checks = {f"exact_{name}": instances.get(name) == part for name, part in exact_instances.items()}

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
        "voice_u_direct_to_sma": ("voice.ANT", "voice_external_sma.RF", "VOICE_U_EXTERNAL_RF_50R"),
        "voice_v_direct_to_sma": ("voice_v.ANT", "voice_v_external_sma.RF", "VOICE_V_EXTERNAL_RF_50R"),
        "fmsw_to_match": ("receiver_fmsw_external_sma.RF", "receiver_fmi_match_inductor.END_1", "RX_FMSW_PROTECTED_RF"),
        "amlw_to_coupling": ("receiver_amlw_external_sma.RF", "receiver_ami_coupling_cap.END_1", "RX_AMLW_PROTECTED_RF"),
    }
    for index in range(3):
        required_routes[f"nrf{index}_module_to_jumper"] = (f"nrf{index}.ANT", f"nrf{index}_rf_jumper.END_A", f"NRF{index}_MODULE_RF_50R")
        required_routes[f"nrf{index}_jumper_to_board"] = (f"nrf{index}_rf_jumper.END_B", f"nrf{index}_rf_board_connector.CENTER", f"NRF{index}_MODULE_RF_50R")
        required_routes[f"nrf{index}_coupler_to_sma"] = (f"nrf{index}_coupler.RF_OUT", f"nrf{index}_external_sma.RF", f"NRF{index}_EXTERNAL_RF_50R")
    route_checks = {f"route_{name}": route in routes for name, route in required_routes.items()}

    sma = devices["gct_rfpc_sma31_fn_175_a"]["electrical_contract"]
    rp_sma = devices["gct_rfpc_sma32_fn_175_a"]["electrical_contract"]
    ufl = devices["hirose_ufl_r_smt_1_10"]["electrical_contract"]
    jumper = devices["te_2118651_2"]["electrical_contract"]
    native_coupler = devices["kyocera_avx_cp0603q5425entr"]["electrical_contract"]
    nrf_coupler = devices["ttm_dc2337j5010ahf"]["electrical_contract"]
    cc_balun = devices["ttm_b0310j50100ahf"]["electrical_contract"]
    cc_switch = devices["infineon_bgs13sn8e6327xtsa1"]["electrical_contract"]
    voice_esd = devices["nexperia_pesd24vy1bsf"]["electrical_contract"]
    receiver_esd = devices["littelfuse_sesd0402x1un_0020_090"]["electrical_contract"]

    c5_top_ghz = d("5.885")
    connector_margin_ghz = d(rp_sma["maximum_frequency_ghz"]) - c5_top_ghz
    native_known_loss_24_db = d(native_coupler["mainline_loss_max_db"]["2400_2496"])
    native_known_loss_5_db = d(native_coupler["mainline_loss_max_db"]["4900_5950"])
    nrf_known_loss_low_db = d(nrf_coupler["mainline_insertion_loss_db_max_2400_2500"])
    nrf_known_loss_high_db = d(nrf_coupler["mainline_insertion_loss_db_max_2500_3300"])
    cc_known_868_915_db = d(cc_balun["insertion_loss_db_max"]) + d(2) * d(cc_switch["insertion_loss_db_698_to_960_typ_max"][1])

    voice_cap_pf = d(voice_esd["typical_capacitance_pf"])
    voice_top_hz = d(480_000_000)
    normalized_shunt = d(2) * d(str(math.pi)) * voice_top_hz * voice_cap_pf * d("1e-12") * d(50)
    voice_ideal_esd_loss_db = -d(20) * d(str(math.log10(float(d(2) / (d(4) + normalized_shunt**2).sqrt()))))

    am_top_hz = d(1_710_000)
    am_pod_inductance_uh_nom = d(300)
    am_pod_inductance_uh_max = am_pod_inductance_uh_nom * d("1.05")
    pi = d(str(math.pi))
    am_total_cap_pf_max = d("1e12") / ((d(2) * pi * am_top_hz) ** 2 * am_pod_inductance_uh_max * d("1e-6"))
    am_input_cap_pf = d(8)
    am_external_cap_pf_max = am_total_cap_pf_max - am_input_cap_pf
    am_after_esd_cap_pf = am_external_cap_pf_max - d(receiver_esd["maximum_unidirectional_capacitance_pf"])

    paths = [
        {"id": "S3-2G4", "mode": "50_ohm_tx_rx", "band_mhz": [2400, 2484], "connector": "RFPC-SMA32-FN-175-A RP-SMA", "known_mainline_loss_db_max": q(native_known_loss_24_db), "complete_feed_loss_target_db_max": "1.500", "return_loss_target_db_min": "10.000"},
        {"id": "C5-2G4/5", "mode": "50_ohm_tx_rx", "band_mhz": [2400, 5885], "connector": "RFPC-SMA32-FN-175-A RP-SMA", "known_mainline_loss_db_max": {"2g4": q(native_known_loss_24_db), "5g": q(native_known_loss_5_db)}, "complete_feed_loss_target_db_max": {"2g4": "1.500", "5g": "2.000"}, "return_loss_target_db_min": "10.000"},
    ]
    for index in range(3):
        paths.append({"id": f"N24-{index}", "mode": "50_ohm_tx_rx", "band_mhz": [2400, 2525], "connector": "RFPC-SMA31-FN-175-A SMA", "known_mainline_loss_db_max": {"2400_2500": q(nrf_known_loss_low_db), "2500_2525": q(nrf_known_loss_high_db)}, "complete_feed_loss_target_db_max": "1.500", "return_loss_target_db_min": "10.000"})
    paths.extend([
        {"id": "CC-SUB", "mode": "matched_to_50_ohm_tx_rx", "band_mhz": [300, 928], "profiles_mhz": [315, 433, 868, 915], "connector": "RFPC-SMA31-FN-175-A SMA", "known_loss_db_max_868_915_before_passives_trace_connector": q(cc_known_868_915_db), "complete_tuned_feed_loss_target_db_max": "3.000", "return_loss_target_db_min": "10.000", "rule": "315/433 switch loss and all branch matching remain VNA/conducted gates; first-pass values are not accepted as a paper match"},
        {"id": "VOICE-VHF", "mode": "50_ohm_tx_rx", "band_mhz": [134, 174], "connector": "RFPC-SMA31-FN-175-A SMA", "source": "SA818S-V ANT contact 12", "ideal_0p17pf_esd_loss_db_at_480mhz_upper_bound": q(voice_ideal_esd_loss_db, "0.000001"), "complete_feed_loss_target_db_max": "0.750", "return_loss_target_db_min": "10.000"},
        {"id": "VOICE-UHF", "mode": "50_ohm_tx_rx", "band_mhz": [400, 480], "qualified_alternate_band_mhz": [400, 470], "connector": "RFPC-SMA31-FN-175-A SMA", "source": "SA818S-U ANT contact 12; SA818S-CE only after qualification", "ideal_0p17pf_esd_loss_db_at_480mhz": q(voice_ideal_esd_loss_db, "0.000001"), "complete_feed_loss_target_db_max": "0.750", "return_loss_target_db_min": "10.000"},
        {"id": "RX-FM/SW", "mode": "50_ohm_connector_corridor_to_non50_receiver_match", "band_mhz": [2.3, 108], "connector": "RFPC-SMA31-FN-175-A SMA", "sensitivity_degradation_target_db_max": "1.500", "rule": "hold 50 ohms only from SMA to the first 56-nH matching body; place 1-nF coupling at FMI and qualify FM and SW separately"},
        {"id": "RX-AM/LW", "mode": "non50_high_impedance_loop_pod", "band_mhz": [0.153, 1.710], "connector": "RFPC-SMA31-FN-175-A SMA used mechanically", "pod_inductance_uh": "300 +/-5%", "total_capacitance_pf_max_at_1710khz_worst_l": q(am_total_cap_pf_max), "si4732_input_capacitance_pf": q(am_input_cap_pf), "external_total_capacitance_pf_max": q(am_external_cap_pf_max), "remaining_after_esd_pf_max": q(am_after_esd_cap_pf), "rule": "never route or document this as a generic 50-ohm coax feed; use a short direct loop/pod and minimize all pad/trace/connector capacitance"},
    ])

    checks = {
        **exact_checks,
        **route_checks,
        "h34_digital_phase_is_reviewed": digital["review_summary"]["status"] == "reviewed",
        "antenna_policy_has_exactly_ten_onboard_ports": candidate["antenna_policy"]["base_onboard_sma_count"] == 10 and len(candidate["antenna_policy"]["base_onboard_sma_paths"]) == 10,
        "all_ten_paths_are_instantiated_once": len(paths) == 10 and {row["id"] for row in paths} == set(candidate["antenna_policy"]["base_onboard_sma_paths"]),
        "eight_tx_capable_and_two_receive_only_paths": sum("tx_rx" in row["mode"] for row in paths) == 8 and sum(row["id"].startswith("RX-") for row in paths) == 2,
        "every_external_connector_is_50_ohm_and_6ghz": sma["impedance_ohm"] == rp_sma["impedance_ohm"] == 50 and sma["maximum_frequency_ghz"] == rp_sma["maximum_frequency_ghz"] == 6,
        "c5_top_band_fits_connector_with_115mhz_margin": connector_margin_ghz >= d("0.115"),
        "jumper_and_board_receptacle_cover_c5_top_band": d(jumper["frequency_max_ghz"]) >= c5_top_ghz and d(ufl["frequency_max_ghz"]) >= c5_top_ghz,
        "native_coupler_covers_s3_and_c5_bands": native_coupler["bands_mhz"][0][0] <= 2400 and native_coupler["bands_mhz"][0][1] >= 2484 and native_coupler["bands_mhz"][1][0] <= 5180 and native_coupler["bands_mhz"][1][1] >= 5885,
        "nrf_coupler_covers_all_channels": nrf_coupler["operating_band_mhz"][0] <= 2400 and nrf_coupler["operating_band_mhz"][1] >= 2525,
        "nrf_coupler_loss_is_below_quarter_db": max(nrf_known_loss_low_db, nrf_known_loss_high_db) <= d("0.25"),
        "cc_balun_covers_all_profiles": cc_balun["frequency_mhz"][0] <= 315 and cc_balun["frequency_mhz"][1] >= 915,
        "cc_switch_covers_all_profiles": cc_switch["frequency_mhz"][0] <= 315 and cc_switch["frequency_mhz"][1] >= 915,
        "cc_known_868_915_loss_is_1p84db": cc_known_868_915_db == d("1.84"),
        "voice_esd_is_negligible_in_ideal_shunt_model": voice_ideal_esd_loss_db < d("0.001"),
        "am_total_cap_is_worst_case_315uh": d("27.4") < am_total_cap_pf_max < d("27.6"),
        "am_external_cap_budget_is_below_19p6pf": am_external_cap_pf_max < d("19.6"),
        "am_esd_leaves_more_than_19pf": am_after_esd_cap_pf > d(19),
        "amlw_is_explicitly_not_50_ohm": paths[-1]["mode"] == "non50_high_impedance_loop_pod" and "50-ohm" in paths[-1]["rule"],
        "all_50ohm_paths_have_measured_loss_or_sensitivity_gate": all("complete_feed_loss_target_db_max" in row or "complete_tuned_feed_loss_target_db_max" in row or "sensitivity_degradation_target_db_max" in row for row in paths[:-1]),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.5.1 checks failed: " + ", ".join(failed))

    residual = [
        "measure S3/C5 complete-feed insertion and return loss at every channel edge, including both microcoax transitions and the selected stackup launch",
        "measure all three E01 module-to-SMA feeds and received-lot Gen1 mating/retention independently",
        "VNA-tune CC1101 differential-to-single-ended match and every 315/433/868/915 branch; prove output, sensitivity, harmonics and switch loss",
        "measure the independent SA818S-V and SA818S-U feed insertion/return loss, output power and harmonics at both power settings; repeat UHF for SA818S-CE before enabling that alternate",
        "qualify Si4732 FMI FM and SW sensitivity/overload with the complete external whip and first-pass 56-nH/1-nF network",
        "measure RX-AM/LW total capacitance <=19.500 pF external to the Si4732 input with the received SMA, PCB and exact pod",
        "derate every allowed TX power/EIRP table by measured complete-feed loss and selected antenna gain before regional profile release",
        "use impedance coupons and de-embedded SMA/U.FL fixtures for H6/H8 acceptance; nominal field-solver values alone cannot close a feed",
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H3.5.1",
        "status": "reviewed_rf_feed_connector_matching_and_loss_constraints",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, DEVICES_PATH, DIGITAL_PATH)},
        "provenance": SOURCES,
        "summary": {"external_ports": 10, "tx_capable_paths": 8, "receive_only_paths": 2, "generic_50_ohm_paths": 8, "matched_or_special_receive_paths": 2},
        "path_constraints": paths,
        "shared_constraints": {
            "controlled_impedance_ohm": "50 +/-10% until stackup coupon correlation; tighten if field solver/fabricator supports it",
            "complete_feed_return_loss_db_min": "10.000 for every generic 50-ohm TX/RX path at every admitted band edge",
            "measurement_rule": "loss, return loss and regional EIRP use the complete assembled feed; component maxima are bounds, not substitutes for VNA/HIL",
            "connector_rule": "S3/C5 use RP-SMA; nRF/CC/voice/receiver use standard SMA; permanent band labels remain mandatory",
            "matching_rule": "reserve tuneable 0402 positions where a discrete match exists; do not add an unproven match to module-native 50-ohm S3/C5/nRF/SA818S paths",
        },
        "derived": {
            "c5_connector_frequency_margin_ghz": q(connector_margin_ghz),
            "cc_known_868_915_loss_db_before_passives_trace_connector": q(cc_known_868_915_db),
            "voice_ideal_esd_loss_db_at_480mhz": q(voice_ideal_esd_loss_db, "0.000001"),
            "amlw_total_capacitance_pf_max_at_1710khz_315uh": q(am_total_cap_pf_max),
            "amlw_external_capacitance_pf_max_after_8pf_input": q(am_external_cap_pf_max),
            "amlw_remaining_pf_after_0p25pf_esd": q(am_after_esd_cap_pf),
        },
        "checks": checks,
        "corrections": [],
        "open_findings": [],
        "residual_physical_only": residual,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.5.2", "action": "derive RF corridors, keepouts, reference-plane and return-current constraints"},
    }

    en = f"""# RF feed constraints

`H3.5.1` is reviewed: `{len(checks)}` machine checks cover all ten external antenna ports and leave no analytical finding open. The exact current marker is `H3.6.1`.

## Per-path contract

| Port | Electrical boundary | Pre-layout acceptance target |
|---|---|---|
| S3-2G4 | 50-ohm module -> 30-mm UMCC -> U.FL -> dual-band coupler -> RP-SMA | complete feed <=1.5 dB, return loss >=10 dB |
| C5-2G4/5 | same, through 5.885 GHz | <=1.5 dB at 2.4 GHz, <=2.0 dB at 5 GHz, return loss >=10 dB |
| N24-0/1/2 | three independent 50-ohm module -> UMCC/U.FL -> 10-dB coupler -> SMA feeds | each <=1.5 dB and >=10-dB return loss through 2525 MHz |
| CC-SUB | CC1101 differential match -> balun -> dual-ended selected branch -> SMA | tuned complete path <=3 dB and >=10-dB return loss at 315/433/868/915 MHz |
| VOICE-VHF | native 50-ohm SA818S-V ANT 12 -> short protected trace -> dedicated SMA | <=0.75 dB and >=10-dB return loss at 134-174 MHz |
| VOICE-UHF | native 50-ohm SA818S-U ANT 12 -> short protected trace -> dedicated SMA | <=0.75 dB and >=10-dB return loss at 400-480 MHz; CE alternate is capped at 470 MHz |
| RX-FM/SW | 50-ohm SMA corridor only up to the first 56-nH body, then receiver-specific match | complete-fixture sensitivity degradation <=1.5 dB; FM and SW qualify separately |
| RX-AM/LW | **not a 50-ohm feed**; SMA is only the serial mechanical boundary for a short loop/pod | external capacitance <=`{q(am_external_cap_pf_max)} pF` including connector, PCB, ESD and pod |

The AM/LW bound uses the pod's 300-uH +5% corner and the 1710-kHz high edge: total resonance capacitance is `{q(am_total_cap_pf_max)} pF`. The Si4732 input consumes 8 pF and the worst registered ESD consumes up to 0.25 pF, leaving `{q(am_after_esd_cap_pf)} pF` for SMA, PCB and pod parasitics. Generic long coax is therefore forbidden on this port.

Known component loss is not mistaken for complete-feed loss. For example, the CC 868/915 path already has a `{q(cc_known_868_915_db)}-dB` paper maximum from the balun and two switches before matching passives, launches and trace; all four branches remain conducted/VNA gates.

Machine evidence: [`H3-VRF51-rf-feed-constraints.json`](../hardware/verification/generated/H3-VRF51-rf-feed-constraints.json).
"""
    ru = f"""# Ограничения антенных трактов

`H3.5.1` проведён ревью: `{len(checks)}` машинных checks охватывают все десять внешних антенных портов, незакрытых аналитических findings нет. Точный текущий маркер — `H3.6.1`.

## Контракт каждого тракта

| Порт | Электрическая граница | Pre-layout acceptance target |
|---|---|---|
| S3-2G4 | 50 Ом module -> 30-мм UMCC -> U.FL -> dual-band coupler -> RP-SMA | полный feed <=1,5 дБ, return loss >=10 дБ |
| C5-2G4/5 | тот же тракт до 5,885 ГГц | <=1,5 дБ на 2,4 ГГц, <=2,0 дБ на 5 ГГц, return loss >=10 дБ |
| N24-0/1/2 | три независимых 50-омных module -> UMCC/U.FL -> 10-dB coupler -> SMA | каждый <=1,5 дБ и return loss >=10 дБ до 2525 МГц |
| CC-SUB | differential match CC1101 -> balun -> выбранная с двух концов branch -> SMA | настроенный полный тракт <=3 дБ и return loss >=10 дБ на 315/433/868/915 МГц |
| VOICE-VHF | native 50-омный ANT 12 SA818S-V -> короткая защищённая трасса -> отдельный SMA | <=0,75 дБ и return loss >=10 дБ на 134-174 МГц |
| VOICE-UHF | native 50-омный ANT 12 SA818S-U -> короткая защищённая трасса -> отдельный SMA | <=0,75 дБ и return loss >=10 дБ на 400-480 МГц; alternate CE ограничен 470 МГц |
| RX-FM/SW | 50-омный SMA corridor только до первого корпуса 56 нГн, затем receiver-specific match | деградация sensitivity полного fixture <=1,5 дБ; FM и SW проверяются отдельно |
| RX-AM/LW | **не 50-омный тракт**; SMA служит только серийной механической границей короткой петли/pod | внешняя ёмкость <=`{q(am_external_cap_pf_max)} пФ` вместе с connector, PCB, ESD и pod |

AM/LW bound использует corner pod 300 мкГн +5% и верхнюю границу 1710 кГц: полная резонансная ёмкость равна `{q(am_total_cap_pf_max)} пФ`. Вход Si4732 занимает 8 пФ, зарегистрированный ESD — до 0,25 пФ; на SMA, PCB и parasitics pod остаётся `{q(am_after_esd_cap_pf)} пФ`. Поэтому произвольный длинный coax на этом порту запрещён.

Известная потеря компонента не выдаётся за потерю полного feed. Например, на CC 868/915 бумажный максимум balun и двух switches уже равен `{q(cc_known_868_915_db)} дБ` до matching passives, launches и trace; все четыре branches остаются conducted/VNA gates.

Машинное evidence: [`H3-VRF51-rf-feed-constraints.json`](../hardware/verification/generated/H3-VRF51-rf-feed-constraints.json).
"""
    return {OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", DOC_EN: en, DOC_RU: ru}, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("stale H3.5.1 artifacts: " + ", ".join(stale))
    print(f"ok: H3.5.1 reviewed; {len(manifest['checks'])} checks, next H3.5.2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
