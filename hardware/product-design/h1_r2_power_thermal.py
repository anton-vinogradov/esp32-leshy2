#!/usr/bin/env python3
"""Audit and render the H1-R2 six-domain rail and thermal architecture."""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "hardware/product-design/h1-r2-power-thermal.json"
PLACEMENT_PATH = REPO / "hardware/product-design/generated/H1-R2-placement-audit.json"
AUDIT_PATH = REPO / "hardware/product-design/generated/H1-R2-power-thermal-audit.json"
SVG_PATH = REPO / "docs/images/h1-r2-power-thermal.svg"
EN_DOC_PATH = REPO / "docs/h1-r2-power-thermal.md"
RU_DOC_PATH = REPO / "docs/h1-r2-power-thermal.ru.md"


def load() -> dict:
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def audit(model: dict) -> dict:
    support_ma = sum(model["main_support_worst_ma"].values())
    groups = []
    for name, row in model["signal_group_loads"].items():
        groups.append({
            "group": name,
            "main_ma": support_ma + row["main_ma"],
            "voice_4v_ma": row["voice_4v_ma"],
            "active_5v_ma": row["active_5v_ma"],
        })
    worst = max(groups, key=lambda row: row["main_ma"])
    main = model["rail_capabilities"]["3V3_MAIN"]
    cell = model["main_power_cell"]
    converter = cell["converter"]
    inductor = cell["inductor"]
    efuse = cell["efuse"]
    rilm = cell["efuse_threshold_resistor"]

    ilm_nominal = 5747.0 / rilm["resistance_ohm"]
    ilm_minimum = ilm_nominal * 0.90 / (1.0 + rilm["tolerance_fraction"])
    ilm_maximum = ilm_nominal * 1.10 / (1.0 - rilm["tolerance_fraction"])
    vin_max = model["source_contract"]["nvdc_sys_voltage_v"][1]
    vout = model["source_contract"]["main_voltage_v"]
    inductance_h = inductor["inductance_uh"] * 1e-6
    frequency_hz = converter["switching_frequency_khz"] * 1e3
    ripple_a = vout * (vin_max - vout) / (vin_max * inductance_h * frequency_hz)
    peak_at_worst = worst["main_ma"] / 1000.0 + ripple_a / 2.0
    peak_at_step = main["accepted_step_a"] + ripple_a / 2.0

    thermal = model["thermal_contract"]
    allowed_converter_loss = (
        thermal["converter_junction_design_c"] - thermal["ambient_design_c"]
    ) / thermal["converter_rtheta_ja_effective_c_per_w"]
    worst_output_w = worst["main_ma"] / 1000.0 * vout
    admitted_output_w = main["accepted_continuous_a"] * vout
    efficiency_floor_worst = worst_output_w / (worst_output_w + allowed_converter_loss)
    efficiency_floor_admitted = admitted_output_w / (admitted_output_w + allowed_converter_loss)
    efuse_loss_worst = (worst["main_ma"] / 1000.0) ** 2 * efuse["ron_thermal_envelope_ohm"]
    efuse_loss_admitted = main["accepted_continuous_a"] ** 2 * efuse["ron_thermal_envelope_ohm"]
    efuse_junction_worst = thermal["ambient_design_c"] + efuse_loss_worst * efuse["rtheta_ja_8via_c_per_w"]
    efuse_junction_admitted = thermal["ambient_design_c"] + efuse_loss_admitted * efuse["rtheta_ja_8via_c_per_w"]
    inductor_loss_worst = (worst["main_ma"] / 1000.0) ** 2 * inductor["dcr_max_ohm"]
    inductor_loss_admitted = main["accepted_continuous_a"] ** 2 * inductor["dcr_max_ohm"]
    inductor_rise_admitted = thermal["inductor_temperature_rise_rating_c"] * (
        main["accepted_continuous_a"] / inductor["rms_rating_a"]
    ) ** 2

    placement = json.loads(PLACEMENT_PATH.read_text(encoding="utf-8")) if PLACEMENT_PATH.exists() else None
    checks = {
        "six_compute_domains_present": len(model["six_compute_domains"]) == 6,
        "all_signal_groups_enumerated": len(groups) == 11,
        "h0_continuous_minimum_met": main["accepted_continuous_a"] >= model["source_contract"]["minimum_continuous_a"],
        "h0_step_minimum_met": main["accepted_step_a"] >= model["source_contract"]["minimum_step_a"],
        "worst_load_within_admitted_continuous": worst["main_ma"] / 1000.0 <= main["accepted_continuous_a"],
        "efuse_guaranteed_low_above_step": ilm_minimum >= main["accepted_step_a"],
        "efuse_high_below_converter_low_limit": ilm_maximum < converter["valley_current_limit_a"]["minimum"],
        "inductor_peak_below_saturation_rating": converter["valley_current_limit_a"]["maximum"] < inductor["saturation_rating_a"],
        "inductor_rms_above_admission": inductor["rms_rating_a"] > main["accepted_continuous_a"],
        "converter_efficiency_gate_is_realistic_not_claimed": efficiency_floor_admitted <= 0.90,
        "efuse_thermal_bound_below_design_junction": efuse_junction_admitted <= thermal["efuse_junction_design_c"],
        "placed_power_cell_has_no_collision": bool(
            placement
            and placement.get("structural_status") == "pass"
            and not placement.get("same_face_collisions")
            and not placement.get("errors")
            and placement.get("minimum_opposing_clearance_mm", -1)
            >= placement.get("required_opposing_clearance_mm", 0)
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": 1,
        "marker": model["marker"],
        "status": "pass_architecture_with_h3_dynamic_thermal_gate" if not failures else "fail",
        "support_worst_ma": support_ma,
        "groups": groups,
        "worst_main_group": worst,
        "main_margin": {
            "accepted_continuous_a": main["accepted_continuous_a"],
            "accepted_step_a": main["accepted_step_a"],
            "worst_load_a": round(worst["main_ma"] / 1000.0, 4),
            "continuous_margin_a": round(main["accepted_continuous_a"] - worst["main_ma"] / 1000.0, 4),
            "continuous_margin_percent_of_load": round((main["accepted_continuous_a"] / (worst["main_ma"] / 1000.0) - 1.0) * 100.0, 2),
        },
        "efuse_threshold_a": {
            "nominal": round(ilm_nominal, 4),
            "guaranteed_minimum": round(ilm_minimum, 4),
            "guaranteed_maximum": round(ilm_maximum, 4),
        },
        "switching_cell": {
            "inductor_ripple_at_8v4_a": round(ripple_a, 4),
            "inductor_peak_at_worst_load_a": round(peak_at_worst, 4),
            "inductor_peak_at_admitted_step_a": round(peak_at_step, 4),
        },
        "thermal_bounds": {
            "allowed_converter_loss_w": round(allowed_converter_loss, 4),
            "required_converter_efficiency_at_worst": round(efficiency_floor_worst, 4),
            "required_converter_efficiency_at_admitted_continuous": round(efficiency_floor_admitted, 4),
            "efuse_loss_at_worst_w": round(efuse_loss_worst, 4),
            "efuse_loss_at_admitted_continuous_w": round(efuse_loss_admitted, 4),
            "efuse_junction_at_worst_c": round(efuse_junction_worst, 2),
            "efuse_junction_at_admitted_continuous_c": round(efuse_junction_admitted, 2),
            "inductor_copper_loss_at_worst_w": round(inductor_loss_worst, 4),
            "inductor_copper_loss_at_admitted_continuous_w": round(inductor_loss_admitted, 4),
            "inductor_estimated_rise_at_admitted_continuous_c": round(inductor_rise_admitted, 2),
            "interpretation": "converter efficiency is an H3 pass threshold, not a predicted value; eFuse and inductor figures are conservative H1 bounds",
        },
        "checks": checks,
        "failures": failures,
        "h3_required_evidence": thermal["h3_required_evidence"],
    }


def render_svg(model: dict, result: dict) -> str:
    esc = html.escape
    width, height = 1280, 760
    node_y = 105
    nodes = [
        (40, 180, "NVDC_SYS", "6.0–8.4 V source"),
        (260, 220, model["main_power_cell"]["converter"]["mpn"], "6-A buck · C3190178"),
        (520, 230, model["main_power_cell"]["inductor"]["mpn"], "2.2 µH · 10 A RMS / 15 A sat"),
        (790, 210, model["main_power_cell"]["efuse"]["mpn"], "4.34-A guaranteed-low trip"),
        (1040, 200, "3V3_MAIN", "3.75 A continuous / 4.25 A step"),
    ]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="36" y="38" font-family="sans-serif" font-size="25" font-weight="700" fill="#172033">Leshy2 · {esc(model["marker"])} rail and thermal architecture</text>',
        '<text x="36" y="65" font-family="sans-serif" font-size="13" fill="#526076">Every box is one exact device or one named rail; H3 still proves dynamic and enclosure behaviour.</text>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#2563eb"/></marker></defs>',
    ]
    for index, (x, w, title, subtitle) in enumerate(nodes):
        fill = "#e0f2fe" if index in {0, 4} else "#eef2ff"
        out.append(f'<rect x="{x}" y="{node_y}" width="{w}" height="82" rx="9" fill="{fill}" stroke="#2563eb" stroke-width="2"/>')
        out.append(f'<text x="{x+w/2}" y="{node_y+32}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#172033">{esc(title)}</text>')
        out.append(f'<text x="{x+w/2}" y="{node_y+56}" text-anchor="middle" font-family="sans-serif" font-size="10.5" fill="#526076">{esc(subtitle)}</text>')
        if index:
            prev_x, prev_w, _, _ = nodes[index - 1]
            out.append(f'<path d="M {prev_x+prev_w} {node_y+41} L {x-10} {node_y+41}" stroke="#2563eb" stroke-width="3" marker-end="url(#arrow)"/>')

    out.extend([
        '<text x="36" y="245" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Enumerated 3V3_MAIN worst cases</text>',
        '<line x1="445" y1="228" x2="445" y2="555" stroke="#94a3b8" stroke-width="1" stroke-dasharray="5 4"/>',
        '<text x="445" y="220" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#526076">3.75-A admission</text>',
    ])
    max_bar = 300.0
    for index, row in enumerate(sorted(result["groups"], key=lambda item: item["main_ma"], reverse=True)):
        y = 270 + index * 24
        bar = row["main_ma"] / 3750.0 * max_bar
        colour = "#16a34a" if index == 0 else "#60a5fa"
        out.append(f'<text x="38" y="{y+11}" font-family="sans-serif" font-size="10.5" fill="#334155">{esc(row["group"])}</text>')
        out.append(f'<rect x="145" y="{y}" width="{bar:.2f}" height="14" rx="3" fill="{colour}"/>')
        out.append(f'<text x="{151+bar:.2f}" y="{y+11}" font-family="sans-serif" font-size="10" fill="#334155">{row["main_ma"]/1000:.3f} A</text>')

    thermal = result["thermal_bounds"]
    checks = result["checks"]
    out.extend([
        '<text x="520" y="245" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Electrical result</text>',
        f'<text x="520" y="277" font-family="sans-serif" font-size="12" fill="#166534">✓ worst group: {esc(result["worst_main_group"]["group"])} · {result["main_margin"]["worst_load_a"]:.3f} A</text>',
        f'<text x="520" y="301" font-family="sans-serif" font-size="12" fill="#166534">✓ continuous margin: {result["main_margin"]["continuous_margin_a"]:.3f} A · {result["main_margin"]["continuous_margin_percent_of_load"]:.1f}%</text>',
        f'<text x="520" y="325" font-family="sans-serif" font-size="12" fill="#166534">✓ eFuse guaranteed: {result["efuse_threshold_a"]["guaranteed_minimum"]:.3f}–{result["efuse_threshold_a"]["guaranteed_maximum"]:.3f} A</text>',
        f'<text x="520" y="349" font-family="sans-serif" font-size="12" fill="#166534">✓ step peak in inductor: {result["switching_cell"]["inductor_peak_at_admitted_step_a"]:.3f} A</text>',
        '<text x="520" y="397" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Thermal admission</text>',
        f'<text x="520" y="429" font-family="sans-serif" font-size="12" fill="#166534">✓ eFuse at 3.75 A / 45°C ambient: {thermal["efuse_junction_at_admitted_continuous_c"]:.1f}°C bound</text>',
        f'<text x="520" y="453" font-family="sans-serif" font-size="12" fill="#166534">✓ inductor estimated rise at 3.75 A: {thermal["inductor_estimated_rise_at_admitted_continuous_c"]:.1f}°C</text>',
        f'<text x="520" y="477" font-family="sans-serif" font-size="12" fill="#b45309">H3 gate: converter efficiency ≥ {thermal["required_converter_efficiency_at_admitted_continuous"]*100:.1f}%</text>',
        f'<text x="520" y="501" font-family="sans-serif" font-size="12" fill="#b45309">H3 gate: effective input/output C ≥ 30 / 44 µF</text>',
        '<text x="520" y="549" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Physical result</text>',
        f'<text x="520" y="581" font-family="sans-serif" font-size="12" fill="#166534">{("✓" if checks["placed_power_cell_has_no_collision"] else "✕")} exact bodies fit without same-face or opposing collision</text>',
        '<text x="520" y="605" font-family="sans-serif" font-size="12" fill="#526076">3×22 µF input + 3×22 µF output are individually placed.</text>',
        '<text x="36" y="714" font-family="sans-serif" font-size="11" fill="#526076">H1 accepts the architecture and physical envelopes. H3 closes effective capacitance, switching loss, load-step response and enclosure thermal behaviour.</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def render_doc(model: dict, result: dict, ru: bool) -> str:
    worst = result["worst_main_group"]
    margin = result["main_margin"]
    thermal = result["thermal_bounds"]
    cell = model["main_power_cell"]
    if ru:
        title = f'# {model["marker"]} · питание и тепловой запас'
        intro = 'Шесть вычислительных доменов и все взаимоисключающие сигнальные группы пересчитаны до production-ECAD. Это принятый рабочий силовой дизайн H1, а не разрешение начинать KiCad или заказ.'
        result_h = '## Результат'
        bullets = [
            f'- Худшая группа — `{worst["group"]}`: `{margin["worst_load_a"]:.3f} А` на `3V3_MAIN`. Приняты `{margin["accepted_continuous_a"]:.2f} А` continuously и `{margin["accepted_step_a"]:.2f} А` step; запас до continuous-границы — `{margin["continuous_margin_a"]:.3f} А` (`{margin["continuous_margin_percent_of_load"]:.1f}%`).',
            f'- `TPS566231PRQFR` сохраняет отдельный диагностический Power-Good и даёт 6-А класс. `TPS25974LRPWR` с `RC0402FR-071K18L` гарантирует порог `{result["efuse_threshold_a"]["guaranteed_minimum"]:.3f}–{result["efuse_threshold_a"]["guaranteed_maximum"]:.3f} А`: step проходит, а eFuse срабатывает раньше минимального current-limit преобразователя.',
            f'- `PSPMAA0605H-2R2M-ANP` имеет 10-А RMS / 15-А saturation. Расчётный пик при принятом step — `{result["switching_cell"]["inductor_peak_at_admitted_step_a"]:.3f} А`.',
            '- Три входных и три выходных `GRM32ER71E226KE15L` размещены отдельными корпусами. H3 обязан доказать не номинальную, а эффективную ёмкость не меньше 30/44 мкФ с bias, температурой и допуском.',
            f'- При 45°C ambient консервативная оценка eFuse на 3,75 А даёт `{thermal["efuse_junction_at_admitted_continuous_c"]:.1f}°C`; H3 должен подтвердить КПД преобразователя не хуже `{thermal["required_converter_efficiency_at_admitted_continuous"]*100:.1f}%` и полный тепловой путь корпуса.',
        ]
        factory_h = '## Выбранные фабричные позиции'
        next_h = '## Что ещё проверяет H3'
        footer = f'> Маркер результата: **{model["marker"]}**. H1 продолжается.'
    else:
        title = f'# {model["marker"]} · rail and thermal headroom'
        intro = 'All six compute domains and every mutually exclusive signal group have been recalculated before production ECAD. This is the accepted H1 working power design, not authorization to start KiCad or order boards.'
        result_h = '## Result'
        bullets = [
            f'- The worst group is `{worst["group"]}` at `{margin["worst_load_a"]:.3f} A` on `3V3_MAIN`. The accepted envelopes are `{margin["accepted_continuous_a"]:.2f} A` continuous and `{margin["accepted_step_a"]:.2f} A` step, leaving `{margin["continuous_margin_a"]:.3f} A` (`{margin["continuous_margin_percent_of_load"]:.1f}%`) to the continuous admission limit.',
            f'- `TPS566231PRQFR` preserves a separate diagnostic Power-Good and provides the 6-A class. `TPS25974LRPWR` with `RC0402FR-071K18L` guarantees `{result["efuse_threshold_a"]["guaranteed_minimum"]:.3f}–{result["efuse_threshold_a"]["guaranteed_maximum"]:.3f} A`: the step passes and the eFuse trips below the converter minimum current limit.',
            f'- `PSPMAA0605H-2R2M-ANP` is rated 10-A RMS / 15-A saturation. Calculated peak at the accepted step is `{result["switching_cell"]["inductor_peak_at_admitted_step_a"]:.3f} A`.',
            '- Three input and three output `GRM32ER71E226KE15L` bodies are placed individually. H3 must prove at least 30/44 µF effective capacitance after bias, temperature and tolerance rather than accepting nominal values.',
            f'- At 45°C ambient, the conservative eFuse bound at 3.75 A is `{thermal["efuse_junction_at_admitted_continuous_c"]:.1f}°C`; H3 must show at least `{thermal["required_converter_efficiency_at_admitted_continuous"]*100:.1f}%` converter efficiency and close the enclosure thermal path.',
        ]
        factory_h = '## Selected factory parts'
        next_h = '## H3 evidence still required'
        footer = f'> Result marker: **{model["marker"]}**. H1 remains in progress.'
    rows = [cell["converter"], cell["inductor"], cell["efuse"], cell["efuse_threshold_resistor"], cell["input_capacitors"], cell["vcc_capacitor"], cell["bootstrap_capacitor"], cell["bootstrap_link"]]
    lines = [title, '', intro, '', '![H1-R2 rail and thermal architecture](images/h1-r2-power-thermal.svg)', '', result_h, '', *bullets, '', factory_h, '', '| Exact MPN | JLCPCB | Role / current route |', '|---|---|---|']
    for row in rows:
        jlc = row.get("jlcpcb_part", "—")
        url = row.get("url")
        jlc_text = f'[`{jlc}`]({url})' if url else f'`{jlc}`'
        role = row.get("availability", row.get("value", "accepted working part"))
        lines.append(f'| `{row["mpn"]}` | {jlc_text} | {role} |')
    lines.extend(['', next_h, ''])
    lines.extend(f'- {item}' for item in model["thermal_contract"]["h3_required_evidence"])
    lines.extend(['', footer, ''])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    model = load()
    result = audit(model)
    outputs = {
        AUDIT_PATH: json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        SVG_PATH: render_svg(model, result),
        EN_DOC_PATH: render_doc(model, result, False),
        RU_DOC_PATH: render_doc(model, result, True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                print(f"stale generated artifact: {path.relative_to(REPO)}")
                return 1
    if result["failures"]:
        print("failed checks:", ", ".join(result["failures"]))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
