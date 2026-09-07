import json
from pathlib import Path
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
        self.output = self.root / "reports/ui.json"
        self.report = {
            "source": self.project + ".kicad_pcb",
            "kicad_version": "test",
            "violations": [],
            "unconnected_items": [{"type": "unconnected_items"}],
        }

    def successful_run(self, command, **_kwargs):
        Path(command[command.index("-o") + 1]).write_text(json.dumps(self.report), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "DRC finished")

    def capture(self, runner=None):
        with patch.object(drc.subprocess, "run", side_effect=runner or self.successful_run):
            return drc.run_drc(self.project, self.output, root=self.root, cli=Path("/test/kicad-cli"))

    def test_success_captures_exact_board_rules_report_and_utc(self):
        self.assertEqual(self.report, self.capture())
        receipt = drc.validate_provenance(self.output, self.project, self.root)
        self.assertEqual(3, len(receipt["inputs_sha256"]))
        self.assertEqual(drc.sha256(self.output), receipt["report_sha256"])
        self.assertTrue(receipt["started_at_utc"].endswith("+00:00"))
        self.assertTrue(receipt["completed_at_utc"].endswith("+00:00"))
        # Expected unconnected items must not prevent recording an unfinished board.
        self.assertEqual(0, receipt["exit_code"])

    def test_findings_are_preserved_for_the_importer_to_reject(self):
        self.report["violations"] = [{"type": "clearance"}]
        self.assertEqual(self.report, self.capture())
        self.assertEqual(1, len(json.loads(self.output.read_text())["violations"]))

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

    def test_changed_report_invalidates_receipt(self):
        self.capture()
        self.output.write_text(json.dumps({**self.report, "violations": [{"type": "clearance"}]}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "report differs"):
            drc.validate_provenance(self.output, self.project, self.root)

    def test_wrong_project_schema_or_failed_exit_is_rejected(self):
        self.capture()
        path = drc.provenance_path(self.output)
        original = json.loads(path.read_text())
        for field, value in (("project", "LESHY2-RF-R2"), ("schema_version", 2), ("exit_code", 1)):
            with self.subTest(field=field):
                path.write_text(json.dumps({**original, field: value}), encoding="utf-8")
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

    def test_report_cannot_overwrite_board_input(self):
        self.output = self.directory / (self.project + ".kicad_pcb")
        with self.assertRaisesRegex(ValueError, "must not overwrite"):
            self.capture()


if __name__ == "__main__":
    unittest.main()
