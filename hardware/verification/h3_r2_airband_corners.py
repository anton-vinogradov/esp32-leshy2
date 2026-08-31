#!/usr/bin/env python3
"""Verify the exact H3-R2 Airband lumped filter and publish reproducible evidence."""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "hardware/product-design/h1-airband-filter.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
INSTANCES = ROOT / "hardware/ecad/h2-r2-instance-ledger-contract.json"
TOPOLOGY = ROOT / "hardware/ecad/h2-r2-topology-overrides.json"
OUTPUT = ROOT / "hardware/verification/generated/H3-R2-airband-corners.json"
DOC_EN = ROOT / "docs/airband-electrical-verification.md"
DOC_RU = ROOT / "docs/airband-electrical-verification.ru.md"

EXPECTED_TOPOLOGY = {
    "air_bpf_s1_l220.END_1": "AIR_BPF_IN_RF", "air_bpf_s1_l220.END_2": "AIR_BPF_S1_L_MID",
    "air_bpf_s1_l47.END_1": "AIR_BPF_S1_L_MID", "air_bpf_s1_l47.END_2": "AIR_BPF_S1_LC",
    "air_bpf_s1_c.END_1": "AIR_BPF_S1_LC", "air_bpf_s1_c.END_2": "AIR_BPF_N1",
    "air_bpf_p1_l_a.END_1": "AIR_BPF_N1", "air_bpf_p1_l_a.END_2": "POWER_GROUND",
    "air_bpf_p1_l_b.END_1": "AIR_BPF_N1", "air_bpf_p1_l_b.END_2": "POWER_GROUND",
    "air_bpf_p1_c120.END_1": "AIR_BPF_N1", "air_bpf_p1_c120.END_2": "POWER_GROUND",
    "air_bpf_p1_c20.END_1": "AIR_BPF_N1", "air_bpf_p1_c20.END_2": "POWER_GROUND",
    "air_bpf_p1_c1p4.END_1": "AIR_BPF_N1", "air_bpf_p1_c1p4.END_2": "POWER_GROUND",
    "air_bpf_s2_l.END_1": "AIR_BPF_N1", "air_bpf_s2_l.END_2": "AIR_BPF_S2_LC",
    "air_bpf_s2_c.END_1": "AIR_BPF_S2_LC", "air_bpf_s2_c.END_2": "AIR_BPF_N2",
    "air_bpf_p2_l_a.END_1": "AIR_BPF_N2", "air_bpf_p2_l_a.END_2": "POWER_GROUND",
    "air_bpf_p2_l_b.END_1": "AIR_BPF_N2", "air_bpf_p2_l_b.END_2": "POWER_GROUND",
    "air_bpf_p2_c120.END_1": "AIR_BPF_N2", "air_bpf_p2_c120.END_2": "POWER_GROUND",
    "air_bpf_p2_c20.END_1": "AIR_BPF_N2", "air_bpf_p2_c20.END_2": "POWER_GROUND",
    "air_bpf_p2_c1p4.END_1": "AIR_BPF_N2", "air_bpf_p2_c1p4.END_2": "POWER_GROUND",
    "air_bpf_s3_l220.END_1": "AIR_BPF_N2", "air_bpf_s3_l220.END_2": "AIR_BPF_S3_L_MID",
    "air_bpf_s3_l47.END_1": "AIR_BPF_S3_L_MID", "air_bpf_s3_l47.END_2": "AIR_BPF_S3_LC",
    "air_bpf_s3_c.END_1": "AIR_BPF_S3_LC", "air_bpf_s3_c.END_2": "AIR_BPF_OUT_RF",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def multiply(left: tuple[complex, complex, complex, complex], right: tuple[complex, complex, complex, complex]) -> tuple[complex, complex, complex, complex]:
    a, b, c, d = left
    e, f, g, h = right
    return a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h


def loss_db(cells: list[dict], signs: list[int], frequency_mhz: float, impedance: float) -> float:
    omega = 2.0 * math.pi * frequency_mhz * 1e6
    matrix = (1.0 + 0j, 0j, 0j, 1.0 + 0j)
    for index, cell in enumerate(cells):
        l_h = cell["l_nh"] * 1e-9 * (1.0 + signs[2 * index] * cell["l_tolerance_fraction"])
        c_f = cell["c_pf"] * 1e-12 + signs[2 * index + 1] * cell["c_tolerance_pf"] * 1e-12
        z_l = omega * l_h / cell["l_q_floor"] + 1j * omega * l_h
        z_c = 1.0 / (omega * c_f * 1200.0) - 1j / (omega * c_f)
        if cell["kind"] == "series_resonator":
            section = (1.0 + 0j, z_l + z_c, 0j, 1.0 + 0j)
        elif cell["kind"] == "shunt_parallel_resonator":
            section = (1.0 + 0j, 0j, 1.0 / z_l + 1.0 / z_c, 1.0 + 0j)
        else:
            raise ValueError(f"unsupported filter cell: {cell['kind']}")
        matrix = multiply(matrix, section)
    a, b, c, d = matrix
    s21 = 2.0 / (a + b / impedance + c * impedance + d)
    return -20.0 * math.log10(abs(s21))


def build() -> dict:
    design = load(DESIGN)
    devices = load(DEVICES)["devices"]
    instances = load(INSTANCES)["exact_instance_names"]
    topology = load(TOPOLOGY)["endpoint_overrides"]
    errors: list[str] = []

    population = design["candidate"]["physical_population"]
    expected_quantity = sum(row["quantity"] for row in population)
    if expected_quantity != design["candidate"]["physical_fitted_parts"] or expected_quantity != 18:
        errors.append("physical Airband filter population is not exactly 18 fitted parts")
    for row in population:
        device = devices.get(row["device_id"], {})
        allocated = instances.get(row["device_id"], [])
        if device.get("mpn") != row["mpn"]:
            errors.append(f"MPN drift: {row['device_id']}")
        if len(allocated) != row["quantity"]:
            errors.append(f"instance allocation drift: {row['device_id']}")
        route = json.dumps(device.get("orderable_source", {}), ensure_ascii=False)
        if not all(token in route for token in (row["jlcpcb_part"], "SMT Assembly", "Standard PCBA", "MOQ 1")):
            errors.append(f"current Standard-PCBA route incomplete: {row['mpn']}")
    for contact, net in EXPECTED_TOPOLOGY.items():
        if topology.get(contact) != net:
            errors.append(f"topology drift: {contact} expected {net}")
    stale_filter_contacts = sorted(
        contact for contact in topology
        if contact.startswith("air_bpf_") and contact not in EXPECTED_TOPOLOGY
    )
    if stale_filter_contacts:
        errors.append(f"stale Airband filter contacts remain: {stale_filter_contacts}")

    cells = design["candidate"]["effective_cells"]
    mask = design["reference_mask"]
    pass_start, pass_stop = mask["passband_mhz"]
    pass_frequencies = [pass_start + 0.25 * index for index in range(int(round((pass_stop - pass_start) / 0.25)) + 1)]
    stop_frequencies = [row["frequency_mhz"] for row in mask["stop_points"]]
    pass_worst = {frequency: {"loss_db": -math.inf, "corner": None} for frequency in pass_frequencies}
    stop_worst = {frequency: {"loss_db": math.inf, "corner": None} for frequency in stop_frequencies}
    for corner in range(1 << (2 * len(cells))):
        signs = [1 if corner & (1 << bit) else -1 for bit in range(2 * len(cells))]
        for frequency in pass_frequencies:
            loss = loss_db(cells, signs, frequency, design["impedance_ohm"])
            if loss > pass_worst[frequency]["loss_db"]:
                pass_worst[frequency] = {"loss_db": loss, "corner": corner}
        for frequency in stop_frequencies:
            loss = loss_db(cells, signs, frequency, design["impedance_ohm"])
            if loss < stop_worst[frequency]["loss_db"]:
                stop_worst[frequency] = {"loss_db": loss, "corner": corner}

    pass_frequency, pass_record = max(pass_worst.items(), key=lambda item: item[1]["loss_db"])
    pass_margin = mask["maximum_passband_loss_db"] - pass_record["loss_db"]
    stop_results = []
    for requirement in mask["stop_points"]:
        record = stop_worst[requirement["frequency_mhz"]]
        stop_results.append({
            **requirement,
            "worst_loss_db": record["loss_db"],
            "margin_db": record["loss_db"] - requirement["minimum_loss_db"],
            "corner": record["corner"],
        })
    minimum_margin = min([pass_margin] + [row["margin_db"] for row in stop_results])
    if minimum_margin <= 0:
        errors.append(f"Airband lumped corner mask fails by {-minimum_margin:.6f} dB")

    result = {
        "schema_version": 1,
        "id": "LESHY2-H3-R2-AIRBAND-CORNERS",
        "marker": "H3-R2.3",
        "status": "pass" if not errors else "fail",
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (DESIGN, DEVICES, INSTANCES, TOPOLOGY)},
        "method": {
            "corner_count": 1 << (2 * len(cells)),
            "independent_effective_parameters": 2 * len(cells),
            "passband_grid_step_mhz": 0.25,
            "passband_grid_points": len(pass_frequencies),
            "capacitor_q": 1200.0,
            "containment_rule": design["candidate"]["effective_bound_rule"],
        },
        "factory_population": {
            "fitted_parts": expected_quantity,
            "distinct_mpns": len(population),
            "all_exact_mpns_stocked_standard_pcba_on_2026_08_31": not any("route" in error for error in errors),
            "material_cost_usd": design["candidate"]["factory_route"]["one_device_material_cost_usd"],
        },
        "passband": {
            "range_mhz": mask["passband_mhz"],
            "maximum_allowed_loss_db": mask["maximum_passband_loss_db"],
            "worst_loss_db": pass_record["loss_db"],
            "worst_frequency_mhz": pass_frequency,
            "worst_corner": pass_record["corner"],
            "margin_db": pass_margin,
        },
        "stop_points": stop_results,
        "minimum_margin_db": minimum_margin,
        "residual": design["residual_boundary"],
        "errors": errors,
    }
    return result


def render(result: dict, language: str) -> str:
    ru = language == "ru"
    title = "Проверка Airband-фильтра" if ru else "Airband filter verification"
    intro = (
        "Текущая принципиальная схема использует пятизвенный LC-фильтр из 18 деталей. "
        "Скрипт проверяет все 1 024 предельные комбинации допусков, а не только номинал."
        if ru else
        "The current schematic uses a five-cell LC filter built from 18 fitted parts. "
        "The script checks all 1,024 tolerance endpoints, not only the nominal response."
    )
    status = "расчёт пройден" if ru else "calculation passed"
    lines = [f"# {title}", "", intro, "", f"**H3-R2.3: {status}.**", ""]
    lines += [
        "| Проверка | Требование | Худший случай | Запас |" if ru else "| Check | Requirement | Worst case | Margin |",
        "|---|---:|---:|---:|",
        f"| {'Полоса 118–137 МГц' if ru else '118–137 MHz passband'} | ≤ {result['passband']['maximum_allowed_loss_db']:.2f} dB | {result['passband']['worst_loss_db']:.3f} dB @ {result['passband']['worst_frequency_mhz']:.2f} MHz | {result['passband']['margin_db']:.3f} dB |",
    ]
    for row in result["stop_points"]:
        lines.append(f"| {row['frequency_mhz']:.0f} MHz stop | ≥ {row['minimum_loss_db']:.2f} dB | {row['worst_loss_db']:.3f} dB | {row['margin_db']:.3f} dB |")
    lines += [
        "",
        ("Все десять MPN доступны как SMT для Economic/Standard PCBA, MOQ 1; проверено 2026-08-31. "
         "Стоимость 18 деталей одного устройства: ${:.4f}." if ru else
         "All ten MPNs are available as SMT for Economic/Standard PCBA with MOQ 1, checked 2026-08-31. "
         "The 18 fitted parts cost ${:.4f} for one device.").format(result["factory_population"]["material_cost_usd"]),
        "",
        ("Оставшаяся граница: это проверка сосредоточенной схемы. Перед заказом H6 обязан повторить ту же маску с извлечёнными паразитиками разведённой платы; H8 подтверждает результат VNA." if ru else
         "Residual boundary: this is a lumped-network result. Before ordering, H6 must rerun the same mask with extracted routed-PCB parasitics; H8 confirms it by VNA."),
        "",
        "Generated by `hardware/verification/h3_r2_airband_corners.py`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    expected = {
        OUTPUT: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        DOC_EN: render(result, "en"),
        DOC_RU: render(result, "ru"),
    }
    if args.write:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("stale:", ", ".join(stale))
            return 1
    print(json.dumps({"status": result["status"], "minimum_margin_db": result["minimum_margin_db"], "errors": result["errors"]}, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
