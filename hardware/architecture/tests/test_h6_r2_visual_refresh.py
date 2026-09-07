"""The public visual refresh must update/check both views without writing PCBs."""

import contextlib
import importlib.util
import io
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, patch


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/layout/h6_r2_routing_render.py"


class VisualRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("h6_visual_refresh_under_test", SCRIPT)
        cls.renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.renderer)

    def result(self, code=0, output=""):
        return SimpleNamespace(returncode=code, stdout=output)

    def main(self, flag):
        with patch.object(self.renderer.sys, "argv", [str(SCRIPT), flag]), contextlib.redirect_stdout(io.StringIO()) as output:
            code = self.renderer.main()
        return code, output.getvalue()

    def test_existing_current_pcbnew_runtime_is_preferred(self):
        r = self.renderer
        with patch.object(r.sys, "executable", "/runtime/current"), \
                patch.object(Path, "is_file", return_value=True), \
                patch.object(r.subprocess, "run", return_value=self.result()) as run:
            self.assertEqual("/runtime/current", r.component_python())
        self.assertEqual(1, run.call_count)
        self.assertEqual(["/runtime/current", "-c", "import pcbnew; assert hasattr(pcbnew, 'LoadBoard')"],
                         run.call_args.args[0])

    def test_system_python_without_pcbnew_dispatches_to_bundled_runtime(self):
        r = self.renderer
        bundled = str(r.KICAD_PYTHON_CANDIDATES[0])
        with patch.object(r.sys, "executable", "/runtime/system"), \
                patch.object(Path, "is_file", return_value=True), \
                patch.object(r.subprocess, "run", side_effect=[self.result(1, "no pcbnew"), self.result()]) as run:
            self.assertEqual(bundled, r.component_python())
        self.assertEqual(["/runtime/system", bundled], [item.args[0][0] for item in run.call_args_list])
        self.assertTrue(all(item.kwargs["timeout"] == 15 for item in run.call_args_list))

    def test_unavailable_runtime_is_a_failure_not_silent_partial_refresh(self):
        r = self.renderer
        with patch.object(Path, "is_file", return_value=False), \
                patch.object(r.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "No installed Python with pcbnew"):
                r.component_python()
        run.assert_not_called()

    def test_probe_timeout_or_loader_error_can_try_next_existing_runtime(self):
        r = self.renderer
        with patch.object(r.sys, "executable", "/runtime/system"), \
                patch.object(Path, "is_file", return_value=True), \
                patch.object(r.subprocess, "run", side_effect=[subprocess.TimeoutExpired("probe", 15),
                                                               OSError("loader error"), self.result()]):
            self.assertEqual(str(r.KICAD_PYTHON_CANDIDATES[1]), r.component_python())

    def test_component_check_uses_system_python_without_pcbnew_probe(self):
        r = self.renderer
        with patch.object(r.sys, "executable", "/runtime/system"), \
                patch.object(r, "component_python") as probe, \
                patch.object(r.subprocess, "run", return_value=self.result()) as run:
            self.assertEqual([], r.component_views("--check"))
        probe.assert_not_called()
        self.assertEqual(["/runtime/system", str(r.COMPONENT_RENDER_SCRIPT), "--check"], run.call_args.args[0])
        self.assertEqual(ROOT, run.call_args.kwargs["cwd"])

    def test_component_write_uses_selected_runtime_and_existing_writer(self):
        r = self.renderer
        with patch.object(r, "component_python", return_value="/runtime/kicad"), \
                patch.object(r.subprocess, "run", return_value=self.result()) as run:
            self.assertEqual([], r.component_views("--write"))
        self.assertEqual(["/runtime/kicad", str(r.COMPONENT_RENDER_SCRIPT), "--write"], run.call_args.args[0])

    def test_component_child_failure_preserves_exit_and_diagnostic(self):
        r = self.renderer
        with patch.object(r.subprocess, "run", return_value=self.result(7, "stale component view: UI")):
            errors = r.component_views("--check")
        self.assertEqual(1, len(errors))
        self.assertIn("exit 7", errors[0])
        self.assertIn("stale component view: UI", errors[0])

    def test_missing_child_executable_is_reported_as_failure(self):
        with patch.object(self.renderer.subprocess, "run", side_effect=OSError("missing executable")):
            errors = self.renderer.component_views("--check")
        self.assertIn("missing executable", errors[0])

    def test_invalid_component_mode_is_not_dispatched(self):
        with patch.object(self.renderer.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                self.renderer.component_views("--delete")
        run.assert_not_called()

    def test_write_preflights_then_refreshes_both_groups_and_checks_both(self):
        r = self.renderer
        events = []
        with patch.object(r, "component_python", side_effect=lambda: events.append("runtime") or "/runtime/kicad"), \
                patch.object(r, "render", side_effect=lambda name, *args: events.append("render:" + name)), \
                patch.object(r, "check", side_effect=lambda name, *args: events.append("check:" + name) or []), \
                patch.object(r, "component_views", side_effect=lambda mode, *args: events.append("component:" + mode) or []) as component:
            code, output = self.main("--write")
        self.assertEqual(0, code)
        self.assertEqual(["runtime", "render:ui", "render:rf", "component:--write",
                          "check:ui", "check:rf", "component:--check"], events)
        self.assertEqual([call("--write", "/runtime/kicad"), call("--check")], component.call_args_list)
        self.assertIn("4 component faces and overview", output)

    def test_missing_runtime_prevents_any_partial_write(self):
        r = self.renderer
        with patch.object(r, "component_python", side_effect=RuntimeError("no pcbnew runtime")), \
                patch.object(r, "render") as render, patch.object(r, "component_views") as component:
            code, output = self.main("--write")
        self.assertEqual(1, code)
        self.assertIn("no pcbnew runtime", output)
        render.assert_not_called()
        component.assert_not_called()

    def test_component_write_error_is_not_overwritten_by_later_success(self):
        r = self.renderer
        with patch.object(r, "component_python", return_value="/runtime/kicad"), \
                patch.object(r, "render"), patch.object(r, "check", return_value=[]) as check, \
                patch.object(r, "component_views", return_value=["component write failed"]) as component:
            code, output = self.main("--write")
        self.assertEqual(1, code)
        self.assertNotIn("renders pass", output)
        check.assert_not_called()
        component.assert_called_once_with("--write", "/runtime/kicad")

    def test_check_rejects_stale_components_even_when_routing_is_fresh(self):
        r = self.renderer
        with patch.object(r, "render") as render, patch.object(r, "component_python") as probe, \
                patch.object(r, "check", return_value=[]) as check, \
                patch.object(r, "component_views", return_value=["component view is stale"]) as component:
            code, output = self.main("--check")
        self.assertEqual(1, code)
        self.assertIn("component view is stale", output)
        self.assertEqual(2, check.call_count)
        component.assert_called_once_with("--check")
        render.assert_not_called()
        probe.assert_not_called()

    def test_check_reports_stale_routing_and_components_together(self):
        r = self.renderer
        with patch.object(r, "check", side_effect=[["UI routing stale"], []]), \
                patch.object(r, "component_views", return_value=["RF component stale"]):
            code, output = self.main("--check")
        self.assertEqual(1, code)
        self.assertIn("UI routing stale", output)
        self.assertIn("RF component stale", output)

    def test_check_only_accepts_both_fresh_groups(self):
        r = self.renderer
        with patch.object(r, "render") as render, patch.object(r, "check", return_value=[]), \
                patch.object(r, "component_views", return_value=[]) as component:
            code, output = self.main("--check")
        self.assertEqual(0, code)
        self.assertIn("renders pass", output)
        render.assert_not_called()
        component.assert_called_once_with("--check")


if __name__ == "__main__":
    unittest.main()
