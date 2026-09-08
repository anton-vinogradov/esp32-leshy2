"""Finite one-product/three-service USB consolidation, never a generic merge."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
OLD, NEW = "jae_dx07s016ja1r1500", "gct_usb4105_gf_a"
SPEC = importlib.util.spec_from_file_location("usb_inventory", ROOT / "hardware/ecad/h2_r2_native_inventory.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class USBGroupConsolidationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"scope": "base_product", "device_id": OLD, "mpn": "JAE DX07S016JA1R1500", "quantity": "1", "placements": "product_usb_connector"},
            {"scope": "base_product", "device_id": NEW, "mpn": "GCT USB4105-GF-A", "quantity": "2", "placements": "c5_service_usb_connector;rp_service_usb_connector"},
        ]
        self.model = {"r2_device_replacements": {OLD: {"device_id": NEW, "mpn": "GCT USB4105-GF-A", "merge_into_existing_group": NEW}},
                      "r2_quantity_overrides": {NEW: {"quantity_per_device": 3}}}

    def test_exact_one_plus_three_is_four_not_duplicate_overwrite(self):
        before = copy.deepcopy(self.rows)
        result = MODULE.r2_cost_base_rows(self.rows, self.model)
        self.assertEqual(before, self.rows)
        self.assertEqual(1, len(result))
        self.assertEqual(4, result[0]["quantity_per_device"])
        self.assertEqual(NEW, result[0]["device_id"])
        self.assertEqual(OLD, result[0]["historical_capture_route"])
        self.assertEqual({"product_usb_connector", "c5_service_usb_connector", "hub_rp_service_usb_connector", "rf_rp_service_usb_connector"},
                         set(result[0]["role"].split(",")))

    def test_naive_duplicate_replacement_is_rejected(self):
        del self.model["r2_device_replacements"][OLD]["merge_into_existing_group"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MODULE.r2_cost_base_rows(self.rows, self.model)

    def test_unreviewed_target_or_source_is_rejected(self):
        for change in ("target", "source", "mpn"):
            with self.subTest(change=change):
                model = copy.deepcopy(self.model)
                if change == "target":
                    model["r2_device_replacements"][OLD]["merge_into_existing_group"] = "another_device"
                elif change == "source":
                    model["r2_device_replacements"]["another_device"] = model["r2_device_replacements"].pop(OLD)
                else:
                    model["r2_device_replacements"][OLD]["mpn"] = "USB4105-060"
                with self.assertRaisesRegex(ValueError, "unreviewed"):
                    MODULE.r2_cost_base_rows(self.rows, model)

    def test_missing_duplicate_wrong_quantity_or_scope_is_rejected(self):
        cases = []
        cases.append((self.rows[:1], self.model))
        cases.append((self.rows + [self.rows[1]], self.model))
        rows = copy.deepcopy(self.rows); rows[0]["quantity"] = "2"; cases.append((rows, self.model))
        rows = copy.deepcopy(self.rows); rows[1]["scope"] = "external"; cases.append((rows, self.model))
        model = copy.deepcopy(self.model); model["r2_quantity_overrides"][NEW]["quantity_per_device"] = 4; cases.append((self.rows, model))
        for rows, model in cases:
            with self.subTest(rows=rows, model=model), self.assertRaisesRegex(ValueError, "exactly one product"):
                MODULE.r2_cost_base_rows(rows, model)

    def test_real_current_model_has_one_four_port_group(self):
        with (ROOT / "hardware/architecture/generated/G2F-3I-target-bom.csv").open() as stream:
            historical = list(csv.DictReader(stream))
        model = json.loads((ROOT / "hardware/product-design/h1-r2-cost-review.json").read_text())
        rows = MODULE.r2_cost_base_rows(historical, model)
        self.assertEqual(220, len(rows))
        self.assertEqual(1120, sum(row["quantity_per_device"] for row in rows))
        self.assertNotIn(OLD, {row["device_id"] for row in rows})
        self.assertEqual([4], [row["quantity_per_device"] for row in rows if row["device_id"] == NEW])

    def test_all_seventeen_product_endpoints_have_explicit_unchanged_roles(self):
        expected = {"A1_GND": "POWER_GROUND", "A4_VBUS": "USB_C_VBUS_RAW",
                    "A5_CC1": "USB_C_CC1_CONNECTOR", "A6_DP": "USB2_DP_CONNECTOR",
                    "A7_DM": "USB2_DM_CONNECTOR", "A8_SBU1": None,
                    "A9_VBUS": "USB_C_VBUS_RAW", "A12_GND": "POWER_GROUND",
                    "B1_GND": "POWER_GROUND", "B4_VBUS": "USB_C_VBUS_RAW",
                    "B5_CC2": "USB_C_CC2_CONNECTOR", "B6_DP": "USB2_DP_CONNECTOR",
                    "B7_DM": "USB2_DM_CONNECTOR", "B8_SBU2": None,
                    "B9_VBUS": "USB_C_VBUS_RAW", "B12_GND": "POWER_GROUND", "SHIELD": "POWER_GROUND"}
        contract = json.loads((ROOT / "hardware/ecad/h2-r2-topology-overrides.json").read_text())
        actual = {key.split(".", 1)[1]: value for key, value in contract["endpoint_overrides"].items() if key.startswith("product_usb_connector.")}
        self.assertEqual(expected, actual)
        rows = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json").read_text())["rows"]
        product = [row for row in rows if row["instance"] == "product_usb_connector"]
        self.assertEqual(expected, {row["contact"]: row["net"] for row in product})
        self.assertEqual({NEW}, {row["device_id"] for row in product})
        self.assertEqual({"J1"}, {row["reference"] for row in product})
        self.assertEqual({"LESHY2-RF-R2"}, {row["project"] for row in product})

    def test_fresh_factory_route_does_not_replace_historical_price_or_order(self):
        device = json.loads((ROOT / "hardware/architecture/devices.json").read_text())["devices"][NEW]
        self.assertEqual((100, 0.5745), (device["cost"]["target_quantity"], device["cost"]["unit_price_usd"]))
        route = device["orderable_source"]
        self.assertEqual(("Global Connector Technology", "C3020560", 9),
                         (route["manufacturer"], route["jlcpcb_part_number"], route["minimum_order_quantity"]))
        self.assertFalse(route["order_or_stock_reservation_made"])
        self.assertEqual((16, 12, 5.0, 20000), tuple(device["electrical_contract"][key] for key in
            ("mating_contact_count", "smt_solder_position_count", "collective_vbus_current_rating_a", "durability_mating_cycles")))

    def test_current_typed_interface_map_has_one_complete_passive_gct_and_no_retired_jae(self):
        from hardware.verification import h6_r2_electrical_semantics as semantics
        fragment = semantics.load(ROOT / "hardware/verification/h6-electrical-pins-interfaces.json")
        reviews = semantics.reviewed_maps([fragment], semantics.load(semantics.MATERIAL)["groups"])
        self.assertNotIn(OLD, reviews)
        self.assertEqual(1, sum(row["device_id"] == NEW for row in fragment["devices"]))
        pins = reviews[NEW]["pins"]
        self.assertEqual({"A1","A4","A5","A6","A7","A8","A9","A12",
                          "B1","B4","B5","B6","B7","B8","B9","B12","SH"}, set(pins))
        self.assertEqual({"passive"}, {pin["type"] for pin in pins.values()})
        self.assertEqual([], reviews[NEW]["unresolved"])


if __name__ == "__main__":
    unittest.main()
