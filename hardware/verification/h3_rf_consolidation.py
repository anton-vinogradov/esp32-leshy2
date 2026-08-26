#!/usr/bin/env python3
"""Consolidate H3.5 RF pre-layout and coexistence evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
FEED_PATH = REPO / "hardware/verification/generated/H3-VRF51-rf-feed-constraints.json"
LAYOUT_PATH = REPO / "hardware/verification/generated/H3-VRF52-rf-layout-constraints.json"
COEX_PATH = REPO / "hardware/verification/generated/H3-VRF53-rf-coexistence.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF54-rf-consolidation.json"
DOC_EN = REPO / "docs/rf-verification-result.md"
DOC_RU = REPO / "docs/rf-verification-result.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))
    coex = json.loads(COEX_PATH.read_text(encoding="utf-8"))
    leaves = [feed, layout, coex]
    feed_ids = {row["id"] for row in feed["path_constraints"]}
    layout_ids = {row["id"] for row in layout["path_corridors"]}
    groups = {row["signal_group"] for row in coex["group_quiet_matrix"]}
    path_groups = {
        "S3-2G4": "SG-S3-24",
        "C5-2G4/5": "SG-C5-NATIVE",
        "N24-0": "SG-N24",
        "N24-1": "SG-N24",
        "N24-2": "SG-N24",
        "CC-SUB": "SG-CC",
        "VOICE-VHF": "SG-VOICE",
        "VOICE-UHF": "SG-VOICE",
        "RX-FM/SW": "SG-BROADCAST",
        "RX-AM/LW": "SG-BROADCAST",
    }
    residual = list(dict.fromkeys(item for leaf in leaves for item in leaf["residual_physical_only"]))
    leaf_checks = sum(leaf["review_summary"]["checks"] for leaf in leaves)
    corrections = [item for leaf in leaves for item in leaf["corrections"]]
    am_feed = next(row for row in feed["path_constraints"] if row["id"] == "RX-AM/LW")
    am_layout = next(row for row in layout["path_corridors"] if row["id"] == "RX-AM/LW")
    nrf_layout = [row for row in layout["path_corridors"] if row["id"].startswith("N24-")]

    downstream = {
        "H4": [
            "consume the complete H3.5 package with firmware F3 target/emulator evidence; no RF analytical finding may remain open",
            "confirm every physical-only item has an owner in H5, H6 or H8 and no purchase/layout authorization is inferred from this review",
        ],
        "H5": [
            "identify and measure received E01 module RF axes, five Gen1 microcoax mating pairs and service bend/retention behavior",
            "retain raw connector/pod/cable records; mismatch reopens H1/H2/H3.5 instead of being patched only in placement",
        ],
        "H6": [
            "release a fabricator stack-up, field-solve and coupon-correlate every 50-ohm launch/mainline",
            "export for all ten path IDs: routed length, layer, solved impedance, reference plane, transitions, fence pitch and nearest aggressor",
            "run DRC plus explicit return-path/plane-slot/RF-corridor review; extract RX-AM/LW capacitance rather than forcing it to 50 ohms",
        ],
        "H8": [
            "VNA/spectrum/power/sensitivity/harmonic/EIRP qualification for every admitted path, band, channel, power, antenna and pose",
            "L1 isolated baseline, L2 all foreign quiet contracts, L3 maximum support aggression and L5 transition/fault evidence",
            "FX-I6-N24-T1 target plus independent observer for every mandatory role/identity mix with no hidden standby or RX gap",
        ],
    }
    checks = {
        "all_three_leaf_reviews_are_closed": all(leaf["review_summary"]["status"] == "reviewed" for leaf in leaves),
        "all_leaf_fail_counts_are_zero": all(leaf["review_summary"]["failed"] == 0 for leaf in leaves),
        "all_leaf_unresolved_counts_are_zero": all(leaf["review_summary"]["unresolved"] == 0 for leaf in leaves),
        "all_leaf_open_findings_are_empty": all(not leaf["open_findings"] for leaf in leaves),
        "leaf_check_total_is_128": leaf_checks == 128,
        "feed_and_layout_cover_same_ten_paths": feed_ids == layout_ids and len(feed_ids) == 10,
        "every_onboard_path_has_runtime_group": set(path_groups) == feed_ids and set(path_groups.values()).issubset(groups),
        "all_nine_runtime_groups_are_covered": len(groups) == 9,
        "eight_tx_and_two_receive_only_paths_preserved": feed["summary"]["tx_capable_paths"] == 8 and feed["summary"]["receive_only_paths"] == 2,
        "all_five_microcoaxes_preserved": layout["summary"]["microcoaxes"] == 5,
        "ordinary_paths_have_plane_and_return_contract": all("reference plane" in row["return_contract"] for row in layout["path_corridors"] if row["id"] != "RX-AM/LW"),
        "amlw_is_non50_end_to_end": am_feed["mode"] == "non50_high_impedance_loop_pod" and am_layout["via_fence_pitch_mm_max"] is None and "no plane" in am_layout["return_contract"],
        "amlw_capacitance_budget_is_19p5pf": am_feed["external_total_capacitance_pf_max"] == "19.500",
        "three_nrf_paths_have_separate_connectors": len(nrf_layout) == 3 and len({row["external_connector_instance"] for row in nrf_layout}) == 3,
        "nrf_four_modes_and_eight_permutations_preserved": coex["summary"]["nrf_role_modes"] == 4 and coex["summary"]["nrf_identity_permutations"] == 8,
        "one_group_runtime_limit_preserved": coex["checks"]["one_top_level_group_is_hard_limit"] and coex["checks"]["cross_group_runtime_is_prohibited"],
        "all_13_quiet_contracts_preserved": coex["summary"]["quiet_contracts"] == 13,
        "laboratory_injection_never_expands_runtime": "never becomes runtime permission" in coex["acceptance"]["lab_injection"],
        "unknown_state_fails_closed": coex["checks"]["unknown_fails_to_none_and_tx_disarmed"],
        "physical_residuals_are_nonempty_and_assigned": len(residual) >= 15 and set(downstream) == {"H4", "H5", "H6", "H8"},
        "paper_review_does_not_claim_final_rf": coex["checks"]["paper_does_not_overclaim_same_channel_isolation"] and "field-solve" in downstream["H6"][0] and "VNA" in downstream["H8"][0],
        "correction_is_preserved": corrections == ["RX-AM/LW is excluded from the generic 50-ohm plane/via-fence template; its controlling layout quantity is extracted capacitance"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.5.4 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.5.4",
        "status": "reviewed_rf_prelayout_and_coexistence_consolidation",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (FEED_PATH, LAYOUT_PATH, COEX_PATH)},
        "consolidated": {"leaf_packages": 3, "leaf_checks": leaf_checks, "consolidation_checks": len(checks), "paths": 10, "signal_groups": 9, "quiet_contracts": 13, "physical_residuals": len(residual)},
        "path_to_runtime_group": path_groups,
        "corrections": corrections,
        "downstream_evidence": downstream,
        "checks": checks,
        "open_findings": [],
        "residual_physical_only": residual,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.6.1", "action": "build the worst-case board, battery and enclosure thermal model"},
    }

    en = f"""# RF verification result

`H3.5` is reviewed: three leaf packages contribute `{leaf_checks}` passing checks and this consolidation adds `{len(checks)}` cross-domain checks. No analytical finding remains open. The exact current marker is `H3.6.1`.

The closed paper contract contains ten source-to-port paths, eight TX-capable paths, five removable microcoaxes, nine runtime signal groups and thirteen quiet-state contracts. VHF and UHF are independent physical feeds but one runtime group with hardware one-hot selection. Ordinary RF mainlines have feed/loss, corridor, plane and return rules; `RX-AM/LW` retains its separate high-impedance `19.500-pF` external-capacitance contract. Full 3×nRF24 remains mandatory in all four role mixes and all eight identity permutations.

This is a pre-layout result, not final RF performance. `{len(residual)}` physical-only items are explicitly assigned to H5 received evidence, H6 field-solved/coupon-correlated routing and H8 VNA/spectrum/OTA/coexistence qualification. It does not authorize purchase, KiCad placement/routing or fabrication.

Machine evidence: [`H3-VRF54-rf-consolidation.json`](../hardware/verification/generated/H3-VRF54-rf-consolidation.json).
"""
    ru = f"""# Сводный результат RF-проверки

`H3.5` проведён ревью: три leaf-пакета дают `{leaf_checks}` проходящих checks, сведение добавляет `{len(checks)}` сквозных checks. Незакрытых аналитических findings нет. Точный текущий маркер — `H3.6.1`.

Закрытый бумажный контракт содержит десять source-to-port трактов, восемь TX-capable трактов, пять съёмных microcoax, девять runtime signal groups и тринадцать quiet-state contracts. VHF и UHF физически независимы, но образуют одну runtime-группу с аппаратным one-hot выбором. Обычные RF-mainline имеют правила feed/loss, corridor, plane и return; `RX-AM/LW` сохраняет отдельный high-impedance бюджет внешней ёмкости `19,500 пФ`. Полные 3×nRF24 остаются обязательными во всех четырёх смесях и восьми перестановках ролей.

Это pre-layout результат, а не заявление финальных RF-характеристик. `{len(residual)}` только физических пунктов явно назначены H5 received evidence, H6 field-solved/coupon-correlated routing и H8 VNA/spectrum/OTA/coexistence qualification. Результат не разрешает закупку, KiCad placement/routing или печать.

Машинное evidence: [`H3-VRF54-rf-consolidation.json`](../hardware/verification/generated/H3-VRF54-rf-consolidation.json).
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
            raise SystemExit("stale H3.5.4 artifacts: " + ", ".join(stale))
    print(f"ok: H3.5 reviewed; {manifest['consolidated']['leaf_checks']} leaf + {manifest['consolidated']['consolidation_checks']} consolidation checks, next H3.6.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
