"""Unit-level fail-closed checks; no native ERC or production-file mutation."""

import copy
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from hardware.verification import h6_r2_electrical_semantics as semantics


def review(device="reviewed", mpn="Exact-123"):
    return {
        "device_id": device,
        "mpn": mpn,
        "evidence": [{
            "url": "https://www.ti.com/lit/ds/exact.pdf",
            "section": "Pin functions",
            "checked": "2026-09-07",
        }],
        "pins": {
            "1": {"type": "input", "reason": "Data input"},
            "2": {"type": "output", "reason": "Data output"},
        },
        "unresolved": [],
    }


def fragment(*rows):
    return {"schema_version": 1, "devices": list(rows)}


def one_pin_review():
    row = review()
    del row["pins"]["2"]
    return {"reviewed": row}


GROUPS = [{
    "device_id": "reviewed", "mpn": "Exact-123",
    "pad_inventory": {"1": {}, "2": {}, "3": {}},
}]


class ReviewedMapTests(unittest.TestCase):
    def test_partial_review_is_allowed_without_claiming_unreviewed_pad(self):
        result = semantics.reviewed_maps([fragment(review())], GROUPS)
        self.assertEqual({"reviewed"}, set(result))
        self.assertEqual({"1", "2"}, set(result["reviewed"]["pins"]))
        self.assertNotIn("3", result["reviewed"]["pins"])

    def test_missing_or_incomplete_evidence_is_rejected(self):
        for evidence in (None, [], [{}], [{"url": "https://www.ti.com"}],
                         [{"url": "x", "section": "pins", "checked": ""}]):
            with self.subTest(evidence=evidence):
                row = review()
                if evidence is None:
                    del row["evidence"]
                else:
                    row["evidence"] = evidence
                with self.assertRaisesRegex(ValueError, "evidence"):
                    semantics.reviewed_maps([fragment(row)], GROUPS)

    def test_wrong_mpn_is_rejected_not_normalized(self):
        for mpn in ("Exact-123-A", "exact-123", "Exact-123 "):
            with self.subTest(mpn=mpn):
                with self.assertRaisesRegex(ValueError, "MPN mismatch"):
                    semantics.reviewed_maps([fragment(review(mpn=mpn))], GROUPS)

    def test_unknown_device_or_pad_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown or duplicate"):
            semantics.reviewed_maps([fragment(review(device="other"))], GROUPS)
        row = review()
        row["pins"]["99"] = {"type": "passive", "reason": "Not a real pad"}
        with self.assertRaisesRegex(ValueError, "pad/type/reason"):
            semantics.reviewed_maps([fragment(row)], GROUPS)

    def test_duplicate_device_within_or_across_fragments_is_rejected(self):
        for fragments in ([fragment(review(), review())],
                          [fragment(review()), fragment(review())]):
            with self.subTest(fragment_count=len(fragments)):
                with self.assertRaisesRegex(ValueError, "duplicate"):
                    semantics.reviewed_maps(fragments, GROUPS)

    def test_invalid_schema_type_or_reason_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "schema"):
            semantics.reviewed_maps([{"schema_version": 2, "devices": []}], GROUPS)
        for spec in ({"type": "power", "reason": "Broad H2 role is insufficient"},
                     {"type": "input"}, {"type": "input", "reason": ""}):
            with self.subTest(spec=spec):
                row = review()
                row["pins"]["1"] = spec
                with self.assertRaisesRegex(ValueError, "pad/type/reason"):
                    semantics.reviewed_maps([fragment(row)], GROUPS)


class CachedPinTypeTests(unittest.TestCase):
    def test_only_reviewed_cache_type_tokens_change(self):
        source = r'''(kicad_sch
  (lib_symbols
    (symbol "Leshy2_R2:reviewed"
      (property "Value" "Exact-123 (quoted) \"value\"")
      (symbol "reviewed_1_1"
        (pin passive line (at 1.25 -2.5 180)
          (name "input \"quoted\" (name)") (number "1"))
        (pin passive line (at 3 4 0) (name "Y") (number "2"))
        (pin passive line (at 5 6 90) (name "unreviewed") (number "3"))))
    (symbol "Leshy2_R2:other"
      (pin passive line (at 0 0 0) (name "other") (number "1"))))
  (wire (pts (xy 1.25 -2.5) (xy 3 4)) (uuid "wire-uuid"))
  (symbol (lib_id "Leshy2_R2:reviewed") (at 12.5 30 0)
    (uuid "instance-uuid") (pin "1" (uuid "physical-pin-uuid"))))'''
        expected = source.replace("(pin passive line (at 1.25", "(pin input line (at 1.25")
        expected = expected.replace("(pin passive line (at 3 4", "(pin output line (at 3 4")
        result, reviewed_count = semantics.apply_reviewed_types(source, {"reviewed": review()})
        self.assertEqual(2, reviewed_count)
        self.assertEqual(expected, result)
        self.assertEqual((result, 2), semantics.apply_reviewed_types(result, {"reviewed": review()}))

    def test_pin_like_text_inside_a_quoted_property_is_not_a_pin(self):
        source = '''(kicad_sch (lib_symbols (symbol "Leshy2_R2:reviewed"
          (property "Note" "Keep (pin passive line) literal text")
          (pin passive line (name "A") (number "1")))))'''
        expected = source.replace('(pin passive line (name "A")', '(pin input line (name "A")')
        self.assertEqual((expected, 1), semantics.apply_reviewed_types(source, one_pin_review()))

    def test_all_legal_pin_shapes_get_the_reviewed_type(self):
        # Independent KiCad Symbol Pin style list, not copied from the parser at runtime.
        shapes = ("line", "inverted", "clock", "inverted_clock", "input_low",
                  "clock_low", "output_low", "edge_clock_high", "non_logic")
        for shape in shapes:
            with self.subTest(shape=shape):
                source = f'(symbol "Leshy2_R2:reviewed" (pin passive {shape} (number "1")))'
                self.assertEqual((source.replace("pin passive", "pin input"), 1),
                                 semantics.apply_reviewed_types(source, one_pin_review()))

    def test_missing_reviewed_pad_cannot_be_counted_as_reviewed(self):
        source = '(symbol "Leshy2_R2:reviewed" (pin passive line (number "2")))'
        with self.assertRaisesRegex(ValueError, "reviewed pads absent"):
            semantics.apply_reviewed_types(source, one_pin_review())

    def test_required_instance_cannot_fall_back_to_an_untyped_external_library(self):
        with self.assertRaisesRegex(ValueError, "required reviewed symbol cache"):
            semantics.apply_reviewed_types('(kicad_sch (lib_symbols))', one_pin_review(), required_devices={"reviewed"})

    def test_unknown_style_malformed_header_and_duplicate_pads_fail_closed(self):
        for pins in ('(pin passive made_up (number "1"))', '(pin passive (number "1"))',
                     '(pin passive line (number "1")) (pin passive line (number "1"))'):
            with self.subTest(pins=pins):
                with self.assertRaises(ValueError):
                    semantics.apply_reviewed_types(f'(symbol "Leshy2_R2:reviewed" {pins})', one_pin_review())

    def test_duplicate_reviewed_cache_is_not_double_counted(self):
        source = '(symbol "Leshy2_R2:reviewed" (pin passive line (number "1")))'
        with self.assertRaisesRegex(ValueError, "duplicate reviewed symbol cache"):
            semantics.apply_reviewed_types(source + source, one_pin_review())

    def test_unreviewed_cache_is_unchanged(self):
        source = '(kicad_sch (lib_symbols (symbol "Leshy2_R2:other" (pin passive line (number "1")))))'
        self.assertEqual((source, 0), semantics.apply_reviewed_types(source, {"reviewed": review()}))

    def test_missing_pin_number_or_unterminated_expression_is_rejected(self):
        for source in ('(symbol "Leshy2_R2:reviewed" (pin passive line))',
                       '(symbol "Leshy2_R2:reviewed" (pin passive line (number "1"))'):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    semantics.apply_reviewed_types(source, {"reviewed": review()})


class NativeMembershipTests(unittest.TestCase):
    def membership(self, xml):
        # Exercise membership logic without creating a native project or files.
        with patch.object(semantics.ET, "parse", return_value=ET.ElementTree(ET.fromstring(xml))):
            return semantics.net_membership(Path("not-written.xml"))

    def test_membership_preserves_exact_names_without_alias_normalization(self):
        xml = '''<export><nets>
          <net name="3V3_MAIN"><node ref="C6" pin="1"/></net>
          <net name="/old/3V3_MAIN"><node ref="U1" pin="2"/></net>
        </nets></export>'''
        self.assertEqual({("C6", "1"): "3V3_MAIN", ("U1", "2"): "/old/3V3_MAIN"}, self.membership(xml))

    def test_duplicate_node_in_same_or_different_net_is_rejected(self):
        for xml in (
            '<export><nets><net name="a"><node ref="U1" pin="1"/><node ref="U1" pin="1"/></net></nets></export>',
            '<export><nets><net name="a"><node ref="U1" pin="1"/></net><net name="b"><node ref="U1" pin="1"/></net></nets></export>',
        ):
            with self.subTest(xml=xml):
                with self.assertRaisesRegex(ValueError, "duplicate"):
                    self.membership(xml)

    def test_missing_nets_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no nets"):
            self.membership("<export/>")


class DirectNetFindingTests(unittest.TestCase):
    def findings(self, types):
        instances, reviews, nodes = [], {}, {}
        for index, pin_type in enumerate(types, 1):
            ref, device = f"U{index}", f"device{index}"
            instances.append({"reference": ref, "instance": device, "device_id": device})
            nodes[(ref, "1")] = "TEST_NET"
            reviews[device] = {"pins": {"1": {"type": pin_type, "reason": "test function"}}}
        return semantics.direct_net_findings(nodes, instances, reviews)

    def test_push_pull_output_conflict_is_reported_with_exact_participants(self):
        findings = self.findings(["output", "output", "input"])
        self.assertEqual(1, len(findings))
        self.assertEqual("multiple_push_pull_outputs", findings[0]["kind"])
        self.assertEqual("requires_review", findings[0]["status"])
        self.assertEqual({"U1", "U2"}, {pin["reference"] for pin in findings[0]["pins"]})

    def test_open_drain_and_tristate_are_not_falsely_called_multiple_push_pull(self):
        for types in (["open_collector", "open_collector", "input"],
                      ["output", "open_collector"], ["tri_state", "tri_state"]):
            with self.subTest(types=types):
                self.assertEqual([], self.findings(types))

    def test_absent_direct_power_source_is_scoped_warning_not_power_failure(self):
        findings = self.findings(["power_in", "passive", "output"])
        self.assertEqual(1, len(findings))
        self.assertEqual("no_direct_reviewed_power_output", findings[0]["kind"])
        self.assertEqual("requires_source_path_review", findings[0]["status"])
        self.assertEqual(["U1"], [pin["reference"] for pin in findings[0]["pins"]])

    def test_direct_power_output_satisfies_direct_source_screen(self):
        self.assertEqual([], self.findings(["power_in", "power_out"]))

    def test_unknown_native_reference_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "absent from instance ledger"):
            semantics.direct_net_findings({("U404", "1"): "net"}, [], {})

    def test_unreviewed_pins_are_not_counted_as_verified_sources_or_inputs(self):
        instances = [{"reference": "U1", "instance": "unknown", "device_id": "unknown"}]
        self.assertEqual([], semantics.direct_net_findings({("U1", "1"): "net"}, instances, {}))


class SavedAuditTests(unittest.TestCase):
    def setUp(self):
        self.reviews = {"reviewed": review()}
        self.hashes = {"source": "a" * 64}
        self.counts = {project: 2 for project in semantics.PROJECTS}
        self.sheets = {project: ["/", "/leaf/"] for project in semantics.PROJECTS}
        projects = []
        for project in semantics.PROJECTS:
            report = {
                "$schema": "https://schemas.kicad.org/erc.v1.json",
                "source": f"{project}.kicad_sch", "date": "2026-09-07T13:00:00",
                "coordinate_units": "mm", "kicad_version": "10.0.5",
                "included_severities": ["error", "warning", "exclusion"],
                "sheets": [{"path": path, "uuid_path": f"/fixture{index}", "violations": []}
                           for index, path in enumerate(self.sheets[project])],
            }
            report["sheets"][1]["violations"] = [{
                "type": "power_pin_not_driven", "severity": "error",
                "description": "Unresolved direct-source evidence", "items": [],
            }]
            projects.append({
                "project": project, "cached_pin_types_reviewed": 2,
                "native_connectivity_unchanged": True, "physical_netlist_nodes": 3,
                "native_xml_sha256": "b" * 64, "typed_xml_sha256": "c" * 64,
                "erc_report_sha256": "d" * 64, "erc_content_sha256": semantics.content_digest(report),
                "native_erc": report, "erc_count_by_type": {"power_pin_not_driven": 1},
                "direct_net_findings": [],
            })
        self.audit = {
            "schema_version": 1, "marker": "H6.0.3-R1", "gate": "H6-NATIVE-ELECTRICAL-SEMANTICS",
            "status": "review_required", "source_hashes": self.hashes,
            "coverage": semantics.review_coverage(GROUPS, self.reviews),
            "authorization": {"fabrication": False, "gate_closed": False},
            "source_review_findings": [], "projects": projects,
        }

    def validate(self, audit):
        return semantics.validate_audit(audit, GROUPS, self.reviews, self.hashes, self.counts, self.sheets)

    def test_complete_partial_evidence_retains_errors_without_claiming_pass(self):
        self.assertIsNone(self.validate(self.audit))

    def test_stale_status_fabrication_or_fabricated_coverage_is_rejected(self):
        changes = (
            ("source_hashes", {}), ("status", "pass"), ("marker", "complete"),
            ("authorization", {"fabrication": True, "gate_closed": False}),
            ("coverage", {"reviewed_devices": 999999}),
            ("source_review_findings", [{"finding": "invented"}]),
        )
        for key, value in changes:
            with self.subTest(key=key):
                audit = copy.deepcopy(self.audit)
                audit[key] = value
                with self.assertRaises(ValueError):
                    self.validate(audit)

    def test_missing_duplicate_or_unknown_projects_are_rejected(self):
        for projects in ([], self.audit["projects"][:1], [self.audit["projects"][0]] * 2):
            with self.subTest(project_count=len(projects)):
                audit = copy.deepcopy(self.audit)
                audit["projects"] = copy.deepcopy(projects)
                with self.assertRaisesRegex(ValueError, "both distinct"):
                    self.validate(audit)

    def test_missing_or_invented_application_and_native_evidence_is_rejected(self):
        for key, value in (("cached_pin_types_reviewed", 0), ("cached_pin_types_reviewed", 9999),
                           ("native_connectivity_unchanged", False), ("native_connectivity_unchanged", "true"),
                           ("physical_netlist_nodes", 0), ("physical_netlist_nodes", True),
                           ("native_xml_sha256", ""), ("erc_report_sha256", "made-up"),
                           ("native_erc", {}), ("direct_net_findings", None)):
            with self.subTest(key=key, value=value):
                audit = copy.deepcopy(self.audit)
                audit["projects"][0][key] = value
                with self.assertRaises(ValueError):
                    self.validate(audit)

    def test_wrong_native_source_severity_and_sheet_coverage_are_rejected(self):
        for key, value in (("source", "another.kicad_sch"), ("included_severities", ["warning"]),
                           ("sheets", []), ("sheets", self.audit["projects"][0]["native_erc"]["sheets"][:1])):
            with self.subTest(key=key):
                audit = copy.deepcopy(self.audit)
                project = audit["projects"][0]
                project["native_erc"][key] = copy.deepcopy(value)
                project["erc_content_sha256"] = semantics.content_digest(project["native_erc"])
                with self.assertRaises(ValueError):
                    self.validate(audit)

    def test_removed_or_recounted_native_violations_are_rejected(self):
        audit = copy.deepcopy(self.audit)
        audit["projects"][0]["native_erc"]["sheets"][1]["violations"] = []
        with self.assertRaisesRegex(ValueError, "content changed"):
            self.validate(audit)
        project = audit["projects"][0]
        project["erc_content_sha256"] = semantics.content_digest(project["native_erc"])
        with self.assertRaisesRegex(ValueError, "count does not match"):
            self.validate(audit)

    def test_map_unresolved_findings_cannot_disappear(self):
        self.reviews["reviewed"]["unresolved"] = ["Configuration still needs review"]
        with self.assertRaisesRegex(ValueError, "source findings"):
            self.validate(self.audit)


if __name__ == "__main__":
    unittest.main()
