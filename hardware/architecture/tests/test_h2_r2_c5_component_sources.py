"""Source-only C5 allocation checks; no native generation or electrical admission."""

import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
UI, RF = "LESHY2-UI-R2", "LESHY2-RF-R2"
TS = "ti_ts3usb221erser"
LV = "ti_sn74lv20apwr"
NX = "nexperia_nx3008nbks_115"
OLD_TS, OLD_LV, OLD_NX = "onsemi_fsusb42_mux", "nexperia_74hc20pw_118", "diodes_2n7002dw_7_f"
NEW = {"c5_service_path_logic": "U59", "c5_service_path_logic_bypass": "C86"}


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"hardware/ecad/{name}.py")
    result = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(result)
    return result


class C5ComponentSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.devices = load("hardware/architecture/devices.json")["devices"]
        cls.inventory = load("hardware/ecad/h2-r2-native-inventory-contract.json")
        cls.instances = load("hardware/ecad/h2-r2-instance-ledger-contract.json")
        cls.footprints = load("hardware/ecad/h2-r2-symbol-footprint-contract.json")
        cls.native_inventory = module("h2_r2_native_inventory")
        cls.instance_generator = module("h2_r2_instance_ledger")
        cls.symbol_generator = module("h2_r2_symbol_library")

    def quantities(self):
        authority = self.inventory["authority"]
        base = self.native_inventory.r2_cost_base_rows(
            self.native_inventory.load_authority(ROOT / authority["component_groups"]),
            load(authority["r2_cost_model"]),
        )
        quantities = {row["device_id"]: row["quantity_per_device"] for row in base}
        contract = self.inventory["component_inventory"]
        for row in contract["adjustments"]:
            quantities[row["device_id"]] += row["quantity_delta"]
        for row in contract["new_groups"]:
            self.assertNotIn(row["device_id"], quantities)
            quantities[row["device_id"]] = row["quantity"]
        return quantities

    def test_primary_pin_maps_are_exact_package_specific_not_old_vendor_numbering(self):
        expected_ts = {"1": "HSD1_PLUS", "2": "HSD1_MINUS", "3": "HSD2_PLUS", "4": "HSD2_MINUS",
                       "5": "GND", "6": "OE", "7": "D_MINUS", "8": "D_PLUS", "9": "SEL", "10": "VCC"}
        expected_nx = {"1": "S1", "2": "G1", "3": "D2", "4": "S2", "5": "G2", "6": "D1"}
        for device_id, expected in ((TS, expected_ts), (NX, expected_nx)):
            actual = self.devices[device_id]
            self.assertEqual(expected, {contact["physical"]: name for name, contact in actual["contacts"].items()})
            self.assertEqual(expected, actual["pinout_invariant"]["physical_pin_to_contact"])
        self.assertEqual(self.devices[OLD_LV]["contacts"], self.devices[LV]["contacts"])
        self.assertEqual(set(self.devices[OLD_TS]["contacts"]), set(self.devices[TS]["contacts"]))
        self.assertEqual(set(self.devices[OLD_NX]["contacts"]), set(self.devices[NX]["contacts"]))
        self.assertNotEqual(self.devices[OLD_NX]["pinout_invariant"]["physical_pin_to_contact"], expected_nx)
        self.assertEqual("signal", self.devices[TS]["contacts"]["OE"]["role"])

    def test_exact_factory_captures_distinguish_stocked_and_preorder(self):
        expected = {
            TS: ("Texas Instruments", "C129313", "2026-09-14T00:03:22Z", 2998, 2993, 1),
            LV: ("Texas Instruments", "C2862070", "2026-09-14T00:10:12Z", 0, None, 21),
            NX: ("Nexperia", "C396098", "2026-09-14T00:24:23Z", 5255, 5229, 1),
        }
        for device_id, values in expected.items():
            with self.subTest(device=device_id):
                source = self.devices[device_id]["orderable_source"]
                stock = source["live_inventory"]
                self.assertEqual(values, (source["manufacturer"], source["jlcpcb_part_number"], source["checked"],
                                          stock["stock"], stock["available_order_quantity"], stock["moq"]))
                self.assertEqual(("Extended", "SMT", ["Economic", "Standard"]),
                                 (source["library_type"], source["assembly_type"], source["assembly_services"]))
        lv = self.devices[LV]["orderable_source"]
        self.assertEqual("pre_order", lv["live_inventory"]["route"])
        self.assertIsNone(lv["live_inventory"]["lead_time"])
        self.assertEqual(0.4265, lv["preorder_estimate"]["unit_price"])
        self.assertTrue(lv["preorder_estimate"]["not_a_stocked_price_tier"])
        self.assertNotIn("price_tiers_usd", lv)
        for device_id, prices in ((TS, [.3416, .2678, .236, .1967, .1791, .1685]),
                                  (NX, [.1615, .125, .1094, .0899, .0813, .0761])):
            tiers = self.devices[device_id]["orderable_source"]["price_tiers_usd"]
            self.assertEqual([1, 50, 150, 500, 3000, 6000], [row["quantity"] for row in tiers])
            self.assertEqual(prices, [row["unit_price"] for row in tiers])

    def test_conditioned_limits_do_not_become_electrical_or_timing_qualification(self):
        for device_id in (TS, LV, NX):
            self.assertEqual("engineering_candidate_not_electrically_or_hil_qualified", self.devices[device_id]["qualification"])
            contract = self.devices[device_id]["electrical_contract"]
            for flag in ("circuit_qualification", "timing_qualification", "hil_qualification"):
                self.assertIs(False, contract[flag])
        ts = self.devices[TS]["electrical_contract"]
        self.assertEqual([2.3, 3.6], ts["recommended_supply_v"])
        self.assertEqual((480, 1000, "typical_only_no_guaranteed_minimum"),
                         (ts["usb_speed_mbps"], ts["bandwidth_mhz"], ts["bandwidth_limit_type"]))
        self.assertEqual({"supply_v": 0, "port_v": [0, 5.25]}, ts["power_off_port_leakage_conditions"])
        self.assertEqual(ts["power_off_port_leakage_max_ua"], ts["power_off_leakage_max_ua"])
        lv = self.devices[LV]["electrical_contract"]
        self.assertEqual([3.0, 3.6], lv["logic_thresholds"]["supply_v"])
        self.assertEqual((50, .1, .1), (lv["low_load_output"]["current_ua"],
                                     lv["low_load_output"]["voh_min_vcc_minus_v"], lv["low_load_output"]["vol_max_v"]))
        nx = self.devices[NX]["electrical_contract"]
        self.assertEqual({"max_ohm": 2.8, "vgs_v": 1.8, "drain_current_ma": 10, "junction_temperature_c": 25},
                         nx["on_resistance_limits"][0])
        self.assertIn("25 C only", nx["open_conditions"])
        self.assertFalse(self.devices[OLD_NX]["current_r2_scope_review"]["electrical_qualification"])

    def test_cost_schema_keeps_capture_time_and_preorder_allocation_not_a_unit_tier(self):
        from hardware.architecture import generate

        database, candidates = generate.load_sources()
        self.assertEqual([], generate.validate_sources(database, candidates))
        for device_id in (TS, LV, NX):
            cost = self.devices[device_id]["cost"]
            self.assertEqual(1, cost["target_quantity"])
            self.assertEqual("2026-09-14", cost["source"]["checked"])
            self.assertEqual(self.devices[device_id]["orderable_source"]["checked"],
                             cost["source"]["checked_at"])
            # The existing metadata validator must still reject the old format.
            broken = copy.deepcopy(database)
            broken["devices"][device_id]["cost"]["source"]["checked"] = cost["source"]["checked_at"]
            self.assertIn(f"device {device_id}: cost source checked date must be YYYY-MM-DD",
                          generate.validate_sources(broken, candidates))
        lv = self.devices[LV]
        cost, route = lv["cost"], lv["orderable_source"]
        self.assertIs(True, cost["estimated"])
        self.assertIs(False, cost["stocked_unit_tier"])
        self.assertEqual(21, cost["procurement_moq"])
        self.assertEqual(route["live_inventory"]["moq"], cost["procurement_moq"])
        self.assertEqual(route["preorder_estimate"]["unit_price"], cost["unit_price_usd"])
        self.assertEqual(2, self.quantities()[LV])
        self.assertEqual(.853, round(cost["unit_price_usd"] * self.quantities()[LV], 4))
        self.assertEqual(8.9565, round(cost["unit_price_usd"] * cost["procurement_moq"], 4))
        for text in ("not an order total", "MOQ 21", "no stocked quantity-one tier"):
            self.assertIn(text, cost["price_break"])
        broken = copy.deepcopy(database)
        broken["devices"][LV]["cost"]["target_quantity"] = 21
        self.assertIn(f"device {LV}: cost target quantity must be 1 or 100",
                      generate.validate_sources(broken, candidates))

    def test_inventory_changes_only_the_finite_counts_and_keeps_rp_and_pack_parts(self):
        quantities = self.quantities()
        self.assertEqual((252, 1220), (len(quantities), sum(quantities.values())))
        self.assertEqual((252, 1220), (self.inventory["component_inventory"]["expected_group_count"],
                                      self.inventory["component_inventory"]["expected_quantity_per_product"]))
        self.assertEqual({TS: 1, LV: 2, NX: 3, OLD_TS: 2, OLD_NX: 2},
                         {key: quantities[key] for key in (TS, LV, NX, OLD_TS, OLD_NX)})
        self.assertNotIn(OLD_LV, quantities)
        names = self.instances["exact_instance_names"]
        self.assertEqual(["hub_rp_service_usb_switch", "rf_rp_service_usb_switch"], names[OLD_TS])
        self.assertEqual(["pack_hold", "pack_status_buffer"], names[OLD_NX])
        self.assertEqual(["c5_service_hub_reset_sink", "safe_reset_sink_a", "safe_reset_sink_b"], names[NX])
        self.assertEqual({UI: NEW}, self.instances["reference_overrides"])

    def test_definition_contact_and_physical_instance_deltas_are_independently_counted(self):
        quantities = self.quantities()
        external_ids = set(self.inventory["component_inventory"]["non_pcba_dispositions"])
        self.assertEqual(1615, sum(len(self.devices[key]["contacts"]) for key in quantities))
        self.assertEqual(1556, sum(len(self.devices[key]["contacts"]) for key in quantities if key not in external_ids))
        self.assertEqual(1210, sum(value for key, value in quantities.items() if key not in external_ids))
        # Existing replacements retain their package contact counts. Only the
        # second NAND14 and its capacitor2 add physical instance pins (+16).
        for new, old in ((TS, OLD_TS), (LV, OLD_LV), (NX, OLD_NX)):
            self.assertEqual(len(self.devices[old]["contacts"]), len(self.devices[new]["contacts"]))
        added = len(self.devices[LV]["contacts"]) + len(self.devices["yageo_cc0402krx7r9bb104"]["contacts"])
        self.assertEqual(16, added)
        self.assertEqual(4321, 4305 + added)

    def test_standard_new_package_pad_inventories_have_no_added_exposed_pad(self):
        materializer = module("h2_r2_contact_materialization")
        for device_id, count in ((TS, 10), (LV, 14), (NX, 6)):
            footprint = self.footprints["footprint_overrides"][self.devices[device_id]["mpn"]]
            path, _ = materializer.resolve_footprint(footprint)
            if path is None:
                self.skipTest("Standard KiCad footprint library is unavailable")
            pads, ignored = materializer.parse_pads(path)
            self.assertEqual({str(pin) for pin in range(1, count + 1)}, set(pads))
            self.assertEqual(count, sum(row["occurrences"] for row in pads.values()))
            self.assertEqual(0, ignored)

    def test_footprints_and_both_prefix_helpers_keep_nx_as_q(self):
        for device_id, footprint, prefix in (
            (TS, "Package_DFN_QFN:Texas_UQFN-10_1.5x2mm_P0.5mm", "U"),
            (LV, "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "U"),
            (NX, "Package_TO_SOT_SMD:SOT-363_SC-70-6", "Q"),
        ):
            self.assertEqual(footprint, self.footprints["footprint_overrides"][self.devices[device_id]["mpn"]])
            for helper in (self.instance_generator, self.symbol_generator):
                self.assertEqual(prefix, helper.reference_prefix(device_id, footprint))
        self.assertEqual(["RF_02_PACK_SAFETY_AON"], self.footprints["sheet_affinity_overrides"][OLD_NX])

    def test_in_memory_instance_allocation_preserves_all_1208_existing_ref_owner_tuples(self):
        # Allocation fixture only: deliberately no symbol/contact generation,
        # native export, schema acceptance or claim that published outputs are fresh.
        inventory = load("hardware/ecad/generated/H2-R2-native-inventory.json")
        definitions = load("hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json")
        old_rows = [row for row in load("hardware/ecad/generated/H2-R2-native-instance-ledger.json")["rows"]
                    if row["instance"] not in NEW]
        old_groups = {row["device_id"]: row for row in inventory["component_groups"]}
        old_definitions = {row["device_id"]: row for row in definitions["groups"]}
        replacements = {TS: OLD_TS, LV: OLD_LV, NX: OLD_NX}
        new_groups = {row["device_id"]: row for row in self.inventory["component_inventory"]["new_groups"]}
        projected_groups, projected_definitions = [], []
        for device_id, quantity in self.quantities().items():
            prototype = device_id if device_id in old_groups else replacements[device_id]
            group = copy.deepcopy(old_groups[prototype])
            group.update(device_id=device_id, mpn=self.devices[device_id]["mpn"], quantity_per_product=quantity)
            if device_id in new_groups:
                group["role"] = new_groups[device_id].get("role", "")
            projected_groups.append(group)
            definition = copy.deepcopy(old_definitions[prototype])
            definition["device_id"] = device_id
            if device_id in replacements:
                definition["symbol_id"] = f"Leshy2_R2:{device_id}"
            if device_id in self.footprints["sheet_affinity_overrides"]:
                definition["native_sheet_affinity"] = self.footprints["sheet_affinity_overrides"][device_id]
            mpn = self.devices[device_id]["mpn"]
            if mpn in self.footprints["footprint_overrides"]:
                definition["footprint"] = self.footprints["footprint_overrides"][mpn]
            projected_definitions.append(definition)
        inventory["component_groups"] = projected_groups
        definitions["groups"] = projected_definitions
        overrides = {
            ROOT / "hardware/ecad/generated/H2-R2-native-inventory.json": inventory,
            ROOT / "hardware/ecad/generated/H2-R2-symbol-footprint-ledger.json": definitions,
        }
        real_load = self.instance_generator.load
        with mock.patch.object(self.instance_generator, "load", side_effect=lambda path: (
            overrides[path] if path in overrides else real_load(path)
        )):
            result = self.instance_generator.build()
        self.assertEqual([], result["errors"])
        self.assertEqual((1210, 246), (len(result["rows"]), result["summary"]["component_group_count"]))
        old = {row["instance_uid"]: row for row in old_rows}
        self.assertEqual(1208, len(old))
        fitted = {row["instance_uid"]: row for row in result["rows"]}
        for uid, row in old.items():
            for field in ("reference", "project", "sheet", "instance"):
                self.assertEqual(row[field], fitted[uid][field], (uid, field))
        frozen = sorted((row["project"], row["instance"], row["reference"]) for uid, row in fitted.items() if uid in old)
        self.assertEqual("216e588158c69e18ff7f60999b14a26ea543388b2c705a98cc6fd89513b60250",
                         hashlib.sha256(json.dumps(frozen, separators=(",", ":")).encode()).hexdigest())
        changed = {"c5_service_usb_switch": TS, "c5_service_release_logic": LV,
                   "c5_service_hub_reset_sink": NX, "safe_reset_sink_a": NX, "safe_reset_sink_b": NX}
        for uid, row in old.items():
            self.assertEqual(changed.get(row["instance"], row["device_id"]), fitted[uid]["device_id"])
        self.assertEqual(NEW, {row["instance"]: row["reference"] for uid, row in fitted.items() if uid not in old})


if __name__ == "__main__":
    unittest.main()
