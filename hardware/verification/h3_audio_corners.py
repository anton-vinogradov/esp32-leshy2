#!/usr/bin/env python3
"""Verify H3.3.2 codec, microphone, headset, voice injection and speaker corners."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from itertools import product
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
METHODS_PATH = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
DISPLAY_PATH = REPO / "hardware/verification/generated/H3-VRF31-display.json"
DC_PATH = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF32-audio.json"
DOC_EN = REPO / "docs/audio-electrical-verification.md"
DOC_RU = REPO / "docs/audio-electrical-verification.ru.md"

SOURCES = {
    "codec_product_brief": "https://www.everest-semi.com/pdf/ES8311%20PB.pdf",
    "codec_application_guide": "https://files.waveshare.com/wiki/common/ES8311.user.Guide.pdf",
    "speaker_amplifier": "https://www.diodes.com/datasheet/download/PAM8302A.pdf",
    "speaker": "https://puiaudio.com/product/speakers-and-receivers/as02404po",
    "microphone": "https://www.sameskydevices.com/product/resource/cmej-0413-42-smt-tr.pdf",
    "headset_jack": "https://www.sameskydevices.com/product/resource/sj-43504-smt-tr.pdf",
    "voice_module": "https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf",
    "microphone_selectors": "https://www.ti.com/lit/ds/symlink/ts5a63157.pdf",
    "speaker_selector": "https://www.ti.com/lit/ds/symlink/tmux1136.pdf",
    "passive_family": "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_16.pdf",
    "selected_tx_resistor": "https://www.vishay.com/docs/20035/dcrcwe3.pdf",
}

PI = Decimal("3.141592653589793238462643383279503")


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def db_ratio(db: Decimal) -> Decimal:
    return (db * d(10).ln() / d(20)).exp()


def db(value: Decimal) -> Decimal:
    return d(20) * value.ln() / d(10).ln()


def route_set(candidate: dict) -> set[tuple[str, str, str]]:
    return {(row["from"], row["to"], row["net"]) for row in candidate["fixed_routes"]}


def require_route(routes: set[tuple[str, str, str]], start: str, end: str, net: str) -> bool:
    return (start, end, net) in routes or (end, start, net) in routes


def attenuator_magnitude(r_top: Decimal, r_bottom: Decimal, capacitance: Decimal, frequency: Decimal) -> Decimal:
    """Magnitude of Rtop feeding Rbottom || C without float/complex arithmetic."""
    x_c = d(1) / (d(2) * PI * frequency * capacitance)
    denominator = r_bottom * r_bottom + x_c * x_c
    z_real = r_bottom * x_c * x_c / denominator
    z_imag = -(r_bottom * r_bottom * x_c / denominator)
    numerator_mag_sq = z_real * z_real + z_imag * z_imag
    denominator_mag_sq = (r_top + z_real) ** 2 + z_imag * z_imag
    return (numerator_mag_sq / denominator_mag_sq).sqrt()


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    methods = json.loads(METHODS_PATH.read_text(encoding="utf-8"))
    display = json.loads(DISPLAY_PATH.read_text(encoding="utf-8"))
    dc_budget = json.loads(DC_PATH.read_text(encoding="utf-8"))
    instances = candidate["instances"]
    routes = route_set(candidate)

    exact_parts = {
        "codec": "everest_es8311_qfn20",
        "audio_capture_buffer": "ti_tlv9061_idbvr",
        "audio_capture_selector": "ti_ts5a63157_dckr",
        "headset_mic_selector": "ti_ts5a63157_dckr",
        "audio_speaker_selector": "ti_tmux1136_dgsr",
        "audio_tx_selector": "ti_ts5a63157_dckr",
        "speaker_amp": "diodes_pam8302a_aycr",
        "speaker": "pui_as02404po",
        "microphone": "same_sky_cmej_0413_42_smt_tr",
        "headphone_jack": "same_sky_sj_43504_smt_tr",
        "codec_adc_p_series": "yageo_rc0402jr_070rl",
        "codec_adc_n_series": "yageo_rc0402jr_070rl",
        "codec_tx_atten_top": "vishay_crcw0402160kfked",
        "headset_microphone_bias_filter_res": "yageo_rc0402fr_07220rl",
        "headset_microphone_bias_filter_cap": "murata_grm188r60j106me47d",
    }
    exact_part_checks = {name: instances.get(name) == device for name, device in exact_parts.items()}
    topology_checks = {
        "independent_internal_bias_filter": require_route(routes, "abstract:3V3_MAIN", "microphone_bias_filter_res.END_1", "3V3_MAIN")
        and require_route(routes, "microphone_bias_filter_res.END_2", "microphone_bias_res.END_1", "MIC_BIAS_FILTERED"),
        "independent_headset_bias_filter": require_route(routes, "abstract:3V3_MAIN", "headset_microphone_bias_filter_res.END_1", "3V3_MAIN")
        and require_route(routes, "headset_microphone_bias_filter_res.END_2", "headset_mic_bias_res.END_1", "HEADSET_MIC_BIAS_FILTERED"),
        "direct_reference_mic1p": require_route(routes, "codec_adc_p_series.END_2", "codec.MIC1P", "CODEC_ADC_IN_P"),
        "direct_reference_mic1n": require_route(routes, "codec_adc_n_series.END_2", "codec.MIC1N", "CODEC_ADC_IN_N"),
        "buffer_unity_feedback": require_route(routes, "audio_capture_buffer.OUT", "audio_capture_buffer.IN_MINUS", "CODEC_CAPTURE_BUFFER_FB"),
        "speaker_fail_low": require_route(routes, "speaker_amp.SD", "speaker_amp_enable_pulldown.END_1", "SPEAKER_AMP_EN"),
        "speaker_btl_positive": require_route(routes, "speaker_output_bead_p.END_2", "speaker.PLUS", "SPEAKER_BTL_P"),
        "speaker_btl_negative": require_route(routes, "speaker_output_bead_n.END_2", "speaker.MINUS", "SPEAKER_BTL_N"),
        "ctia_ground": require_route(routes, "headphone_jack.RING2", "abstract:audio-ground", "HEADSET_RING2_GROUND"),
        "headset_detect_only": require_route(routes, "headset_detect_series.END_2", "slow_io.P02", "HEADSET_ABSENT"),
        "codec_tx_reaches_voice": require_route(routes, "voice_audio_iso.2B", "voice_mic_coupling.END_1", "VOICE_MIC_SELECTED_ISOLATED")
        and require_route(routes, "voice_mic_coupling.END_2", "voice.MIC_IN", "VOICE_MIC_IN"),
    }
    structural = {**{f"exact_{name}": ok for name, ok in exact_part_checks.items()}, **topology_checks}
    if not all(structural.values()):
        raise ValueError("H3.3.2 exact topology failed: " + ", ".join(name for name, ok in structural.items() if not ok))

    rail_min = d(display["supply_corner"]["display_connector_v"]["min"])
    rail_max = d(display["supply_corner"]["display_connector_v"]["max"])

    # Internal and headset microphone bias networks are now independent.
    r_filter_nom = d(220)
    r_bias_nom = d(2200)
    resistor_tol = d("0.01")
    capsule_current = d("0.0005")
    microphone_v_min = rail_min - capsule_current * (r_filter_nom * (d(1) + resistor_tol) + r_bias_nom * (d(1) + resistor_tol))
    microphone_v_max = rail_max - capsule_current * (r_filter_nom * (d(1) - resistor_tol) + r_bias_nom * (d(1) - resistor_tol))
    microphone_supply_min_allowed = d("1.0")
    microphone_supply_max_allowed = d("10.0")
    headset_short_current = rail_max / ((r_filter_nom + r_bias_nom) * (d(1) - resistor_tol))
    headset_short_filter_loss = headset_short_current**2 * r_filter_nom * (d(1) - resistor_tol)
    headset_short_bias_loss = headset_short_current**2 * r_bias_nom * (d(1) - resistor_tol)
    resistor_power_rating = d("0.063")

    sensitivity_min_v = db_ratio(d(-45))
    sensitivity_typ_v = db_ratio(d(-42))
    sensitivity_max_v = db_ratio(d(-39))
    aop_factor = db_ratio(d(115 - 94))
    microphone_aop_max_v = sensitivity_max_v * aop_factor
    pga_max = db_ratio(d(30))
    adc_full_scale_min_typical = d(2) * rail_min / d("3.3")
    pga_94db_min_v = sensitivity_min_v * pga_max
    pga_94db_max_v = sensitivity_max_v * pga_max
    maximum_pga_at_aop_db_typical = db(adc_full_scale_min_typical / microphone_aop_max_v)
    former_series = d(33000)
    codec_input_impedance = d(6000)
    former_capture_ratio = codec_input_impedance / (codec_input_impedance + former_series)
    former_capture_loss_db = db(former_capture_ratio)

    # Headphone voice-band corner, with deliberately conservative 50% DC-bias retention.
    headphone_cap_nom_each = d("0.000022")
    headphone_cap_tolerance = d("0.20")
    conservative_bias_retention = d("0.50")
    headphone_cap_min = d(2) * headphone_cap_nom_each * (d(1) - headphone_cap_tolerance) * conservative_bias_retention
    hp_series_min = d(22) * (d(1) - resistor_tol)
    headphone_fc_16 = d(1) / (d(2) * PI * headphone_cap_min * (d(16) + hp_series_min))
    headphone_fc_32 = d(1) / (d(2) * PI * headphone_cap_min * (d(32) + hp_series_min))
    detect_ratio_min = d(100000) * (d(1) - resistor_tol) / (
        d(100000) * (d(1) - resistor_tol) + d(2) * d(10000) * (d(1) + resistor_tol)
    )
    detect_vih_fraction = d("0.70")
    detect_high_min = detect_ratio_min * rail_min
    plugged_tip_current_max = rail_max / (d(10000) * (d(1) - resistor_tol) + d(16))
    plugged_tip_dc_max = plugged_tip_current_max * d(16)

    # PAM8302A and the actual 4-ohm +/-15% speaker.
    speaker_r_nom = d(4)
    speaker_r_min = speaker_r_nom * (d(1) - d("0.15"))
    speaker_rated_power = d(2)
    amplifier_efficiency_min = d("0.85")
    amplifier_iq_max = d("0.008")
    theoretical_btl_power = rail_max**2 / (d(2) * speaker_r_min)
    amplifier_supply_current = theoretical_btl_power / (rail_max * amplifier_efficiency_min) + amplifier_iq_max
    audio_branch_limit = d("0.625")
    audio_aux_margin = audio_branch_limit - amplifier_supply_current
    amplifier_loss = theoretical_btl_power * (d(1) / amplifier_efficiency_min - d(1)) + rail_max * amplifier_iq_max
    amplifier_theta_ja = d("47.9")
    amplifier_ambient_max = d(85)
    amplifier_junction_max = amplifier_ambient_max + amplifier_loss * amplifier_theta_ja
    amplifier_recommended_junction_max = d(125)
    speaker_environment_max = d(50)

    # Full-scale single-ended codec leg through 160k / (2.2k || 10nF) into SA518.
    tx_frequency = d(1500)
    tx_top_nom = d(160000)
    tx_bottom_nom = d(2200)
    tx_cap_nom = d("0.000000010")
    tx_values = []
    for r_top, r_bottom, cap, rail, output_coefficient in product(
        (tx_top_nom * d("0.99"), tx_top_nom * d("1.01")),
        (tx_bottom_nom * d("0.99"), tx_bottom_nom * d("1.01")),
        (tx_cap_nom * d("0.90"), tx_cap_nom * d("1.10")),
        (rail_min, rail_max),
        (d("1.71"), d("1.89")),
    ):
        attenuation = attenuator_magnitude(r_top, r_bottom, cap, tx_frequency)
        codec_single_leg = output_coefficient * rail / d("3.3") / d(2)
        tx_values.append(attenuation * codec_single_leg)
    tx_injection_min = min(tx_values)
    tx_injection_max = max(tx_values)
    sa518_target = d("0.010")
    required_dac_scale_min = sa518_target / tx_injection_max
    required_dac_scale_max = sa518_target / tx_injection_min

    dc_worst = d(dc_budget["worst_by_rail"]["3V3_MAIN"]["load_ma"])
    dc_hardware_reserve = d(dc_budget["worst_by_rail"]["3V3_MAIN"]["hardware_reserve_percent"])
    dc_accepted_margin = d(dc_budget["worst_by_rail"]["3V3_MAIN"]["accepted_envelope_margin_ma"])

    checks = {
        **structural,
        "microphone_supply_above_min": microphone_v_min >= microphone_supply_min_allowed,
        "microphone_supply_below_max": microphone_v_max <= microphone_supply_max_allowed,
        "headset_short_filter_resistor_power": headset_short_filter_loss <= resistor_power_rating,
        "headset_short_bias_resistor_power": headset_short_bias_loss <= resistor_power_rating,
        "normal_speech_at_30db_below_adc_typical_full_scale": pga_94db_max_v < adc_full_scale_min_typical,
        "initial_zero_db_handles_microphone_aop": microphone_aop_max_v < adc_full_scale_min_typical,
        "headphone_16ohm_voice_corner_below_300hz": headphone_fc_16 <= d(300),
        "headphone_32ohm_voice_corner_below_200hz": headphone_fc_32 <= d(200),
        "headset_detect_high_meets_ratio": detect_ratio_min >= detect_vih_fraction,
        "speaker_theoretical_power_below_rating": theoretical_btl_power <= speaker_rated_power,
        "speaker_amplifier_inside_625ma_branch": amplifier_supply_current <= audio_branch_limit,
        "amplifier_junction_20c_margin": amplifier_junction_max <= amplifier_recommended_junction_max - d(20),
        "codec_tx_full_scale_can_reach_sa518_target": tx_injection_min >= sa518_target,
        "codec_tx_target_is_downward_calibratable": required_dac_scale_min > d(0) and required_dac_scale_max <= d(1),
        "revised_main_rail_inside_2500ma_admission": dc_worst <= d(2500),
        "revised_main_rail_has_25pct_hardware_reserve": dc_hardware_reserve >= d(25),
        "method_has_missing_limit_rule": any(row["id"] == "PF-10" for row in methods["pass_fail_rules"]),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.3.2 checks failed: " + ", ".join(failed))

    old_cost = d(devices["yageo_rc0402fr_0733kl"]["cost"]["unit_price_usd"]) * d(2) + d(
        devices["yageo_rc0402fr_07220kl"]["cost"]["unit_price_usd"]
    )
    new_cost = d(devices["yageo_rc0402jr_070rl"]["cost"]["unit_price_usd"]) * d(2) + d(
        devices["vishay_crcw0402160kfked"]["cost"]["unit_price_usd"]
    )
    added_cost = d(devices["yageo_rc0402fr_07220rl"]["cost"]["unit_price_usd"]) + d(
        devices["murata_grm188r60j106me47d"]["cost"]["unit_price_usd"]
    )

    manifest = {
        "schema_version": 1,
        "stage": "H3.3.2",
        "status": "reviewed_audio_analog_corners_after_four_source_corrections",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (CANDIDATE_PATH, DEVICES_PATH, METHODS_PATH, DISPLAY_PATH, DC_PATH)
        },
        "provenance": SOURCES,
        "method": "interval_corner plus bounded analytical power/thermal envelopes",
        "exact_part_checks": exact_part_checks,
        "topology_checks": topology_checks,
        "microphone_and_adc": {
            "independent_bias_supply_v": {"min": q(microphone_v_min, "0.000001"), "max": q(microphone_v_max, "0.000001")},
            "capsule_allowed_supply_v": {"min": q(microphone_supply_min_allowed), "max": q(microphone_supply_max_allowed)},
            "headset_ground_short_current_ma_max": q(headset_short_current * d(1000)),
            "headset_short_resistor_loss_mw": {"filter": q(headset_short_filter_loss * d(1000)), "bias": q(headset_short_bias_loss * d(1000))},
            "sensitivity_at_94dbspl_mvrms": {"min": q(sensitivity_min_v * d(1000)), "typ": q(sensitivity_typ_v * d(1000)), "max": q(sensitivity_max_v * d(1000))},
            "microphone_aop_db_spl": 115,
            "aop_max_mvrms": q(microphone_aop_max_v * d(1000)),
            "codec_input_impedance_kohm_typ": q(codec_input_impedance / d(1000)),
            "codec_full_scale_input_vrms_typ_at_min_rail": q(adc_full_scale_min_typical),
            "pga_range_db": {"min": "0", "max": "30"},
            "normal_94dbspl_after_30db_pga_mvrms": {"min": q(pga_94db_min_v * d(1000)), "max": q(pga_94db_max_v * d(1000))},
            "maximum_pga_at_115dbspl_db_typical_full_scale": q(maximum_pga_at_aop_db_typical),
            "firmware_admission": "start at 0 dB; allow up to 30 dB for normal speech, but cap loud-input gain at 21 dB until specimen clipping/ALC qualification",
            "removed_33kohm_loss_db": q(former_capture_loss_db),
            "noise_boundary": "the microphone specifies 60 dBA S/N, ES8311 specifies 100 dB ADC SNR and PAM8302A specifies 300 uV maximum unweighted output noise; board/enclosure/RF-coupled noise cannot be closed without routed hardware and remains an H8 measurement",
        },
        "headset": {
            "standard": "CTIA/AHJ mono dual-ear playback plus microphone; OUTP/OUTN feed opposite-phase left/right legs, so this is not a stereo codec",
            "conservative_effective_coupling_uf_per_ear": q(headphone_cap_min * d(1000000)),
            "high_pass_hz": {"16_ohm": q(headphone_fc_16), "32_ohm": q(headphone_fc_32)},
            "no_plug_detect_high_fraction_min": q(detect_ratio_min, "0.000001"),
            "no_plug_detect_high_v_min": q(detect_high_min),
            "plugged_tip_bias_current_ma_max": q(plugged_tip_current_max * d(1000)),
            "plugged_tip_dc_mv_max_into_16ohm": q(plugged_tip_dc_max * d(1000)),
            "interpretation": "the conservative capacitor corner preserves voice-band playback; low-bass response, headset sensitivity, crosstalk and insertion pop remain measured accessory/HIL properties",
        },
        "speaker": {
            "part": devices[instances["speaker"]]["mpn"],
            "nominal_impedance_ohm": q(speaker_r_nom),
            "minimum_impedance_corner_ohm": q(speaker_r_min),
            "rated_power_w": q(speaker_rated_power),
            "theoretical_btl_sine_power_w_max": q(theoretical_btl_power, "0.000001"),
            "power_margin_to_speaker_rating_w": q(speaker_rated_power - theoretical_btl_power),
            "pam8302a_supply_current_ma_max": q(amplifier_supply_current * d(1000)),
            "audio_branch_admission_ma": q(audio_branch_limit * d(1000)),
            "remaining_codec_selector_margin_ma": q(audio_aux_margin * d(1000)),
            "amplifier_loss_w_max": q(amplifier_loss),
            "amplifier_junction_c_at_85c_ambient": q(amplifier_junction_max),
            "amplifier_margin_to_125c_c": q(amplifier_recommended_junction_max - amplifier_junction_max),
            "speaker_operating_environment_c_max": q(speaker_environment_max),
            "operating_rule": "speaker playback is muted above the speaker's 50 C local environment limit; the rest of the product may remain active subject to the later H3.6 system thermal envelope",
            "startup_rule": "hold PAM8302A SD low through reset/power transition and for at least 10 ms after the main rail is valid; mute codec/selectors before shutdown",
        },
        "voice_tx_injection": {
            "sa518_modulation_target_mvrms": q(sa518_target * d(1000)),
            "frequency_hz": int(tx_frequency),
            "selected_top_resistor": devices[instances["codec_tx_atten_top"]]["mpn"],
            "top_resistor_ohm": int(tx_top_nom),
            "bottom_resistor_ohm": int(tx_bottom_nom),
            "shunt_cap_nf": q(tx_cap_nom * d(1000000000)),
            "full_scale_injection_mvrms": {"min": q(tx_injection_min * d(1000)), "max": q(tx_injection_max * d(1000))},
            "required_codec_full_scale_fraction": {"min": q(required_dac_scale_min, "0.000001"), "max": q(required_dac_scale_max, "0.000001")},
            "rule": "calibrate only downward against measured RF deviation; audio selection never asserts PTT or bypasses RUN/KILL and FAULT_KILL",
        },
        "main_rail_crosscheck": {
            "worst_profile_load_ma": q(dc_worst),
            "accepted_2500ma_margin_ma": q(dc_accepted_margin),
            "hardware_reserve_percent": q(dc_hardware_reserve),
            "normal_display_branch_ma": 200,
            "audio_branch_ma": 625,
            "correction": "normal backlight load is no longer confused with the TPS2553 fault threshold; the actual 4-ohm speaker replaces the former 8-ohm audio basis",
        },
        "checks": checks,
        "corrections": [
            {
                "id": "H3.3.2-F01",
                "finding": "matched 33-kOhm MIC1P/MIC1N series parts formed an unnecessary -16.26-dB divider with the ES8311 6-kOhm input and consumed microphone SNR",
                "correction": "fit exact zero-ohm serial configuration links and retain the two footprints for controlled rework",
                "functional_effect": "restores the reference direct-coupled input while the ES8311 PGA/ALC retains 0-to-30-dB gain control",
            },
            {
                "id": "H3.3.2-F02",
                "finding": "the shared microphone-bias filter let a grounded ordinary-TRS sleeve reduce the internal-microphone supply",
                "correction": "add an independent exact 220-ohm/10-uF headset-bias filter before its existing 2.2-kOhm resistor",
                "functional_effect": "TRS headphones may keep the internal microphone selected without analog supply interaction",
            },
            {
                "id": "H3.3.2-F03",
                "finding": "the 220-kOhm codec-to-SA518 attenuator could not reach the published 10-mV modulation target at low full-scale corners",
                "correction": "use active/in-stock exact Vishay CRCW0402160KFKED; full-scale injection is 10.454-to-12.797 mVrms and is calibrated only downward",
                "functional_effect": "digital/recorded audio can reach nominal deviation without adding an active analog stage",
            },
            {
                "id": "H3.3.2-F04",
                "finding": "the H3.1 audio load cited an 8-ohm curve although the exact speaker is 4 ohm +/-15%, while the display load counted a fault threshold as continuous operation",
                "correction": "reserve 625 mA for audio and 200 mA for normal display/backlight operation; retain the TPS2553 threshold only as a latched fault bound",
                "functional_effect": "the worst 3V3_MAIN profile is 2493 mA with 28.36% guaranteed hardware reserve and no function removed",
            },
        ],
        "cost_delta_usd_at_100": {
            "replaced_instances_old": q(old_cost, "0.0000"),
            "replaced_instances_new": q(new_cost, "0.0000"),
            "added_headset_filter": q(added_cost, "0.0000"),
            "total_delta_per_board": q(new_cost + added_cost - old_cost, "0.0000"),
            "scope": "two ADC configuration links, one codec-TX attenuation resistor and the independent headset 220-ohm/10-uF filter; assembly and tax excluded",
        },
        "residual_physical_only": [
            "measure microphone/headset sensitivity, codec clipping/ALC/noise, channel phase perception, crosstalk, insertion pop and RF immunity on routed hardware",
            "measure PAM8302A current, output EMI, speaker temperature/excursion and enclosure response; enforce the 50 C speaker-local mute rule",
            "calibrate SA518 deviation downward from the bounded full-scale codec injection and repeat across module lots, rail and temperature",
            "prove reset/brownout/off ordering, >=10-ms amplifier-enable delay and absence of back-power with codec, voice and main domains independently off",
        ],
        "review_summary": {"checks": len(checks), "failed_checks": len(failed), "corrected_findings": 4, "unresolved_findings": 0, "status": "reviewed"},
        "next": {"stage": "H3.3.3", "action": "verify IR drive, receive thresholds and thermal duty limits"},
        "open_findings": [],
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    mic = manifest["microphone_and_adc"]
    hp = manifest["headset"]
    speaker = manifest["speaker"]
    tx = manifest["voice_tx_injection"]
    rail = manifest["main_rail_crosscheck"]
    cost = manifest["cost_delta_usd_at_100"]
    if russian:
        title = "# Электрическая проверка аудио"
        nav = "[English](audio-electrical-verification.md) · [На главную](../README.ru.md) · [Схемы](schematics.ru.md) · [Виртуальная проверка](virtual-verification.ru.md)"
        intro = "H3.3.2 проверяет весь аналоговый тракт: внутренний/гарнитурный микрофон и RX → ES8311 → гарнитура/динамик, плюс регулируемую подачу codec audio в SA518. Это расчёт серийных деталей; акустика, шум разведённой платы и RF immunity остаются измерениями H8."
        sections = f"""## Захват и микрофоны

- Независимые bias-фильтры дают каждой капсуле `{mic['independent_bias_supply_v']['min']}…{mic['independent_bias_supply_v']['max']} В`; замкнутый на землю TRS-контакт больше не просаживает внутренний микрофон.
- `33 кΩ` перед MIC1P/MIC1N убраны: они отнимали `{mic['removed_33kohm_loss_db']} dB`. Серийные `0 Ω` теперь повторяют референс ES8311, а PGA остаётся программируемым `0…30 dB`.
- Безопасный старт — `0 dB`; до HIL для громкого входа действует cap `21 dB`. Публичные пределы шума не заменяют измерение собранной платы.

## Гарнитура

Разъём — CTIA/AHJ, mono dual-ear + microphone, не stereo codec. Даже при консервативных `{hp['conservative_effective_coupling_uf_per_ear']} мкФ` эффективной ёмкости нижняя граница равна `{hp['high_pass_hz']['16_ohm']} Гц` для 16 Ω и `{hp['high_pass_hz']['32_ohm']} Гц` для 32 Ω: голос сохраняется, low bass проверяется физически. Detect-only P02 имеет минимум `{hp['no_plug_detect_high_fraction_min']}·VCC`; ток DC через вставленные 16-Ω наушники не выше `{hp['plugged_tip_bias_current_ma_max']} мА`.

## Динамик

В реальном углу `4 Ω −15% = {speaker['minimum_impedance_corner_ohm']} Ω` теоретический BTL-предел равен `{speaker['theoretical_btl_sine_power_w_max']} Вт`, ниже 2-Вт рейтинга динамика. PAM8302A требует до `{speaker['pam8302a_supply_current_ma_max']} мА`; ветка получает `{speaker['audio_branch_admission_ma']} мА`. При 85 °C расчётный junction `{speaker['amplifier_junction_c_at_85c_ambient']} °C`, но сам динамик допускает только 50 °C локально, поэтому выше этого порога playback аппаратно/программно mute, а остальные функции могут продолжаться по будущему H3.6 envelope. SD включается не раньше 10 мс после valid rail.

## Подача audio в SA518

`{tx['selected_top_resistor']}` вместе с 2,2 кΩ/10 нФ даёт `{tx['full_scale_injection_mvrms']['min']}…{tx['full_scale_injection_mvrms']['max']} мВ RMS` против опубликованной цели `{tx['sa518_modulation_target_mvrms']} мВ`. Калибровка идёт только вниз codec volume; выбор audio никогда не включает PTT.

## Перепроверка 3V3_MAIN

Исправленный worst case — `{rail['worst_profile_load_ma']} мА` из 2500 мА принятого режима и `{rail['hardware_reserve_percent']}%` до гарантированного hardware limit. Normal display/backlight теперь `{rail['normal_display_branch_ma']} мА`, audio — `{rail['audio_branch_ma']} мА`; fault-порог подсветки больше не считается рабочей нагрузкой.

Итоговая аналоговая конфигурация добавляет `{cost['total_delta_per_board']} USD` на устройство при количестве 100. **H3.3.2 проверено; текущий точный маркер — `H3.3.3`.**

[Машинный пакет H3-VRF32](../hardware/verification/generated/H3-VRF32-audio.json)."""
    else:
        title = "# Audio electrical verification"
        nav = "[Русский](audio-electrical-verification.ru.md) · [Home](../README.md) · [Schematics](schematics.md) · [Virtual verification](virtual-verification.md)"
        intro = "H3.3.2 checks the complete analog chain: internal/headset microphone and RX → ES8311 → headset/speaker, plus calibrated codec-audio injection into SA518. This is a serial-part calculation; routed-board noise, acoustics and RF immunity remain H8 measurements."
        sections = f"""## Capture and microphones

- Independent bias filters give each capsule `{mic['independent_bias_supply_v']['min']}…{mic['independent_bias_supply_v']['max']} V`; a grounded TRS sleeve no longer pulls down the internal microphone.
- The `33 kΩ` MIC1P/MIC1N parts are removed: they cost `{mic['removed_33kohm_loss_db']} dB`. Serial `0 Ω` links now follow the ES8311 reference while PGA remains programmable from `0…30 dB`.
- Safe startup is `0 dB`; loud-input gain is capped at `21 dB` until HIL. Public component noise limits do not replace an assembled-board measurement.

## Headset

The jack is CTIA/AHJ mono dual-ear plus microphone, not a stereo codec. Even with a conservative `{hp['conservative_effective_coupling_uf_per_ear']} uF` effective capacitor, the lower corner is `{hp['high_pass_hz']['16_ohm']} Hz` at 16 ohm and `{hp['high_pass_hz']['32_ohm']} Hz` at 32 ohm: voice is preserved while low bass remains physical. Detect-only P02 retains at least `{hp['no_plug_detect_high_fraction_min']}·VCC`; DC through inserted 16-ohm headphones is at most `{hp['plugged_tip_bias_current_ma_max']} mA`.

## Speaker

At the real `4 ohm −15% = {speaker['minimum_impedance_corner_ohm']} ohm` corner, the theoretical BTL ceiling is `{speaker['theoretical_btl_sine_power_w_max']} W`, below the speaker's 2-W rating. PAM8302A needs at most `{speaker['pam8302a_supply_current_ma_max']} mA`; the branch receives `{speaker['audio_branch_admission_ma']} mA`. Calculated junction at 85 C ambient is `{speaker['amplifier_junction_c_at_85c_ambient']} C`, but the speaker itself is limited to a 50 C local environment, so playback is muted above that threshold while later H3.6 governs the remaining product. SD is not released until at least 10 ms after rail validity.

## Codec audio into SA518

`{tx['selected_top_resistor']}` with 2.2 kohm/10 nF produces `{tx['full_scale_injection_mvrms']['min']}…{tx['full_scale_injection_mvrms']['max']} mVrms` against the published `{tx['sa518_modulation_target_mvrms']}-mV target. Calibration only turns codec volume down; selecting audio never asserts PTT.

## 3V3_MAIN cross-check

The corrected worst case is `{rail['worst_profile_load_ma']} mA` inside the 2500-mA admission and retains `{rail['hardware_reserve_percent']}%` to the guaranteed hardware limit. Normal display/backlight is now `{rail['normal_display_branch_ma']} mA`, audio is `{rail['audio_branch_ma']} mA`; a backlight fault threshold is no longer counted as an operating load.

The final analog configuration adds `{cost['total_delta_per_board']} USD` per unit at quantity 100. **H3.3.2 is verified; the exact current marker is `H3.3.3`.**

[Machine H3-VRF32 package](../hardware/verification/generated/H3-VRF32-audio.json)."""
    return "\n\n".join((title, nav, intro, sections)) + "\n"


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
    else:
        stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("stale H3.3.2 artifacts: " + ", ".join(stale))
            return 1
    print(f"ok: H3.3.2 reviewed; {manifest['review_summary']['checks']} checks, 0 unresolved findings, next H3.3.3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
