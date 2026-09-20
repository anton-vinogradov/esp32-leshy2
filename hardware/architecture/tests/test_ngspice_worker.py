"""Adapter safety/failure tests; optional real library tests use fresh processes."""

import copy
import ctypes as C
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

from tools import ngspice_worker as worker


REQUEST = {"netlist": ["divider", "V1 in 0 3.3", "R1 in out 1k", "R2 out 0 1k", ".end"], "vectors": ["v(out)"]}


class NgspiceWorkerTests(unittest.TestCase):
    def test_valid_inline_model_and_vectors(self):
        request = copy.deepcopy(REQUEST)
        request["netlist"][1:1] = ["* .include in comments is harmless", ".param x=1", "+ y=2",
                                   ".subckt unused p n", "D1 p n dm", ".model dm D(IS=1e-12)", ".ends unused"]
        request["vectors"] = ["v(out)", "i(v1)", "v1#branch", "out"]
        self.assertEqual((request["netlist"], request["vectors"]), worker.validate_request(request))

    def test_native_transmission_line_delay_is_allowed(self):
        request = copy.deepcopy(REQUEST)
        request["netlist"].insert(2, "T_TPD in 0 delayed 0 Z0=50 TD=450n")
        self.assertEqual(request["netlist"], worker.validate_request(request)[0])

    def test_all_non_op_analysis_and_file_command_directives_rejected(self):
        for directive in (".control", ".include model.lib", ".inc model.lib", ".lib x", ".sp x", ".exec x", ".shell x",
                          ".load x", ".save all", ".wrdata x", ".tran 1n 1u", ".dc V1 0 3 1", ".ac dec 1 1 10",
                          ".noise x", ".tf x", ".four x", ".meas x", ".hdl x", ".option x", ".print all", ".plot all"):
            request = copy.deepcopy(REQUEST)
            request["netlist"].insert(1, "  " + directive.upper())
            with self.subTest(directive=directive), self.assertRaisesRegex(ValueError, "directive"):
                worker.validate_request(request)

    def test_unsafe_cards_and_embedded_lines_rejected(self):
        for line in ("V2 x 0 1\n.control", "V2 x 0 1\r.control", "V2 x 0 1\0", "V2 x 0 `shell`",
                     "V2 x 0 $(shell)", "V2 x 0 1; shell", "V2 x 0 PWL FILE='secret'", "A1 x filesource", "+ .include x"):
            request = copy.deepcopy(REQUEST)
            request["netlist"].insert(2, line)
            with self.subTest(line=line), self.assertRaises(ValueError):
                worker.validate_request(request)

    def test_schema_title_end_and_continuation_rejected(self):
        for request in ({}, {**REQUEST, "commands": ["op"]}, {**REQUEST, "netlist": []},
                        {**REQUEST, "netlist": [".control", "V1 x 0 1", ".end"]},
                        {**REQUEST, "netlist": REQUEST["netlist"][:-1]},
                        {**REQUEST, "netlist": REQUEST["netlist"] + [".op"]},
                        {**REQUEST, "netlist": ["title", "+ x", ".end"]}):
            with self.subTest(request=request), self.assertRaises(ValueError):
                worker.validate_request(request)

    def test_empty_unsafe_or_duplicate_vectors_rejected(self):
        for vectors in ([], [""], ["v(out)", "V(OUT)"], ["v(out);shell"], ["v(out) + 1"], ["@m1[id]"], [None], ["v(out)\nquit"]):
            with self.subTest(vectors=vectors), self.assertRaises(ValueError):
                worker.validate_request({**REQUEST, "vectors": vectors})

    def test_callback_logs_bounded_and_errors_not_lost_after_truncation(self):
        messages = worker.Messages()
        with redirect_stderr(io.StringIO()) as output:
            messages.receive(b"stdout " + b"x" * (worker.MAX_LOG * 2), 0, None)
            messages.receive(b"stderr Warning: unsupported parameter ignored", 0, None)
        self.assertEqual(worker.MAX_LOG, len(output.getvalue()))
        with self.assertRaisesRegex(ValueError, "unsupported"):
            messages.check(0, "parse")

    def test_controlled_exit_or_nonzero_native_return_rejected(self):
        for controlled in (False, True):
            messages = worker.Messages()
            if controlled:
                messages.controlled_exit(0, False, True, 0, None)
            with self.subTest(controlled=controlled), self.assertRaises(ValueError):
                messages.check(0 if controlled else 1, "op")

    def test_external_init_files_refused(self):
        with patch.object(worker.os.path, "lexists", return_value=True), self.assertRaisesRegex(ValueError, "init file"):
            worker.reject_init_files()

    def test_configured_init_directory_is_guarded_without_changing_home(self):
        custom = "/tmp/ngspice-init-guard-fixture"
        with patch.dict(worker.os.environ, {"SPICE_USERINIT_DIR": custom}), \
                patch.object(worker.os.path, "lexists", side_effect=lambda p: str(p) == custom + "/.spiceinit"), \
                self.assertRaisesRegex(ValueError, "init file"):
            worker.reject_init_files()

    def test_real_scalar_extraction_and_missing_complex_nonfinite_rejection(self):
        data = (C.c_double * 1)(1.65)
        info = worker.VectorInfo(b"out", 3, 1, data, None, 1)
        library = Mock(ngGet_Vec_Info=Mock(return_value=C.pointer(info)))
        self.assertEqual(1.65, worker.read_vector(library, "v(out)"))
        library.ngGet_Vec_Info.return_value = C.POINTER(worker.VectorInfo)()
        with self.assertRaisesRegex(ValueError, "missing"):
            worker.read_vector(library, "v(out)")
        library.ngGet_Vec_Info.return_value = C.pointer(info)
        for field, value, expected in (("length", 2, "one operating"), ("flags", 2, "complex"),
                                       ("realdata", None, "non-real"),
                                       ("compdata", (worker.Complex * 1)(worker.Complex(1, 1)), "complex")):
            prior = getattr(info, field)
            setattr(info, field, value)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, expected):
                worker.read_vector(library, "v(out)")
            setattr(info, field, prior)
        info.realdata = data
        info.compdata = None
        for value in (float("nan"), float("inf"), float("-inf")):
            data[0] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "nonfinite"):
                worker.read_vector(library, "v(out)")

    def test_cli_parse_and_native_failure_are_json_exit_two(self):
        for raw, error in (("{bad", None), (json.dumps(REQUEST), OSError("missing library"))):
            with patch("sys.stdin", io.StringIO(raw)), patch.object(worker, "run_request", side_effect=error) as run, \
                    redirect_stdout(io.StringIO()) as output:
                self.assertEqual(2, worker.main([]))
                result = json.loads(output.getvalue())
                self.assertEqual("execution_error", result["status"])
                self.assertIs(False, result["qualified"])
                if error is None:
                    run.assert_not_called()

    def test_cli_success_never_claims_qualification(self):
        result = {"status": "worker_execution_success", "qualified": False, "values": {"v(out)": 1.65}}
        with patch("sys.stdin", io.StringIO(json.dumps(REQUEST))), patch.object(worker, "run_request", return_value=result), \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(0, worker.main([]))
            self.assertEqual(result, json.loads(output.getvalue()))

    def test_request_file_alternative_does_not_read_stdin(self):
        result = {"status": "worker_execution_success", "qualified": False}
        with patch.object(Path, "is_file", return_value=True), patch.object(Path, "is_symlink", return_value=False), \
                patch.object(Path, "open", return_value=io.StringIO(json.dumps(REQUEST))), \
                patch.object(worker, "run_request", return_value=result) as run, patch("sys.stdin") as stdin, \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(0, worker.main(["--request", "/tmp/request.json"]))
            stdin.read.assert_not_called()
            self.assertEqual(REQUEST, run.call_args.args[0])
            self.assertFalse(json.loads(output.getvalue())["qualified"])

    def test_request_symlink_and_oversized_input_rejected(self):
        with patch.object(Path, "is_file", return_value=True), patch.object(Path, "is_symlink", return_value=True), \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(2, worker.main(["--request", "/tmp/request.json"]))
            self.assertIn("real request", json.loads(output.getvalue())["error"])
        with patch("sys.stdin", io.StringIO("x" * (worker.MAX_INPUT + 1))), redirect_stdout(io.StringIO()) as output:
            self.assertEqual(2, worker.main([]))
            self.assertIn("too large", json.loads(output.getvalue())["error"])

    @unittest.skipUnless(worker.DEFAULT_LIBRARY.is_file(), "KiCad shared ngspice not available")
    def test_real_divider_fresh_process(self):
        run = subprocess.run([sys.executable, "-B", str(Path(worker.__file__))], input=json.dumps(REQUEST),
                             text=True, capture_output=True, timeout=15, check=False)
        self.assertEqual(0, run.returncode, run.stderr + run.stdout)
        result = json.loads(run.stdout)
        self.assertAlmostEqual(1.65, result["values"]["v(out)"])
        self.assertEqual("worker_execution_success", result["status"])
        self.assertFalse(result["qualified"])
        self.assertTrue(result["ngspice_version"])
        self.assertRegex(result["library_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(2, len(result["code_model_sha256"]))
        self.assertIn("can't find the initialization file spinit", run.stderr)

    @unittest.skipUnless(worker.DEFAULT_LIBRARY.is_file(), "KiCad shared ngspice not available")
    def test_real_bad_model_and_missing_vector_fail(self):
        bad_model = copy.deepcopy(REQUEST)
        bad_model["netlist"].insert(2, "Xbad in out UNKNOWN_MODEL")
        missing = {**REQUEST, "vectors": ["v(absent)"]}
        for request in (bad_model, missing):
            with self.subTest(request=request):
                run = subprocess.run([sys.executable, "-B", str(Path(worker.__file__))], input=json.dumps(request),
                                     text=True, capture_output=True, timeout=15, check=False)
                self.assertEqual(2, run.returncode, run.stderr + run.stdout)
                self.assertEqual("execution_error", json.loads(run.stdout)["status"])

    @unittest.skipUnless(worker.DEFAULT_LIBRARY.is_file(), "KiCad shared ngspice not available")
    def test_real_inline_pspice_vswitch_translation(self):
        request = {"netlist": ["PSpice VSWITCH compatibility control", "V1 in 0 3.3", "Vc gate 0 1",
                   "R1 in out 1000", "S1 out 0 gate 0 sw", ".model sw VSWITCH(Ron=1 Roff=1e12 Von=1 Voff=0)", ".end"],
                   "vectors": ["v(out)"]}
        run = subprocess.run([sys.executable, "-B", str(Path(worker.__file__))], input=json.dumps(request),
                             text=True, capture_output=True, timeout=15, check=False)
        self.assertEqual(0, run.returncode, run.stderr + run.stdout)
        self.assertAlmostEqual(3.3 / 1001, json.loads(run.stdout)["values"]["v(out)"], places=9)


if __name__ == "__main__":
    unittest.main()
