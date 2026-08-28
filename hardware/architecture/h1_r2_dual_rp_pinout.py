#!/usr/bin/env python3
"""Validate and publish the exact H1-R2 dual-RP working pin authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "hardware/architecture/h1-r2-dual-rp-pinout.json"
H0 = ROOT / "hardware/architecture/h0-r2-rebaseline.json"
C5_MUX = ROOT / "hardware/architecture/c5-sdio-service-mux-contract.json"
U219 = ROOT / "hardware/architecture/h1-r2-u219-cap.json"
DEVICES = ROOT / "hardware/architecture/devices.json"
G2F = ROOT / "hardware/architecture/candidates/G2F-3I.json"
OUTPUT = ROOT / "hardware/architecture/generated/H1-R2-dual-rp-pinout-audit.json"
DOC_EN = ROOT / "docs/pinout.md"
DOC_RU = ROOT / "docs/pinout.ru.md"


EXPECTED_GROUPS = {
    "hub_rp": [
        {0, 1, 2, 3, 4, 5}, {7, 8, 9, 10, 11, 12}, {13, 14, 15, 16, 17},
        {18, 19, 20, 21, 22, 23}, {24, 25, 26, 27, 28, 29},
        {30, 31, 32, 33, 34, 35}, {36}, {37, 38, 39, 40, 41, 44},
        {42, 43}, {45}, {46}, {6, 47},
    ],
    "rf_rp": [
        {0, 1, 2, 3, 6}, {4, 5}, {7, 8}, {9, 10, 11, 23, 39, 42, 43},
        {12, 13, 14, 30, 31, 40, 41, 44, 45, 46, 47}, {28, 32, 33, 34},
        {16, 17, 18, 20, 21, 22}, {19, 24, 25, 26, 27}, {35}, {36},
        {15, 29, 37, 38},
    ],
}

VALID_DIRECTIONS = {"in", "out", "io", "od", "reserve"}
VALID_CONTROLLER_PREFIXES = (
    "GPIO", "GPIO_IRQ", "PWM", "PIO0_", "PIO1_", "PIO2_", "I2C0", "I2C1",
    "SPI1", "UART0", "UART1_OR_GPIO", "GPIO_IRQ_OR_OUTPUT_PROFILE",
)


def expected_i2c_mux(gpio: int) -> tuple[str, str]:
    """Return the RP2350 fixed I2C controller/signal for a Bank-0 GPIO."""
    position = gpio % 4
    return {
        0: ("I2C0", "SDA"),
        1: ("I2C0", "SCL"),
        2: ("I2C1", "SDA"),
        3: ("I2C1", "SCL"),
    }[position]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(source: dict[str, Any], h0: dict[str, Any], c5_mux: dict[str, Any],
             u219: dict[str, Any], devices: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    devices = devices or load(DEVICES)
    if source.get("marker") != "H1-R2.31":
        errors.append("marker must be H1-R2.31")
    if source.get("status") != "current_working_authority_not_kicad":
        errors.append("pin map must remain a working authority, not a KiCad claim")
    if source.get("authority_chain", {}).get("does_not_authorize") != [
        "R2 KiCad", "fabrication", "ordering"
    ]:
        errors.append("authority boundary must deny KiCad, fabrication and ordering")
    authority = source.get("authority_chain", {})
    if authority.get("c5_mux_source") != str(C5_MUX.relative_to(ROOT)):
        errors.append("dual-RP authority must join the exact C5 mux source")
    if authority.get("u219_profile_source") != str(U219.relative_to(ROOT)):
        errors.append("dual-RP authority must join the exact U214/U219 profile source")
    if authority.get("rp2354b_fixed_mux_source") != \
            "https://github.com/raspberrypi/pico-sdk/blob/master/src/rp2_common/hardware_gpio/include/hardware/gpio.h":
        errors.append("dual-RP authority must cite the official RP2350 fixed-mux table")
    if "closed" not in authority.get("c5_electrical_join_status", ""):
        errors.append("C5 electrical pad/mux join must be explicit")
    remaining = " ".join(authority.get("remaining_h2_gates", []))
    for token in ("C11355", "service-VBUS", "MPN"):
        if token not in remaining:
            errors.append(f"remaining C5 production gates must name {token}")

    rp = devices.get("devices", {}).get("rp2354b_a4", {})
    identity = source.get("rp_identity", {})
    if rp.get("mpn") != "SC1512-A4" or identity.get("silicon") != "RP2354B0A4" \
            or identity.get("ordering_alias") != "SC1512(13)-A4":
        errors.append("RP2354B identity must join the registered SC1512-A4/A4 device")
    gpio_contacts = {name for name in rp.get("contacts", {}) if name.startswith("GPIO")}
    if gpio_contacts != {f"GPIO{gpio}" for gpio in range(48)}:
        errors.append("registered RP2354B package must expose GPIO0..47 exactly")

    for domain in ("hub_rp", "rf_rp"):
        block = source.get(domain, {})
        rows = block.get("pin_map", [])
        gpios = [row.get("gpio") for row in rows]
        if gpios != list(range(48)):
            errors.append(f"{domain}: pin_map must contain GPIO0..47 exactly once in order")
        if len({row.get("net") for row in rows}) != 48:
            errors.append(f"{domain}: net names must be unique")
        for row in rows:
            gpio = row.get("gpio")
            direction = row.get("direction")
            controller = row.get("controller", "")
            reset = row.get("reset", "")
            if direction not in VALID_DIRECTIONS:
                errors.append(f"{domain} GPIO{gpio}: invalid direction {direction}")
            if not any(controller == prefix or controller.startswith(prefix)
                       for prefix in VALID_CONTROLLER_PREFIXES):
                errors.append(f"{domain} GPIO{gpio}: unsupported controller {controller}")
            if not reset or not any(token in reset for token in ("input", "released/high-Z")):
                errors.append(f"{domain} GPIO{gpio}: reset state is not fail-closed/high-Z")
            if direction == "reserve" and "DNP" not in reset:
                errors.append(f"{domain} GPIO{gpio}: reserve must remain DNP")
            if direction == "od" and "released" not in reset:
                errors.append(f"{domain} GPIO{gpio}: open-drain output must reset released")

            if controller in {"I2C0", "I2C1"}:
                expected_controller, signal = expected_i2c_mux(gpio)
                if controller != expected_controller or signal not in row.get("net", ""):
                    errors.append(
                        f"{domain} GPIO{gpio}: {controller}/{row.get('net')} violates RP2350 "
                        f"fixed mux {expected_controller} {signal}"
                    )
                expected_direction = "io" if signal == "SDA" else "od"
                if direction != expected_direction:
                    errors.append(
                        f"{domain} GPIO{gpio}: {signal} direction must be {expected_direction}"
                    )
        reserve = [row["gpio"] for row in rows if row.get("direction") == "reserve"]
        budget = block.get("gpio_budget", {})
        if budget.get("available") != 48:
            errors.append(f"{domain}: GPIO available count must be 48")
        if budget.get("used") + budget.get("reserve") != 48:
            errors.append(f"{domain}: GPIO used+reserve must equal 48")
        if reserve != budget.get("reserve_gpios") or len(reserve) != budget.get("reserve"):
            errors.append(f"{domain}: reserve GPIO list/count mismatch")

        h0_groups = [set(row["gpios"]) for row in h0[domain]["pin_groups"]]
        if h0_groups != EXPECTED_GROUPS[domain]:
            errors.append(f"{domain}: reviewed H0 functional groups changed")
        h0_group_gpio_rows = [gpio for group in h0_groups for gpio in group]
        if len(h0_group_gpio_rows) != 48 or set(h0_group_gpio_rows) != set(range(48)):
            errors.append(f"{domain}: reviewed H0 functional groups must partition GPIO0..47 exactly once")
        if set(gpios) != set().union(*h0_groups):
            errors.append(f"{domain}: exact map does not cover the reviewed H0 groups")
        if budget.get("used") != h0[domain]["gpio_budget"]["used"]:
            errors.append(f"{domain}: exact map changes the reviewed H0 used count")
        if budget.get("reserve") != h0[domain]["gpio_budget"]["free"]:
            errors.append(f"{domain}: exact map changes the reviewed H0 reserve count")

        pio = block.get("pio_budget", {})
        pio_claims = pio.get("allocations", [])
        if len({row.get("resource") for row in pio_claims}) != len(pio_claims):
            errors.append(f"{domain}: a PIO state machine is double-booked")
        if pio.get("used_state_machines") != len(pio_claims):
            errors.append(f"{domain}: PIO used count does not match allocations")
        if pio.get("used_state_machines", 0) + pio.get("reserve_state_machines", 0) != pio.get("available_state_machines"):
            errors.append(f"{domain}: PIO budget does not close")
        if pio.get("available_state_machines") != 12:
            errors.append(f"{domain}: RP2354B must expose 12 PIO state machines")
        windows = {row.get("pio"): row for row in pio.get("gpio_windows", [])}
        if len(windows) != len(pio.get("gpio_windows", [])):
            errors.append(f"{domain}: PIO window declarations must be unique")
        for row in rows:
            controller = row.get("controller", "")
            if not controller.startswith(("PIO0_", "PIO1_", "PIO2_")):
                continue
            pio_name = controller[:4]
            window = windows.get(pio_name)
            if not window:
                errors.append(f"{domain} GPIO{row['gpio']}: {pio_name} has no GPIO window")
                continue
            base = window.get("base")
            if base not in (0, 16) or not base <= row["gpio"] <= base + 31:
                errors.append(
                    f"{domain} GPIO{row['gpio']}: outside declared {pio_name} base-{base} window"
                )

        dma = block.get("dma_budget", {})
        dma_claimed = sum(row.get("channels", 0) for row in dma.get("allocations", []))
        if dma_claimed != dma.get("used_channels"):
            errors.append(f"{domain}: DMA used count does not match allocations")
        if dma.get("used_channels", 0) + dma.get("reserve_channels", 0) != dma.get("available_channels"):
            errors.append(f"{domain}: DMA budget does not close")
        if dma.get("available_channels") != 16:
            errors.append(f"{domain}: RP2354B must expose 16 DMA channels")

    h0_m1 = {row["net"]: row["contact"] for row in h0["interboard_rebaseline"]["pin_map"]}
    hub_by_gpio = {row["gpio"]: row for row in source["hub_rp"]["pin_map"]}
    rf_by_gpio = {row["gpio"]: row for row in source["rf_rp"]["pin_map"]}
    expected_m1 = {
        "HUB_RF_ALERT_N": (22, 17, 19, "in", "od"),
        "HUB_RF_CS_N": (23, 16, 25, "out", "in"),
        "HUB_RF_SCK": (24, 13, 26, "out", "in"),
        "HUB_RF_MOSI": (26, 14, 24, "out", "in"),
        "HUB_RF_MISO": (27, 15, 27, "in", "out"),
    }
    rows = source.get("m1_binding", [])
    if {row.get("net") for row in rows} != set(expected_m1):
        errors.append("M1 dual-RP binding must contain exactly alert, CS, SCK, MOSI and MISO")
    for row in rows:
        net = row["net"]
        contact, hub_gpio, rf_gpio, hub_direction, rf_direction = expected_m1[net]
        if (row.get("contact"), row.get("hub_gpio"), row.get("rf_gpio")) != (contact, hub_gpio, rf_gpio):
            errors.append(f"{net}: exact M1/GPIO tuple changed")
        if h0_m1.get(net) != contact:
            errors.append(f"{net}: contact does not match the accepted H0 M1 map")
        if hub_by_gpio[hub_gpio]["net"] != net or rf_by_gpio[rf_gpio]["net"] != net:
            errors.append(f"{net}: endpoint net does not match both RP pin maps")
        if hub_by_gpio[hub_gpio]["direction"] != hub_direction \
                or rf_by_gpio[rf_gpio]["direction"] != rf_direction:
            errors.append(f"{net}: Hub/RF direction pair is not electrically symmetric")

    fixed_spi1 = {
        24: ("HUB_RF_MOSI", "in"),
        25: ("HUB_RF_CS_N", "in"),
        26: ("HUB_RF_SCK", "in"),
        27: ("HUB_RF_MISO", "out"),
    }
    for gpio, (net, direction) in fixed_spi1.items():
        row = rf_by_gpio[gpio]
        if (row.get("net"), row.get("direction"), row.get("controller")) != \
                (net, direction, "SPI1"):
            errors.append(f"rf_rp GPIO{gpio}: fixed SPI1 slave mux/direction changed")
    for gpio, net, direction in ((16, "VOICE_UART_TX", "out"), (17, "VOICE_UART_RX", "in")):
        row = rf_by_gpio[gpio]
        if (row.get("net"), row.get("direction"), row.get("controller")) != \
                (net, direction, "UART0"):
            errors.append(f"rf_rp GPIO{gpio}: fixed UART0 mux/direction changed")
    for gpio, net, direction in (
        (40, "CAP_GNSS_TX_OR_RF_SW0", "out"),
        (41, "CAP_GNSS_RX_OR_CC_GDO0", "in"),
    ):
        row = rf_by_gpio[gpio]
        if row.get("net") != net or row.get("direction") != direction \
                or not row.get("controller", "").startswith("UART1_OR_GPIO"):
            errors.append(f"rf_rp GPIO{gpio}: fixed UART1/profile mux/direction changed")

    isolation = source.get("s3_rom_uart_isolation", {})
    if isolation.get("affected_s3_gpio") != [43, 44]:
        errors.append("S3 ROM UART isolation must cover GPIO43/44")
    isolation_text = " ".join(str(value) for value in isolation.values())
    for token in ("Ioff", "OE", "ROM", "high-Z"):
        if token not in isolation_text:
            errors.append(f"S3 ROM UART isolation lacks {token} contract")
    for gpio, net in ((2, "S3_HUB_D2"), (3, "S3_HUB_D3")):
        if hub_by_gpio[gpio]["net"] != net or "isolation" not in hub_by_gpio[gpio]["endpoint"]:
            errors.append(f"Hub GPIO{gpio} must terminate through S3 ROM-UART isolation")

    c5_rows = {row["net"]: row for row in source["hub_rp"]["pin_map"] if row["net"].startswith("C5_SDIO_")}
    expected_c5_endpoints = {
        "C5_SDIO_CLK": (7, "C5 GPIO9 / module pad 11"),
        "C5_SDIO_CMD": (8, "C5 GPIO10 / module pad 12"),
        "C5_SDIO_D0": (9, "C5 GPIO8 / module pad 10"),
        "C5_SDIO_D1": (10, "C5 GPIO7 / module pad 9"),
        "C5_SDIO_D2": (11, "FSUSB42 HSD2+", "C5 GPIO14 / module pad 14"),
        "C5_SDIO_D3": (12, "FSUSB42 HSD2-", "C5 GPIO13 / module pad 13"),
    }
    if set(c5_rows) != set(expected_c5_endpoints):
        errors.append("Hub-side C5 bus must contain exactly CLK/CMD/DAT0..DAT3")
    for net, expected in expected_c5_endpoints.items():
        row = c5_rows.get(net, {})
        if row.get("gpio") != expected[0] or not all(token in row.get("endpoint", "") for token in expected[1:]):
            errors.append(f"{net}: exact Hub/C5/mux endpoint is wrong")
    contract_map = {
        row["signal"]: (row["gpio"], row["module_pad"])
        for row in c5_mux.get("c5_module", {}).get("signals", [])
    }
    if contract_map != {
        "SDIO_DAT1": ("GPIO7", 9), "SDIO_DAT0": ("GPIO8", 10),
        "SDIO_CLK": ("GPIO9", 11), "SDIO_CMD": ("GPIO10", 12),
        "SDIO_DAT3_USB_DM": ("GPIO13", 13), "SDIO_DAT2_USB_DP": ("GPIO14", 14),
    }:
        errors.append("joined C5 source no longer contains the exact fixed SDIO/module-pad map")
    route = c5_mux.get("production_mux_route", {})
    candidate = route.get("candidate", {})
    if (candidate.get("mpn"), candidate.get("jlcpcb_part_number")) != ("FSUSB42MUX", "C11355"):
        errors.append("joined C5 source lost exact FSUSB42MUX/C11355 identity")
    if route.get("selection_status") == "accepted":
        errors.append("C11355 production route must remain fail-closed until live route/MOQ/price are proven")
    if c5_mux.get("ownership", {}).get("service_vbus", {}).get("detector_and_latch_mpn_status") == "accepted":
        errors.append("service-VBUS detector/latch must remain open until an exact MPN is selected")

    rf = {row["gpio"]: row for row in source["rf_rp"]["pin_map"]}
    expected_cap_rows = {
        12: ("CAP_PIN10_BUSY_OR_NFC_CS_N", "io", "SN74CBTLV1G125", "U219 NFC_CS_N"),
        13: ("CAP_IRQ", "in", "U214 DIO1", "U219 NFC_IRQ"),
        14: ("CAP_RESET_N_OR_POWER_EN", "out", "U214 RESET_N", "U219 POWER_EN"),
        30: ("CAP_I2C_SDA", "io", "TCA4307DGKR", "U214/U219 contact 4 SDA"),
        31: ("CAP_I2C_SCL", "od", "TCA4307DGKR", "U214/U219 contact 3 SCL"),
        40: ("CAP_GNSS_TX_OR_RF_SW0", "out", "U214 GNSS RX", "U219 RF_SW0"),
        41: ("CAP_GNSS_RX_OR_CC_GDO0", "in", "U214 GNSS TX", "U219 CC1101 GDO0"),
        44: ("CAP_SPI_MISO", "in", "U214 MISO", "U219 shared MISO"),
        45: ("CAP_SPI_SCK", "out", "U214 SCK", "U219 shared SCLK"),
        46: ("CAP_SPI_MOSI", "out", "U214 MOSI", "U219 shared MOSI"),
        47: ("CAP_SPI_PRIMARY_CS_N", "out", "U214 NSS_N", "U219 CC1101_CS_N"),
    }
    for gpio, (net, direction, *tokens) in expected_cap_rows.items():
        row = rf[gpio]
        if row.get("net") != net or row.get("direction") != direction \
                or not all(token in row.get("endpoint", "") for token in tokens):
            errors.append(f"rf_rp GPIO{gpio}: exact-one U214/U219 profile semantics changed")
    if u219.get("accessories", {}).get("slot_population") != "exactly_one":
        errors.append("joined U219 source must require exactly-one U214/U219 population")
    pin10 = u219.get("pin_10_bidirectional_boundary", {})
    if pin10.get("host_gpio") != "RP GPIO12" or pin10.get("switch_mpn") != "SN74CBTLV1G125DCKR":
        errors.append("joined U219 source lost the exact GPIO12 bilateral boundary")
    if u219.get("pin_8_power_boundary", {}).get("host_gpio") != "RP GPIO14":
        errors.append("joined U219 source lost the exact GPIO14 reset/power boundary")
    shared_irq = u219.get("shared_irq_contract", {})
    if (shared_irq.get("connector_contact"), shared_irq.get("host_gpio"),
            shared_irq.get("host_net")) != (9, "RP GPIO13", "CAP_IRQ") \
            or "polarity is not published" not in shared_irq.get("u219_role", ""):
        errors.append("joined U219 source lost the profile-neutral GPIO13 IRQ contract")
    shared = u219.get("shared_spi_contract", {})
    if (shared.get("miso"), shared.get("clock"), shared.get("mosi")) != (
        "existing U214 MISO on RP GPIO44", "existing U214 SCK on RP GPIO45",
        "existing U214 MOSI on RP GPIO46",
    ):
        errors.append("joined U219 source changed the shared GPIO44..46 SPI assignment")
    shared_i2c = u219.get("shared_i2c_contract", {})
    if "RF RP GPIO30" not in shared_i2c.get("sda", "") \
            or "RF RP GPIO31" not in shared_i2c.get("scl", "") \
            or "TCA4307DGKR" not in (shared_i2c.get("sda", "") + shared_i2c.get("scl", "")):
        errors.append("joined U219 source changed the shared GPIO30/31 isolated I2C1 assignment")
    execution = " ".join(source.get("execution_gates", []))
    for token in ("powered-off-Ioff", "3V3_MAIN", "AON"):
        if token not in execution:
            errors.append(f"Pack/Safety I2C boundary gate must name {token}")
    if "14/12-channel DMA" not in execution:
        errors.append("execution gate must match the current Hub/RF 14/12 DMA budgets")
    for gpio in range(4):
        row = rf[gpio]
        endpoint_reset = row.get("endpoint", "") + " " + row.get("reset", "")
        for token in ("SN74LVC1G126DCKR", "Ioff", "OE low"):
            if token not in endpoint_reset:
                errors.append(f"rf_rp GPIO{gpio}: audio path lacks reset-off {token} isolation")
    return errors


def build(source: dict[str, Any] | None = None, h0: dict[str, Any] | None = None,
          c5_mux: dict[str, Any] | None = None, u219: dict[str, Any] | None = None,
          devices: dict[str, Any] | None = None) -> dict[str, Any]:
    source = source or load(SOURCE)
    h0 = h0 or load(H0)
    c5_mux = c5_mux or load(C5_MUX)
    u219 = u219 or load(U219)
    devices = devices or load(DEVICES)
    errors = validate(source, h0, c5_mux, u219, devices)
    return {
        "schema_version": 1,
        "artifact": "H1-R2-dual-rp-pinout-audit",
        "marker": source.get("marker"),
        "status": "pass_exact_dual_rp_working_authority" if not errors else "fail",
        "authority": {
            "source": str(SOURCE.relative_to(ROOT)),
            "source_sha256": digest(SOURCE),
            "functional_source": str(H0.relative_to(ROOT)),
            "functional_source_sha256": digest(H0),
            "c5_mux_source": str(C5_MUX.relative_to(ROOT)),
            "c5_mux_source_sha256": digest(C5_MUX),
            "u219_profile_source": str(U219.relative_to(ROOT)),
            "u219_profile_source_sha256": digest(U219),
            "device_register_source": str(DEVICES.relative_to(ROOT)),
            "device_register_source_sha256": digest(DEVICES),
            "r2_h2_authorized": False,
            "c5_electrical_join_status": source["authority_chain"]["c5_electrical_join_status"],
            "remaining_h2_gates": source["authority_chain"]["remaining_h2_gates"],
        },
        "summary": {
            "domains": 2,
            "gpio_rows": len(source["hub_rp"]["pin_map"]) + len(source["rf_rp"]["pin_map"]),
            "m1_signal_bindings": len(source["m1_binding"]),
            "hub_gpio_used": source["hub_rp"]["gpio_budget"]["used"],
            "hub_gpio_reserve": source["hub_rp"]["gpio_budget"]["reserve"],
            "rf_gpio_used": source["rf_rp"]["gpio_budget"]["used"],
            "rf_gpio_reserve": source["rf_rp"]["gpio_budget"]["reserve"],
            "hub_pio_used": source["hub_rp"]["pio_budget"]["used_state_machines"],
            "hub_dma_used": source["hub_rp"]["dma_budget"]["used_channels"],
            "rf_pio_used": source["rf_rp"]["pio_budget"]["used_state_machines"],
            "rf_dma_used": source["rf_rp"]["dma_budget"]["used_channels"],
        },
        "hub_rp": source["hub_rp"],
        "rf_rp": source["rf_rp"],
        "m1_binding": source["m1_binding"],
        "s3_rom_uart_isolation": source["s3_rom_uart_isolation"],
        "execution_gates": source["execution_gates"],
        "errors": errors,
    }


def render_public(source: dict[str, Any], candidate: dict[str, Any], russian: bool) -> str:
    if russian:
        title = "# Текущая распиновка Leshy2 R2"
        nav = "[На главную](../README.ru.md) · [English](pinout.md) · [Железо](hardware.ru.md)"
        intro = (
            "Это точная рабочая H1-R2.31-карта GPIO двух независимых RP2354B и их пяти "
            "сигналов через M1. Точный электрический контракт module-pad/IO-mux C5 присоединён. "
            "Она ещё не разрешает KiCad: до нового R2 H2 остаются live production route "
            "FSUSB42MUX/C11355 и точный MPN detector/latch service-VBUS."
        )
        names = {"hub_rp": "Передний Hub RP", "rf_rp": "Задний RF RP"}
        cols = "| GPIO | Сеть | Направление | Контроллер | Физический endpoint | Reset / pull |"
        resource = "Ресурсы"
        m1_heading = "Связь Hub RP ↔ RF RP через M1"
        iso_heading = "Изоляция ROM-UART S3"
        gates_heading = "Что ещё не доказано"
        nm_heading = "Точный pin-map dual NMOS"
    else:
        title = "# Current Leshy2 R2 pin assignment"
        nav = "[Home](../README.md) · [Русский](pinout.ru.md) · [Hardware](hardware.md)"
        intro = (
            "This is the exact H1-R2.31 working GPIO map for the two independent RP2354B domains "
            "and their five M1 signals. The exact C5 module-pad/IO-mux electrical contract is joined. "
            "It still does not authorize KiCad: the live FSUSB42MUX/C11355 production route and an "
            "exact service-VBUS detector/latch MPN remain fail-closed before a new R2 H2 export."
        )
        names = {"hub_rp": "Front Hub RP", "rf_rp": "Rear RF RP"}
        cols = "| GPIO | Net | Direction | Controller | Physical endpoint | Reset / pull |"
        resource = "Resources"
        m1_heading = "Hub RP ↔ RF RP through M1"
        iso_heading = "S3 ROM-UART isolation"
        gates_heading = "Still unproven"
        nm_heading = "Exact dual-NMOS pin map"

    def esc(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        title, "", nav, "", intro, "",
        f"> Machine source: `{SOURCE.relative_to(ROOT)}`. Current marker: **`{source['marker']}`**.", "",
    ]
    for domain in ("hub_rp", "rf_rp"):
        block = source[domain]
        budget = block["gpio_budget"]
        pio = block["pio_budget"]
        dma = block["dma_budget"]
        lines.extend([
            f"## {names[domain]}", "", block["role"], "",
            f"**GPIO:** `{budget['used']}/48` used, `{budget['reserve']}` reserve. "
            f"**PIO:** `{pio['used_state_machines']}/12` used. "
            f"**DMA:** `{dma['used_channels']}/16` used.", "", cols,
            "|---:|---|---|---|---|---|",
        ])
        for row in block["pin_map"]:
            lines.append(
                f"| `{row['gpio']}` | `{esc(row['net'])}` | `{row['direction']}` | "
                f"`{esc(row['controller'])}` | {esc(row['endpoint'])} | {esc(row['reset'])} |"
            )
        lines.extend(["", f"### {resource}", "", "| Kind | Allocation |", "|---|---|"])
        pio_text = "; ".join(f"`{row['resource']}` → {row['consumer']}" for row in pio["allocations"])
        dma_text = "; ".join(f"{row['consumer']} = `{row['channels']}`" for row in dma["allocations"])
        lines.extend([f"| PIO | {pio_text} |", f"| DMA | {dma_text} |", ""])

    lines.extend([f"## {m1_heading}", "", "| Net | M1 | Hub GPIO | RF GPIO | Driver |", "|---|---:|---:|---:|---|"])
    for row in source["m1_binding"]:
        lines.append(
            f"| `{row['net']}` | `{row['contact']}` | `{row['hub_gpio']}` | "
            f"`{row['rf_gpio']}` | {row['driver']} |"
        )
    isolation = source["s3_rom_uart_isolation"]
    lines.extend([
        "", f"## {iso_heading}", "", isolation["requirement"], "", isolation["enable_sequence"],
        "", f"## {gates_heading}", "",
    ])
    lines.extend(f"- {gate}" for gate in source["execution_gates"])

    dual = candidate["sot363_2n7002dw_contract"]
    lines.extend([
        "", f"## {nm_heading}", "",
        f"`{dual['mpn']}` / JLC `{dual['jlcpcb_part']}` keeps the exact physical SOT-363 top-view mapping.",
        "", "| Physical pin | Terminal |", "|---:|---|",
    ])
    for physical, contact in dual["physical_pin_to_contact"].items():
        lines.append(f"| `{physical}` | `{contact}` |")
    lines.extend(["", "| Instance | Channel | Gate | Source | Drain |", "|---|---|---|---|---|"])
    for instance, channels in dual["instances"].items():
        for channel, nets in channels.items():
            suffix = channel.rsplit("_", 1)[-1]
            lines.append(
                f"| `{instance}` | `{channel}` | `{nets[f'G{suffix}']}` | "
                f"`{nets[f'S{suffix}']}` | `{nets[f'D{suffix}']}` |"
            )
    lines.append("")
    return "\n".join(lines)


def render_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source, h0, c5_mux, u219, candidate = load(SOURCE), load(H0), load(C5_MUX), load(U219), load(G2F)
    audit = build(source, h0, c5_mux, u219)
    outputs = {
        OUTPUT: render_json(audit),
        DOC_EN: render_public(source, candidate, False),
        DOC_RU: render_public(source, candidate, True),
    }
    if audit["errors"]:
        for error in audit["errors"]:
            print(f"error: {error}")
        return 1
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
        return 0
    stale = [str(path.relative_to(ROOT)) for path, content in outputs.items()
             if not path.is_file() or path.read_text(encoding="utf-8") != content]
    if stale:
        print("stale: " + ", ".join(stale))
        return 1
    print("ok: exact dual-RP GPIO/M1 plus C5 electrical join; production gates still block R2 H2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
