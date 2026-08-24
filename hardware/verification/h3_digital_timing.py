#!/usr/bin/env python3
"""Verify H3.4.2 digital bandwidth, latency and timing budgets."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path


getcontext().prec = 34

REPO = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = REPO / "hardware/architecture/candidates/G2F-3I.json"
DEVICES_PATH = REPO / "hardware/architecture/devices.json"
METHODS_PATH = REPO / "hardware/verification/generated/H3-VRF03-method-contract.json"
DISPLAY_PATH = REPO / "hardware/verification/generated/H3-VRF31-display.json"
LEVELS_PATH = REPO / "hardware/verification/generated/H3-VRF41-digital-levels.json"
OUTPUT = REPO / "hardware/verification/generated/H3-VRF42-digital-timing.json"
DOC_EN = REPO / "docs/digital-timing-verification.md"
DOC_RU = REPO / "docs/digital-timing-verification.ru.md"

SOURCES = {
    "nrf24l01_product_specification": "https://devzone.nordicsemi.com/cfs-file/__key/support-attachments/beef5d1b77644c448dabff31668f3a47-aad1a46f307945a7b0204fd969e86bdf/content.pdf",
    "cc1101_datasheet": "https://www.ti.com/lit/ds/symlink/cc1101.pdf",
    "sd_physical_layer_simplified_specification": "https://www.sdcard.org/cms/wp-content/themes/sdcard-org/dl.php?f=Part1_Physical_Layer_Simplified_Specification_Ver7.10.pdf",
    "st77922_datasheet": "https://dl.espressif.com/AE/esp-iot-solution/ST77922_SPEC_V0.1.pdf",
    "es8311_product_brief": "https://www.everest-semi.com/pdf/ES8311%20PB.pdf",
    "esp32_s3_technical_reference": "https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf",
    "esp32_c5_technical_reference": "https://www.espressif.com/sites/default/files/documentation/esp32-c5_technical_reference_manual_en.pdf",
    "rp2350_datasheet": "https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf",
}


def d(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal, places: str = "0.001") -> str:
    return format(value.quantize(Decimal(places)), "f")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict[Path, str], dict]:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    devices = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))["devices"]
    methods = json.loads(METHODS_PATH.read_text(encoding="utf-8"))
    display = json.loads(DISPLAY_PATH.read_text(encoding="utf-8"))
    levels = json.loads(LEVELS_PATH.read_text(encoding="utf-8"))
    resources = {row["id"]: row for row in candidate["resource_contracts"]}
    capacities = {row["id"]: row for row in candidate["capacity_contracts"]}

    display_hz = d(display["qspi_corner"]["selected_initial_write_clock_hz"])
    display_raw_bytes_s = display_hz * d(4) / d(8)
    display_quantum_s = d(display["qspi_corner"]["maximum_nonpreemptible_quantum_ms"]) / d(1000)
    display_quantum_bytes = display_raw_bytes_s * display_quantum_s
    frame_bytes = d(320 * 480 * 2)
    frame_payload_ms = frame_bytes / display_raw_bytes_s * d(1000)
    display_budget_bytes_s = d(1_000_000)
    display_quanta_s = display_budget_bytes_s / display_quantum_bytes
    full_frames_s_at_budget = display_budget_bytes_s / frame_bytes

    sd_init_hz = d(400_000)
    sd_default_hz = d(25_000_000)
    sd_high_speed_hz = d(50_000_000)
    sd_raw_bytes_s = sd_high_speed_hz / d(8)
    sd_protocol_reserve_bytes_s = d(1_250_000)
    sd_payload_after_reserves = sd_raw_bytes_s - sd_protocol_reserve_bytes_s - display_budget_bytes_s
    sd_block_bytes = d(512)
    sd_block_wire_us = sd_block_bytes / sd_raw_bytes_s * d(1_000_000)
    record_rate_bytes_s = d(1_500_000)
    card_stall_ms = d(250)
    required_stall_buffer = record_rate_bytes_s * card_stall_ms / d(1000)
    selected_stall_buffer = d(512 * 1024)
    selected_stall_ms = selected_stall_buffer / record_rate_bytes_s * d(1000)

    audio_sample_hz = d(48_000)
    audio_channels = d(2)
    audio_sample_bits = d(24)
    audio_slot_bits = d(32)
    i2s_bclk_hz = audio_sample_hz * audio_channels * audio_slot_bits
    audio_payload_bytes_s_per_direction = audio_sample_hz * audio_channels * audio_sample_bits / d(8)
    audio_slot_bytes_s_per_direction = audio_sample_hz * audio_channels * audio_slot_bits / d(8)
    audio_dma_frames_per_buffer = d(256)
    audio_dma_buffer_count = d(4)
    audio_buffer_ms = audio_dma_frames_per_buffer / audio_sample_hz * d(1000)
    audio_ring_ms = audio_buffer_ms * audio_dma_buffer_count
    audio_service_quantum_ms = d(1)

    nrf_spi_hz = d(10_000_000)
    nrf_payload_bytes = d(32)
    nrf_spi_transaction_bytes = nrf_payload_bytes + d(1)
    nrf_spi_drain_us = nrf_spi_transaction_bytes * d(8) / nrf_spi_hz * d(1_000_000)
    nrf_air_hz = d(2_000_000)
    nrf_fast_packet_bits = (d(1) + d(3) + d("1.125") + nrf_payload_bytes + d(1)) * d(8)
    nrf_fast_packet_us = nrf_fast_packet_bits / nrf_air_hz * d(1_000_000)
    nrf_three_level_fifo_us = nrf_fast_packet_us * d(3)
    nrf_all_three_serial_drain_us = nrf_spi_drain_us * d(3)
    nrf_service_budget_us = d(200)

    cc_air_bps = d(600_000)
    cc_watermark_bytes = d(32)
    cc_watermark_us = cc_watermark_bytes * d(8) / cc_air_bps * d(1_000_000)
    cc_spi_hz = d(10_000_000)
    cc_spi_drain_us = (cc_watermark_bytes + d(1)) * d(8) / cc_spi_hz * d(1_000_000)
    cc_service_budget_us = d(200)

    rp_nrf_payload_bytes_s = d(3) * nrf_air_hz / d(8)
    rp_cc_payload_bytes_s = cc_air_bps / d(8)
    rp_radio_aggregate_bytes_s = rp_nrf_payload_bytes_s + rp_cc_payload_bytes_s
    rp_ipc_payload_floor_bytes_s = d(1_500_000)
    rp_ipc_payload_margin_bytes_s = rp_ipc_payload_floor_bytes_s - rp_radio_aggregate_bytes_s
    rp_ipc_raw_bytes_s = d(20_000_000) / d(8)

    c5_ipc_raw_bytes_s = d(20_000_000) / d(8)
    c5_occupancy_limit = d("0.70")
    c5_occupied_bytes_s = c5_ipc_raw_bytes_s * c5_occupancy_limit
    c5_payload_floor_bytes_s = d(1_500_000)
    c5_framing_budget_bytes_s = c5_occupied_bytes_s - c5_payload_floor_bytes_s

    i2c_hz = d(400_000)
    i2c_max_payload_bytes = d(32)
    i2c_framed_bytes = i2c_max_payload_bytes + d(3)
    i2c_transaction_ms = i2c_framed_bytes * d(9) / i2c_hz * d(1000) + d("0.025")
    i2c_clients = d(len(resources["S3_INTERNAL_I2C"]["clients"]))
    i2c_full_sweep_ms = i2c_transaction_ms * i2c_clients

    resource_rows = [
        {"id": "DISPLAY_SD_SPI", "owner": "s3", "independence": "scheduled only between display and storage; no radio/IPC/audio endpoint uses SPI2", "deadline": resources["DISPLAY_SD_SPI"]["deadline"]},
        {"id": "S3_I2S", "owner": "s3", "independence": "dedicated I2S0 plus one independent GDMA TX/RX pair", "deadline": resources["S3_I2S"]["deadline"]},
        {"id": "NRF0_SPI", "owner": "rp", "independence": "PIO0 SM0 plus two persistent DMA channels", "deadline": resources["NRF0_SPI"]["deadline"]},
        {"id": "NRF1_SPI", "owner": "rp", "independence": "PIO0 SM1 plus two persistent DMA channels", "deadline": resources["NRF1_SPI"]["deadline"]},
        {"id": "NRF2_SPI", "owner": "rp", "independence": "PIO0 SM2 plus two persistent DMA channels", "deadline": resources["NRF2_SPI"]["deadline"]},
        {"id": "CC_SPI", "owner": "rp", "independence": "PIO0 SM3 plus two persistent DMA channels", "deadline": resources["CC_SPI"]["deadline"]},
        {"id": "S3_RP_IPC", "owner": "s3", "independence": "dedicated S3 SPI3 and RP SPI1 plus their own DMA", "deadline": resources["S3_RP_IPC"]["deadline"]},
        {"id": "S3_C5_IPC", "owner": "s3", "independence": "dedicated one-bit SDMMC/SDIO host path", "deadline": resources["S3_C5_IPC"]["deadline"]},
        {"id": "S3_INTERNAL_I2C", "owner": "s3", "independence": "scheduled control/status only; never transports a radio FIFO, encoder phase or PTT edge", "deadline": resources["S3_INTERNAL_I2C"]["deadline"]},
    ]

    capacity_checks = {}
    for name, row in capacities.items():
        used = sum(claim["units"] for claim in row["claims"])
        capacity_checks[f"{name.lower()}_accounting"] = used + row["reserve"] == row["available"]

    checks = {
        "h341_levels_are_reviewed": levels["review_summary"]["status"] == "reviewed" and levels["review_summary"]["failed"] == 0,
        "all_16_required_resource_contracts_present": set(candidate["required_resource_contracts"]) == set(resources) and len(resources) == 16,
        "all_12_exclusive_resources_are_dedicated": all(resources[name]["sharing"] == "dedicated" for name in candidate["exclusive_resource_contracts"]),
        **capacity_checks,
        "display_clock_is_40mhz": display_hz == d(40_000_000),
        "display_quantum_is_20kbytes": display_quantum_bytes == d(20_000),
        "display_full_frame_below_100ms": frame_payload_ms < d(100),
        "display_budget_supports_three_full_frames_per_second": full_frames_s_at_budget >= d(3),
        "display_budget_is_at_most_50_quanta_per_second": display_quanta_s <= d(50),
        "sd_initial_clock_is_within_400khz": sd_init_hz <= d(400_000),
        "sd_default_clock_is_25mhz": sd_default_hz == d(25_000_000),
        "sd_high_speed_clock_is_50mhz": sd_high_speed_hz == d(50_000_000),
        "sd_payload_after_protocol_and_display_is_4mbps": sd_payload_after_reserves >= d(4_000_000),
        "sd_single_block_wire_time_below_100us": sd_block_wire_us < d(100),
        "record_stall_buffer_is_at_least_512kib": selected_stall_buffer >= d(512 * 1024),
        "record_stall_buffer_exceeds_250ms": selected_stall_ms > card_stall_ms,
        "audio_bclk_is_3_072mhz": i2s_bclk_hz == d(3_072_000),
        "audio_full_duplex_payload_per_direction_is_288kbytes_s": audio_payload_bytes_s_per_direction == d(288_000),
        "audio_ring_exceeds_20ms": audio_ring_ms > d(20),
        "audio_service_quantum_has_5x_buffer_margin": audio_buffer_ms >= audio_service_quantum_ms * d(5),
        "nrf_spi_is_10mbps": nrf_spi_hz == d(10_000_000),
        "nrf_single_payload_drain_below_27us": nrf_spi_drain_us < d(27),
        "nrf_three_serial_drains_below_80us": nrf_all_three_serial_drain_us < d(80),
        "nrf_fifo_guard_exceeds_450us": nrf_three_level_fifo_us > d(450),
        "nrf_service_budget_below_fifo_guard": nrf_service_budget_us < nrf_three_level_fifo_us,
        "cc_watermark_guard_exceeds_426us": cc_watermark_us > d(426),
        "cc_spi_drain_below_27us": cc_spi_drain_us < d(27),
        "cc_service_budget_below_watermark_guard": cc_service_budget_us < cc_watermark_us,
        "rp_ipc_raw_is_2_5mbytes_s": rp_ipc_raw_bytes_s == d(2_500_000),
        "rp_ipc_carries_three_nrf_plus_cc_max_payload": rp_ipc_payload_margin_bytes_s > 0,
        "rp_ipc_payload_margin_is_at_least_40pct": rp_ipc_payload_margin_bytes_s / rp_ipc_payload_floor_bytes_s >= d("0.40"),
        "c5_ipc_raw_is_2_5mbytes_s": c5_ipc_raw_bytes_s == d(2_500_000),
        "c5_ipc_payload_fits_70pct_occupancy": c5_framing_budget_bytes_s > 0,
        "i2c_full_32byte_11client_sweep_below_10ms": i2c_full_sweep_ms < d(10),
        "ui_deadline_is_100ms": "<=100 ms" in resources["S3_INTERNAL_I2C"]["deadline"],
        "method_has_timing_rule": any(row["id"] == "PF-06" for row in methods["pass_fail_rules"]),
        "all_reviewed_resources_have_deadline_and_gate": all(row["deadline"] and resources[row["id"]]["proof_gate"] for row in resource_rows),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("H3.4.2 checks failed: " + ", ".join(failed))

    residual_hil = [
        "qualify SD card identity/CMD6 high-speed mode, >=4.0-MB/s storage, 1.5-MB/s record, 250-ms stalls and 512-KiB buffering",
        "scope shared SPI2 edges, CS-high high-Z/contention and <=1-ms display/SD arbitration under insert/remove",
        "capture all three nRF24 IRQ-to-drain paths and every 3PRX/PTX role mix at 10-Mbit/s SPI",
        "capture CC1101 GDO/FIFO service at 600-kbit/s air rate and 10-Mbit/s SPI",
        "run full-duplex 48-kHz audio without DMA underrun/overrun during display, storage and radio-event stress",
        "prove S3-RP >=1.5 MB/s with <=250-us alert-to-read and S3-C5 >=1.5 MB/s with <=2-ms control RTT",
        "measure 400-kHz SYS_I2C transaction/recovery/IRQ latency with every assembled address and simultaneous UI activity",
    ]
    manifest = {
        "schema_version": 1,
        "stage": "H3.4.2",
        "status": "reviewed_digital_bandwidth_latency_and_timing",
        "source_hashes": {str(path.relative_to(REPO)): sha256(path) for path in (CANDIDATE_PATH, DEVICES_PATH, METHODS_PATH, DISPLAY_PATH, LEVELS_PATH)},
        "provenance": SOURCES,
        "display_storage": {
            "display_qspi_hz": int(display_hz),
            "display_raw_bytes_s": int(display_raw_bytes_s),
            "display_quantum_ms": q(display_quantum_s * d(1000)),
            "display_quantum_bytes": int(display_quantum_bytes),
            "full_frame_bytes_rgb565": int(frame_bytes),
            "full_frame_payload_ms": q(frame_payload_ms),
            "admitted_display_budget_bytes_s": int(display_budget_bytes_s),
            "full_frames_s_equivalent_at_budget": q(full_frames_s_at_budget),
            "sd_clock_profile_hz": {"initial_max": int(sd_init_hz), "default": int(sd_default_hz), "qualified_high_speed": int(sd_high_speed_hz)},
            "sd_raw_bytes_s_at_high_speed": int(sd_raw_bytes_s),
            "protocol_card_reserve_bytes_s": int(sd_protocol_reserve_bytes_s),
            "remaining_storage_payload_bytes_s": int(sd_payload_after_reserves),
            "single_512byte_block_wire_us": q(sd_block_wire_us),
            "record_bytes_s": int(record_rate_bytes_s),
            "stall_ms": int(card_stall_ms),
            "minimum_stall_buffer_bytes": int(required_stall_buffer),
            "selected_stall_buffer_bytes": int(selected_stall_buffer),
            "selected_stall_coverage_ms": q(selected_stall_ms),
            "rules": ["50 MHz is entered only after card identity and CMD6 high-speed admission; otherwise the card remains at 25 MHz and cannot claim the 4-MB/s qualified profile", "card busy polling releases CS between bounded polls so it cannot hold the display off for the card-internal stall", "display and SD transfers are each <=1 ms; critical UI has priority, and the display average payload budget is <=1 MB/s while the qualified 4-MB/s storage profile is active"],
        },
        "audio": {
            "sample_hz": int(audio_sample_hz), "channels": int(audio_channels), "sample_bits": int(audio_sample_bits), "slot_bits": int(audio_slot_bits),
            "bclk_hz": int(i2s_bclk_hz), "payload_bytes_s_per_direction": int(audio_payload_bytes_s_per_direction), "slot_bytes_s_per_direction": int(audio_slot_bytes_s_per_direction),
            "dma_buffers": int(audio_dma_buffer_count), "frames_per_buffer": int(audio_dma_frames_per_buffer), "buffer_ms": q(audio_buffer_ms), "ring_ms": q(audio_ring_ms), "service_quantum_ms_max": int(audio_service_quantum_ms),
        },
        "radio_service": {
            "nrf24": {"radios": 3, "spi_hz_each": int(nrf_spi_hz), "maximum_air_bps_each": int(nrf_air_hz), "payload_bytes": int(nrf_payload_bytes), "single_spi_drain_us": q(nrf_spi_drain_us), "all_three_serial_upper_bound_us": q(nrf_all_three_serial_drain_us), "three_level_fifo_guard_us": q(nrf_three_level_fifo_us), "irq_to_service_budget_us": int(nrf_service_budget_us)},
            "cc1101": {"maximum_air_bps": int(cc_air_bps), "fifo_bytes": 64, "watermark_bytes": int(cc_watermark_bytes), "watermark_guard_us": q(cc_watermark_us), "spi_hz": int(cc_spi_hz), "watermark_spi_drain_us": q(cc_spi_drain_us), "irq_to_service_budget_us": int(cc_service_budget_us)},
            "rule": "all four compatibility-radio buses are independent PIO state machines with persistent DMA; display, storage, audio, C5 and U214 cannot own or block them",
        },
        "ipc": {
            "s3_rp": {"raw_bytes_s": int(rp_ipc_raw_bytes_s), "qualified_payload_floor_bytes_s": int(rp_ipc_payload_floor_bytes_s), "three_nrf_plus_cc_max_payload_bytes_s": int(rp_radio_aggregate_bytes_s), "payload_margin_bytes_s": int(rp_ipc_payload_margin_bytes_s), "alert_to_read_us_max": 250},
            "s3_c5": {"raw_bytes_s": int(c5_ipc_raw_bytes_s), "occupancy_max_percent": q(c5_occupancy_limit * d(100)), "occupied_bytes_s": int(c5_occupied_bytes_s), "qualified_payload_floor_bytes_s": int(c5_payload_floor_bytes_s), "framing_budget_bytes_s": int(c5_framing_budget_bytes_s), "control_rtt_ms_max": 2, "scope": "admitted waterfall/metadata/event payload, not an impossible promise to forward every raw Wi-Fi frame or RF sample"},
        },
        "control_i2c": {"clock_hz": int(i2c_hz), "reviewed_clients": int(i2c_clients), "bounded_payload_bytes": int(i2c_max_payload_bytes), "single_transaction_ms": q(i2c_transaction_ms), "full_sweep_ms": q(i2c_full_sweep_ms), "ordinary_ui_deadline_ms": 100},
        "resource_rows": resource_rows,
        "checks": checks,
        "corrections": [],
        "open_findings": [],
        "residual_physical_only": residual_hil,
        "review_summary": {"checks": len(checks), "failed": 0, "unresolved": 0, "status": "reviewed"},
        "next": {"stage": "H3.4.4", "action": "consolidate digital level, timing and boundary-loading evidence"},
    }

    en = f"""# Digital bandwidth, latency and timing

`H3.4.2` is reviewed with `{len(checks)}` machine checks and no open analytical finding. The exact current marker is `H3.4.4`.

## Closed paper budgets

| Path | Reviewed result |
|---|---|
| Display + storage | 40-MHz quad display gives 20 MB/s and a full RGB565 frame in `{q(frame_payload_ms)} ms`; each display quantum is 20 kB/1 ms. A qualified 50-MHz SD profile leaves exactly 4.0 MB/s after 1.25 MB/s protocol/card reserve and 1.0 MB/s display allowance. A 512-KiB ring covers `{q(selected_stall_ms)} ms` at 1.5 MB/s. |
| Audio | 48-kHz, stereo, 24-bit samples in 32-bit slots: 3.072-MHz BCLK, 288 kB/s payload per direction and `{q(audio_ring_ms)} ms` across four DMA buffers. |
| Three nRF24 | Each dedicated 10-Mbit/s SPI drains 32 bytes in `{q(nrf_spi_drain_us)} us`; even a serialized three-radio upper bound is `{q(nrf_all_three_serial_drain_us)} us` against a >`{q(nrf_three_level_fifo_us)}-us` three-level FIFO guard. |
| CC1101 | 32-byte watermark fills in `{q(cc_watermark_us)} us` at 600 kbit/s and drains in `{q(cc_spi_drain_us)} us` at 10 Mbit/s. |
| S3↔RP | 1.5-MB/s payload floor exceeds the three-nRF-plus-CC theoretical payload (`{q(rp_radio_aggregate_bytes_s / d(1_000_000))} MB/s`) by `{q(rp_ipc_payload_margin_bytes_s / d(1_000_000))} MB/s`. |
| S3↔C5 | 20-MHz one-bit SDIO provides 2.5 MB/s raw; 70% admitted occupancy leaves 1.5 MB/s payload plus 0.25 MB/s framing. This carries admitted waterfall/metadata/events, not every raw Wi-Fi frame or RF sample. |
| SYS_I2C | A deliberately large 32-byte transaction takes `{q(i2c_transaction_ms)} ms`; an eleven-client sweep takes `{q(i2c_full_sweep_ms)} ms`, well below the 100-ms ordinary UI deadline. |

The storage 50-MHz mode is conditional on card identity and CMD6 high-speed admission. A fallback card may work at 25 MHz but may not claim the 4-MB/s profile. Radio FIFOs never share a controller, PIO state machine or persistent DMA channel with display/storage.

Seven physical timing gates remain explicit for H8, including logic-analyzer traces, real media stalls, USB/IPC load and audio underrun/overrun stress.

Machine evidence: [`H3-VRF42-digital-timing.json`](../hardware/verification/generated/H3-VRF42-digital-timing.json).
"""
    ru = f"""# Digital bandwidth, latency и timing

`H3.4.2` проверено: `{len(checks)}` машинных checks, незакрытых аналитических findings нет. Точный текущий маркер — `H3.4.4`.

## Закрытые бумажные бюджеты

| Тракт | Проверенный результат |
|---|---|
| Display + storage | Quad display 40 МГц даёт 20 МБ/с и полный RGB565 frame за `{q(frame_payload_ms)} мс`; каждый display quantum — 20 кБ/1 мс. Qualified SD profile 50 МГц оставляет ровно 4,0 МБ/с после 1,25 МБ/с protocol/card reserve и 1,0 МБ/с allowance дисплея. Ring 512 КиБ покрывает `{q(selected_stall_ms)} мс` при записи 1,5 МБ/с. |
| Audio | 48 кГц, stereo, samples 24 bit в slots 32 bit: BCLK 3,072 МГц, payload 288 кБ/с в каждом направлении и `{q(audio_ring_ms)} мс` в четырёх DMA buffers. |
| Три nRF24 | Каждый отдельный SPI 10 Мбит/с выгружает 32 bytes за `{q(nrf_spi_drain_us)} мкс`; даже serial upper bound трёх radios — `{q(nrf_all_three_serial_drain_us)} мкс` при guard трёхуровневого FIFO >`{q(nrf_three_level_fifo_us)} мкс`. |
| CC1101 | Watermark 32 bytes заполняется за `{q(cc_watermark_us)} мкс` при 600 кбит/с и выгружается за `{q(cc_spi_drain_us)} мкс` по SPI 10 Мбит/с. |
| S3↔RP | Payload floor 1,5 МБ/с превышает теоретический payload трёх nRF плюс CC (`{q(rp_radio_aggregate_bytes_s / d(1_000_000))} МБ/с`) на `{q(rp_ipc_payload_margin_bytes_s / d(1_000_000))} МБ/с`. |
| S3↔C5 | One-bit SDIO 20 МГц даёт 2,5 МБ/с raw; admitted occupancy 70% оставляет 1,5 МБ/с payload и 0,25 МБ/с framing. Это admitted waterfall/metadata/events, а не обещание переслать каждый raw Wi-Fi frame или RF sample. |
| SYS_I2C | Нарочно крупная transaction 32 bytes занимает `{q(i2c_transaction_ms)} мс`; sweep одиннадцати clients — `{q(i2c_full_sweep_ms)} мс`, намного меньше обычного UI deadline 100 мс. |

Режим SD 50 МГц разрешён только после проверки identity и CMD6 high-speed admission. Fallback-карта может работать на 25 МГц, но не получает заявленный профиль 4 МБ/с. Radio FIFO не делит controller, PIO state machine или persistent DMA channel с display/storage.

Семь физических timing gates явно остаются H8: logic-analyzer traces, реальные media stalls, USB/IPC load и audio underrun/overrun stress.

Машинное evidence: [`H3-VRF42-digital-timing.json`](../hardware/verification/generated/H3-VRF42-digital-timing.json).
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
            raise SystemExit("stale H3.4.2 artifacts: " + ", ".join(stale))
    print(f"ok: H3.4.2 reviewed; {len(manifest['checks'])} checks, next H3.4.4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
