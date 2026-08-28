#!/usr/bin/env python3
"""Consolidate H3.4 digital level, timing and boundary-loading evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
INPUTS = {
    "levels": REPO / "hardware/verification/generated/H3-VRF41-digital-levels.json",
    "timing": REPO / "hardware/verification/generated/H3-VRF42-digital-timing.json",
    "boundaries": REPO / "hardware/verification/generated/H3-VRF43-boundary-loading.json",
}
OUTPUT = REPO / "hardware/verification/generated/H3-VRF44-digital-consolidation.json"
DOC_EN = REPO / "docs/digital-verification-result.md"
DOC_RU = REPO / "docs/digital-verification-result.ru.md"
C5_INVARIANT_PATH = REPO / "hardware/architecture/c5-procurement-invariant.json"


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    rows = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    levels, timing, boundaries = (rows[name] for name in ("levels", "timing", "boundaries"))
    check_counts = {name: len(row["checks"]) for name, row in rows.items()}
    leaf_checks = sum(check_counts.values())
    corrections = [item for row in rows.values() for item in row["corrections"]]
    physical = {name: row["residual_physical_only"] for name, row in rows.items()}
    physical_flat = [item for values in physical.values() for item in values]

    level_scope = levels["review_scope"]
    level_model = levels["worst_case_level_model"]
    display = timing["display_storage"]
    audio = timing["audio"]
    nrf = timing["radio_service"]["nrf24"]
    cc = timing["radio_service"]["cc1101"]
    ipc = timing["ipc"]
    m1 = boundaries["m1"]
    expansion = boundaries["expansion_power"]
    u214 = boundaries["u214_signal_loading"]
    service = boundaries["service_boundaries"]
    c5 = json.loads(C5_INVARIANT_PATH.read_text(encoding="utf-8"))

    checks = {
        "all_leaf_checks_pass": all(all(row["checks"].values()) for row in rows.values()),
        "leaf_stages_are_exact": [row["stage"] for row in rows.values()] == ["H3.4.1", "H3.4.2", "H3.4.3"],
        "all_leaf_statuses_are_reviewed": all(row["review_summary"]["status"] == "reviewed" for row in rows.values()),
        "all_leaf_open_findings_are_empty": all(row["open_findings"] == [] for row in rows.values()),
        "leaf_check_count_is_171": leaf_checks == 171,
        "single_self_review_correction_is_preserved": len(corrections) == 1 and "pF-to-ns" in corrections[0],
        "all_19_physical_residuals_are_preserved": len(physical_flat) == 19,
        "physical_residuals_are_nonempty_and_unique": all(item.strip() for item in physical_flat) and len(physical_flat) == len(set(physical_flat)),
        "all_controller_allocations_are_covered": level_scope["controller_allocations"] == 130,
        "all_interface_and_quiet_groups_are_covered": level_scope["interface_groups"] == 13 and level_scope["quiet_contracts"] == 13,
        "all_no_back_power_invariants_are_covered": level_scope["no_back_power_invariants"] == 6,
        "every_direct_route_and_off_pull_check_passes": all(levels["direct_route_checks"].values()) and all(levels["off_safe_pull_checks"].values()),
        "every_interface_has_reset_and_no_back_power_contract": all(row["reset_or_off_state"].strip() and row["no_back_power"].strip() for row in levels["interface_groups"]),
        "worst_lvc_level_margins_are_positive": d(level_model["lvc_cmos_at_vcc_3v"]["guaranteed_high_margin_v"]) >= d("0.2") and d(level_model["lvc_cmos_at_vcc_3v"]["guaranteed_low_margin_v"]) >= d("0.25"),
        "display_quantum_and_sd_stall_are_bounded": d(display["display_quantum_ms"]) <= d(1) and d(display["selected_stall_coverage_ms"]) >= d(display["stall_ms"]),
        "qualified_storage_payload_is_4mbps": display["remaining_storage_payload_bytes_s"] >= 4_000_000,
        "audio_ring_exceeds_twenty_service_quanta": d(audio["ring_ms"]) >= d(20) * d(audio["service_quantum_ms_max"]),
        "three_nrf_serial_drain_fits_fifo_guard": d(nrf["all_three_serial_upper_bound_us"]) < d(nrf["three_level_fifo_guard_us"]),
        "cc_drain_fits_fifo_guard": d(cc["watermark_spi_drain_us"]) < d(cc["watermark_guard_us"]),
        "s3_rp_ipc_covers_all_compatibility_radio_payload": ipc["s3_rp"]["qualified_payload_floor_bytes_s"] > ipc["s3_rp"]["three_nrf_plus_cc_max_payload_bytes_s"],
        "both_ipc_links_have_1_5mbps_floor": ipc["s3_rp"]["qualified_payload_floor_bytes_s"] >= 1_500_000 and ipc["s3_c5"]["qualified_payload_floor_bytes_s"] >= 1_500_000,
        "m1_contact_current_drop_and_rate_pass": d(m1["main"]["current_a_per_contact"]) < d(m1["rating"]["current_a_per_contact"]) and d(m1["main"]["drop_v_max"]) < d("0.030") and d(m1["rate_margin_over_usb2_hs"]) >= d(16),
        "m1_maps_and_local_returns_are_complete": m1["contacts"] == 80 and m1["unique_nets"] == 51 and max(m1["return_and_locality"][key] for key in ("ipc_ground_distance_contacts_max", "usb_ground_distance_contacts_max")) <= 1,
        "expansion_branches_fit_converter_and_efuses": d(expansion["branch_accepted_a"]) < d(expansion["branch_efuse_floor_a"]) and d(expansion["two_branch_trip_floor_a"]) < d(expansion["common_converter_floor_a"]),
        "u214_spi_and_i2c_loading_pass": d(u214["timing_margin_ns"]) > d(40) and d(u214["i2c"]["rise_at_admission_ns"]) < d(u214["i2c"]["rise_ns_max"]),
        "service_vbus_cannot_power_product": service["product_power_from_service_vbus"] is False and d(service["two_ports_four_lines_poweroff_leakage_ua_max"]) <= d(8),
        "resource_ownership_rows_are_unique": len(timing["resource_rows"]) == 9 and len({row["id"] for row in timing["resource_rows"]}) == 9,
        "c5_production_revision_is_dual_source_and_fail_closed": c5["silicon_revision_policy"]["production_floor"] == "v1.2"
        and c5["silicon_revision_policy"]["engineering_only"] == ["v1.0"]
        and set(c5["silicon_revision_policy"]["rejected"]) == {"v0.1", "unknown"}
        and {row["id"] for row in c5["incoming_inspection"]["checks"]} == {"MD_IDENTITY", "EFUSE_SILICON_REVISION"},
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.4.4 checks failed: " + ", ".join(failed))

    manifest = {
        "schema_version": 1,
        "stage": "H3.4.4",
        "status": "reviewed_digital_interface_timing_level_and_loading_consolidation",
        "input_hashes": {str(path.relative_to(REPO)): sha256(path) for path in INPUTS.values()},
        "leaf_summary": {
            name: {"stage": row["stage"], "status": row["status"], "checks": check_counts[name], "corrections": len(row["corrections"]), "physical_residuals": len(row["residual_physical_only"])}
            for name, row in rows.items()
        },
        "consolidated": {
            "leaf_checks": leaf_checks,
            "consolidation_checks": len(checks),
            "failed_checks": 0,
            "source_or_self_review_corrections": len(corrections),
            "unresolved_analytical_findings": 0,
            "physical_only_residuals": len(physical_flat),
            "controller_allocations": level_scope["controller_allocations"],
            "interface_groups": level_scope["interface_groups"],
            "independent_resource_rows": len(timing["resource_rows"]),
        },
        "closed_cross_domain_contracts": {
            "display_storage": "40-MHz direct QSPI with <=1-ms quanta; qualified SD profile retains >=4 MB/s and 512-KiB stall buffering",
            "audio": "48-kHz full-duplex DMA has 21.333-ms ring and a dedicated controller",
            "compatibility_radios": "three independent nRF24 SPI engines plus independent CC1101 SPI service fit their FIFO guards",
            "ipc": "both S3-RP and S3-C5 links admit >=1.5 MB/s without sharing display, storage, audio or radio controllers",
            "quiet_state": "all 13 interface groups have reset/off and no-back-power contracts; inactive interfaces are hardware-quiet",
            "m1_expansion_service": "M1 current/drop/rate, protected extension branches, U214 load and data-only service USB limits pass",
            "c5_revision_admission": "production requires incoming MD/lot identity and eFuse revision >=v1.2; v1.0 is engineering-only and v0.1/unknown fail closed",
        },
        "c5_procurement_invariant": {
            "path": str(C5_INVARIANT_PATH.relative_to(REPO)),
            "sha256": sha256(C5_INVARIANT_PATH),
            "invariant_id": c5["invariant_id"],
            "production_floor": c5["silicon_revision_policy"]["production_floor"],
            "incoming_checks": [row["id"] for row in c5["incoming_inspection"]["checks"]],
        },
        "corrections": corrections,
        "physical_hil_residuals": physical,
        "checks": checks,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.6.1", "action": "build the worst-case board, battery and enclosure thermal model"},
    }

    en = f"""# Consolidated digital-interface result · historical R1

`H3.4` is reviewed: all three leaf packages and `{leaf_checks}` leaf checks pass, followed by `{len(checks)}` cross-domain consolidation checks. No analytical finding remains open. The historical R1 progression marker is `H3.6.1`.

## Closed analytical envelope

| Boundary | Reviewed result |
|---|---|
| Levels and quiet state | 130 controller allocations, 13 interface groups, 13 reset/off contracts and all six no-back-power invariants pass |
| Display and storage | 40-MHz direct QSPI, <=1-ms work quanta, 15.36-ms full-frame payload; qualified SD keeps >=4 MB/s and 512-KiB covers 349.525 ms |
| Audio | 48-kHz stereo full-duplex, 3.072-MHz BCLK and 21.333-ms DMA ring on its own controller |
| Compatibility radios | Three simultaneous full-function nRF24 paths and CC1101 have independent SPI/DMA service; worst serialized nRF drain is 79.2 us inside a 457.5-us guard |
| IPC | Both S3-RP and S3-C5 admit >=1.5 MB/s; S3-RP retains 675 kB/s over the three-nRF-plus-CC theoretical payload |
| M1 and extensions | 80-contact/51-net M1, protected U214/native Unit branches, U214 10-MHz SPI/150-pF I2C and data-only service USB pass |
| C5 revision admission | Official MPN stays `ESP32-C5-WROOM-1U-N8R8`; production requires both incoming MD/lot identity and eFuse revision >=v1.2; v1.0 is engineering-only and v0.1/unknown fail closed |

The one-active-signal-group rule still applies at the product level. It does not serialize the three nRF24 radios: those three remain a deliberately concurrent group with independent engines, full RX/TX/mixed-role operation and bounded FIFO service.

## Physical boundary retained

All `{len(physical_flat)}` residual items remain explicit H5/H8 measurements: far-end levels and eyes, reset/brownout captures, SD specimens, DMA and IPC traces, radio FIFO timing, M1/U214 mating and loading, extension misuse, and multi-host service USB. H3.4 does not relabel them as simulated passes.

One self-review correction is preserved in the evidence: the U214 I2C pF-to-ns conversion was fixed before acceptance; 150 pF now evaluates to 279.609 ns against the 300-ns limit.

Machine evidence: [`H3-VRF44-digital-consolidation.json`](../hardware/verification/generated/H3-VRF44-digital-consolidation.json).
"""
    ru = f"""# Сводный результат digital interfaces · historical R1

`H3.4` проведён ревью: проходят все три leaf-пакета, `{leaf_checks}` их checks и `{len(checks)}` сквозных сводных checks. Незакрытых аналитических findings нет. Исторический маркер прогресса R1 — `H3.6.1`.

## Закрытый аналитический envelope

| Граница | Проверенный результат |
|---|---|
| Levels и quiet state | Проходят 130 controller allocations, 13 interface groups, 13 reset/off contracts и все шесть no-back-power invariants |
| Display и storage | Direct QSPI 40 МГц, work quanta <=1 мс, full-frame payload 15,36 мс; квалифицированная SD сохраняет >=4 МБ/с, а 512 КиБ покрывают 349,525 мс |
| Audio | Full-duplex stereo 48 кГц, BCLK 3,072 МГц и DMA-ring 21,333 мс на отдельном controller |
| Compatibility radios | Три одновременно полнофункциональных nRF24 и CC1101 имеют независимый SPI/DMA service; worst serialized drain трёх nRF равен 79,2 мкс при guard 457,5 мкс |
| IPC | S3-RP и S3-C5 допускают >=1,5 МБ/с; S3-RP сохраняет 675 кБ/с сверх теоретического payload трёх nRF плюс CC |
| M1 и расширения | Проходят M1 на 80 контактов/51 net, защищённые ветки U214/native Unit, U214 SPI 10 МГц/I2C 150 пФ и data-only service USB |
| Допуск ревизии C5 | Официальный MPN остаётся `ESP32-C5-WROOM-1U-N8R8`; production требует одновременно MD/lot identity и eFuse revision >=v1.2; v1.0 только engineering, v0.1/unknown запрещены |

Правило one-active-signal-group остаётся продуктовым. Оно не сериализует три nRF24: это намеренно одновременная группа с независимыми engines, полным RX/TX/mixed-role режимом и ограниченным временем обслуживания FIFO.

## Сохранённая физическая граница

Все `{len(physical_flat)}` остаточных пунктов остаются явными измерениями H5/H8: far-end levels/eyes, reset/brownout captures, экземпляры SD, DMA и IPC traces, timing радио-FIFO, стыковка и loading M1/U214, неправильное использование расширений и service USB с несколькими hosts. H3.4 не переименовывает их в пройденную симуляцию.

В evidence сохранено одно исправление саморевью: пересчёт пФ в нс для U214 I2C исправлен до принятия; 150 пФ теперь дают 279,609 нс при лимите 300 нс.

Машинное evidence: [`H3-VRF44-digital-consolidation.json`](../hardware/verification/generated/H3-VRF44-digital-consolidation.json).
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
            raise SystemExit("stale H3.4.4 artifacts: " + ", ".join(stale))
    print(f"ok: H3.4 reviewed; {manifest['consolidated']['leaf_checks']} leaf + {manifest['consolidated']['consolidation_checks']} consolidation checks, next H3.6.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
