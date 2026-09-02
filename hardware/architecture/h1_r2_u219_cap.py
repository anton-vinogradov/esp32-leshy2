#!/usr/bin/env python3
"""Validate and generate the isolated H1-R2 U214/U219 Cap overlay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "hardware/architecture/h1-r2-u219-cap.json"
BASE = ROOT / "hardware/architecture/candidates/G2F-3I.json"
GENERATED_JSON = ROOT / "hardware/architecture/generated/H1-R2-U219-cap-policy.json"
GENERATED_CSV = ROOT / "hardware/architecture/generated/H1-R2-U219-bom-delta.csv"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decimal(value: object) -> Decimal:
    return Decimal(str(value))


def base_route_set(base: dict) -> set[tuple[str, str, str]]:
    return {(row["from"], row["to"], row["net"]) for row in base["fixed_routes"]}


def validate(model: dict, base: dict) -> list[str]:
    errors: list[str] = []
    if model.get("schema") != "leshy2.h1-r2.u219-cap.v1":
        errors.append("unexpected U219 overlay schema")
    scope = model.get("scope", {})
    if scope.get("base_candidate") != "hardware/architecture/candidates/G2F-3I.json":
        errors.append("overlay must bind exact G2F-3I base candidate")
    if scope.get("production_or_hil_claim") is not False:
        errors.append("paper overlay may not claim production or HIL closure")

    accessories = model.get("accessories", {})
    if accessories.get("slot_population") != "exactly_one":
        errors.append("U214 and U219 must be mutually exclusive in one physical slot")
    if accessories.get("unknown_or_unsigned_profile") != "branch_off_and_pin10_disconnected":
        errors.append("unknown profile must fail with power off and pin 10 disconnected")
    u219 = accessories.get("u219", {})
    if u219.get("envelope_mm") != [84.0, 24.0, 19.7]:
        errors.append("U219 must retain the official 84x24x19.7-mm envelope")
    if u219.get("listed_5v_current_ma") != 96:
        errors.append("U219 protected-power budget must include official listed 96 mA")
    expected_pins = {
        "1": "G0", "2": "RF_SW0",
        "3": "SCL", "4": "SDA",
        "5": "5V_OUT", "6": "GND",
        "7": "BLANK/undocumented-current; legacy dock contract says 5V_IN",
        "8": "POWER_EN", "9": "NFC_IRQ",
        "10": "NFC_CS", "11": "SCLK", "12": "MOSI", "13": "MISO", "14": "CC_CS",
    }
    if u219.get("official_pin_table") != expected_pins:
        errors.append("U219 official 14-contact table changed or is incomplete")

    pin8 = model.get("pin_8_power_boundary", {})
    if pin8.get("connector_contact") != 8 or pin8.get("host_gpio") != "RP GPIO14":
        errors.append("contact 8 must reuse RP GPIO14")
    if pin8.get("fail_safe_default") != "low":
        errors.append("U219 POWER_EN must fail low")
    power = model.get("protected_5v_boundary", {})
    if power.get("u219_listed_load_ma") != 96 or "TPS259470" not in power.get("protection", ""):
        errors.append("U219 must reuse the exact protected 5-V Cap boundary")
    if "do not energize" not in power.get("contact_7_gate", ""):
        errors.append("official U219 contact-7 conflict must block power until received-unit proof")

    pin10 = model.get("pin_10_bidirectional_boundary", {})
    if pin10.get("connector_contact") != 10 or pin10.get("host_gpio") != "RP GPIO12":
        errors.append("contact 10 must reuse RP GPIO12 bidirectionally")
    if pin10.get("switch_mpn") != "SN74CBTLV1G125DCKR":
        errors.append("contact 10 requires the audited bilateral switch")
    aon = pin10.get("aon_enable", {})
    if aon.get("inverter_mpn") != "SN74LVC1G06DCKR":
        errors.append("contact 10 /OE requires the audited AON open-drain inverter")
    if aon.get("command_source") != "existing U214_READY; the signed profile is admitted before any upstream branch request can make READY high":
        errors.append("pin 10 /OE must derive from the existing qualified READY plane without a GPIO")
    if aon.get("supply") != "AON_SAFE_3V3" or "disconnects pin 10" not in aon.get("loss_behavior", ""):
        errors.append("pin 10 must disconnect on qualification loss from the AON plane")
    for token in ("u214_return_buffer channel 1", "u214_series_busy"):
        if not any(token in row for row in pin10.get("supersedes", [])):
            errors.append(f"pin10 overlay does not supersede {token}")

    routes = base_route_set(base)
    required_base_routes = {
        ("u214_host_buffer_a.1Y", "u214_series_rst.END_1", "U214_RST_BUFFERED"),
        ("u214_series_rst.END_2", "u214_esd_a.D2_PLUS", "U214_RST_CONNECTOR"),
        ("u214_esd_a.D2_PLUS", "u214_connector.PIN_8", "U214_RST_CONNECTOR"),
        ("u214_connector.PIN_10", "u214_esd_b.D2_MINUS", "U214_BUSY_CONNECTOR"),
        ("evidence_mask.P17", "evidence_mask_p17_pulldown.END_1", "EVIDENCE_MASK_UNUSED_P17"),
        ("evidence_or_4.K2", "abstract:no-connect", "EVIDENCE_OR_4_UNUSED_DIODE_NC"),
        ("evidence_or_4.A_COMMON", "safety_controller.PA22", "ANY_TX_AON_N"),
    }
    missing = sorted(required_base_routes - routes)
    if missing:
        errors.append(f"base candidate routes required by overlay are missing: {missing}")

    i2c = model.get("shared_i2c_contract", {})
    if i2c.get("owner") != "rear RF RP2354B I2C1 domain":
        errors.append("U219 I2C must reuse the rear RF RP I2C1 domain")
    if "contact 3 SCL" not in i2c.get("scl", "") or "RF RP GPIO31" not in i2c.get("scl", ""):
        errors.append("U219 contact 3 must reuse the isolated I2C1 SCL path to RF GPIO31")
    if "contact 4 SDA" not in i2c.get("sda", "") or "RF RP GPIO30" not in i2c.get("sda", ""):
        errors.append("U219 contact 4 must reuse the isolated I2C1 SDA path to RF GPIO30")
    if "TCA4307DGKR" not in i2c.get("scl", "") or "TCA4307DGKR" not in i2c.get("sda", ""):
        errors.append("U219 SCL/SDA must retain the existing hot-plug/stuck-low isolator")
    if "no new GPIO" not in i2c.get("isolation", ""):
        errors.append("U219 I2C reuse may not consume a new GPIO")

    irq = model.get("shared_irq_contract", {})
    if (irq.get("connector_contact"), irq.get("host_gpio"), irq.get("host_net")) != \
            (9, "RP GPIO13", "CAP_IRQ"):
        errors.append("U214/U219 contact 9 must use the profile-neutral CAP_IRQ path on RP GPIO13")
    if "active-high" not in irq.get("u214_role", ""):
        errors.append("U214 DIO1 active-high semantics must remain profile metadata")
    if "polarity is not published" not in irq.get("u219_role", ""):
        errors.append("U219 NFC_IRQ polarity must remain an explicit received-unit HIL gate")
    if "never encode active-low" not in irq.get("rule", ""):
        errors.append("shared Cap IRQ net may not invent active-low polarity")

    spi = model.get("shared_spi_contract", {})
    if spi.get("owner") != "rear RF RP2354B PIO/SPI domain":
        errors.append("U219 shared SPI must remain on the rear RF RP domain")
    chip_selects = spi.get("chip_selects", {})
    if set(chip_selects) != {"u214", "u219_cc1101", "u219_nfc"}:
        errors.append("shared SPI must define all three profile chip-select roles")
    if not any("conflicting shared-CS" in row for row in spi.get("rules", [])):
        errors.append("official U219 shared-CS tutorial conflict must remain an explicit gate")

    policy = model.get("radio_policy", {})
    cc = policy.get("cc1101", {})
    if set(cc.get("forbidden_commands", [])) != {"SFSTXON", "STX", "PATABLE write", "TX FIFO write"}:
        errors.append("CC1101 RX-only command firewall is incomplete")
    if cc.get("hardware_tx_evidence") != "absent for U219 CC1101; therefore TX is unconditionally forbidden":
        errors.append("U219 CC1101 must remain hard RX-only without evidence")
    nfc = policy.get("nfc", {})
    if set(nfc.get("forbidden", [])) != {"tag write", "card emulation", "field-on without EV_N9 lease"}:
        errors.append("U219 NFC must remain poll/read only and evidence leased")
    if "blocked until" not in nfc.get("runtime_enable", ""):
        errors.append("NFC field enable must remain blocked pending physical evidence HIL")

    evidence = model.get("nfc_field_evidence", {})
    if evidence.get("signal") != "EV_N9_U219_NFC":
        errors.append("independent NFC evidence must be EV_N9_U219_NFC")
    expected_fanout = {
        "TCA9535 evidence_mask.P17 diagnostic input",
        "existing evidence_or_4.K2 spare cathode",
        "existing evidence_or_4.A_COMMON -> ANY_TX_AON_N",
    }
    if set(evidence.get("digital_fanout", [])) != expected_fanout:
        errors.append("EV_N9 must reach P17, K2 and ANY_TX_AON_N")
    analog_text = " ".join(evidence.get("analog_path", []))
    for token in ("BAT54S,215", "LMV331IDBVR", "full-wave", "open-collector"):
        if token not in analog_text:
            errors.append(f"NFC evidence path missing {token}")
    if "DNP C0G" not in evidence.get("pickup", {}).get("tuning", ""):
        errors.append("pickup tuning bank must remain DNP until VNA/HIL")

    surface = model.get("jlcpcb_live_surface", {})
    if "canPresaleNumber > 0" not in surface.get("semantics", ""):
        errors.append("JLC availability semantics must use canPresaleNumber")
    expected_parts = {
        "SN74CBTLV1G125DCKR": ("Texas Instruments", "C131992", Decimal("0.2846"), 1),
        "SN74LVC1G06DCKR": ("Texas Instruments", "C7828", Decimal("0.1674"), 1),
        "BAT54S,215": ("Nexperia", "C47546", Decimal("0.0335"), 2),
        "LMV331IDBVR": ("Texas Instruments", "C34731", Decimal("0.1655"), 1),
        "0402WGF1001TCE": ("UNI-ROYAL(Uniroyal Elec)", "C11702", Decimal("0.0039"), 2),
        "0402WGF1002TCE": ("UNI-ROYAL(Uniroyal Elec)", "C25744", Decimal("0.0031"), 4),
        "0402WGF1003TCE": ("UNI-ROYAL(Uniroyal Elec)", "C25741", Decimal("0.0028"), 2),
        "0402WGF1004TCE": ("UNI-ROYAL(Uniroyal Elec)", "C26083", Decimal("0.0026"), 1),
        "GRM155R71H103KA88D": ("Murata Electronics", "C77019", Decimal("0.0097"), 1),
        "CC0402KRX7R9BB104": ("YAGEO", "C131394", Decimal("0.0107"), 3),
    }
    checked_at = surface.get("checked_at", "")
    if not checked_at.startswith(model.get("evidence_date", "") + "T"):
        errors.append("live JLC evidence timestamp must match the dated design evidence")
    found_parts = {row.get("mpn"): row for row in surface.get("parts", [])}
    if set(found_parts) != set(expected_parts):
        errors.append("live JLC part set differs from the ten audited exact MPNs")
    for mpn, (manufacturer, cnum, price, quantity) in expected_parts.items():
        row = found_parts.get(mpn, {})
        if row.get("manufacturer") != manufacturer or row.get("jlc_number") != cnum:
            errors.append(f"{mpn}: manufacturer/C-number mismatch")
        if row.get("can_presale_number", 0) <= 0:
            errors.append(f"{mpn}: live available-order quantity is not proven")
        if row.get("moq") != 1:
            errors.append(f"{mpn}: expected MOQ 1")
        if row.get("assembly_type") != "SMT" or not row.get("standard_pcba"):
            errors.append(f"{mpn}: not proven placeable on Standard PCBA")
        if decimal(row.get("unit_price_usd", 0)) != price:
            errors.append(f"{mpn}: saved live one-piece price mismatch")
        if row.get("quantity_per_device", 1) != quantity:
            errors.append(f"{mpn}: quantity per device mismatch")

    if set(found_parts) == set(expected_parts):
        pin10_active = sum(
            decimal(found_parts[mpn]["unit_price_usd"])
            for mpn in ("SN74CBTLV1G125DCKR", "SN74LVC1G06DCKR")
        )
        nfc_active = (
            decimal(found_parts["BAT54S,215"]["unit_price_usd"]) * 2
            + decimal(found_parts["LMV331IDBVR"]["unit_price_usd"])
        )
        support_passives = sum(
            decimal(found_parts[mpn]["unit_price_usd"])
            * found_parts[mpn].get("quantity_per_device", 1)
            for mpn in (
                "0402WGF1001TCE", "0402WGF1002TCE", "0402WGF1003TCE",
                "0402WGF1004TCE", "GRM155R71H103KA88D", "CC0402KRX7R9BB104",
            )
        )
        selected_added = pin10_active + nfc_active + support_passives
        bom = model.get("bom_delta", {})
        checks = {
            "pin10_new_active_usd_per_device": pin10_active,
            "nfc_evidence_new_active_usd_per_device": nfc_active,
            "support_passives_usd_per_device": support_passives,
            "known_active_added_usd_per_device": pin10_active + nfc_active,
            "selected_populated_added_usd_per_device": selected_added,
            "selected_populated_net_after_removed_usd_per_device": selected_added
            - decimal(bom.get("removed_22r_usd_per_device", 0)),
            "one_prototype_selected_populated_added_usd": selected_added,
            "one_prototype_selected_populated_net_after_removed_usd": selected_added
            - decimal(bom.get("removed_22r_usd_per_device", 0)),
        }
        for key, calculated in checks.items():
            if decimal(bom.get(key, 0)) != calculated:
                errors.append(f"BOM calculation mismatch for {key}: {calculated}")
        if bom.get("cost_status") != "complete_selected_populated_components":
            errors.append("U219 selected populated delta must be complete")

    gates = model.get("acceptance_gates", [])
    if len(gates) < 6 or any(row.get("closed") is not False for row in gates):
        errors.append("all U219 specimen/VNA/HIL gates must remain explicitly open")
    if not any("RF_SW1" in row.get("requirement", "") for row in gates):
        errors.append("official RF_SW1 pin-table inconsistency gate is missing")
    ambiguous_pins = {
        pin for pin, role in u219.get("official_pin_table", {}).items()
        if "undocumented-current" in role
    }
    if ambiguous_pins != {"7"}:
        errors.append("only U219 contact 7 may remain an official-source ambiguity")
    return errors


def generated_policy(model: dict, base: dict) -> dict:
    errors = validate(model, base)
    return {
        "schema": "leshy2.generated.h1-r2.u219-cap-policy.v1",
        "design_id": model["design_id"],
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "base_candidate": str(BASE.relative_to(ROOT)),
        "base_candidate_sha256": sha256(BASE),
        "evidence_date": model["evidence_date"],
        "validation": {"passed": not errors, "errors": errors},
        "slot": {
            "population": model["accessories"]["slot_population"],
            "profiles": [model["accessories"]["u214"]["profile"], model["accessories"]["u219"]["profile"]],
            "unknown": model["accessories"]["unknown_or_unsigned_profile"],
        },
        "pin_8": model["pin_8_power_boundary"],
        "protected_5v": model["protected_5v_boundary"],
        "pin_10": model["pin_10_bidirectional_boundary"],
        "i2c": model["shared_i2c_contract"],
        "spi": model["shared_spi_contract"],
        "radio_policy": model["radio_policy"],
        "nfc_field_evidence": model["nfc_field_evidence"],
        "jlcpcb_live_surface": model["jlcpcb_live_surface"],
        "bom_delta": model["bom_delta"],
        "acceptance_gates": model["acceptance_gates"],
    }


def render_json(model: dict, base: dict) -> str:
    return json.dumps(generated_policy(model, base), indent=2, ensure_ascii=False) + "\n"


def render_csv(model: dict) -> str:
    parts = {row["mpn"]: row for row in model["jlcpcb_live_surface"]["parts"]}
    rows: list[dict[str, object]] = []
    for change, group, instance, mpn in (
        ("ADD", "pin10_power", "u219_pin10_switch", "SN74CBTLV1G125DCKR"),
        ("ADD", "pin10_power", "u219_pin10_oe_driver", "SN74LVC1G06DCKR"),
        ("ADD", "nfc_evidence", "u219_field_bridge_d1_d2", "BAT54S,215"),
        ("ADD", "nfc_evidence", "u219_field_comparator", "LMV331IDBVR"),
        ("ADD", "support_passives", "u219_field_input_r_pair", "0402WGF1001TCE"),
        ("ADD", "support_passives", "u219_10k_network", "0402WGF1002TCE"),
        ("ADD", "support_passives", "u219_100k_network", "0402WGF1003TCE"),
        ("ADD", "support_passives", "u219_field_hysteresis", "0402WGF1004TCE"),
        ("ADD", "support_passives", "u219_field_env_cap", "GRM155R71H103KA88D"),
        ("ADD", "support_passives", "u219_bypass_caps", "CC0402KRX7R9BB104"),
    ):
        part = parts[mpn]
        qty = part.get("quantity_per_device", 1)
        price = decimal(part["unit_price_usd"])
        rows.append({
            "change": change,
            "group": group,
            "instance": instance,
            "manufacturer": part["manufacturer"],
            "mpn_or_bundle": mpn,
            "jlc_number": part["jlc_number"],
            "qty_per_device": qty,
            "qty_one_prototype": qty,
            "route": "J0 Extended SMT / Standard PCBA",
            "can_presale_number": part["can_presale_number"],
            "moq": part["moq"],
            "unit_price_usd": str(price),
            "line_per_device_usd": str(price * qty),
            "line_one_prototype_usd": str(price * qty),
            "evidence_date": model["evidence_date"],
            "note": "live available-order quantity uses canPresaleNumber",
        })
    rows.append({
        "change": "REMOVE", "group": "pin10_power", "instance": "u214_series_busy",
        "manufacturer": "Panasonic", "mpn_or_bundle": "ERJ-2RKF22R0X", "jlc_number": "base selection",
        "qty_per_device": -1, "qty_one_prototype": -1, "route": "removed from overlay target",
        "can_presale_number": "n/a", "moq": "n/a", "unit_price_usd": "0.0155",
        "line_per_device_usd": "-0.0155", "line_one_prototype_usd": "-0.0155",
        "evidence_date": model["evidence_date"], "note": "saved base quantity-100 unit-price basis",
    })
    rows.append({
        "change": "DNP", "group": "nfc_evidence", "instance": "u219_pickup_c0g_tuning_bank",
        "manufacturer": "TBD after VNA", "mpn_or_bundle": "DNP-C0G-BANK", "jlc_number": "TBD",
        "qty_per_device": 0, "qty_one_prototype": 0, "route": "not orderable until VNA/HIL selection",
        "can_presale_number": 0, "moq": "TBD", "unit_price_usd": "", "line_per_device_usd": "",
        "line_one_prototype_usd": "", "evidence_date": model["evidence_date"],
        "note": "footprints only; no exact production MPN accepted",
    })
    rows.append({
        "change": "SELECTED_POPULATED_NET", "group": "complete", "instance": "H1-R2-U219-CAP-01",
        "manufacturer": "", "mpn_or_bundle": "", "jlc_number": "", "qty_per_device": "", "qty_one_prototype": "",
        "route": "", "can_presale_number": "", "moq": "", "unit_price_usd": "",
        "line_per_device_usd": "0.7392", "line_one_prototype_usd": "0.7392",
        "evidence_date": model["evidence_date"],
        "note": "all selected populated U219 support additions less the removed 22-Ohm part; DNP tuning bank remains unpopulated",
    })
    fieldnames = list(rows[0])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def outputs(model: dict, base: dict) -> dict[Path, str]:
    return {GENERATED_JSON: render_json(model, base), GENERATED_CSV: render_csv(model)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    model, base = load_json(SOURCE), load_json(BASE)
    errors = validate(model, base)
    if errors:
        for error in errors:
            print(error)
        return 1
    rendered = outputs(model, base)
    if args.write:
        for path, content in rendered.items():
            path.write_text(content, encoding="utf-8")
    if args.check:
        stale = [path for path, content in rendered.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        for path in stale:
            print(f"stale generated artifact: {path.relative_to(ROOT)}")
        return int(bool(stale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
