#!/usr/bin/env python3
"""Render and stress-check the H1 Airband input-filter candidate."""

from __future__ import annotations

import argparse
import html
import json
import math
import random
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "hardware/product-design/h1-airband-filter.json"
AUDIT_PATH = REPO / "hardware/product-design/generated/H1-Airband-filter-audit.json"
SVG_PATH = REPO / "docs/images/h1-airband-filter.svg"
EN_DOC_PATH = REPO / "docs/h1-airband-filter.md"
RU_DOC_PATH = REPO / "docs/h1-airband-filter.ru.md"


def load() -> dict:
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def multiply(left: tuple[complex, complex, complex, complex], right: tuple[complex, complex, complex, complex]) -> tuple[complex, complex, complex, complex]:
    a, b, c, d = left
    e, f, g, h = right
    return a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h


def loss_db(model: dict, frequency_mhz: float, values: list[tuple[float, float]] | None = None) -> float:
    omega = 2.0 * math.pi * frequency_mhz * 1_000_000.0
    matrix = (1 + 0j, 0j, 0j, 1 + 0j)
    cells = model["candidate"]["cells"]
    for index, cell in enumerate(cells):
        l_nh, c_pf = values[index] if values else (cell["l_nh"], cell["c_pf"])
        z_l = omega * l_nh * 1e-9 / cell["l_q"] + 1j * omega * l_nh * 1e-9
        z_c = 1.0 / (omega * c_pf * 1e-12 * 1200.0) - 1j / (omega * c_pf * 1e-12)
        if cell["kind"] == "series_resonator":
            element = (1 + 0j, z_l + z_c, 0j, 1 + 0j)
        elif cell["kind"] == "shunt_parallel_resonator":
            element = (1 + 0j, 0j, 1.0 / z_l + 1.0 / z_c, 1 + 0j)
        else:
            element = (1 + 0j, 0j, 1.0 / (z_l + z_c), 1 + 0j)
        matrix = multiply(matrix, element)
    a, b, c, d = matrix
    z0 = model["impedance_ohm"]
    s21 = 2.0 / (a + b / z0 + c * z0 + d)
    return -20.0 * math.log10(abs(s21))


def stressed_values(model: dict, rng: random.Random) -> list[tuple[float, float]]:
    values = []
    for cell in model["candidate"]["cells"]:
        l = cell["l_nh"] * (1.0 + rng.uniform(-cell["l_tolerance_fraction"], cell["l_tolerance_fraction"]))
        if "c_tolerance_fraction" in cell:
            c = cell["c_pf"] * (1.0 + rng.uniform(-cell["c_tolerance_fraction"], cell["c_tolerance_fraction"]))
        else:
            c = cell["c_pf"] + rng.uniform(-cell["c_tolerance_pf"], cell["c_tolerance_pf"])
        values.append((l, c))
    return values


def audit(model: dict) -> dict:
    pass_frequencies = [float(x) for x in range(118, 138)]
    stop_points = model["reference"]["stop_points"]
    named = sorted(set(pass_frequencies + [row["frequency_mhz"] for row in stop_points]))
    nominal = {str(int(f) if f.is_integer() else f): round(loss_db(model, f), 4) for f in named}
    rng = random.Random(model["candidate"]["stress_sweep"]["seed"])
    scenarios: list[list[tuple[float, float]]] = []
    for direction in (-1.0, 1.0):
        row = []
        for cell in model["candidate"]["cells"]:
            l = cell["l_nh"] * (1.0 + direction * cell["l_tolerance_fraction"])
            c = cell["c_pf"] * (1.0 + direction * cell.get("c_tolerance_fraction", 0.0))
            if "c_tolerance_pf" in cell:
                c = cell["c_pf"] + direction * cell["c_tolerance_pf"]
            row.append((l, c))
        scenarios.append(row)
    scenarios.extend(stressed_values(model, rng) for _ in range(model["candidate"]["stress_sweep"]["random_samples"]))
    stress = {str(int(f) if f.is_integer() else f): {"minimum_loss_db": 1e9, "maximum_loss_db": -1e9} for f in named}
    for values in scenarios:
        for frequency in named:
            key = str(int(frequency) if frequency.is_integer() else frequency)
            value = loss_db(model, frequency, values)
            stress[key]["minimum_loss_db"] = min(stress[key]["minimum_loss_db"], value)
            stress[key]["maximum_loss_db"] = max(stress[key]["maximum_loss_db"], value)
    for row in stress.values():
        row["minimum_loss_db"] = round(row["minimum_loss_db"], 4)
        row["maximum_loss_db"] = round(row["maximum_loss_db"], 4)

    maximum = model["reference"]["maximum_passband_loss_db"]
    nominal_pass_max = max(nominal[str(int(f))] for f in pass_frequencies)
    stress_pass_max = max(stress[str(int(f))]["maximum_loss_db"] for f in pass_frequencies)
    stop_results = []
    for point in stop_points:
        key = str(int(point["frequency_mhz"]))
        stop_results.append({
            **point,
            "nominal_loss_db": nominal[key],
            "stress_minimum_loss_db": stress[key]["minimum_loss_db"],
            "nominal_pass": nominal[key] >= point["minimum_loss_db"],
            "stress_pass": stress[key]["minimum_loss_db"] >= point["minimum_loss_db"],
        })
    failures = []
    if nominal_pass_max > maximum:
        failures.append("nominal passband exceeds the 4.5-dB mask")
    if stress_pass_max > maximum:
        failures.append("tolerance/Q stress exceeds the 4.5-dB passband mask")
    failures.extend(f"stress rejection misses the mask at {row['frequency_mhz']:g} MHz" for row in stop_results if not row["stress_pass"])
    return {
        "schema_version": 1,
        "marker": model["marker"],
        "status": "nominal_pass_stress_fail" if failures else "pass",
        "candidate_is_production_frozen": False,
        "nominal_passband_maximum_loss_db": round(nominal_pass_max, 4),
        "stress_passband_maximum_loss_db": round(stress_pass_max, 4),
        "stress_scenario_count": len(scenarios),
        "stop_results": stop_results,
        "nominal_loss_db": nominal,
        "stress_envelope_db": stress,
        "failures": failures,
        "accepted_result": model["decision"]["accepted"],
        "next_gate": model["decision"]["next_gate"],
    }


def render_svg(model: dict, result: dict) -> str:
    width, height = 1120, 570
    left, top, plot_w, plot_h = 78, 92, 720, 390
    f_min, f_max, loss_max = 80.0, 220.0, 60.0

    def x(frequency: float) -> float:
        return left + (frequency - f_min) / (f_max - f_min) * plot_w

    def y(loss: float) -> float:
        return top + plot_h - min(loss, loss_max) / loss_max * plot_h

    samples = [(float(f), loss_db(model, float(f))) for f in range(80, 221)]
    failed_stress = next(row for row in result["stop_results"] if not row["stress_pass"])
    path = " ".join(("M" if index == 0 else "L") + f" {x(f):.2f} {y(loss):.2f}" for index, (f, loss) in enumerate(samples))
    esc = html.escape
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="1120" height="570" fill="#ffffff"/>',
        f'<text x="36" y="38" font-family="sans-serif" font-size="25" font-weight="700" fill="#172033">Leshy2 · {esc(model["marker"])} Airband filter feasibility</text>',
        '<text x="36" y="64" font-family="sans-serif" font-size="13" fill="#526076">Nominal finite-Q response passes; the fixed-value production BOM remains open because tolerance stress does not.</text>',
        f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#f8fafc" stroke="#334155" stroke-width="1.5"/>',
    ]
    for loss in (0, 10, 20, 30, 40, 50, 60):
        out.append(f'<line x1="{left}" y1="{y(loss):.2f}" x2="{left + plot_w}" y2="{y(loss):.2f}" stroke="#dbe2ea" stroke-width="1"/>')
        out.append(f'<text x="{left - 10}" y="{y(loss) + 4:.2f}" text-anchor="end" font-family="sans-serif" font-size="10" fill="#526076">{loss}</text>')
    for frequency in (80, 95, 105, 118, 127, 137, 155, 180, 220):
        out.append(f'<line x1="{x(frequency):.2f}" y1="{top}" x2="{x(frequency):.2f}" y2="{top + plot_h}" stroke="#e2e8f0" stroke-width="1"/>')
        out.append(f'<text x="{x(frequency):.2f}" y="{top + plot_h + 20}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#526076">{frequency}</text>')
    out.extend([
        f'<rect x="{x(118):.2f}" y="{y(4.5):.2f}" width="{x(137)-x(118):.2f}" height="{y(0)-y(4.5):.2f}" fill="#dcfce7" fill-opacity="0.8"/>',
        f'<path d="{path}" fill="none" stroke="#2563eb" stroke-width="2.5"/>',
        f'<text x="{left + plot_w/2:.2f}" y="{height - 28}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#334155">frequency, MHz</text>',
        f'<text x="20" y="{top + plot_h/2:.2f}" transform="rotate(-90 20 {top + plot_h/2:.2f})" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#334155">insertion loss, dB</text>',
        '<text x="840" y="105" font-family="sans-serif" font-size="16" font-weight="700" fill="#172033">Result</text>',
        f'<text x="840" y="135" font-family="sans-serif" font-size="12" fill="#166534">✓ nominal pass max: {result["nominal_passband_maximum_loss_db"]:.2f} dB</text>',
        f'<text x="840" y="158" font-family="sans-serif" font-size="12" fill="#166534">✓ named nominal stop points pass</text>',
        f'<text x="840" y="181" font-family="sans-serif" font-size="12" fill="#166534">✓ stress passband max: {result["stress_passband_maximum_loss_db"]:.2f} dB</text>',
        f'<text x="840" y="204" font-family="sans-serif" font-size="12" fill="#b42318">✕ {failed_stress["frequency_mhz"]:g} MHz stress stop: {failed_stress["stress_minimum_loss_db"]:.2f} / {failed_stress["minimum_loss_db"]:g} dB</text>',
        '<text x="840" y="227" font-family="sans-serif" font-size="12" fill="#b42318">✕ fixed-value BOM is not frozen</text>',
        '<text x="840" y="267" font-family="sans-serif" font-size="16" font-weight="700" fill="#172033">Physical consequence</text>',
        '<text x="840" y="297" font-family="sans-serif" font-size="12" fill="#526076">24 × 11 mm ground-fenced cell</text>',
        '<text x="840" y="318" font-family="sans-serif" font-size="12" fill="#526076">alternate-value / DNP tuning pads</text>',
        '<text x="840" y="339" font-family="sans-serif" font-size="12" fill="#526076">H3 extracted-parasitic optimisation</text>',
        '<text x="840" y="373" font-family="sans-serif" font-size="16" font-weight="700" fill="#172033">Interpretation</text>',
        '<text x="840" y="403" font-family="sans-serif" font-size="12" fill="#526076">The cheap compact route survives,</text>',
        '<text x="840" y="424" font-family="sans-serif" font-size="12" fill="#526076">but nominal simulation is not review.</text>',
        '<text x="840" y="445" font-family="sans-serif" font-size="12" fill="#526076">No production MPN is accepted here.</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def render_doc(model: dict, result: dict, ru: bool) -> str:
    failed_stress = next(row for row in result["stop_results"] if not row["stress_pass"])
    if ru:
        title = f'# {model["marker"]} · входной фильтр Airband'
        intro = 'Проверена дешёвая и компактная замена большому `BPF-A127+`. Это результат физической проработки, а не разрешение начинать KiCad.'
        result_heading = '## Что получилось'
        bullets = [
            f'- Номинальный finite-Q расчёт проходит маску: худшая потеря в 118–137 МГц — `{result["nominal_passband_maximum_loss_db"]:.2f} дБ` при лимите `4,5 дБ`; все именованные nominal stop-точки проходят.',
            f'- Stress sweep из `{result["stress_scenario_count"]}` наборов сохраняет passband (`{result["stress_passband_maximum_loss_db"]:.2f} дБ` при лимите `4,5 дБ`), но на {failed_stress["frequency_mhz"]:g} МГц худшее подавление — `{failed_stress["stress_minimum_loss_db"]:.2f} дБ` вместо `{failed_stress["minimum_loss_db"]:g} дБ`. Поэтому значения элементов и production MPN **не приняты**.',
            '- Сохраняется серийная LC-реализация, но её физическая ячейка увеличена до `24 × 11 мм`, получает via-fence и площадки альтернативных/DNP номиналов.',
            '- Полоса 180–2200 МГц не доказывается lumped-моделью выше SRF: её закрывают extracted-модель H3 и VNA в H7.',
        ]
        factory = '## Свидетельства фабричной реализуемости'
        note = 'Это не BOM фильтра: строки доказывают, что нужные классы точных серийных RF-индуктивностей существуют на фабричной поверхности. Полный набор MPN принимается только после H3.'
        next_heading = '## Следующий gate'
        next_text = 'H3 должен подобрать один фиксированный фабричный BOM-state с учётом паразитик платы и допусков. Если полная маска не сойдётся, возвращаемся к точному покупному фильтру или меняем границу приёмника; номинальный результат не будет выдан за готовое решение.'
    else:
        title = f'# {model["marker"]} · Airband input filter'
        intro = 'A compact low-cost replacement for the large `BPF-A127+` has been tested. This is a physical-design result, not authorization to start KiCad.'
        result_heading = '## Result'
        bullets = [
            f'- The nominal finite-Q model passes: worst 118–137 MHz loss is `{result["nominal_passband_maximum_loss_db"]:.2f} dB` against `4.5 dB`, and every named nominal stop point passes.',
            f'- A `{result["stress_scenario_count"]}`-state value stress sweep keeps the passband within limit (`{result["stress_passband_maximum_loss_db"]:.2f} dB` against `4.5 dB`), but worst {failed_stress["frequency_mhz"]:g}-MHz rejection is `{failed_stress["stress_minimum_loss_db"]:.2f} dB` against `{failed_stress["minimum_loss_db"]:g} dB`. Values and production MPNs are therefore **not accepted**.',
            '- The serial LC route is retained, but its physical cell grows to `24 × 11 mm` and gains a via fence plus alternate-value/DNP tuning pads.',
            '- A lumped model cannot prove 180–2200 MHz above component SRF; H3 extracted modelling and H7 VNA measurement close that band.',
        ]
        factory = '## Factory feasibility witnesses'
        note = 'This is not the filter BOM. These rows prove that the required precision serial RF-inductor classes exist on the factory surface. The complete MPN set is accepted only after H3.'
        next_heading = '## Next gate'
        next_text = 'H3 must find one fixed factory BOM state with extracted PCB parasitics and tolerances. If the complete mask does not close, the design returns to an exact purchased filter or a different receiver boundary; nominal compliance will not be presented as a finished result.'
    lines = [title, '', intro, '', '![Airband filter feasibility](images/h1-airband-filter.svg)', '', result_heading, '', *bullets, '', factory, '', note, '', '| Exact MPN | JLCPCB | Value | Current route |', '|---|---|---|---|']
    for row in model['factory_feasibility_witnesses']:
        lines.append(f'| `{row["mpn"]}` | [`{row["jlcpcb_part"]}`]({row["url"]}) | {row["value"]} | {row["availability"]} |')
    lines.extend(['', next_heading, '', next_text, '', f'> Exact current marker: **{model["marker"]}**. H1 remains in progress.' if not ru else f'> Точный текущий маркер: **{model["marker"]}**. H1 продолжается.', ''])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    model = load()
    result = audit(model)
    outputs = {
        AUDIT_PATH: json.dumps(result, indent=2, ensure_ascii=False) + '\n',
        SVG_PATH: render_svg(model, result),
        EN_DOC_PATH: render_doc(model, result, False),
        RU_DOC_PATH: render_doc(model, result, True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    if args.check:
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                print(f'stale generated artifact: {path.relative_to(REPO)}')
                return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
