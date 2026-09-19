"""CI orchestration/acceptance negatives; no native tools or router required."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools.route_474 import (PLAN, campaign, check_accepted_evidence, checked_result_hash,
                             cohort, failed_first, ResourceBudget, finish_registry,
                             expand_seeded_orders, sha, write)
from threading import Event


def cases():
    return {kind: {"id": kind, "scope": {"expected_connections": count},
                   "nets": [{"kicad_net": "a"}, {"kicad_net": "b"}]}
            for kind, count in (("ui", 252), ("rf", 222))}


def row(job, *, passed=True, signature="a" * 64):
    target = 252 if job["kind"] == "ui" else 222
    flags = ("geometry_pass", "candidate_pass", "preservation_recipe_pass", "dependencies_unchanged",
             "selected_complete", "drc_checked", "candidate_unchanged_during_checks")
    grade = {**dict.fromkeys(flags, True), "selected_remaining": [target, 0 if passed else 1],
             "native_unconnected": [1000, 1000 - target], "resolved_connections": target,
             "drc_violations": 0, "schematic_parity_errors": 0, "drc_selected_unconnected": 0,
             "kicad_version": "10.0.5", "failures": {}, "roi_escaped_objects": [],
             "all_net_regressions": {}, "electrically_qualified": False,
             "added_geometry_signature": signature, "new_vias": 10, "new_trace_length_mm": 100,
             "per_net": {"a": [1, 0], "b": [1, 0 if passed else 1]}}
    if not passed:
        grade.update(geometry_pass=False, candidate_pass=False, selected_complete=False)
    return {"profile": {"id": job["id"], **({"replay_of": job["replay_of"]} if "replay_of" in job else {})},
            "recipe": copy.deepcopy(job["recipe"]), "folder": "/fixture/" + job["id"], "cold_from_original": True,
            "geometry_pass": passed, "engine": {"exit_code": 0, "seconds": 1},
            "validation_process": {"exit_code": 0}, "validation": grade}


def plans(count=1):
    return {kind: {"profiles": [{"name": f"p-{i}"} for i in range(count)]} for kind in ("ui", "rf")}


class CampaignTests(unittest.TestCase):
    def test_default_plan_runs_two_initials_and_six_replays(self):
        plan = json.loads(PLAN.read_text())["cases"]
        self.assertEqual({kind: len(section["profiles"]) for kind, section in plan.items()},
                         {"ui": 1, "rf": 1})
        self.assertTrue(all(not section.get("adaptive") for section in plan.values()))
        jobs = []
        def execute(batch, wave):
            jobs.extend(batch)
            return [row(job) for job in batch]
        result = campaign(cases(), plan, execute)
        self.assertEqual((result["status"], result["resolved"]), ("pass", 474))
        self.assertEqual(len(jobs), 8)
        self.assertEqual(sum("replay_of" in job for job in jobs), 6)

    def test_seed_order_is_exact_stable_and_frozen_for_replays(self):
        case_set = cases()
        case_set["ui"]["nets"] = [{"kicad_net": str(i)} for i in range(20)]
        config = {"cases": plans(2)}
        for i, recipe in enumerate(config["cases"]["ui"]["profiles"]):
            recipe.update(order_seed=i, ordering="original")
        original = copy.deepcopy(config)
        expanded = expand_seeded_orders(config, case_set)
        self.assertEqual(config, original)
        self.assertEqual(expanded, expand_seeded_orders(config, case_set))
        profiles = expanded["cases"]["ui"]["profiles"]
        self.assertNotEqual(profiles[0]["net_order"], profiles[1]["net_order"])
        for profile in profiles:
            self.assertCountEqual(profile["net_order"], [str(i) for i in range(20)])
            self.assertNotIn("order_seed", profile)
        result = campaign(case_set, expanded["cases"], lambda jobs, _: [row(j) for j in jobs])
        self.assertEqual(result["resolved"], 474)
        winner = result["cases"]["ui"]["winner"]["recipe"]
        self.assertTrue(all(r["recipe"] == winner for r in result["cases"]["ui"]["replays"]))

    def test_seed_cannot_hide_scope_or_override_order(self):
        for mutation in ({"order_seed": True}, {"order_seed": -1}, {"order_seed": 65536},
                         {"ordering": "mps"}, {"net_order": ["unknown"]}):
            config = {"cases": plans()}
            config["cases"]["ui"]["profiles"][0].update(order_seed=1, ordering="original")
            config["cases"]["ui"]["profiles"][0].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                expand_seeded_orders(config, cases())

    def test_complete_both_boards_and_three_replays(self):
        jobs = []
        def execute(batch, wave):
            jobs.extend(batch)
            return [row(j) for j in batch]
        result = campaign(cases(), plans(), execute)
        self.assertEqual((result["status"], result["resolved"]), ("pass", 474))
        self.assertEqual(len(jobs), 8)
        self.assertEqual(sum("replay_of" in j for j in jobs), 6)
        self.assertFalse(result["production_ready"])

    def test_partial_never_credited(self):
        result = campaign(cases(), plans(3), lambda jobs, _: [row(j, passed=j["kind"] == "rf") for j in jobs])
        self.assertEqual((result["status"], result["resolved"]), ("fail", 222))
        self.assertEqual(len(result["cases"]["ui"]["attempts"]), 3)

    def test_bounded_search_does_not_run_remaining_profiles_after_winner(self):
        result = campaign(cases(), plans(8), lambda jobs, _: [row(j) for j in jobs], wave_size=2)
        self.assertEqual(result["resolved"], 474)
        self.assertEqual(len(result["cases"]["ui"]["attempts"]), 4)

    def test_adaptive_failed_first_freezes_exact_scope(self):
        plan = plans()
        plan["ui"]["adaptive"] = [{"name": "template", "direction": "backward"}]
        def execute(jobs, wave):
            return [row(j, passed=j["kind"] == "rf" or j["recipe"]["name"].startswith("failed-first")) for j in jobs]
        result = campaign(cases(), plan, execute)
        self.assertEqual(result["resolved"], 474)
        self.assertEqual(result["cases"]["ui"]["winner"]["recipe"]["net_order"], ["b", "a"])

    def test_replay_mismatch_fails_case(self):
        def execute(jobs, wave):
            return [row(j, signature="b" * 64 if j["id"] == "ui-replay-3" else "a" * 64) for j in jobs]
        result = campaign(cases(), plans(), execute)
        self.assertEqual((result["status"], result["resolved"]), ("fail", 222))

    def test_cancelled_no_credit(self):
        result = campaign(cases(), plans(), lambda *_: self.fail("Called after cancellation"), cancelled=lambda: True)
        self.assertEqual(result["resolved"], 0)

    def test_wrong_job_identity_raises(self):
        def execute(jobs, wave):
            r = [row(j) for j in jobs]
            r[0]["profile"]["id"] = "wrong"
            return r
        with self.assertRaises(ValueError):
            campaign(cases(), plans(), execute)

    def test_missing_result_raises(self):
        with self.assertRaises(ValueError):
            campaign(cases(), plans(), lambda *_: [])

    def test_cohort_negative_mutations(self):
        winner = row({"id": "ui-initial", "kind": "ui", "recipe": {"name": "p"}})
        replays = [row({"id": f"ui-replay-{i}", "kind": "ui", "recipe": {"name": "p"},
                        "replay_of": "ui-initial"}) for i in range(1, 4)]
        self.assertTrue(cohort(cases()["ui"], winner, replays)["accepted"])
        self.assertFalse(cohort(cases()["ui"], winner, replays[:-1])["accepted"])
        changed_winner = copy.deepcopy(winner)
        changed_winner["cold_from_original"] = False
        self.assertFalse(cohort(cases()["ui"], changed_winner, replays)["accepted"])
        for location, key, value in ((None, "folder", winner["folder"]),
                                    (None, "cold_from_original", False),
                                    (None, "recipe", {"name": "other"}),
                                    ("validation", "drc_violations", 1),
                                    ("validation", "roi_escaped_objects", ["escape"]),
                                    ("validation", "all_net_regressions", {"other": 1}),
                                    ("validation", "schematic_parity_errors", 1),
                                    ("validation_process", "exit_code", 1)):
            with self.subTest(key=key):
                changed = copy.deepcopy(replays)
                (changed[-1][location] if location else changed[-1])[key] = value
                self.assertFalse(cohort(cases()["ui"], winner, changed)["accepted"])

    def test_adaptive_requires_checked_no_regression(self):
        r = row({"id": "partial", "kind": "ui", "recipe": {}}, passed=False)
        r["validation"]["all_net_regressions"] = {"bad": 1}
        self.assertIsNone(failed_first(cases()["ui"], [r], {}, 1))

    def test_resource_budget_released_on_exception(self):
        budget = ResourceBudget(8, Event())
        with self.assertRaises(RuntimeError):
            with budget.acquire(2):
                self.assertEqual(budget.available, 6)
                raise RuntimeError("failure")
        self.assertEqual(budget.available, 8)

    def test_normal_cleanup_is_not_user_cancellation(self):
        cancel, abort = Event(), Event()
        class Registry:
            def cancel_all(self):
                cancel.set()
        report = {"status": "pass", "resolved": 474}
        finish_registry(Registry(), cancel, abort, report)
        self.assertEqual(report, {"status": "pass", "resolved": 474, "cancelled": False})

    def test_explicit_cancel_during_cleanup_removes_credit(self):
        cancel, abort = Event(), Event()
        class Registry:
            def cancel_all(self):
                cancel.set()
                abort.set()
        report = {"status": "pass", "resolved": 474}
        finish_registry(Registry(), cancel, abort, report)
        self.assertEqual(report, {"status": "fail", "resolved": 0, "cancelled": True})


class AcceptedEvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.proof_names = ("candidate/validation.json", "candidate/work/native-drc.json",
                            "candidate/work/native-drc.json.provenance.json", "inventory.json",
                            "checked-result.json")
        self.backend_results = {}
        self.result = campaign(cases(), plans(),
                               lambda jobs, _: [self.checked_row(job) for job in jobs])

    def checked_row(self, job):
        attempt = row(job)
        folder = self.root / job["id"]
        result = {key: copy.deepcopy(attempt[key]) for key in
                  ("geometry_pass", "engine", "validation_process", "validation")}
        for name, key in (("candidate/validation.json", "validation_sha256"),
                          ("candidate/work/native-drc.json", "drc_report_sha256"),
                          ("candidate/work/native-drc.json.provenance.json", "drc_receipt_sha256"),
                          ("inventory.json", "inventory_sha256")):
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            write(path, {"job": job["id"], "proof": name})
            result[key] = sha(path)
        write(folder / "checked-result.json", result)
        self.backend_results[job["id"]] = copy.deepcopy(result)
        attempt.update(result, folder=str(folder),
                       checked_result_sha256=checked_result_hash(folder, result))
        return attempt

    def accepted_rows(self):
        return [attempt for state in self.result["cases"].values()
                for attempt in [state["winner"], *state["replays"]]]

    def test_intact_evidence_for_all_eight_attempts_passes(self):
        self.assertEqual((self.result["status"], self.result["resolved"]), ("pass", 474))
        self.assertEqual(len(self.accepted_rows()), 8)
        check_accepted_evidence(self.result)

    def test_changed_or_missing_proof_rejects_every_winner_and_replay(self):
        for attempt in self.accepted_rows():
            for name in self.proof_names:
                path = Path(attempt["folder"]) / name
                original = path.read_bytes()
                for missing in (False, True):
                    with self.subTest(job=attempt["profile"]["id"], proof=name, missing=missing):
                        try:
                            if missing:
                                path.unlink()
                            else:
                                write(path, {"changed": True})
                            with self.assertRaises((ValueError, OSError)):
                                check_accepted_evidence(self.result)
                        finally:
                            path.write_bytes(original)

    def test_capture_rejects_checked_result_changed_before_hashing(self):
        attempt = self.accepted_rows()[0]
        folder = Path(attempt["folder"])
        write(folder / "checked-result.json", {"geometry_pass": True})
        with self.assertRaisesRegex(ValueError, "differs from backend"):
            checked_result_hash(folder, self.backend_results[attempt["profile"]["id"]])

    def test_rewriting_proof_and_its_advertised_digest_does_not_refresh_trust(self):
        attempt = self.result["cases"]["ui"]["replays"][-1]
        folder = Path(attempt["folder"])
        write(folder / "inventory.json", {"status": "pass", "forged": True})
        saved = copy.deepcopy(self.backend_results[attempt["profile"]["id"]])
        saved["inventory_sha256"] = sha(folder / "inventory.json")
        write(folder / "checked-result.json", saved)
        with self.assertRaises(ValueError):
            check_accepted_evidence(self.result)

    def test_missing_captured_digest_rejects_even_unchanged_checked_result(self):
        attempt = self.accepted_rows()[0]
        del attempt["checked_result_sha256"]
        with self.assertRaisesRegex(ValueError, "checked-result.json"):
            check_accepted_evidence(self.result)

    def test_rejected_search_artifacts_do_not_enter_accepted_cohort(self):
        self.result["cases"]["ui"]["attempts"].append(
            row({"id": "rejected-without-proof", "kind": "ui", "recipe": {}}, passed=False))
        check_accepted_evidence(self.result)


if __name__ == "__main__":
    unittest.main()
