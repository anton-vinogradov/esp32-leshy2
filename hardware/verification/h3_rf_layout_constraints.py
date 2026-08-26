#!/usr/bin/env python3
"""Derive H3.5.2 RF corridor, plane and return-current constraints."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
H1_PATH = REPO / "hardware/product-design/generated/H1-unified-coordinate-table.json"
FEED_PATH = REPO / "hardware/verification/generated/H3-VRF51-rf-feed-constraints.json"
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF52-rf-layout-constraints.json"
DOC_EN = REPO / "docs/rf-layout-constraints.md"
DOC_RU = REPO / "docs/rf-layout-constraints.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def route_length(points: list[list[float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def build() -> tuple[dict[Path, str], dict]:
    h1 = json.loads(H1_PATH.read_text(encoding="utf-8"))
    feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    audit = h1["physical_interconnect_clearance_audit"]
    topology = audit["antenna_source_to_port_topology"]
    guides = topology["guides"]
    guide_by_path = {row["path"]: row for row in guides}
    feed_by_path = {row["id"]: row for row in feed["path_constraints"]}

    # A conservative common high-band fence pitch is rounded down from lambda_g/20
    # at the C5 5.885-GHz edge with epsilon_eff=3.5. It is a placement constraint,
    # not a claim about the later production stack-up.
    lambda_g_mm = 299_792_458_000 / (5_885_000_000 * math.sqrt(3.5))
    calculated_pitch_mm = lambda_g_mm / 20
    high_band_fence_pitch_mm = 1.25

    per_path = []
    for path_id in feed_by_path:
        guide = guide_by_path[path_id]
        mode = feed_by_path[path_id]["mode"]
        if path_id in {"S3-2G4", "C5-2G4/5", "N24-0", "N24-1", "N24-2"}:
            fence_pitch = high_band_fence_pitch_mm
            aggressor_clearance = "max(5 x solved trace width, 1.50 mm)"
        elif path_id == "RX-AM/LW":
            fence_pitch = None
            aggressor_clearance = "capacitance-extracted keepout; no plane or aggressor beneath the high-Z segment"
        else:
            fence_pitch = 2.50
            aggressor_clearance = "max(3 x solved trace width, 1.00 mm)"
        per_path.append({
            "id": path_id,
            "frame": guide["frame"],
            "source_instance": guide["radio_source_instance"],
            "external_connector_instance": guide["external_connector_instance"],
            "h1_topology_guide_mm": guide["points_mm"],
            "h1_topology_guide_length_mm": round(route_length(guide["points_mm"]), 3),
            "guide_status": "topology-and-paper-corridor only; not production copper",
            "mode": mode,
            "maximum_signal_layer_transitions": 1,
            "via_fence_pitch_mm_max": fence_pitch,
            "aggressor_clearance": aggressor_clearance,
            "return_contract": (
                "local SMA shell ground remains solid, but the external high-impedance AMI segment has no plane beneath it; "
                "extracted connector+PCB+ESD+pod capacitance must remain within H3-VRF51"
                if path_id == "RX-AM/LW" else
                "one uninterrupted reference plane follows the entire PCB mainline; every allowed layer transition gets an adjacent symmetric ground-via pair"
            ),
        })

    frames = {row["frame"] for row in per_path}
    source_paths = {row["id"] for row in per_path}
    expected_paths = set(candidate["antenna_policy"]["base_onboard_sma_paths"])
    nrf_lengths = [row["h1_topology_guide_length_mm"] for row in per_path if row["id"].startswith("N24-")]
    native_cables = audit["rf_microcoax"]

    common_rules = {
        "stackup_and_width": "H6 must solve 50-ohm width/spacing against the released fabricator stack-up and correlate it with an impedance coupon; no generic width is frozen in H3",
        "reference_plane": "no 50-ohm mainline may cross a plane split, void, antipad field, connector-tail keepout or narrowed return neck",
        "layer_changes": "prefer zero signal-layer changes; at most one transition is allowed per antenna path, adjacent to its outer connector, and it must be field-solved with symmetric return vias",
        "connector_return": "SMA/RP-SMA shells, U.FL ground lands, coupler grounds, RF switches, balun and every shunt ESD/matching body receive immediate local ground vias; target pad-edge-to-via-edge <=0.75 mm where the footprint permits",
        "corners": "use arcs or two 45-degree bends; no acute corner and no decorative meander or phase-equalization length",
        "stubs": "no tee or test-pad stub on a mainline; directional samplers remain inline and detector branches depart only from their coupled ports",
        "esd_order": "place the RF ESD shunt at the external connector boundary before any long internal trace, with the shortest possible return",
        "microcoax": "all five removable 30-mm assemblies keep independent service slack and strain relief, do not become board restraints, and may not be compressed by the mated 11-mm sandwich",
        "crossing": "RF mainlines do not cross each other; unavoidable digital crossings occur once, orthogonally, on another layer over an unbroken plane",
        "quiet_aggressors": "no display/SD/USB clock, DC/DC switch node, crystal clock, class-D output or high-current LED/IR edge is routed parallel inside an RF clearance corridor",
        "coupled_evidence": "LTC5532 detector and hold circuitry live outside the mainline corridor; the coupled branch is shortest-first and never returns through receiver or oscillator ground",
        "tuning": "CC1101 branches and receiver matching retain accessible 0402 tuning lands inside their RF zones without lengthening unrelated paths",
        "documentation": "H6 exports routed length, layer, solved impedance, reference plane, transitions, fence pitch and nearest aggressor for each of the ten path IDs",
    }
    special_rules = {
        "native_and_nrf": "module U.FL/IPEX-to-board U.FL remains physical microcoax; only the board-receptacle-to-coupler-to-SMA section is PCB mainline",
        "cc_sub": "keep RF_P/RF_N length mismatch <=0.50 mm through the balun; place both BGS13SN8 switches and four branch networks as one compact, symmetric, via-fenced island; isolate every unselected branch without shared narrow ground",
        "voice": "place each SA818S ANT contact 12, its own protection and its own SMA in an independent shortest practical corridor; keep class-D speaker current, the other voice corridor and codec input ground outside both",
        "fm_sw": "hold 50 ohms only from SMA to the first 56-nH body; the receiver-side match is not forced into a 50-ohm geometry",
        "am_lw": "do not apply the 50-ohm plane/fence template to the high-Z AMI segment; minimize surface area and extracted capacitance, forbid long coax, and keep all copper/aggressors away beneath it",
    }

    checks = {
        "h351_is_reviewed": feed["review_summary"]["status"] == "reviewed",
        "h1_clearance_audit_passed": audit["result"] == "paper_keepouts_passed_final_ecad_and_h5_open",
        "h1_topology_is_explicitly_not_final_copper": topology["final_copper_status"] == "open_until_kicad_drc",
        "exactly_ten_guides": topology["guide_count"] == len(guides) == 10,
        "guide_paths_equal_feed_paths": set(guide_by_path) == set(feed_by_path),
        "guide_paths_equal_antenna_policy": source_paths == expected_paths,
        "four_ui_and_six_rf_paths": sum(row["frame"] == "ui-inner" for row in per_path) == 4 and sum(row["frame"] == "rf-inner" for row in per_path) == 6,
        "only_two_board_frames": frames == {"ui-inner", "rf-inner"},
        "every_guide_reaches_antenna_edge": all(row["h1_topology_guide_mm"][-1][1] == 0.0 for row in per_path),
        "all_guide_lengths_positive": all(row["h1_topology_guide_length_mm"] > 0 for row in per_path),
        "all_nrf_guides_are_independent": len(nrf_lengths) == 3 and len({row["external_connector_instance"] for row in per_path if row["id"].startswith("N24-")}) == 3,
        "five_microcoaxes_accounted": native_cables["all_five_feed_assemblies_accounted"] is True,
        "microcoax_same_face_keepouts_pass": native_cables["same_face_keepouts_passed"] is True,
        "microcoax_has_positive_3d_slack": all(row["unprojected_3d_slack_mm"] > 0 for row in native_cables["native_direct_projections"] + native_cables["nrf_reserves"]),
        "common_high_band_pitch_is_conservative": high_band_fence_pitch_mm <= calculated_pitch_mm,
        "generic_paths_have_reference_fence": all(row["via_fence_pitch_mm_max"] is not None for row in per_path if row["id"] != "RX-AM/LW"),
        "amlw_has_no_generic_fence": next(row for row in per_path if row["id"] == "RX-AM/LW")["via_fence_pitch_mm_max"] is None,
        "amlw_rule_preserves_capacitance_contract": "capacitance" in special_rules["am_lw"] and "50-ohm" in special_rules["am_lw"],
        "cc_differential_balance_is_bounded": "0.50 mm" in special_rules["cc_sub"],
        "all_paths_limit_layer_transitions": all(row["maximum_signal_layer_transitions"] == 1 for row in per_path),
        "no_stub_rule_is_explicit": "no tee" in common_rules["stubs"],
        "aggressor_rule_names_all_major_classes": all(token in common_rules["quiet_aggressors"] for token in ("display", "USB", "DC/DC", "class-D", "IR")),
        "h6_export_contract_names_ten_ids": "ten path IDs" in common_rules["documentation"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.5.2 checks failed: " + ", ".join(failed))

    residual = [
        "release the fabricator stack-up, field-solve every launch and 50-ohm geometry, and correlate with coupons in H6",
        "prove each routed path stays inside the accepted mechanical envelope and has no DRC, return-path or plane-slot violation",
        "measure received 2118651-2 bend/retention/strain behavior and E01 connector axes before freezing the five microcoax paths",
        "extract AM/LW connector, pad and high-Z trace capacitance and prove the complete external budget remains <=19.500 pF",
        "inspect every RF via fence, connector ground, ESD return and coupled-sampler branch on the fabricated board before H8 VNA/spectrum work",
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H3.5.2",
        "status": "reviewed_rf_corridor_plane_and_return_constraints",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (H1_PATH, FEED_PATH, CANDIDATE_PATH)},
        "summary": {"paths": len(per_path), "ui_inner_paths": 4, "rf_inner_paths": 6, "microcoaxes": 5, "checks": len(checks)},
        "derived": {"c5_lambda_g_over_20_mm_at_5p885ghz_eps_eff_3p5": round(calculated_pitch_mm, 3), "selected_high_band_fence_pitch_mm_max": high_band_fence_pitch_mm},
        "path_corridors": per_path,
        "common_rules": common_rules,
        "special_rules": special_rules,
        "checks": checks,
        "corrections": ["RX-AM/LW is excluded from the generic 50-ohm plane/via-fence template; its controlling layout quantity is extracted capacitance"],
        "open_findings": [],
        "residual_physical_only": residual,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.5.3", "action": "verify isolation, quiet-state and full three-nRF concurrency assumptions"},
    }

    rows_en = "\n".join(f"| {r['id']} | {r['frame']} | {r['h1_topology_guide_length_mm']:.3f} | {r['via_fence_pitch_mm_max'] if r['via_fence_pitch_mm_max'] is not None else 'capacitance-controlled'} |" for r in per_path)
    rows_ru = rows_en
    en = f"""# RF layout constraints

`H3.5.2` is reviewed with `{len(checks)}` machine checks and no open analytical finding. The exact current marker is `H3.6.1`.

The H1 lines remain topology/corridor guides, not alleged KiCad copper. Their projected lengths are carried forward only so H6 cannot silently lose or swap a path.

| Path | Board inner frame | H1 guide, mm | Maximum via-fence pitch, mm |
|---|---:|---:|---:|
{rows_en}

For every ordinary RF mainline H6 must solve the released stack-up, preserve one uninterrupted reference plane, use no tee/test stub, prefer zero and allow at most one field-solved signal-layer transition, and place connector/ESD/matching return vias immediately. The common 2.4/5-GHz fence pitch is `1.25 mm`, rounded below the conservative `lambda_g/20 = {calculated_pitch_mm:.3f} mm` value at 5.885 GHz and effective permittivity 3.5.

`RX-AM/LW` is deliberately different: its high-impedance segment gets no generic 50-ohm plane or fence. Its connector, PCB, ESD and pod capacitance must instead fit the H3.5.1 `19.500-pF` external budget.

Machine evidence: [`H3-VRF52-rf-layout-constraints.json`](../hardware/verification/generated/H3-VRF52-rf-layout-constraints.json).
"""
    ru = f"""# Ограничения RF layout

`H3.5.2` проведён ревью: `{len(checks)}` машинных checks, незакрытых аналитических findings нет. Точный текущий маркер — `H3.6.1`.

Линии H1 остаются topology/corridor guides, а не якобы готовой медью KiCad. Их проекционные длины перенесены только для того, чтобы H6 не мог молча потерять или перепутать тракт.

| Тракт | Внутренняя сторона платы | Guide H1, мм | Максимальный шаг via fence, мм |
|---|---:|---:|---:|
{rows_ru}

Для каждого обычного RF-mainline H6 обязан рассчитать геометрию по утверждённому stack-up, сохранить непрерывную reference plane, исключить tee/test stub, предпочитать ноль и допускать максимум один рассчитанный signal-layer transition, а return vias connector/ESD/matching ставить немедленно. Общий шаг fence для 2,4/5 ГГц равен `1,25 мм`: он округлён вниз от консервативного `lambda_g/20 = {calculated_pitch_mm:.3f} мм` на 5,885 ГГц при effective permittivity 3,5.

`RX-AM/LW` намеренно отличается: под его high-impedance сегментом нет общего 50-омного plane/fence. Вместо этого connector, PCB, ESD и pod должны уложиться во внешний бюджет H3.5.1 `19,500 пФ`.

Машинное evidence: [`H3-VRF52-rf-layout-constraints.json`](../hardware/verification/generated/H3-VRF52-rf-layout-constraints.json).
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
            raise SystemExit("stale H3.5.2 artifacts: " + ", ".join(stale))
    print(f"ok: H3.5.2 reviewed; {len(manifest['checks'])} checks, next H3.5.3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
