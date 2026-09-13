"""Keep the shared validation entrypoint ordered, serial and native-read-only."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location("h6_validate",ROOT/"hardware/layout/h6_r2_validate.py")
workflow=importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)


class ValidationWorkflowTests(unittest.TestCase):
    def test_refresh_and_check_never_call_native_seed_writes(self):
        for refresh in (False,True):
            steps=workflow.commands(refresh,Path("work/example"),True,python="native-python")
            for command in steps:
                self.assertNotIn("shell",command)
                if command[1] in ("hardware/layout/h6_r2_placement.py","hardware/layout/h6_r2_manual_copper.py"):
                    self.assertNotIn("--write",command)
            scripts=[command[1] for command in steps]
            self.assertLess(scripts.index("hardware/layout/h6_r2_silkscreen_audit.py"),scripts.index("hardware/layout/h6_r2_current_routing.py"))
            if refresh:
                drcs=[i for i,c in enumerate(steps) if c[1]=="hardware/layout/h6_r2_drc.py"]
                self.assertEqual(2,len(drcs))
                self.assertEqual(drcs[0]+1,drcs[1])
                self.assertLess(drcs[-1],scripts.index("hardware/layout/h6_r2_current_routing.py"))
            else:
                self.assertFalse(any("--write" in c or "--refresh-derived" in c for c in steps))

    def test_changed_native_board_stops_even_if_subprocess_succeeds(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(workflow,"board_hashes",return_value={"RF":"new"}), patch.object(workflow.subprocess,"run") as run:
            run.return_value.returncode=0
            with self.assertRaisesRegex(RuntimeError,"changed a native PCB"):
                workflow.run_one(["fake","check.py"],Path(directory)/"log",{"RF":"old"})

    def test_failed_subprocess_stops_without_rollback(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(workflow,"board_hashes",return_value={"RF":"old"}), patch.object(workflow.subprocess,"run") as run:
            run.return_value.returncode=2
            with self.assertRaisesRegex(RuntimeError,"Command failed"):
                workflow.run_one(["fake","check.py"],Path(directory)/"log",{"RF":"old"})


if __name__=="__main__":unittest.main()
