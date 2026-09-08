"""Finite hand-reviewed LED proposals, not blanket autorouter admission.

The policy/record tests run without KiCad. Native obstacle clearance and old
copper preservation belong to the separate candidate promotion/DRC review.
"""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/layout/h6_r2_manual_copper.py"
SPEC = importlib.util.spec_from_file_location("reviewed_led_manual_copper", SCRIPT)
copper = importlib.util.module_from_spec(SPEC)
# Only native dependencies are stubbed, never the production validation logic.
placement_stub = types.ModuleType("h6_r2_placement")
placement_stub.build = Mock(side_effect=AssertionError("a unit test must not regenerate placement"))
with patch.dict(sys.modules, {"pcbnew": types.ModuleType("pcbnew"),
                             "h6_r2_placement": placement_stub}):
    SPEC.loader.exec_module(copper)

PROJECT = "LESHY2-UI-R2"
PREFIX = "/UI_11_STORAGE_CONTROLS_INDICATORS/"
POLICY = json.loads((ROOT / "hardware/layout/h6-r2-routing-policy.json").read_text())


def candidate(canonical="NRF0_TX_LED_A"):
    result = {
        "id": "UI-REVIEWED-" + canonical,
        "project": PROJECT,
        "canonical_net": canonical,
        "kicad_net": PREFIX + canonical,
        "routing_class": "GENERAL_CONTROL",
        "segments": [
            {"layer": "B.Cu", "width_mm": 0.15, "start_mm": [1.0, 1.0], "end_mm": [2.0, 1.0]},
            {"layer": "F.Cu", "width_mm": 0.15, "start_mm": [2.0, 1.0], "end_mm": [3.0, 1.0]},
        ],
        "vias": [{"at_mm": [2.0, 1.0], "diameter_mm": 0.4, "drill_mm": 0.2, "type": "through"}],
        "expected_resolved_connections": 1,
        "reason": "Explicit hand-reviewed resistor-to-LED proposal; native DRC/promotion remain separate.",
        "reviewed_proposal": {"decision": "hand-reviewed proposal", "minimum_clearance_mm": 0.15},
    }
    rebind(result)
    return result


def rebind(route):
    route["reviewed_proposal"]["geometry_sha256"] = copper.proposal_geometry_sha256(route)


def policy_row(route):
    return {**{key: route[key] for key in ("project", "canonical_net", "kicad_net", "routing_class")},
            "route_mode": "automatic_helper_allowed_then_manual_review"}


def validate(route, row=None, policy=None, project=PROJECT):
    copper.validate_reviewed_proposal(route, policy_row(route) if row is None else row,
                                     project, POLICY if policy is None else policy)


class ReviewedLedProposalTests(unittest.TestCase):
    def test_independent_finite_scope_is_exactly_two_ui_nets(self):
        self.assertEqual({
            (PROJECT, "NRF0_TX_LED_A", PREFIX + "NRF0_TX_LED_A"),
            (PROJECT, "S3_TX_LED_A", PREFIX + "S3_TX_LED_A"),
        }, copper.REVIEWED_GENERAL_PROPOSALS)
        for name in ("NRF0_TX_LED_A", "S3_TX_LED_A"):
            validate(candidate(name))

    def test_no_basename_other_sheet_project_or_other_led_admission(self):
        cases = [candidate("NRF1_TX_LED_A"), candidate("C5_TX_LED_A"), candidate("FAULT_LED_A")]
        renamed = candidate()
        renamed["kicad_net"] = "/OTHER_SHEET/NRF0_TX_LED_A"
        cases.append(renamed)
        foreign = candidate()
        foreign["project"] = "LESHY2-RF-R2"
        cases.append(foreign)
        for route in cases:
            with self.subTest(route=route["kicad_net"], project=route["project"]):
                rebind(route)
                with self.assertRaisesRegex(ValueError, "allow-list"):
                    validate(route)
        with self.assertRaisesRegex(ValueError, "allow-list"):
            validate(candidate(), project="LESHY2-RF-R2")

    def test_full_policy_identity_and_mode_are_mandatory(self):
        route = candidate()
        for key, value in (
            ("project", "LESHY2-RF-R2"), ("canonical_net", "S3_TX_LED_A"),
            ("kicad_net", "/OTHER/NRF0_TX_LED_A"), ("routing_class", "SAFETY_CONTROL"),
            ("route_mode", "manual_only"), ("route_mode", "automatic"),
        ):
            row = policy_row(route)
            row[key] = value
            with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, "policy binding/mode"):
                validate(route, row=row)
        with self.assertRaisesRegex(ValueError, "policy binding/mode"):
            validate(route, row={})

    def test_class_cannot_be_relabelled_to_enter_old_manual_branch(self):
        route = candidate()
        route["routing_class"] = "SAFETY_CONTROL"
        rebind(route)
        row = policy_row(route)
        row["route_mode"] = "manual_only"
        with self.assertRaisesRegex(ValueError, "policy binding/mode"):
            copper.preflight_reviewed_proposals([route], {(PROJECT, route["kicad_net"]): row}, POLICY)

    def test_only_an_explicit_hand_review_is_accepted(self):
        for replacement in (None, {}, {"decision": "automatic"}, True):
            route = candidate()
            route["reviewed_proposal"] = replacement
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "hand-review decision"):
                validate(route)
        route = candidate()
        del route["reviewed_proposal"]
        with self.assertRaisesRegex(ValueError, "hand-review decision"):
            validate(route)
        for key, value in (("decision", "hand_reviewed_proposal"), ("minimum_clearance_mm", 0.1),
                           ("minimum_clearance_mm", float("nan")), ("minimum_clearance_mm", "0.15"),
                           ("minimum_clearance_mm", True), ("auto_accept", True)):
            route = candidate()
            route["reviewed_proposal"][key] = value
            with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, "hand-review decision"):
                validate(route)

    def test_missing_id_reason_and_noninteger_or_zero_delta_are_rejected(self):
        for key, values in (("id", [None, "", " "]), ("reason", [None, "", " "]),
                            ("expected_resolved_connections", [0, 2, -1, True, 1.0, "1", None])):
            for value in values:
                route = candidate()
                route[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    validate(route)
        route = candidate()
        del route["id"]
        with self.assertRaises(ValueError):
            validate(route)

    def test_stale_geometry_decision_cannot_cover_changed_segments_or_vias(self):
        for location, key, value in (("segments", "end_mm", [2.1, 1.0]),
                                     ("segments", "layer", "In2.Cu"),
                                     ("vias", "at_mm", [2.1, 1.0])):
            route = candidate()
            route[location][0][key] = value
            with self.subTest(location=location, key=key), self.assertRaisesRegex(ValueError, "geometry changed"):
                validate(route)
        route = candidate()
        route["reviewed_proposal"]["geometry_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "geometry changed"):
            validate(route)

    def test_hash_binds_net_identity_and_has_stable_object_key_order(self):
        route = candidate()
        reordered = {key: route[key] for key in reversed(route)}
        self.assertEqual(copper.proposal_geometry_sha256(route), copper.proposal_geometry_sha256(reordered))
        other = candidate("S3_TX_LED_A")
        self.assertNotEqual(copper.proposal_geometry_sha256(route), copper.proposal_geometry_sha256(other))

    def test_all_policy_signal_layers_allowed_but_reference_layers_and_non_copper_rejected(self):
        for layer in ("F.Cu", "B.Cu", "In2.Cu", "In3.Cu"):
            route = candidate()
            route["segments"][0]["layer"] = layer
            rebind(route)
            validate(route)
        for layer in ("In1.Cu", "In4.Cu", "F.SilkS", "Edge.Cuts", "unknown"):
            route = candidate()
            route["segments"][0]["layer"] = layer
            rebind(route)
            with self.subTest(layer=layer), self.assertRaisesRegex(ValueError, "segment geometry"):
                validate(route)

    def test_segment_width_coordinates_and_competing_geometry_are_fail_closed(self):
        for key, value in (("width_mm", 0.1), ("width_mm", 0.2), ("width_mm", True),
                           ("width_mm", "0.15"), ("start_mm", [True, 1]),
                           ("end_mm", [2, float("inf")]), ("end_mm", [2]),
                           ("end_mm", [1.0, 1.0]), ("net", "OTHER")):
            route = candidate()
            route["segments"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate(route)
        for key in ("path_mm", "layer", "width_mm"):
            route = candidate()
            route[key] = []
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "explicit segments"):
                validate(route)
        for key, value in (("segments", []), ("segments", {}), ("vias", None)):
            route = candidate()
            route[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "explicit segments"):
                validate(route)

    def test_via_recipe_cannot_hide_blind_via_layer_override_or_bad_numbers(self):
        for key, value in (("diameter_mm", 0.5), ("drill_mm", 0.25), ("diameter_mm", "0.4"),
                           ("drill_mm", float("nan")), ("at_mm", [2, False]),
                           ("type", "blind"), ("layers", ["B.Cu", "In3.Cu"]),
                           ("net", "OTHER")):
            route = candidate()
            route["vias"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, "through vias"):
                validate(route)
        route = candidate()
        del route["vias"][0]["type"]  # The existing manifest defaults to through.
        rebind(route)
        validate(route)

    def test_routing_policy_cannot_expand_scope_layers_or_change_geometry_implicitly(self):
        for group, key, value in (
            ("automatic_helper", "allowed_classes", ["GENERAL_CONTROL", "SAFETY_CONTROL"]),
            ("automatic_helper", "routable_layers", ["F.Cu", "B.Cu", "In1.Cu", "In3.Cu"]),
            ("automatic_helper", "routable_layers", ["F.Cu", "B.Cu", "In2.Cu", "In3.Cu", "B.Cu"]),
            ("automatic_helper", "reserved_reference_layers", ["In4.Cu"]),
            ("GENERAL_CONTROL", "nominal_track_width_mm", 0.2),
            ("GENERAL_CONTROL", "route_mode", "manual_only"),
        ):
            policy = copy.deepcopy(POLICY)
            target = policy["classes"][group] if group == "GENERAL_CONTROL" else policy[group]
            target[key] = value
            with self.subTest(group=group, key=key), self.assertRaisesRegex(ValueError, "policy recipe"):
                validate(candidate(), policy=policy)
        with self.assertRaisesRegex(ValueError, "current routing contract"):
            copper.validate_reviewed_proposal(candidate(), policy_row(candidate()), PROJECT, None)

    def test_duplicate_net_or_id_is_rejected_before_any_board_mutation(self):
        first = candidate()
        duplicate_net = copy.deepcopy(first)
        duplicate_net["id"] = "another id"
        duplicate_id = candidate("S3_TX_LED_A")
        duplicate_id["id"] = first["id"]
        for second in (duplicate_net, duplicate_id):
            rows = [first, second]
            bindings = {(PROJECT, row["kicad_net"]): policy_row(row) for row in rows}
            board = Mock()
            with self.subTest(second=second["id"]), self.assertRaisesRegex(ValueError, "duplicate"):
                copper.add_routes(board, rows, bindings, PROJECT, {}, POLICY)
            self.assertEqual([], board.mock_calls)

    def test_later_bad_proposal_is_rejected_before_first_valid_trace_is_added(self):
        first, second = candidate(), candidate("S3_TX_LED_A")
        second["segments"][0]["layer"] = "In1.Cu"
        rows = [first, second]
        board = Mock()
        bindings = {(PROJECT, row["kicad_net"]): policy_row(row) for row in rows}
        with self.assertRaisesRegex(ValueError, "segment geometry"):
            copper.add_routes(board, rows, bindings, PROJECT, {}, POLICY)
        self.assertEqual([], board.mock_calls)

    def test_foreign_project_does_not_disappear_when_build_filters_projects(self):
        route = candidate()
        route["project"] = "MISSPELLED-UI"
        rebind(route)
        with self.assertRaisesRegex(ValueError, "allow-list"):
            copper.preflight_reviewed_proposals([route], {}, POLICY)

    def test_valid_review_retained_in_result_and_native_connection_delta_still_enforced(self):
        route = candidate()
        pcb = Mock(F_Cu=0, B_Cu=31, VIATYPE_THROUGH=3)
        board = Mock()
        board.GetLayerID.return_value = 0
        for after, success in ((0, True), (1, False), (2, False)):
            with self.subTest(after=after), patch.object(copper, "pcbnew", pcb), \
                    patch.object(copper, "remaining_for_net", side_effect=[1, after]):
                if success:
                    result = copper.add_routes(board, [route], {(PROJECT, route["kicad_net"]): policy_row(route)},
                                               PROJECT, {}, POLICY)
                    self.assertEqual(route["reviewed_proposal"], result[0]["reviewed_proposal"])
                    self.assertEqual(1, result[0]["resolved_connections"])
                else:
                    with self.assertRaisesRegex(ValueError, "resolved .* expected 1"):
                        copper.add_routes(board, [route], {(PROJECT, route["kicad_net"]): policy_row(route)},
                                          PROJECT, {}, POLICY)

    def test_other_automatic_class_does_not_enter_legacy_manual_branch(self):
        route = candidate()
        route["routing_class"] = "SERIAL_CONTROL"
        del route["reviewed_proposal"]
        board = Mock()
        with self.assertRaisesRegex(ValueError, "only accepts manual routes"):
            copper.add_routes(board, [route], {(PROJECT, route["kicad_net"]): policy_row(route)}, PROJECT, {}, POLICY)
        self.assertEqual([], board.mock_calls)

    def test_existing_manual_only_records_need_no_new_review_fields(self):
        records = json.loads((ROOT / "hardware/layout/h6-r2-manual-copper.json").read_text())["routes"]
        # Root may append the two proposals concurrently; this check concerns
        # retained legacy modes only, not a frozen route-count golden.
        audit = json.loads((ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json").read_text())
        bindings = {(row["project"], row["kicad_net"]): row for row in audit["rows"]}
        retained = [row for row in records if row["routing_class"] != "GENERAL_CONTROL"]
        self.assertTrue(retained)
        copper.preflight_reviewed_proposals(retained, bindings, None)

    def test_current_two_reviewed_records_match_finite_scope_and_geometry_hashes(self):
        records = json.loads((ROOT / "hardware/layout/h6-r2-manual-copper.json").read_text())["routes"]
        proposals = [row for row in records if row["routing_class"] == "GENERAL_CONTROL"]
        self.assertEqual(2, len(proposals))
        self.assertEqual({"NRF0_TX_LED_A", "S3_TX_LED_A"}, {row["canonical_net"] for row in proposals})
        audit = json.loads((ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json").read_text())
        bindings = {(row["project"], row["kicad_net"]): row for row in audit["rows"]}
        copper.preflight_reviewed_proposals(records, bindings, POLICY)
        self.assertEqual(10, sum(len(row["segments"]) for row in proposals))
        self.assertEqual(2, sum(len(row["vias"]) for row in proposals))
        vias = {row["canonical_net"]: row["vias"][0]["at_mm"] for row in proposals}
        self.assertEqual({"NRF0_TX_LED_A": [40.8, 106.2], "S3_TX_LED_A": [5.8, 106.2]}, vias)


if __name__ == "__main__":
    unittest.main()
