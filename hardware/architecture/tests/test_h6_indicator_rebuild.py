"""Adverse reconstruction mutations must not inherit native or physical approval."""

from collections import defaultdict
from contextlib import redirect_stdout
import copy
from fractions import Fraction as F
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import rebuild_indicators as tool


class IndicatorRebuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual, cls.hashes = tool.load_sources()

    def setUp(self):
        self.data = copy.deepcopy(self.actual)
        self.spec = tool.validate_sources(self.data)

    def instance(self, name):
        return next(r for r in self.data["instances"]["rows"] if r["project"] == tool.PROJECT and r["instance"] == name)

    def endpoint(self, name):
        return next(r for r in self.data["nets"]["rows"] if r["project"] == tool.PROJECT and r["endpoint"] == name)

    def generated_fixture(self):
        components = {r: {"footprint": p["footprint"], "edg_path": p["edg_path"],
                          "edg_part": "" if r.startswith("R") else p["mpn"],
                          "edg_value": "2.2k, 1%, 0.0625 W" if r.startswith("R") else p["mpn"]}
                      for r, p in self.spec["components"].items()}
        groups = defaultdict(list)
        for pin, net in self.spec["terminal_nets"].items():
            groups[net].append(pin)
        return components, list(groups.values())

    def native_fixture(self):
        native = {r: {"value": p["mpn"], "footprint": p["footprint"], "pads": {}} for r, p in self.spec["components"].items()}
        for terminal, net in self.spec["terminal_nets"].items():
            ref, pin = terminal.split(".")
            native[ref]["pads"][pin] = self.spec["bindings"][net]
        return native

    def test_complete_current_projection_has_20_parts_40_pads_and_22_nets(self):
        components, groups = self.generated_fixture()
        self.assertEqual((20, 40, 22), (len(components), sum(map(len, groups)), len(groups)))
        tool.validate_generated(components, groups, self.spec, self.spec["terminal_nets"])
        tool.validate_native(self.native_fixture(), self.spec)
        self.assertEqual({"R26.1", "R27.1", "R31.1", "R33.1", "R35.1", "R36.1", "R37.1", "R38.1", "R75.1"}, set(next(g for g in groups if "R38.1" in g)))
        self.assertEqual("FAULT_KILL", self.spec["terminal_nets"]["R32.1"])
        self.assertEqual("POWER_GROUND", self.spec["terminal_nets"]["D4.1"])

    def test_external_voice_boundary_keeps_both_rf_drivers(self):
        endpoints = self.spec["external_endpoints_not_generated"]["EV_N6_VOICE"]
        self.assertIn("LESHY2-RF-R2:evidence_cmp_voice.OUT", endpoints)
        self.assertIn("LESHY2-RF-R2:evidence_cmp_voice_v.OUT", endpoints)

    def test_missing_or_duplicate_branch_is_rejected(self):
        rows = self.data["instances"]["rows"]
        row = self.instance("s3_tx_led")
        rows.remove(row)
        with self.assertRaisesRegex(ValueError, "coverage"):
            tool.validate_sources(self.data)
        rows.extend([row, copy.deepcopy(row)])
        with self.assertRaisesRegex(ValueError, "coverage"):
            tool.validate_sources(self.data)

    def test_source_exact_part_value_footprint_and_fault_topology_are_bound(self):
        for field, value in (("mpn", "other-part"), ("device_id", tool.AMBER_ID), ("footprint", "wrong:footprint")):
            with self.subTest(field=field):
                row = self.instance("s3_tx_led")
                original = row[field]
                row[field] = value
                with self.assertRaises(ValueError):
                    tool.validate_sources(self.data)
                row[field] = original
        self.data["devices"]["devices"][tool.RES_ID]["kind"] = "1kohm_1pct_0402_resistor"
        with self.assertRaises(ValueError):
            tool.validate_sources(self.data)
        self.data = copy.deepcopy(self.actual)
        self.endpoint("fault_led_series.END_1")["net"] = "AON_SAFE_3V3"
        with self.assertRaisesRegex(ValueError, "connection"):
            tool.validate_sources(self.data)

    def test_missing_or_duplicated_native_endpoint_is_rejected(self):
        rows, row = self.data["nets"]["rows"], self.endpoint("s3_tx_led.A")
        rows.remove(row)
        with self.assertRaisesRegex(ValueError, "endpoint coverage"):
            tool.validate_sources(self.data)
        rows.extend([row, copy.deepcopy(row)])
        with self.assertRaisesRegex(ValueError, "endpoint coverage"):
            tool.validate_sources(self.data)

    def test_native_crossbranch_net_and_contact_disposition_are_rejected(self):
        for key, value in (("net", "C5_TX_LED_A"), ("disposition", "no_connect")):
            with self.subTest(key=key):
                row = self.endpoint("s3_tx_led.A")
                original = row[key]
                row[key] = value
                with self.assertRaises(ValueError):
                    tool.validate_sources(self.data)
                row[key] = original

    def test_materialized_anode_cathode_swap_is_rejected(self):
        group = next(g for g in self.data["material"]["groups"] if g["device_id"] == tool.RED_ID)
        for row in group["contacts"]:
            row["pads"] = ["1" if row["contact"] == "A" else "2"]
        with self.assertRaisesRegex(ValueError, "swapped"):
            tool.validate_sources(self.data)

    def test_duplicate_material_contact_or_noninjective_pcb_binding_is_rejected(self):
        group = next(g for g in self.data["material"]["groups"] if g["device_id"] == tool.RED_ID)
        group["contacts"].append(copy.deepcopy(group["contacts"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate material"):
            tool.validate_sources(self.data)
        self.data = copy.deepcopy(self.actual)
        bindings = self.data["bindings"]["projects"][tool.PROJECT]["canonical_to_kicad"]
        bindings["C5_TX_LED_A"] = bindings["S3_TX_LED_A"]
        with self.assertRaisesRegex(ValueError, "distinct"):
            tool.validate_sources(self.data)

    def test_missing_or_conflicting_provenance_cannot_be_overwritten(self):
        del self.data["material"]["sources"]["device_register"]
        with self.assertRaisesRegex(ValueError, "membership"):
            tool.source_declarations(self.data)
        self.data = copy.deepcopy(self.actual)
        self.data["bindings"]["source_hashes"][tool.INPUTS["instances"]] = "0" * 64
        with self.assertRaisesRegex(ValueError, "conflicting"):
            tool.source_declarations(self.data)

    def test_same_singleton_groups_with_swapped_named_returns_are_rejected(self):
        components, groups = self.generated_fixture()
        nets = copy.deepcopy(self.spec["terminal_nets"])
        nets["D9.1"], nets["D1.1"] = nets["D1.1"], nets["D9.1"]
        with self.assertRaisesRegex(ValueError, "boundary"):
            tool.validate_generated(components, groups, self.spec, nets)

    def test_exported_led_part_and_resistor_value_are_checked(self):
        for ref, key, wrong in (("D9", "edg_part", "LTST-C190KFKT"), ("R38", "edg_value", "1k, 1%, 0.0625 W")):
            components, groups = self.generated_fixture()
            components[ref][key] = wrong
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "part/value"):
                tool.validate_generated(components, groups, self.spec, self.spec["terminal_nets"])

    def test_generated_omission_duplicate_and_footprint_change_are_rejected(self):
        for mutation in (lambda c, g: c.pop("D9"), lambda c, g: g.append(g[0]),
                         lambda c, g: c["D9"].update(footprint="wrong:footprint"),
                         lambda c, g: g[0].pop()):
            components, groups = self.generated_fixture()
            mutation(components, groups)
            with self.assertRaises(ValueError):
                tool.validate_generated(components, groups, self.spec)

    def test_generated_led_swap_and_crossbranch_short_are_rejected(self):
        components, groups = self.generated_fixture()
        swapped = [["D9.1" if p == "D9.2" else "D9.2" if p == "D9.1" else p for p in g] for g in groups]
        with self.assertRaisesRegex(ValueError, "topology"):
            tool.validate_generated(components, swapped, self.spec)
        index1 = next(i for i, g in enumerate(groups) if "D9.2" in g)
        index2 = next(i for i, g in enumerate(groups) if "D1.2" in g)
        groups[index1].extend(groups[index2])
        groups.pop(index2)
        with self.assertRaisesRegex(ValueError, "topology"):
            tool.validate_generated(components, groups, self.spec)

    def test_separately_isolated_aon_branches_are_not_native_topology(self):
        components, groups = self.generated_fixture()
        source = next(g for g in groups if "R38.1" in g)
        groups.remove(source)
        groups.extend([[pad] for pad in source])
        with self.assertRaisesRegex(ValueError, "topology"):
            tool.validate_generated(components, groups, self.spec)

    def test_native_pcb_part_pad_or_omission_mutations_are_rejected(self):
        for mutate in (lambda n: n["D9"].update(value="other-part"), lambda n: n.pop("D9"),
                       lambda n: n["D9"]["pads"].update({"1": "wrong-net"})):
            native = self.native_fixture()
            mutate(native)
            with self.assertRaises(ValueError):
                tool.validate_native(native, self.spec)

    def test_stale_or_removed_source_hash_is_rejected(self):
        for hashes in ({**self.hashes, "tools/rebuild_indicators.py": "0" * 64}, {}):
            with self.assertRaisesRegex(ValueError, "sources changed|missing source"):
                tool.unchanged(hashes)
        with patch.object(tool, "snapshot", return_value={}):
            with self.assertRaisesRegex(ValueError, "sources changed"):
                tool.unchanged(self.hashes)

    def report_fixture(self):
        components, groups = self.generated_fixture()
        return {"status": "not_qualified", "mechanics_status": "pass", "qualified": False,
                "electrically_qualified": False, "production_promoted": False, "supply_checked": False,
                "branches": 10, "components": 20, "canonical_edg_sha256": "same-semantic-hash",
                "artifact_sha256": {name: "same" for name in tool.ARTIFACTS}, "native": self.native_fixture(),
                "generated": {"components": components, "terminal_groups": groups, "terminal_nets": self.spec["terminal_nets"]},
                "numerical": {name: {"resistance_ohm": [2178, 2222], "conditional_current_upper_a_exact": str(F("3.6") / 2178),
                                     "conditional_resistor_power_upper_w_exact": str(F("3.6") ** 2 / 2178)} for name in tool.BRANCHES}}

    def test_raw_protobuf_variation_allowed_but_semantic_or_text_change_rejected(self):
        first, second = self.report_fixture(), self.report_fixture()
        second["artifact_sha256"]["Indicators.edg"] = "raw-second"
        self.assertFalse(tool.replay_result([first, second], self.spec)["raw_protobuf_byte_identical"])
        for mutation in (lambda r: r.update(canonical_edg_sha256="different"),
                         lambda r: r["artifact_sha256"].update({"Indicators.net": "different"})):
            other = copy.deepcopy(second)
            mutation(other)
            with self.assertRaisesRegex(ValueError, "replay differs"):
                tool.replay_result([first, other], self.spec)

    def test_mechanics_success_cannot_become_physical_or_procurement_approval(self):
        for key in ("qualified", "electrically_qualified", "production_promoted", "supply_checked"):
            report = self.report_fixture()
            report[key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "qualification"):
                tool.validate_result(report, self.spec)

    def test_report_missing_numerics_artifacts_or_named_pads_is_rejected(self):
        for mutate in (lambda r: r["numerical"].pop("s3_tx_led"), lambda r: r["artifact_sha256"].pop("Indicators.csv"),
                       lambda r: r["generated"]["terminal_nets"].pop("D9.1")):
            report = copy.deepcopy(self.report_fixture())
            mutate(report)
            with self.assertRaises(ValueError):
                tool.validate_result(report, self.spec)

    def test_artifact_hashes_are_rechecked_before_publishing(self):
        path = Mock()
        file = path.__truediv__ = Mock(return_value=Mock())
        file.return_value.is_file.return_value = True
        file.return_value.is_symlink.return_value = False
        with patch.object(tool, "digest", return_value="changed"), self.assertRaisesRegex(ValueError, "artifact changed"):
            tool.validate_artifacts(self.report_fixture(), path)

    def test_successful_leader_with_orphan_is_cleaned_and_rejected(self):
        # Real bounded subprocess test; the child stays in the owned group.
        command = [sys.executable, "-c", "import os,subprocess,sys; p=subprocess.Popen([sys.executable,'-c','import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)']); print(p.pid,flush=True)"]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "child"
            target.mkdir()
            with self.assertRaisesRegex(ValueError, "descendants"):
                tool.run_worker(command, target, 5, None)
            pid = int((Path(directory) / "child.log").read_text().strip())
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    return
                stat = Path(f"/proc/{pid}/stat")
                if stat.exists():  # Linux may retain a terminated orphan as a zombie.
                    try:
                        if stat.read_text().rsplit(") ", 1)[1].startswith("Z"):
                            return
                    except FileNotFoundError:
                        return
                time.sleep(.01)
            self.fail(f"Synthetic child {pid} is still running")

    def test_sigterm_uses_normal_cancellation_and_restores_handler(self):
        previous = tool.signal.getsignal(tool.signal.SIGTERM)
        stream = io.StringIO()
        def terminate(args):
            os.kill(os.getpid(), tool.signal.SIGTERM)
        with patch.object(tool, "worker", side_effect=terminate), redirect_stdout(stream):
            self.assertEqual(130, tool.main(["--worker", "unused"]))
        self.assertEqual(previous, tool.signal.getsignal(tool.signal.SIGTERM))
        self.assertEqual("cancelled", json.loads(stream.getvalue())["status"])
        self.assertIsNone(json.loads(stream.getvalue())["report"])

    def test_runtime_implementation_change_is_rejected_before_import(self):
        dist = Mock(version="0.5.2")
        dist.locate_file.return_value = tool.PILOT / "venv/lib/python3.12/site-packages/edg"
        with patch.object(tool.metadata, "distribution", return_value=dist), patch.object(tool, "digest", return_value="wrong"):
            with self.assertRaisesRegex(ValueError, "installed EDG"):
                tool.prepare_runtime(Path("unused"), tool.DEFAULT_JAVA)

    def test_worker_failure_does_not_return_an_old_success_report(self):
        stream = io.StringIO()
        with patch.object(tool, "worker", side_effect=ValueError("stale")), redirect_stdout(stream):
            code = tool.main(["--worker", "unused"])
        self.assertEqual(2, code)
        self.assertIsNone(json.loads(stream.getvalue())["report"])


if __name__ == "__main__":
    unittest.main()
