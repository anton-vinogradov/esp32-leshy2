#!/usr/bin/env python3
"""Calculate H3.1.2 worst-case DC load and protection margin for every rail."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
STATES = REPO / "hardware/verification/generated/H3-VRF11-power-state-register.json"
METHODS = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
CANDIDATE = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES = REPO / "hardware/architecture/devices.json"
POWER_REVIEW = REPO / "hardware/ecad/generated/H2-REV51-power-paths.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
DOC_EN = REPO / "docs/dc-power-budget.md"
DOC_RU = REPO / "docs/dc-power-budget.ru.md"


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Every value below is either a published maximum, a protection threshold, or
# an explicit product admission limit.  Typical values never prove a pass.
PROVENANCE = [
    {
        "id": "SRC-S3-PEAK",
        "value": "340 mA",
        "use": "ESP32-S3 hard rail reservation in every SUPPORT_WORST profile",
        "basis": "published 802.11b 1-Mbit/s 21-dBm peak; also bounds non-RF support operation",
        "url": "https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf",
    },
    {
        "id": "SRC-C5-PEAK",
        "value": "408 mA",
        "use": "ESP32-C5 hard rail reservation in every SUPPORT_WORST profile",
        "basis": "published 5-GHz 802.11a 6-Mbit/s 18-dBm peak",
        "url": "https://documentation.espressif.com/esp32-c5_datasheet_en.html",
    },
    {
        "id": "SRC-RP-BOUND",
        "value": "250 mA",
        "use": "RP2354B core, stacked flash and active PIO/DMA/I/O reservation",
        "basis": "200-mA internal core-regulator maximum plus an explicit 50-mA I/O/flash allowance",
        "url": "https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf",
    },
    {
        "id": "SRC-DISPLAY-BOUND",
        "value": "294 mA",
        "use": "display/touch logic plus maximum protected backlight branch",
        "basis": "60-mA logic admission plus the existing 234-mA maximum backlight eFuse corner",
        "url": "https://www.ti.com/lit/ds/symlink/tps2553.pdf",
    },
    {
        "id": "SRC-SD-BOUND",
        "value": "500 mA",
        "use": "qualified microSD medium and socket path",
        "basis": "exact DM3AT-SF-PEJM5 connector rating; media exceeding the bound is not admitted",
        "url": "https://www.hirose.com/product/document?clcode=CL0609-0032-3-00&productname=DM3AT-SF-PEJM5&series=DM3&documenttype=Catalog&lang=en&documentid=D31627_en",
    },
    {
        "id": "SRC-AUDIO-BOUND",
        "value": "500 mA",
        "use": "codec, selectors and maximum admitted speaker playback",
        "basis": "accepted product branch ceiling; it exceeds the PAM8302A 8-ohm 3.6-V curve",
        "url": "https://www.diodes.com/datasheet/download/PAM8302A.pdf",
    },
    {
        "id": "SRC-NRF24-MAX",
        "value": "14 mA per module",
        "use": "each E01-ML01IPX in PTX; all three may transmit concurrently",
        "basis": "Ebyte published maximum TX current at 0 dBm",
        "url": "https://www.ebyte.com/product/47.html",
    },
    {
        "id": "SRC-SA518-MAX",
        "value": "900 mA",
        "use": "SA518 high-power 1-W TX from VVOICE_4V",
        "basis": "NiceRF published maximum at 4.0 V",
        "url": "https://www.nicerf.com/upload/20260430/391f11abcc1d835ac5ed151613fdae68.pdf",
    },
    {
        "id": "SRC-EXT-EFUSE",
        "value": "1.632 to 2.035 A",
        "use": "each exposed 5-V branch after H3 correction to 1.82-kohm RILM",
        "basis": "3334/R equation, 1% resistor and +/-10% TPS25947 ILIM accuracy",
        "url": "https://www.ti.com/lit/ds/symlink/tps25947.pdf",
    },
    {
        "id": "SRC-AON-EFUSE",
        "value": "165 mA conservative minimum",
        "use": "AON_SAFE_3V3 protected continuous capability",
        "basis": "208-mA nominal from 240-kohm RILIM, derated by the published full-PVT +/-20% accuracy",
        "url": "https://www.ti.com/lit/ds/symlink/tps25961.pdf",
    },
    {
        "id": "SRC-CONVERTERS",
        "value": "AON 0.3 A; application rails 4 A each",
        "use": "converter output-current ceilings",
        "basis": "TPS629203 and TPS564252 manufacturer ratings",
        "url": "https://www.ti.com/product/TPS564252",
    },
]


RAILS = {
    "AON_SAFE_3V3": {
        "voltage_v": d("3.3"),
        "converter_min_a": d("0.300"),
        "protection_min_a": d("0.165"),
        "accepted_continuous_a": d("0.165"),
        "protection": "TPS25961DRVR, 240-kohm RILIM, conservative -20% full-PVT corner",
    },
    "3V3_MAIN": {
        "voltage_v": d("3.222"),
        "converter_min_a": d("4.000"),
        "protection_min_a": d("3.200"),
        "accepted_continuous_a": d("2.500"),
        "protection": "TPS25974LRPWR guaranteed 3.2-A minimum circuit-breaker corner",
    },
    "VVOICE_4V": {
        "voltage_v": d("4.0"),
        "converter_min_a": d("4.000"),
        "protection_min_a": d("1.550"),
        "accepted_continuous_a": d("1.250"),
        "protection": "TPS25974LRPWR guaranteed 1.55-A minimum circuit-breaker corner",
    },
    "5V_EXT_ACTIVE_BRANCH": {
        "voltage_v": d("5.0"),
        "converter_min_a": d("4.000"),
        "protection_min_a": d("1.632"),
        "accepted_continuous_a": d("1.250"),
        "protection": "TPS259470LRPWR plus corrected 1.82-kohm RILM; U214 and Unit branches are mutually exclusive",
    },
}


AON_FIXED_MA = {
    "pd_controller_vin": d("6.0"),
    "two_mspm0_safety_controllers": d("30.0"),
    "supervisors_watchdog_logic_comparators_and_pullups": d("18.0"),
    "ten_front_indicators_at_2k2": d("15.0"),
    "two_native_rf_ltc5532_detectors": d("1.4"),
    "ir_optical_evidence_amplifier_and_bias": d("2.0"),
}

AON_GROUP_MA = {
    "NONE": d("0"),
    "S3_RF": d("0"),
    "C5_RF": d("0"),
    "NRF24": d("17.1"),
    "CC1101": d("5.7"),
    "VOICE": d("5.7"),
    "IR": d("0"),
    "LORA_CAP": d("0"),
    "M5_UNIT": d("0"),
    "BROADCAST_RX": d("0"),
}

MAIN_SUPPORT_MA = {
    "SUPPORT_IDLE": {
        "s3_compute_and_memory": d("100"),
        "c5_compute_no_active_rf": d("65"),
        "rp2354_pio_dma_and_flash": d("100"),
        "display_touch_and_backlight": d("80"),
        "micro_sd": d("0"),
        "audio_codec_and_speaker": d("10"),
        "remaining_named_main_logic_controls_and_bias": d("40"),
    },
    "SUPPORT_WORST": {
        "s3_compute_memory_and_rf_peak_reservation": d("340"),
        "c5_compute_memory_and_5ghz_peak_reservation": d("408"),
        "rp2354_pio_dma_io_and_stacked_flash": d("250"),
        "display_touch_and_max_protected_backlight": d("294"),
        "qualified_micro_sd_at_socket_limit": d("500"),
        "codec_selectors_and_max_speaker_playback": d("500"),
        "remaining_named_main_logic_controls_pullups_and_isolators": d("100"),
    },
}

MAIN_GROUP_MA = {
    "NONE": d("0"),
    "S3_RF": d("0"),
    "C5_RF": d("0"),
    "NRF24": d("42"),
    "CC1101": d("35"),
    "VOICE": d("20"),
    "IR": d("70"),
    "LORA_CAP": d("20"),
    "M5_UNIT": d("20"),
    "BROADCAST_RX": d("30"),
}

VOICE_GROUP_MA = {"VOICE": d("900")}
EXT_GROUP_MA = {"LORA_CAP": d("1250"), "M5_UNIT": d("1250")}


def rail_row(rail: str, load_ma: Decimal) -> dict:
    c = RAILS[rail]
    load_a = load_ma / d(1000)
    effective_min = min(c["converter_min_a"], c["protection_min_a"])
    reserve_pct = (effective_min / load_a - d(1)) * d(100) if load_a else d("9999")
    accepted_margin_ma = (c["accepted_continuous_a"] - load_a) * d(1000)
    status = "pass" if reserve_pct >= d(25) and accepted_margin_ma >= 0 else "fail"
    return {
        "rail": rail,
        "load_ma": q(load_ma),
        "output_power_w": q(load_a * c["voltage_v"]),
        "converter_min_a": q(c["converter_min_a"]),
        "protection_min_a": q(c["protection_min_a"]),
        "effective_hardware_min_a": q(effective_min),
        "accepted_continuous_a": q(c["accepted_continuous_a"]),
        "accepted_envelope_margin_ma": q(accepted_margin_ma),
        "hardware_reserve_percent": q(reserve_pct),
        "status": status,
    }


def profile_load(profile: dict) -> dict:
    group = profile["signal_group"]
    support = profile["support_profile"]
    aon_ma = sum(AON_FIXED_MA.values(), d(0)) + AON_GROUP_MA[group]
    main_parts = dict(MAIN_SUPPORT_MA[support])
    main_parts[f"active_group_{group.lower()}"] = MAIN_GROUP_MA[group]
    main_ma = sum(main_parts.values(), d(0))
    voice_ma = VOICE_GROUP_MA.get(group, d(0))
    ext_ma = EXT_GROUP_MA.get(group, d(0))
    rails = [
        rail_row("AON_SAFE_3V3", aon_ma),
        rail_row("3V3_MAIN", main_ma),
        rail_row("VVOICE_4V", voice_ma),
        rail_row("5V_EXT_ACTIVE_BRANCH", ext_ma),
    ]
    return {
        **profile,
        "loads_ma": {
            "AON_SAFE_3V3": q(aon_ma),
            "3V3_MAIN": q(main_ma),
            "VVOICE_4V": q(voice_ma),
            "5V_EXT_ACTIVE_BRANCH": q(ext_ma),
        },
        "rail_results": rails,
        "status": "pass" if all(row["status"] == "pass" for row in rails) else "fail",
    }


def build() -> tuple[dict[Path, str], dict]:
    states = json.loads(STATES.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    if states.get("status") != "reviewed_all_legal_source_charge_and_operating_states_enumerated":
        raise ValueError("H3.1.1 is not reviewed")
    if not any(rule["id"] == "PF-02" for rule in methods["pass_fail_rules"]):
        raise ValueError("PF-02 reserve rule is missing")
    profiles = [profile_load(profile) for profile in states["operating_profiles"]]
    failures = [profile for profile in profiles if profile["status"] != "pass"]
    worst_by_rail = {}
    for rail in RAILS:
        candidates = [
            (d(profile["loads_ma"][rail]), profile)
            for profile in profiles
        ]
        load, profile = max(candidates, key=lambda pair: pair[0])
        result = next(row for row in profile["rail_results"] if row["rail"] == rail)
        worst_by_rail[rail] = {
            "profile": f"{profile['signal_group']}/{profile['group_mode']}/{profile['support_profile']}",
            **result,
        }
    if failures:
        raise ValueError(f"DC rail margin failures remain: {len(failures)}")
    manifest = {
        "schema_version": 1,
        "stage": "H3.1.2",
        "status": "reviewed_all_rail_loads_and_protection_margins_pass_after_ext_5v_rilm_correction",
        "method": "dc_network plus Decimal interval corners; PF-02 >=25% steady hardware reserve",
        "source_hashes": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (STATES, METHODS, CANDIDATE, DEVICES, POWER_REVIEW)
        },
        "provenance": PROVENANCE,
        "rail_capabilities": {
            rail: {key: q(value) if isinstance(value, Decimal) else value for key, value in contract.items()}
            for rail, contract in RAILS.items()
        },
        "load_model": {
            "aon_fixed_ma": {key: q(value) for key, value in AON_FIXED_MA.items()},
            "aon_group_ma": {key: q(value) for key, value in AON_GROUP_MA.items()},
            "main_support_ma": {
                key: {name: q(value) for name, value in values.items()}
                for key, values in MAIN_SUPPORT_MA.items()
            },
            "main_group_ma": {key: q(value) for key, value in MAIN_GROUP_MA.items()},
            "voice_group_ma": {key: q(value) for key, value in VOICE_GROUP_MA.items()},
            "external_group_ma": {key: q(value) for key, value in EXT_GROUP_MA.items()},
            "anti_hidden_allowance": "the 100-mA main miscellaneous line explicitly owns level shifters, I/O expanders, supervisors, load-switch quiescent current, reset/default pull networks and control indicators not already present in a named major branch; H8 must measure it as one ledger-backed aggregate",
        },
        "profiles": profiles,
        "worst_by_rail": worst_by_rail,
        "corrections": [
            {
                "id": "H3.1.2-F01",
                "finding": "2.21-kohm external-branch RILM produced only 1.358 A at the guaranteed low corner, below the 1.5625-A PF-02 requirement for a 1.25-A port",
                "correction": "both U214 and native-Unit eFuses now use active/orderable Yageo RC0402FR-071K82L; guaranteed low corner is 1.632 A and high corner is 2.035 A",
                "functional_effect": "restores >=30.6% steady reserve and preserves the bounded 2-A post-start transient without changing the connector contract",
                "cost_effect_usd_at_100": "0.0000 versus the replaced resistor at the same published $0.0097 tier",
            }
        ],
        "summary": {
            "operating_profiles": len(profiles),
            "rail_profiles_evaluated": len(profiles) * len(RAILS),
            "failed_profiles": len(failures),
            "unresolved_numeric_inputs": 0,
            "corrected_findings": 1,
            "minimum_hardware_reserve_percent": min(
                d(row["hardware_reserve_percent"])
                for profile in profiles
                for row in profile["rail_results"]
                if d(row["load_ma"]) > 0
            ).quantize(d("0.001")).to_eng_string(),
        },
        "next": {
            "stage": "H3.1.3",
            "action": "apply rail loads to every source/charge state and calculate input, cell and steady dissipation envelopes",
        },
        "residual_physical_gates": [
            "H3.2 load-step, inrush and protection timing",
            "H6 copper, placement and converter-loop thermal layout",
            "H8 measured rail currents with display, selected microSD, speaker, every RF group and both exposed-port profiles",
        ],
        "open_findings": [],
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    rows = []
    for rail, result in manifest["worst_by_rail"].items():
        rows.append(
            f"| `{rail}` | {result['load_ma']} mA | {result['effective_hardware_min_a']} A | "
            f"{result['hardware_reserve_percent']}% | {result['accepted_envelope_margin_ma']} mA | `{result['profile']}` |"
        )
    table = "\n".join(rows)
    if russian:
        title = "# Постоянный бюджет питания"
        nav = "[English](dc-power-budget.md) · [На главную](../README.ru.md) · [Состояния](power-state-register.ru.md) · [Методы](verification-methods.ru.md)"
        intro = "H3.1.2 привязал численный ток к каждому из 50 профилей нагрузки. Для worst case оба ESP резервируются по опубликованному RF-пику, три nRF24 действительно считаются одновременно, а типовые значения не доказывают прохождение."
        headers = "| Шина | Худшая нагрузка | Минимум железа | Запас железа | До принятого рабочего envelope | Худший профиль |\n|---|---:|---:|---:|---:|---|"
        finding_h = "## Исправление по результату расчёта"
        finding = "Оба внешних eFuse получили серийный `Yageo RC0402FR-071K82L` 1,82 кΩ вместо 2,21 кΩ. Гарантированный минимум порога вырос с 1,358 до 1,632 А: запас над портом 1,25 А теперь 30,6%, короткий 2-А импульс сохранён. Цена на проверенном тираже 100 не изменилась."
        boundary_h = "## Что результат означает"
        boundary = "Все четыре DC-шины проходят правило 25% по минимальному hardware threshold. Самый тесный рабочий envelope — `3V3_MAIN`: консервативные 2,462 А оставляют 38 мА до принятого требования 2,5 А, но 30,0% до гарантированного 3,2-А порога защиты. Поэтому H3.2 обязан проверить ступень нагрузки, а H8 — измерить реальную сумму."
        marker = "**Статус:** `H3.1.2` завершено и проверено; текущий точный маркер — `H3.3.2`."
        evidence = "[Полный машинный расчёт](../hardware/verification/generated/H3-VRF12-dc-budget.json)."
    else:
        title = "# Steady DC power budget"
        nav = "[Русский](dc-power-budget.ru.md) · [Home](../README.md) · [States](power-state-register.md) · [Methods](verification-methods.md)"
        intro = "H3.1.2 attaches a numeric current to all 50 load profiles. Both ESP devices reserve their published RF peak in the worst case, all three nRF24 radios are genuinely concurrent, and typical values never prove a pass."
        headers = "| Rail | Worst load | Hardware minimum | Hardware reserve | Accepted-envelope margin | Worst profile |\n|---|---:|---:|---:|---:|---|"
        finding_h = "## Calculation-driven correction"
        finding = "Both exposed-port eFuses now use the active `Yageo RC0402FR-071K82L` 1.82-kohm resistor instead of 2.21 kohm. The guaranteed-low threshold rises from 1.358 to 1.632 A: steady reserve above the 1.25-A port is 30.6%, while the bounded 2-A pulse remains available. The checked quantity-100 price is unchanged."
        boundary_h = "## What this proves"
        boundary = "All four DC rails pass the 25% rule against the minimum hardware threshold. `3V3_MAIN` has the tightest accepted operating envelope: the conservative 2.462-A load leaves 38 mA to the accepted 2.5-A requirement but 30.0% to the guaranteed 3.2-A protection threshold. H3.2 must therefore prove the load step and H8 must measure the real sum."
        marker = "**Status:** `H3.1.2` is complete and reviewed; the exact current marker is `H3.3.2`."
        evidence = "[Complete machine calculation](../hardware/verification/generated/H3-VRF12-dc-budget.json)."
    return "\n\n".join((title, nav, intro, headers + "\n" + table, finding_h, finding, boundary_h, boundary, marker, evidence)) + "\n"


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
        stale = [path for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(
            "ok: H3.1.2 DC budget current; "
            f"{manifest['summary']['rail_profiles_evaluated']} rail profiles, "
            f"minimum reserve {manifest['summary']['minimum_hardware_reserve_percent']}%"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
