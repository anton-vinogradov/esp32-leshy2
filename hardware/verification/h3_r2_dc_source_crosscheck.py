#!/usr/bin/env python3
"""Cross-check and publish the reviewed H3-R2.1 DC/source result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PLAN = REPO / "hardware/verification/h3-r2-verification-plan.json"
METHODS = REPO / "hardware/verification/generated/H3-R2-method-contract.json"
STATES = REPO / "hardware/verification/generated/H3-R2-power-state-register.json"
LOADS = REPO / "hardware/verification/generated/H3-R2-load-binding.json"
RAILS = REPO / "hardware/verification/generated/H3-R2-rail-margins.json"
SOURCES = REPO / "hardware/verification/generated/H3-R2-source-margins.json"
OUTPUT = REPO / "hardware/verification/generated/H3-R2-dc-source-crosscheck.json"
DOC_EN = REPO / "docs/power-dc-source-result.md"
DOC_RU = REPO / "docs/power-dc-source-result.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    states = json.loads(STATES.read_text(encoding="utf-8"))
    loads = json.loads(LOADS.read_text(encoding="utf-8"))
    rails = json.loads(RAILS.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    rail_ownership = {row["instance_uid"]: row["owner"] for row in rails["ownership"]}
    source_ownership = {row["instance_uid"]: row["owner"] for row in sources["ownership"]}
    deferred = {uid for uid, owner in rail_ownership.items() if owner == "deferred_h3_r2_1_4"}
    numeric = {uid for uid, owner in rail_ownership.items() if owner != "deferred_h3_r2_1_4"}
    all_load_uids = {row["instance_uid"] for row in loads["load_lines"]}
    all_load_uids.update(f"EXTERNAL:{row['id']}" for row in loads["external_load_lines"])
    rules = {row["id"] for row in methods["pass_fail_rules"]}
    required_rules = {"PF-R2-01", "PF-R2-02", "PF-R2-03", "PF-R2-04", "PF-R2-07", "PF-R2-11"}
    checks = {
        "plan_closes_h3_r2_1": (
            next(row for row in plan["substeps"] if row["id"] == "H3-R2.1")["status"] == "reviewed"
            and next(
                detail
                for row in plan["substeps"] if row["id"] == "H3-R2.1"
                for detail in row["details"] if detail["id"] == "H3-R2.1.5"
            )["status"] == "reviewed"
        ),
        "state_register_passes": states["status"] == "pass" and states["summary"]["invariant_violations"] == 0,
        "all_2266_states_exist": states["summary"]["legal_states"] == 2266 == sources["summary"]["states_evaluated"],
        "all_56_profiles_exist": states["summary"]["operating_profiles"] == 56 == len(rails["profiles"]),
        "all_224_rail_profiles_exist": rails["summary"]["rail_profiles_evaluated"] == 224,
        "all_current_loads_are_bound": len(all_load_uids) == rails["summary"]["physical_and_external_lines_owned"],
        "rail_ownership_exact": set(rail_ownership) == all_load_uids,
        "numeric_and_deferred_partition": numeric.isdisjoint(deferred) and numeric | deferred == all_load_uids,
        "all_77_deferred_lines_are_source_owned": len(deferred) == 77 and set(source_ownership) == deferred,
        "no_hidden_load_or_source_allowance": loads["summary"]["hidden_miscellaneous_allowances"] == 0 == rails["summary"]["hidden_miscellaneous_allowances"] == sources["summary"]["hidden_miscellaneous_allowances"],
        "rail_current_voltage_thermal_pass": rails["summary"]["current_failures"] == rails["summary"]["voltage_failures"] == rails["summary"]["steady_thermal_failures"] == 0,
        "all_source_states_safe": sources["summary"]["failed_states"] == 0,
        "oversized_usb_only_profiles_are_refused": sources["summary"]["usb_only_profiles_refused"] == 14,
        "method_rules_present": required_rules <= rules,
        "ordering_stays_blocked": not any(plan["authorization"][key] for key in ("pcb_placement_and_routing", "fabrication", "purchasing")),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ValueError("H3-R2.1.5 cross-check failures: " + ", ".join(failures))
    manifest = {
        "schema_version": 1,
        "artifact": "H3-R2-dc-source-crosscheck",
        "marker": "H3-R2.1.5",
        "status": "reviewed_h3_r2_1_worst_case_dc_source_charge_and_power_states",
        "source_sha256": {str(path.relative_to(REPO)): sha256(path) for path in (METHODS, STATES, LOADS, RAILS, SOURCES)},
        "checks": checks,
        "coverage": {
            "legal_states": 2266,
            "operating_profiles": 56,
            "rail_profiles": 224,
            "physical_and_external_loads": len(all_load_uids),
            "direct_numeric_rail_owners": len(numeric),
            "source_pack_owners": len(deferred),
            "pass_fail_rules_used": sorted(required_rules),
        },
        "result": {
            "minimum_rail_current_reserve_percent": rails["summary"]["minimum_electrical_reserve_percent"],
            "minimum_junction_margin_c": rails["summary"]["minimum_junction_margin_c"],
            "maximum_sys_demand_w": sources["summary"]["maximum_sys_demand_w"],
            "maximum_pack_discharge_a": sources["summary"]["maximum_pack_discharge_a"],
            "maximum_sustained_pack_discharge_a": sources["summary"]["maximum_sustained_pack_discharge_a"],
            "pack_reserve_percent_at_worst": sources["summary"]["pack_reserve_percent_at_worst"],
            "usb_only_profiles_refused": sources["summary"]["usb_only_profiles_refused"],
            "charge_states_derated": sources["summary"]["charge_states_derated"],
        },
        "corrections": rails["corrections"],
        "conditional_admissions": [
            "unknown 5-V fallback contributes zero assumed watts until source current and DPM headroom are measured",
            "5-V/3-A USB-only refuses fourteen oversized profiles; a healthy pack may supplement",
            "external 5 V retains a 1.25-A electrical ceiling and a 1.00-A sustained admission until H6/H8",
            "SUPPORT_WORST is an electrical simultaneous corner, not unattended permission",
        ],
        "residual_gates": {
            "H3-R2.2": "startup, shutdown, inrush, DPM, brownout and USB/pack handover",
            "H3-R2.6": "joined component/enclosure thermal and single-fault proof",
            "H6": "routed resistance, parasitics and post-route re-analysis",
            "H8": "measured currents, efficiencies, temperatures and handover",
        },
        "authorization": {"pcb_placement_or_routing": False, "purchasing": False, "fabrication": False},
        "next": {"marker": "H3-R2.2.1", "action": "verify ordered startup, shutdown, reset and recovery sequencing"},
        "errors": [],
    }
    return {OUTPUT: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", DOC_EN: render_doc(manifest, False), DOC_RU: render_doc(manifest, True)}, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    c = manifest["coverage"]
    r = manifest["result"]
    if russian:
        title = "# Итог DC, источников и заряда · H3-R2.1"
        nav = "[English](power-dc-source-result.md) · [Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [Шины](power-rail-margins.ru.md) · [Источники](power-source-margins.ru.md)"
        intro = "`H3-R2.1.5` завершает cross-check первого workstream H3. Это проведённое ревью H3-R2.1, а не всей фазы H3 и не разрешение на KiCad или заказ."
        coverage_h = "## Покрытие"
        coverage = f"Сверены `{c['legal_states']}` состояния, `{c['operating_profiles']}` рабочих профиля, `{c['rail_profiles']}` rail-corner, `{c['physical_and_external_loads']}` нагрузок и все `{c['source_pack_owners']}` source/pack-строки. Пропусков, дублей и скрытой строки «прочее» нет."
        result_h = "## Что доказано"
        result = (f"- Минимальный запас тока шин: `{r['minimum_rail_current_reserve_percent']}%`; температуры кристалла: `{r['minimum_junction_margin_c']} °C`.\n"
                  f"- Максимальный SYS: `{r['maximum_sys_demand_w']} Вт`; pack: `{r['maximum_pack_discharge_a']} А`, длительно `{r['maximum_sustained_pack_discharge_a']} А`.\n"
                  f"- 5 В × 3 А безопасно отказывает `{r['usb_only_profiles_refused']}` тяжёлым USB-only состояниям; заряд снижается раньше нагрузки в `{r['charge_states_derated']}` состояниях.\n"
                  "- 9 В × 3 А и 15 В × 2 А запускают любой объявленный профиль.")
        boundary_h = "## Что дальше"
        boundary = "`H3-R2.2` проверяет динамику: запуск, shutdown, inrush, DPM, brownout, watchdog и USB↔pack handover. Routed parasitics остаются H6, измерения — H8."
        end = "**H3-R2.1 полностью проведён ревью.** Актуальная точка указана в [роадмапе](roadmap.ru.md). Placement, routing, закупка и печать по-прежнему запрещены.\n\n[Машинный cross-check](../hardware/verification/generated/H3-R2-dc-source-crosscheck.json)."
    else:
        title = "# DC, source and charge result · H3-R2.1"
        nav = "[Русский](power-dc-source-result.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [Rails](power-rail-margins.md) · [Sources](power-source-margins.md)"
        intro = "`H3-R2.1.5` completes the first H3 workstream cross-check. H3-R2.1 is reviewed; the whole H3 phase is not, and neither KiCad nor ordering is authorized."
        coverage_h = "## Coverage"
        coverage = f"The check reconciles `{c['legal_states']}` states, `{c['operating_profiles']}` operating profiles, `{c['rail_profiles']}` rail corners, `{c['physical_and_external_loads']}` loads and all `{c['source_pack_owners']}` source/pack lines. No gap, duplicate or hidden miscellaneous line remains."
        result_h = "## What is proved"
        result = (f"- Minimum rail-current reserve: `{r['minimum_rail_current_reserve_percent']}%`; junction-temperature reserve: `{r['minimum_junction_margin_c']} °C`.\n"
                  f"- Maximum SYS: `{r['maximum_sys_demand_w']} W`; pack: `{r['maximum_pack_discharge_a']} A`, sustained `{r['maximum_sustained_pack_discharge_a']} A`.\n"
                  f"- 5 V × 3 A safely refuses `{r['usb_only_profiles_refused']}` heavy USB-only states; charge yields before load in `{r['charge_states_derated']}` states.\n"
                  "- 9 V × 3 A and 15 V × 2 A run every declared profile.")
        boundary_h = "## Next boundary"
        boundary = "`H3-R2.2` verifies dynamics: startup, shutdown, inrush, DPM, brownout, watchdog and USB↔pack handover. Routed parasitics remain H6 and measurement remains H8."
        end = "**H3-R2.1 is fully reviewed.** The [roadmap](roadmap.md) carries the live marker. Placement, routing, purchasing and fabrication remain forbidden.\n\n[Machine cross-check](../hardware/verification/generated/H3-R2-dc-source-crosscheck.json)."
    return "\n\n".join((title, nav, intro, coverage_h, coverage, result_h, result, boundary_h, boundary, end)) + "\n"


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
        print(f"wrote H3-R2.1.5: {len(manifest['checks'])} cross-checks")
        return 0
    stale = [str(path.relative_to(REPO)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        raise SystemExit("stale H3-R2.1.5 artifacts: " + ", ".join(stale))
    print(f"ok: H3-R2.1 reviewed; {len(manifest['checks'])} cross-checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
