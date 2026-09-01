import copy
import json
import unittest

from hardware.verification import h5_supplier_response


class H5SupplierResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pending = json.loads(
            h5_supplier_response.INPUT.read_text(encoding="utf-8")
        )

    def complete_response(self) -> dict:
        data = copy.deepcopy(self.pending)
        data["status"] = "response_recorded"
        data["supplier"].update(
            {
                "legal_entity": "Example Manufacturing Ltd.",
                "received_on": "2026-08-27",
                "source_reference": "supplier-message-123",
            }
        )
        data["sa818s_v"].update(
            {
                "standard_pcba_installation": True,
                "sample_lead_time_days": 21,
                "moq": 1,
                "preorder_or_service_charge_usd": 5.0,
                "notes": "exact MPN only",
            }
        )
        data["dual_module_job"].update(
            {
                "accepted": True,
                "common_rev_1_8_land_pattern_confirmed": True,
                "separate_rf_paths_confirmed": True,
                "notes": "accepted as two independent fitted positions",
            }
        )
        for row in data["j4_f_operations"]:
            row.update(
                {
                    "accepted": True,
                    "setup_nre_usd": 10.0,
                    "per_unit_usd_q5": 2.0,
                    "per_unit_usd_q10": 1.5,
                    "required_fixtures_or_files": [],
                    "reject_rework_terms": "rework or replace after failed supplied test",
                }
            )
        for row in data["j4_p_operations"]:
            if row.get("in_supplier_scope") is False:
                continue
            row.update(
                {
                    "accepted": True,
                    "setup_nre_usd": 5.0,
                    "per_unit_usd_q5": 1.0,
                    "per_unit_usd_q10": 0.75,
                    "requirements_or_exclusions": "none",
                }
            )
        data["battery_shipping"].update({"supply_scope": False, "user_supplied": True})
        data["identity_control"].update(
            {
                "exact_external_mpns_controlled_at_incoming_inspection": True,
                "silent_substitution_prohibited": True,
                "exceptions": [],
                "notes": "customer approval required for any change",
            }
        )
        return data

    def test_current_partial_record_is_fail_closed_and_generated(self):
        result = h5_supplier_response.build()
        self.assertEqual("partial_response_gate_open", result["status"])
        self.assertFalse(result["summary"]["response_complete"])
        self.assertFalse(result["summary"]["factory_gate_passed"])
        self.assertGreater(result["summary"]["missing_field_count"], 0)
        self.assertEqual([], result["explicit_declines"])
        self.assertEqual(1, result["summary"]["out_of_supplier_scope_operations"])
        self.assertEqual(4, result["summary"]["release_required_final_assembly_operations"])
        self.assertEqual(3, result["summary"]["optional_non_gating_operations"])
        self.assertTrue(result["checks"]["exact_sa818s_v_identity_preserved"])
        self.assertTrue(result["checks"]["commercial_layout_and_fabrication_authority_remains_false"])
        self.assertEqual(0, result["summary"]["orders_authorized"])

    def test_complete_positive_response_passes_supplier_gate_only(self):
        result = h5_supplier_response.build(self.complete_response())
        self.assertEqual("passed_supplier_gate", result["status"])
        self.assertTrue(result["summary"]["response_complete"])
        self.assertTrue(result["summary"]["factory_gate_passed"])
        self.assertEqual([], result["missing_fields"])
        self.assertTrue(all(value is False for value in result["authorization"].values()))
        self.assertEqual("prepare the separate cost/order decision", result["next"])

    def test_complete_decline_requires_alternate_factory(self):
        data = self.complete_response()
        data["j4_f_operations"][0]["accepted"] = False
        result = h5_supplier_response.build(data)
        self.assertEqual("complete_response_gate_failed", result["status"])
        self.assertTrue(result["summary"]["response_complete"])
        self.assertFalse(result["summary"]["factory_gate_passed"])
        self.assertIn("alternate factory", result["next"])

    def test_optional_function_test_and_packing_do_not_gate_one_prototype(self):
        data = self.complete_response()
        for row in data["j4_f_operations"] + data["j4_p_operations"]:
            if row.get("required_for_release") is False:
                row["accepted"] = False
        result = h5_supplier_response.build(data)
        self.assertEqual("passed_supplier_gate", result["status"])
        self.assertEqual([], result["explicit_declines"])

    def test_response_record_cannot_grant_order_authority(self):
        data = self.complete_response()
        data["authorization"]["purchase"] = True
        result = h5_supplier_response.build(data)
        self.assertFalse(result["summary"]["factory_gate_passed"])
        self.assertIn(
            "the response record cannot authorize commercial, layout or fabrication actions",
            result["blockers"],
        )


if __name__ == "__main__":
    unittest.main()
