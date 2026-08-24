#!/usr/bin/env python3
"""Consolidate H3.1 steady-DC evidence and close the phase."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
STATES = REPO / "hardware/verification/generated/H3-VRF11-power-state-register.json"
RAILS = REPO / "hardware/verification/generated/H3-VRF12-dc-budget.json"
SOURCES = REPO / "hardware/verification/generated/H3-VRF13-source-charge-budget.json"
METHODS = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF14-dc-consolidation.json"
DOC_EN = REPO / "docs/dc-verification-result.md"
DOC_RU = REPO / "docs/dc-verification-result.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    states = json.loads(STATES.read_text(encoding="utf-8"))
    rails = json.loads(RAILS.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    checks = {
        "all_states_enumerated": states["summary"]["legal_states"] == 2032 and states["summary"]["invariant_violations"] == 0,
        "all_rail_profiles_pass": rails["summary"]["rail_profiles_evaluated"] == 200 and rails["summary"]["failed_profiles"] == 0,
        "every_state_has_source_result": sources["summary"]["states_evaluated"] == states["summary"]["legal_states"],
        "source_and_pack_safety_pass": sources["summary"]["failed_states"] == 0,
        "no_unresolved_numeric_input": rails["summary"]["unresolved_numeric_inputs"] == 0 and sources["summary"]["unresolved_numeric_inputs"] == 0,
        "pf02_margin_rule_present": any(row["id"] == "PF-02" for row in methods["pass_fail_rules"]),
        "calculation_findings_corrected": rails["summary"]["corrected_findings"] == len(rails["corrections"]) == 2,
        "source_limits_are_explicit": sources["summary"]["source_limited_profiles_explicitly_refused"] > 0,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    if failed_checks:
        raise ValueError("H3.1 consolidation failed: " + ", ".join(failed_checks))

    manifest = {
        "schema_version": 1,
        "stage": "H3.1.4",
        "status": "reviewed_h3_1_steady_dc_phase_complete",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (STATES, RAILS, SOURCES, METHODS)},
        "checks": checks,
        "accepted_results": {
            "source_charge_states": states["summary"]["source_charge_states"],
            "complete_power_states": states["summary"]["legal_states"],
            "load_profiles": rails["summary"]["operating_profiles"],
            "rail_profiles": rails["summary"]["rail_profiles_evaluated"],
            "minimum_rail_hardware_reserve_percent": rails["summary"]["minimum_hardware_reserve_percent"],
            "maximum_sys_demand_w": sources["summary"]["maximum_sys_demand_w"],
            "maximum_pack_discharge_a": sources["summary"]["maximum_pack_discharge_a"],
            "pack_hardware_reserve_percent_at_worst": sources["summary"]["pack_hardware_reserve_percent_at_worst"],
            "maximum_rail_conversion_loss_w": sources["summary"]["maximum_rail_conversion_loss_w"],
            "maximum_efuse_conduction_loss_w": sources["summary"]["maximum_efuse_conduction_loss_w"],
            "usb_5v3a_profiles_explicitly_refused_without_pack": sources["summary"]["source_limited_profiles_explicitly_refused"],
            "charge_states_derated_by_dpm": sources["summary"]["charge_states_derated_by_dpm"],
            "failed_checks": len(failed_checks),
        },
        "corrections": rails["corrections"],
        "conditional_admissions": [
            "5-V fallback without a healthy pack is AON diagnostics only until source-advertised current and DPM headroom are measured",
            "5-V/3-A USB-only refuses the 14 declared heavy profiles that exceed the conservative cascaded-efficiency budget",
            "a healthy pack may supplement an insufficient USB source within the proven 2.833-A worst-case discharge envelope",
            "charge current is a request, not an entitlement: DPM reduces it to zero or available headroom before system load",
        ],
        "downstream_inputs": {
            "H3.2": "model dynamic startup/shutdown, handover, DPM, eFuse and load-step behavior against the accepted steady endpoints",
            "H3.6": "use 2.550-W maximum rail conversion loss and 0.386-W maximum eFuse conduction loss as conservative thermal sources",
            "H6": "preserve the converter, eFuse, current-sense and high-current return placement/routing constraints",
            "H8": "measure all four rail currents, conversion efficiency, pack current and DPM behavior at named worst profiles",
        },
        "residual_physical_only": sorted(set(rails["residual_physical_gates"] + sources["residual_physical_gates"])),
        "review_summary": {
            "unresolved_findings": 0,
            "corrected_findings": len(rails["corrections"]),
            "phase_status": "reviewed",
        },
        "next": {"stage": "H3.2.1", "action": "model startup, orderly shutdown and hard FAULT_KILL shutdown"},
        "open_findings": [],
    }
    return {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }, manifest


def render_doc(manifest: dict, russian: bool) -> str:
    r = manifest["accepted_results"]
    corrections = manifest["corrections"]
    if russian:
        title = "# Результат проверки постоянного питания"
        nav = "[English](dc-verification-result.md) · [На главную](../README.ru.md) · [DC-шины](dc-power-budget.ru.md) · [Источники](source-charge-budget.ru.md)"
        intro = "H3.1 завершена как единая проверка: реестр состояний → нагрузки шин → источники/заряд/разряд → сводное ревью. Ни один следующий вывод не основан на типовом токе вместо maximum или принятого admission limit."
        result_h = "## Принятый результат"
        result = (
            f"- `{r['source_charge_states']}` source/charge состояния, `{r['complete_power_states']}` полных состояния и `{r['rail_profiles']}` rail-профилей проверены без незакрытых нарушений.\n"
            f"- Минимальный запас защиты шин: `{r['minimum_rail_hardware_reserve_percent']}%`.\n"
            f"- Worst case SYS: `{r['maximum_sys_demand_w']} Вт`; pack: `{r['maximum_pack_discharge_a']} А` с запасом `{r['pack_hardware_reserve_percent_at_worst']}%` до 10-А контракта.\n"
            f"- 5 В × 3 А без pack явно отказывает `{r['usb_5v3a_profiles_explicitly_refused_without_pack']}` тяжёлым профилям; это admission control, а не скрытая просадка."
        )
        correction_h = "## Исправлено во время ревью"
        correction_text = "\n".join((
            "- При старом RILM 2,21 кОм гарантированный минимум внешнего eFuse составлял лишь 1,358 А — меньше требуемых PF-02 1,5625 А для порта 1,25 А. Оба eFuse U214/Unit получили серийный Yageo RC0402FR-071K82L 1,82 кОм: теперь диапазон 1,632–2,035 А, постоянный запас не менее 30,6%, а ограниченный 2-А пусковой импульс и контракт разъёма сохранены.",
            "- Бюджет audio ошибочно опирался на 8-омную кривую PAM8302A при выбранном динамике 4 Ом ±15%, а backlight одновременно считался по fault threshold вместо normal reference. Исправленные допуски 625 мА audio и 200 мА display/backlight дают worst case 3V3_MAIN 2 493 мА и 28,36% аппаратного запаса.",
        ))
        next_h = "## Что ещё не доказано"
        next_text = "Постоянные пределы не заменяют динамику и температуру. H3.2 проверяет startup/shutdown, USB↔pack handover, brownout, DPM, inrush и FAULT_KILL; H3.6 получает 2,550 Вт converter-loss и 0,386 Вт eFuse-loss для thermal model; H8 оставляет реальные измерения."
        marker = "**Статус:** `H3.1` завершено и проверено. Текущий точный маркер — `H3.4.1`, digital levels/defaults и no-back-power."
        evidence = "[Машинный пакет закрытия H3.1](../hardware/verification/generated/H3-VRF14-dc-consolidation.json)."
    else:
        title = "# Steady-power verification result"
        nav = "[Русский](dc-verification-result.ru.md) · [Home](../README.md) · [DC rails](dc-power-budget.md) · [Sources](source-charge-budget.md)"
        intro = "H3.1 closes as one chain: state register → rail loads → source/charge/discharge → consolidated review. No result substitutes a typical current for a maximum or accepted admission limit."
        result_h = "## Accepted result"
        result = (
            f"- `{r['source_charge_states']}` source/charge states, `{r['complete_power_states']}` complete states and `{r['rail_profiles']}` rail profiles pass with no unresolved violation.\n"
            f"- Minimum rail protection reserve: `{r['minimum_rail_hardware_reserve_percent']}%`.\n"
            f"- Worst SYS case: `{r['maximum_sys_demand_w']} W`; pack: `{r['maximum_pack_discharge_a']} A`, with `{r['pack_hardware_reserve_percent_at_worst']}%` reserve to the 10-A contract.\n"
            f"- 5 V × 3 A without a pack explicitly refuses `{r['usb_5v3a_profiles_explicitly_refused_without_pack']}` heavy profiles; this is admission control, not a hidden brownout."
        )
        correction_h = "## Corrected during review"
        correction_text = "\n".join(
            f"- {correction['finding']}. Correction: {correction['correction']}. Functional effect: {correction['functional_effect']}."
            for correction in corrections
        )
        next_h = "## What remains unproven"
        next_text = "Steady limits do not replace dynamics or temperature. H3.2 checks startup/shutdown, USB↔pack handover, brownout, DPM, inrush and FAULT_KILL; H3.6 consumes the 2.550-W converter loss and 0.386-W eFuse loss in its thermal model; H8 retains physical measurements."
        marker = "**Status:** `H3.1` is reviewed. The exact current marker is `H3.4.1`, digital levels/defaults and no-back-power."
        evidence = "[Machine H3.1 closure package](../hardware/verification/generated/H3-VRF14-dc-consolidation.json)."
    return "\n\n".join((title, nav, intro, result_h, result, correction_h, correction_text, next_h, next_text, marker, evidence)) + "\n"


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
        print("ok: H3.1 consolidated; reviewed, 0 unresolved findings, next H3.2.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
