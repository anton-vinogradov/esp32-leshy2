#!/usr/bin/env python3
"""Publish the current Airband filter feasibility result from one shared solver."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
MODEL_PATH = REPO / "hardware/product-design/h1-airband-filter.json"
SOLVER_PATH = REPO / "hardware/verification/h3_r2_airband_corners.py"
AUDIT_PATH = REPO / "hardware/product-design/generated/H1-Airband-filter-audit.json"
SVG_PATH = REPO / "docs/images/h1-airband-filter.svg"
EN_DOC_PATH = REPO / "docs/h1-airband-filter.md"
RU_DOC_PATH = REPO / "docs/h1-airband-filter.ru.md"


def _load_solver():
    spec = importlib.util.spec_from_file_location("h3_r2_airband_corners", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SOLVER = _load_solver()


def load() -> dict:
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def audit(model: dict) -> dict:
    result = SOLVER.build()
    return {
        "schema_version": 2,
        "marker": model["marker"],
        "status": result["status"],
        "candidate_is_production_frozen": False,
        "lumped_topology_is_reviewed": result["status"] == "pass",
        "corner_count": result["method"]["corner_count"],
        "nominal_and_corner_model": result,
        "factory_population": model["candidate"]["physical_population"],
        "factory_route": model["candidate"]["factory_route"],
        "residual_boundary": model["residual_boundary"],
    }


def render_svg(model: dict, result: dict) -> str:
    width, height = 1120, 570
    left, top, plot_w, plot_h = 78, 92, 720, 390
    f_min, f_max, loss_max = 80.0, 220.0, 60.0
    cells = model["candidate"]["effective_cells"]
    signs = [0] * (2 * len(cells))

    def x(frequency: float) -> float:
        return left + (frequency - f_min) / (f_max - f_min) * plot_w

    def y(loss: float) -> float:
        return top + plot_h - min(loss, loss_max) / loss_max * plot_h

    samples = [(float(f), SOLVER.loss_db(cells, signs, float(f), model["impedance_ohm"])) for f in range(80, 221)]
    path = " ".join(("M" if index == 0 else "L") + f" {x(f):.2f} {y(loss):.2f}" for index, (f, loss) in enumerate(samples))
    h3 = result["nominal_and_corner_model"]
    esc = html.escape
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="1120" height="570" fill="#ffffff"/>',
        f'<text x="36" y="38" font-family="sans-serif" font-size="25" font-weight="700" fill="#172033">Leshy2 · {esc(model["marker"])} Airband filter</text>',
        '<text x="36" y="64" font-family="sans-serif" font-size="13" fill="#526076">Exact 18-part factory BOM · all 1,024 effective tolerance endpoints pass the reference mask</text>',
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
        '<text x="840" y="112" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Bounded result</text>',
        f'<text x="840" y="146" font-family="sans-serif" font-size="12" fill="#166534">✓ {h3["method"]["corner_count"]} endpoint corners</text>',
        f'<text x="840" y="171" font-family="sans-serif" font-size="12" fill="#166534">✓ passband worst: {h3["passband"]["worst_loss_db"]:.3f} / 4.500 dB</text>',
        f'<text x="840" y="196" font-family="sans-serif" font-size="12" fill="#166534">✓ minimum lumped margin: {h3["minimum_margin_db"]:.3f} dB</text>',
        '<text x="840" y="238" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Factory route</text>',
        '<text x="840" y="272" font-family="sans-serif" font-size="12" fill="#166534">✓ 10 exact stocked MPNs</text>',
        '<text x="840" y="297" font-family="sans-serif" font-size="12" fill="#166534">✓ 18 SMT parts · MOQ 1</text>',
        f'<text x="840" y="322" font-family="sans-serif" font-size="12" fill="#166534">✓ ${model["candidate"]["factory_route"]["one_device_material_cost_usd"]:.4f} / device</text>',
        '<text x="840" y="366" font-family="sans-serif" font-size="17" font-weight="700" fill="#172033">Still open</text>',
        '<text x="840" y="400" font-family="sans-serif" font-size="12" fill="#b45309">H6 routed-parasitic extraction</text>',
        '<text x="840" y="425" font-family="sans-serif" font-size="12" fill="#b45309">H8 assembled-board VNA check</text>',
        '</svg>',
    ])
    return "\n".join(out) + "\n"


def render_doc(model: dict, result: dict, ru: bool) -> str:
    h3 = result["nominal_and_corner_model"]
    if ru:
        title = f'# {model["marker"]} · входной фильтр Airband'
        intro = 'Большой покупной `BPF-A127+` заменён точной фабрично устанавливаемой LC-сетью без ослабления принятой маски.'
        result_title = '## Результат'
        bullets = [
            f'- Все `{h3["method"]["corner_count"]}` предельные комбинации эффективных допусков проходят; минимальный расчётный запас — `{h3["minimum_margin_db"]:.3f} дБ`.',
            '- Фильтр содержит `18` деталей и `10` точных MPN; все доступны JLCPCB как SMT для Standard PCBA с MOQ 1 на 2026-08-31.',
            f'- Материалы фильтра для одного устройства стоят `${model["candidate"]["factory_route"]["one_device_material_cost_usd"]:.4f}` вместо дорогого готового фильтра.',
            '- Это ещё не production freeze: малый запас требует повторить ту же маску в H6 с паразитиками реальной разводки, а H8 подтверждает результат VNA.',
        ]
        population_title = '## Точная устанавливаемая группа'
        next_title = '## Следующий gate'
    else:
        title = f'# {model["marker"]} · Airband input filter'
        intro = 'The large purchased `BPF-A127+` has been replaced by an exact factory-placeable LC network without weakening the accepted mask.'
        result_title = '## Result'
        bullets = [
            f'- All `{h3["method"]["corner_count"]}` effective tolerance endpoints pass; the minimum calculated margin is `{h3["minimum_margin_db"]:.3f} dB`.',
            '- The filter has `18` fitted parts and `10` exact MPNs; all were live JLCPCB SMT routes for Standard PCBA with MOQ 1 on 2026-08-31.',
            f'- One device uses `${model["candidate"]["factory_route"]["one_device_material_cost_usd"]:.4f}` of filter material instead of the costly purchased filter.',
            '- This is not yet a production freeze: the small margin requires the same H6 mask with routed parasitics, followed by the H8 assembled-board VNA check.',
        ]
        population_title = '## Exact fitted group'
        next_title = '## Next gate'
    lines = [title, '', intro, '', '![Airband filter verification](images/h1-airband-filter.svg)', '', result_title, '', *bullets, '', population_title, '', '| Exact MPN | JLCPCB | Quantity | Role |', '|---|---|---:|---|']
    for row in model['candidate']['physical_population']:
        lines.append(f'| `{row["mpn"]}` | `{row["jlcpcb_part"]}` | {row["quantity"]} | {row["role"]} |')
    lines.extend(['', next_title, '', model['residual_boundary']['h6_gate'] + ' ' + model['residual_boundary']['h8_gate'], ''])
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
        stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding='utf-8') != content]
        if stale:
            print('stale generated artifacts:', ', '.join(stale))
            return 1
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
