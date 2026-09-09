"""Independent semantic inventory and native-label negative regressions."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "interface_coverage", ROOT / "hardware/layout/h6_r2_interface_label_coverage.py")
coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coverage)
UI, RF = coverage.PROJECTS


def read(path):
    return json.loads((ROOT / path).read_text())


class InterfaceLabelCoverageTests(unittest.TestCase):
    def setUp(self):
        self.ledger = read("hardware/ecad/generated/H2-R2-native-instance-ledger.json")["rows"]
        self.devices = read("hardware/architecture/devices.json")["devices"]
        self.contract = coverage.load_contract(ROOT)
        self.labels = {UI: [], RF: []}
        self.snapshots = {p: {"project": p, "placements": [], "texts": []} for p in (UI, RF)}
        ledger = {(r["project"], r["reference"]): r for r in self.ledger}
        for record in self.contract["interfaces"] + self.contract["assembly_contexts"]:
            self.snapshots[record["project"]]["placements"].append({
                "reference": record["reference"], "instance": record["instance"],
                "side": record["component_side"],
                "footprint": ledger[(record["project"], record["reference"])]["footprint"]})
            for spec in record["labels"]:
                if spec.get("optional"):
                    continue
                project = spec.get("project", record["project"])
                for _ in range(spec.get("count", 1)):
                    label = {"instance": record["instance"],
                             "reference": spec.get("reference", record["reference"]),
                             "text": spec["text"], "layer": spec["layer"],
                             "at_mm": [10., 2. * len(self.labels[project])], "role": "assembly"}
                    if "source_project" in spec:
                        label["source_project"] = spec["source_project"]
                    self.labels[project].append(label)
                    self.snapshots[project]["texts"].append({
                        "id": str(len(self.labels[project])), "text": label["text"],
                        "layer": label["layer"], "at_mm": label["at_mm"],
                        "visible": True, "mirrored": label["layer"] == "B.Silkscreen"})

    def check(self, native=True):
        return coverage.check_coverage(self.ledger, self.devices, self.labels,
                                       self.snapshots if native else None, self.contract)

    def rejected(self, kind):
        result = self.check()
        self.assertEqual("review_required", result["status"])
        self.assertIn(kind, [e["kind"] for e in result["errors"]])
        self.assertFalse(result["production_release_authorized"])

    def test_actual_ledger_interface_inventory_is_independent_and_exhaustive(self):
        actual = {(r["project"], r["reference"]) for r in self.ledger
                  if coverage.is_interface(r, self.devices)}
        ui = {f"J{i}" for i in range(1, 19)} | {f"SW{i}" for i in range(1, 22)}
        ui |= {f"D{i}" for i in range(1, 12)} | {"U23", "U24"}
        rf = {f"J{i}" for i in range(1, 14)} | {f"SW{i}" for i in range(1, 6)}
        rf |= {"BT1", "MK1", "LS1", "U83", "L32", "TP1"}
        self.assertEqual({(UI, r) for r in ui} | {(RF, r) for r in rf}, actual)
        self.assertEqual(76, len(actual))
        self.assertFalse(coverage.is_interface(next(r for r in self.ledger
                         if r["instance"] == "ir_emitter_limit"), self.devices))
        self.assertTrue(coverage.is_interface(next(r for r in self.ledger
                        if r["instance"] == "ir_carrier"), self.devices))

    def test_complete_native_labels_pass_without_geometry_or_release_claim(self):
        result = self.check()
        self.assertEqual([], result["errors"])
        self.assertEqual("pass_scoped_native", result["status"])
        self.assertEqual(76, result["required_interface_count"])
        self.assertEqual(76, result["matched_interface_count"])
        self.assertEqual(result["required_label_count"], result["native_matched_label_count"])
        self.assertFalse(result["production_release_authorized"])
        semantic = self.check(native=False)
        self.assertEqual("pass_scoped_semantic_plan", semantic["status"])
        self.assertFalse(semantic["native_checked"])

    def test_accepted_debug_short_labels_keep_exact_physical_owners(self):
        expected = {"J2": ("pack_dbg_header", "PACK"),
                    "J3": ("rf_rp_dbg_header", "RF"),
                    "J13": ("safety_dbg_header", "SAFE")}
        for ref, (instance, text) in expected.items():
            record = next(r for r in self.contract["interfaces"]
                          if r["project"] == RF and r["reference"] == ref)
            self.assertEqual(instance, record["instance"])
            self.assertEqual([(text, "B.Silkscreen")],
                             [(s["text"], s["layer"]) for s in record["labels"]])
            ledger = next(r for r in self.ledger if r["project"] == RF and r["reference"] == ref)
            self.assertEqual(instance, ledger["instance"])
        original = copy.deepcopy(self.labels)
        for ref, old_draft in (("J2", "PK"), ("J3", "RF DBG"), ("J13", "SAFE\nDBG")):
            with self.subTest(ref=ref):
                self.labels = copy.deepcopy(original)
                label = next(r for r in self.labels[RF] if r["reference"] == ref)
                label["text"] = old_draft
                self.assertEqual("review_required", self.check()["status"])

    def test_native_project_scope_is_explicit_and_crossboard_owner_survives(self):
        for project, count in ((UI, 53), (RF, 23)):
            result = coverage.check_coverage(self.ledger, self.devices,
                {project: self.labels[project]}, {project: self.snapshots[project]},
                self.contract, projects=(project,))
            self.assertEqual([], result["errors"])
            self.assertEqual(count, result["required_interface_count"])
        result = coverage.check_coverage(self.ledger, self.devices, {}, {}, self.contract, projects=())
        self.assertEqual("review_required", result["status"])

    def test_missing_new_duplicated_or_wrongly_typed_physical_interface_rejected(self):
        original = copy.deepcopy((self.ledger, self.devices, self.contract))
        for mutation in ("missing_both", "new_connector", "new_kind_connector", "duplicate_ref", "duplicate_instance", "wrong_mpn", "wrong_kind"):
            with self.subTest(mutation=mutation):
                self.ledger, self.devices, self.contract = copy.deepcopy(original)
                row = next(r for r in self.ledger if r["instance"] == "ir_carrier")
                if mutation == "missing_both":
                    self.ledger.remove(row)
                    self.contract["interfaces"] = [r for r in self.contract["interfaces"] if r["instance"] != "ir_carrier"]
                elif mutation.startswith("new_"):
                    new = copy.deepcopy(next(r for r in self.ledger if r["instance"] == "m1_ui_plug"))
                    new.update(instance="additional_interface", reference="J99" if mutation == "new_connector" else "U999")
                    self.ledger.append(new)
                elif mutation == "duplicate_ref":
                    self.ledger.append(copy.deepcopy(row))
                elif mutation == "duplicate_instance":
                    other = copy.deepcopy(row); other["reference"] = "U999"; self.ledger.append(other)
                elif mutation == "wrong_mpn":
                    row["mpn"] = "wrong"
                else:
                    self.devices[row["device_id"]]["kind"] = "ordinary_resistor"
                self.assertEqual("review_required", self.check()["status"])

    def test_missing_extra_duplicate_wrong_reference_side_text_and_crossboard_owner_rejected(self):
        original = copy.deepcopy(self.labels)
        for mutation in ("missing", "empty", "duplicate", "wrong_ref", "wrong_side", "wrong_text", "wrong_owner", "extra_ic"):
            with self.subTest(mutation=mutation):
                self.labels = copy.deepcopy(original)
                label = next(r for r in self.labels[UI] if r["instance"] == "ir_emitter")
                if mutation == "missing": self.labels[UI].remove(label)
                elif mutation == "empty": self.labels[UI] = []
                elif mutation == "duplicate": self.labels[UI].append(copy.deepcopy(label))
                elif mutation == "wrong_ref": label["reference"] = "D44"
                elif mutation == "wrong_side": label["layer"] = "B.Silkscreen"
                elif mutation == "wrong_text": label["text"] = "IR RX"
                elif mutation == "wrong_owner":
                    next(r for r in self.labels[UI] if r["instance"] == "microphone")["source_project"] = UI
                else:
                    label = copy.deepcopy(label); label.update(instance="s3", reference="U1")
                    self.labels[UI].append(label)
                self.assertEqual("review_required", self.check()["status"])

    def test_contract_truncation_duplicates_empty_and_optional_only_not_waivers(self):
        original = copy.deepcopy(self.contract)
        for mutation in ("truncated", "duplicate", "empty", "all_optional", "wrong_identity", "release"):
            with self.subTest(mutation=mutation):
                self.contract = copy.deepcopy(original)
                if mutation == "truncated": self.contract["interfaces"].pop()
                elif mutation == "duplicate": self.contract["interfaces"].append(copy.deepcopy(self.contract["interfaces"][0]))
                elif mutation == "empty": self.contract["interfaces"][0]["labels"] = []
                elif mutation == "all_optional":
                    for s in self.contract["interfaces"][0]["labels"]: s["optional"] = True
                elif mutation == "wrong_identity": self.contract["interfaces"][0]["instance"] = "other"
                else: self.contract["production_release_authorized"] = True
                self.assertEqual("review_required", self.check()["status"])

    def test_native_missing_ref_wrong_side_and_swapped_instance_rejected(self):
        original = copy.deepcopy(self.snapshots)
        for mutation in ("missing", "wrong_side", "wrong_owner", "wrong_footprint", "duplicate"):
            with self.subTest(mutation=mutation):
                self.snapshots = copy.deepcopy(original)
                rows = self.snapshots[UI]["placements"]
                row = next(r for r in rows if r["reference"] == "U23")
                if mutation == "missing": rows.remove(row)
                elif mutation == "wrong_side": row["side"] = "F.Cu"
                elif mutation == "wrong_owner": row["instance"] = "ir_demod"
                elif mutation == "wrong_footprint": row["footprint"] = "Resistor_SMD:R_0402_1005Metric"
                else: rows.append(copy.deepcopy(row))
                self.assertEqual("review_required", self.check()["status"])

    def test_native_fab_hidden_mirror_missing_duplicate_and_position_drift_rejected(self):
        original = copy.deepcopy(self.snapshots)
        for mutation in ("fab", "hidden", "mirror", "missing", "duplicate", "extra_elsewhere", "moved"):
            with self.subTest(mutation=mutation):
                self.snapshots = copy.deepcopy(original)
                rows = self.snapshots[UI]["texts"]
                row = next(r for r in rows if r["text"] == "IR TX")
                if mutation == "fab": row["layer"] = "F.Fab"
                elif mutation == "hidden": row["visible"] = False
                elif mutation == "mirror": row["mirrored"] = True
                elif mutation == "missing": rows.remove(row)
                elif mutation == "duplicate": rows.append(copy.deepcopy(row))
                elif mutation == "extra_elsewhere":
                    other = copy.deepcopy(row); other["at_mm"][0] += 3; rows.append(other)
                else: row["at_mm"] = [2., 2.]
                self.assertEqual("review_required", self.check()["status"])

    def test_optional_local_mic_does_not_replace_required_crossboard_mic(self):
        local = {"instance": "microphone", "reference": "MK1", "text": "MIC",
                 "layer": "B.Silkscreen", "at_mm": [45., 145.]}
        self.labels[RF].append(local)
        self.snapshots[RF]["texts"].append(dict(local, visible=True, mirrored=True))
        self.assertEqual([], self.check()["errors"])
        self.labels[UI] = [r for r in self.labels[UI] if r["instance"] != "microphone"]
        self.rejected("required_label_count_mismatch")

    def test_unplanned_optional_native_text_and_failed_snapshot_are_not_silently_accepted(self):
        self.snapshots[RF]["texts"].append({"text": "MIC", "layer": "B.Silkscreen",
            "at_mm": [45., 145.], "visible": True, "mirrored": True})
        self.rejected("extra_native_interface_label")
        self.snapshots[RF]["texts"].pop()
        for field in ("errors", "extraction_errors"):
            with self.subTest(field=field):
                self.snapshots[RF][field] = [{"kind": "native_extraction_failed"}]
                self.rejected("native_snapshot_contains_errors")
                del self.snapshots[RF][field]

    def test_auxiliary_branding_allowed_but_not_interface_identity_waiver(self):
        self.labels[UI].append({"instance": "board_branding", "reference": None,
                                "text": "Board revision", "layer": "F.Silkscreen"})
        self.assertEqual([], self.check()["errors"])
        self.labels[UI][-1]["reference"] = "U23"
        self.rejected("unexpected_label_identity")

    def test_cell_and_speaker_polarities_are_explicit_not_generic_presence(self):
        records = {r["instance"]: r for r in self.contract["interfaces"]}
        self.assertEqual({"CELL0 -", "CELL1 +", "CELL0 +", "CELL1 -"},
                         {r["text"] for r in records["pack_holder"]["labels"]})
        self.assertEqual({"SPK +", "SPK -"}, {r["text"] for r in records["speaker"]["labels"]})
        self.assertTrue(all(r["layer"] == "B.Silkscreen" for r in records["speaker"]["labels"]))
        self.assertIn("BTL", records["speaker"]["rationale"])
        self.assertIn("checkerboard", records["pack_holder"]["rationale"])


if __name__ == "__main__":
    unittest.main()
