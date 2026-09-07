import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from hardware.layout import h6_r2_drc as drc


class H6R2DrcProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = "LESHY2-UI-R2"
        self.directory = self.root / "hardware/ecad/kicad" / self.project
        self.directory.mkdir(parents=True)
        for suffix in (".kicad_pcb", ".kicad_pro", ".kicad_dru"):
            (self.directory / (self.project + suffix)).write_text(suffix, encoding="utf-8")
        self.schematic = self.directory / (self.project + ".kicad_sch")
        self.schematic.write_text('(kicad_sch (sheet (property "Sheetfile" "sub/CHILD.kicad_sch")))')
        (self.directory / "sub").mkdir()
        self.child = self.directory / "sub/CHILD.kicad_sch"
        self.child.write_text('(kicad_sch (sheet (property "Sheetfile" "DEEP.kicad_sch")))')
        self.grandchild = self.directory / "sub/DEEP.kicad_sch"
        self.grandchild.write_text('(kicad_sch)')
        for name in ("fp-lib-table", "sym-lib-table"):
            (self.directory / name).write_text(name)
        self.library = self.root / "hardware/ecad/libraries"
        self.footprints = []
        for name in ("Leshy2", "Leshy2_R2"):
            folder = self.library / (name + ".pretty")
            folder.mkdir(parents=True)
            path = folder / "TEST.kicad_mod"
            path.write_text('(footprint "TEST")')
            self.footprints.append(path)
        self.symbols = self.library / "leshy2_r2.kicad_sym"
        self.symbols.write_text('(kicad_symbol_lib)')
        self.output = self.root / "reports/ui.json"
        self.report = {
            "source": self.project + ".kicad_pcb",
            "kicad_version": "test",
            "violations": [],
            "unconnected_items": [{"type": "unconnected_items"}],
            "schematic_parity": [],
        }

    def successful_run(self, command, **kwargs):
        (Path(kwargs["cwd"]) / command[command.index("-o") + 1]).write_text(json.dumps(self.report), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "DRC finished")

    def capture(self, runner=None):
        with patch.object(drc.subprocess, "run", side_effect=runner or self.successful_run):
            return drc.run_drc(self.project, self.output, root=self.root, cli=Path("/test/kicad-cli"))

    def test_success_captures_board_rules_schematics_libraries_report_and_utc(self):
        self.assertEqual(self.report, self.capture())
        receipt = drc.validate_provenance(self.output, self.project, self.root)
        self.assertEqual(11, len(receipt["inputs_sha256"]))
        self.assertEqual(2, receipt["schema_version"])
        self.assertIs(True, receipt["schematic_parity_requested"])
        self.assertEqual(["pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "-o"], receipt["command"][1:-2])
        self.assertEqual("repository_root", receipt["command_working_directory"])
        self.assertEqual("reports/ui.json", receipt["published_report_path"])
        self.assertEqual(f"hardware/ecad/kicad/{self.project}/{self.project}.kicad_pcb", receipt["command"][-1])
        self.assertFalse(Path(receipt["command"][-2]).is_absolute())
        self.assertNotIn(str(self.root), json.dumps(receipt))
        self.assertEqual({"violations": 0, "unconnected_items": 1, "schematic_parity": 0}, receipt["report_list_counts"])
        self.assertIn("not content-hashed", receipt["external_environment"]["standard_libraries"])
        self.assertIn("kicad_version", receipt["external_environment"]["cli"])
        self.assertEqual(drc.sha256(self.output), receipt["report_sha256"])
        self.assertTrue(receipt["started_at_utc"].endswith("+00:00"))
        self.assertTrue(receipt["completed_at_utc"].endswith("+00:00"))
        # Expected unconnected items must not prevent recording an unfinished board.
        self.assertEqual(0, receipt["exit_code"])

    def test_command_is_executed_relative_not_redacted_afterward(self):
        executed = []

        def runner(command, **kwargs):
            self.assertEqual(self.root.resolve(), kwargs["cwd"])
            self.assertFalse(Path(command[-1]).is_absolute())
            self.assertFalse(Path(command[-2]).is_absolute())
            executed.append(list(command))
            return self.successful_run(command, **kwargs)

        self.capture(runner)
        receipt = drc.validate_provenance(self.output, self.project, self.root)
        self.assertEqual(executed, [receipt["command"]])
        self.assertEqual(drc.sha256(self.output), receipt["report_sha256"])

    def test_report_and_embedded_current_routing_receipt_survive_repository_relocation(self):
        self.capture()
        report_bytes = self.output.read_bytes()
        receipt_bytes = drc.provenance_path(self.output).read_bytes()
        receipt = json.loads(receipt_bytes)
        with tempfile.TemporaryDirectory() as directory:
            relocated = Path(directory) / "checkout"
            shutil.copytree(self.root, relocated)
            report = relocated / "reports/ui.json"
            self.assertEqual(receipt, drc.validate_provenance(report, self.project, relocated))
            # Current-routing stores the same receipt and raw report SHA inline;
            # checking it must not require the original machine's checkout path.
            embedded = {"report_sha256": drc.sha256(report), "provenance": receipt}
            drc.validate_receipt(embedded["provenance"], self.project, embedded["report_sha256"], relocated)
            self.assertEqual(report_bytes, report.read_bytes())
            self.assertEqual(receipt_bytes, drc.provenance_path(report).read_bytes())
            (relocated / self.child.relative_to(self.root)).write_text("changed schematic")
            with self.assertRaisesRegex(ValueError, "changed since"):
                drc.validate_receipt(embedded["provenance"], self.project, embedded["report_sha256"], relocated)

    def test_absolute_traversing_or_wrong_command_paths_are_rejected(self):
        self.capture()
        receipt = drc.validate_provenance(self.output, self.project, self.root)
        variants = []
        for index in (-2, -1):
            for value in (str(self.root / receipt["command"][index]), "../" + receipt["command"][index],
                          "./" + receipt["command"][index], "wrong/OTHER.kicad_pcb"):
                command = list(receipt["command"])
                command[index] = value
                variants.append({"command": command})
        for value in (str(self.output), "../reports/ui.json", "reports/../reports/ui.json", "reports//ui.json", "other/ui.json"):
            variants.append({"published_report_path": value})
        variants.extend(({"command_working_directory": str(self.root)}, {"command_working_directory": None}))
        for change in variants:
            with self.subTest(change=change), self.assertRaises(ValueError):
                drc.validate_receipt({**receipt, **change}, self.project, drc.sha256(self.output), self.root)

    def test_copied_report_at_an_unrecorded_location_is_rejected(self):
        self.capture()
        other = self.output.with_name("other.json")
        shutil.copyfile(self.output, other)
        shutil.copyfile(drc.provenance_path(self.output), drc.provenance_path(other))
        with self.assertRaisesRegex(ValueError, "different published report"):
            drc.validate_provenance(other, self.project, self.root)

    def test_external_output_and_symlink_escape_are_rejected_before_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory)
            link = self.root / "outside"
            link.symlink_to(outside, target_is_directory=True)
            for output in (outside / "drc.json", link / "drc.json"):
                with self.subTest(output=output), patch.object(drc.subprocess, "run") as runner:
                    with self.assertRaisesRegex(ValueError, "inside the repository"):
                        drc.run_drc(self.project, output, root=self.root, cli=Path("/test/kicad-cli"))
                    runner.assert_not_called()
            self.assertEqual([], list(outside.iterdir()))

    def test_findings_are_preserved_for_the_importer_to_reject(self):
        self.report["violations"] = [{"type": "clearance"}]
        self.report["schematic_parity"] = [{"type": "net_conflict"}]
        self.assertEqual(self.report, self.capture())
        self.assertEqual(1, len(json.loads(self.output.read_text())["violations"]))
        receipt = drc.validate_provenance(self.output, self.project, self.root)
        self.assertEqual(1, receipt["report_list_counts"]["schematic_parity"])

    def test_report_without_receipt_is_rejected(self):
        self.output.parent.mkdir()
        self.output.write_text(json.dumps(self.report), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing DRC provenance"):
            drc.validate_provenance(self.output, self.project, self.root)

    def test_changed_board_project_or_rules_invalidates_receipt(self):
        for suffix in (".kicad_pcb", ".kicad_pro", ".kicad_dru"):
            with self.subTest(suffix=suffix):
                self.capture()
                path = self.directory / (self.project + suffix)
                path.write_text("changed " + suffix, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "changed since"):
                    drc.validate_provenance(self.output, self.project, self.root)

    def test_changed_schematic_child_tables_footprint_or_symbol_invalidates_receipt(self):
        paths = [self.schematic, self.child, self.grandchild,
                 self.directory / "fp-lib-table", self.directory / "sym-lib-table",
                 *self.footprints, self.symbols]
        for path in paths:
            with self.subTest(path=path):
                self.capture()
                path.write_text(path.read_text() + "\n; changed\n")
                with self.assertRaisesRegex(ValueError, "changed since"):
                    drc.validate_provenance(self.output, self.project, self.root)

    def test_added_or_deleted_controlled_library_file_invalidates_receipt(self):
        self.capture()
        added = self.footprints[0].with_name("ADDED.kicad_mod")
        added.write_text('(footprint "ADDED")')
        with self.assertRaisesRegex(ValueError, "changed since"):
            drc.validate_provenance(self.output, self.project, self.root)
        self.capture()
        added.unlink()
        with self.assertRaisesRegex(ValueError, "changed since"):
            drc.validate_provenance(self.output, self.project, self.root)

    def test_child_outside_project_but_in_repo_is_hashed(self):
        shared = self.directory.parent / "SHARED.kicad_sch"
        shared.write_text('(kicad_sch)')
        self.child.write_text('(kicad_sch (sheet (property "Sheetfile" "../../SHARED.kicad_sch")))')
        self.capture()
        receipt = drc.validate_provenance(self.output, self.project, self.root)
        self.assertIn(str(shared.relative_to(self.root)), receipt["inputs_sha256"])
        shared.write_text('(kicad_sch changed)')
        with self.assertRaisesRegex(ValueError, "changed since"):
            drc.validate_provenance(self.output, self.project, self.root)

    def test_missing_referenced_child_fails_before_running(self):
        self.child.unlink()
        with patch.object(drc.subprocess, "run") as runner:
            with self.assertRaises(FileNotFoundError):
                drc.run_drc(self.project, self.output, root=self.root, cli=Path("/test/kicad-cli"))
            runner.assert_not_called()

    def test_child_outside_repository_is_rejected(self):
        self.child.write_text('(kicad_sch (sheet (property "Sheetfile" "/outside/CHILD.kicad_sch")))')
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            self.capture()

    def test_changed_report_invalidates_receipt(self):
        self.capture()
        self.output.write_text(json.dumps({**self.report, "violations": [{"type": "clearance"}]}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "report differs"):
            drc.validate_provenance(self.output, self.project, self.root)

    def test_wrong_project_schema_or_failed_exit_is_rejected(self):
        self.capture()
        path = drc.provenance_path(self.output)
        original = json.loads(path.read_text())
        for field, value in (("project", "LESHY2-RF-R2"), ("schema_version", 1), ("exit_code", 1)):
            with self.subTest(field=field):
                path.write_text(json.dumps({**original, field: value}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    drc.validate_provenance(self.output, self.project, self.root)

    def test_schema_one_never_counts_as_fresh_schematic_parity(self):
        self.capture()
        path = drc.provenance_path(self.output)
        receipt = json.loads(path.read_text())
        receipt["schema_version"] = 1
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "project/schema"):
            drc.validate_provenance(self.output, self.project, self.root)

    def test_parity_flag_command_observation_and_environment_boundary_are_required(self):
        self.capture()
        path = drc.provenance_path(self.output)
        original = json.loads(path.read_text())
        no_parity = [item for item in original["command"] if item != "--schematic-parity"]
        changes = [
            {"schematic_parity_requested": False},
            {"command": no_parity},
            {"command": original["command"][:-1] + ["different.kicad_pcb"]},
            {"command": original["command"] + ["--save-board"]},
            {"required_report_fields": ["violations", "unconnected_items"]},
            {"report_list_counts": {"violations": 0, "unconnected_items": 1}},
            {"report_list_counts": {"violations": 0, "unconnected_items": 1, "schematic_parity": False}},
            {"external_environment": {}},
        ]
        for change in changes:
            with self.subTest(change=change):
                path.write_text(json.dumps({**original, **change}))
                with self.assertRaises(ValueError):
                    drc.validate_provenance(self.output, self.project, self.root)

    def test_failed_cli_keeps_last_report_and_receipt(self):
        self.capture()
        old_report = self.output.read_bytes()
        old_receipt = drc.provenance_path(self.output).read_bytes()
        with self.assertRaisesRegex(ValueError, "KiCad DRC failed"):
            self.capture(lambda command, **kwargs: subprocess.CompletedProcess(command, 1, "failed"))
        self.assertEqual(old_report, self.output.read_bytes())
        self.assertEqual(old_receipt, drc.provenance_path(self.output).read_bytes())

    def test_inputs_changed_during_run_are_not_published(self):
        self.capture()
        old_report = self.output.read_bytes()
        old_receipt = drc.provenance_path(self.output).read_bytes()

        def mutate(command, **kwargs):
            (self.directory / (self.project + ".kicad_pcb")).write_text("changed", encoding="utf-8")
            return self.successful_run(command, **kwargs)

        with self.assertRaisesRegex(ValueError, "changed during"):
            self.capture(mutate)
        self.assertEqual(old_report, self.output.read_bytes())
        self.assertEqual(old_receipt, drc.provenance_path(self.output).read_bytes())

    def test_child_or_library_changed_during_run_is_not_published(self):
        for path in [self.grandchild, self.footprints[1], self.symbols]:
            with self.subTest(path=path):
                self.capture()
                old_report = self.output.read_bytes()
                old_receipt = drc.provenance_path(self.output).read_bytes()

                def mutate(command, **kwargs):
                    path.write_text(path.read_text() + "\n; changed\n")
                    return self.successful_run(command, **kwargs)

                with self.assertRaisesRegex(ValueError, "changed during"):
                    self.capture(mutate)
                self.assertEqual(old_report, self.output.read_bytes())
                self.assertEqual(old_receipt, drc.provenance_path(self.output).read_bytes())

    def test_missing_report_cannot_reuse_old_report(self):
        self.capture()
        with self.assertRaisesRegex(ValueError, "produced no report"):
            self.capture(lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "done"))

    def test_wrong_report_source_and_incomplete_report_are_rejected(self):
        self.report["source"] = "OTHER.kicad_pcb"
        with self.assertRaisesRegex(ValueError, "source does not match"):
            self.capture()
        self.report["source"] = self.project + ".kicad_pcb"
        del self.report["violations"]
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.capture()

    def test_missing_null_or_nonlist_parity_is_not_published(self):
        self.capture()
        old_report = self.output.read_bytes()
        old_receipt = drc.provenance_path(self.output).read_bytes()
        for value in (None, {}, "", 0):
            with self.subTest(value=value):
                self.report["schematic_parity"] = value
                with self.assertRaisesRegex(ValueError, "schematic_parity"):
                    self.capture()
        del self.report["schematic_parity"]
        with self.assertRaisesRegex(ValueError, "schematic_parity"):
            self.capture()
        self.assertEqual(old_report, self.output.read_bytes())
        self.assertEqual(old_receipt, drc.provenance_path(self.output).read_bytes())

    def test_import_rejects_missing_parity_even_with_matching_report_hash(self):
        self.capture()
        del self.report["schematic_parity"]
        self.output.write_text(json.dumps(self.report))
        path = drc.provenance_path(self.output)
        receipt = json.loads(path.read_text())
        receipt["report_sha256"] = drc.sha256(self.output)
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "schematic_parity"):
            drc.validate_provenance(self.output, self.project, self.root)

    def test_receipt_observed_count_must_match_report(self):
        self.capture()
        path = drc.provenance_path(self.output)
        receipt = json.loads(path.read_text())
        receipt["report_list_counts"]["schematic_parity"] = 1
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "observations differ"):
            drc.validate_provenance(self.output, self.project, self.root)

    def test_report_cannot_overwrite_board_input(self):
        self.output = self.directory / (self.project + ".kicad_pcb")
        with self.assertRaisesRegex(ValueError, "must not overwrite"):
            self.capture()


if __name__ == "__main__":
    unittest.main()
