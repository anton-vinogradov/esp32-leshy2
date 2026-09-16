"""Exact source-to-PCB membership; no routing, DRC or production writes."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid5, NAMESPACE_URL

from hardware.layout import h6_r2_component_inventory as audit
from hardware.layout.h6_r2_route_candidate import forms


def fixture():
    expected = []
    for project in audit.PROJECTS:
        for ref, excluded, dnp in (("R1", False, False), ("TP1", True, False),
                                   ("R2", False, True)):
            identity = f"{project}:{ref}"
            expected.append({"project": project, "reference": ref,
                             "footprint": "Library:" + ref, "value": "MPN:" + identity,
                             "device_id": "device:" + ref, "instance": "instance:" + ref,
                             "schematic_path": "/" + str(uuid5(NAMESPACE_URL, identity)),
                             "board_only": False, "bom_excluded": excluded,
                             "position_excluded": excluded, "dnp": dnp})
        expected.append({"project": project, "reference": "MH1",
                         "footprint": "MountingHole:MountingHole_2.7mm_M2.5",
                         "value": "M2.5 compression-stop axis", "device_id": "",
                         "instance": "", "schematic_path": "", "board_only": True,
                         "bom_excluded": True, "position_excluded": True, "dnp": False})
    observed = [dict(row, uuid=str(uuid5(NAMESPACE_URL, "native:" + row["project"]
                                        + ":" + row["reference"]))) for row in expected]
    return expected, observed


def finding_types(report):
    return {row["type"] for row in report["findings"]}


class ComponentInventoryTests(unittest.TestCase):
    def test_exact_match_same_ref_on_different_boards_and_serializable(self):
        expected, observed = fixture()
        before = deepcopy((expected, observed))
        result = audit.compare_inventory(expected, observed)
        self.assertEqual("pass", result["status"])
        self.assertEqual(result, json.loads(json.dumps(result)))
        self.assertEqual(before, (expected, observed))

    def test_missing_dnp_bom_excluded_and_mechanical_are_all_failures(self):
        for index in (0, 1, 2, 3):
            expected, observed = fixture()
            removed = observed.pop(index)
            with self.subTest(reference=removed["reference"]):
                result = audit.compare_inventory(expected, observed)
                self.assertEqual({"missing_component"}, finding_types(result))
                self.assertEqual(removed["reference"], result["findings"][0]["reference"])

    def test_duplicates_are_not_collapsed_even_with_fresh_uuid(self):
        expected, observed = fixture()
        observed.append(dict(observed[0], uuid=str(uuid5(NAMESPACE_URL, "duplicate"))))
        self.assertIn("duplicate_reference", finding_types(audit.compare_inventory(expected, observed)))

    def test_extra_mechanical_and_unknown_project_have_no_blanket_exemption(self):
        for change in ({"reference": "MH99"}, {"project": "OTHER-PCB"}):
            expected, observed = fixture()
            observed.append(dict(observed[3], uuid=str(uuid5(NAMESPACE_URL, "extra")), **change))
            self.assertIn("unexpected_component", finding_types(audit.compare_inventory(expected, observed)))

    def test_wrong_board_detected_even_with_same_reference_and_same_board_counts(self):
        expected, observed = fixture()
        observed[0]["project"], observed[4]["project"] = observed[4]["project"], observed[0]["project"]
        result = audit.compare_inventory(expected, observed)
        self.assertIn("component_identity_mismatch", finding_types(result))
        self.assertTrue(all(row["expected"] == row["observed"] for row in result["boards"]))

    def test_same_count_swap_and_same_count_delete_duplicate_fail(self):
        expected, observed = fixture()
        observed[0]["reference"], observed[2]["reference"] = observed[2]["reference"], observed[0]["reference"]
        self.assertIn("component_identity_mismatch", finding_types(audit.compare_inventory(expected, observed)))
        expected, observed = fixture()
        observed[2] = deepcopy(observed[0])
        result = audit.compare_inventory(expected, observed)
        self.assertTrue({"missing_component", "duplicate_reference"}.issubset(finding_types(result)))
        self.assertEqual(result["summary"]["native_footprints"], result["summary"]["expected_footprints"])

    def test_every_source_identity_and_assembly_field_is_checked(self):
        for field in audit.FIELDS:
            expected, observed = fixture()
            observed[0][field] = not observed[0][field] if field in audit.BOOLEAN_FIELDS else "changed"
            with self.subTest(field=field):
                result = audit.compare_inventory(expected, observed)
                self.assertIn("component_identity_mismatch", finding_types(result))

    def test_invalid_duplicate_native_and_schematic_uuids_fail(self):
        for uid in (None, "invalid", "00000000-0000-0000-0000-000000000000"):
            expected, observed = fixture()
            observed[0]["uuid"] = uid
            self.assertIn("invalid_native_uuid", finding_types(audit.compare_inventory(expected, observed)))
        expected, observed = fixture()
        observed[1]["uuid"] = observed[0]["uuid"]
        observed[1]["schematic_path"] = observed[0]["schematic_path"]
        self.assertTrue({"duplicate_native_uuid", "duplicate_schematic_identity"}.issubset(
            finding_types(audit.compare_inventory(expected, observed))))

    def test_empty_malformed_or_duplicated_authority_fails_closed(self):
        expected, observed = fixture()
        for source in ([], None, [{}], expected + [expected[0]], expected[:4]):
            with self.subTest(source=type(source).__name__):
                with self.assertRaises(ValueError):
                    audit.compare_inventory(source, observed)
        for field, value in (("dnp", 0), ("footprint", None), ("schematic_path", [])):
            expected, observed = fixture()
            observed[0][field] = value
            with self.assertRaises(ValueError):
                audit.compare_inventory(expected, observed)

    def test_actual_independent_authority_counts_and_explicit_exemptions(self):
        expected, sources, exemptions = audit.expected_inventory()
        self.assertEqual(1218, len(expected))
        self.assertEqual(1210, sum(bool(r["schematic_path"]) for r in expected))
        self.assertEqual({"LESHY2-UI-R2": 434, "LESHY2-RF-R2": 784},
                         {p: sum(r["project"] == p for r in expected) for p in audit.PROJECTS})
        loop = next(r for r in expected if r["device_id"] == "leshy2_nfc_pickup_loop_r2")
        self.assertTrue(loop["board_only"] and loop["bom_excluded"] and loop["schematic_path"])
        self.assertEqual(6, len(exemptions))
        self.assertEqual(10, sum(r["quantity"] for r in exemptions))
        self.assertFalse(any(name.endswith(".kicad_pcb") for name in sources))

    def test_stale_and_invalid_source_ledgers_rejected(self):
        for data in ({"status": "fail", "errors": ["fault"]},
                     {"status": "pass", "errors": [], "stale": True}):
            with patch.object(audit.inventory, "build", return_value=data):
                with self.assertRaises(ValueError):
                    audit.expected_inventory()

    def test_changed_source_or_board_during_inspection_is_rejected(self):
        expected, observed = fixture()
        for sources, board_hashes in (({"source.json": "a" * 64}, {}),
                                     ({}, {audit.PROJECTS[0]: "a" * 64})):
            with patch.object(audit, "expected_inventory", return_value=(expected, sources, [])), \
                 patch.object(audit, "native_inventory", return_value=(observed, board_hashes)), \
                 patch.object(audit, "sha", return_value="b" * 64):
                with self.assertRaises(ValueError):
                    audit.build({p: Path("copy.kicad_pcb") for p in audit.PROJECTS})

    def test_native_current_and_copy_only_fault_injection(self):
        try:
            import pcbnew
        except ImportError:
            self.skipTest("KiCad Python needed for native read-only/copy-only checks")
        paths = {p: audit.ROOT / f"hardware/ecad/kicad/{p}/{p}.kicad_pcb" for p in audit.PROJECTS}
        hashes = {p: audit.sha(path) for p, path in paths.items()}
        result = audit.build(paths)
        self.assertEqual("pass", result["status"], result["findings"])
        self.assertEqual(1218, result["summary"]["native_footprints"])
        self.assertTrue(result["read_only"])
        self.assertFalse(result["drc_checked"] or result["dnp_footprint_omission_allowed"])
        # At least one real footprint has duplicate pad numbers. These are
        # legitimate physical pads and are not duplicate component instances.
        rf = pcbnew.LoadBoard(str(paths[audit.PROJECTS[1]]))
        self.assertTrue(any(len([p.GetNumber() for p in f.Pads()]) !=
                            len({p.GetNumber() for p in f.Pads()}) for f in rf.GetFootprints()))
        expected, _, _ = audit.expected_inventory()
        with tempfile.TemporaryDirectory() as directory:
            # KiCad SWIG footprint proxies must never outlive their board.
            owners = []
            for mutation, finding in (("missing", "missing_component"),
                                      ("duplicate", "duplicate_reference"),
                                      ("same_count_swap", "component_identity_mismatch")):
                copy_path = Path(directory) / (mutation + ".kicad_pcb")
                board = pcbnew.LoadBoard(str(paths[audit.PROJECTS[0]]))
                owners.append(board)
                by_ref = {fp.GetReference(): fp for fp in board.GetFootprints()}
                if mutation == "missing":
                    # The native SWIG Remove() ownership transfer can poison
                    # later loads in the same process. Remove one exact form
                    # from a disposable copy, then inspect it with pcbnew.
                    source = paths[audit.PROJECTS[0]].read_text()
                    block = next(block for kind, block in forms(source)
                                 if kind == "footprint" and '(property "Reference" "R1"' in block)
                    copy_path.write_text(source.replace(block, "", 1))
                elif mutation == "duplicate":
                    by_ref["C1"].SetReference("R1")
                else:
                    by_ref["R1"].SetReference("C1")
                    by_ref["C1"].SetReference("R1")
                if mutation != "missing":
                    pcbnew.SaveBoard(str(copy_path), board)
                observed, _ = audit.native_inventory(dict(paths, **{audit.PROJECTS[0]: copy_path}))
                with self.subTest(mutation=mutation):
                    self.assertIn(finding, finding_types(audit.compare_inventory(expected, observed)))
            wrong_boards = dict(zip(audit.PROJECTS, reversed(list(paths.values()))))
            observed, _ = audit.native_inventory(wrong_boards)
            self.assertEqual("fail", audit.compare_inventory(expected, observed)["status"])
        self.assertEqual(hashes, {p: audit.sha(path) for p, path in paths.items()})


if __name__ == "__main__":
    unittest.main()
