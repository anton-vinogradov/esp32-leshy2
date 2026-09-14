import importlib.util
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "hardware/verification/h5_r2_current_routes.py"
SPEC = importlib.util.spec_from_file_location("h5_r2_current_routes", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class H5R2CurrentRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.build()

    def test_current_inventory_has_no_unmapped_route(self):
        self.assertEqual([], self.result["errors"])
        self.assertEqual(
            "reviewed_with_one_order_time_global_sourcing_gate",
            self.result["status"],
        )
        self.assertEqual(250, self.result["summary"]["component_groups"])
        self.assertEqual(1218, self.result["summary"]["component_articles"])
        self.assertEqual(205, self.result["summary"]["legacy_routes_reused"])
        self.assertEqual(45, self.result["summary"]["new_or_replaced_routes"])

    def test_only_wbc16_is_a_current_sourcing_gate(self):
        gates = [
            row for row in self.result["routes"]
            if row["route_class"] == "jlcpcb_global_sourcing_required"
        ]
        self.assertEqual(["WBC16-1TLC"], [row["mpn"] for row in gates])
        self.assertTrue(self.result["boundary"]["h6_may_continue"])
        self.assertFalse(self.result["boundary"]["order_release_may_continue"])

    def test_docs_expose_real_cost_and_gate(self):
        ru = MODULE.render_doc(self.result, True)
        self.assertIn("250 закупаемых групп / 1218 изделий", ru)
        self.assertIn("WBC16-1TLC", ru)
        self.assertIn(f"${self.result['summary']['known_combined_usd']:.2f}", ru)
        for language in (False, True):
            page = MODULE.render_doc(self.result, language)
            self.assertIn("SN74LV20APWR", page)
            self.assertIn("MOQ 21", page)
            self.assertIn("$8.9565", page)

    def test_four_gct_ports_use_the_fresh_preorder_route(self):
        rows = {row["device_id"]: row for row in self.result["routes"]}
        self.assertNotIn("jae_dx07s016ja1r1500", rows)
        gct = rows["gct_usb4105_gf_a"]
        self.assertEqual(4, gct["quantity_per_product"])
        self.assertEqual("jlcpcb_preorder", gct["route_class"])
        self.assertEqual("C3020560", gct["jlcpcb_part_number"])
        fresh = gct["fresh_factory_snapshot"]
        self.assertEqual(9, fresh["minimum_purchase_quantity"])
        self.assertEqual(1044, fresh["stock"])
        self.assertEqual(9.59, fresh["estimated_purchase_subtotal_usd"])
        self.assertFalse(fresh["is_order_or_reservation"])
        self.assertIn(fresh["source"], self.result["inputs"])

    def test_three_c5_eco_routes_retain_exact_timestamped_standard_pcba_evidence(self):
        routes = {row["device_id"]: row for row in self.result["routes"]}
        expected = {
            "ti_ts3usb221erser": ("TS3USB221ERSER", "C129313", 1, 2998, 2993, "2026-09-14T00:03:22Z"),
            "ti_sn74lv20apwr": ("SN74LV20APWR", "C2862070", 2, 0, None, "2026-09-14T00:10:12Z"),
            "nexperia_nx3008nbks_115": ("NX3008NBKS,115", "C396098", 3, 5255, 5229, "2026-09-14T00:24:23Z"),
        }
        for device_id, (mpn, number, quantity, stock, available, checked) in expected.items():
            with self.subTest(device_id=device_id):
                row = routes[device_id]
                self.assertEqual((mpn, number, quantity),
                                 (row["mpn"], row["jlcpcb_part_number"], row["quantity_per_product"]))
                self.assertIsNone(row["legacy_h5_route"])
                snapshot = row["fresh_factory_snapshot"]
                self.assertEqual((stock, available, checked),
                                 (snapshot["stock"], snapshot["available_order_quantity"], snapshot["checked_at_utc"]))
                self.assertIn("Standard", snapshot["assembly_services"])
                self.assertEqual("SMT", snapshot["assembly_type"])
                self.assertIn(snapshot["source"], self.result["inputs"])
                self.assertFalse(snapshot["is_order_or_reservation"])
                self.assertTrue(snapshot["order_time_recheck"])

    def test_zero_stock_nand_is_preorder_not_a_stocked_two_piece_quote(self):
        row = next(row for row in self.result["routes"] if row["device_id"] == "ti_sn74lv20apwr")
        self.assertEqual("jlcpcb_preorder", row["route_class"])
        snapshot = row["fresh_factory_snapshot"]
        self.assertEqual((0, None, 21),
                         (snapshot["stock"], snapshot["available_order_quantity"], snapshot["minimum_purchase_quantity"]))
        self.assertEqual(0.4265, snapshot["estimated_unit_price_usd_at_minimum"])
        self.assertEqual(8.9565, snapshot["estimated_purchase_subtotal_usd"])
        self.assertTrue(snapshot["not_a_stocked_price_tier"])
        self.assertFalse(snapshot["final_quote_confirmed"])
        self.assertFalse(snapshot["stock_allocation_confirmed"])
        self.assertIsNone(snapshot["lead_time"])
        gates = self.result["current_preorder_gates"]
        self.assertEqual(6, len(gates))
        self.assertEqual(6, self.result["summary"]["current_preorder_confirmation_gates"])
        self.assertIn("SN74LV20APWR", {gate["mpn"] for gate in gates})
        self.assertTrue(all(gate["order_release_allowed"] is False for gate in gates))
        self.assertIn("MOQ21", self.result["boundary"]["reason"])

    def test_c5_eco_capture_rejects_identity_service_and_availability_changes(self):
        devices = MODULE.load(MODULE.DEVICES)["devices"]
        groups = {row["device_id"]: row for row in MODULE.load(MODULE.INVENTORY)["component_groups"]}
        for device_id in MODULE.C5_ECO_PARTS:
            for mutation in ("mpn", "manufacturer", "jlc", "service", "assembly", "timestamp", "route"):
                with self.subTest(device_id=device_id, mutation=mutation):
                    group, device = copy.deepcopy(groups[device_id]), copy.deepcopy(devices[device_id])
                    source = device["orderable_source"]
                    if mutation == "mpn":
                        group["mpn"] = device["mpn"] = "OTHER"
                    elif mutation == "manufacturer":
                        source["manufacturer"] = device["manufacturer"] = "OTHER"
                    elif mutation == "jlc":
                        source["jlcpcb_part_number"] = group["jlcpcb_part_number"] = "C0"
                    elif mutation == "service":
                        source["assembly_services"] = ["Economic"]
                    elif mutation == "assembly":
                        source["assembly_type"] = "manual"
                    elif mutation == "timestamp":
                        source["checked"] = None
                    else:
                        source["live_inventory"]["route"] = "catalog_only"
                    _, errors = MODULE.c5_eco_snapshot(group, device)
                    self.assertTrue(errors)
        for device_id in ("ti_ts3usb221erser", "nexperia_nx3008nbks_115"):
            for field in ("stock", "available_order_quantity"):
                device = copy.deepcopy(devices[device_id])
                device["orderable_source"]["live_inventory"][field] = 0
                self.assertTrue(MODULE.c5_eco_snapshot(groups[device_id], device)[1])
        device = copy.deepcopy(devices["ti_sn74lv20apwr"])
        device["orderable_source"]["preorder_estimate"]["not_a_stocked_price_tier"] = False
        self.assertTrue(MODULE.c5_eco_snapshot(groups["ti_sn74lv20apwr"], device)[1])

    def test_generated_current_results_and_their_inputs_are_hash_bound(self):
        self.assertEqual(self.result, json.loads(MODULE.OUTPUT.read_text()))
        for path, expected in self.result["inputs"].items():
            self.assertEqual(expected, hashlib.sha256((REPO / path).read_bytes()).hexdigest(), path)
        self.assertEqual(MODULE.render_doc(self.result, False), MODULE.EN.read_text())
        self.assertEqual(MODULE.render_doc(self.result, True), MODULE.RU.read_text())

    def test_invalid_nand_availability_blocks_current_route_acceptance(self):
        devices = copy.deepcopy(MODULE.load(MODULE.DEVICES))
        devices["devices"]["ti_sn74lv20apwr"]["orderable_source"]["live_inventory"]["route"] = "stocked"
        original_load = MODULE.load
        with patch.object(MODULE, "load", side_effect=lambda path:
                          devices if path == MODULE.DEVICES else original_load(path)):
            result = MODULE.build()
        self.assertEqual("fail", result["status"])
        self.assertTrue(result["errors"])
        self.assertFalse(result["boundary"]["h6_may_continue"])
        self.assertFalse(result["boundary"]["order_release_may_continue"])


if __name__ == "__main__":
    unittest.main()
