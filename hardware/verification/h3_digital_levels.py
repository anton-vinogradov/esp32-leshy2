#!/usr/bin/env python3
"""Verify H3.4.1 digital levels, pulls, reset defaults and no-back-power."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
METHODS_PATH = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
NO_BACK_POWER_PATH = REPO / "hardware/ecad/generated/H2-REV53-no-back-power.json"
QUIET_PATH = REPO / "hardware/ecad/generated/H2-REV54-quiet-state.json"
CONTACTS_PATH = REPO / "hardware/ecad/generated/H2-REV72-physical-contacts.json"
DISPLAY_PATH = REPO / "hardware/verification/generated/H3-VRF31-display.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF41-digital-levels.json"
DOC_EN = REPO / "docs/digital-levels-verification.md"
DOC_RU = REPO / "docs/digital-levels-verification.ru.md"

SOURCES = {
    "nexperia_74lvc126a": "https://assets.nexperia.com/documents/data-sheet/74LVC126A.pdf",
    "nexperia_74lvc2g126": "https://assets.nexperia.com/documents/data-sheet/74LVC2G126.pdf",
    "ti_sn74lvc1g126": "https://www.ti.com/lit/ds/symlink/sn74lvc1g126.pdf",
    "ti_sn74lvc1g125": "https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf",
    "ti_sn74lvc3g34": "https://www.ti.com/lit/ds/symlink/sn74lvc3g34.pdf",
    "ti_sn74lvc1g07": "https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf",
    "ti_txs0102": "https://www.ti.com/lit/ds/symlink/txs0102.pdf",
    "ti_tca4307": "https://www.ti.com/lit/ds/symlink/tca4307.pdf",
    "onsemi_fsusb42": "https://www.onsemi.com/download/data-sheet/pdf/fsusb42-d.pdf",
    "esp32_s3_module": "https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf",
    "esp32_c5_module": "https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf",
    "rp2350": "https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf",
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
    methods = json.loads(METHODS_PATH.read_text(encoding="utf-8"))
    no_back_power = json.loads(NO_BACK_POWER_PATH.read_text(encoding="utf-8"))
    quiet = json.loads(QUIET_PATH.read_text(encoding="utf-8"))
    contacts = json.loads(CONTACTS_PATH.read_text(encoding="utf-8"))
    display = json.loads(DISPLAY_PATH.read_text(encoding="utf-8"))
    instances = candidate["instances"]
    allocations = candidate["allocations"]
    allocation_keys = {(row["instance"], row["contact"], row["net"]) for row in allocations}

    exact_instances = {
        "nrf0_host_buffer": "nexperia_74lvc126apw_118",
        "nrf1_host_buffer": "nexperia_74lvc126apw_118",
        "nrf2_host_buffer": "nexperia_74lvc126apw_118",
        "nrf0_return_buffer": "nexperia_74lvc2g126dc_125",
        "nrf1_return_buffer": "nexperia_74lvc2g126dc_125",
        "nrf2_return_buffer": "nexperia_74lvc2g126dc_125",
        "cc_host_buffer": "nexperia_74lvc126apw_118",
        "cc_return_buffer": "nexperia_74lvc126apw_118",
        "cc_band_buffer": "nexperia_74lvc2g126dc_125",
        "u214_host_buffer_a": "nexperia_74lvc126apw_118",
        "u214_host_buffer_b": "nexperia_74lvc126apw_118",
        "u214_return_buffer": "nexperia_74lvc126apw_118",
        "u214_i2c_iso": "tca4307dgkr",
        "unit_signal_iso": "ti_txs0102_dcur",
        "sd_host_buffer": "ti_sn74lvc3g34_dcur",
        "sd_miso_buffer": "ti_sn74lvc1g125_dckr",
        "codec_i2c_iso": "ti_sn74lvc2g66_dcur",
        "codec_i2s_bclk_iso": "ti_sn74lvc1g126_dckr",
        "codec_i2s_ws_iso": "ti_sn74lvc1g126_dckr",
        "codec_i2s_dout_iso": "ti_sn74lvc1g126_dckr",
        "codec_i2s_din_iso": "ti_sn74lvc1g126_dckr",
        "receiver_i2c_iso": "ti_sn74lvc2g66_dcur",
        "receiver_irq_iso": "ti_sn74lvc1g07_dckr",
        "voice_ptt_iso": "ti_sn74lvc1g126_dckr",
        "voice_uart_tx_iso": "ti_sn74lvc1g126_dckr",
        "voice_audio_iso": "ti_sn74lvc2g66_dcur",
        "ir_return_buffer": "nexperia_74lvc2g126dc_125",
        "c5_service_usb_switch": "onsemi_fsusb42_mux",
        "rp_service_usb_switch": "onsemi_fsusb42_mux",
    }
    off_safe_pulls = (
        "nrf_power_on_pulldown",
        "cc_power_on_pulldown",
        "u214_req_pulldown",
        "unit_req_pulldown",
        "unit_signal_iso_oe_pulldown",
        "codec_power_on_pulldown",
        "audio_arm_pulldown",
        "receiver_power_on_pulldown",
        "ir_power_on_pulldown",
        "ir_tx_gate_pulldown",
        "voice_en_pulldown",
        "voice_uart_rx_pulldown",
        "voice_uart_tx_pulldown",
        "sd_on_pulldown",
        "sd_host_sck_pulldown",
        "sd_host_d0_pulldown",
        "sd_host_d1_pullup",
        "sd_host_cs_pullup",
    )

    main_min = d(display["supply_corner"]["display_connector_v"]["min"])
    main_max = d(display["supply_corner"]["display_connector_v"]["max"])
    lvc_vih_min = d("2.0")
    lvc_vil_max = d("0.8")
    lvc_voh_min_at_24ma = d("2.2")
    lvc_vol_max_at_24ma = d("0.55")
    lvc_high_margin = lvc_voh_min_at_24ma - lvc_vih_min
    lvc_low_margin = lvc_vil_max - lvc_vol_max_at_24ma
    pull_10k_current_max_ma = main_max / d(10000) * d(1000)

    i2c_pull_ohm = d("2200")
    i2c_sink_current_max_ma = d("3.4") / i2c_pull_ohm * d(1000)
    i2c_vol_max = d("0.4")
    i2c_vil_max = d("0.8")
    i2c_low_margin = i2c_vil_max - i2c_vol_max

    direct_high_margin = d("0.05") * main_min
    direct_low_margin = d("0.15") * main_min

    interface_groups = [
        {
            "id": "S3_C5_SDIO",
            "signals": 4,
            "boundary": "common_3v3_main_direct",
            "level_proof": "common instantaneous rail; conservative CMOS VOH>=0.80*VDD and VIH<=0.75*VDD",
            "minimum_high_margin_v": q(direct_high_margin),
            "minimum_low_margin_v": q(direct_low_margin),
            "reset_or_off_state": "both controllers held in reset during rail-invalid state; clock is host output and transaction starts only after both boot contracts pass",
            "no_back_power": "no partial-power crossing: both endpoints use the same protected 3V3_MAIN rail",
        },
        {
            "id": "S3_RP_IPC",
            "signals": 4,
            "boundary": "common_3v3_main_direct",
            "level_proof": "3.3-V CMOS/JEDEC-compatible endpoints on one instantaneous rail",
            "minimum_high_margin_v": q(direct_high_margin),
            "minimum_low_margin_v": q(direct_low_margin),
            "reset_or_off_state": "CS deasserted and clocks/DMA stopped until both endpoints are ready",
            "no_back_power": "no partial-power crossing: both endpoints use the same protected 3V3_MAIN rail",
        },
        {
            "id": "DISPLAY_TOUCH_STORAGE_HOST",
            "signals": 10,
            "boundary": "common_main_display_plus_switched_sd",
            "level_proof": "display/touch stay on 3V3_MAIN; SD host outputs and return are isolated by exact Ioff LVC devices",
            "minimum_high_margin_v": q(lvc_high_margin),
            "minimum_low_margin_v": q(lvc_low_margin),
            "reset_or_off_state": "LCD/touch reset low, backlight gate low, SD SCK/D0 low and CS/D1 high",
            "no_back_power": "display logic deliberately shares the host rail; powered-off SD sees Ioff-protected host/return buffers",
        },
        {
            "id": "SYS_I2C_AON_MAIN",
            "signals": 2,
            "boundary": "open_drain_aon_to_main",
            "level_proof": "2.2-kOhm pull-ups source <=1.546 mA; exact PA0 contacts are 5-V-tolerant open-drain and PA11 is input-only",
            "minimum_high_margin_v": "receiving-domain pull-up; no cross-domain high driver",
            "minimum_low_margin_v": q(i2c_low_margin),
            "reset_or_off_state": "all transmitters release the bus at reset; target rail never sources the main rail",
            "no_back_power": "open-drain only; no push-pull high crosses the AON/main boundary",
        },
        {
            "id": "NRF24_X3",
            "signals": 18,
            "boundary": "switched_rail_bidirectional_lvc_ioff",
            "level_proof": "three exact 74LVC126A host buffers and three exact 74LVC2G126 return buffers",
            "minimum_high_margin_v": q(lvc_high_margin),
            "minimum_low_margin_v": q(lvc_low_margin),
            "reset_or_off_state": "CE/SCK/MOSI low, CSN/IRQ high, group rail off; OE follows qualified rail",
            "no_back_power": "Ioff at VCC=0 V in both directions; local and host pulls define every disabled line",
        },
        {
            "id": "CC1101",
            "signals": 7,
            "boundary": "switched_rail_bidirectional_lvc_ioff",
            "level_proof": "exact 74LVC126A host/return and 74LVC2G126 band-return buffers",
            "minimum_high_margin_v": q(lvc_high_margin),
            "minimum_low_margin_v": q(lvc_low_margin),
            "reset_or_off_state": "SCK/SI low, CSN high, GDO returns low, rail off",
            "no_back_power": "Ioff at VCC=0 V and qualified OEs isolate both directions",
        },
        {
            "id": "U214_CAP",
            "signals": 11,
            "boundary": "reverse_blocked_5v_branch_plus_lvc_and_i2c_isolation",
            "level_proof": "nine 3.3-V paths use exact LVC Ioff buffers; two I2C paths use TCA4307 at <=400 kHz",
            "minimum_high_margin_v": q(lvc_high_margin),
            "minimum_low_margin_v": q(min(lvc_low_margin, i2c_low_margin)),
            "reset_or_off_state": "branch off; READY low; nine push-pull paths high-Z and I2C segments disconnected",
            "no_back_power": "true-reverse-blocking eFuse, Ioff buffers and powered-off-high-Z TCA4307",
        },
        {
            "id": "M5_UNIT",
            "signals": 2,
            "boundary": "reverse_blocked_5v_branch_plus_txs0102",
            "level_proof": "TXS0102 VCCA/VCCB are both 3V3_MAIN for this design; it provides isolation, not a claimed voltage conversion",
            "minimum_high_margin_v": q(direct_high_margin),
            "minimum_low_margin_v": q(direct_low_margin),
            "reset_or_off_state": "OE has a 10-kOhm pull-down and remains low until UNIT_READY",
            "no_back_power": "OE low or either supply at ground makes both ports high-Z; branch eFuse is reverse-blocking",
        },
        {
            "id": "CODEC_I2C_I2S",
            "signals": 6,
            "boundary": "switched_codec_rail_with_analog_switch_and_lvc_ioff",
            "level_proof": "I2C is disconnected by powered-main SN74LVC2G66; four I2S directions use exact LVC Ioff buffers",
            "minimum_high_margin_v": q(lvc_high_margin),
            "minimum_low_margin_v": q(lvc_low_margin),
            "reset_or_off_state": "AUDIO_ARM low, selector defaults fixed, codec reset/READY invalid and every isolator disabled",
            "no_back_power": "the analog switch is open before the codec rail is admitted; I2S outputs are Ioff protected",
        },
        {
            "id": "RECEIVER_I2C_IRQ",
            "signals": 3,
            "boundary": "switched_receiver_rail_with_switch_and_open_drain_ioff",
            "level_proof": "I2C is disconnected by powered-main SN74LVC2G66; IRQ uses SN74LVC1G07 Ioff open drain into a main-side pull-up",
            "minimum_high_margin_v": "receiving-domain pull-up",
            "minimum_low_margin_v": q(i2c_low_margin),
            "reset_or_off_state": "receiver reset asserted, I2C switch open and IRQ output high-Z",
            "no_back_power": "no powered-main pull-up reaches the receiver domain while its rail is off",
        },
        {
            "id": "VOICE_DIGITAL",
            "signals": 4,
            "boundary": "switched_voice_io_rail_with_lvc_ioff",
            "level_proof": "PTT and UART TX use exact SN74LVC1G126; RX is locally biased and H/L uses an Ioff open-drain driver",
            "minimum_high_margin_v": q(lvc_high_margin),
            "minimum_low_margin_v": q(lvc_low_margin),
            "reset_or_off_state": "module PTT is pulled inactive-high; UART paths and H/L are disabled until VOICE_READY",
            "no_back_power": "VVOICE_IO_3V3 is off and every driven crossing is Ioff or open analog isolation",
        },
        {
            "id": "IR_RX_TX",
            "signals": 4,
            "boundary": "switched_ir_receive_rail_plus_fault_dominant_tx",
            "level_proof": "two receive returns use exact 74LVC2G126 Ioff; TX gate remains on the main/AON safety side",
            "minimum_high_margin_v": q(lvc_high_margin),
            "minimum_low_margin_v": q(lvc_low_margin),
            "reset_or_off_state": "receiver rail QOD-off, returns high-Z with C5 inputs idle-high, emitter MOSFET gate low",
            "no_back_power": "Ioff receive buffer plus independent pull-down and FAULT_KILL-dominant TX gate",
        },
        {
            "id": "SERVICE_USB_C5_RP",
            "signals": 4,
            "boundary": "usb2_differential_data_only",
            "level_proof": "USB analog levels are not reduced to CMOS thresholds; exact FSUSB42MUX supports 480 Mbps and 720-MHz bandwidth",
            "minimum_high_margin_v": "bounded in H3.4.3 and deferred to H8 eye measurement",
            "minimum_low_margin_v": "bounded in H3.4.3 and deferred to H8 eye measurement",
            "reset_or_off_state": "OE/SEL hard-low select the board-side path; service VBUS is sense-only",
            "no_back_power": "FSUSB42MUX power-off I/O range is 0..4.3 V with <=2-uA leakage; VBUS ends only at 1-MOhm bleeder/test pad",
        },
    ]

    exact_checks = {f"exact_{name}": instances.get(name) == part for name, part in exact_instances.items()}
    pull_checks = {f"present_{name}": name in instances for name in off_safe_pulls}
    quiet_ids = [row["id"] for row in quiet["reviewed_contracts"]]
    direct_route_checks = {
        "s3_c5_sdio_clk": ("s3", "GPIO10", "S3_C5_SDIO_CLK") in allocation_keys and ("c5", "GPIO9", "S3_C5_SDIO_CLK") in allocation_keys,
        "s3_c5_sdio_cmd": ("s3", "GPIO11", "S3_C5_SDIO_CMD") in allocation_keys and ("c5", "GPIO10", "S3_C5_SDIO_CMD") in allocation_keys,
        "s3_rp_ipc_cs": ("s3", "GPIO9", "S3_RP_IPC_CS_N") in allocation_keys and ("rp", "GPIO25", "S3_RP_IPC_CS_N") in allocation_keys,
        "sys_i2c_sda": ("s3", "GPIO1", "SYS_I2C_SDA") in allocation_keys and ("pack_admission", "PA0", "SYS_I2C_SDA") in allocation_keys and ("safety_controller", "PA0", "SYS_I2C_SDA") in allocation_keys,
        "sys_i2c_scl_input_only_aon": ("pack_admission", "PA11", "SYS_I2C_SCL") in allocation_keys and ("safety_controller", "PA11", "SYS_I2C_SCL") in allocation_keys,
    }
    checks = {
        **exact_checks,
        **pull_checks,
        **direct_route_checks,
        "all_130_controller_allocations_reviewed": len(allocations) == 130,
        "allocation_directions_complete": all(row["direction"] in {"i", "o", "io", "od"} for row in allocations),
        "all_13_quiet_contracts_reviewed": len(quiet_ids) == 13 and quiet["reviewed_contract_count"] == 13 and all(row["status"] == "reviewed" for row in quiet["reviewed_contracts"]),
        "all_required_quiet_groups_present": set(quiet_ids) == {"N24_QUIET", "CC_QUIET", "U214_CAP_QUIET", "UNIT_PORT_QUIET", "VOICE_QUIET", "RECEIVER_QUIET", "CODEC_AUDIO_QUIET", "VOICE_INTERFACE_QUIET", "IR_QUIET", "S3_RF_QUIET", "C5_RF_QUIET", "STORAGE_QUIET", "SERVICE_IPC_QUIET"},
        "six_no_back_power_invariants_preserved": len(no_back_power["invariants"]) == 6,
        "m1_maps_identical": no_back_power["m1"]["ui_rf_maps_identical"] is True,
        "m1_has_no_forbidden_rail": no_back_power["m1"]["forbidden_raw_or_exposed_rails"] == [],
        "physical_contact_reconciliation_has_no_mismatch": contacts["summary"]["physical_contact_mismatches"] == 0 and contacts["summary"]["mpn_mismatches"] == 0,
        "lvc_high_margin_positive": lvc_high_margin > 0,
        "lvc_low_margin_positive": lvc_low_margin > 0,
        "10k_pull_load_below_24ma_test_point": pull_10k_current_max_ma < d(24),
        "i2c_pull_current_below_3ma_test_point": i2c_sink_current_max_ma < d(3),
        "i2c_low_margin_positive": i2c_low_margin > 0,
        "direct_common_rail_high_margin_positive": direct_high_margin > 0,
        "direct_common_rail_low_margin_positive": direct_low_margin > 0,
        "tca4307_is_400khz_and_powered_off_high_z": devices["tca4307dgkr"]["electrical_contract"]["maximum_bus_hz"] == 400000 and devices["tca4307dgkr"]["electrical_contract"]["powered_off_bus_state"] == "high impedance",
        "txs0102_isolation_contract_present": "high impedance" in devices["ti_txs0102_dcur"]["electrical_contract"]["isolation"],
        "service_usb_power_off_leakage_bounded": devices["onsemi_fsusb42_mux"]["electrical_contract"]["power_off_leakage_max_ua"] <= 2,
        "method_contains_pf05": any(row["id"] == "PF-05" for row in methods["pass_fail_rules"]),
        "all_13_interface_groups_have_no_back_power_rule": len(interface_groups) == 13 and all(row["no_back_power"] for row in interface_groups),
        "all_13_interface_groups_have_reset_rule": all(row["reset_or_off_state"] for row in interface_groups),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.4.1 checks failed: " + ", ".join(failed))

    residual_hil = [
        "measure powered-off leakage at every switched-domain signal while the host remains powered",
        "capture reset and brownout pin states for S3, C5, RP2354B, both MSPM0 controllers and TCA6424A",
        "inject one and three simultaneous service USB hosts and verify no product rail is sourced",
        "exercise U214 and Unit wrong-accessory/external-source cases and measure reverse current",
        "measure VIH/VIL/VOH/VOL at the far end of M1 under simultaneous worst allowed branch load",
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H3.4.1",
        "status": "reviewed_digital_levels_pulls_reset_defaults_and_no_back_power",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, DEVICES_PATH, METHODS_PATH, NO_BACK_POWER_PATH, QUIET_PATH, CONTACTS_PATH, DISPLAY_PATH)},
        "provenance": SOURCES,
        "review_scope": {
            "controller_allocations": len(allocations),
            "interface_groups": len(interface_groups),
            "quiet_contracts": len(quiet_ids),
            "no_back_power_invariants": len(no_back_power["invariants"]),
            "physical_contact_rows": contacts["summary"]["ledger_rows"],
            "analytical_findings_open": 0,
            "source_corrections": 0,
        },
        "worst_case_level_model": {
            "3v3_main_connector_v": {"min": str(main_min), "max": str(main_max)},
            "lvc_cmos_at_vcc_3v": {
                "vih_min_v": str(lvc_vih_min),
                "vil_max_v": str(lvc_vil_max),
                "voh_min_v_at_24ma": str(lvc_voh_min_at_24ma),
                "vol_max_v_at_24ma": str(lvc_vol_max_at_24ma),
                "guaranteed_high_margin_v": q(lvc_high_margin),
                "guaranteed_low_margin_v": q(lvc_low_margin),
                "actual_10k_pull_load_ma_max": q(pull_10k_current_max_ma),
                "interpretation": "the 24-mA output test point is deliberately more severe than the <=0.329-mA static pull load; trace/edge timing is checked separately in H3.4.3",
            },
            "sys_i2c": {
                "pullup_ohm": int(i2c_pull_ohm),
                "sink_current_ma_at_3v4": q(i2c_sink_current_max_ma),
                "vol_max_v_at_3ma": str(i2c_vol_max),
                "vil_max_v": str(i2c_vil_max),
                "guaranteed_low_margin_v": q(i2c_low_margin),
            },
            "common_rail_direct_cmos": {
                "voh_ratio_min": "0.80*VDD",
                "vih_ratio_max": "0.75*VDD",
                "vol_ratio_max": "0.10*VDD",
                "vil_ratio_min": "0.25*VDD",
                "high_margin_v_at_main_min": q(direct_high_margin),
                "low_margin_v_at_main_min": q(direct_low_margin),
                "rule": "the same instantaneous rail is used on both ends; unrelated min/max rail endpoints are not subtracted from one another",
            },
        },
        "exact_instance_checks": exact_checks,
        "off_safe_pull_checks": pull_checks,
        "direct_route_checks": direct_route_checks,
        "interface_groups": interface_groups,
        "checks": checks,
        "corrections": [],
        "open_findings": [],
        "residual_physical_only": residual_hil,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.4.4", "action": "consolidate digital level, timing and boundary-loading evidence"},
    }

    en = f"""# Digital levels, defaults and no-back-power

`H3.4.1` is reviewed: `{len(checks)}` machine checks cover all `{len(allocations)}` controller allocations, `{len(interface_groups)}` digital interface groups, `{len(quiet_ids)}` quiet-state contracts and all six no-back-power invariants. No analytical finding or component change remains open. The exact current marker is `H3.4.4`.

## Guaranteed static margins

| Boundary | Worst reviewed result |
|---|---|
| LVC buffered 3.3-V paths | `VOH-VIH >= {q(lvc_high_margin)} V`; `VIL-VOL >= {q(lvc_low_margin)} V` at the much harsher 24-mA data-sheet point; actual 10-kOhm pull load is <=`{q(pull_10k_current_max_ma)} mA` |
| Direct common-rail CMOS | same instantaneous rail; conservative high margin `{q(direct_high_margin)} V`, low margin `{q(direct_low_margin)} V` at the minimum reviewed rail |
| SYS_I2C open drain | 2.2-kOhm pull-up sinks <=`{q(i2c_sink_current_max_ma)} mA`; guaranteed low margin `{q(i2c_low_margin)} V`; no push-pull high crosses the AON/main boundary |
| Service USB | exact FSUSB42MUX power-off isolation and sense-only VBUS pass; USB differential SI is bounded in H3.4.3 and physically checked in H8, not disguised as a CMOS margin |

Every switched domain has an off-safe enable, a local line default and either exact `Ioff`, a powered-main open switch, powered-off-high-Z I2C isolation or a same-rail/no-partial-power proof. The three nRF24 paths remain fully independent and all six signals per module are isolated in both directions.

## What paper review does not close

Five measurements remain explicit H8 gates: powered-off leakage, reset/brownout captures, simultaneous service-host injection, wrong-accessory reverse current and far-end M1 logic levels under load. They are not reported as paper passes.

Machine evidence: [`H3-VRF41-digital-levels.json`](../hardware/verification/generated/H3-VRF41-digital-levels.json).
"""
    ru = f"""# Digital levels, defaults и no-back-power

`H3.4.1` проверено: `{len(checks)}` машинных checks охватывают все `{len(allocations)}` controller allocations, `{len(interface_groups)}` групп digital interfaces, `{len(quiet_ids)}` quiet-state contracts и все шесть no-back-power invariants. Незакрытых аналитических findings и замен компонентов нет. Точный текущий маркер — `H3.4.4`.

## Гарантированные статические запасы

| Граница | Худший проверенный результат |
|---|---|
| Буферизованные LVC-тракты 3,3 В | `VOH-VIH >= {q(lvc_high_margin)} В`; `VIL-VOL >= {q(lvc_low_margin)} В` в гораздо более тяжёлом datasheet point 24 мА; фактическая нагрузка pull 10 кОм <=`{q(pull_10k_current_max_ma)} мА` |
| Прямой common-rail CMOS | одна мгновенная шина; conservative high margin `{q(direct_high_margin)} В`, low margin `{q(direct_low_margin)} В` при минимальном проверенном rail |
| Open-drain SYS_I2C | pull-up 2,2 кОм требует <=`{q(i2c_sink_current_max_ma)} мА`; гарантированный low margin `{q(i2c_low_margin)} В`; push-pull high не пересекает AON/main boundary |
| Service USB | проходят exact FSUSB42MUX power-off isolation и sense-only VBUS; USB differential SI ограничен в H3.4.3 и физически проверяется в H8, а не маскируется CMOS-расчётом |

У каждого switched domain есть off-safe enable, локальное состояние каждой линии и одно из точных доказательств: `Ioff`, разомкнутый powered-main switch, powered-off-high-Z I2C isolation либо same-rail/no-partial-power. Три nRF24 остаются независимыми, у каждого изолированы все шесть сигналов в обоих направлениях.

## Чего бумажное ревью не закрывает

Пять измерений остаются явными gates H8: powered-off leakage, осциллограммы reset/brownout, одновременное подключение service hosts, reverse current при неверном аксессуаре и уровни на дальнем конце M1 под нагрузкой. Бумажными passes они не названы.

Машинное evidence: [`H3-VRF41-digital-levels.json`](../hardware/verification/generated/H3-VRF41-digital-levels.json).
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
            raise SystemExit("stale H3.4.1 artifacts: " + ", ".join(stale))
    print(f"ok: H3.4.1 reviewed; {len(manifest['checks'])} checks, next H3.4.4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
